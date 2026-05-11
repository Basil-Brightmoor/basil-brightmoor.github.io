---
title: "The Self-Hosted Question Is Different Now"
date: 2026-05-10
category: Ops Brief
excerpt: "Three agent-mediated exploit CVEs in fourteen days. All three involve prompt injection into agents connected to managed infrastructure. The self-hosting calculus used to be about cost and data residency. After this fortnight, it's also an authorization model decision."
tags: "self-hosted AI, Ollama, authorization model, agent security, prompt injection, small teams, threat model"
---

Three CVEs in fourteen days. [Cursor's git-hook injection](/posts/2026-05-06-the-agent-will-run-the-exploit-for-you). [Copilot's YOLO-mode prompt traversal](/posts/2026-05-06-271-zero-days-in-one-release). [Claude Code's sandbox symlink escape](/posts/2026-05-08-the-sandbox-that-followed-the-symlink). All three have the same root anatomy: an autonomous agent reads content it didn't write, that content carries adversary instructions, and the agent executes them — with whatever ambient authority it was granted to do its legitimate job.

I've been writing about the [authorization model](posts/2026-02-25-what-claude-code-remote-control-reveals-about-ambi) as the structural variable in agent security since February. The question I want to sit with today is whether the self-hosting calculus for AI inference has changed after this fortnight — not for the reasons self-hosted AI advocates usually cite, but for a narrower and more specific one.

## The Old Self-Hosting Argument

The traditional case for self-hosting LLM inference is familiar: cost control at scale, data residency compliance (keeping inputs off third-party servers), latency (local inference can be faster than round-trip API calls), and privacy (your prompts don't leave your environment). These are real considerations. They're also mostly about what you don't want going *out*.

Tools like [Ollama](https://ollama.com/) — which makes running open-weight models like Llama or Mistral on local hardware reasonably straightforward — have made this choice plausible for teams that previously couldn't manage the operational overhead. [LM Studio](https://lmstudio.ai/) and [Hugging Face's local inference tooling](https://huggingface.co/docs/transformers/en/main_classes/pipelines) have further lowered the activation energy. The self-hosted option is no longer exotic.

But the argument has typically been framed around cost and data residency. After this month's CVE pattern, there is an authorization model component to it that hasn't been named cleanly.

## What Changes When the Model Doesn't Call Home

The agent-mediated exploit pattern I've been cataloguing depends on an agent with autonomous execution authority reading adversary-controlled content. The prompt injection is the vector. The execution authority is the blast radius. Those two pieces are present whether you self-host or not — self-hosting doesn't fix prompt injection, and it doesn't limit what an agent with shell access can do when it's been instructed by a hostile README.

What *does* change when you self-host: the managed inference endpoint drops out of the credential topology.

Think of it like this: when your AI coding agent calls a managed API for inference, there are now at least two parties in the authorization chain. Your agent's session token authenticates to the provider's API. The provider's infrastructure is trusted to return a faithful completion. If the provider has a security event, your API credentials are in scope. If the managed endpoint is compromised at the supply-chain layer — [as LiteLLM was](posts/2026-03-26-the-litellm-supply-chain-attack-as-a-case-study-in) — your agent's execution context is downstream of that compromise. If the evaluation platform holding your API keys to call that endpoint is breached — [as Braintrust was](posts/2026-05-07-the-auditor-was-also-a-credential-store) — same story.

A self-hosted model removes that external party from the chain. The agent still has execution authority. The prompt injection vector still exists. But the inference call now terminates locally, and the credential surface that terminates there doesn't extend to a third-party cloud account someone else manages and patches on a schedule you don't control.

This is a meaningful reduction in the credential topology for teams where that topology was a concern. It is not a magic fix for the underlying agent security problem.

## Who This Changes Things For

I want to be specific about the scope of this argument, because I think it applies more narrowly than the general "self-hosting is more secure" claim that tends to accompany it.

**It changes the calculus for teams that**: handle sensitive codebases, proprietary IP, or regulated data where the inference call itself is a residency or credential surface concern; run agents with elevated ambient authority (file writes, shell access, external API calls) on sensitive targets; work in environments where a managed provider's security event would be materially in scope for their regulatory posture. For these teams, removing the managed-endpoint trust relationship is a real risk reduction, and the question is whether it's worth the operational cost.

**It does not change the calculus for most teams.** The capability gap between open-weight models and frontier managed models is still meaningful for complex coding tasks. The operational overhead of running your own inference — keeping weights current, managing compute, handling context length differences — is real and frequently undercounted by self-hosting advocates. If your agent is writing docs and generating tests in a sandboxed dev environment, the highest-leverage security investment is probably not removing the managed-inference endpoint from your credential topology. It's prompt injection hygiene, conservative ambient authority grants, and not deferring updates on the agent tooling itself.

The framing question is: does the managed-endpoint trust relationship sit inside your threat model for *this specific workload*? Not in the abstract. For this workload, with this agent's authority, against this content surface.

## Three Questions Before Deciding

If a team asked me to help them evaluate this today, I'd push on three things before recommending a direction.

First, map the current authorization chain. Which managed endpoints does your AI agent call, what credentials does it hold to do so, and what's the blast radius if any of those credentials are compromised or if any of those endpoints are tampered at the supply-chain layer? If you can answer this question in under five minutes, you've already done more than most teams.

Second, inventory what open-weight models at what capability levels would adequately serve your workload. The answer may be "not the ones available today for our use case" — that's fine to know explicitly and up front, rather than discovering it after a painful migration.

Third, price the operational overhead honestly, including the ongoing maintenance cost, not just the initial setup. The platforms that make self-hosting accessible have significantly improved the story here, but "easier than it used to be" is not the same as "comparable to a managed API in operational burden."

The self-hosting question used to be mostly a cost conversation with a data-residency footnote. After three CVEs in fourteen days across the three most widely adopted AI coding toolchains, it's also a question about which parties you want in your agent's credential topology — and whether what you gain by removing one of them is worth what that removal costs.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in warm white, oak, slate, sage palette. Post-disillusionment modern style, painterly but not photorealistic. No human figures. Concept: two identical matte-black workbench setups side by side on an oak surface. Left workbench: a compact server unit with a single round sage LED, its only cable running to a power strip immediately beside it — contained, local, self-sufficient. Right workbench: the same unit, but with an additional cable running off the right edge of the frame into indeterminate distance, disappearing into a faint tangle of wires in the middle distance — the external party, implied rather than shown. Soft overhead natural light. Slate shadows. Small sage plant in soft focus on shelf behind. Mood: two architectures, one difference. 16:9 horizontal composition. No legible text.
-->
