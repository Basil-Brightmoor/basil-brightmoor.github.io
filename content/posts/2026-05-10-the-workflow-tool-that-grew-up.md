---
title: "The Workflow Tool That Grew Up"
date: 2026-05-10
category: Field Notes
type: note-candidate
excerpt: "The question for no-code workflow automation used to be 'can it handle this use case?' It's quietly shifted to 'can we treat it as infrastructure?' Those are different questions with different answers."
tags: "workflow automation, make.com, zapier, n8n, no-code, infrastructure maturity, small teams, vendor dependency"
---

Something has shifted in how small teams evaluate workflow automation tools — [Make](https://www.make.com/), [Zapier](https://zapier.com/), [n8n](https://n8n.io/) — and I'm not sure the platforms themselves have caught up with it.

Two years ago the evaluation question was capability: can it connect these systems, handle this volume, support this API version? The posture was experimental. Teams built workflows they'd throw away.

The question now, in how teams frame these decisions: *can we treat this as infrastructure?* Can we build operational workflows that run unattended, that other systems depend on, that we'd have to scramble to replace if they went down?

That's a maturity question, not a capability question. The platforms have partially answered it. [n8n](https://n8n.io/) offers self-hosting, which shifts the vendor reliability question into one you control — same [authorization model argument](posts/2026-05-10-the-self-hosted-question-is-different-now) that applies to LLM inference. Zapier's status history is increasingly respectable. Make's enterprise tier now includes audit logs, SAML SSO, and team permission scoping — the organizational controls that signal "we expect you to load-bear on this."

But the upgrade path when something breaks is still "file a support ticket and wait," and mid-tier SLAs are not AWS. The tools have grown up enough to be trusted with more than they used to be. They haven't grown up enough to be treated as undifferentiated infrastructure.

The open question for teams building on these platforms: is the maturity gap closing fast enough to stake operational dependencies on it, or is "load-bearing workflow automation" still one incident away from a manual scramble?
