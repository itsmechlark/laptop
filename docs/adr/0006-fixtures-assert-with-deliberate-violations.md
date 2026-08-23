# Fixtures assert with deliberate violations, and their detection count is checked

**Context:** Three of `check-payload`'s checks are silent when the payload is
clean — handoff invocability, reference reachability, anchor resolution. A clean
result and a check that has stopped firing look identical from outside. This is
not hypothetical: the invocability bug the first of them was built for shipped
for months with every other check passing — `skills/tdd/SKILL.md` said "the
`rspec` skill" when `rspec` is a rule, not a skill. Reference reachability
catches the sibling case, a file a rename left behind, which resolves nothing
and breaks nothing.

**Decision:** Each of those checks runs first against a fixture carrying one
deliberate violation of every kind it recognizes, and the run fails unless the
detection count is exactly right — 4 for `spec/invocability-fixture/`, 2 and 2
for the two halves of `spec/orphan-fixture/`.

**Consequences:** A check that stops firing fails the build instead of going
quiet. The price is a `spec/` tree that looks broken to anyone reading it, which
is why the standing instruction is not to "fix" those fixtures — their
violations are the assertion. Teaching a check a new violation kind now means
updating a fixture and a count deliberately, in the same change.

**Rejected:** Trusting the checks. Cheaper, and indistinguishable from this
arrangement for as long as everything works — which is the problem, since the
failure it hides is a safeguard that quietly stopped safeguarding anything.
