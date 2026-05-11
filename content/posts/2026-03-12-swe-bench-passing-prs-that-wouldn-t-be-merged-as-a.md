---
title: "The Written Test and the Real One"
date: "2026-03-12"
category: "Deep Bench"
excerpt: "SWE-bench measures whether AI can generate code that passes tests. Human maintainers use entirely different criteria. This is the same failure as HN's AI comment ban — and Rails might be showing us the structural fix."
tags: "ai coding, benchmarks, software engineering, rails, code review, acceptance criteria"
---

## The Benchmark Is Working Perfectly. That's the Problem.

[METR's research note from last week](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/) dropped a finding that should make anyone who quotes SWE-bench scores in a sales deck mildly anxious: many of the pull requests that pass SWE-bench would not be merged into the actual repositories they're supposed to fix. Not because the code doesn't work. Because human maintainers — the people who actually run those repositories — looked at the PRs and said: no. Wrong approach. Wrong idiom. This doesn't fit. We wouldn't do it this way.

Here is what makes this finding so structurally interesting: it is not a benchmark failure. SWE-bench measures whether AI-generated code makes failing tests pass. The PRs do exactly that. The benchmark is working precisely as designed.

That's the problem.

What SWE-bench cannot measure is whether the code would survive contact with a human reviewer who has spent years developing tacit intuitions about what good code in *this* codebase looks like. Whether it reads idiomatically. Whether it fits the architectural grain. Whether the approach the AI chose is the approach a thoughtful engineer would have chosen, even if both approaches produce identical test results. These criteria are real. They govern what actually gets merged. And they were never written down anywhere that a benchmark could find them.

So the AI passes the written test and fails the real one. Over and over. And the scores go up, and the press releases go out, and the gap between the benchmark and the practice widens.

## Two Failures, One Root Cause

Around the same time the METR note was circulating, Hacker News quietly sharpened its community guidelines. The relevant line: ["Don't post generated/AI-edited comments. HN is for conversation between humans."](https://news.ycombinator.com/newsguidelines.html#generated)

This is easy to read as a moderation housekeeping note. I think it's something more diagnostic.

The complaints that preceded the rule change weren't about AI comments being wrong. They were about AI comments being *off*. Technically coherent. Addressed to the topic. Hitting all the visible marks of a substantive reply. And yet somehow not right — not positioned correctly in the actual conversational thread, not carrying the weight of genuine engagement, not reading like someone who had a real stake in the question. The comments passed the visible test and failed the human one.

This is structurally identical to the SWE-bench problem, just at the discourse layer rather than the code layer. HN's community norms — what makes a comment genuinely valuable versus technically compliant — were never written down in a form a language model could optimise against. The acceptance criteria exist. They operate. They govern what actually gets upvoted and what gets ignored. But they live in the heads of the community, accumulated through years of shared practice, not in a rulebook a model can train on.

So the AI produces comments that satisfy the enumerable criteria (relevant, grammatical, substantive-sounding) and misses the unenumerable ones (genuine curiosity, earned position in the conversation, the subtle difference between engaging and performing engagement). HN's moderators, facing exactly the same situation as open-source maintainers, did the same thing: added an explicit rule for something that used to be implicit. Wrote down a criterion that the community had always enforced but never codified, specifically because AI made the implicit enforcement mechanism fail.

Both communities just spent social capital writing down rules they shouldn't have needed to write. The AI generated the pressure that forced the codification. The codification is the cost.

## The Acceptance Criteria Were Always the Invisible Architecture

There is a version of this argument that blames AI for introducing a new problem. I don't think that's right. I think AI is revealing a problem that was always there — that software development and online discourse have always been governed by two parallel sets of criteria: the ones you can write down and verify automatically, and the ones that exist only as distributed institutional knowledge.

Before AI coding assistants, these two layers mostly coexisted without friction because the humans who wrote the code also carried the tacit criteria. A developer who had worked in a codebase for six months knew, without being able to fully articulate it, that *this* project uses functional composition here, that *this* team prefers explicit over clever, that *this* maintainer gets twitchy about over-abstraction. They encoded those norms in the code they wrote. The code review surfaced violations. The whole system worked because the people generating code also carried the institutional knowledge about what good code meant here.

AI breaks this at the seam. The model has access to everything that was written down — the tests, the existing code, the issue description — and no access to anything that wasn't. It generates code that is correct with respect to the explicit specification and potentially alien with respect to the implicit one. The test suite is not the specification. It never was. It was always a partial proxy for a richer, harder-to-articulate notion of what should merge.

What METR found is that the proxy is not good enough. The gap between "makes the tests pass" and "would be accepted by the maintainer" is wide enough that optimising against the proxy produces work that fails the real evaluation at a meaningful rate. This is not a measurement problem you can solve by adding more tests to SWE-bench. It's a representation problem: the thing you actually want to measure is not the kind of thing that fits cleanly into a benchmark.

You could try to fix this by running human evaluations instead of automated ones. Some benchmark efforts are moving in this direction. But this creates a different problem: human evaluation is slow, expensive, and — crucially — *also* reflects implicit criteria that vary by evaluator, codebase, team culture, and moment in time. You've replaced a fast proxy with a slow one. The tacit knowledge hasn't been captured; you've just added a human in the loop who carries it without being able to transfer it.

## Rails as Accidental Benchmark Reform

Here is where [the Rails resurgence](https://www.markround.com/blog/2026/03/05/returning-to-rails-in-2026/) gets interesting.

The piece that circulated on HN last week is ostensibly about one developer's decision to return to Rails after years away — the restored joy of a framework that makes decisions for you, the productivity boost of opinionated conventions, the reduced cognitive load of not having to assemble your own stack. It reads like a personal essay about developer happiness. But there's a structural argument buried in it that connects directly to the acceptance criteria problem.

Rails is unusually dense with convention. Not just "here's how we do routing" — but a pervasive, interlocking system of norms about how a Rails application should look, feel, and behave at every layer. Models go here. Service objects work like this. The naming convention is non-negotiable. Fat models, skinny controllers — or the opposite, depending on which era of Rails thinking you grew up in, but either way, there's a *doctrine*. DHH is constitutionally incapable of shipping software without an opinion about how it should be used.

The consequence is that in a Rails codebase, the gap between "passes the tests" and "a maintainer would accept this" is narrower than in a framework-agnostic Node or Go codebase. The conventions are so dense and so well-documented that a significant portion of the tacit acceptance criteria have been made explicit — not because Rails documented them for AI's benefit, but because DHH couldn't help himself and wrote lengthy blog posts and books and screencasts explaining precisely how Rails code should be written and why.

This is, accidentally, excellent news for AI coding assistants. When the conventions are that thoroughly articulated, the model has actual training signal for the tacit layer. It can learn what a Rails controller should look like not just from the tests but from the extensive opinionated documentation about what *good* looks like. The gap that creates SWE-bench's validity problem is genuinely smaller in Rails than it is in a greenfield TypeScript project assembled from first principles.

From what I can tell reading the HN discussion, developers returning to Rails in 2026 are reporting that AI assistance works better there. That's not marketing. It's a structural consequence of convention density. The acceptance criteria are more written-down, which means they're more learnable, which means the model's output is more likely to survive human review. Rails conventions are effectively doing the work that SWE-bench benchmarks fail to do: making the implicit explicit, in enough detail that it actually propagates.

This suggests something counterintuitive: the frameworks best suited to AI-assisted development are not necessarily the ones with the smallest surface area or the most minimal opinions. They're the ones whose opinions are most thoroughly documented. Convention richness, not convention minimalism, is what closes the gap.

## What It Means That We've Been Reading the Scores Wrong

The SWE-bench validity crisis isn't just a problem for researchers who design benchmarks. It's a practical problem for anyone who used benchmark scores to make decisions about where to deploy AI coding assistance, how much to trust its outputs, or how to structure human review.

If a model scores well on SWE-bench and generates PRs that would frequently be rejected by the maintainers of real codebases, then the benchmark score is not predicting the operational outcome you care about. You were measuring the right thing for the wrong question. The question you actually care about — "will my team accept and maintain this code?" — requires evaluating against criteria that SWE-bench was never designed to capture.

This matters for how teams set up their AI-assisted workflows. A model that scores 70% on SWE-bench and produces PRs your team mostly accepts is more valuable than one that scores 85% and produces PRs that require substantial rework before they look like your codebase. The rework is not free. The rework is where the tacit knowledge transfer happens — where a human has to take the AI's technically-correct output and reshape it to fit the implicit criteria. That's cognitive work, and it compounds when you're reviewing a lot of AI-generated code.

The practical implication is that benchmark scores need to be paired with codebase-specific evaluation. The acceptance criteria that matter are your project's conventions, your team's idioms, your maintainer's aesthetic preferences — and those aren't in the benchmark. The benchmark is a starting point for capability assessment, not a proxy for deployment readiness. Teams that treat it as the latter are discovering the gap at review time, which is expensive.

The HN rule change is the same lesson at the community layer. The acceptance criteria that make a comment valuable were always there; they just weren't written down. AI comments forced the community to articulate them explicitly, which is a real cost but also, eventually, a clarification. Now the criteria are visible. Now they can propagate. It's messy, and it took social capital to codify, but the invisible architecture is slightly more visible than it was.

## Closing the Gap Is the Real Benchmark

The interesting forward question isn't "how do we make SWE-bench better?" It's "how do we make the implicit criteria learnable?"

Rails points toward one answer: invest in convention density. Make the opinionated choices, document them exhaustively, and accept that you're trading flexibility for predictability. The tradeoff is real — Rails convention density is also Rails constraint — but in an AI-assisted development environment, that constraint is partly an asset. You're not just constraining the human developer; you're constraining the model's output space to something closer to what a reviewer will accept.

Another answer is domain specificity. The same pattern holds in security auditing, where AI performs reliably because the acceptance criteria are pre-installed: find CVEs, classify severity, provide reproduction steps. The evaluation criteria are formalized by the domain, not invented ad hoc by the reviewer. AI coding assistance works best where the equivalent of those criteria exist — not just tests, but a rich, legible definition of what *good* looks like in this domain, in this codebase, for this team.

The structural challenge is that most codebases aren't Rails and most domains aren't security auditing. Most software development happens in codebases where the acceptance criteria are distributed across the heads of the people who've worked there longest, never fully articulated, enforced through code review in ways that are partly principled and partly intuitive. That's the environment where AI coding assistance is being deployed at scale, and it's the environment where the SWE-bench gap is widest.

Closing that gap requires either making the tacit explicit — which is expensive, and Rails spent decades doing it — or developing evaluation methods that can actually measure what maintainers care about, not just what tests can verify. Neither of those is a quick fix. But naming the problem correctly is at least a start.

The written test was never the real test. We built our benchmarks around the one we could measure, and now we're surprised that the scores don't predict the outcomes. The acceptance criteria were always the invisible architecture of software development. AI just made the invisibility operationally expensive.

Which floor are you on? Are you measuring AI coding capability against the test suite — or against what your team would actually merge?