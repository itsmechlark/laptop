# The gate

Run this against your own output before handing anything back. Every line is
pass or fail — repair what fails and re-run until it passes, rather than noting
it as a caveat in the change summary. Once it passes, stop: further passes make
prose blander, not sharper.

Detection-mode requests stop at [Detect mode](#detect-mode) and skip the rest.

## Voice preserved

Skip this section when the draft was generated rather than written — an agent's
own output, a first pass from a model. There is no voice to protect, and the
checks below would fail a correct edit.

- [ ] The author's point is intact and nothing was added — no claim, example,
      statistic, quote, or opinion they didn't supply
- [ ] Their vocabulary, cadence, bluntness, humor, uncertainty, and digressions
      survive
- [ ] Sentences that were already strong were left alone, not smoothed for
      consistency with the ones around them
- [ ] Cutting was proportional to the slop actually present — no compression
      pass that stripped character along with filler
- [ ] Edge, profanity, jokes, and honest admissions are still there
- [ ] The existing structure survives unless the structure itself was the
      problem
- [ ] Tangled sentences are fixed; spoken cadence, fragments, and shifts of
      pace are not

## The point lands

- [ ] The draft leads with what the reader needs, and any setup that stayed is
      supplying context, tension, or character
- [ ] Every sentence earns its place through a concrete fact, a protected
      detail, or a direct verb
- [ ] Generic sentences pass the portability test, or were cut or made specific
- [ ] Active voice with a human subject wherever the sentence allows it
- [ ] Claims that needed a fact the author didn't supply are flagged, not
      filled in

## Words

- [ ] No banned word survives except where quoted as an example
- [ ] Empty adverbs and filler phrases are gone, except where one is carrying
      emphasis or the author's register
- [ ] No inflated claim stands in for a specific one

## Patterns

- [ ] Binary contrasts, negative listing, rhetorical setups, and throat-clearing
      openers are gone
- [ ] Faux-insight setups, colon reveals, superficial `-ing` analysis,
      fake-strong verbs, synonym cycling, and dramatic fragments are fixed
- [ ] Importance puffery is replaced by the consequence; weasel attribution is
      replaced by a named source, or flagged where no source exists
- [ ] Interpretive metadiscourse is gone — metacommentary, reader guidance,
      emphasis markers, redundant glossing
- [ ] Any fake-profound kicker is deleted, not rewritten into a better metaphor
- [ ] No summary-recap ending; the close lands on something concrete, a
      takeaway, or a next action
- [ ] Formatting slop is gone — emoji headings, decorative bold, bullets that
      wanted to be prose, headings over three lines, empty template sections
- [ ] Mid-sentence colons are followed by lower case unless grammar, a proper
      noun, a title, or a code identifier requires otherwise
- [ ] Em dashes are sparse: none in short copy, one or two in a longer draft

## Final read

- [ ] No robotic symmetry in **your** output — no repeated sentence shapes, no
      stack of punchy fragments, no paragraphs of uniform length
- [ ] The author would recognize this as their own writing
- [ ] It sounds natural read aloud to a sharp colleague
- [ ] The output is the full edited draft plus a **What changed** section of
      three to six lines, not a diff and not a comma inventory
- [ ] Anything deliberately left alone that the author might expect cut is
      named

## Detect mode

- [ ] Every finding names its pattern, quotes the offending line, and gives a
      one-line fix
- [ ] Findings are ordered by how much the fix would improve the draft
- [ ] Nothing was rewritten, nothing was scored, and the text was never claimed
      to be AI-generated
