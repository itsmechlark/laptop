# Policy files

A policy is configuration, not code: a declarative statement of what an agent
may do, loaded at run time and reviewable on its own. If tightening a rule
requires editing application logic, it isn't a policy.

## Shape

There is no cross-framework standard, so treat the following as the set of
concerns a policy has to cover rather than a schema to copy verbatim.

```yaml
name: support-triage
version: 3

enforcement: block            # default outcome for a match: audit | warn | block | escalate

allowed_tools: [search_tickets, summarize, lookup_customer]
blocked_tools: [run_shell, delete_record, execute_sql]

identity: on_behalf_of_user   # or `service` — how downstream calls authenticate
required_scopes: [tickets.read, customers.read]

blocked_patterns:
  - "(?i)(api[_-]?key|password|secret|token)\\s*[:=]"
  - "(?i)\\b(drop|truncate|alter)\\s+table\\b"
  - "\\b\\d{3}-\\d{2}-\\d{4}\\b"           # US SSN

require_approval: [send_email, issue_refund]

limits:
  max_calls_per_request: 25
  max_calls_per_tool:
    lookup_customer: 10
  max_depth: 3                # delegation / recursion depth
  max_duration_seconds: 300
  max_cost_usd: 5.00
  max_cumulative:             # summed across the run, per argument
    issue_refund.amount_usd: 500
```

```yaml
# Bad: names an agent, constrains nothing
name: support-triage
allowed_tools: ["*"]
```

| Key | Covers |
| --- | --- |
| `enforcement` | What a match does, so a rule can ship in audit mode before it blocks |
| `allowed_tools` | The authorization list — enumerated, never `*` |
| `blocked_tools` | Dangerous operations, denied even if an allowlist names them |
| `identity` | Whether downstream calls carry the user's authorization or a service account's |
| `required_scopes` | The ceiling on the delegated grant, checked when the token is minted |
| `blocked_patterns` | Regexes matched against the prompt and generated arguments |
| `require_approval` | Tools that need a recorded human decision before execution |
| `limits.max_calls_*` | Loop containment, per request and per tool |
| `limits.max_depth` | How far a delegation chain may recurse |
| `limits.max_duration_seconds`, `limits.max_cost_usd` | Circuit breakers for a run that is progressing but not terminating |
| `limits.max_cumulative` | Ceiling on the summed value of an argument — the money, not the call count |

Version the policy and record that version in every audit entry. Without it,
"why was this allowed in March?" is unanswerable.

The parameter schema is not in this file. Argument *shape* — enums, ranges,
formats, maximum lengths — belongs on the tool definition, where the framework
validates it before your check runs. This file governs what happens next.

## Composition

Policies arrive in layers — organization, team, agent — and the layers must
narrow, never widen:

| Field | Composition |
| --- | --- |
| `allowed_tools` | Intersection of every layer |
| `blocked_tools` | Union of every layer |
| `blocked_patterns` | Union of every layer |
| `require_approval` | Union of every layer |
| `required_scopes` | Intersection of every layer |
| `identity` | `on_behalf_of_user` wins over `service` — a layer may narrow the identity, never broaden it |
| `enforcement` | Strictest across layers, ordering `audit` < `warn` < `escalate` < `block` |
| `limits.*` | Minimum across layers |

```python
final_policy = compose_policies(org_policy, team_policy, agent_policy)
```

The property to test: adding a layer can only remove capability. A merge that
lets a later layer re-grant a tool an earlier layer denied is a bug, and the
one worth a dedicated test — it fails open and looks correct in review.

Delegation composes the same way. An agent handing off to a sub-agent passes
its *effective* policy down as another layer, so the sub-agent's permissions
are a subset of the caller's by construction rather than by discipline.

## Pattern lists

Patterns exist to be updated without a release. Keep them in the policy file
or a referenced list, never inline in the check function.

- **Match against both directions**: the user's prompt on the way in, and the
  agent's generated arguments on the way to the tool.
- **Anchor and bound them.** An unanchored `.*` alternation over long tool
  arguments is a denial-of-service against your own agent; prefer explicit
  character classes and bounded repetition.
- **Compile once at load**, not per call.
- **A pattern match is a deny plus an audit record** naming which pattern
  matched — by index or name. Never log the matched text.
- **Test them.** A regex list nobody has a fixture for is decorative; include
  known-bad strings that must be denied and realistic strings that must pass.

Patterns are a coarse net. They catch obvious credentials and injection
payloads; they don't catch a well-phrased instruction to exfiltrate data. Pair
them with the allowlist — the allowlist is what actually bounds blast radius.

## Approvals

- Request approval **before** execution, and record the requester, approver,
  tool, and decision.
- Bind the decision to the specific call, not to the tool or the session, so a
  second call to the same tool asks again.
- Give approvals a timeout that denies on expiry, so an unanswered prompt
  doesn't leave a request hanging on a maybe.
- Escalation is a denial with context, never a silent skip of the tool.

## Rolling out a policy

Policy changes are behavioral changes to a running system. Ship them the same
way: start at `enforcement: audit` — evaluate the rule, record what it *would*
have denied, allow the call — and read those records before promoting it to
`warn` and then `block`. That surfaces the legitimate workflow the new rule
would have broken, before it breaks it.

Shadow mode is a property of the rule, not a global switch. A policy where every
rule is in audit mode enforces nothing, which is fine for a day and indefensible
for a quarter — track which rules are still un-promoted and why.

Going the other direction, loosening a rule deserves the scrutiny of a code
change: whose request, what evidence, and what the blast radius becomes.
