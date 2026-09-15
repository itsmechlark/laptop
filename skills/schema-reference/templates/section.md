# Section scaffold

One section per domain. Copy the block below, fill it in, delete the guidance
lines. The five parts stay in this order in every section — a reader learns the
shape once and then navigates by it.

Omit a part only where it is genuinely empty. An empty heading costs a reader a
stop and teaches them to skim.

---

## <Domain name — no number>

<One paragraph: what these models are collectively for, and what this section is
*not*. The "not" line is what stops the next person building a second events
system inside groups, or a second suspension flag inside moderation.>

### Models

| Model | Intent | Source of truth |
| --- | --- | --- |
| `Model` | One line: what it is for, not what columns it has | The model, or the model it defers to |

<Every model in this domain gets a row. Promote one to a `####` heading below
the table only when it carries an invariant a reader will otherwise violate — a
counter that isn't authoritative, a soft-delete preserving audit history, a read
model that must never decide authorization. Default to a row.>

### Invariants

<What must stay true, stated so a reviewer can check it against a diff:
database CHECKs and partial unique indexes and what they enforce, which table
wins when two could hold the same fact, and what the code must never add. Skip
anything the schema file already says plainly — types, nullability, plain
foreign keys.>

### Integration

<Which other domains this one composes, and what it deliberately does not
reproduce. Name the direction: this section reads X, X never reads this.>

### When changing

<A review checklist — the models, contracts, routes, and generated artifacts
that move together with this domain. This is the part a future agent actually
uses, so name real paths.>
