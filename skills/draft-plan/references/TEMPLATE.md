# The plan template

Two blocks: one header for the plan, one repeated structure per task. Both are
fixed, and both are written for a reader who has this document and nothing else.

## Header

Every plan opens with this. `metadata.spec` is not optional — the plan argues
from the spec, so the spec travels with it, and an implementer reads both. It
sits in the frontmatter rather than the body because a path repeated in two
places is a path that can disagree with itself; the same goes for `stack`.

`metadata.topic` is copied from the spec unchanged. It is the join key that ties
this plan to the spec above it and the lore notes written after it, and copying
it wrong is the one frontmatter error nothing downstream will catch.

`description` is required and short: one line, under 120 characters, no
wrapping. **The output directory's existing convention wins** — read what is
already in the plans directory, and where those files carry a different shape or
none, match them and say so instead of leaving two conventions in one directory.

```markdown
---
name: <the slice, kebab-case>
description: <one line, under 120 characters — when a reader should open this>
metadata:
  status: ready
  topic: <the join key, copied from the spec>
  spec: <docs/specs/<file>.md — or the tracker item, or the URL>
  stack: <languages, frameworks, and libraries a task will touch>
---

# <Slice name> implementation plan

**Goal:** One sentence: what a user can do afterwards that they cannot do now.

**Approach:** Two or three sentences on how, at the level a reviewer needs to
follow the task order.

**Execution:** Tasks are independent within their stated dependencies. Steps use
`- [ ]` so progress is trackable. Follow the test-first cycle exactly as written.

## Global Constraints

Project-wide requirements, one line each, values copied verbatim from the spec.
Every task's requirements implicitly include this section.

- Ruby >= 3.2, Rails 7.1 — do not introduce 7.2-only APIs
- All new behavior ships behind `deposit_refunds_enabled`, default off
- Migrations must be backward-compatible: expand and backfill only in this slice
```

Global Constraints is the section most often left empty and most often needed.
An implementer reads their own task, not the header, so anything that must hold
everywhere is repeated in the tasks where a violation is plausible.

## Task

````markdown
### Task N: <what this task delivers>

**Depends on:** Task N-1 (or `nothing`)

**Files:**
- Create: `app/services/deposit_refund.rb`
- Modify: `app/models/reservation.rb` — the `#refundable?` predicate, near line 210
- Test: `spec/services/deposit_refund_spec.rb`

**Interfaces:**
- Consumes: `Reservation#refundable?` -> Boolean (Task 1)
- Produces: `DepositRefund.new(reservation:) -> DepositRefund`,
  `DepositRefund#call -> Result[:ok | :not_refundable]`

- [ ] **Step 1: Write the failing test**

```ruby
RSpec.describe DepositRefund do
  it "refuses a reservation that is not refundable" do
    reservation = build(:reservation, :non_refundable)

    expect(described_class.new(reservation:).call).to eq(:not_refundable)
  end
end
```

- [ ] **Step 2: Run it and watch it fail**

Run: `bundle exec rspec spec/services/deposit_refund_spec.rb`
Expected: `NameError: uninitialized constant DepositRefund`

- [ ] **Step 3: Write the minimum that passes**

```ruby
class DepositRefund
  def initialize(reservation:) = @reservation = reservation

  def call = @reservation.refundable? ? :ok : :not_refundable
end
```

- [ ] **Step 4: Run it green**

Run: `bundle exec rspec spec/services/deposit_refund_spec.rb`
Expected: 1 example, 0 failures

- [ ] **Step 5: Commit**

```sh
git add app/services/deposit_refund.rb spec/services/deposit_refund_spec.rb
git commit -m "feat(refunds): refuse a refund on a non-refundable reservation"
```
````

The example is Ruby because it has to be something. The structure is the
portable part — the test code, the exact command, and the expected output are
required in every language.

## What each part is doing

| Part | Why it is there |
| --- | --- |
| `Depends on:` | The only ordering signal a parallel dispatcher can read. `nothing` means it can start immediately |
| `Files:` with `Create`/`Modify`/`Test` | An implementer should never have to search for where the work goes. `Modify` names the method as well as the line, because line numbers rot |
| `Interfaces:` | The implementer sees only this task. Consumes and Produces are how neighboring tasks agree on names without talking |
| Test before code, every task | The cycle `tdd` owns. An unattended implementer follows what is written or nothing |
| Explicit expected output | Turns "run the test" into a checkable claim. `Expected: FAIL with <message>` is what stops a step passing for the wrong reason |
| A commit per task | Keeps the blast radius one task wide and makes a bad task revertible without unwinding its neighbors |
