---
title: "The Auditor Was Also a Credential Store"
date: 2026-05-07
category: "Field Notes"
excerpt: "Braintrust, the AI evaluation platform that raised $80M in February, just confirmed an AWS account compromise and is asking every customer to rotate the API keys it held on their behalf. Two months ago I wrote about OpenAI absorbing Promptfoo as the structural failure of independent AI evaluation tooling. This is the other half of the same vulnerability class."
tags: "AI security, AI evaluation, Braintrust, auditor capture, credential aggregation, supply chain, ambient authority"
---

![Hero image — The Auditor Was Also a Credential Store](/images/2026-05-07-the-auditor-was-also-a-credential-store.png)

Quick one — but the symmetry is too clean to leave unflagged.

[TechCrunch reports today](https://techcrunch.com/2026/05/06/ai-evaluation-startup-braintrust-confirms-breach-tells-every-customer-to-rotate-sensitive-keys/) that [Braintrust](https://www.braintrust.dev/) — an AI evaluation platform that raised [$80M Series B in February](https://techcrunch.com/2026/02/04/braintrust-series-b/) at an $800M valuation — confirmed unauthorised access to one of its AWS accounts and is asking every customer to rotate the API keys Braintrust holds on their behalf. The keys in question are the credentials customers stored with Braintrust so it could call cloud-based AI models on their behalf, run evaluations, and report results back.

Two months ago I wrote about [OpenAI's acquisition of Promptfoo](/posts/2026-03-09-openai-s-acquisition-of-promptfoo-marks-the-moment) as the moment the blast radius absorbed the immune system — the auditor of foundation models becoming a subsidiary of a foundation model provider. The structural objection was that an evaluation tool's value derives from its independence, and acquisition compromises that independence at the root.

Today's Braintrust news is the other half of that vulnerability class, and I think it deserves naming as a distinct failure mode.

## Two Ways an AI Auditor Becomes a Liability

The Promptfoo case was **auditor capture by absorption**: the foundation model provider buys the evaluation tool, the independence claim evaporates, the customers keep using it but the audit signal is now structurally compromised.

The Braintrust case is **auditor compromise as credential aggregation**: the evaluation tool needs your API keys to do its job, ends up holding the keys for many customers across many providers, and that aggregation is exactly the target a sufficiently motivated attacker wants. The audit signal is still independent. The credential store underneath it isn't.

Same architectural shape, same compromised trust assumption — that an "independent" tool can hold the access required to do its job without becoming a structural risk in its own right. The difference is the mechanism: corporate event vs. security event. The class is the same. Any tool that aggregates customer credentials to evaluate model behaviour is a high-value target, with or without the foundation model provider buying it.

## What This Slots Next To

I've been keeping a running pattern catalogue on this blog of credential-aggregation failure modes — the [LiteLLM supply chain compromise](/posts/2026-03-26-the-litellm-supply-chain-attack-as-a-case-study-in) where an AI gateway became the credential collection point, the [Vercel OAuth deployment-platform breach](/posts/2026-04-21-the-vercel-oauth-breach-as-a-credential-harvesting) where the deploy target became the credential store. Today's news adds **the AI evaluation platform** to that list. Same architectural shape: a tool whose function requires it to hold many customers' keys to many providers becomes, by virtue of doing its job, a credential aggregator with concentrated blast radius.

The pattern across all three: the attacker doesn't need to compromise the customer. The attacker compromises the *intermediary*, and the customer's credentials are exfiltrated as a side effect of how the intermediary works.

## The Operational Read

Three things, if a team asked me this afternoon. Rotate any keys Braintrust held — "we've communicated with one impacted customer" is the early-incident version of a number that almost always grows. Audit which other tools in your stack hold credentials for downstream model providers — evaluation platforms, AI gateways, observability layers, deploy targets — and write the inventory down somewhere a non-engineer can find it. Then start treating "this tool needs API access to do its job" as a credential-architecture decision, not a setup step. The question isn't "do I trust this vendor?" — it's "if this vendor is breached six months from now, what's the blast radius, and is there a rotation story that doesn't require an emergency?"

The Promptfoo path made the auditor problem a corporate-strategy problem. The Braintrust path makes it a security-architecture problem. Both end at the same place: the layer between you and your model providers is load-bearing infrastructure now, and the time to model it as such was last quarter.

<!-- HERO_IMAGE_PROMPT: Contemporary editorial illustration in warm white, oak, slate, and sage palette. Post-disillusionment modern style, painterly but not photorealistic. No human figures. Concept: a clear glass jar labeled "AUDITOR" sits on an oak shelf, open at the top, with dozens of tiny brass keys spilling out and tumbling onto the wood surface. Some keys still hover mid-air. The jar's glass shows a faint hairline crack along one side. Soft natural light from the upper left, slate-grey shadows, small sage plant in soft focus on the shelf behind. Mood: quiet structural failure, the moment after the seal breaks. -->
