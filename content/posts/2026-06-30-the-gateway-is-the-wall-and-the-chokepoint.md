---
title: "The Gateway Is the Wall — and the Chokepoint"
date: 2026-06-30
category: Deep Bench
excerpt: "The MCP gateway crystallized into a real tooling category this year. It finally builds the interior wall I keep saying agent stacks are missing, by becoming the one wall everything leans on."
tags: ["MCP", "MCP gateway", "Bifrost", "Kong", "Cloudflare", "ContextForge", "observability", "ambient authority", "tooling scout"]
---

![](/images/2026-06-30-the-gateway-is-the-wall-and-the-chokepoint-hero.png)

For about a year I've been complaining, in one phrasing or another, that agentic stacks have no interior walls. You wire an AI agent to a dozen [Model Context Protocol](https://modelcontextprotocol.io/) servers — a file tool, a database tool, a Slack tool, a deploy tool — and the moment the grant is made, every one of those tools is reachable by every reasoning step, with no toll booth in between. The agent that was told to "help me tidy this spreadsheet" can also, in the same breath and the same session, reach the tool that sends data somewhere. The authorization model was binary: connected or not. Nobody was standing in the hallway between the rooms.

This month I went looking at what's actually shipping in the MCP tooling space, and the thing that's crystallized is the answer to exactly that complaint. It has a boring infrastructure name — the **MCP gateway** — and it is the most genuinely useful new category I've seen in the agent-tooling world in a while. So let me do the thing I try to do with anything I'm excited about: praise it properly first, then turn it over and show you the seam.

## What an MCP gateway actually is

Strip away the marketing and an MCP gateway is a [centralized proxy that sits between your agents and your MCP servers](https://openobserve.ai/blog/mcp-gateway-guide/). Instead of each agent holding a tangle of direct connections to individual tool servers — each with its own URL, its own credentials, its own behavior — every call goes through one front door. That front door does six jobs: authentication and authorization (who may reach which tool), routing (send this request to the right backend), policy enforcement (organizational rules, time-based restrictions, resource limits), rate limiting (so one runaway agent can't hammer a backend), observability and audit logging (every call timestamped, every latency and error recorded), and protocol translation (bridging MCP to plain REST or gRPC).

If you've worked with web infrastructure, you already know this animal. It's an [API gateway](https://en.wikipedia.org/wiki/API_management) — the same pattern that's sat in front of microservices for fifteen years — re-pointed at the agent-to-tool layer. The reason it's worth a post isn't novelty of mechanism. It's *where* it's standing. The web learned, painfully and over a decade, that you don't let every service talk directly to every other service with ad-hoc credentials and no audit trail. Agent stacks are speed-running that same lesson, and the gateway is the moment the lesson lands.

The category is real and it's populated. A few I looked at:

- **[Bifrost](https://github.com/maximhq/bifrost)** (Maxim AI, written in Go, Apache 2.0) is the one that surprised me — it runs as both an LLM gateway *and* an MCP gateway in a single binary, with routing, guardrails, and observability through one control plane, and it advertises roughly 11 microseconds of overhead per request at 5,000 requests per second. Drop-in via `npx` or a Docker container; existing OpenAI- or Anthropic-SDK code works by changing the base URL.
- **[Kong AI Gateway](https://developer.konghq.com/ai-gateway/)** added first-class MCP support in Gateway 3.12 via its [AI MCP Proxy plugin](https://developer.konghq.com/plugins/ai-mcp-proxy/), with a `mode` parameter that lets it proxy MCP servers, convert existing REST APIs into MCP tools, or expose grouped tools as an MCP server. This is the enterprise-API-management crowd arriving in the agent space carrying everything they already know about OAuth, JWT, and quotas.
- **[Cloudflare](https://www.cloudflare.com/)** shipped MCP Server Portals — present every authorized MCP server behind a single Portal URL, distributed across their 250+ points of presence, so clients configure one endpoint instead of a list.
- **[ContextForge](https://github.com/IBM/mcp-context-forge)** (IBM, Apache 2.0) is an open-source registry-plus-proxy that federates MCP, A2A, and REST/gRPC behind centralized governance, with OpenTelemetry observability and an admin dashboard.

Different shapes, same instinct: stop letting agents hold a fistful of direct tool connections, and put a managed, observable, policy-enforcing layer in the middle. The thing I've been asking for — the toll booth in the hallway — is now a product you can `docker run`.

## The interior wall, finally built

Here's the part I'm genuinely glad about, and I want to be unambiguous about it. The gateway is the first widely-shipping answer to the "no interior walls" problem that isn't just a warning in a blog post.

Concretely: with a gateway in place, "this agent may read the analytics tool but may not reach the tool that sends email" stops being a hope and becomes a routing rule. The agent can no longer reach a backend the gateway won't route it to. The audit log stops being "we think it only did read operations" and becomes a timestamped record of every tool call it actually made. The runaway-loop failure mode — the one that [spent six thousand dollars on AWS before anyone looked](/posts/2026-06-12-the-agent-spent-six-thousand-dollars-before-anyone-looked/) by re-deploying the same template in a loop — meets an actual rate limit instead of a credit-card statement on the first of the month. The gateway turns a pile of *intentions* about what an agent should be allowed to do into *enforced* boundaries with a *record*. That is the legibility I've been circling for months, made operational.

The analogy I keep reaching for is the office building that grew up. Early-stage, everyone has a master key and the doors are propped open because it's faster. It works right up until it spectacularly doesn't — somebody walks out with the server, and there's no badge log to say who. The gateway is the day you install the badge readers: now there's one controlled entry to each wing, every swipe is logged, and "who could reach payroll" is a question with an answer instead of a shrug. Nobody misses the propped doors once the first incident makes the case for them.

## The seam: one wall is also one chokepoint

And now the turn, because there's always a turn, and pretending there isn't is how you end up trusting something more than it earned.

The gateway's power and its risk are the *same property* viewed from two directions. The thing that makes it valuable is that *everything goes through it*. The thing that makes it dangerous is that everything goes through it.

A wall that every agent leans on is, by definition, a single load-bearing point. You've taken ambient authority that used to be *distributed* — messily, illegibly, but distributed — across a dozen direct connections, and you've *concentrated* it into one layer that now holds the credentials to all of them, sees every call, and decides every route. That concentration is exactly what makes the audit log possible. It's also what makes the gateway the most valuable thing in the stack to compromise, to misconfigure, or to lose. The [routing-layer-as-attack-target argument I made about LiteLLM](/posts/2026-04-02-litelllm-got-compromised-your-routing-layer-is-the-target/) isn't a different problem from this one — it's this exact problem, and the gateway is the routing layer with a nicer dashboard. A tool that brokers access to everything is worth poisoning for precisely the reason it's worth buying.

There are three specific places I'd keep my eyes when I put one of these in:

**The credential collapse.** Before the gateway, a leaked token from one tool server cost you one tool server. After, the gateway is where the keys live — it injects credentials on the agent's behalf so the agent never holds them, which is genuinely good hygiene, right up until the gateway itself is the thing that's breached or misconfigured. You didn't remove the blast radius; you moved it to one address and made that address load-bearing. Worth it, usually. But it's a trade, not a free win, and the teams who'll be glad they made it are the ones who made it *on purpose* and guard that one address accordingly.

**The policy you didn't write.** A routing rule enforces what you *wrote*, with the literal-minded diligence of all infrastructure, not what you *meant*. "Agent may reach the database tool" reads as a safe read-only grant in your head and as full read-write at the gateway unless you scoped it. The gateway makes boundaries enforceable, which is precisely why a sloppy boundary is now *enforced sloppiness* at scale. The wall does exactly what the config says. The config is now the thing that has to be right, and it's the thing nobody reviews with the seriousness they'd give the agent itself.

**The dependency you just added.** A gateway in the request path means every agent-to-tool call now depends on the gateway being up, correct, and not the bottleneck. The managed ones (Cloudflare, Kong's commercial tier) trade your "I run my own proxy" independence for "someone else runs the one chokepoint every agent in my stack passes through" — the same [control-plane-on-one-vendor](/posts/2026-06-26-aws-sells-the-off-switch-i-said-was-missing/) shape I keep meeting. When the chokepoint is also someone else's account, an outage or a policy suspension takes your whole agent fleet's hands off the tools at once, not one tool at a time. The self-hosted ones (Bifrost, ContextForge) keep the chokepoint in your basement, which is more work and more yours.

## So: put one in, and know what you built

None of this is an argument against gateways. It's an argument for installing one with your eyes open. The interior wall is real, it's overdue, and "every tool call is logged and policy-checked" is a strictly better world than "we grant access and hope." If you're running agents against more than two or three MCP servers and you don't have a gateway, the propped-doors phase is running out of road, and an open-source binary you control — Bifrost or ContextForge — is a very reasonable afternoon.

Just hold the two truths at once. The gateway is the wall you've been missing *and* the chokepoint you've just created, and those are the same fact. So treat the gateway config with the same suspicion you'd train on the agent: scope the routes like they're enforced, because now they are; keep one observation point that doesn't run through the gateway's own logs, so a single failure can't go dark *and* erase its own trail; and decide, on purpose, whether the one address that now holds all the keys lives in your basement or someone else's building.

A wall is only as good as your honesty about what's now leaning on it. What's the one tool in your stack you'd least want a misrouted agent to reach — and does anything between the agent and that tool currently know how to say no?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — NOT flat-icon style. A workshop desk scene shot at a 30-degree diagonal: in the sharp foreground, a single brushed-aluminum, matte-black autonomous machine with one round sage-green LED eye stands mid-motion at a small control panel, its hand reaching toward one gate in a row of three small numbered turnstile-style gates set into a low interior wall that runs diagonally across the midground — one gate glowing open with warm light, two shut. Behind the wall, in soft focus, a dense thicket of cables and small server-boxes (the dozen tools) fans out, every cable funneling INTO the single wall like rivers into one lock. Foreground left: a coffee mug catching warm tungsten lamp light at ~3200K from the upper-left; foreground right: an open notebook with a hand-drawn schematic of a single chokepoint and arrows converging on it. Midground: a secondary monitor showing a clean audit-log dashboard with rows of timestamped entries, lit cool ~5600K screen glow. Background: a window with cool morning light and a corkboard with pinned papers. Three states visible at once — gates opening, cables converging, log scrolling. Palette: warm white, light oak desktop, slate gray, sage-green and oxblood accents, with warm/cool color-temperature contrast creating depth. 5-7 populated objects, diagonal leading lines from the converging cables pulling the eye across in a Z-sweep. Mood: sharp, deliberate, quiet, watchful, the studio of someone who built the systems and now writes about their failure modes. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
The MCP gateway finally builds the interior wall agent stacks have been missing. Every tool call routed, policy-checked, logged. The catch: a wall every agent leans on is also the one chokepoint worth poisoning. Same fact, two directions.

Full piece linked in bio.

#AIagents #MCP #devtools #AIsecurity #aiinfrastructure
-->
