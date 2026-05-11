---
title: "The Oversight Pattern Nobody Designed For"
date: "2026-03-12"
category: "Ops Brief"
excerpt: "The first real data on how humans oversee AI coding agents is in. Experienced users don't approve each step or fully delegate — they auto-approve more AND interrupt more. That third pattern has infrastructure implications nobody is building for."
tags: "AI agents, oversight, Claude Code, accountability, developer workflows, autonomy"
---

## The Data Is In, and It's Weird

[Anthropic published research this week](https://www.anthropic.com/research/measuring-agent-autonomy) analyzing millions of human-agent interactions, including complete Claude Code session lifecycles. Separately, a team behind a tool called [rudel.ai](https://github.com/obsessiondb/rudel) posted their own analysis of 1,573 Claude Code sessions on Hacker News — 15 million tokens and 270,000 interactions across three months of real development work.

Both datasets point to the same surprising finding, and it's not what either the "AI will replace developers" camp or the "humans must approve every action" camp expected.

## The Third Pattern

Here's the naive model of how human oversight should scale with experience: either you trust the agent more over time (approve more, intervene less) or you trust it less (approve less, intervene more). Delegation or control. Pick one.

The data shows neither. It shows both simultaneously.

New Claude Code users employed full auto-approval in roughly 20% of their sessions. Experienced users increased that to over 40%. So far, the delegation story. But experienced users also interrupt at nearly double the rate of new users — around 9% versus 5%. They're approving more *and* intervening more.

This is the emergence of a third oversight pattern. Not step-by-step approval. Not full delegation. Something closer to supervisory monitoring — let the agent run, watch the trajectory, and intervene when the trajectory looks wrong. It's the difference between a driving instructor who grabs the wheel at every intersection and a senior pilot who watches the autopilot and takes over when the instruments look off.

The analogy matters because these two approaches require completely different infrastructure. Step-by-step approval needs a confirmation dialog. Full delegation needs good rollback. Supervisory monitoring needs something else entirely: *legible state*. The human needs to be able to glance at what's happening and quickly determine whether the trajectory is acceptable — not whether each individual action is correct, but whether the overall direction makes sense.

## What the Rudel Data Adds

The rudel.ai analysis fills in a detail the Anthropic study doesn't emphasize: 26% of sessions are abandoned, most within the first 60 seconds. And error cascades in the first two minutes predict whether the session will be abandoned.

Read those two findings together. Experienced users don't just auto-approve more — they bail faster when things go wrong. The monitoring pattern isn't passive trust. It's active triage. The experienced user has developed an internal model of what a productive session looks like in its first minutes, and when reality diverges from that model, they cut losses immediately rather than trying to steer a struggling agent back on track.

This is operationally significant. It means the critical window for agent-human interaction isn't the middle of a session (where the work happens) or the end (where the review happens). It's the first two minutes. The agent's initial framing — how it interprets the task, what approach it proposes, what it reaches for first — is where the experienced user makes the go/no-go decision.

## The Infrastructure Gap

Here's the problem: almost none of the emerging AI oversight tooling is built for supervisory monitoring.

The approval-pattern tools are well-understood: permission dialogs, scope restrictions, confirmation prompts. The delegation-pattern tools are emerging: sandbox environments, rollback mechanisms, automated test gates. But the monitoring-pattern tools — the ones that give a human legible, glanceable state about an agent's trajectory — are barely a category yet.

What would monitoring-pattern infrastructure actually look like? A few things come to mind:

**Trajectory summaries, not action logs.** The experienced user who interrupts at 9% isn't reading every action. They need a compressed signal: "the agent is refactoring the auth module" or "the agent is installing three new dependencies it wasn't asked about." Direction, not steps.

**Early-session diagnostics.** If the first two minutes predict abandonment, there's value in surfacing what the agent is *about to do* before it starts doing it. Not a confirmation dialog — that's the approval pattern. More like an intent declaration: "I'm planning to approach this by..."

**Deviation alerts.** In the supervisory monitoring pattern, the human isn't watching continuously. They need to be pulled back in when the trajectory diverges from the expected path. Not when any individual action fails, but when the *direction* shifts in a way the human didn't authorize.

Anthropic's own recommendation in the study is telling: they argue against mandating specific approval patterns and suggest focus should remain on whether humans *can* effectively monitor and intervene. That's the right framing. But "can" is doing a lot of work in that sentence, because right now the monitoring affordances are thin.

## Why This Matters Beyond Developer Tools

The supervisory monitoring pattern isn't unique to coding. It's the same pattern that emerged in aviation automation, in industrial process control, in any domain where skilled operators oversee automated systems. The literature on this is decades deep, and one of its central findings is consistent: the monitoring pattern is the hardest to support well, because it requires the human to maintain situational awareness without actively doing the work that would sustain it.

In aviation, this is called the "automation paradox" — the better the autopilot, the harder it is for the pilot to stay engaged enough to catch the moments when the autopilot is wrong. The intervention skill atrophies precisely because it's exercised less frequently.

The Anthropic data is showing the early stages of the same dynamic in AI-assisted development. Experienced users are developing the monitoring pattern naturally, but we don't know yet whether their interventions are well-calibrated or whether they're catching the right failure modes. A 9% interrupt rate tells you something is happening. It doesn't tell you whether the interrupts are at the right moments.

## The Practical Question

If you're running a team that uses AI coding agents, the Anthropic data suggests you should stop thinking about oversight as a binary — "do we approve each step or not?" — and start thinking about it as a monitoring design problem.

What does your team see when an agent is running? Can they tell, at a glance, what the agent is doing and whether it's on track? When they interrupt, is it because of good signal or because of anxiety? When they don't interrupt, is it because the trajectory is correct or because they stopped watching?

The rudel.ai team is building toward session analytics. Anthropic is building toward code review. Both are useful. But neither is quite the thing the data is pointing at, which is trajectory legibility — the ability for a human to understand, quickly and accurately, where the agent is heading and whether that's where it should be heading.

The oversight pattern the data reveals is the right one. It's more efficient than step-by-step approval and more accountable than full delegation. But it needs infrastructure that doesn't exist yet — infrastructure that treats the human not as an approver or a delegator but as a monitor who needs the right instruments on the dashboard.

We built the autopilot. Now we need the flight instruments.
