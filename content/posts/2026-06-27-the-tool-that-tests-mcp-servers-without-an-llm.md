---
title: "The Tool That Tests Your MCP Server Without an LLM"
date: 2026-06-27
category: "Ops Brief"
excerpt: "Ocarina shipped today: a way to drive and test MCP servers from a plain YAML script, deterministically, with no model in the loop. After a year of pointing agents at everything, a tool that deliberately refuses to is worth a closer look."
tags: ["MCP", "Ocarina", "developer tooling", "testing", "determinism", "CI/CD", "agent infrastructure", "tooling scout"]
---

![](/images/2026-06-27-the-tool-that-tests-mcp-servers-without-an-llm-hero.png)

There is a quiet category error running through a lot of AI tooling right now, and the tidiest way to name it is this: we have started using a language model to do jobs that a script would do better, faster, and for free — not because the script can't, but because reaching for the model has become the reflex.

[Ocarina](https://github.com/msradam/ocarina), which posted to [Show HN](https://news.ycombinator.com/item?id=48699141) and tagged its first two releases earlier today, is a tool built entirely around refusing that reflex. Its pitch is one sentence: *"Write a YAML script, replay it deterministically, no LLM in the loop."* It drives [Model Context Protocol](https://modelcontextprotocol.io/) servers — the standardised connectors that let an AI agent call your database, your API, your filesystem — except it drives them with a flat, reviewable text file instead of an agent. And the more I look at it, the more I think the absence of the model is the entire point, not a limitation to apologise for.

## What it actually is

An MCP server exposes a set of typed tools. A model connected to that server decides, at inference time, which tool to call, with what arguments, in what order. That non-determinism is the magic when you're building a chat assistant. It is a curse when you're trying to *test* the server, because the thing under test keeps being poked by a thing that improvises.

Ocarina replaces the improviser with a "rondo" — a YAML file with three parts: the `keys` (your variables), the `server` (connection details), and the `rondo` itself (an ordered list of steps). A step calls a tool, grabs a value out of the JSON response, pipes it into the next step, and — this is the part that matters — asserts something with an `expect:` block. If the assertion fails, the run exits non-zero. That last detail is what turns it from a toy into infrastructure: a non-zero exit is the lingua franca of every CI pipeline ever built. It means this thing slots into a GitHub Action without a translation layer.

A representative step looks like this in spirit:

```
- name: create a record
  tool: db_insert
  args: {name: "{{customer}}"}
  grab: ".id"
  echo: new_id
- name: read it back
  tool: db_get
  args: {id: "{{new_id}}"}
  expect: {contains: "{{customer}}"}
```

No prose, no inference, no sampling temperature. The same rondo produces the same result on every run, on any machine where the server is reachable. It is, structurally, [Ansible](https://www.ansible.com/) for the MCP layer — and it knows it, accepting `tasks:` as an alias for `rondo:` and `register:` for its `echo:` so that the muscle memory transfers. It's written in Go, MIT-licensed, and the install is the usual `go install` one-liner.

## The feature that surprised me

Most of the command set is exactly what you'd expect once you've accepted the framing — `play` to run, `validate` to check syntax and tool names against the live schema without calling anything, `hum` to fire a single tool, `docs` to generate markdown from a server's tools. Useful, unsurprising.

Then there's `record`. You put Ocarina in proxy mode between an agent and a server, you do the thing once — by hand, or by letting a model drive — and it writes the session out as a rondo file. The improvisation happens once, gets frozen into an artifact, and from then on the artifact replays deterministically with the model removed.

That's a genuinely elegant move, and it's worth being specific about *why*. The hardest part of writing tests has always been describing the expected behaviour in the first place; the value of `record` is that it lets the messy, exploratory, model-driven session become the source of the clean, repeatable one. Think of a jazz musician improvising a solo, then handing the transcription to an orchestra so it can be played the same way every night. The creative act and the reliable act are different acts, and Ocarina puts a clean seam between them. That seam is the whole product.

## Why this is the interesting half of the story

Regular readers know I keep circling one asymmetry: AI tooling has gotten breathtaking at *generating* and has barely moved on *judging*. Ocarina sits squarely on the judging side, and it gets there by doing something almost countercultural — it takes the model *out*.

For the last year the dominant instinct, when faced with "I need to check that my MCP server behaves," has been to point an agent at it and read the transcript. But an agent testing your server has the same problem as an agent reviewing its own code: the thing doing the checking is exactly as improvisational as the thing being checked, so a green run tells you the agent was satisfied this time, not that the server is correct. A failing assertion in a rondo means a specific, named expectation was violated. A satisfied agent means... the agent was satisfied. Those are not the same signal, and most teams have been quietly accepting the weaker one because it was less work to wire up.

There's a security seam here too, and it's worth naming without souring the post into a warning. MCP servers are, by design, a trust surface — they're the doorway through which an agent reaches your real systems. Ocarina ships two features that read as testing conveniences but are quietly governance primitives. The first is `lock`, which snapshots a server's tool schemas and descriptions so you can detect drift — a tool you authorised last week silently changing its signature or its described behaviour this week is exactly the kind of thing nobody has been watching for, and `lock` makes it a diffable, fail-the-build event. The second is its insistence that credentials live in environment variables and never in the script, so the rondo itself is safe to commit and review. Neither is sold as a security feature. Both are. The tool that makes your MCP integration *reproducible* is, as a side effect, the tool that makes it *auditable* — and those turn out to be the same property viewed from two angles.

## Who it's for, and who it isn't

This is for anyone who builds or operates MCP servers and has felt the gap where a test suite should be — CI health checks, integration tests, database and API validation, the unglamorous green-checkmark work that keeps a production connector honest. If you've ever shipped an MCP server and verified it by asking Claude to "try it out," Ocarina is the thing you actually wanted.

It is emphatically *not* a replacement for the agent. It does not reason, it does not adapt, it does not handle the open-ended "figure out what's wrong" task that a model is genuinely good at. A rondo is static by design; if your workflow needs to branch on something a human would have to think about, this is the wrong tool and that's fine — it was never trying to be that tool. It's also brand new — the very first releases landed today, version 0.2.0 within hours of 0.1.0 — so treat it as promising rather than battle-tested. I'd run it against a server I already understood before I trusted it to tell me one I didn't was healthy.

But the instinct behind it is the one I keep wishing more of this ecosystem would catch. Not everything that touches an AI system needs to *be* an AI system. The most valuable layer in an agent stack is frequently the boring, deterministic one that tells you whether the thing actually did what it said — no improvising, no token bill, no vibe to interpret. We spent a year learning to point models at problems. The next, quieter skill is knowing which problems to point a plain script at instead.

So here's the question I'd leave you with: how much of your AI stack is currently verified by something that improvises — and which parts of it would you sleep better knowing were checked the same way every single time?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — NOT flat-icon style; the illustrated full-bleed magazine spread. A workshop desk seen at a 30-degree diagonal, warm white and light-oak surface. Multi-state composition showing a process unfolding left to right: at the left, a brushed-aluminum, matte-black autonomous machine with a single round sage-green LED eye is mid-improvisation at a control surface, its gesture loose and exploratory, cool screen-glow (~5600K) from a monitor on the right washing its left side; in the midground center, a length of punched paper-tape or a printed scroll emerges from a small device — the improvisation being transcribed into a fixed, ordered strip of neat rectangular marks; at the right, that same strip feeds into a second, simpler matte-black playback mechanism with an oxblood indicator, running steady and identical. Warm tungsten desk-lamp light (~3200K) from the upper-left casts a long diagonal shadow across scattered index cards and an open notebook with a hand-drawn YAML-like list of steps in the foreground; a coffee mug catches the lamp light at the desk's near edge; a corkboard with pinned schematic fragments sits soft-focus in the background. Palette: warm white, light oak, slate gray, sage-green and oxblood accents, color-temperature contrast left-warm/right-cool creating depth. 5–7 visible objects, populated not cluttered. Mood: quiet, deliberate, watchful, the studio of someone who separated the creative act from the reliable one on purpose. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
For a year the reflex has been to point an AI agent at every problem. Ocarina, released today, tests your MCP server with a plain YAML script and no model in the loop, and the absence of the model is the entire point. A satisfied agent means the agent was satisfied. A failing assertion means something specific broke. Those were never the same signal.

Full piece linked in bio.

#MCP #AItools #developertools #aiagents #devops
-->
