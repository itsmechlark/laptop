# Interviewing a product manager

The person answering is usually a product manager with no programming
background. Everything in this file is about what they see and hear; the
technical work behind it stays yours.

## How a question is shaped

Every question carries three parts, in this order:

1. **The question**, in one sentence, in the words the business uses.
2. **Why it matters**, in one line — what the answer decides. "This decides
   what we'll check afterwards to know it worked."
3. **Two or three example answers**, drawn from the conversation so far, so the
   PM can pick one, correct one, or say none fit.

```text
Who runs into this most often?
This decides who we design for first.
For example: front-desk staff during the dinner rush, the manager closing out
the day, or guests booking from their phone. Or someone else?
```

Examples anchor. If the PM picks the first example every time, the examples are
leading them — ask the next question open and offer examples only if they stall.

"I don't know" is a complete answer. Record it as an open question, ask who
would know, and move on.

## The question bank

Ask only what the conversation hasn't already answered, one at a time.

**Who has the problem**

- Who runs into this most often?
- Is there anyone this should deliberately *not* change things for?

**How often, and what it costs** — one question between them, only when the
size of the problem is genuinely unknown:

- How often does this happen, and what does it cost the person when it does —
  time, money, a complaint, a mistake?
- What do people do about it today?

**How we'd know it worked**

- What number would you check afterwards to know this worked, and who gives it
  to you today?

Whether anything counts that number today is yours to check, not theirs. If
nothing does, tell them — "nobody counts this today, so we'll need a way to
count it" — and that becomes a requirement in the document.

**What's deliberately out**

- What have people already suggested that this should *not* include?
- What's the closest thing to this that we're leaving for later?

**Why now**

- What changed that makes this worth doing now — or what is it holding up?

## When the PM brings a technical answer

PMs often pass along what an engineer told them: "we need a webhook", "just add
a column", "it's an API thing". Don't argue and don't echo it. Ask what it would
let someone do:

```text
What would that let the restaurant do that they can't do today?
```

Put the answer in the Problem or Outcome. Record the technical term itself under
**Open questions** as a suggested approach for engineering to weigh, so it
isn't lost and isn't decided.

## Saying technical things in product words

| What you're doing or finding | What the PM hears |
| --- | --- |
| Reading the glossary or code to check current behavior | "Checking whether the product already handles this…" |
| A hit in an out-of-scope knowledge base | "This was considered before and set aside because…" |
| An existing ADR that constrains the work | "Engineering has already decided … and this needs to work within that." |
| No instrumentation for a success measure | "Nobody counts this today — we'll need a way to count it." |
| The approach, the design | "how engineering will build it" |
| Code that can't confirm current behavior | "I couldn't confirm whether the product does this today — I've noted it as an assumption." |
| Offering to save to `docs/prds/` or `~/.agents/prds/` | "Want me to save a copy for the engineering team?" — then who can see it, per step 4 of the skill |
| Publishing to a tracker or wiki | "Want me to post this to Jira?" — naming the team's own tool, and wait for the yes |
| Handing off to `brainstorming`, `slice`, `draft-spec`, or `grilling` | See [Handing it on](#handing-it-on) |
| The job-story Outcome form | "what someone can do once this is done" |
| Frontmatter, Markdown, YAML | Never mentioned |

## Showing the draft

Deliver it in the chat as a clean document the PM can paste into Jira,
Confluence, or a doc — headings and bullets, no frontmatter block. Then ask:

```text
Does this match what you meant? Anything to change, add, or take out?
```

Read silence or "looks fine" after a long draft cautiously. Point at the one
section most likely to be wrong — usually **Out of scope** or an assumption you
supplied — and ask about that specifically.

## Handing it on

Give one next step, in plain words, matched to the route in step 4 of the
skill:

- How to build it isn't decided: "Share this with your engineering lead —
  they'll work out how to build it."
- It's large and the approach is settled: "Engineering can break this into
  pieces that ship one at a time."
- One agreed piece needs build detail: "Engineering can write up the build
  details for this piece."
- Only when the PM asks for the draft to be challenged: "Happy to — I'll poke
  holes in it one question at a time."

If the PM wants to carry on into the engineering work themselves, say first that
the conversation will get more technical from there.
