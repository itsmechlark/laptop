# Framework interception points

Every tool-calling framework has a seam between "the model asked for this tool"
and "the tool ran". Governance goes in that seam. What follows is where the
seam is in each framework — not a stable API reference. These libraries move
fast, so **verify the current hook name against the installed version's docs**
before writing against it, and prefer a wrapper you own over a framework
feature you don't control.

## The portable shape

Whatever the framework, the wrapper does the same things in the same order:

```python
def govern(policy):
    def wrap(fn):
        @functools.wraps(fn)
        async def inner(ctx, *args, **kwargs):
            decision = policy.check(fn.__name__, kwargs, ctx)  # 1. name, arguments, caller
            audit.record(decision)                             # 2. always logged
            if decision.outcome is BLOCK:                      # 3. fail closed
                raise PolicyDenied(decision.reason)
            if decision.outcome is ESCALATE:                   # 4. human, or a denial
                await approvals.request_or_deny(decision)
            return await fn(ctx, *args, **kwargs)              # 5. only then, execute
        return inner
    return wrap
```

`ctx` carries the requesting user's authorization, and it is why the signature
takes it explicitly: a tool that reaches downstream on its own service
credential has no way to be governed per user, however good the policy is.

Keep this in your own module. It is the piece that must not vary by framework,
and the piece a framework upgrade must not silently change.

## PydanticAI

Tools are registered with `@agent.tool`. Apply the governance decorator to the
tool function so the check runs inside the call rather than around the agent
run — an agent-level wrapper sees the final result, not each tool call.

Tool arguments arrive as validated Pydantic models, which is the cleanest place
to inspect them: validate structure first, then apply content patterns to the
model's fields.

## CrewAI

Apply governance at the **Crew** level so it covers every agent in the crew,
rather than per agent where a newly added agent silently escapes it. The
`before_kickoff` hook is the place for policy validation and composition — load
and compose the org/team/agent layers there, and fail the kickoff if the
composed policy can't be built.

Per-agent tool lists are a convenience, not an authorization boundary; the
policy still has to be the thing that decides.

## OpenAI Agents SDK

Wrap `@function_tool` functions with the governance decorator. For multi-agent
work, guard the handoff: a handoff is a delegation, so the receiving agent's
effective policy is the composition of both, and trust in the delegate belongs
in that check.

The SDK's own guardrails run on inputs and outputs — useful, but they are not
a substitute for a pre-execution check on tool arguments.

## LangChain / LangGraph

Wrap tools with a `RunnableBinding` or a plain tool wrapper. In LangGraph,
apply governance **at the graph edge** as well: edges are where control flow is
decided, and flow control is the thing you want bounded when a loop misbehaves.

Watch for tools reached through a retriever or a sub-chain — they bypass a
wrapper applied only to the top-level tool list.

## AutoGen

Governance goes in the `ConversableAgent.register_for_execution` hook, which is
the point where a proposed call becomes an executed one. Note that AutoGen
splits proposal (`register_for_llm`) from execution — governing only the
proposal side leaves the executing agent unguarded.

## What to check regardless of framework

- The wrapper is applied to **every** registered tool. A test that enumerates
  the registry and asserts each entry is wrapped catches the tool someone adds
  next quarter.
- The caller's authorization survives every hop — handoffs, sub-chains, and
  queued work included. Frameworks routinely drop context across a delegation,
  and the tool then falls back to whatever credential it was configured with.
- Framework retries don't bypass the check or double-count the rate limit.
- Streaming and parallel tool calls still route through the same seam.
- Errors raised by the policy propagate as denials, and aren't swallowed by a
  framework-level catch-all that turns them into a retry.
