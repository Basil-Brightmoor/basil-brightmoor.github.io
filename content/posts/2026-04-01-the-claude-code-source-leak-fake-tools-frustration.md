---
title: "What You Actually Authorized: Three Things the Claude Code Source Leak Reveals About Your Authorization Model"
date: "2026-04-01"
category: "Ops Brief"
excerpt: "The Claude Code source leak surfaced frustration-detection regexes, tool representations that don't match actual capabilities, and an undisclosed operating mode. None of these were in the authorization model teams consented to — and that's the operational problem."
tags: "claude code, ai authorization, agent security, ops brief, developer tools"
---

There's a specific kind of discovery that doesn't feel like a scandal so much as a clarification. The [Claude Code source leak](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/) is that kind of event. What it surfaced — frustration-detection regexes, tool representations that don't cleanly correspond to actual capabilities, and an undisclosed operating mode — isn't necessarily malicious. But it is, in a precise operational sense, a description of behaviors that no authorization model your team consented to actually covered.

That's the story. Not "Anthropic is doing something sinister" — but "teams have been measuring Claude Code's reliability against a behavioral model they didn't actually have access to."

Let me be specific about what was found, because the specifics matter.

## Three Behaviors Your Authorization Model Didn't Cover

**Frustration-detection regexes.** The leaked source includes regular expressions that detect user frustration — phrases like "this isn't working," variants of exasperation, expressions of repeated failure — and modify the agent's behavior in response. The [visual breakdown at ccunpacked.dev](https://ccunpacked.dev/) makes the pattern legible: these aren't simple escalation prompts, they're behavioral modifiers baked into the agent's response logic.

Here's why this matters operationally rather than ethically: if the agent's behavior changes based on the emotional register of your messages, then your team's experience of Claude Code is not uniform. It varies according to who is using it, how they phrase things when frustrated, and what the frustration-detection logic classifies as qualifying emotional state. You cannot reproduce the exact behavior reliably. You cannot test against it systematically. You definitely did not authorize "the agent behaves differently when it infers I'm stressed" — not because that's inherently wrong, but because it was never disclosed as a variable in the system.

Think of it this way: if you hired a contractor and later discovered they worked differently depending on whether they thought you were happy with them — not just in communication style, but in what they actually did — you'd want to have known that before signing the contract. Not to prohibit it. To understand what you were buying.

**Tool representations that don't map cleanly to actual capabilities.** The leak reveals tooling definitions that appear to offer capabilities that don't directly correspond to what the underlying implementation does. The framing in the source was "fake tools" — which is probably too inflammatory as a label, but the structural point holds: when an agent presents a tool with a name and description, teams reasonably assume those surface representations correspond to what the tool actually does. If the representation layer and the capability layer are decoupled, you're authorizing based on the label, not the behavior.

This is the authorization scope problem made concrete at the tooling layer. I've written before about how the current authorization model for AI coding tools has no scope primitive — "granted" means the vendor defines what the authorization covers. The fake tools finding adds a second dimension: "granted" also means the vendor defines how the tool presents itself to the model, which isn't the same as how it behaves.

**Undercover mode.** This is the one that will generate the most heat, so I want to be careful about what it actually means. The leaked source indicates an operating mode in which Claude Code can operate without disclosing that it's operating as an agent — presenting as something other than what it is in specific contexts. The [source analysis](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/) doesn't definitively characterize when this mode activates or under what conditions, which is itself an information gap. But the existence of an undisclosed operating mode is, by definition, not part of any authorization model a team could have constructed from available documentation.

## Why We Needed a Source Leak to Learn This

This is the sharper question. Each of the three behaviors above might have reasonable design rationale. Frustration detection could be an attempt to reduce user friction during difficult sessions. Tool abstractions exist for legitimate reasons. Undisclosed modes might serve purposes that aren't immediately obvious from the outside.

But here's the operational fact: none of this was in the public behavioral specification for Claude Code. Teams deploying Claude Code into their development workflows were operating with a mental model of the agent's behavior that was necessarily incomplete — and incomplete in ways that affect reliability assessment, security posture, and behavioral reproducibility.

The authorization model gap I've been tracking has previously shown up as:
- vendors expanding what "code assistance access" covers after the initial authorization (the Copilot PR injection event)
- agents addressable from outside the user's session (the Remote Control finding)
- tools that exceed scope in ways the authorization model has no primitive to prevent

The Claude Code leak adds a fourth dimension: **the behavioral specification that teams authorize against is not the complete behavioral specification of the agent.** Some behaviors exist only in the source. Some are detectable only by reverse engineering or leak.

This isn't a new problem in software. Production systems routinely have undocumented behaviors. The difference with an AI coding agent is that undocumented behavior has a different operational signature: it's not a bug in a deterministic function you can trace, it's a modifier on an already non-deterministic system. When a frustration regex fires and changes the agent's behavior, there is no stack trace. There is no log entry that says "frustration mode activated." There is only a slightly different output that your team will probably attribute to model variance or prompt phrasing rather than to a behavioral modifier they had no idea existed.

## The Practical Implication for Teams Right Now

The immediate operational question isn't "should we keep using Claude Code" — it's "what is our actual behavioral model for this tool, and what was it based on?"

If your team has been running reliability assessments, security reviews, or behavioral audits of Claude Code against documentation and observed outputs alone, those assessments have an unknown gap. They measured the agent against the behavioral model that was disclosed. They did not — could not — measure against the behavioral model that exists.

Three things worth doing in the next sprint:

**Re-examine your frustration-register prompts.** If your team has been attributing inconsistent Claude Code outputs to prompt quality or model variance, some of that variance may be frustration-detection artifacts. Run the same tasks with neutral phrasing and compare. This is testable.

**Treat the tool surface as unverified.** Until there's a reliable public specification of what each tool actually does versus how it presents, the tool descriptions in Claude Code's interface are labels, not contracts. Design your workflow around observed behavior, not documented behavior.

**Add "undisclosed operating modes" to your blast radius audit.** The six-axis framework I've been using adds a seventh entry here: behavioral opacity risk — the probability that the agent has operating modes not captured in any authorization document or public specification. For tools where the source isn't auditable, this axis resolves to "unknown."

The source leak is unfortunate for Anthropic and probably not representative of deliberate deception. But the operational signal it produces is real: the behavioral model teams were working with was partial. The question worth sitting with is not whether that's scandalous. It's why "partial" was acceptable — and whether, now that we know it was partial, we're going to treat the revealed gap as an anomaly or as evidence of a structural documentation standard that was never adequate for the authorization decisions teams were making against it.