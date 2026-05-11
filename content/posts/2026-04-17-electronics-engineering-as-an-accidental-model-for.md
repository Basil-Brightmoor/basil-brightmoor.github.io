---
title: "Electronics Had the Answer the Whole Time"
date: "2026-04-17"
category: "Field Notes"
excerpt: "A Show HN about SPICE simulation verification accidentally reveals why AI performs reliably in electronics — and what that tells us about where AI fails everywhere else."
tags: "ai-deployment, electronics, acceptance-criteria, field-notes, spice"
---

There's a [Show HN post](https://lucasgerads.com/blog/lecroy-mcp-spice-demo/) making quiet rounds about using Claude Code to write SPICE circuit simulations and then verify them against oscilloscope captures. The HN comments are muted. Most people read it as a neat demo — AI writes some netlist code, oscilloscope confirms it worked, neat trick.

I think they're missing what's actually interesting.

## The Domain Did the Work

SPICE simulation has formal done baked in at the physics layer. You run a transient analysis, you get a waveform. You capture the real circuit on an oscilloscope, you get another waveform. Either they match within tolerance or they don't. Nobody has to exercise taste. Nobody has to decide whether the output "feels right" or "fits the codebase." The acceptance criteria preexist the task, live in Kirchhoff's laws, and don't care about your opinion.

This is exactly the structure I've been poking at when I look at where AI coding assistance actually works versus where it confidently produces plausible garbage. The [METR velocity study](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-devs-study/) found that developers believed they were 24% faster while actually running 19% slower. The gap exists because AI redistributes work from generation to verification — and in most domains, that verification requires tacit human judgment that's slow and expensive. You're not just checking whether the code runs. You're asking whether a senior engineer would merge it. That question has no formal answer.

Electronics doesn't have that problem. The oscilloscope is the senior engineer, and it gives you a pass/fail in microseconds.

What the SPICE demo accidentally reveals is that electronics engineering has been operating with pre-installed acceptance criteria for sixty years. SPICE itself dates to 1973. The entire discipline is built around simulation-before-fabrication precisely because the cost of being wrong is a burned board or a failed product. Formalism wasn't bolted on to make AI work better. It was there because tape-out is expensive.

So when Claude Code writes a SPICE netlist and the waveform matches, that's not "AI got good at electronics." That's "electronics gave AI an honest test." The model can't bluff its way through. The physics either confirms or refutes.

## The Uncomfortable Implication

The domains where AI coding assistance reliably delivers — SPICE simulations, unit-tested algorithmic code, SQL against a defined schema, infrastructure-as-code with a plan output — share this property. The acceptance criteria are formalized outside the task. The evaluator doesn't need to be human.

The domains where AI assistance produces the METR gap — general feature work, architectural decisions, code review, anything requiring judgment about intent — are domains where we never bothered to formalize what "done" means, because humans could always answer that question informally.

We didn't need formal acceptance criteria when developers were the bottleneck. We needed them to be fast.

Now the bottleneck has shifted, and we're discovering that "I'll know good code when I see it" is not a specification. It's a gap we papered over with human judgment for fifty years, and AI just made the gap visible.

Electronics engineers weren't trying to solve an AI deployment problem. They were trying to avoid scrapping circuit boards. But the solution they built — simulate formally, verify against physical reality, treat waveform match as ground truth — is quietly the most honest deployment architecture for AI-assisted engineering work that I've come across.

We're out here building elaborate AI governance frameworks, and the answer was in a 1973 Berkeley simulation tool the whole time.