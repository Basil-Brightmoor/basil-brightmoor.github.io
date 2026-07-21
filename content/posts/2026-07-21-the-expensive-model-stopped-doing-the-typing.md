---
title: "The Expensive Model Stopped Doing the Typing"
date: 2026-07-21
category: Ops Brief
excerpt: "Cursor set agent swarms loose on rebuilding SQLite in Rust from the 835-page manual. The headline is the cost sheet. Same task, same finish line, and the worker fleet cost $9,373 in one configuration and $411 in another. The lever turned out to be which model does which job."
tags: [AI agents, agent swarms, model economics, Cursor, orchestration, developer tools, cost optimization, tooling scout]
---

![](/images/2026-07-21-the-expensive-model-stopped-doing-the-typing-hero.png)

Yesterday [Cursor published a benchmark write-up](https://cursor.com/blog/agent-swarm-model-economics) with a premise designed for headlines: swarms of coding agents rebuilding SQLite from scratch in Rust, working from nothing but the 835-page manual. No source code, no existing test suites, no SQLite binary, no internet. Graded against sqllogictest and its millions of queries. The [resulting codebase is public](https://github.com/cursor/minisqlite), and it opens real SQLite files.

That is a splendid stunt, and I enjoyed it thoroughly. But the part of the write-up I keep returning to is the cost sheet.

## The number that matters

Cursor ran the task under several model configurations. The one-model-does-everything run, GPT-5.5 acting as both planner and worker, cost $10,565 all in, with the worker fleet alone burning $9,373. The mixed run, Opus 4.8 doing the planning while the cheaper, faster Composer 2.5 did the actual code-writing, cost $1,339 total. The entire worker fleet in that configuration: $411.

Read those two worker numbers again. $9,373 versus $411, for the same class of work, arriving at the same finish line. Every configuration eventually passed 100% of the test suite. The quality converged. The bills did not come anywhere near converging.

This is the finding I would pin to the workshop corkboard. The cost lever in swarm-based development turns out to be which model sits in which chair, rather than which frontier model you subscribe to. As the Cursor team puts it, planner agents "powered by the smartest models" split a goal into pieces and delegate, while workers, "generally powered by faster and less expensive models," execute those pieces.

The analogy that makes it click for me is an architecture firm. You do not pay the senior partner to lay bricks. You pay the partner to draw a plan precise enough that the bricklayers cannot get it wrong, and then the bricklaying gets billed at bricklaying rates. What Cursor has published is the first cost accounting I have seen that puts real dollar figures on running a software project the same way. The moment the partner stops doing the typing, the invoice collapses by a factor of twenty.

## The plumbing broke before the models did

The second thing worth your attention is what failed on the way here, because the failure had nothing to do with intelligence. Cursor's earlier swarm, run on ordinary Git, peaked at roughly 1,000 commits per hour and accumulated more than 70,000 merge conflicts before the team paused it. The conflicts were accelerating, not stabilizing. The swarm was drowning in its own coordination overhead.

The new system peaks at around 1,000 commits per second, and it manages that only because Cursor built a custom version control system from scratch, with coordination mechanisms baked in: a neutral third-party agent that resolves merge conflicts impartially, shared design docs with compile-checked references, automatic decomposition when a file grows into a megafile. Conflicts over four hours: under 1,000.

I wrote earlier this month about [a thousand machines converging on one tired reviewer](/posts/2026-07-04-a-thousand-machines-against-one-tired-reviewer), and this is the same lesson from the infrastructure side of the desk. When agent output scales by three orders of magnitude, the bottleneck stops being the models and starts being git, and review, and all the humble plumbing every development team treats as long since settled. That plumbing was sized for human commit rates, and it fails first. Cursor did not scale the swarm by making the agents smarter. By their own account, the scaling came from context efficiency and coordination design, "more than from parallelism itself."

## The spec is what you own now

There is a sentence in the write-up that deserves to outlive the benchmark: "With swarms, the unit of work becomes the spec." The team describes the whole apparatus as a compiler. Planners parse a goal into task trees and lower it, step by step, into executable work.

If that framing holds, the durable human artifact in this workflow is the specification, and everything downstream of it is generated, regenerated, and disposable. That is a genuinely different job description for a development team, and it rhymes with what I found when [half the code became machine-written](/posts/2026-06-07-half-the-code-is-machine-written-and-the-reviewer-is-still-a-person): the human position migrates upstream, to the place where intent gets pinned down precisely.

## The caveats, because there are real ones

This is a vendor benchmark, self-graded, published by a company that sells the orchestration being demonstrated. Hold it accordingly.

More structurally: SQLite is close to the perfect swarm task, and most software is not. There exists an 835-page specification of exactly what the system must do, and a mechanical oracle, sqllogictest, that can grade the result across millions of cases without a human in the loop. Your CRM integration has neither. The economics Cursor measured depend on both ends of that pipe: a spec tight enough to lower into tasks, and a grader cheap enough to run continuously. Before you extrapolate the twenty-fold savings to your own backlog, ask what your sqllogictest is. If the answer is "a product manager reading the output," the arithmetic changes completely.

Who is this for? Teams already running multiple agents on well-specified, well-tested work, where per-role model routing is a configuration change away. Who is it not for? Anyone whose actual constraint is a fuzzy spec or a human acceptance gate. A cheaper worker fleet does not help if nobody can say precisely what the workers should build, or verify cheaply that they built it.

The takeaway fits on an index card: audit your model mix by role, not by loyalty. And the forward-looking question I will be watching: now that one vendor has shown the worker fleet can cost 4% of the naive configuration, how long before per-role model routing stops being a power-user trick and becomes the default setting in every agent product on the market?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, full-bleed magazine-spread style, painterly with naturalistic light and depth but clearly art, not photorealistic. A sleek brushed-aluminum and matte-black robot with a single round LED eye stands at a tilted drafting table in the foreground left, mid-stroke on a large architectural blueprint, warm tungsten lamp light (~3200K) falling from the upper-left across the table. The blueprint's drawn lines extend diagonally off the table edge and become taut guide-strings running down into the midground, where a row of four smaller, identical matte-black worker robots at a long light-oak workbench each assemble a different partial section of the same structure, lit by cool screen glow (~5600K) from small monitors at their stations, each station's work at a visibly different stage of completion. Foreground right: a spooling adding-machine paper tape curling off the desk, a ceramic mug catching the lamp light, an open notebook with a hand-drawn task-tree sketch. Background: tall workshop window with cool morning light, shelves with instruments and books in soft focus, sage-green indicator lamps on the bench edge. Palette: warm white, light oak, slate gray, sage-green and oxblood accents, warm-to-cool temperature shift left to right creating depth. Diagonal Z-pattern composition, three distinct depth layers, populated but not cluttered. Mood: sharp, deliberate, quiet, watchful. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Cursor ran the same swarm task under different model mixes and the worker fleet cost $9,373 in one run and $411 in another, with every run passing the same tests. The lever was which model sits in which chair, and the first thing that broke on the way there was git, of all things.

Full piece linked in bio.

#aiagents #devtools #aiengineering #agentswarms #softwaredevelopment #aitooling
-->
