# Trigger-eval coverage is prioritized, not uniform

**Context:** Only model-invocable skills can misfire, and a query set costs
tokens to run and attention to keep current. Covering every invocable skill
equally would spend most of that budget on skills whose worst case is a cheap
recovery.

**Decision:** A skill earns a query set for one of two reasons — it competes
with a sibling for the same requests, or a wrong trigger is expensive.
Everything else goes on `check-payload`'s `evals_exempt` list, and the script
warns about any invocable first-party skill that is on neither, so the gap stays
visible instead of silent.

**Consequences:** Coverage is uneven by design, and the exempt list has to be
read as *deliberately uncovered* rather than forgotten — a name comes off it the
first time the skill actually misfires. Adjacent skills share one query pool
with labels assigned per skill, so a query proves exactly one of them fires;
labeling a shared query should-trigger for both makes the pair unfalsifiable,
and `check-payload` fails on that rather than trusting it. A skill that becomes
one others route into earns a set before any misfire, because for a primitive
the expensive failure is the *missed* trigger — the agent improvising the
workflow instead of loading it — and description overlap cannot see that coming
(`grilling` came off the list for that reason, not for a misfire).

**Rejected:** Covering every invocable skill. It would remove the judgment call
about what counts as expensive, but the evals are hand-run and token-priced, so
a suite nobody finishes running measures less than a smaller one that gets run.
Excluding vendored skills is not a coverage judgment at all — a bad result there
has no in-repo fix, since editing the description desynchronizes the recorded
hash.
