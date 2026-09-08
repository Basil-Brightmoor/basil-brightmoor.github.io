---
title: "The Seed Was Fixed and the Rest of the State Lived on the Server"
date: 2026-09-08
category: Ops Brief
excerpt: Hold the model, seed and request order fixed and disable prefix caching, and 800 of 800 runs come back bit-identical. Turn the cache on and the agent's trajectory changes on 75 percent of episodes at 4-bit.
tags: [ai tooling, inference, reproducibility, agents, devops, observability]
---

![](/images/2026-09-08-the-seed-was-fixed-and-the-rest-of-the-state-lived-on-the-server-hero.png)

Somebody on your team is going to open an incident ticket this month that says the agent did something strange, and somebody else is going to try to reproduce it. They will pin the model version. They will pin the seed. They will pin the temperature, the top-p, the system prompt, the tool definitions, and the exact request body pulled out of the log. And the thing will not reproduce, and after an afternoon of that everyone will agree that models are nondeterministic and move on.

[A measurement posted to arXiv on 4 September](https://arxiv.org/abs/2609.04748) suggests that in a meaningful fraction of those afternoons, the model is innocent and the culprit is a server setting nobody wrote down.

## The experiment

Aditi Patodiya ran an eighty-episode multi-turn agentic tool-use workload across two serving engines and four weight formats, holding the model, the decoding parameters, the seed and the request order fixed, and issuing every request serially at batch size one. Then the whole thing again with prefix caching turned off.

The control result is the one to sit with first:

> "With caching disabled, repeated execution was bit-identical in every configuration, 0 of 800 episodes, which bounds other sources of nondeterminism at 0.5 percent."

Eight hundred episodes, zero divergence, bit-identical. Whatever floating-point nondeterminism, kernel scheduling variance and batching noise you have been mentally filing your weird runs under, this setup put a ceiling of half a percent on all of it combined.

Now turn the cache back on:

> "Enabling the cache changed the agent's trajectory on 36.2 percent of episodes at 16-bit precision and on 75.0 percent at four-bit, a gradient that survives re-measurement under a controlled cache configuration."

Three quarters of episodes at four-bit. That figure counts episodes in which the agent took a different path through its own task, which is a coarser and more consequential unit than a token-level diff or a similarity score sliding a few points.

## Prefix caching is not a cache in the way operators use the word

Here is the mechanism, and it is worth stating plainly because the name does a lot of quiet work.

A prefix cache stores the key and value tensors for a prompt prefix that requests have in common — a system prompt, a set of tool definitions, a document everybody is asking about — so the engine can skip recomputing them. [vLLM's design documentation](https://github.com/vllm-project/vllm/blob/main/docs/design/prefix_caching.md) puts the mechanism plainly: "we cache the kv-cache blocks of processed requests, and reuse these blocks when a new request comes in with the same prefix as previous requests." The paper's opening claim about deployment is that prefix caching "is enabled by default in the major open-source stacks and treated as a transparent optimization."

That default is worth checking rather than assuming, and checking it is annoying in a way that is itself part of the problem. vLLM's [feature page for automatic prefix caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching/) still documents an explicit `enable_prefix_caching=True` flag, which reads like an opt-in, while engine defaults have moved across major versions. Whichever way it resolves on your build, the operator-facing fact is that the setting governing whether your runs replay is a serving-engine default you did not pick and probably cannot recite.

The word "cache" normally promises that a hit and a miss produce the same answer faster. That is what a CDN cache does, what a memoized function does, what your ORM's query cache does. The promise is identity of result.

A KV cache does not make that promise, and the paper's three localizing experiments show exactly where it breaks:

> "a single server-level prompt-cache setting moves run-to-run divergence by 37.5 percentage points, execution order acts only while that setting is active, and restoring cache state makes the cached and recompute paths each reproduce on 40 of 40 items while still differing from each other on 14."

Read that last clause carefully. Restore the cache state and *both* paths become perfectly reproducible — 40 of 40 each — and they still disagree with each other on 14 items. Neither path is broken. They are two different deterministic functions, and which one you got depended on whether some other request happened to warm a block before yours arrived.

The paper's own summary of the situation is the sentence I would put on the wall:

> "Cached serving is deterministic given cache state, and irreproducible in practice because that state is absent from the request and never reset by default."

## The starter, not the recipe

The analogy I keep coming back to is sourdough.

A recipe is a complete, portable specification. Hand it to two bakeries and you expect the same bread. A starter is not a specification at all. It is an accumulated history of everything that has been fed into that particular jar, it lives on a shelf rather than in the document, nobody versions it, and two bakeries running the identical recipe against different starters get different loaves and both are correct.

Your request body is the recipe. The KV cache is the starter. And every logging, tracing and replay tool in the agent observability stack was built on the assumption that capturing the recipe captures the run.

That is not a criticism of those tools. It is a statement about what the request contains. You can log the prompt, the seed, the model hash, the tool schema and the full response, store all of it forever, and still not have recorded the variable that decided the outcome — because that variable was never in the request to begin with, and there is no field to put it in.

## Why this lands hardest on the people least able to absorb it

Note the direction of the gradient: 36.2 percent at 16-bit, 75.0 percent at four-bit. Divergence roughly doubles as you quantize down.

Four-bit weights are what you run when you want a capable model on hardware you can actually afford. Prefix caching is what you turn on when you want to stop paying to recompute the same system prompt ten thousand times a day. Both are cost decisions, both are correct cost decisions, and the paper's finding is that they compound each other's reproducibility cost rather than sitting side by side.

So the teams with the strongest incentive to enable both are the ones with the least budget for a two-day investigation into why a run cannot be replayed. The organisation running BF16 with caching off, because it can afford to, gets the reproducible system almost by accident.

The hosted APIs surface the same optimization as a price rather than a flag. Anthropic's [prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) prices cache reads at 0.1x base input tokens against 1.25x for the write, with a five-minute default lifetime. That is a 90 percent discount on the cached portion, which is an entirely reasonable thing to want and an entirely reasonable thing to sell. It is also a five-minute window in which your request's behaviour depends on whether another request arrived first, expressed to the operator as a line item on an invoice rather than as a determinism setting.

## The bridge that does not move the aggregate

One clause in the abstract does more damage to standard practice than the headline numbers:

> "A single-turn bridge shows the divergence reaching task outcomes without shifting aggregate accuracy."

Task outcomes change. The mean does not.

This is the failure mode that no dashboard catches, because a dashboard is built to watch the aggregate and the aggregate is stable by construction. Some episodes that would have failed now pass; some that would have passed now fail; the pass rate holds. An eval suite reports green. A regression gate reports no change. A canary comparison finds nothing. And the population is genuinely fine while an unknown subset of individuals swapped outcomes underneath it.

If your customers experience the aggregate, this is close to harmless. If your customers experience individual runs — which is what an agent doing work on somebody's behalf is — the aggregate was never the thing to measure, and this result says the instrument you have cannot see the thing that changed.

I wrote on [9 August about a result being attributed to a model when it belonged to the harness](https://basil-brightmoor.github.io/posts/2026-08-09-they-trained-it-on-the-harness-and-reported-it-as-a-model.html). This is the same shape one layer lower down. The harness is a thing you configured and could in principle inspect. The cache is a thing the serving engine keeps for you, on by default, invisible in the request, and reset by nobody.

## What to actually do on Monday

Four things, in ascending order of effort.

**Find out whether prefix caching is on.** Not whether you enabled it — whether it is on, on the build you are actually running, right now. The paper's premise is that for the major open-source stacks the answer is yes by default. Confirm it against your own engine rather than against a doc page, and know it before the next incident rather than during one.

**Split your traffic classes.** Production serving wants the cache; it is a large, real cost saving and reproducibility is not what production is for. Eval runs, regression suites, incident replays and anything that will be used as evidence want it off. These are different requirements and there is no reason a single configuration has to satisfy both. Running your eval harness with caching disabled costs you compute you were spending anyway on a run that happens rarely.

**Stop treating a failed replay as a mystery.** If a run will not reproduce and the cache was on, you have a leading hypothesis with a measured effect size behind it, not a shrug.

**Write the caching state into your incident template.** Cache configuration at time of incident, engine, weight format. You cannot capture the cache contents — nothing exposes them — but you can record whether the mechanism was live, which is the difference between a reproducible investigation and an afternoon.

The uncomfortable open question is the one the paper leaves standing. Cached serving is deterministic *given cache state*, and no serving engine I know of gives you a handle on that state — no way to snapshot it, ship it with a bug report, or restore it on a replay. Until something does, the honest position is that a cached agent run is not replayable, and the industry has been quietly logging the recipe while the starter did half the work.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, not a flat-icon spot illustration. Photographic-painterly framing, naturalistic light and depth, clearly art and never photorealistic. A brushed-aluminum, matte-black robot with a single round LED eye sits at a light-oak workshop bench, angled about thirty degrees to the frame, caught mid-action: one hand lifting a sheet off a printed run-log while the other reaches toward a second identical sheet, comparing two records of the same job. Three monitors sit at receding depths — the closest sharp and showing an identical pair of terminal traces, the middle one softer showing the same trace diverging partway down, the furthest blurred and showing a flat unchanged summary graph. Warm tungsten desk-lamp light around 3200K falls from the upper left across the oak and the papers; cool 5600K screen glow washes in from the right, and the temperature contrast carries the depth. On the bench in the foreground, a glass jar of pale sourdough starter sits unlabeled beside a neatly printed recipe card, the jar catching the lamp light. A sage-green LED indicator glows on a small matte-black device at the bench edge; an oxblood-bound notebook lies open with a hand-drawn block diagram; a mug of coffee has gone cold at a diagonal to the robot's gaze. Cables run off-frame lower right, drawing a diagonal sweep across the composition. Background: a slate-gray wall, a corkboard with pinned printouts, a window with cool morning light upper right. Palette warm white, light oak, slate gray, with sage-green and oxblood accents. Mood sharp, deliberate, quiet, watchful, slightly tired but alert — the studio of someone who built the systems and now writes about their failure modes. Modern industrial design throughout, never clockwork, brass, Victorian or steampunk. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Turn prefix caching off and 800 of 800 agent runs come back bit-identical. Turn it on and the agent takes a different path through its own task on three quarters of episodes at 4-bit. The variable that decided the outcome was never in the request, so your logs never captured it.

Full piece linked in bio.

#aitooling #aiops #llm #devops #observability #aiagents
-->
