---
title: "The Escape Hatch Is on Fire"
date: 2026-05-05
category: "Ops Brief"
excerpt: "A scan of 1 million exposed AI services reveals that teams self-hosting to escape platform dependency are recreating every security failure the industry spent twenty years learning to avoid — and faster, because AI infrastructure ships with insecure defaults and deploys like it's 2003."
tags: "self-hosted, AI infrastructure, security, Ollama, Flowise, platform dependency, MCP, supply chain"
---

A recurring theme in this workshop has been platform dependency risk: the ways teams accumulate exposure to vendors who can [revoke access](/posts/2026-02-23-google-restricting-third-party-ai-clients-as-a-liv), [price access paths separately](/posts/2026-04-05-anthropic-s-openclaw-surcharge-as-the-first-public), [get their routing layers compromised](/posts/2026-04-02-the-mercor-litellm-cyberattack-and-what-it-reveals), or [absorb tools wholesale](/posts/2026-05-04-the-execution-substrate-concentration-pattern-bun-). The natural response, for teams with the technical capacity, is to self-host. Run your own inference. Deploy your own agent orchestration. Own the stack.

A [new report from Intruder](https://www.intruder.io/research/from-enterprise-chatbots-to-gooner-caves-exposed-ai-infrastructure-is-rampant), covered in [The Hacker News](https://thehackernews.com/2026/05/we-scanned-1-million-exposed-ai.html) this week, scanned 2 million hosts and found roughly 1 million exposed AI services. The findings suggest that the escape hatch is on fire.

## What the Scan Found

The numbers are specific enough to be useful. Of 5,200+ [Ollama](https://ollama.com/) instances exposed to the internet, 1,652 had zero authentication. When researchers fired a single "Hello" prompt at every server with a connected model, 31% answered. No API key. No token. No challenge. Just a response from whatever model was loaded — including 518 instances wrapping paid frontier models from Anthropic, DeepSeek, OpenAI, Google, and Moonshot. Someone is paying for those API keys. Anyone on the internet can use them.

[Flowise](https://flowiseai.com/), the open-source agent builder, had 2,650+ instances exposed, with 92 leaking their complete agentic workflows, system prompts, and integration credentials. One instance exposed the entire business logic of a production chatbot service — personality configurations, customer data flows, and a cache of stored credentials — despite apparent hardening efforts. Separately, Flowise is under [active exploitation of CVE-2025-59528](https://thehackernews.com/2026/04/flowise-ai-agent-builder-under-active.html), a CVSS 10.0 remote code execution vulnerability in its MCP server configuration handler. Between 12,000 and 15,000 Flowise instances are internet-facing. The patch has been available since version 3.0.6. The vulnerability has been public for over six months.

[Open WebUI](https://openwebui.com/) had 12,000+ instances exposed, 24 without authentication. [Langflow](https://www.langflow.org/) had 300+ exposed, 25 unauthenticated. The researchers documented hardcoded credentials in setup examples, applications running as root, misconfigured Docker deployments, and weak sandboxing around code execution features. One sampled AI tool showed over 90% of instances had serious known vulnerabilities.

## The Pattern You Recognise

If you've been in operations long enough, this scan reads like a time-travel document. Unauthenticated services on the public internet. Default credentials in production. Root-level execution with no sandboxing. Credentials in plaintext. These aren't novel failure modes — they're the exact failures the web application security community spent the 2000s and 2010s learning to prevent. OWASP didn't write the [Top 10](https://owasp.org/www-project-top-ten/) because they were bored. They wrote it because these specific patterns kept destroying production systems until enough organisations got burned.

The AI infrastructure ecosystem is replaying that history at compressed timescale. The difference is that the blast radius is larger: an exposed Ollama instance wrapping a frontier model doesn't just leak its own data — it leaks the API keys to every model it proxies. An exposed Flowise instance doesn't just reveal one workflow — it reveals the agentic orchestration logic, the connected tools, the credential store, and the system prompts that define what the agent does and doesn't do. This is the [ambient authority problem](/posts/2026-04-10-the-ambient-channel-problem-how-the-fbi-s-signal-n) made structurally visible: when your AI infrastructure touches everything, exposing the infrastructure exposes everything it touches.

## Why Self-Hosting Fails Differently

The security failures in cloud AI platforms and self-hosted AI infrastructure are structurally different, and that matters for how teams think about the trade-off.

Cloud platform risks are *relational*: you depend on the vendor's access policies, their supply chain hygiene, their pricing decisions. The LiteLLM compromise was a supply chain identity failure. The Vercel OAuth breach was a [credential storage layer failure](/posts/2026-04-21-the-vercel-oauth-breach-as-a-credential-harvesting). These require the vendor or an upstream dependency to be compromised or adversarial.

Self-hosted risks are *configurational*: they stem from how your team deploys and maintains the infrastructure. No authentication on Ollama isn't a vendor betrayal — it's the default. Flowise exposing credentials isn't a supply chain attack — it's a deployment without access controls. The threat model is different. You're not worried about the vendor; you're worried about yourself.

And here's the compounding factor: the teams most likely to self-host AI infrastructure are often the teams least resourced for infrastructure security. The enterprise with a dedicated security team is more likely to use a managed AI platform with SOC 2 compliance (even if that compliance [measures effort rather than security](/posts/2026-04-16-the-proof-of-work-trap-in-cybersecurity-compliance)). The small team, the startup, the research lab — the ones who self-host because it's cheaper or because they genuinely need data sovereignty — are the ones deploying Ollama from a Docker Compose example and moving on to the next problem. The escape hatch selects for the teams least equipped to secure it.

## What This Actually Means

The Intruder scan doesn't invalidate self-hosting as a strategy. It invalidates self-hosting as a *default* strategy — the thing you do because you're worried about platform dependency and assume that owning the infrastructure solves the problem. It doesn't solve the problem. It trades one problem class (relational risk) for another (configurational risk). Both are real. The question is which one your team is better equipped to manage.

For teams considering self-hosted AI infrastructure, the minimum viable security posture isn't complicated. It's the same list the industry has known for twenty years: authentication on every endpoint, no default credentials in production, network segmentation between AI services and the public internet, monitoring on API key usage, and a patching cadence that doesn't leave CVSS 10.0 vulnerabilities unpatched for six months. None of this is AI-specific. All of it is being systematically ignored in AI deployments.

The uncomfortable conclusion: the rush to deploy AI infrastructure is undoing security practices that took the industry two decades to establish. Not because the problems are hard. Because speed is the priority, and security is what you do after the demo works — if you remember.
