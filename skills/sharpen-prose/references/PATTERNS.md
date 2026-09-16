# Words and patterns to cut

The long-form taxonomy behind AGENTS.md §8 (*Writing for a human reader*). §8
names five hype adjectives and four throat-clearing phrases because it loads
into every session and has to stay short. This is the full list.

Every pattern below has a name on purpose. Half of them are invisible in your
own draft until you can say what they are, and a named pattern is something the
author can check; "this feels AI-ish" is not.

## Words to cut

**Banned outright.** These are dead on arrival in prose a person reads:

> delve, foster, leverage, utilize, facilitate, empower, streamline, robust,
> cutting-edge, paradigm shift, game changer, tapestry, realm, beacon,
> multifaceted, meticulous, intricate, paramount, transformative, elevate,
> embark, supercharge, harness, ever-evolving

Plus the inflated claim as a sentence: "this is huge", "this changes
everything". §8 adds *comprehensive*, *seamless*, *powerful*, and
*significantly* to the list.

**Often empty, sometimes not.** Cut these when they stall the point; keep them
when they carry emphasis or the author's register:

> just, literally, honestly, simply, actually, crucially, essentially, really

**Filler phrases.** Same test, but they survive far less often:

> it's worth noting that, at the end of the day, in today's world, when it
> comes to, the fact of the matter is, needless to say, in order to

Two standing exceptions: a word quoted as an example of bad writing, and a word
that is already an identifier, a field name, or someone else's title. Never
"correct" those.

## Patterns to cut

### 1. Binary contrasts

The "not just X, it's Y" construction, and its cousins ("less about X, more
about Y", "X isn't the problem — Y is"). It manufactures an insight by
inventing a foil nobody proposed.

```
Bad:  This isn't just a caching layer, it's a rethink of how the request
      lifecycle works.
Good: The caching layer moved into the request lifecycle, so a cache miss no
      longer costs a second round trip.
```

### 2. Throat-clearing openers

Sentences that announce the subject instead of saying something about it. "In
this document we'll explore", "This PR aims to", "Let's dive in", "First, some
context". Delete and start at the second paragraph.

### 3. Faux-insight setups

"Here's the thing", "But here's what's interesting", "And that's the part most
people miss". A drum roll ahead of an ordinary fact. Cut the drum roll; if the
fact can't carry itself, the fact is the problem.

### 4. Colon reveals

A short clause, a colon, then the payoff — "The result: a 40% drop." Once is
fine. Three times in a page is a tic, and it flattens sentences that wanted
different shapes.

### 5. Superficial analysis

The trailing `-ing` clause that restates the sentence as though interpreting
it: "…, highlighting the need for better observability", "…, demonstrating the
value of early testing". It adds no information and reads as a model marking
its own homework.

```
Bad:  We added a retry, reducing timeouts by half and showing the importance
      of resilient design.
Good: Adding the retry halved the timeouts.
```

### 6. Importance puffery

Telling the reader something matters instead of showing why. "Critically",
"importantly", "it cannot be overstated", "a key consideration". If it matters,
the consequence says so.

### 7. Interpretive metadiscourse

Prose about the prose: authorial metacommentary ("as we saw above"), reader
guidance ("keep this in mind as you read"), emphasis markers ("note that"), and
redundant glossing ("in other words", followed by the same sentence). §8's "no
invented subsection labels" is this pattern wearing bold text.

### 8. Weasel attribution

"Studies show", "experts agree", "it's widely believed", "many teams find".
Either name the source or drop the claim. In an ADR or a PRD this is the most
expensive pattern on the list — an unsourced assertion is indistinguishable
from a researched one on the page, and the next reader inherits it as fact.

### 9. Fake-strong verbs

Verbs that perform force without doing work: *unlock*, *drive*, *deliver*,
*enable*, *surface*, *unpack*, *tackle*, *navigate*, *spearhead*. Replace with
the plain verb for what happened.

```
Bad:  The change unlocks faster onboarding and drives adoption.
Good: New accounts skip the email step, so setup is two screens instead of four.
```

### 10. Synonym cycling

Rotating through words for the same thing to avoid repetition — "the endpoint",
then "the route", then "the handler", then "the API surface" — when they are one
thing. Repeat the noun. In technical writing the vocabulary is the contract, and
a synonym reads as a second concept.

### 11. Negative listing

Defining something by what it isn't, at length. One negation can sharpen a
boundary; a stack of them ("it's not a framework, not a library, not a
compiler") is a paragraph that has said nothing yet.

### 12. Dramatic fragmentation

One-word or one-clause sentences deployed for weight. "Every time. No
exceptions. That's the whole trick." A fragment is fine; a run of them is a
cadence nobody speaks in.

### 13. Robotic rhythm

Sentences of near-identical length and shape, paragraph after paragraph — the
uniformly-hedged, em-dash-heavy cadence that §8 calls the giveaway. The fix is
variation, not shorter sentences. **Check your own output for this one**: a tidy
edit produces it reliably.

### 14. Rhetorical setups

Questions asked so the author can answer them. "So what does this mean for
your team?" "Why does this matter?" Ask a question only when it's genuinely
open, which in a PR description or a design doc is nearly never.

### 15. Fake-profound kickers

The closing flourish that reaches for significance the piece didn't earn. "And
that's what good engineering really looks like." "Sometimes the best code is
the code you delete." Delete the line — do not rewrite it into a better
metaphor. The paragraph above it was the ending.

### 16. Summary-recap endings

A final paragraph restating what the reader just read. "In summary", "to recap",
"as we've seen". Close on something concrete instead: a takeaway, a number, a
next action, or nothing.

### 17. Formatting slop

Structure the reader didn't ask for. Emoji in headings, bold applied to a phrase
for decoration rather than reference, a bulleted list where two sentences of
prose would read better, a heading over three lines of text. §8's "don't fill a
template's empty sections" belongs here too — a heading with nothing under it
teaches the reader to skim.

Also: a colon inside a sentence is followed by lower case unless grammar, a
proper noun, a title, or a code identifier says otherwise.

### 18. Em dashes

Keep them sparse. None in short copy; one or two in a longer piece, where the
interruption is doing something a comma can't. Density is the tell, not the
character — replacing all of them with colons trades one tic for another.
