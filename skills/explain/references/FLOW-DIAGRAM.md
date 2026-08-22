# Flow diagrams

The diagram is the first half of a flow explanation. Its job is to stand alone:
a reader who sees only the diagram should be able to say which states exist,
where the flow branches, and every way it can end.

## What it shows

- **States and transitions** — the lifecycle, not the method calls
- **Decision points** — where the flow branches, phrased as a question
- **Key actions** — what happens at each step, in plain English
- **Terminal states** — every way the flow ends, the failures included

Nothing else. A diagram that mirrors the call graph has the same problem as the
code it was drawn from: it shows structure where the reader needs behavior.

## Conventions

- Box-drawing characters for structure: `┌─┐`, `│`, `├──`, `└──`, `▼`, `◄`
- Entry points named as the thing you could grep for — an HTTP verb and path, a
  queue name, an event name, a task name
- Decision points as a plain-text question with `YES` / `NO` branches
- Actions as short descriptions, never method signatures
- Sub-steps indented under the action they belong to
- One diagram per flow. If it will not fit, the subject is two flows — say so,
  and diagram the one that was asked for

## Worked example: password reset

The two halves of the deliverable, at the level of detail to aim for.

```
                    ┌──────────────────────┐
                    │ User forgot password │
                    └──────────┬───────────┘
                               │
                               ▼
                    POST /passwords (email)
                               │
                       user found by email?
                      ┌────────┴────────┐
                      │ NO              │ YES
                      ▼                 ▼
                 (same response)   Generate reset token
                      │                 │
                      │            Send reset email
                      │                 │
                      └────────┬────────┘
                               │
                               ▼
                  redirect to login ("Check your email")
                               │
                               │
                    ┌──────────┴───────────┐
                    │  User clicks email   │
                    └──────────┬───────────┘
                               │
                               ▼
                  GET /passwords/:token/edit
                               │
                        token valid?
                      ┌────────┴────────┐
                      │ NO              │ YES
                      ▼                 ▼
                redirect to         render password
                new_password_path   reset form
                                        │
                                        ▼
                              PATCH /passwords/:token
                                        │
                                 password valid?
                               ┌────────┴────────┐
                               │ NO              │ YES
                               ▼                 ▼
                          render form       Update password
                          with errors       Clear reset token
                                                │
                                           Log user in
                                                │
                                                ▼
                                        redirect to dashboard
```

### Entry points

1. **User submits email** — `POST /passwords` looks up the user and sends a reset email. Returns the same response whether the user exists or not, to prevent email enumeration.
2. **User clicks reset link** — `GET /passwords/:token/edit` validates the token and renders the password form if it holds.
3. **User submits new password** — `PATCH /passwords/:token` updates the password and logs the user in.

### Branching logic

- **User existence**: the email lookup decides whether a reset email is sent, but the HTTP response is identical either way — no information leakage.
- **Token validity**: the token must exist and not be expired. Invalid tokens redirect back to the "forgot password" form.
- **Password validation**: `has_secure_password` validates presence, length, and confirmation match.

### Side effects

- **Reset token written to the database** — stored as a SHA256 digest, not plain text
- **Email enqueued** — `PasswordMailer.reset_instructions`, delivered via a background job (Sidekiq)
- **Session created** — the user is logged in automatically after a successful reset
- **Token cleared** — an `after_update` callback removes the reset token so it cannot be reused
