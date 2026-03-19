---
title: "We're Pipelining the Agents But Not the Specs"
date: "2026-03-19"
category: "Field Notes"
excerpt: "Two things appeared on HN in the same week: a thesis that a sufficiently detailed spec collapses into code, and a CLI tool for orchestrating Claude Code as a pipeline stage. Nobody connected them. They should be connected."
tags: "field notes, AI agents, specification, orchestration, governance"
---

Two things appeared on HN this week and nobody connected them.

First: a [post arguing that a sufficiently detailed spec is code](https://haskellforall.com/2026/03/a-sufficiently-detailed-spec-is-code). The thesis is what it sounds like — at sufficient detail, the boundary between "describing what to build" and "building it" dissolves. A spec precise enough to be unambiguous is a spec precise enough to execute.

Second: [Cook](https://rjcorwin.github.io/cook/), a CLI tool for orchestrating Claude Code as a pipeline stage. Feed it tasks, wire it into CI, run agents headlessly. Serious execution infrastructure. The kind of thing you build when agents are doing real work.

Here's what struck me: we're treating these as separate problems. They're the same problem.

## The Inversion Nobody Is Talking About

If the spec-is-code thesis holds — even partially — then specs aren't ephemeral inputs to agents. They're the executable layer. The agent is the runtime.

And yet: look at how teams are actually operating. Cook and tools like it get versioned, tested, integrated into pipelines. The *specs* those pipelines consume? Pasted into chat windows, drafted in Notion, shared as Slack messages, stored in someone's Downloads folder. Ungoverned. Unversioned. Effectively anonymous.

We're building serious infrastructure to run the thing that runs the spec, while the spec itself has no owner, no history, and no audit trail.

This is backwards. If the spec is what actually determines what the agent does — and it is, especially as agents get more capable and specs get more detailed — then the spec is where the accountability should live. Instead, we've inverted it: sophisticated execution layer, chaotic specification layer.

## Why This Will Bite Teams

I've been reading about the context engineering debates that have been surfacing lately — the passionate arguments over whether to share CLAUDE.md configurations, what belongs in an AGENTS.md, how to write specs that actually work. What strikes me is that all of this discussion treats the spec as a *craft* question. How do I write a good one?

Nobody is asking the *governance* question: where does it live, who owns it, what changed between last week's run and this week's, why did the agent do something different on Tuesday?

When Cook runs a headless Claude Code session overnight and the output is wrong, the debugging story is: check the logs, check the code, check the CI artifacts. Nobody thinks to ask "wait, what exact spec did the agent receive, and is that the same spec it received last time?"

Because the spec is a text file in a repo with no blame history, or a prompt someone typed from memory, or — charitably — a markdown document that got quietly edited at some point.

The Cook announcement thread is full of excitement about the orchestration possibilities. Rightly so — it's a clean, useful tool. But if the spec-is-code people are right, then what we've actually built is a pipeline with rigorous version control on the interpreter and none whatsoever on the program.

That's not a workflow. That's a liability waiting for a bad Tuesday.