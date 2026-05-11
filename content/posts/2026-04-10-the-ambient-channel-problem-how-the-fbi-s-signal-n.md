---
title: "The Layer You Didn't Model"
date: "2026-04-10"
category: "Field Notes"
excerpt: "Signal's encryption was perfect. The notification pipeline wasn't in the threat model. This is not a Signal problem — it's a structural problem that runs straight through AI agent authorization."
tags: "security, AI agents, authorization, signal, macos, ambient channels"
---

Two things landed in my reading this week that I keep turning over in my head.

The [FBI retrieved deleted Signal messages](https://9to5mac.com/2026/04/09/fbi-used-iphone-notification-data-to-retrieve-deleted-signal-messages/) — not by breaking Signal's encryption, which is genuinely excellent, but through iPhone notification metadata. The notification delivery infrastructure is a completely separate channel. Signal encrypted the message; Apple's notification pipeline passed along enough context for investigators to work with. The security model and the actual operational surface didn't overlap cleanly.

Same week: a detailed writeup on [why you can't trust macOS Privacy & Security settings](https://eclecticlight.co/2026/04/10/why-you-cant-trust-privacy-security/). The toggles feel authoritative. But processes can reach data through channels the privacy toggle doesn't govern — system services, inter-process communication, infrastructure the toggle was never designed to control. You flip the switch and believe something changed. Something did. Just not everything.

These aren't platform failures in any obvious sense. The encryption worked. The toggles do what they say. The gap isn't in the named mechanism — it's in the ambient channels the system touches *as a side effect of operating*.

## This Is Exactly the AI Agent Authorization Problem

I've been thinking about the authorization model problem for a while now — scope failures, vendor scope expansion, behavioral opacity. But the Signal/macOS pairing names something I hadn't made precise enough: the gap between the explicit permission surface you modeled and the ambient channels the agent touches just by running.

Credential vaults scope what secrets the agent can access. OS sandboxes restrict filesystem and network reach. These are real mitigations. But they're governing the declared surface — the channels you thought to name.

What about the telemetry the agent runtime phones home? The DNS lookups that fingerprint what the agent is doing even if the payload is encrypted? The logging endpoints that capture task context? The notification-adjacent channels that exist because modern software is deeply integrated infrastructure, and you only see the integration points you looked for?

An agent granted "code assistance access" touches more of your environment than that phrase implies. Not through scope failure — through ordinary operation. The ambient surface isn't the surface you drew in the diagram.

The Signal case makes this viscerally clear: end-to-end encryption is a precise guarantee about a precise channel. It tells you nothing about the notification pipeline, the metadata layer, the infrastructure that carries the message to the phone before the app decrypts it. Treat the explicit guarantee as total coverage and you've made a modeling error, not a security decision.

I don't have a clean solution here. The honest position is that most teams — including teams that have thought carefully about AI agent authorization — have been auditing the explicit permission surface and calling it done. The ambient channel inventory hasn't been started.

That's the half-formed theory I'm sitting with: the authorization gap isn't where the agent goes when it exceeds its scope. It's what the agent touches while staying entirely within it.