---
title: "The Kill Switch Is Now Infrastructure"
date: "2026-03-09"
category: "Tool Report"
excerpt: "Agent Safehouse treats AI containment as a first-class product concern. The fact that something like this now exists is the more interesting signal."
tags: "AI agents, security, sandboxing, defensive tooling, macOS"
---

Something about [Agent Safehouse](https://agent-safehouse.dev/) stopped me mid-scroll: it's a macOS-native sandbox for local AI agents. Not a configuration guide. Not a best-practices doc. An actual product, built specifically to contain what your coding agent does while it's running.

That's new. And what it signals is more interesting than the tool itself.

## What It Does

Agent Safehouse wraps your local agent in a macOS sandbox layer — restricting filesystem access, network calls, and process spawning to what you've explicitly permitted. The agent runs; it just can't roam. Think of it as a playpen with walls you designed rather than a house with doors you forgot to lock.

Who it's for: developers running agentic coding tools — Claude Code, Cursor, similar — who've granted shell access and are starting to feel the ambient authority problem in their gut even if they haven't named it yet. Who it's not for: teams running cloud-hosted agents where the containment question lives at the infrastructure layer, not the laptop layer.

## The Signal

Here's what Agent Safehouse's existence tells me: the kill switch instinct — that vague discomfort developers feel when they realize an agent has more authority than they consciously intended to grant — has matured enough to attract product builders.

That's a meaningful threshold. Tools don't get built until a pain point is specific enough, widespread enough, and sticky enough to justify the work. Somebody looked at the "I gave my agent shell access and now I'm not entirely sure what it can reach" problem and decided it was worth building infrastructure around.

I wrote a few weeks back that [Firefox shipping a kill switch](https://agent-safehouse.dev/) was an admission that the grant/revoke model is broken for ambient agents. Agent Safehouse is the same admission, packaged as a local tool rather than a browser feature. The instinct is identical: *authorized* no longer reliably predicts *intended*, and we need a containment layer to cover the gap.

The deeper pattern worth watching: defensive AI tooling is splitting into two categories. One is reactive — kill switches, scope limiters, things you reach for after something goes wrong or nearly does. The other is proactive — tools like Agent Safehouse that you install *before* the incident, because you've internalized that ambient authority is a structural condition of running local agents, not an edge case.

The proactive category is newer. Its existence means the developer community is getting ahead of the authorization failure rather than just responding to it.

That's progress. Not comfort — but progress.

**Practical takeaway:** If you're running a local coding agent with shell access and you're on macOS, Agent Safehouse is worth fifteen minutes of evaluation time. Not because something has gone wrong. Because the architecture makes "something goes wrong" more likely than most developers currently price in.