# Linked

Linked directly from `SKILL.md`, so this file is reachable and must not be
reported.

It also links [CHAINED.md](CHAINED.md), which makes that file reachable through
the single hop the rule permits — the existing 2-hop check warns about the
chain, but reachability holds and the orphan check must stay quiet about it.

The fenced block below mentions a fourth file. A mention inside a fence is
documentation, not a link, so `FENCED.md` must still be reported:

```markdown
See [FENCED.md](FENCED.md) for the response shapes.
```
