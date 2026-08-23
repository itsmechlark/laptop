# The sharpening bank

Questions for Step 3, grouped by what each group surfaces. **Ask two or three,
never the group.** A questionnaire turns a five-minute conversation into a chore
and trains the user to answer it in single words, which is the opposite of what
this step is for.

## Choosing

Pick by what the user actually said, in this order of preference:

1. **The thing they said quickly and moved past.** Speed is the tell. A risk
   mentioned in a subclause is a risk they have already decided not to raise.
2. **The claim with no evidence behind it.** "That's basically done", "should be
   fine", "just needs testing" — each is a conclusion whose working is missing.
3. **The gap between the repository and their account.** Three days of commits
   on a branch they didn't mention, or a whole day they described with nothing to
   show, both mean something is unsaid.

If none of those apply, the update is probably in good shape. Ask the date
question and move to writing.

## Completeness

- "You mentioned [X] — is that done-done, or is there a loose end the reader
  should know about?"
- "Is there anything you learned that changes the plan or the estimate?"
- "Is there anything you started and backed out of? That's often worth a line —
  it tells the reader an approach was ruled out rather than never tried."
- "Are you waiting on anything from the reader's side, or from anyone you depend
  on? Now's the time to ask — don't let it sit until the next update."

## Risk

The group that matters most, and the one people answer defensively. Push here.

- "Is there a risk you're not mentioning because you think you can handle it?
  Those are the ones worth flagging early."
- "If the reader asked 'are we on track?' right now — what's your honest
  answer?"
- "Is there a part of this that works but you're not confident in — something
  that could break under edge cases or real load?"
- "Are there assumptions you're making about their infrastructure, their data,
  or their users that you haven't actually verified?"

## Dates and estimates

- "Are you going to hit the next deadline? If there's any doubt, say it now —
  not the day before."
- "Did anything take longer than you expected? Does that change the timeline for
  what comes next, or was it absorbed?"
- "Is the estimate you gave still the estimate you'd give today?"

When the answer to the first is no, stop and route it into a conversation before
the update goes out — see Step 3 in the `SKILL.md`. A date slipping for the first
time inside a broadcast update is the failure this group exists to prevent.

## Quality gaps

- "Is there anything you shipped without the test coverage you'd want? What's
  the gap, and does the reader need to know about it?"
- "Is there anything live right now that you'd want to be told about if it
  broke over the weekend?"
- "Did you leave a `TODO` or a shortcut behind that someone should know exists?"

Report the gap, not a confession. "The refund path has no automated coverage for
partial amounts yet" is useful to a reader; a paragraph of self-criticism is not.

## Continuity

- "If you were off tomorrow, what would fall through the cracks?"
- "Is there anything only you currently know how to run, deploy, or fix?"

Cheap to ask, and it surfaces the single-point-of-failure work that never makes
it into any update because it never feels like news.

## Internal alignment

Not for this update — for the conversation the update doesn't replace.

- "Is there something here you need to raise with your team before this goes
  out?"
- "Did anything come up that a teammate needs to know — a decision you made, a
  direction you changed, or a dependency you introduced?"
- "Is there a conversation you should have with someone specific before your
  next working session, beyond this update?"

Ask one of these before writing, whatever the audience. Internal alignment
breaks quietly: everyone assumes the code will explain itself, and the update to
the client goes out while a teammate is still building against the old
assumption.
