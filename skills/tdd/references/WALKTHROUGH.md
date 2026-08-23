# Three walkthroughs

One feature driven outside-in from an empty stack, the bug-fix variant, and the
case the Iron Law does not cover: changing behavior in code that already exists
and has no tests.

The commands and messages below are RSpec-shaped for concreteness. The shape is
what transfers.

Notice how few of the reds below are assertion failures. Most are exceptions —
a missing route, an undefined constant, a method that doesn't exist. That is
normal outside-in: each one names the next thing to build, which is exactly the
test for an honest red. The one broken-test case looks different and is called
out where it appears.

## 1. A feature, outside-in

**Slice:** *When I'm looking for an item by name, I want to search the list, so
I can find it without scrolling.* Ships when: typing "Widget" into the search box
and submitting shows the Widget and nothing else.

### Push the first test

Write the end-to-end test for the "ships when" behavior. Visit the page, fill in
"Widget", submit, expect "Widget" in the results and the other record absent.

```
$ rspec spec/system/item_search_spec.rb
Failure/Error: fill_in "Search", with: "Widget"
  Capybara::ElementNotFound: Unable to find field "Search"
```

An honest red: the search field doesn't exist, and the message says so. The next
question is what the page needs — a handler that responds to a search parameter.
That's a layer down.

### Drop to the handler

```
$ rspec spec/requests/items_spec.rb
Failure/Error: get items_path, params: { search: "Widget" }
  ActionController::RoutingError: No route matches [GET] "/items"
```

**One change, one run.** Add the route — inert glue, no behavior of its own, and
a failing test one layer up demanded it. Run again:

```
NameError: uninitialized constant ItemsController
```

Create the empty controller. Run again:

```
AbstractController::ActionNotFound: The action 'index' could not be found
```

Add the empty action. Run again:

```
expected the response body to include "Widget"
```

That one is different. The previous three were structural — something wasn't
defined. This one is a behavior gap: the response is rendering, and the filtering
logic that would put "Widget" in it doesn't exist. Filtering is a unit concern.
Drop down again.

### A red that isn't

All four runs above were honest reds: each message named the next thing to
build. Compare this one, which would look just as red in the terminal:

```
$ rspec spec/requests/items_spec.rb
LoadError: cannot load such file -- support/search_helpers
```

`search_helpers` is not something this slice is building. It's a `require` in
the spec file pointing at a path that doesn't exist, and the test never reached
the code at all — nothing about the feature is proven either way. Fix the
require and run again. The real red is still ahead of you.

### Drop to the unit

```ruby
it "returns only items matching the term" do
  widget = Item.create!(name: "Widget")
  Item.create!(name: "Gadget")

  expect(Item.search("Widget")).to eq([widget])
end
```

```
$ rspec spec/models/item_spec.rb:12
NoMethodError: undefined method `search' for Item:Class
```

Verify RED. An exception, and an honest one — it names `search`, which is
precisely what this test exists to force into being.

GREEN: the simplest filter that passes. Not case-insensitivity, not fuzzy
matching, not a `limit:` keyword. Nothing the test didn't ask for. Verify GREEN,
refactor if there's anything to clean, and **pop**.

### Pop back up

Rerun the request spec. It now fails on the view, not the data — wire the
controller and template, one change per run, until it's green. Pop again: rerun
the system spec, drive the remaining UI the same way. When it goes green the
stack is empty and the slice is done.

The whole trace, as a stack:

```
system spec        ← pushed first, popped last
  request spec
    model spec     ← the only layer that got real logic
```

Three layers, three failing tests, and every line of production code traceable
to one of them.

## 2. A bug fix

Same loop, different entry point: the reproduction *is* the outermost test.

1. **Reproduce from the outside.** Write the test at the layer the bug is
   reported at — if a user saw it in the UI, start there, not at the unit you
   suspect. A unit test written against your hypothesis passes when the
   hypothesis is wrong, and you'll have proved nothing.
2. **Watch it fail with the reported symptom.** Not a similar failure — the
   actual one. If the reproduction fails differently than the report describes,
   you're reproducing a different bug.
3. **Follow the failure down** to the layer that owns the defect, pushing a
   failing test at each layer that has behavior of its own.
4. **Fix under red-green-refactor**, then pop back up. The outermost test going
   green is what proves the user-visible symptom is gone.

The reproduction test is the deliverable, not scaffolding. It's what stops the
bug coming back, and it's why AGENTS.md §1, *Engineering mindset (plan & code
like a staff engineer)*, says a bug fix starts with a test that reproduces the
bug.

**When you can't reproduce it,** stop. Don't write a test for the mechanism you
suspect and call the fix proven — you'd be pinning a guess. Say the repro is
missing and go get what would produce one: the input, the environment, the
timing, the record. A fix with no failing test is a change nobody can verify.

## 3. Changing untested legacy code

The Iron Law says delete production code written before its test. That governs
code *you* write in this session. Code that was already in the repository when
you arrived is not yours to delete, and deleting it to satisfy the rule would be
the most destructive possible reading of it.

The sequence instead:

1. **Characterize the current behavior.** Write a test that asserts what the code
   does *today* — including behavior you think is wrong. Run it and confirm it
   passes. This is deliberate: it is not your red, it's a safety net. If it
   fails, you've misread the code, which is worth knowing before you change it.
2. **Get the characterization green and honest.** If the code is too coupled to
   test at all, that's a seam problem — `codebase-design` places the seam, and
   the minimum change that makes the code reachable from a test is itself a
   refactor you make under the existing suite.
3. **Now write the failing test for the new behavior.** This is your red. Watch
   it fail for the right reason.
4. **Change the code.** The characterization tests are what tell you which
   *other* behaviors you broke on the way.
5. **Retire what you deliberately changed.** A characterization test asserting
   behavior the change intentionally replaced is now wrong — delete or update it,
   and say in the commit which behavior changed on purpose. Leaving it green by
   weakening the assertion hides exactly the thing a reader needs to see.

Characterization tests you *didn't* change stay. They're coverage the next person
gets for free.

**The one thing not to do** is change untested code and add a test afterwards
that passes. It documents whatever you happened to write, proves no behavior was
preserved, and reads in the diff exactly like work that was driven by a test.
