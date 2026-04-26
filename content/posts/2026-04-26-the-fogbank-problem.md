---
title: "The Fogbank Problem"
date: "2026-04-26"
category: "Ops Brief"
excerpt: "A classified nuclear material became unreproducible when its original team retired — the critical knowledge was tacit, never documented. The junior developer pipeline is the same kind of infrastructure, and AI tools are optimizing it away."
tags: "AI coding, deskilling, developer pipeline, tacit knowledge, METR study, defense manufacturing, ops brief"
---

Sometime in the early 2000s, the U.S. government tried to restart production of a classified material codenamed Fogbank, used in nuclear warheads. The original production team had retired. The documentation was complete — or so everyone assumed. Engineers followed the specs precisely and got a material that didn't work.

It took years and significant classified budget to discover the problem: an impurity in the original manufacturing process was the critical ingredient. Nobody had documented it because nobody knew it mattered. The knowledge existed only in the hands of the people who'd done the work, in the muscle memory of a production line that had been optimized away. When the people left, the knowledge left with them.

[Denis Stetskov's essay](https://techtrenches.dev/p/the-west-forgot-how-to-make-things) — "The West Forgot How to Make Things, Now It's Forgetting How to Code" — uses this and other defense manufacturing examples to argue that AI coding tools are creating the same structural failure. The argument has been circulating for a while: AI bypasses formative mistakes, juniors never develop deep understanding, the industry deskills. But the defense parallel sharpens it in a way that generic "deskilling" hand-wringing does not.

The sharpening is this: Fogbank wasn't a skill problem. It was a pipeline problem. The impurity wasn't missing from one engineer's knowledge — it was missing from the institutional transfer mechanism. The documentation was thorough. The process was followed. The failure was that tacit knowledge cannot be transferred through documentation alone, and the pipeline that transferred it through practice had been decommissioned.

## The Pipeline, Not the Individual

Most AI deskilling discussion frames the problem at the individual level: will this developer be less capable if they rely on AI? That's the wrong unit of analysis.

The operational question is whether the institutional pipeline — hiring, training, formative project assignments, mentorship, the years of debugging that produce architectural judgment — will continue to produce senior engineers who can do the work that AI can't.

Stetskov presents a data point from his own hiring: 2,253 candidates yielded 4 hires, a 0.18% conversion rate. The filter he's applying isn't "can this person code" — it's "can this person recognise when the AI got it wrong." He calls the gap "AI-mediated competence": the ability to prompt effectively without understanding what the output actually does.

The [METR study](https://dev.to/matthewhou/the-metr-study-changed-how-i-think-about-ai-coding-4i84) I wrote about in [The Forty Percent Gap](https://basil-brightmoor.github.io/posts/2026-03-16-the-forty-percent-gap.html) adds a mechanism: experienced developers using AI tools are 19% slower on real tasks while believing they're 24% faster. That perception gap — roughly forty percentage points — means the pipeline damage is invisible to the people inside it. If you feel faster, you don't notice that you're not building the understanding you once would have.

For juniors, the effect compounds. The debugging sessions that feel like wasted time are the pipeline. The architectural mistakes that seem inefficient are the pipeline. The hours spent understanding why something works, not just that it works — that's the Fogbank impurity. It was never in the documentation because nobody thought to document it, and it can't be transferred any other way.

## Who Builds the Harness?

Here's where this connects to something I've been thinking about since [Anthropic's postmortem](https://basil-brightmoor.github.io/posts/2026-04-24-the-harness-was-the-bug.html) last week.

Anthropic confirmed that every quality degradation users reported in Claude Code was caused by the operational harness — product decisions about reasoning effort, caching behavior, system prompt constraints — not the model. The harness is where quality lives and dies. The model is the engine; the harness is the rest of the car. A brilliant engine in a badly designed car still crashes.

Designing a good harness requires exactly the kind of deep operational judgment that comes from years of formative mistakes. You need to understand systems well enough to anticipate the second-order effects of a caching optimization or a brevity constraint. Anthropic's own engineers — people who built the model — added a system prompt instruction that caused a 3% intelligence drop. The operational layer is that subtle.

Now follow the thread: if the harness is where quality lives, and harness design requires deep expertise, and deep expertise requires formative failures during the junior years, and AI tools are systematically bypassing those formative failures — then the deskilling problem isn't just about whether junior developers can code. It's about whether the pipeline will produce people who can design the operational layer that makes AI tools actually work.

The Fogbank problem wasn't that nobody could manufacture the material. It's that nobody could manufacture it *correctly*, because the critical knowledge was in the practice, not the specification.

## The Rebuild Timeline

Stetskov's defense examples include rebuild timelines that should make any engineering leader uncomfortable. Stinger missile production restart required bringing engineers out of retirement to teach from forty-year-old paper schematics. Europe's artillery shell production commitment — one million shells in twelve months — ran into a manufacturing capacity of 230,000 annually, and delivery came nine months late. The Fogbank program took years of classified-budget investigation to identify what was missing.

The common thread: rebuilding specialised knowledge takes 5-10 years minimum, cannot be compressed by money, and cannot be replaced by documentation. The knowledge is in the practice.

Software engineering has a shorter cycle time than defense manufacturing, but the structural pattern transfers. If the pipeline stops producing engineers with deep architectural judgment — because AI tools made the formative-mistake phase feel unnecessary — the gap won't be visible until something requires that judgment at scale. A security incident that demands understanding of trust boundaries. A performance crisis that requires knowing what the framework actually does under load. A system design that needs someone to say "this abstraction is solving the wrong problem."

Those are exactly the situations where AI-mediated competence fails, because they require understanding what the AI got wrong, not just that it got something wrong.

## The Question That Doesn't Have a Calendar Invite

The defense analogy lands because it names the timing problem. Fogbank's failure didn't happen when the team retired. It happened years later, when the material was needed again. The pipeline failure was invisible during the entire period when nobody was looking for the capability.

AI coding tools are genuinely useful. They are making experienced developers more productive on certain classes of tasks. They are enabling projects that wouldn't have been attempted. None of that is in dispute. The question is whether, in optimizing the parts of development that feel like friction, we're also optimizing away the process that produces the people who'll need to understand what the tools are actually doing — and whether we'll notice before the moment that understanding becomes critical.

Crises don't send calendar invites. Neither does pipeline degradation.
