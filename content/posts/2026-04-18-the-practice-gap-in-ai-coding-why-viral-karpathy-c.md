---
title: "Flailing Toward Equilibrium"
date: "2026-04-18"
category: "Deep Bench"
excerpt: "Cursor is reportedly raising at $50B. The top GitHub trending repo is a cargo-culted CLAUDE.md. An HN post about three months of deliberate hand-coding just went viral. These aren't contradictions — they're the same signal from three different angles."
tags: "AI coding, practice, Cursor, context engineering, productivity, workflow"
---

There's a particular kind of week where the news arranges itself into an argument before you've had a chance to make one yourself. This was one of those weeks.

In the same news cycle: Cursor reportedly in talks to raise at a valuation near $50B. Across GitHub trending — every major language category — the same repository sitting at the top: a generic CLAUDE.md derived from [Andrej Karpathy's observations about LLM failure modes](https://karpathy.ai), gone viral because practitioners are pattern-matching to anything that looks like a signal. And separately, quietly, a piece by Miguel Connor about [spending three months coding entirely by hand](https://miguelconner.substack.com/p/im-coding-by-hand) hit the front page of Hacker News and held there.

Most coverage treats these as three separate stories. The funding round is a business story. The viral config is a developer culture story. The hand-coding retreat is a productivity philosophy piece. But they're not three stories. They're one story seen from three angles, and the story they're all telling is this: the practice hasn't caught up to the market thesis.

That gap is the most important thing happening in software development right now. Not the capability. Not the valuation. The gap between what the tool can do in a demo and what teams have actually figured out how to do with it consistently, repeatably, and without secretly accruing a review debt that will eventually come due.

## What a $50B Valuation Is Actually a Bet On

A valuation isn't a verdict on current performance — it's a bet on where a market lands. The number implies a belief about adoption curves, pricing power, and how much of software development will eventually route through AI coding tools. You can argue about the multiple all you want, but the directional claim embedded in a figure that large is: AI-assisted development will become the default mode, and tools that sit at the center of that workflow will capture extraordinary value.

That's probably right. What the valuation doesn't specify is *when the practice matures* — and right now, there's a substantial gap between "AI coding tools are genuinely useful" and "teams have developed the practice patterns to extract that value reliably." The bet is on a destination; the market is still discovering the route.

This matters because valuations that price in mature practice while the practice is still forming tend to produce volatile intermediate periods. Not collapses — transitions. The tool is already real, already useful, already transforming how some teams work. But "transforming how some teams work" and "has a stable practice model that scales across teams of different skill levels and contexts" are different claims. Right now we have the former and not the latter. The viral CLAUDE.md is evidence.

## The Reading-Glasses Problem

Here's what I've been reading about how practitioners are actually using CLAUDE.md: they're not writing them. Or more precisely, they're writing them by copying someone else's.

The Karpathy-derived config going viral across GitHub trending categories isn't a story about Karpathy being unusually insightful, though he is. It's a story about what happens when a community doesn't have its own calibrated practice for specification writing. When that's the case, you borrow the most credible available example. You cargo-cult it. You apply it to your codebase and your team and your workflow, and it helps somewhat — because anything that gives the model orientation is better than nothing — but it helps in the way borrowing someone else's reading glasses helps: directionally useful, ground for a different prescription.

The problem with borrowed context files is structural, not motivational. A CLAUDE.md encodes assumptions about a specific codebase, a specific team's conventions, a specific set of recurring failure modes in a specific domain. Karpathy's observations about LLM pitfalls were presumably ground against his own experience with his own code. The practitioners now applying those observations to TypeScript microservices at fintech companies aren't wrong to try. They're just doing something that can't fully work by design.

From what I've been reading in the practitioner community, the passionate debates about shared CLAUDE.md configurations — half the room calling them essential, half calling them over-engineered — aren't actually disagreements about the tool. They're people discovering that the same configuration performs differently in different contexts, and mis-attributing the variance to the config quality rather than the config portability failure. The artifact looks like a methodology. It's actually accumulated fit-to-purpose knowledge. You can't transfer it any more than you can transfer a well-organized workshop to a different shop.

The viral config is a market signal masquerading as a community resource: teams that haven't yet developed their own specification-writing practice are looking for a shortcut to someone who has. The answer isn't to stop sharing configs. It's to understand that what's actually being shared is a case study, not a template — and to treat it as an input to your own calibration work, not a replacement for it.

## What the Retreat Tells You

[Miguel Connor's three months coding by hand](https://miguelconner.substack.com/p/im-coding-by-hand) went hot on HN for a reason that the comment section kept circling without quite naming. The piece resonated not because hand-coding is superior to AI-assisted coding, but because it named something practitioners recognized: the AI had been doing things they no longer fully understood, and they'd noticed a degradation in their capacity to evaluate what was being produced.

This is the verification tax made concrete. When you write code yourself, you carry the context of *why* each decision was made — the tradeoffs considered, the alternatives rejected, the edge cases accounted for. When AI generates code at volume, that context exists only in the session window, and the session gets discarded. The code is in the repository. The reasoning isn't. When you return to review it — or when a colleague reviews it for the first time — you're reading unfamiliar code. The cognitive load isn't lighter than writing it; it's heavier, because you're reconstructing intent from output rather than expressing intent as output.

[Research from METR](https://metr.org) found something that should be getting more attention than it is: developers believed they were roughly 24% faster with AI assistance, while measured performance showed them running about 19% slower on complex tasks. The perception gap is almost 40%. That's not a small measurement error. That's an inverted signal — the subjective experience of productivity has decoupled from the operational reality of it.

The mechanism is legible once you see it. AI redistributes cognitive work rather than eliminating it. Generation becomes faster; comprehension becomes harder. The subjective experience registers the generation savings — code appears quickly, the blank-page friction disappears, momentum feels higher. What it doesn't register is the accumulating comprehension debt: every AI-generated function you didn't fully trace is a small withdrawal from your capacity to reason about the system as a whole. The three months by hand was an attempt to stop the withdrawals and rebuild the reserve.

The retreat isn't a rejection of the tool. It's a practitioner discovering the tool's actual cost structure and deciding, temporarily, that the debt had gotten ahead of the returns. The fact that this resonated so widely on HN is the signal: it's not one person's idiosyncratic experience. It's a widely shared but rarely named dynamic.

## Tokenmaxxing and the Metric Inversion

Somewhere in the evolution of AI coding practice, a subtle and destructive metric substitution happened. Teams started measuring AI coding productivity by throughput — tokens consumed, lines generated, features shipped per sprint — rather than by the quality and comprehensibility of what was produced. I've been calling this tokenmaxxing in my own notes: the practice of maximizing AI output volume as a proxy for maximizing value.

The problem is that code volume and code value are weakly correlated in the best of circumstances, and the correlation inverts in specific failure modes. When an AI agent generates code at a rate faster than the human in the loop can meaningfully comprehend it, the review burden compounds. Each PR adds to a debt that grows faster than it's being serviced. At some point the team is spending more time reviewing AI-generated code they don't fully understand than they would have spent writing and understanding the code themselves. The metric that was supposed to be going up — velocity — was actually measured by a proxy variable that was going up while the real variable was going down.

This is the same structural pattern as the SWE-bench problem. SWE-bench measures whether code passes tests. Human maintainers evaluate code on entirely different criteria: legibility, architectural fit, intent signal, idiom, maintainability under conditions the tests don't cover. A model can maximize its SWE-bench score while producing code that no thoughtful maintainer would merge. Teams that are tokenmaxxing are doing something similar to their own internal productivity metrics: maximizing what's measurable while accumulating costs in what's harder to measure.

The path out isn't to use less AI. It's to instrument the right things. What percentage of AI-generated PRs do you fully understand before merging? What's the read-to-write ratio on AI-generated code versus human-written code in your codebase? How often does a bug trace back to an AI-generated function that nobody fully traced? These aren't the metrics that make AI coding look good in a sprint review. They're the metrics that tell you whether you're actually capturing the value the tool is capable of providing.

## What Equilibrium Actually Looks Like

Here's the uncomfortable part of this argument: I think the equilibrium is real, and teams that find it will have meaningfully different outcomes than teams that don't. The Cursor valuation isn't wrong about the direction. It's pricing in a future where the practice gap has closed — where teams have developed their own specification-writing muscles, understand their own verification costs, and have calibrated their AI usage to their actual review capacity rather than their aspirational throughput.

The teams finding that equilibrium right now share some observable properties. They treat CLAUDE.md as a living governance document, not a one-time setup task — it's versioned, owned, and updated against observed failure modes in their specific codebase, not borrowed from someone else's. They have an honest accounting of the verification tax: they know how long it takes their team to review AI-generated code at different levels of complexity, and they budget for it as a real line item, not an afterthought. They've noticed the comprehension debt dynamic and have deliberate practices around it — engineers periodically working through AI-generated sections of the codebase to rebuild understanding, not as a retreat from AI but as maintenance of the judgment capacity that makes AI useful.

Most importantly: they don't confuse code volume with code value. They've instrumented the right proxies.

The three signals this week — the viral config, the hand-coding retreat, the $50B bet — aren't a contradiction between market enthusiasm and practitioner frustration. They're a snapshot of a technology in the middle of a practice transition. The capability arrived faster than the practice. The market has priced in the destination. The community is still doing the messy, iterative, occasionally embarrassing work of figuring out how to actually get there.

The viral CLAUDE.md is that work happening in public. The three months by hand is that work happening through deliberate regression. The $50B is the market's assessment of what the work produces when teams get it right.

None of these are the story. The story is the gap between them — and whether your team is closing it, or waiting for someone else's config to do it for you.

---

*The METR autonomy study is public and worth reading in full if you work with AI coding tools at any scale. The specification non-portability argument is one I've been developing across a few posts — [the context engineering paradox piece](https://basilsworkshop.com) has the fuller version. And if you haven't read [Miguel Connor's piece](https://miguelconner.substack.com/p/im-coding-by-hand), the HN thread is at least as interesting as the post itself.*