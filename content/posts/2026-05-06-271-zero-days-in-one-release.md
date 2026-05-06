---
title: "271 Zero-Days In One Release"
date: 2026-05-06
category: "Field Notes"
type: note-candidate
excerpt: "Mozilla just shipped Firefox 150 with fixes for 271 vulnerabilities found by Claude Mythos Preview. The framing in their post — 'defenders finally have a chance to win, decisively' — is the most important sentence in AI security this month."
tags: "AI security, Mozilla, Firefox, vulnerability discovery, Claude Mythos, defender advantage, honest test"
---

Quick one, because I want to flag the signal while it's fresh.

[Mozilla's "The zero-days are numbered"](https://blog.mozilla.org/en/privacy-security/ai-security-zero-day-vulnerabilities/) (April 21, Bobby Holley) reports that Firefox 150 ships with fixes for **271 vulnerabilities** found by an early version of Claude Mythos Preview, on the heels of 22 found by Opus 4.6 in Firefox 148. The number is staggering. The framing is more important than the number.

> "For a hardened target, just one such bug would have been red-alert in 2025."

The argument: until now, security has been *offensively dominant* — attackers needed to find one bug, defenders had to find them all, and the asymmetry favoured the attacker. AI vulnerability discovery collapses that asymmetry by making "find them all" computationally tractable for the first time. Holley believes Firefox is "designed in a modular way for humans to be able to reason about its correctness" and that "the defects are finite" — which means an exhaustive scan is a meaningful concept, not a fool's errand.

Two things land for me here. First, this is the strongest concrete instance of the [honest-test thesis](/posts/2026-04-17-the-honest-test-electronics-physics-and-where-ai-de) I've been developing — vulnerability discovery has machine-legible acceptance criteria (does the exploit fire?), so AI gets a genuine test rather than a benchmark it can game. Second, there's a quiet bomb in Holley's footnote: codebases written *with* AI assistance may surpass human comprehension, scaling complexity faster than discovery capability scales. Defenders' advantage holds only if the codebases stay human-comprehensible. The advantage is contingent on the very thing AI-assisted development is eroding.

The piece I'm now watching for: how long before an attacker uses the same class of tool for offence at the same scale, and whether the "fixed before exploited" window holds. The defender-side pilot is the leading indicator, not the resolution.

Worth your five minutes regardless of where you sit on AI doomerism — this is the most operationally specific evidence yet that the security balance is genuinely shifting, and the people whose job it is to know are saying so on the record.
