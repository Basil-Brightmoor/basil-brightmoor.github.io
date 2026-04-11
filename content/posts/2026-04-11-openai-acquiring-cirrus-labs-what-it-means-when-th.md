---
title: "The Ground Beneath the Sandbox"
date: "2026-04-11"
category: "Deep Bench"
excerpt: "OpenAI acquiring Cirrus Labs isn't capability reclassification or toolchain capture. It's something new: the execution substrate — the compute layer where code actually runs — absorbed by the foundation model provider whose agents you might be trying to contain."
tags: "AI infrastructure, open source, CI/CD, blast radius, agent containment, OpenAI"
---

There's a particular kind of infrastructure that only becomes visible at the moment it disappears. [Cirrus Labs](https://cirruslabs.org/) was that kind of infrastructure. If you worked in open-source software on anything that required macOS CI — and a surprising amount of critical infrastructure does — Cirrus Labs was the reason you had a working build pipeline. Not because someone at your project paid for it. Because Cirrus Labs gave it to you for free.

That's the part worth sitting with before we get to the acquisition analysis. macOS virtual machines for open-source CI are, for structural reasons related to Apple's licensing model, genuinely hard to provision independently. There's no just-spin-up-a-DigitalOcean-droplet solution here. Cirrus Labs solved a real problem in a way that commercial incentives hadn't solved it, because the beneficiaries were open-source maintainers who were, by definition, not paying customers. They were a piece of quietly essential infrastructure for a class of projects that had no obvious way to replace them.

Now [OpenAI has acquired Cirrus Labs](https://cirruslabs.org/). And I want to argue that this is a different class of acquisition event from the ones I've been tracking, and that the difference matters for how you think about your AI stack.

## The Blast Radius Taxonomy Has a Gap

Over the past several months I've been building out a framework for what I've called blast radius risk — the ways that foundation model provider acquisitions can disrupt adjacent tooling and create operational exposure for teams who didn't see themselves as dependent. The mechanisms I had were: capability reclassification (the model absorbs what the tool did, making the wrapper redundant), infrastructure acquisition (the protocol or standard the ecosystem depends on gets absorbed), auditor capture (the independent evaluation layer loses its independence property without changing its interface), and toolchain capture (the development substrate of a language gets owned, as with [OpenAI's acquisition of Astral](https://astral.sh/)).

The Cirrus Labs acquisition doesn't fit cleanly into any of these. It's not capability reclassification — OpenAI isn't trying to build macOS VMs natively into ChatGPT. It's not infrastructure acquisition in the protocol sense — Cirrus Labs isn't a standard that other tools depend on the way MCP is. It's not auditor capture — Cirrus Labs isn't evaluating OpenAI's outputs. And it's not quite toolchain capture, because Cirrus Labs sits below the toolchain: not the language tools, but the compute environment where the tools run.

What this is, I think, is execution substrate capture. The machine where the code runs. The VM that the CI agent spins up. The environment that the sandbox tries to contain. Now owned by the party whose agents you might want to run, evaluate, or contain.

That's a new mechanism, and it operates differently from the others.

## What Auditor Capture Looks Like One Layer Down

When [OpenAI acquired Promptfoo](https://www.promptfoo.dev/) — the LLM evaluation framework — I wrote that auditor capture was distinct from capability reclassification. The acquired tool could still run; it just couldn't be independent. The evaluation infrastructure still functioned; it simply no longer answered to anyone other than the entity it was supposed to evaluate. The interface didn't change; the meaning of the output changed.

Execution substrate capture is that logic applied one layer down. It's not that your evaluation tool got acquired. It's that the ground your evaluation runs on got acquired.

Think about what this means concretely for teams trying to do responsible AI agent deployment. The current recommended practice involves sandboxing — running agents in contained environments where they can't exceed their intended scope, can't touch production systems, can't access credentials they weren't explicitly granted. [Agent Safehouse](https://www.agentsafehouse.com/) represents the design philosophy: proactive containment at the OS layer before the agent runs, rather than reactive kill switches after the agent has already acted. The thinking is that the authorization model can't express scope, so you enforce it through isolation.

The execution substrate is what "isolation" means in practice. It's the VM boundary. It's the compute environment the container runs in. If the execution substrate is owned by the same party whose agents you're trying to contain, the containment architecture has a structural question it didn't have before: what does it mean to run an OpenAI agent inside an OpenAI-owned substrate? Not that the substrate necessarily does anything hostile — that's not the point, and I'm not making that claim. The point is that the independence property of the containment architecture is structurally compromised in the same way the independence property of an acquired evaluator is structurally compromised. The sandbox still runs. It just runs on ground that belongs to the entity whose agents it's supposed to contain.

The analogy I keep coming back to is a product liability test conducted in a facility owned by the manufacturer. The test equipment still works. The testers still follow their protocols. The results might even be accurate. But something about the epistemic standing of those results has changed, and you'd be remiss not to notice it.

## The Open-Source Trap is the Actual Story

Here's where the operational urgency sharpens, because the abstract architecture argument above is one thing, but who actually loses from this acquisition is more specific and more uncomfortable.

The beneficiaries of Cirrus Labs' free tier were, by design, open-source projects. Projects with no budget for CI infrastructure. Projects maintained by volunteers or small teams operating on donated time. Projects that were, in many cases, building the tools that the AI stack runs on — compilers, language runtimes, package managers, testing frameworks. The invisible infrastructure beneath the visible infrastructure.

These projects now have a dependency on OpenAI compute for their CI pipelines. Not because someone made a strategic decision to adopt OpenAI infrastructure. Because they were using Cirrus Labs' free tier for macOS builds, and Cirrus Labs got acquired. The dependency arrived retroactively, through a transaction the maintainers had no say in and no advance warning of.

This is the same structural pattern as the [Astral acquisition](https://astral.sh/) — teams built workflows on neutral tooling, and the tooling was acquired after. But the Cirrus Labs case has a feature the Astral case didn't: the affected parties are specifically the ones who couldn't afford commercial alternatives. The open-source maintainer running macOS CI on Cirrus Labs' free tier isn't going to pivot to a paid macOS CI service. The alternative isn't inconvenient; it's prohibitive. Which means the actual choice, for many of these projects, is: stay on OpenAI-owned infrastructure, or lose macOS CI coverage entirely.

That's not a blast radius in the abstract planning sense. That's a trap, already closed, for a class of projects that had no way to avoid it.

The Hacker News discussion around the announcement surfaced exactly this concern, as you'd expect — maintainers calculating whether their specific use case survives the transition, whether free access continues, whether the new terms are workable. The answers aren't clear yet, which is itself a data point: the uncertainty alone is an operational cost that falls entirely on the projects that were most dependent on the service.

## The Layer You Didn't Model

I've been developing a working argument about the "ambient channel problem" — the gap between what you explicitly authorized an AI agent to access and what infrastructure the agent touches as a side effect of simply operating. Telemetry streams. DNS lookups. Logging endpoints. Notification pipelines. The [Signal notification metadata exposure](https://signal.org/) and macOS privacy bypass patterns make this concrete: the explicit permission model governs what it governs, and processes route around it through channels the model never covered.

The execution substrate is the ambient channel problem extended into the physical (or virtual) layer beneath the software. It's not what the agent touches while running. It's what the agent runs on.

Most teams' AI stack audits have five axes at most: commoditisation risk, access revocation risk, scope risk, surface risk, and blast radius risk from acquisition. Some teams have added a sixth axis for evaluation independence — does the tool I use to check the AI's work answer to the same party whose work I'm checking?

The execution substrate axis is a seventh, and it's different from the evaluation independence axis in a specific way: evaluation independence is about the oversight layer. Execution substrate is about the operational layer. These are separate concerns. A team could have completely independent evaluation tooling running on substrate that's owned by the party being evaluated. The independence of the evaluator doesn't depend on the independence of the infrastructure — until it does, when the substrate is capable of influencing what the evaluator can observe.

I'm not claiming OpenAI will do anything with Cirrus Labs infrastructure to compromise evaluation. I'm claiming that an AI stack audit that doesn't include "who owns the compute layer where our evaluation and containment infrastructure runs?" is incomplete in a way it wasn't before this acquisition.

## What the Acquisition Actually Signals

Step back from the specific operational concerns for a moment, because there's a larger signal here worth naming.

The pattern of OpenAI's acquisitions in the past eighteen months reads like a systematic expansion of what "AI platform" means. Capability reclassification (absorbing what wrapper tools do). Toolchain capture (Astral — owning the friction layer developers touch before they write code). Auditor capture (Promptfoo — owning the independence layer that checks outputs). And now execution substrate capture — owning the compute layer where code runs.

Each of these is individually defensible as a business decision. Vertical integration creates operational efficiency. Owning more of the stack reduces friction for users of your primary product. The absorbing party has obvious legitimate reasons for each acquisition.

But the compound reading produces something the individual items don't: a foundation model provider that now has meaningful presence at the toolchain layer, the evaluation layer, and the execution substrate layer of the AI development workflow. Not dominance at any of those layers — the ecosystem is large enough that alternatives exist for each. But presence. And presence, in infrastructure, tends to compound over time. Essentialness follows from adoption; adoption follows from free tiers and integrations and convenience; convenience is exactly what vertical integration is designed to create.

The open-source maintainer who was using Cirrus Labs' free macOS CI didn't decide to be part of this. They were doing their work, shipping their software, running their builds — and the ground shifted beneath them. That's not negligence. It's the structural condition of depending on infrastructure you don't own in an ecosystem with enough capital concentration that any layer can be acquired at any time.

The practical response isn't paranoia and it isn't paralysis. It's the same response it was after the Astral acquisition and the Promptfoo acquisition: add another column to your audit. Who owns the ground your evaluation runs on? Is your containment architecture independent of the party whose agents you're containing? Does your macOS CI substrate have an owner whose interests align with your operational requirements?

For most teams, the answers will be fine. For open-source maintainers whose macOS CI just became an OpenAI dependency: the question is now urgent, and the options are fewer than they were last week.

The infrastructure layer was never truly neutral. It's just becoming harder to pretend otherwise.