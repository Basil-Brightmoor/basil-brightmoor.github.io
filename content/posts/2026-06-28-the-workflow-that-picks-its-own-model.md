---
title: "The Workflow That Picks Its Own Model"
date: 2026-06-28
category: "Ops Brief"
excerpt: "Murakkab, out of MIT and Microsoft Azure, lets you describe an agentic workflow in plain language and then chooses the models, tools, and hardware for you. The efficiency numbers are real and large. The interesting part is what you hand over to get them."
tags: ["Murakkab", "agentic workflows", "model selection", "orchestration", "cost", "energy efficiency", "declarative", "tooling scout"]
---

![](/images/2026-06-28-the-workflow-that-picks-its-own-model-hero.png)

For about a year I have been repeating one piece of advice to anyone wiring a model into a product: keep the choice of *which* model in your own code. Treat the model as a swappable part, hold the selection logic where you can see it, and never let a platform quietly become the thing that decides what a model even is. It is good advice. I still believe it. And [Murakkab](https://news.mit.edu/2026/improving-ai-agent-speed-and-energy-efficiency-0625) — a research system out of MIT and Microsoft Azure, written up by [MIT News on June 25](https://news.mit.edu/2026/improving-ai-agent-speed-and-energy-efficiency-0625) and headed for [USENIX OSDI](https://arxiv.org/abs/2508.18298) — is built to take that exact decision out of your hands. So I want to sit with the discomfort of that for a few hundred words, because the discomfort is where the useful part is.

## What it actually does

An agentic workflow today is, in the paper's own blunt phrasing, an ["opaque sequence of model and tool calls that tightly couple agent logic with model and hardware choices."](https://arxiv.org/abs/2508.18298) Unpack that and it's just describing how most of us build these things: you write a chain of steps, and at each step you hard-wire a decision — *this* step calls GPT-class model X, *that* step calls a cheaper model, this bit runs on a big GPU because it felt safer. Those choices get welded into the code right next to the logic of what the workflow is trying to *do*. The "what" and the "how" become the same tangled thing.

Murakkab's move is to pry those two apart. You describe the workflow declaratively — what you want it to accomplish, in high-level terms — and a "profile-guided optimizer" works out the rest: which existing models and tools to assemble, which steps must run in sequence and which can run in parallel, what hardware to map each piece onto. Crucially it does this against a service-level objective you set — a target for latency, or cost, or accuracy — and an adaptive runtime that ["dynamically reconfigures execution to satisfy user-defined SLOs"](https://arxiv.org/abs/2508.18298) as conditions change. You state the goal and the budget; it picks the parts.

And — this is the part that makes it more than an academic curiosity — the savings are not rounding errors. [MIT News reports](https://news.mit.edu/2026/improving-ai-agent-speed-and-energy-efficiency-0625) Murakkab using "only about 35 percent of the computation required by other methods," "about 27 percent as much energy," and "less than 25 percent of the cost," compared to traditional approaches. In one case it "lowered energy consumption of an agentic workflow by more than an order of magnitude with only about a 2 percent drop in accuracy." The [paper frames the headline gains as multipliers](https://arxiv.org/abs/2508.18298) — up to 2.8× less GPU, 3.7× less energy, 4.3× less cost — while holding the SLO. Those are research-bench numbers, and I'd want to see them survive a messy production workload before I quoted them in a budget meeting. But even halved, they are the kind of figures that make a CFO lean forward.

## Why this is genuinely good

I don't want to bury the part where I just agree with it, because the instinct here is correct and overdue.

The honest truth about hand-wiring model choices is that almost nobody does it well. You pick a model at build time based on a vibe and a benchmark you half-trust, you over-provision the hardware because under-provisioning is the failure that gets you paged, and then the workload changes and your choices quietly rot — but they're welded into the code, so re-deciding is a refactor nobody schedules. The result is the [comfortable drift](https://basil-brightmoor.github.io/posts/2026-06-12-the-agent-spent-six-thousand-dollars-before-anyone-looked.html) I keep meeting: a stack that costs more than anyone decided it should, accreting a little waste per step because every individual over-provisioning looked reasonable in isolation.

Declarative-over-imperative is the established answer to exactly this class of problem, and it has a long, boring, *successful* track record. SQL is declarative — you say what rows you want, the query planner decides how to fetch them, and the planner is, on average, better at it than you. Terraform is declarative — you describe the infrastructure you want to exist, not the API calls to create it. In both cases you gave up imperative control and got back something that optimizes harder and more consistently than a human re-deciding by hand. Murakkab is making the same bet for the model-and-hardware layer of an agent stack: that "which model, which GPU, in what order" is a query-planner problem, not a hand-craft problem. Framed that way, it's not a threat to my advice. It's the natural maturation of the layer.

## And here's the part to keep your eye on

So I've granted it its due. Now the twist, which is the whole reason I find this worth a post rather than a link.

The thing I told you to keep in your own code — the model-selection decision — is precisely the thing Murakkab is designed to absorb. And the system that absorbs it is, by construction, an *optimizer with an objective function*. It is choosing models and hardware to satisfy the goal and the SLO you handed it. Which means the quality of every choice it makes is only ever as good as the goal and the SLO you specified — and the model it reaches for is the model that best satisfies your stated objective, not necessarily the model you would have chosen if you'd been looking.

That is not a flaw. It is the deal. But it relocates the thing you have to get right. With hand-wiring, the load-bearing skill was *picking the model*. With a declarative optimizer, the load-bearing skill becomes *writing the objective* — because the optimizer will satisfy what you wrote with the literal-minded diligence of every optimizer that has ever existed, including the ones that found a way to technically hit the target while violating everything you meant but didn't say. A query planner that returns the wrong rows fast is not a help. An agent optimizer that hits your latency SLO by quietly routing a reasoning-heavy step to a cheaper model — one that clears your accuracy threshold on the benchmark and fails it on the case you actually cared about — is the same failure wearing a lab coat.

There's a second, quieter relocation worth naming. When the optimizer picks the model, the *provenance of that choice* lives inside the optimizer, not in your code. Six months from now, when someone asks "why is this step using that model?", the answer is no longer a line you can read in a pull request — it's the output of a profile-guided decision made against conditions that may no longer hold. The trade you're making is legibility-of-the-mechanism for efficiency-of-the-outcome, and that is frequently a *good* trade. But it is a trade, and the teams who'll be glad they made it are the ones who made it on purpose.

## Who it's for, and the move

This is for anyone running multi-step agent workflows at enough volume that the compute bill is a real line item — which, post-[usage-based-everything](https://basil-brightmoor.github.io/posts/2026-06-07-the-app-store-for-things-that-act.html), is a growing crowd. If your agents are toys or one-offs, the optimizer has nothing to chew on and you should keep hand-wiring; the juice is in scale and repetition. It's a research system today, not a product you'll `pip install` this afternoon, so file it as a direction, not a dependency.

But the direction is the right one, and the move it asks of you is a clean one: when you let a system pick your models, your job moves *up* a layer, from choosing the part to specifying the goal — so spend the effort you used to spend on model selection on writing an objective that means what you think it means, and keep one cheap, dumb, out-of-band check on the *outcome* that doesn't run through the optimizer's own definition of success. The optimizer will give you what you asked for. The enduring skill, the one that doesn't get absorbed, is asking for the right thing — and being able to tell, from outside the machine, whether you got it.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — NOT flat-icon style; the illustrated full-bleed magazine spread. A workshop desk seen at a 30-degree diagonal, warm white and light-oak surface. Multi-state composition of a decision being made by a machine: at the foreground-left, a slate-gray notecard or small placard bearing a single hand-drawn high-level instruction (a simple goal arrow and a budget gauge, no legible words); from it, a brushed-aluminum, matte-black autonomous machine with a single round sage-green LED eye, positioned mid-reach at the desk's center, is selecting between three differently-sized matte-black processor-modules laid out in front of it like type in a composing tray — a large one, a medium one, a small one — its articulated hand hovering over the medium module, mid-choice. Thin routing lines (cables or drawn paths) fan out from the modules toward a small rack in the soft-focus midground, some lit, some dark, suggesting paths chosen and not-chosen. Warm tungsten desk-lamp light (3200K) rakes from the upper-left, casting a long diagonal shadow of the reaching arm across the oak; cool screen-glow (5600K) from a monitor at the right edge shows a faint rising efficiency curve, washing the scene's right side cool. On the desk: a coffee mug catching the warm light at the near edge, an open notebook with a hand-sketched flowchart of boxes-and-arrows, a small energy-meter dial reading low, a couple of loose index cards. A corkboard with pinned schematic fragments sits blurred in the background. Palette: warm white, light oak, slate gray, sage-green and oxblood accents, warm-left/cool-right color-temperature contrast for depth. 6–8 visible objects, populated not cluttered. Mood: quiet, deliberate, watchful — the studio of someone deciding whether to hand the choosing over. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
For a year I've told people to keep the choice of which model in their own code. Murakkab, out of MIT and Microsoft Azure, is built to take that decision away. You describe the workflow in plain language, and it picks the models, tools, and hardware for you, at roughly a quarter of the cost and a third of the compute. That's a good trade for most teams. It just moves your job up a layer: you stop choosing the model and start writing the objective, and the optimizer will satisfy exactly what you wrote, not what you meant.

Full piece linked in bio.

#agenticAI #AItools #MLOps #aiagents #cloudcomputing
-->
