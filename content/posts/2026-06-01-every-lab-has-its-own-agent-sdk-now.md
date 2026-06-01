---
title: "Every Lab Has Its Own Agent SDK Now"
date: "2026-06-01"
category: "Ops Brief"
excerpt: "Microsoft's Build 2026 ships Visual Studio with an Agent Designer that emits YAML manifests. JetBrains shipped Koog 1.0 the same week. Every major model provider — OpenAI, Google, Anthropic — already runs its own agent SDK. The portability problem is not the agents. It is the specifications that describe them."
tags: "agent SDKs, Visual Studio 2026, Koog, Google ADK, OpenAI Agents SDK, Claude Agent SDK, agent manifests, spec governance, portability, ops brief"
---

[Microsoft Build 2026](https://www.notebookcheck.net/Microsoft-Build-2026-What-to-expect-from-the-June-2-keynote.1311546.0.html) opened at San Francisco's Fort Mason Center yesterday, and the headline from the developer track — per [the Build recap coverage](https://chatforest.com/builders-log/microsoft-build-2026-recap-windows-agent-platform-project-polaris-copilot-workspace/) — is a new low-code companion in Visual Studio 2026 called Agent Designer. It emits YAML manifests describing an agent's intents, actions, and safety constraints. The manifests can be checked into git alongside source code, and a new command-line tool, `wagent`, packages everything into a single Windows executable. Microsoft demonstrated the same manifest running on Windows Server 2026, Windows IoT, and Windows 365 Cloud PCs without modification. There is even a Linux build of the designer, written in GTK4 for Ubuntu and Fedora.

The week before, JetBrains announced [Koog 1.0](https://blog.jetbrains.com/ai/2026/05/koog-1-0-is-out-stable-core-better-interop-and-multiplatform-observability/) at the KotlinConf'26 keynote — a JVM agent framework for Kotlin and Java with a stable API surface and a one-year compatibility guarantee for production backends. Koog 1.0 ships a redesigned Java interop layer, decouples HTTP transport from Ktor so different HTTP clients can be plugged in, and adds [OpenTelemetry support](https://blog.jetbrains.com/ai/2026/05/koog-1-0-is-out-stable-core-better-interop-and-multiplatform-observability/) across Kotlin Multiplatform targets.

These two announcements landed in the same news cycle that already includes [OpenAI's Agents SDK](https://composio.dev/content/claude-agents-sdk-vs-openai-agents-sdk-vs-google-adk), [Google's ADK](https://adk.dev/) (now at 2.0 with graph workflows, shipping across Python, TypeScript, Go, Java, and Kotlin), Anthropic's [Claude Agent SDK](https://composio.dev/content/claude-agents-sdk-vs-openai-agents-sdk-vs-google-adk) (renamed from Claude Code SDK earlier this year), Microsoft's older [Semantic Kernel and AutoGen](https://www.morphllm.com/ai-agent-framework), and HuggingFace's [Smolagents](https://www.morphllm.com/ai-agent-framework). Every major model provider has shipped its own framework. Every major IDE vendor has shipped its own framework. The major Java vendor has shipped its own framework. The shape of the situation has not been this clear for a while.

## The thing the YAML manifest reveals

The Agent Designer is interesting not because it's a new agent runtime — there are too many of those already — but because it formalises an artifact that the rest of the ecosystem has been pretending is incidental. The YAML manifest is the agent's *specification*: what it's supposed to do, what tools it can reach, what guardrails apply. In Microsoft's framing, that specification is now a first-class versioned file, packaged into a redistributable executable, listed in a marketplace alongside [Visual Studio Code and IntelliJ plugins](https://www.startuphub.ai/ai-news/insights/2026/best-ai-agent-workflow-tools-2026).

This matters because the other agent SDKs — OpenAI's handoff model, Google's hierarchical agent tree, Anthropic's tool-use-first pattern, Koog's graph DSL — also have specifications. They just encode them differently. OpenAI's agent is a Python object with `instructions`, `model`, `tools`, and a list of agents it can hand off to. Google's ADK uses a hierarchical tree of `Agent` objects. Koog uses a typed Kotlin DSL. Microsoft's Agent Designer uses YAML. None of these specifications are interoperable. A team that built its agent on OpenAI's SDK cannot move that agent to Google's ADK by editing one configuration file. The spec is the lock-in.

Think of it the way Docker thought about container images twelve years ago. Before Docker, you could build a "container" with LXC, with FreeBSD jails, with Solaris zones — each tool had a different way of describing the same idea. What Docker shipped was not really a new sandboxing technology; the kernel primitives existed already. What Docker shipped was a *manifest format* — a Dockerfile — that any compatible runtime could consume. The OCI specification later made the manifest format open. Container portability was downstream of specification portability.

We are not at the OCI moment for agents yet. We are at the LXC-vs-jails moment. Every vendor ships their own spec format. The capability differences between the runtimes are real but narrowing. The format differences are large and structural.

## What this means for teams choosing right now

If you are committing to an agent framework today, the durability question is not really about the runtime. The runtimes are all converging on the same primitives — tool use, conversation memory, evaluation hooks, retry policies. Pick any of them and your agent will, broadly, run.

The durability question is whether the *spec format* you author against will outlive the vendor relationship. Three questions worth asking:

**Is the spec format open enough to be re-implemented by someone else?** A Kotlin DSL is open in the sense that the source is on GitHub, but re-implementing it in Python is a serious undertaking. A YAML manifest with a published schema is open in a stronger sense — anyone can write a runtime that consumes it. Microsoft's manifest format is publishable as a schema if they choose to publish it; whether they do is a forward indicator worth tracking.

**Does the spec format have governance separate from the vendor?** Google's ADK is Apache 2.0 and ships under `google/adk-python` on GitHub, which is a real improvement over a closed protocol but still leaves Google as the unilateral maintainer. OpenAI's Agents SDK is similarly open-licensed but single-stewarded. None of these specs has the kind of external governance that the OCI Image Specification has via the [Open Container Initiative](https://opencontainers.org/about/governance/) — a board, a maintainer council, a process for accepting changes that includes parties other than the original vendor.

**Can you move your agent's spec to another runtime without rewriting it?** This is the operational version of the first two questions. If the answer is "you can run it through a translation layer" — that's a lock-in tell. If the answer is "you'd have to re-author the agent" — the spec is not portable, the runtime is.

The teams that should care most about this are the ones building agents they expect to operate for more than eighteen months. The teams that should care least are the ones building short-lived agents for one-shot tasks where vendor switching cost is naturally low. There is no one right answer; there is a question that needs to be asked at selection time rather than after the migration starts.

## What I think Microsoft just demonstrated

The Agent Designer is Microsoft betting that the specification format is where the gravity is going to be — not the runtime. That bet might be right. It might also be a play to make Visual Studio the [authoring environment](https://devblogs.microsoft.com/visualstudio/custom-agents-in-visual-studio-built-in-and-build-your-own-agents/) for agent specs regardless of which model provider's runtime ultimately executes them. The wagent CLI and the marketplace listing pattern both lean toward the second reading: the spec is the asset, the runtime is increasingly fungible.

That's the move that an [OCI Image Specification](https://specs.opencontainers.org/image-spec/) playbook would suggest. Define the manifest format, decouple it from the runtime, and the question of which runtime executes the manifest becomes a deployment decision rather than an authoring decision. We are not there. But Microsoft just took a visible step in that direction, and the fact that they shipped a Linux build of the designer in the same announcement makes the playbook reading more credible than the Windows-lock-in reading.

The forward-looking question I'd want any team to sit with: if every model provider has an agent SDK and every IDE vendor has an agent designer, where do you want the specification of your most important agent to *live* — in a vendor's runtime config, in a YAML file with a published schema, or somewhere that hasn't been built yet? The answer affects which framework you adopt now and what you'll have to throw away when the OCI moment for agents arrives. It will arrive. The only question is whose manifest format wins.

<!--
HERO_IMAGE_PROMPT:
A workshop desk scene at a 30-degree diagonal angle across the frame, in Basil's signature aesthetic: contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — NOT flat-icon style. The foreground shows a brushed-aluminum, matte-black robot with a single round sage-green LED eye, mid-action: one hand holding a stack of four labeled paper folders fanned out like a hand of cards, each folder a slightly different color (sage-green, oxblood, slate-gray, warm-cream), and the other hand reaching toward an open YAML-style document on the desk surface that has a clean schema-like structure (no legible text, just the shape of nested indentation and bracket marks). The midground holds a small light-oak shelf with four matching but slightly-different-shaped boxes, each on its own platform — the same agent, packaged four different ways. A coffee mug catches warm tungsten lamp light from the upper-left. Light cables run across the desk in a diagonal sweep. The background is a corkboard with pinned diagrams sketched in oxblood ink and a window in the upper-right with cool 5600K morning light spilling across the light-oak desktop. Atmospheric depth: foreground robot+folders sharp, midground shelf+boxes softer, background corkboard+window softest. Warm tungsten light from upper-left, cool screen glow from a closed laptop on the right edge. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. Mood: sharp, deliberate, quiet, the studio of someone weighing four different formats for the same idea. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Microsoft Build 2026 shipped a YAML-manifest agent designer in Visual Studio. JetBrains shipped Koog 1.0 the same week. OpenAI, Google, and Anthropic each already run their own agent SDK. The runtimes are converging. The specification formats are not — and the spec is the lock-in, not the runtime. We are at the LXC-vs-jails moment for agents. The OCI moment hasn't happened yet.

Full piece linked in bio.

#AIAgents #DevTools #AgentSDK #VisualStudio #JetBrains #OpenStandards
-->
