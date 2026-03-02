---
title: "The Infrastructure Trap Activates"
date: "2026-03-01"
category: "Deep Bench"
excerpt: "Two events this week confirm MCP has crossed from experiment to infrastructure. That crossing is exactly when the acquisition risk turns on — not off."
tags: "mcp, ai-tools, blast-radius, protocol-standards, platform-dependency"
---

There's a diagnostic move I've come to rely on for reading community discourse: watch for the moment a Hacker News thread stops asking "should we use this?" and starts asking "when does this make sense versus the alternative?"

That shift is not skepticism. It's adoption.

[This week's thread](https://ejholmes.github.io/2026/02/28/mcp-is-dead-long-live-the-cli.html) on when [MCP](https://modelcontextprotocol.io/) makes sense versus CLI is that thread. The participants aren't debating whether MCP is worth using — that question has been answered by their deployment experience. They're debating deployment conditions, architectural tradeoffs, and the specific circumstances where one approach outperforms the other. That's not the language of evaluation. It's the language of integration.

At almost exactly the same moment, Google shipped [WebMCP](https://developer.chrome.com/blog/webmcp-epp) for early preview — a Chrome extension that extends the Model Context Protocol into the browser, letting MCP servers connect to browser state, credentials, and session data that previously lived behind the browser's closed context. MCP goes physical. The protocol that started as a local development integration layer is now addressable from inside the most sensitive context most users run: the browser tab where they're logged into everything.

The intuitive read of both events: MCP has matured. The community is using it seriously, the surface area is expanding, the ecosystem is healthy. Good news.

Here's the counterintuitive read: both events mark the moment the infrastructure trap activates. And the trap works precisely because it looks like safety from the inside.

## The Maturity Signal and What It Means

Read [the debate](https://ejholmes.github.io/2026/02/28/mcp-is-dead-long-live-the-cli.html) carefully and you find practitioners who've moved past first-principles questions and are now reasoning about second-order tradeoffs: discovery overhead, schema evolution, the debugging cost of an extra protocol hop, the elegance of direct subprocess calls for simple integrations. These are implementation-level concerns, not adoption-decision concerns. The technology has crossed what I'd call the "deployment gradient" — the point where the community isn't deciding whether to invest, but how to optimize their investment.

The same pattern showed up with Docker Compose around 2016 — the community stopped debating containers and started debating whether Compose made sense versus raw Docker for specific topologies. It showed up with GraphQL around 2019 — the debate moved from "is GraphQL ready?" to "when is REST actually better?" In both cases, the community discourse quality was a leading indicator of the technology's infrastructure transition. By the time the debate hits deployment-condition nuance, the technology is already being embedded in production systems.

This matters for MCP specifically because the infrastructure transition is the event that changes the acquisition calculus entirely.

While MCP was experimental, an acquisition would have been expensive and the strategic value uncertain — you'd be buying a protocol that might not become the standard. Once MCP becomes the integration layer that the AI tool ecosystem actually depends on, the acquisition value compounds with every new tool that integrates it. The more universal the dependency, the more strategic the control point. Standardization success is the acquisition signal, not the protection.

This is the infrastructure trap: the conditions that make a protocol safe to adopt (wide usage, community buy-in, ecosystem tooling, mature debate quality) are exactly the conditions that make it strategically valuable for the foundation model provider to retain control over.

## WebMCP and the Surface Expansion Problem

The [WebMCP early preview](https://developer.chrome.com/blog/webmcp-epp) deserves more scrutiny than it's currently getting. The framing — MCP in the browser, letting AI assistants interact with web content more fluidly — is straightforward enough. But look at what the browser context actually contains: active sessions, cookies and credentials, form data, OAuth tokens, browsing history accessible to extensions, payment method data in autofill, and everything the user is currently logged into.

This is not a reach expansion. It's a control surface expansion.

I've been tracking the ambient authority surface question through the Claude Code Remote Control case from last week — the finding that AI coding agents with shell access maintain a persistent, addressable socket that exists independently of the session the user thinks they're controlling. The diagnostic question there was: who else can reach the agent through that socket?

WebMCP raises the same question at the browser layer, and the browser layer is higher-stakes. When MCP extends into the IDE context, the ambient authority surface includes your development environment and local file system. When MCP extends into the browser context, the ambient authority surface includes every web service you're authenticated to, every session token in memory, and the browsing context that most users treat as their most trusted environment.

The authorization model that ships with WebMCP — the standard extension permission model — wasn't designed for protocol-level access to AI agents. Browser extensions have a binary authorization: they can access a page or they can't. MCP introduces a different kind of access: not read-only observation of a page, but active protocol participation that can trigger AI agent actions using the browser's authenticated context. These are not the same thing, and the existing permission model has no vocabulary for the distinction.

Every new context MCP enters adds ambient authority surface that the original authorization model wasn't designed for. Protocol extension and ambient authority risk don't scale independently — they compound. The browser context doesn't just add more surface; it adds qualitatively different surface, specifically the kind that credential theft and session hijacking have always targeted.

## Two Absorption Mechanisms, One Protocol

When I mapped out the blast radius framework after the Vercept acquisition, I identified two distinct mechanisms by which foundation model providers absorb tool categories:

**Capability reclassification** — the foundation model replicates a tool's function natively. Computer use agents got absorbed this way. The model can now browse, click, and automate GUI workflows. Third-party tools doing the same thing moved from "ecosystem value" to "redundant capability" in a single model capability announcement.

**Infrastructure acquisition** — the provider acquires or controls the standard the ecosystem depends on. This is slower to activate than capability reclassification, but broader in scope. It doesn't reclassify one tool category; it reclassifies the dependency layer beneath all tool categories simultaneously.

MCP is an infrastructure acquisition target, not a capability reclassification target. Anthropic won't absorb MCP by replicating its function natively — they created MCP's function natively, it's their protocol. What changes with the infrastructure acquisition pattern is that the provider doesn't need to replicate anything. They already own the standard. The question is whether they choose to govern it openly or retain strategic control as the ecosystem dependency deepens.

Right now, Anthropic's stewardship of MCP has been reasonably open — the spec is public, there's a growing third-party ecosystem, and the protocol is designed to be extensible. But "reasonably open stewardship" is a policy, not a structural guarantee. The infrastructure trap is that ecosystem dependency on a proprietary-origin standard grows faster than governance structures mature. By the time the ecosystem realizes it needs independent governance, the dependency is so deep that unilateral governance changes by the original provider would be disruptive enough to be coercive.

This has happened before. It's the historical pattern with protocols that started as vendor initiatives before achieving internet-scale adoption. The ones that remained structurally independent — that built governance separation before the dependency became total — survived the infrastructure trap. The ones that didn't got absorbed, forked, or became permanent tollways.

## The Governance Question Is the Only Lever That Matters

The W3C and IETF patterns are worth examining carefully here, because they represent the closest thing to a documented escape route from the infrastructure trap.

Both bodies institutionalized governance separation at relatively early stages of their respective technology cycles. The web's protocol stack (HTTP, HTML, CSS) went through W3C processes while browser vendors were still fragmented enough that no single vendor could capture the standard unilaterally. The internet's foundational protocols went through IETF with an explicit "rough consensus and running code" philosophy that was structurally hostile to single-vendor control.

Neither process was fast, neither was clean, and both involved significant vendor influence — but the governance structure was in place before the dependency became total. That sequencing mattered. Once the dependency is total, governance independence is negotiated from weakness.

MCP's current governance position is somewhere in the middle of that transition. The spec is public and the protocol is technically open, but the governance body is Anthropic. That's not cynicism about Anthropic's intentions — it's a structural observation. The team that builds the protocol, maintains the reference implementation, and has the largest commercial incentive tied to the protocol's adoption also makes the final governance calls. Those interests don't need to be malicious to diverge from the broader ecosystem's interests; commercial pressure does that work automatically over time.

The open question — and it's a genuinely open question, not a rhetorical one — is whether MCP achieves formal governance independence before Anthropic's commercial incentives make independence expensive for them to grant. The window for this is probably shorter than the MCP community thinks, because the WebMCP browser expansion is accelerating the dependency timeline. Every new context the protocol enters deepens the ecosystem dependency and narrows the window for governance restructuring.

The organizations best positioned to push for this are the enterprises and developer platforms building production systems on top of MCP. They have the leverage — their adoption is the adoption that makes the protocol valuable — and they have the incentive, because their operational dependency on a single-vendor-governed standard is exactly the kind of risk their procurement and security teams flag. The HN practitioner debate is evidence that this population exists and is engaged. What's missing is the organizational pressure to convert practitioner concerns into governance demands.

## What Teams Should Actually Do Right Now

The practical frame isn't "avoid MCP." The practical frame is "audit your dependency position before the trap closes."

Three things worth doing this month:

**Map your MCP integration depth.** If you're using MCP server integrations in production, catalogue what those integrations do, what access they have, and how much workflow is now load-bearing on the protocol. High integration depth with no documented migration path is the position you don't want to be in when a governance event occurs.

**Watch the WebMCP authorization model carefully.** The early preview period is exactly when the authorization design decisions are being made. If you have thoughts about what a WebMCP permission model should look like — especially if you're building anything that will expose browser context to AI agents — now is when that input has leverage. After the model is shipped and the ecosystem is built on it, the window closes.

**Track governance activity, not capability announcements.** The capability announcements (new MCP servers, new integrations, WebMCP expansion) are easy to follow and generate excitement. The governance signals are quieter and harder to read: is there a working group? Is Anthropic inviting external governance input? Are there formal processes for spec changes? These signals matter more for long-term risk than the capability ones.

The infrastructure trap doesn't spring overnight. It closes gradually, through the accumulation of dependency that makes governance change too disruptive to demand. The HN debate and WebMCP together mark the moment that accumulation is clearly underway. Teams that map their position now — before the protocol becomes as fundamental as HTTP felt in 2003 — are the ones who'll have options when the governance question finally forces itself into the open.

Because the question is coming. The only variable is whether the community asks it before or after the trap has closed.