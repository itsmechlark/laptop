---
name: alpha
description: Fixture for the orphan-reference and anchor checks. Not a shipped skill — it lives under spec/ so nothing links it into the payload.
---

# Alpha

The assertion is which of this skill's four references the reachability check
reports. Read [LINKED.md](references/LINKED.md) for what each one is for.

## A heading to aim at

Anchor violation 1 — an intra-file link to a heading that isn't here. The
heading above is the only one this file has, so `#a-heading-that-was-renamed`
resolves to nothing and must be reported.

Jump to [the renamed section](#a-heading-that-was-renamed).

Anchor violation 2 — a cross-file link into a heading `LINKED.md` does not
have. The file resolves, which is exactly why the resource-link check stays
quiet about it and this one must not.

See [the shapes](references/LINKED.md#response-shapes).

A link that must stay quiet, so the check is proving discrimination rather than
just counting: [this one](#a-heading-to-aim-at) resolves to the heading above.
