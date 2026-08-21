# Visual companion guide

**Architectural path only.** Spike and bounded work never offers the companion —
those paths are too short to earn a browser round-trip.

Browser-based visual companion for showing mockups, diagrams, and design options
during brainstorming. Available as a tool — not a mode. Accepting the companion
means it's available for questions that benefit from visual treatment; it does NOT
mean every question goes through the browser.

## When to use

Decide per-question, not per-session. The test: **would the user understand this
better by seeing it than reading it?**

**Use the browser** when the content itself is visual:

- UI mockups — wireframes, layouts, navigation structures, component designs
- Architecture diagrams — system components, data flow, relationship maps
- Side-by-side visual comparisons — comparing layouts, color schemes, design
  directions
- Design polish — look and feel, spacing, visual hierarchy
- Spatial relationships — state machines, flowcharts, entity relationships

**Use the terminal** when the content is text or tabular:

- Requirements and scope questions — "what does X mean?", "which features?"
- Conceptual A/B/C choices — picking between approaches described in words
- Trade-off lists — pros/cons, comparison tables
- Technical decisions — API design, data modeling, architectural approach
- Clarifying questions — anything where the answer is words, not a visual
  preference

A question *about* a UI topic is not automatically a visual question. "What kind
of wizard do you want?" is conceptual — use the terminal. "Which of these wizard
layouts feels right?" is visual — use the browser.

## Offering the companion

Do NOT offer it upfront. Wait until a question would genuinely be clearer shown
than told — a real mockup, layout, or diagram question, not merely a UI *topic*.
The first time that happens, offer it as its own message:

> "This next part might be easier if I show you — I can put together mockups and
> comparisons in a browser tab. It's token-intensive, so only worth it if seeing
> it would help. Want me to?"

**This offer must be its own message** — no clarifying question or other content.
Wait for the user's response. If they decline, continue text-only and don't offer
again unless they raise it.

## How it works

Write HTML mockup files and open them in the user's browser. Two approaches are
available depending on the tools in the session:

### Using agent-browser

The `agent-browser` skill provides fast browser automation via CDP. Before using
it for mockups, load the actual workflow from the CLI — the SKILL.md is a
discovery stub, not the usage guide:

```bash
agent-browser skills get core
```

Use whatever commands the loaded workflow provides for opening a local file URL
(`file://$TMPDIR/mockup-layout.html`), taking a screenshot, and reading the
page state. Do not guess at commands — the CLI surface may change between
versions.

### Using a browser MCP server

If the session has browser tools from an MCP server (Chrome DevTools MCP, or
whatever the host provides), use them directly: navigate to the mockup's
`file://` URL, screenshot it, and read the page when you need its structure.
Check the tool names available in the session rather than assuming them — they
differ between servers and change between versions.

Two constraints worth knowing before you reach for them:

- **Reuse a page instead of opening one.** Opening a new page can be
  approval-gated (`new_page` sits in this repo's `permissions.ask` list), so
  navigating an existing page avoids a prompt on every iteration.
- **Script evaluation may be denied outright.** Don't design the loop around
  running JavaScript in the page; put everything the user needs into the HTML.

## The loop

1. **Write HTML** to a file in `$TMPDIR` — use semantic filenames:
   `layout-options.html`, `wizard-flow.html`, `dashboard-mockup.html`
2. **Open in browser** via `agent-browser` or the session's browser MCP tools
3. **Tell the user what to expect** — brief text summary of what's on screen,
   ask them to respond in the terminal
4. **Get feedback** — the user's terminal response is the primary input
5. **Iterate or advance** — if feedback changes the current screen, write a new
   version (`layout-options-v2.html`). Only advance when the current step is
   validated.
6. **Unload when returning to terminal** — when the next step doesn't need the
   browser (a clarifying question, a trade-off discussion), say so and move on.
   Don't leave a stale mockup on screen while the conversation has moved past it.

## Writing mockup HTML

Start from [`assets/mockup-template.html`](../assets/mockup-template.html) —
copy it to `$TMPDIR`, replace the question and the options, and delete the
wireframe blocks this question doesn't need. It's a self-contained page: styles
inline, no external dependencies, and a `prefers-color-scheme` palette so it
reads in a dark browser as well as a light one.

What the template carries:

- An A/B (or A–D) option grid — the shape most design questions take
- Wireframe blocks as commented-out markup keyed to CSS classes: navbar,
  sidebar-plus-content split, image placeholder, mock input and button
- Theme tokens (`--bg`, `--fg`, `--muted`, `--line`, `--panel`, `--accent`) —
  use these instead of hardcoding colors, or the mockup only works in one theme

For anything the template doesn't cover, keep writing plain semantic HTML with
an inline `<style>`. No framework, no CDN — the file has to open from `file://`
with no network.

## Design tips

- **Scale fidelity to the question** — wireframes for layout decisions, higher
  fidelity for visual style questions
- **Explain the question on each page** — "Which layout feels more
  professional?" not just "Pick one"
- **2–4 options max** per screen
- **Use real content when it matters** — placeholder content can obscure design
  issues that surface only with real text lengths and structures
- **Keep mockups simple** — focus on layout and structure, not pixel-perfect
  design. The goal is to communicate an idea, not ship a prototype.
