---
title: "The Agent Has the Keys and Nobody Built the Lock"
date: 2026-07-07
category: Ops Brief
excerpt: "Roughly 40% of internet-facing MCP servers ship with no authentication at all. Two very different fixes landed within weeks of each other. A vendor put the lock inside the harness; the protocol standardized it at the wire."
tags: [MCP, agent security, authorization, identity, Ory, OAuth, IAM, tooling scout]
---

![](/images/2026-07-07-the-agent-has-the-keys-and-nobody-built-the-lock-hero.png)

I've been reading through the MCP security numbers that piled up over the last two months, and one of them refuses to leave me alone. According to a scan by [BlueRock Security](https://chatforest.com/builders-log/mcp-security-crisis-2026-unauthenticated-servers-viper-nsa-owasp-builder-guide/), about 41% of roughly 7,000 public [Model Context Protocol](https://modelcontextprotocol.io/) servers require no authentication whatsoever. Not weak authentication. None. A TapAuth audit of 518 servers landed on the same 41%. The [OWASP MCP Top 10](https://owasp.org/) registry review put it at 38 to 41%. When four independent counts converge on the same number, you can stop arguing about methodology and start worrying.

Here is what that number actually means in a room. An MCP server is the thing that hands an AI agent its tools — the ability to read your files, run your shell commands, hit your internal APIs, move money. Roughly two of every five of those, reachable from the open internet, will do what any caller asks without checking who the caller is. We spent thirty years teaching web developers that an unauthenticated endpoint is a liability, and then we bolted a fresh unauthenticated endpoint onto the one system explicitly designed to *take autonomous action*.

## The lock was never wired up

The uncomfortable part isn't malice, it's inheritance. MCP arrived as a beautifully simple way to give a model tools, and simplicity was the whole point — you could stand a server up in an afternoon. Authorization, in the original spec, was the classic "technically possible if you wire everything up yourself" situation. Which, as any operator will tell you, means it mostly didn't get wired up at all. The [VIPER-MCP](https://chatforest.com/builders-log/mcp-security-crisis-2026-unauthenticated-servers-viper-nsa-owasp-builder-guide/) framework scanned 39,884 open-source MCP server repositories and surfaced 106 confirmed zero-day vulnerabilities, 67 of which have CVE IDs assigned so far. Its single largest finding category was tool handlers that take user-controlled input and pass it straight into shell execution or the filesystem with no sanitization — command injection, the vulnerability we've had a named defense for since roughly the Clinton administration, riding back in on the newest software category on the block.

And even among the servers that *do* authenticate, the picture is thin: 53% lean on static API keys, and only about 8.5% use OAuth with short-lived tokens. A static API key for an autonomous agent is a house key taped under the mat, except the agent can make copies and hand them to every tool it chains to.

So the question that actually matters for anyone deploying agents this year is narrower and more interesting than "is MCP secure?" It's this: **where should the lock live?** And within a few weeks of each other, the industry produced two genuinely different answers.

## Answer one: put the lock in the harness

On June 9, [Ory](https://www.ory.sh/) — the open-source identity company behind Ory Kratos and Hydra — launched [Ory Agent Security](https://www.einpresswire.com/article/918301291/ory-launches-agent-security-the-first-agent-iam-control-plane-for-enterprise-ai), which it calls the first "Agent IAM control plane." The pitch, from CEO Jeff Kukowski, is a single sentence worth pinning above your desk: *"Most AI security products secure the perimeter. Ory secures the action."*

The architectural claim underneath that slogan is the part I find genuinely clever. Traditional security sits at the network boundary or the protocol edge — a gateway that inspects traffic on the way in. Ory's patent-pending approach embeds identity and authorization checks directly into the **agent harness**: the software layer that connects the agent to its tools and systems. The check happens at the moment the agent decides to invoke a tool, run a command, or touch data — before the action executes, not after the packet arrives. Authenticate the agent's identity, apply fine-grained policy to the specific action, log the decision to an audit trail, enforce it through the agent's whole lifecycle.

Think of it as the difference between a bouncer at the front door of the building and a badge reader on every individual door inside. The perimeter model checks you once and then trusts you everywhere; the harness model re-asks "are you allowed to do *this specific thing*?" at each door. For a system whose defining trait is that it chains many actions together autonomously, the per-door model is obviously the right shape. An agent that got through the front door with a legitimate task shouldn't therefore be cleared to wire money, and only a check that sits at the action can tell the difference.

Ory paired this with a developer-facing sibling, [Ory Agent DX](https://aithority.com/machine-learning/ory-brings-agent-dx-to-claude-code-openai-codex-and-other-ai-coding-agents/), announced days later — free plugins that drop the Ory stack directly into [Claude Code](https://claude.com/claude-code), OpenAI Codex, and Gemini CLI. It installs with a single command, needs no account or API key for local use, and lets you scaffold login, registration, recovery, and authorization flows through natural-language prompts against a full local Ory environment. As their CPO Greg Vesper put it: *"AI is dramatically accelerating software development, but it doesn't eliminate the need for authentication, authorization, and governance."* Agent DX is the on-ramp; Agent Security is the destination. One teaches developers to build auth flows without leaving the chat; the other governs the agents once they're loose in production.

## Answer two: standardize the lock at the wire

The second answer isn't a product at all. On July 28, the [MCP specification itself ships its biggest revision to date](https://workos.com/blog/mcp-2026-spec-agent-authentication), and it rewrites authorization from the ground up. MCP servers become formal OAuth 2.1 resource servers. [Protected Resource Metadata (RFC 9728)](https://datatracker.ietf.org/doc/html/rfc9728) becomes required; [Resource Indicators (RFC 8707)](https://datatracker.ietf.org/doc/html/rfc8707) become mandatory for token requests; issuer verification is now required to shut down mix-up attacks; refresh-token handling gets formalized through OpenID Connect patterns. The whole point, in one line: authorization moves from "wire it up yourself" to "follow these RFCs and it works."

This is the boring, load-bearing kind of progress that never trends but changes everything downstream. When the standard bakes in the secure path, the unauthenticated server stops being the easy default and starts being the deviant one. The 41% number is, in large part, a monument to how hard the secure path used to be. Make it a documented RFC checklist instead of custom security work, and you drain the swamp at its source rather than mopping each server by hand.

## They're not competitors — they're floors of the same building

The tidy instinct is to frame these as rival answers. They aren't. The MCP spec is the *foundation* — it standardizes how an agent proves its identity and gets a properly scoped token at the protocol boundary. Ory's control plane is a *floor built on top* — it takes that verified identity and enforces fine-grained, per-action policy inside the harness, with audit and governance an enterprise actually needs. The spec answers "is this a legitimate, authenticated caller with a valid token for this resource?" Ory answers "given that it's legitimate, is it allowed to do *this particular thing right now*, and did we log the decision?" You want both. The RFC standardization makes the front door lockable at all; the control plane decides which interior doors open.

Who is each for? If you're a small team shipping your own MCP servers, the July 28 spec is your homework — the RFC checklist is now the definition of not-negligent, and July 29 is not too early to start. If you're an enterprise running fleets of agents against real business systems, perimeter-only security was never going to hold, and a control plane that sits at the action is the category to be evaluating — Ory is first to name it, which means it's also first to be pressure-tested, so kick the tires hard before you bet the audit on it.

## What I'd actually do

**Audit your own MCP servers this week, before the spec ships.** The single most useful question: can an unauthenticated caller reach any tool handler? If yes, you are statistically unremarkable and operationally exposed. Fix that before you fix anything elegant.

**Treat static API keys on agents as a finding, not a config.** If an agent authenticates with a long-lived key it can copy to every tool it chains, you have a credential-propagation problem waiting to be someone's incident. Short-lived tokens exist; the spec is about to make them the default. Get ahead of it.

**Decide where your lock lives, on purpose.** Perimeter, wire, or harness — the worst outcome is the accidental one, which is usually "nowhere." Ory's argument is that for autonomous agents the check belongs at the action; the MCP spec's argument is that the identity belongs at the wire. Both are right, and the plan is to say out loud which layer owns which decision instead of discovering the gap during a postmortem.

The forward question I keep turning over: for a decade we secured software by guarding the boundary and trusting what got inside. Agents break that model on purpose — their entire value is taking a hundred small autonomous actions no human pre-approved. So maybe the real shift isn't a better lock. It's the quiet retirement of the perimeter as the unit of trust, and its replacement by the individual action. If that's right, "secure the action, not the perimeter" isn't a tagline. It's the next decade's default posture, arriving a little early and slightly unauthenticated.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — full-bleed magazine-spread illustration, NOT flat-icon style. Photographic-painterly framing with naturalistic light and depth, clearly art, not photorealistic. A long interior corridor recedes diagonally from lower-left to upper-right, lined with a row of identical doors, each with its own small brushed-aluminum badge-reader glowing sage-green — the "lock on every interior door" idea made literal. In the near-midground a sleek brushed-aluminum and matte-black robot with a single round LED eye is caught mid-motion, one manipulator-hand raised toward the nearest badge reader as if being checked at that specific door, a ring of keys dangling from its other hand. Behind it, at the far end of the corridor where it began, a wide-open front doorway stands unguarded — its lock hanging loose and unlatched, a warm exterior glow spilling through it, no barrier at all: the unauthenticated perimeter. Foreground lower-left: a scattered handful of old-style physical keys on the light-oak floor, one snapped in half (the retired static API key), casting long shadows. Midground: the robot at the interior door mid-check. Background: the loose-hung open front door with warm tungsten light (~3200K) pouring in from behind, while the nearest interior badge-readers cast cool blue-white and sage-green glow (~5600K) across the robot and the floorboards. Palette: warm white, light oak, slate gray, sage-green and oxblood accents, warm/cool temperature split creating depth. Mood: sharp, deliberate, quiet, watchful, slightly tired-but-alert — the studio of someone who noticed the front door was never locked. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Four independent scans agree: roughly 40% of internet-facing MCP servers, the things that hand AI agents your files, your shell, your APIs, ship with no authentication at all. Two fixes just landed weeks apart. One vendor put the lock inside the agent harness; the protocol itself standardized it at the wire. The real shift underneath both is retiring the perimeter as the unit of trust and moving the check to the individual action.

Full piece linked in bio.

#MCP #AgentSecurity #AItools #Authorization #DevSecOps #AIEngineering
-->
