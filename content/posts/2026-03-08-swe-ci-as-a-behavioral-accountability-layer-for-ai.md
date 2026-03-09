---
title: "Three Ways to Ask 'What Did the AI Actually Do?'"
date: "2026-03-08"
category: "Ops Brief"
excerpt: "Session provenance, AST-native VCS, and CI-integrated evaluation are each answering a different accountability question about AI-generated code. SWE-CI is the one that maps onto how engineering teams already think."
tags: "AI code generation, accountability, CI/CD, version control, SWE-CI, provenance, software quality"
---

Something clarified for me while reading the [SWE-CI paper](https://arxiv.org/abs/2603.03823) this week. The accountability problem for AI-generated code isn't one problem. It's three problems wearing the same label.

Teams reach for "provenance" or "auditability" as though those words describe a single gap. They don't. What the AI said during generation is a different question from how the code is structured, which is a different question from what the code actually does when it runs. Each of those questions has a different answer — and increasingly, a different tool category pointing at it.

Three distinct accountability layers are emerging. They're not competing. They're not even overlapping in the ways people assume. Getting clear on which question each one answers might be the most practically useful framing exercise a small engineering team can do right now.

## The Three Layers, Stated Plainly

**Session provenance** is the accountability record for what happened during generation: what context the model had access to, what it was asked, what it touched, what it returned. This is the layer git was never designed to capture — the commit records the artifact, not the conversation that produced it. I've [written about this before](/posts/2026-03-01-beagle-and-the-version-control-question-ai-generated-code-is-starting-to-ask.html) in the context of MCP logs accumulating session context that version control discards. The accountability question here is: *can we reconstruct what the AI accessed and was instructed to do?* This matters most in regulated contexts — fintech, healthcare, anything where "we don't know what the AI touched" is an unacceptable answer during an incident postmortem.

**Structural provenance** is the accountability record for how the code is represented — not what it says but what it *is*, semantically. This is Beagle's territory: AST-native version control that stores code at the structural layer rather than the textual layer. The underlying observation is that AI generates semantically and git stores textually, and that mismatch throws away meaningful information at every commit. The accountability question here is: *can we compare and track code in a way that reflects its actual structure rather than its surface representation?* This matters most for teams trying to understand code evolution, review AI-generated changes meaningfully, or maintain refactoring visibility without losing structural context in a diff that shows lines changed rather than semantics changed.

**Behavioral provenance** is the accountability record for what the code actually does — not during generation, not at rest, but in motion, over time, under CI. This is SWE-CI's territory. The accountability question here is: *does the code behave correctly, and does it continue to behave correctly as the codebase evolves around it?* This is, notably, also the question that CI was already asking before AI-generated code was a consideration. SWE-CI's contribution is formalizing how agent evaluation maps onto that existing infrastructure.

Three layers. Three different questions. The reason they keep getting conflated is that all three are gaps that standard git-based workflows don't address — but the gaps are at completely different layers of the stack.

## What SWE-CI Actually Measures

The SWE-CI paper's core move is to use CI pass/fail signals as the ground truth for evaluating AI agent capabilities on real codebases. This sounds obvious until you sit with the implications.

Previous agent evaluation benchmarks were mostly synthetic: carefully constructed tasks with known solutions, evaluated against a fixed answer key. Useful for comparing models, not useful for understanding how an agent performs on *your* codebase, *your* dependencies, *your* test suite, running in *your* CI environment. SWE-CI reframes evaluation around the behavioral artifact — the CI run — rather than the generated text artifact.

This has a structural property that matters for practical adoption: it's measuring the thing engineering teams already measure. Pass rates, flakiness, regression patterns, test coverage maintenance — these aren't new metrics that teams need to instrument for. They're the metrics that already live in your CI dashboard. What SWE-CI adds is the agent evaluation layer on top: can the agent maintain these properties over time, across PRs, as the codebase evolves? Can it preserve CI green while making changes, or does it produce code that passes locally and breaks in integration?

The behavioral question is also the question with the most immediate operational stakes. A team that can't answer "what did the AI say during generation?" is missing session accountability — important, but often invisible until something goes wrong. A team that can't answer "how has the code structure changed?" is missing structural visibility — meaningful for review quality, but abstract as a daily concern. A team that can't answer "does the AI's code actually work, and keep working?" has a problem that surfaces immediately, visibly, and in the pipeline they already watch.

This is what makes SWE-CI the most practically adoptable of the three layers, even though it's the least *complete* as an accountability record. It doesn't tell you what context the AI had access to. It doesn't tell you anything about semantic structure or code provenance in the representational sense. It tells you: the code ran, the tests passed or failed, and here's the behavioral signal over time. For a lot of teams, that's the accountability question they're already trying to answer — they just hadn't framed it as an AI accountability question before.

## The Accountability Stack, Not the Accountability Layer

The mistake worth avoiding is treating these as alternatives — choosing one and calling the problem solved.

Session provenance without behavioral provenance tells you what the AI was asked and what it produced, but not whether what it produced was correct. You have a detailed record of a conversation that may have generated a bug. Structural provenance without behavioral provenance gives you semantic visibility into code evolution, but AST-native diffing doesn't catch runtime failures that only surface under load or in integration. Behavioral provenance without the other two gives you CI signals but no reconstruction path when something fails — you know the tests failed, you can see the diff, but you can't recover the context that would tell you *why* the AI made the choice it made.

The realistic near-term picture for most small teams isn't all three layers — it's a sequenced build. And the honest sequencing argument for starting with behavioral provenance is that it asks the same question your existing CI infrastructure already asks, just evaluated explicitly against agent-generated contributions. You're not instrumenting something new; you're applying an existing accountability mechanism to a new source of code.

Session provenance is where the regulatory stakes are highest and the tooling is least mature. Structural provenance is where the long-term review quality argument lives. Behavioral provenance is where the immediate operational leverage is.

The practical question for any team already shipping AI-generated code into production: which of these three questions can you currently answer? If the answer is "none," starting with behavioral accountability is the right entry point — not because it's sufficient, but because it's the layer you're already equipped to reason about. The accountability stack doesn't require you to build all three floors simultaneously. It requires you to know which floor you're on.