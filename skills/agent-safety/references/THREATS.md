# Threat mapping

Which published risk each control answers, and — more usefully — where the risk
stops being the kind this skill addresses at all.

Referenced entries are from the OWASP Top 10 for LLM Applications and Generative
AI, 2026 edition. Entry numbers move between editions; the names are the stable
handle.

## The entry this skill implements

**Excessive Agency** is the vulnerability that lets damaging actions follow from
unexpected, ambiguous, or manipulated model output — whatever made the model
malfunction. It has three root causes, and a control that addresses one does
nothing for the other two:

| Root cause | What it looks like | Control |
| --- | --- | --- |
| Excessive **functionality** | A tool adopted to read documents can also modify and delete them; a tool trialed in development is still registered; a tool meant for one shell command doesn't stop others | Minimize the tool set; wrap broad tools to expose one function; strict parameter schemas |
| Excessive **permissions** | A read tool connects with an identity holding `UPDATE`/`INSERT`/`DELETE`; a per-user tool connects with a generic privileged account that can see every user's files | Per-tool downstream credentials; user-context propagation across chained calls |
| Excessive **autonomy** | A high-impact action executes with no independent verification | Approval gates bound to the specific call; graduated enforcement |

The distinction that gets missed: an allowlist answers *functionality* only. An
agent whose `allowed_tools` is a single read tool is still unbounded if that
tool's database identity can write, and still a data-breach path if it reads as
a service account instead of as the requesting user.

**Sanitizing model inputs and outputs is not a root control here.** Input
sanitization belongs to Prompt Injection, output sanitization to Improper Output
Handling. Both are worth doing; neither reduces what the agent is permitted to
do, which is the only thing that bounds the damage.

## Where the boundary is

The LLM Top 10 owns the risk while the model is a *component inside* an
application. The moment it becomes an actor — tools it can call, memory it
carries between sessions, consequences it sets in motion downstream — the risk
moves to the companion **Agentic (ASI)** list. Excessive Agency is where the two
meet: it manifests agentically as Tool Misuse & Exploitation, Identity &
Privilege Abuse, and Cascading Failures.

So the controls here are the tool-call half. They do **not** cover:

- Persistent memory poisoned in one session and acted on in the next
- Inter-agent channels as an attack surface in their own right
- Tool configuration that persists and drifts
- Multi-step compromise that is individually policy-compliant at every step
- Cascading failure across a fleet, where one bad decision is amplified by
  agents that treat a peer's output as trusted input

Reach for the Agentic list for those. Neither list covers that ground alone.

## Adjacent entries that change what you build

| Entry | Why it lands here |
| --- | --- |
| **Prompt Injection** | The reason the wrapper exists. There is no reliable prevention today — models draw no architectural line between instructions and data — so defense is architectural: assume the instruction boundary gets crossed and constrain what a crossed boundary can reach. Injection is the input-side compromise; excessive agency is what gives it consequences outside the chat window. |
| **Unbounded Consumption** | Supplies the ceilings: step limits, recursion depth, wall-clock, per-run cost, state hashing to detect loops. Note the two agent-specific scenarios — a published tool that instructs an agent into recursive fan-out, and a long-lived session whose growing context makes turn 100 cost 500× turn 1 while no single request trips a per-request limit. |
| **Hidden Context Exposure** | Tool names, descriptions, and parameter schemas are part of the model's context and are extractable by conversational probing. Design on the assumption that they are public: no credentials in them, and no authorization rule that exists only there. An extracted tool schema hands an attacker concrete targets for the next attempt. |
| **Sensitive Information Disclosure** | Why audit records carry decisions and rule identifiers rather than prompts and arguments — the audit trail is otherwise the breach it was built to detect. |
| **Improper Output Handling** | Downstream encoding and escaping of what the model emits. Adjacent, and out of scope here: a schema-valid response can still carry a malicious query. |

## The pre-deployment check

The trifecta in `SKILL.md` is the cheapest useful review question, because it
needs no code reading: *does this agent have access to private data, exposure to
untrusted content, and a channel to the outside?* Three yeses is the condition
for high-impact exploitation. Removing any one removes it — and that removal is
an architecture decision, made before the policy file exists.
