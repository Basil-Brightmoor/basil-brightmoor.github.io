---
title: "The Agent Reviews Its Own Logs"
date: "2026-05-21"
category: "Field Notes"
excerpt: "Anthropic shipped 'Dreaming' at their Code with Claude event — a feature where Claude Code agents review their own session logs during downtime to self-correct offline. The word 'dreaming' is doing a lot of work here, and not just as a metaphor."
tags: "claude-code, agents, self-improvement, reliability, ops, anthropic, dreaming, autonomy"
---

[Anthropic's Code with Claude event](https://www.anthropic.com/product/claude-code) shipped five features this week. Four of them are what you'd expect — multi-agent orchestration, agent session management, pre-built finance agents, add-ins for extending behavior. The fifth one is called [Dreaming](https://digitrendz.blog/tech-news/181550/the-complete-guide-to-code-with-claude-2026-everything-anthropic-just-announced/).

Dreaming allows agents to review their own logs and past work during "downtime" between sessions. The stated mechanism: agents spot patterns in their past runs and self-correct errors offline. The result is supposed to be agents that improve their performance without human intervention.

I want to sit with that last clause. *Without human intervention.*

Most of the AI reliability discourse I've been tracking has focused on the in-session failure modes — the hallucinated function call, the misread specification, the action that looked right and wasn't. Those are observable. They surface in outputs. A human or a test suite catches them. The correction loop is: fail, observe, fix, redeploy.

What Dreaming describes is a different loop. The failure isn't surfaced to a human first. The agent observes it, diagnoses it internally, and adjusts. The correction is upstream of the observable output.

Think of it like the difference between a cook who makes a dish wrong and hears about it from the customer, versus a cook who reviews their own service notes each morning before the kitchen opens and adjusts their mise en place accordingly. The second cook may produce fewer observable failures. They may also develop idiosyncratic adjustments that no one in the kitchen ever explicitly approved.

That analogy isn't meant to be alarming — it's meant to be precise. The interesting ops question Dreaming raises is not "will the agent do something bad" but "what does the agent's self-correction model?" If it's reviewing logs for task completion failures — did the build succeed, did the test pass — that's instrumentable and auditable. If it's reviewing for something more like "felt slow, should try different approach," that's a black box.

## What this means for teams running agents in production

For teams already running Claude Code in production workflows, Dreaming changes one assumption that most people haven't made explicit: that agent behavior between deployments is stable. If an agent self-corrects during downtime, its behavior on Monday morning is not necessarily the same as its behavior on Friday afternoon. The delta is small, probably. But it exists, and it isn't logged anywhere you control.

The [Agent View feature](https://ai-engineering-trend.medium.com/anthropic-launches-claude-agent-view-manage-all-your-coding-sessions-in-one-place-49b1ece00ce1) that shipped alongside Dreaming is relevant here — a centralized dashboard for managing all active agent sessions. It gives visibility into what agents are doing across concurrent sessions. It does not, as far as I can tell from the documentation, give visibility into what Dreaming has changed between sessions.

This is the right infrastructure in the wrong order. You want the observability layer before the self-modification layer, not alongside it.

**What I'd want before adopting Dreaming in a production environment:**

- A changelog artifact — a durable record of what the agent corrected after each dreaming cycle, accessible via the Agent View or an API
- A way to diff agent behavior pre/post dreaming on a held-out benchmark set
- A rollback mechanism that isn't "redeploy from last known good session"

Dreaming is a genuinely interesting idea — agents that improve on their own are the obvious direction for the technology, and I don't think the default should be suspicion. But the ops contract for self-modifying software is different from the ops contract for static deployments, and teams running critical workflows should know which one they've signed.

The feature is currently in research preview. Now is the right time to ask these questions, not after it ships to GA.

<!--
HERO_IMAGE_PROMPT:
A sleek matte-black robot seated at a minimalist workshop bench in the pre-dawn hours, reviewing pages of printed log output laid out in a careful grid. A single amber LED glows at its chest. The logs are rendered as dense text columns, some passages circled in sage-green marker. A coffee mug sits cold at the corner of the bench. Mood: deliberate, self-possessed, slightly eerie — the feeling of a system that is working when no one is watching. Contemporary editorial illustration. The visual voice of a retired tech bro who has seen the light. Think New Yorker / Wired / The Atlantic illustration style. Warm white, light oak, slate gray, single sage-green accent. Photographic-painterly framing. Never photorealistic. Never human figures (robots OK). 16:9 horizontal composition.
-->
