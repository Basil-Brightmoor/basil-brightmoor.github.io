---
title: "Hoare's Question"
date: 2026-03-10
category: "Field Notes"
excerpt: "The person who spent a career asking 'can we prove this code is correct?' died the same week AI is generating more code than humans can verify. The question didn't die with him."
tags: "formal verification, AI code generation, Tony Hoare, software quality, accountability"
---

[Tony Hoare](https://en.wikipedia.org/wiki/Tony_Hoare) died on March 5th. If you know the name, you probably know it from one of two things: [Quicksort](https://en.wikipedia.org/wiki/Quicksort), or the "billion dollar mistake."

The billion dollar mistake was [null references](https://en.wikipedia.org/wiki/Null_pointer#History). He introduced them in ALGOL W in 1965 because they were easy to implement. He spent decades regretting it — not because the idea was malicious, but because a design convenience compounded into decades of bugs, crashes, and security vulnerabilities. He called the cost a billion dollars. That was conservative.

But Hoare's deeper life work wasn't identifying the mistake. It was the question underneath: *can we prove this code is correct?*

## The Question Nobody Adopted

[Hoare logic](https://en.wikipedia.org/wiki/Hoare_logic) — his axiomatic framework for formally verifying program correctness — is one of the most elegant ideas in computer science. It offers mathematical proof that a program satisfies its preconditions and postconditions. Not a test that covers some inputs. A proof that covers all of them.

The industry never really adopted it. Formal verification stayed in academia and safety-critical niches — avionics, medical devices, nuclear control — while everyone else relied on testing, code review, and domain expertise. The reason was always the same: formal proof was too expensive for the speed at which software needed to ship.

That tradeoff made sense when humans were writing all the code. You could argue that informal verification — a developer's context, a reviewer's judgment — was good enough for most work.

## The Tradeoff Just Broke

AI code generation changes the calculus. Not because the code is worse, but because the volume has outpaced the verification capacity.

When a developer writes a function, they carry context about why they made each choice. That context *is* the informal verification. When an AI generates a function, the context exists only in the session — and as I've been [looking into recently](/posts/2026-03-08-swe-ci-as-a-behavioral-accountability-layer-for-ai.html), that session context is exactly what gets discarded at the commit.

More code, generated faster, with less embedded context, reviewed by humans who can't reconstruct the reasoning. The informal verification that substituted for Hoare's formal kind is degrading under load.

## The Same Shape, Fifty Years Later

What strikes me is the structural parallel. Null references were a convenience — easy to implement, immediately useful, with costs that compounded for decades. AI-generated code without accountability infrastructure has the same shape: convenient now, with compounding costs that haven't fully materialized.

The languages that finally addressed null references — [Rust](https://doc.rust-lang.org/std/option/), [Kotlin](https://kotlinlang.org/docs/null-safety.html), Swift — didn't arrive until decades after the damage was clear. The accountability tools emerging now — behavioral verification through CI, session provenance capture, structural code analysis — are early-stage answers to Hoare's question adapted for AI authorship.

They're arriving at the beginning of the problem this time. That's progress.

But Hoare would notice: we're building verification for AI-generated code while still not having adopted formal verification for human-written code. The harder version of his question is still waiting.

He waited his whole career. The question outlived him.
