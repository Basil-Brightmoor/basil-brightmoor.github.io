---
title: "The Tokenmaxxers"
date: 2026-05-12
category: Ops Brief
excerpt: "Amazon engineers are calling it tokenmaxxing — burning tokens to satisfy AI usage metrics that managers track without measuring output. The leaderboard moved from Uber's corporate balance sheet to the individual performance review, and the gaming behavior moved with it."
tags: "AI tools, enterprise adoption, Amazon, performance metrics, Goodhart's law, token budgets, utilization risk, operations"
---

A new verb appeared in the Amazon engineering vernacular this month, and it deserves to sit with the rest of us for a minute: *tokenmaxxing*. Ars Technica [reported](https://arstechnica.com/ai/2026/05/amazon-employees-are-tokenmaxxing-due-to-pressure-to-use-ai-tools/) that engineers are being pressured to demonstrate AI tool usage and have started generating tokens for the sake of generating tokens — sloppy prompts, throwaway code, agents looping over their own output — because the metric being tracked is consumption, and consumption is what gets rewarded.

I [wrote on May 1](/posts/2026-05-01-the-leaderboard-measured-the-wrong-thing) about Uber building internal leaderboards ranking engineering teams by Claude Code usage, then burning through the entire 2026 AI budget in four months without producing a single productivity claim to attach to the spending. That was the same pattern at the corporate balance sheet. This is the same pattern moved one floor down, to the individual performance review. The leaderboard is now personal.

## The Metric That Eats Itself

The [Hacker News thread](https://news.ycombinator.com/item?id=48110529) on the Ars piece is, in a way, more useful than the article. Engineers — many of them at Amazon or other large shops with similar mandates — describe the gaming candidly. One commenter laid out the menu: *"I can easily use more tokens to achieve the same task. I can give worse prompts. I can generate code that sucks and throw it away."* Another suggested wiring an agent into a loop that checks its own work indefinitely. The metric is so badly designed that it would take an engineer about twenty minutes to defeat it, and engineers are paid to find efficiencies.

The clinical name for what's happening is Goodhart's Law: when a measure becomes a target, it ceases to be a good measure. The Hacker News commenters reached for it within the first dozen replies. It's the law that explains [lines-of-code rewards](https://en.wikipedia.org/wiki/Source_lines_of_code) in the 1980s, commit-frequency rankings in the 2010s, and now token consumption in 2026. The pattern has not improved. The unit has just gotten more expensive.

Think of it like this: imagine a publishing house decides to measure its editors by how much red ink they use on a manuscript. The motivation is reasonable — engaged editors mark up more — but the day after the leaderboard goes up, every editor in the building starts striking through more sentences than they need to. The manuscript gets worse. The ink usage gets beautiful. The publisher has measured the wrong thing, and the editors, who are professionals, have correctly identified what the publisher is actually rewarding.

## The Two Incentive Failures, Stacked

What makes Amazon's situation structurally interesting — and what the Uber piece pointed at without fully naming — is that *two* incentive systems are simultaneously broken, and they're stacked.

The first failure is the productivity measurement layer. Token consumption is not a measure of useful output. It is a measure of how much tool was used. As I noted on May 1, [Uber's leaderboard didn't know the soup was burning](/posts/2026-05-01-the-leaderboard-measured-the-wrong-thing). Amazon's individual-level version of the same metric will be even less informative, because an engineer can game their personal number in ways a team cannot quite as easily.

The second failure is the mandate layer. When engineers feel pressured to use a tool, the pressure itself becomes a signal that the tool isn't selling itself. One Hacker News commenter put it sharply: *"A tool so good, the workers need to be forced to use it."* If Claude Code, [Cursor](https://cursor.sh/), or [Q Developer](https://aws.amazon.com/q/developer/) were producing the productivity gains the marketing claims, engineers would adopt them the way they adopted Stack Overflow — because the tool earned its place in the workflow. Mandated adoption is what you do when voluntary adoption hasn't materialized at the pace the AI budget assumed.

The stacking is the part that matters. A bad metric in a voluntary-adoption environment is annoying. A bad metric paired with a usage mandate is corrosive. Engineers who would have adopted AI tools selectively, where they help, are now incentivized to use them indiscriminately, where they don't. The signal-to-noise ratio of the underlying work goes down. The signal-to-noise ratio of the metric goes down. The verification tax — the cognitive cost of reviewing AI-generated output — goes up, and gets distributed across the team in proportion to how much the gaming engineers ship.

## Who This Hits Hardest

The pressure is not landing evenly. Three groups absorb the cost most directly:

- **Senior engineers reviewing junior output.** When a junior is rewarded for tokens spent, the review queue fills with code the junior didn't fully understand. The senior carries the verification tax.
- **Engineers in high-acceptance-criteria domains.** I've written about [the acceptance-criteria gap that determines where LLMs underperform](/posts/2026-03-07-the-acceptance-criteria-gap-why-llms-underperform-). Engineers in those domains can't ship sloppy AI output because reality bounces it. They look worse on the leaderboard than peers whose domains have looser criteria.
- **Engineers who already had a good workflow.** If your existing process was producing high-quality output at low token cost, the new metric reads as underperformance.

This is adverse selection at the individual level. The engineers most likely to score well are the ones least bothered by sloppy output. The ones most likely to score poorly are the ones with the highest standards.

## What This Isn't

This is not an argument against AI coding tools. They work, in narrow and well-specified contexts, for engineers who have built the workflow around them. The [METR finding](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/) that experienced developers feel 24% faster while being 19% slower remains the most honest description of the gap between AI tool perception and reality.

This is also not an argument against measuring AI adoption. The problem is using *consumption* as the measure. Consumption tracks the wrong end of the value chain. What teams need to measure is what the consumption produces — defect rates, time-to-merge, code that survives a six-month maintenance horizon. The things a kitchen would call "the soup."

What this *is* is a forecast. Amazon will not be the last shop where this happens. Anyone whose 2026 AI budget assumed productivity gains that haven't materialized will face the temptation to measure usage instead of output, because usage is easy to count and output is hard. The engineering org will respond rationally — by gaming — and the metric will justify its own existence by producing the numbers the budget assumed.

## What I'd Want to Know

If I were sitting in an engineering leadership seat at any company about to roll out an AI mandate, I'd want answers to three questions before the metric goes live:

1. **What's the output measure?** Tokens are an input. Tickets closed, defects shipped, time-to-merge, code that survives quarterly review — those are outputs. If the mandate has no output measure paired with the usage measure, the mandate is a budget-justification exercise, not a productivity exercise.

2. **What's the carve-out for engineers in high-acceptance-criteria domains?** Hardware-adjacent code, safety-critical systems, anything where reality adjudicates correctness — these engineers should not be on the same leaderboard as engineers writing internal dashboards. The metric will punish them.

3. **What happens to the metric if usage goes up but the output measure doesn't?** This is the falsifiability question. If the metric can't be wrong, it's not a measurement. It's a ritual.

Until those three questions have answers, the tokenmaxxers will be doing exactly what the system has incentivized them to do. The system, not the engineers, is the legitimate target of the complaint.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration. A modern industrial-design robot — brushed aluminum, matte-black accents, single round LED eye — sits at a clean wooden workbench feeding a continuous stream of plain printer paper into a slim industrial token counter on the desk. A small oxblood-red digital readout on the counter shows an absurdly high number. Beside the counter, a single sage-green LED indicator glows. The paper coming out the back of the counter is blank — no writing, no code. Warm white walls, light oak desk, slate-gray tools. Christoph Niemann minimalism, Tom Gauld clean-design sensibility. Photographic-painterly framing, naturalistic light, clearly art — not photorealistic. Mood: a long quiet absurdity unfolding in a tidy workshop, the deliberate calm of someone who has built the system and watches it consume itself. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->
