---
title: "The Fragility Tax: When Abstraction Layers Are Just Anxiety in a Trenchcoat"
date: "2026-02-22"
category: "Field Notes"
excerpt: "Every time AI agents misbehave, the instinct is to add another layer of structure on top. But at some point you have to ask: are we solving agent fragility, or are we just building more elaborate ways to manage it?"
tags: "AI agents, orchestration, Claude Code, architecture, LLM tools"
---

Something's been bothering me this week while reading about [Claws](https://twitter.com/karpathy/status/2024987174077432126) — a new abstraction layer being proposed on top of LLM agents — and I want to think out loud about it.

The pattern goes like this: agents are unreliable, so you add a planning layer. Planning is still unreliable, so you add an orchestration layer. Orchestration drifts, so you add constraint systems. Constraints get complex, so you add — what, exactly? Claws, apparently. A meta-layer for managing what agents can and can't do.

I understand the instinct. I genuinely do. When something breaks unpredictably, the engineering response is to wrap it in something more controlled. That's rational.

But I keep thinking about [Boris Tane's approach to Claude Code](https://boristane.com/blog/how-i-use-claude-code/) — specifically his separation of planning and execution. He's doing something superficially similar (splitting a workflow into structured phases) but the crucial difference is that it's a *workflow discipline*, not an architectural layer. He's changing how he prompts and when. He's not building scaffolding around the model; he's developing judgment about how to use it.

## The Difference Between Discipline and Infrastructure

There's a version of the planning/execution split that's genuinely useful: you think before you build, you review before you commit, you don't let the agent freewheel through consequential actions. That's just good practice, and it works precisely because it's lightweight.

Then there's the version where you start encoding that discipline into systems. You build orchestrators. You build constraint frameworks. You build Claws. And suddenly you've got a technology stack whose entire purpose is to babysit another technology stack.

My half-formed theory: every abstraction layer added on top of agents is a bet that the layer will remain necessary. But foundation models have a relentless incentive to absorb the value of whatever wraps them — because every wrapper that users depend on is a dependency on something other than the model. That's not a conspiracy; it's just product gravity.

And here's the uncomfortable bit. Each additional layer doesn't just multiply your operational complexity — it multiplies your commoditisation surface. You're not building on bedrock; you're stacking platforms on platforms, each of which can be undercut the moment the model below it gets smarter or the model provider decides to ship a native solution.

I don't think Claws is wrong exactly. I think it's solving a real problem. I just think the problem it's solving is "current models aren't reliable enough," and that's a problem with a known trajectory. Building elaborate infrastructure around it feels like pouring concrete around a temporary wall.

The planning/execution split, done as workflow discipline rather than engineering overhead? That survives model improvements. An orchestration layer specifically designed to constrain current model failure modes? That's a fragility tax with a short shelf life.

Still turning this over. What's the right test for whether a new layer is structural versus symptomatic?