# What earns a place in a rule

A rule is paid for on every file its glob matches, in every session, forever.
That price is the whole test. Content that would be useful *sometimes* still
loses if it loads *always* — which is why a rule is a narrower artifact than an
instruction file and a much narrower one than a skill.

## The four that reliably lose

### Anything a linter, formatter, or type-checker already enforces

The tell: the rule could have been a config key.

```
Use single quotes for strings.        -> Prettier / RuboCop config
Two-space indentation.                -> .editorconfig
No unused imports.                    -> ESLint rule
Sort imports alphabetically.          -> the formatter
```

A tool that fails the build is strictly stronger than a sentence the model
weighs against everything else in its context. Worse, the rule and the tool
drift: the config changes, the rule doesn't, and now two sources of truth
disagree — the tool wins the build while the rule wins the model's attention.

What a linter *cannot* express still belongs in a rule: "prefer a value object
over a hash with three known keys", "a serializer is a published contract,
change it additively". Judgment, not syntax.

### Anything the model already knows

```
Run `npm install` to install dependencies.
Use `git rebase -i` to squash commits.
Rails models go in app/models.
```

The test from `agent-skills` applies unchanged: if it is on the first page of
the official docs, it is already in the model and the rule is buying nothing.

What survives the cut is the part that is not in the docs — the version-specific
quirk, the default your team deliberately overrides, the internal convention a
newcomer would get wrong.

### Edge cases that rarely fire

A rule can be entirely correct and still not worth its cost:

> When adding an index to a table over 100M rows, use `CONCURRENTLY` and do it
> in its own migration.

True, important, and applicable perhaps twice a year — but scoped to
`**/db/migrate/**` it loads on every migration for the whole year to be there
for those two. The occasion, not the file type, is what summons it, and an
occasion is the definition of a skill. Move it and let it be invoked.

### Code that already exists in the repository

Pasting the canonical example into the rule creates a second copy that nothing
keeps in sync. It goes stale the first time someone edits the original, and it
goes stale *silently*, because the rule still reads perfectly well.

```
Bad   A 30-line service-object template, inlined.
Good  `app/services/create_booking.rb` is the shape to follow.
```

The path either stays correct or breaks loudly when the file moves. The paste
does neither.

## The recurrence test

**Write the rule after the second correction, not before.**

A rule written in anticipation is a guess that carries a permanent cost, and
the mistake it guards against may never arrive. Worse, it is unfalsifiable: you
cannot tell a rule that prevented nothing from a rule that prevented everything,
so it never gets removed.

Repetition is the signal that costs nothing to wait for. The first time an agent
gets something wrong, correct it in chat. The second time, you have evidence,
and the correction you already typed twice is most of the rule text — scope it
to the files it governs and you are done.

The same logic runs in reverse for pruning. A rule whose mistake you have not
seen in a year is either doing its job invisibly or is dead weight, and nothing
in the file tells you which. Prefer removing it and watching for the mistake to
come back.

## When a chat prompt should become a rule

Retyping the same instruction into chat is the cheapest possible signal that
something belongs in a file. Watch for it: the third time you paste "remember
this repo uses Mongoid, not ActiveRecord", the paste is the rule.

Then decide where it goes, by what should summon it:

- Tied to a file type or directory → a rule, scoped to that glob.
- Tied to a request or an occasion → a skill; `agent-skills` writes those.
- True of the whole repository, every session → the instruction file.

The prompt text usually needs less editing than it seems. Rules read best in the
voice you would have used in chat — a direct instruction with the reason
attached — not in the voice of a specification.
