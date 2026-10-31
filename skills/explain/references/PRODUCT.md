# Explaining to a product reader

The reader is a product manager, designer, or support lead who wants to know how the product behaves today. Everything in this file is about what they read; the research behind it is the same as for an engineer, and stays yours.

## Saying technical things in product words

| What you found | What the reader gets |
| --- | --- |
| A route or endpoint | The action a person takes: "the guest taps Cancel in the booking widget" |
| A background job | "A few minutes later, the system…" |
| A feature flag or config value | "A setting each restaurant can turn on" — and say which way it is by default, if known |
| A callback or observer side effect | "It also…" |
| An outbound call to a provider | The partner the business knows ("the payment provider"), or "the payment system" |
| A validation or guard clause | The rule, in business terms: "a booking can't be changed less than 2 hours before it starts" |
| An authorization check | Who can do it: "only managers" |
| A path you could not settle (dynamic dispatch, runtime config, another service) | "I couldn't confirm whether…", with what would settle it, in product words |
| An entry point that is a scheduled task or webhook | "Automatically, every night…" or "when the partner tells us…" |

Use the project's glossary vocabulary for domain terms, never a code identifier that sits beside it.

## Diagrams

The box-drawing conventions in [FLOW-DIAGRAM.md](FLOW-DIAGRAM.md) apply unchanged, with two differences: entry points are named as user actions rather than as a verb and path, and decision points are business questions ("Is the booking within 24 hours?"). Actions are short plain phrases. No route, class, or job name appears in the diagram.

## Worked example: a product answer

Question: "Can staff refund part of a deposit?"

> **Answer.** Yes, but only a manager can, and only while the booking is still open.
>
> **When and how.** A manager opens the booking, chooses Refund, and enters an amount up to what the guest paid. The guest gets an email confirming the amount.
>
> **Limits and exceptions.**
> - Front-desk staff don't see the Refund option.
> - Once a booking is marked completed, the option goes away.
> - A refund can't be larger than the deposit.
>
> **What I couldn't confirm.** Whether the money reaches the guest's card immediately or after a delay depends on the payment provider, which I couldn't check from here.

## Worked example: a flow in product words

The password-reset flow from [FLOW-DIAGRAM.md](FLOW-DIAGRAM.md), summary only.

**Ways it starts**

1. A person says they forgot their password and enters their email. The system always shows "Check your email", whether or not that address has an account, so nobody can use the form to find out who is registered.
2. They click the link in the email. If the link is still good, they see a form for a new password; if not, they go back to the start.
3. They submit a new password.

**What decides the outcome**

- Whether the email matches an account decides if an email is sent. The person sees the same message either way.
- The link must exist and not have expired.
- The new password must meet the strength and confirmation rules; if it doesn't, they see the form again with what to fix.

**What else happens**

- A reset email is sent a few moments after the request.
- On success the person is signed in straight away.
- The link stops working once it has been used.
