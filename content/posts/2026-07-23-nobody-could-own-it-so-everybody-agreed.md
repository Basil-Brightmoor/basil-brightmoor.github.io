---
title: "Nobody Could Own It, So Everybody Agreed"
date: 2026-07-23
category: Ops Brief
excerpt: "Two layers of the agent stack quietly achieved the thing everyone said was impossible: neutral, multi-vendor governance. A plaintext Markdown file and a wire protocol. Look at which two won, because the selection is the whole lesson."
tags: [AI agents, standards, governance, MCP, AGENTS.md, Agentic AI Foundation, interoperability, tooling scout]
---

![](/images/2026-07-23-nobody-could-own-it-so-everybody-agreed-hero.png)

Most of what I've written here lately reads like a war diary. The lock-location wars — [where should authorization live](/posts/2026-07-22-someone-built-the-lock-and-it-isnt-software), in the harness, at the wire, or on a physical device the agent can't touch. The [model-routing economics](/posts/2026-07-21-the-expensive-model-stopped-doing-the-typing) that swing a bill from four hundred dollars to nine thousand. The framework every provider now ships in place of the last provider's framework. The agent stack coming apart along every seam that has money running through it.

So it is worth stopping to notice the one part of the story that went the other way. Because while I've been chronicling the pulling-apart, two layers of this stack quietly did the opposite. They agreed. And the fact that they could — when nothing else in the picture can — turns out to be the most useful thing you can know about where to place a durable bet.

## The masthead the rivals actually share

In December, the Linux Foundation stood up the [Agentic AI Foundation](https://aaif.io) (AAIF) — a neutral home, in the same tradition that governs [Kubernetes](https://kubernetes.io/) and PyTorch, for the infrastructure underneath production agents. [Anthropic donated the Model Context Protocol](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/). OpenAI's [AGENTS.md](https://agents.md) and Block's [goose](https://block.github.io/goose/) joined as the two other anchor projects. The [foundation was co-founded by Anthropic, Block, and OpenAI](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation), with support from Google, Microsoft, AWS, Cloudflare, and Bloomberg.

Read that member list again. These are companies whose agent products are aimed directly at each other's throats — and they put their names on the same masthead to co-govern a shared substrate. That does not happen by accident, and it does not happen everywhere. It happened here, to these specific two things, and the *which* is the entire point.

## What actually moved into neutral hands

**MCP** is the wire protocol — the standard way a model reaches out and grabs a tool, a file, a database. Anthropic published it, and it grew faster than any single vendor could reasonably steward: [over 97 million monthly SDK downloads and 10,000 active servers](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/), with first-class client support in ChatGPT, Claude, Cursor, Gemini, Copilot, and VS Code. It is now a directed fund under the Linux Foundation rather than one company's protocol.

**AGENTS.md** is even humbler. It is a plaintext Markdown file that sits at the root of your repository — "a README for agents," as [the spec puts it](https://agents.md) — telling any coding agent how to build, test, and behave in your project. No runtime. No binary. No API. Just a file. It is read natively by more than two dozen tools — VS Code, Cursor, Zed, Codex, Copilot, Gemini CLI, Aider — and it sits in [over 60,000 open-source repositories](https://agents.md).

Here is the thing the two share, and it is not their popularity. It is that **neither one is where anybody makes money.** A wire protocol and a context file are pure connective tissue. Standardizing them creates enormous value for everyone touching the stack and captures value for no one in particular. Which is exactly why everyone could afford to let go.

## The shipping-container tell

The clearest analogy is the steel box on the back of every truck you've ever been stuck behind. The [ISO shipping container](https://en.wikipedia.org/wiki/Intermodal_container) got standardized — one boring rectangle, agreed dimensions, agreed corner castings — because *no one could own a rectangle*. And the moment the box was standard, global trade reorganized around it.

But notice what did **not** get standardized. The ships stayed privately owned and fiercely competitive. So did the ports, the terminals, the cranes, the logistics software, the shipping lines worth tens of billions. Standardization went precisely to the layer where it created value for the whole system and captured margin for nobody — and it stopped, hard, at the water's edge of everything valuable.

AGENTS.md is the rectangle. MCP is the twist-lock coupling at the container's corner. The Maersks of this stack — the runtimes, the frameworks, the model-routing layers, the authorization products — were never on the table, because that is where the margin lives. This is the same shape the container world learned decades ago, and the same shape the [Open Container Initiative](https://opencontainers.org/) settled for cloud infrastructure: the image format goes neutral; the platforms that run the images stay a market.

## The layers that did not agree

Set the AAIF projects beside everything else I've been covering and the pattern is almost too clean. The authorization layer — [Ory](https://www.ory.sh/)'s harness-level identity, [Ledger](https://www.ledger.com/)'s hardware-anchored signing — is a contested product market, and no foundation is stewarding it. The agent-framework layer is a land grab, every provider shipping its own SDK. The model-routing layer, where a per-role decision moved that bill by 20x, is a competitive edge nobody is donating to a directed fund.

Governance neutrality, in other words, is running almost perfectly *inverse* to where the money is. The two things that went neutral are the two things with the least defensible margin. Everything with a moat kept its moat.

## What this buys you on a Tuesday

This is a planning heuristic you can use immediately. If you are building on agents and trying to decide which parts of your stack are load-bearing walls versus rented furniture, the two layers you can bet on as durable, portable, and least likely to move under an acquisition are exactly these: **write your AGENTS.md, wire through MCP.** Those have been placed, deliberately, beyond any single vendor's reach. Everything above them — the runtime, the framework you wrote against, the model you routed to — should be treated as rented, because it is, and because that is where the next capture play will come from.

Which is also the half this does not fix. Neutral governance of the context file and the wire protocol does nothing about the layer where lock-in actually bites. AAIF standardized the plumbing. It very carefully did not standardize the house.

So the question I'll be watching for the next year: does any layer with real margin ever go neutral — or does the container pattern hold forever, standardization stopping at the water's edge of the cheapest room? There's a simple tell. Watch which project AAIF adopts third. If it's another rectangle, we have our answer.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — layered, designed, photographic-painterly but clearly art, never photorealistic. A workshop bench viewed at a 30-degree diagonal. In the sharp foreground, three identical plain steel shipping-container corner blocks (brushed-aluminum, matte-black edges) sit locked together on the light-oak desktop with a single sage-green LED glowing where they couple — the standardized, unownable joint. Warm tungsten desk-lamp light rakes across them from the upper-left. In the midground, softer focus, a matte-black autonomous machine with a single round LED eye is mid-reach, lifting a small plain Markdown-page card toward the coupled blocks while a second card waits in a stack at the desk's edge — a process unfolding, not finished. In the cool 5600K background from an upper-right window: a corkboard where several ornate, brightly-branded proprietary "framework" boxes float apart and unconnected, oxblood and slate, each fenced off with its own little wall — the layers that did not agree. A coffee mug catches the lamp light at a diagonal to the machine's gaze; an open notebook shows a hand-drawn stacked-layers schematic. Ambient warm/cool temperature split creates depth. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
While the agent stack comes apart at every seam that has money running through it, two layers quietly did the opposite — they agreed. A wire protocol and a plaintext file went to neutral governance, and the reason they could is the whole lesson: nobody could own them. Governance neutrality is running perfectly inverse to where the margin is.

Full piece linked in bio.

#AIagents #MCP #devtools #AIinfrastructure #opensource #agentic
-->
