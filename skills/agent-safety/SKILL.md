---
name: agent-safety
description: Govern AI agent systems that call tools — tool allowlists, argument filtering, human-approval gates, rate limits, delegation trust, and append-only audit trails. Use when building or reviewing agents that use tool-calling LLMs or multi-agent orchestration (PydanticAI, CrewAI, OpenAI Agents SDK, LangChain/LangGraph, AutoGen), writing a tool function, defining or composing an agent policy file, restricting what tools an agent may call, scoping a tool's permissions, bounding the blast radius of a prompt injection, adding guardrails to an agent with unrestricted tool access, or auditing what an agent actually did.
---

# Agent Safety & Governance

Governance is a **pre-execution** check sitting between the model's decision to
call a tool and the tool's side effect. Output guardrails inspect text after the
fact — by then the email is sent and the rows are deleted. Everything below is
about making that decision point enforceable, configurable, and auditable.

## When to use this skill

- Writing or reviewing a tool function an LLM is allowed to call
- Wiring an agent framework into systems that have real side effects — email,
  deploys, payments, customer data
- Defining, composing, or reviewing agent policy files
- Adding guardrails to an agent that currently has unrestricted tool access
- Reviewing multi-agent delegation or handoff code
- Building an audit trail for agent actions

Scoped to what an agent is permitted to *do* at run time — not a general defect
review of a diff or a PR, not a vulnerability sweep of a branch, and not the
model provider's API surface of parameters, pricing, and caching.

## Core principles

| Principle | What it means | Why |
| --- | --- | --- |
| **Fail closed** | A governance check that errors, times out, or returns ambiguous is a *deny* | An exception in the policy engine must not become an open door |
| **Policy as configuration** | Rules live in YAML/JSON, loaded at run time | Tightening a rule shouldn't need a deploy, and the policy diff is reviewable on its own |
| **Least privilege** | The minimum tool set, the minimum function within each tool, and the minimum downstream grant that tool holds | Blast radius of a prompt injection is bounded by what the agent could do at all |
| **Append-only audit** | Entries are never edited or deleted | An audit trail the system can rewrite proves nothing |

## The lethal trifecta

Before designing controls, look at what the agent *combines*. Three capabilities
are individually ordinary and jointly exploitable:

1. **Access to private data** — customer records, internal repositories, mail
2. **Exposure to untrusted content** — web pages, tickets, inbound mail, and the
   output of any tool or peer agent that read one
3. **An outbound channel** — sending mail, arbitrary HTTP, writing anywhere
   public

Hold all three and any instruction the agent reads has a path to exfiltrate
everything it can reach; no filter reliably closes that path, because the model
draws no architectural line between instructions and data. Removing one leg
does close it. Split the work so each agent holds at most two — the retriever
reads untrusted content and has no way out, the sender has a way out and never
sees untrusted input.

## The governance boundary

Put the check at the call site, not in the prompt. Instructions are advisory —
the model can be argued out of them by content it reads mid-task. A wrapper
around the tool function cannot be.

Whatever the framework, that wrapper does four things in order: evaluate the
policy against the tool name **and** its arguments, record the decision, raise
on a denial, and only then execute. Keep it in a module you own rather than
adopting a framework's built-in equivalent — it is the piece a framework
upgrade must not silently change. Implementation and the per-framework seam it
attaches to: [FRAMEWORKS.md](references/FRAMEWORKS.md).

**Separate registration from authorization.** The framework's job is knowing
what tools exist; the policy's job is deciding which ones this agent may call
right now. When those collapse into one list, "register a tool" silently means
"grant a capability", and every new tool widens every agent.

**The decision is graduated, not binary.** Reversible low-value actions record
and proceed; unusual-but-recoverable ones warn; irreversible or high-value ones
escalate to a human; the rest deny. Collapsing this to allow/deny forces every
new rule to choose between blocking legitimate work and being switched off — and
an audit-only outcome is what makes a rule safe to ship in the first place.

## Tool access controls

- **Allowlist, never open access.** Name the tools an agent may call. An agent
  whose policy is `allowed_tools: ["*"]` has no policy.
- **Prefer a narrow tool over a broad one with a filter.** A mail tool that
  cannot send is a guarantee; a mail tool with a `send=False` argument is a
  suggestion the model fills in. The same goes for the tool you adopted for one
  of its three functions — wrap it and expose only that one.
- **Give each tool its own downstream credential, scoped to what it does.** A
  read tool connecting with an identity that also holds `UPDATE` and `DELETE` is
  unbounded no matter what its policy says: the allowlist governs the name, the
  grant governs the damage.
- **Blocklist the known-dangerous** regardless of allowlist: shell execution,
  file deletion, database DDL, credential reads. Defense in depth for the case
  where an allowlist is edited carelessly.
- **Require human approval for high-impact, irreversible actions** — sending
  email, deploying, deleting records, moving money. Approval must be requested
  and recorded before the call, not confirmed after it.
- **Bound loops and spend, not just call counts.** An agent stuck in a loop is
  the normal failure mode, not the exotic one. Cap recursion depth, wall-clock
  duration, and per-run cost alongside the call count, and hash the run state to
  catch a loop that varies its arguments each pass. Cap the *cumulative value* of
  the arguments that carry consequence, too — twenty-five refunds sits inside
  `max_calls_per_request: 25` and still clears six figures.

## Constrain arguments, not just tool names

**Type before pattern.** A parameter typed as an enum of three account tiers
cannot express an injection payload. A string parameter checked against a
blocklist can, and only fails on the shapes someone predicted. Give every tool a
strict parameter schema — enums, bounded ranges, formats, explicit maximum
lengths — and validate it before any content check runs. Patterns are the
fallback for the fields that genuinely have to carry free text.

Those fields are where the asymmetry bites. The tool name comes from a set you
defined; the free-text argument is text the model generated, possibly under the
influence of a web page, a ticket comment, or a file it just read. `search`
being allowlisted says nothing about
`search("'; DROP TABLE users; --")`.

Check both ends:

- **The user's original prompt** for threat signals — data exfiltration,
  prompt injection, privilege escalation
- **The agent's generated arguments** for API keys, credentials, PII, and
  injection payloads

Keep the pattern lists in configuration, not in code, so the response to a new
attack shape is a config change rather than a release. Patterns and policy
schema: [POLICY.md](references/POLICY.md).

## Multi-agent delegation

- Every agent in the system carries **its own policy** — a sub-agent is not
  covered by its caller's policy by default.
- **Carry the user's identity and scope across the hop.** A chained call that
  authenticates downstream as the orchestrator's service account turns every
  delegation into a privilege escalation: the sub-agent acts with the fleet's
  reach rather than the requesting user's. Pass the original authorization
  context down the chain and let the downstream system enforce it.
- **Delegation narrows; it never widens.** An inner agent's effective
  permissions must be a subset of the outer agent's. Compose org, team, and
  agent policies most-restrictive-wins rather than letting the innermost
  definition speak last. Per-field composition rules:
  [POLICY.md](references/POLICY.md).
- **Track trust per delegate and decay it.** Degrade on failures and policy
  violations; require ongoing good behavior rather than treating a score earned
  last month as current.

## Audit trails

Log one record per tool call, and one per violation:

| Field | Example |
| --- | --- |
| `timestamp` | `2026-08-10T09:14:22Z` |
| `agent_id` | `support-triage` |
| `tool` | `send_email` |
| `decision` | `audit` / `warn` / `allow` / `escalate` / `deny` |
| `policy` | `team-support@v3` |
| `matched_rule` | `blocked_patterns[2]` — on anything but a clean allow |

Write JSON Lines so log aggregators can ingest it without a parser, mark
session start and end so calls can be correlated into a run, and append only.

**Log decisions and metadata, not user content.** Prompts and tool arguments
are exactly where the credentials and PII are; an audit trail that captures
them becomes the breach it was meant to detect. Log that a rule matched and
which one — not the string that matched it.

## Gotchas

- **A `try`/`except` around the policy check that continues on error is an
  open door.** Fail closed: an unavailable policy engine denies every call.
- **Never let an agent write to its own policy.** Policy files must not be
  reachable through any allowlisted file or database tool — a self-modifying
  policy is an escalation path with an audit trail that looks clean.
- **Output guardrails are not governance.** Filtering the final answer does
  nothing about the tool call made three steps earlier. Sanitizing what goes
  into the model and what comes out of it addresses a different failure — it is
  not a root control for what the agent is permitted to do.
- **A tool nobody calls is still a tool the agent can call.** Trialed during
  development, superseded, never unregistered — the registry is the attack
  surface, not the code path you meant to ship. Derive the allowlist from what
  the task needs, then diff it against what the framework actually exposes.
- **Treat tool names, descriptions, and schemas as public.** They sit in the
  model's context and come back out under conversational probing. A description
  reading "admin only" documents a target and enforces nothing; a connection
  string in one is simply a leaked credential.
- **A wrapper inside the agent process is necessary, not sufficient.** Anything
  reaching the same downstream API by another route — a retry queue, a sibling
  service, a framework internal — goes around it. Enforce the ceilings and the
  authorization where the credential is honoured too, so bypassing the agent
  doesn't bypass the policy.
- **An approval gate that a retry can skip is not a gate.** Cache the approval
  decision against the call, so a re-run of the same step re-requests approval
  instead of inheriting a stale yes.
- **Rate limits belong per request, not only per session.** A per-session cap
  measured in hundreds still allows one runaway request to exhaust it.
- **Trust that never decays isn't trust, it's a constant.** Score with a decay
  window, or drop the mechanism and stop pretending it constrains anything.
- **Framework-level "safe mode" flags are not a substitute for policy.** They
  vary by version and rarely cover argument content — verify what a flag
  actually checks before relying on it.

## Review checklist

- [ ] Every tool an agent can reach is on an explicit allowlist, and nothing is
      registered that the task doesn't need
- [ ] Each tool does one thing, takes a strict parameter schema, and holds only
      the downstream grant that thing requires
- [ ] No single agent holds private data, untrusted input, and an outbound
      channel at once
- [ ] Dangerous operations are blocklisted independently of the allowlist
- [ ] Irreversible actions require recorded human approval
- [ ] Tool arguments are validated structurally, then filtered for content
- [ ] Threat patterns and rules load from configuration, not code
- [ ] Governance failures deny rather than pass through
- [ ] Sub-agent permissions are a subset of the caller's, and delegated calls
      carry the original user's authorization rather than a service identity
- [ ] Policies compose most-restrictive-wins
- [ ] Call-count, depth, duration, cost, and cumulative-value ceilings are all
      enforced per request
- [ ] No credential or authorization rule lives in a prompt, tool description,
      or parameter schema
- [ ] Audit records are append-only, JSON Lines, and free of user content
- [ ] No path exists by which an agent can modify its own policy

## References

Read as needed, not upfront:

- [POLICY.md](references/POLICY.md) — policy file schema, composition rules,
  and pattern lists
- [FRAMEWORKS.md](references/FRAMEWORKS.md) — where the interception point is
  in PydanticAI, CrewAI, OpenAI Agents SDK, LangChain/LangGraph, and AutoGen
- [THREATS.md](references/THREATS.md) — which published threat each control
  answers, and which agent-specific risks these controls do *not* cover
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
  — the threat catalogue these controls map to; Excessive Agency is the entry
  this skill implements
- [OWASP GenAI Security Project](https://genai.owasp.org/) — publisher of that
  list and of the companion Agentic (ASI) list, which owns the risks that appear
  once an agent has persistent memory and peer agents

Adapted from [awesome-copilot](https://github.com/github/awesome-copilot)'s
`agent-safety.instructions.md` (MIT).
