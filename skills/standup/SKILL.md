---
name: standup
description: Write a standup update for a client, manager, or team — identify what was done, what's next, and surface risks before they become surprises. End of day, start of day, or end of week.
argument-hint: "[audience (client|manager|team) and/or context, e.g. 'team, end of week']"
disable-model-invocation: true
---

## Behavior

This is a guided conversation that ends with a polished, ready-to-send update. Start by getting the raw material from the user — then help them sharpen it.

### Step 0: Identify the audience

Who is this update for? It changes everything downstream — how blunt to be, whether jargon is allowed, how it's formatted. Take it from the argument (`client`, `manager`, `team`) or, if it isn't clear, ask once: **"Who's reading this — the client, your manager, or your team?"** Default to **client** if unspecified; it's the most guarded audience, so it's the safe default.

- **Client** — external. Outcomes and trust; no jargon; risks framed around timeline and confidence.
- **Manager / lead** — internal, upward. Progress against the commitment, and above all *where you're blocked or need help*; light jargon is fine.
- **Team** — internal, sideways. Dependencies, decisions, and handoffs; jargon is fine (they know the stack), and terse beats polished.

Carry the audience through the rest of the conversation — below, "the reader" means whichever one you identified.

### Step 1: Gather

Start by checking git for context:

- `git log --since="yesterday" --author=$(git config user.email)` (or the last few days if no recent commits)
- Check for open branches, uncommitted work, open PRs

Then open with:

**"Here's what I can see from git. Before I help you write this — what did you actually spend your time on? Git doesn't always tell the full story."**

Wait for their answer. Git shows commits but misses investigation, debugging, conversations, decisions, and thinking. Their answer fills the gaps.

Then ask:

**"What's the most important thing the reader should know from today — if they read one sentence and nothing else?"**

Wait. This forces them to prioritise. Most updates bury the lead.

Then:

**"Is there anything the reader needs to decide, unblock, or be aware of before your next working session?"**

Wait. This surfaces blockers and risks before they become surprises.

### Step 2: Sharpen — Socratically

Before writing the update, push on what they've said:

**On completeness:**

- "You mentioned [X] — is that done-done, or is there a loose end the reader should know about?"
- "Is there anything you learned today that changes the plan or the estimate?"
- "Are you waiting on anything from the reader's side, or anyone you depend on? Now's the time to ask — don't let it sit."

**On risks — push hard here.** Reframe each for the audience: a client hears timeline and confidence; a manager hears the sprint commitment and where you need help; a teammate hears the dependency or decision that affects their work.

- "Is there a risk here you're not mentioning because you think you can handle it? Those are the ones worth flagging early."
- "If the client asked 'are we on track?' right now — what's your honest answer?"
- "Are you going to hit the next deadline? If there's any doubt, say it now — not the day before."
- "Is there anything that took longer than expected today? If so, does that change the timeline for what comes next?"
- "Are there areas you shipped without full test coverage? What's the QA gap — and does the client know?"
- "Is there a part of this feature that works but you're not confident in — something that could break under edge cases or real load?"
- "Are there any assumptions you're making about the client's infrastructure, data, or users that you haven't verified?"
- "If you got hit by a bus tomorrow, what would fall through the cracks?"

Don't ask all of these — pick the 2–3 most relevant to what they've said. The goal is to catch the thing they'd forget to mention or unconsciously downplay. People instinctively soften risks in updates — push against that.

**On team communication — push here before writing:**

- "Is there something here you need to raise with your team before this update goes out?"
- "Did anything come up today that a teammate needs to know about — a decision you made, a direction you changed, or a dependency you introduced?"
- "Is there a conversation you should have with someone specific before your next working session — beyond this update?"

This matters because the update you're writing isn't the only communication that gets neglected. Internal alignment breaks quietly when people assume teammates will figure it out from the code.

### Step 3: Write the update

Produce a clean, ready-to-send update. Keep it short — readers don't read long updates. Format:

---

**Update: [Date]**

**Done:**

- [Completed items — written as outcomes, not tasks. "Users can now reset their password", not "Implemented password reset controller"]

**In progress:**

- [What's actively being worked on, with brief status. "Billing integration — payment webhooks working, proration logic next"]

**Up next:**

- [What's planned for the next working session]

**Heads up:**

- [Risks, blockers, decisions needed, or anything the reader should be aware of. Omit this section entirely if there's nothing — don't manufacture concern]

---

Tune the format to the audience. The block above suits a **client** or **manager** — for a manager, make "Heads up" explicitly about where you need a decision or help. For a **team**, drop the ceremony: the classic terse standup reads better — **Yesterday** (what you finished), **Today** (what you're picking up), **Blockers** (what's in your way). Same honesty, fewer words.

### Writing principles

- **Outcomes over tasks** — "Users can now do X" beats "Implemented Y controller".
- **Honest over optimistic** — a small concern flagged early builds trust; a surprise later erodes it.
- **Short over thorough** — respect the reader's time. If they want more detail, they'll ask.
- **Jargon depends on the audience** — for a client, write for a smart person who doesn't know your stack ("background processing", not "Sidekiq workers"). For a manager, keep it light. For your team, jargon is fine — they know the stack, so don't dumb it down.
- **No filler** — "Continued working on…" is not an update. Name what changed.

After producing the update, close with:

**"Read it back — does it honestly reflect where things stand? Is there anything you softened that should be said more directly?"**

Wait for their answer. If they identify something, help them reword it clearly — then the update is ready to send.

## Tone

Efficient and honest. This isn't a ceremony — it's a communication tool. Help them say what matters in as few words as possible, without hiding the uncomfortable parts.
