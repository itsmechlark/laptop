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
> comparisons in a browser tab. Want me to?"

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

### Using Chrome DevTools MCP

If a Chrome DevTools MCP session is active, use its tools directly:

1. Write the HTML mockup to a file
2. Open it with `new_page` or `navigate_page` using a `file://` URL
3. Use `take_screenshot` to capture and show to the user
4. Use `take_snapshot` to read the page's accessibility tree for interaction

## The loop

1. **Write HTML** to a file in `$TMPDIR` — use semantic filenames:
   `layout-options.html`, `wizard-flow.html`, `dashboard-mockup.html`
2. **Open in browser** via `agent-browser` or Chrome DevTools MCP
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

Write self-contained HTML files. Include all styles inline — no external
dependencies.

### Minimal example — A/B choice

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Layout Options</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }
  h2 { margin-bottom: 0.25rem; }
  .subtitle { color: #666; margin-top: 0; }
  .options { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem; }
  .option { border: 2px solid #e0e0e0; border-radius: 8px; padding: 1.5rem; }
  .option h3 { margin-top: 0; }
  .letter { font-size: 1.5rem; font-weight: bold; color: #666; margin-bottom: 0.5rem; }
</style>
</head>
<body>
  <h2>Which layout works better?</h2>
  <p class="subtitle">Consider readability and visual hierarchy</p>
  <div class="options">
    <div class="option">
      <div class="letter">A</div>
      <h3>Single Column</h3>
      <p>Clean, focused reading experience. Content flows top to bottom.</p>
    </div>
    <div class="option">
      <div class="letter">B</div>
      <h3>Two Column</h3>
      <p>Sidebar navigation with main content area. Better for complex apps.</p>
    </div>
  </div>
</body>
</html>
```

### Wireframe building blocks

Use simple CSS to represent UI elements:

```html
<!-- Navigation bar -->
<div style="background:#f5f5f5; padding:0.75rem 1rem; border-bottom:1px solid #ddd; display:flex; gap:1rem; align-items:center;">
  <strong>Logo</strong> <span>Home</span> <span>About</span> <span>Contact</span>
</div>

<!-- Sidebar + content layout -->
<div style="display:flex; min-height:400px;">
  <div style="width:200px; background:#fafafa; border-right:1px solid #eee; padding:1rem;">Sidebar</div>
  <div style="flex:1; padding:1rem;">Main content area</div>
</div>

<!-- Placeholder block -->
<div style="background:#f0f0f0; border:2px dashed #ccc; padding:2rem; text-align:center; color:#999;">
  Image placeholder (400×300)
</div>

<!-- Mock form elements -->
<input style="border:1px solid #ccc; padding:0.5rem; border-radius:4px; width:200px;" placeholder="Input field" disabled>
<button style="background:#2563eb; color:white; border:none; padding:0.5rem 1rem; border-radius:4px;">Action</button>
```

### Side-by-side comparison

```html
<div style="display:grid; grid-template-columns:1fr 1fr; gap:2rem;">
  <div>
    <h3>Option A</h3>
    <!-- mockup content -->
  </div>
  <div>
    <h3>Option B</h3>
    <!-- mockup content -->
  </div>
</div>
```

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
