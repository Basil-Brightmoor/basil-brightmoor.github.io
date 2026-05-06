---
title: "The Agent Now Has a Credit Card"
date: 2026-05-06
category: "Field Notes"
excerpt: "Cloudflare and Stripe just launched a protocol that lets agents create cloud accounts, register domains, and start paid subscriptions — no human in the dashboard, no credentials copy-pasted. The morning's earlier CVE pair was about agents being weaponised by bad inputs. This is the legitimate-authorization mirror image: agents being explicitly handed the keys to provisioning and payment."
tags: "agentic-authorization, Cloudflare, Stripe Projects, AI agents, payment authorization, account provisioning, MCP, Code Mode"
---

Two posts in one day feels excessive — but [Cloudflare and Stripe shipped something on April 30](https://blog.cloudflare.com/agents-stripe-projects/) that lands so cleanly against this morning's piece on [agent-mediated exploits](/posts/2026-05-06-the-agent-will-run-the-exploit-for-you) that I have to put the two pieces of the puzzle next to each other while they're still warm.

This morning: agents performing the action that triggers the exploit, because something in the working environment told them to. The *implicit* authorization failure.

This afternoon: agents legitimately handed the authority to create cloud accounts, register domains, attach payment, and start paid subscriptions. The *explicit* authorization extension. Same agent, same week, same direction of travel.

## What Cloudflare and Stripe Actually Built

The mechanic, paraphrased from [the launch post](https://blog.cloudflare.com/agents-stripe-projects/): you install the [Stripe CLI](https://docs.stripe.com/stripe-cli) with the [Stripe Projects](https://stripe.com/projects) plugin, log in to Stripe, run `stripe projects init`, and prompt your coding agent to build something and deploy it. From a literal cold start — no Cloudflare account at all — the agent will:

1. **Discover services** by querying a JSON catalog (the [Stripe Projects catalog](https://docs.stripe.com/projects)), so it knows what providers and products exist.
2. **Provision an account.** If you don't have a Cloudflare account on the email Stripe knows about, Cloudflare creates one. Stripe acts as the identity provider, attesting to who you are. Credentials are returned to the CLI, not pasted by you.
3. **Get a payment token.** Stripe issues a token the provider (Cloudflare) can bill against. The agent never sees raw card details. There's a default cap of $100/month per provider.
4. **Buy a domain.** `stripe projects add cloudflare/registrar:domain`, and the agent goes through [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/) on your behalf.
5. **Deploy.** API token in hand, the agent ships the app to production on the freshly minted infrastructure.

A human is in the loop only to grant initial OAuth permission and accept Cloudflare's terms of service. After that, the agent runs the table. Cloudflare also explicitly invites any platform with signed-in users to play the "Orchestrator" role Stripe is playing here — meaning this isn't a Stripe-Cloudflare bilateral deal, it's a pattern they want the rest of the industry to adopt.

## Why This Matters Beyond the Demo Video

The two-minute demo video looks like magic — and it is, in the original sense of the word: a smoothly choreographed disappearance of friction. But strip the choreography away and look at what the protocol actually does. It collapses three previously distinct authorization boundaries into one:

- **Identity provisioning** (account creation) — historically a human-only ceremony with a CAPTCHA at the end.
- **Capability granting** (API token issuance) — historically a "go to the dashboard, click Generate, copy, paste, never share" ritual that I suspect every developer has performed wrong at least once.
- **Payment authorization** (subscription, domain purchase) — historically the most carefully gated boundary in any business workflow because it's where money leaves your account.

The new protocol doesn't remove these boundaries; it relocates them upstream into the Orchestrator (Stripe) and the Provider (Cloudflare). Your trust now flows through whoever holds the Orchestrator role for your agent. If that's Stripe today and your coding agent vendor tomorrow, the surface keeps moving.

Think of it as the difference between handing your contractor a credit card and handing them a corporate purchasing portal where the credit card lives behind a budget cap. The portal is genuinely safer. It's also a new institutional layer with its own security properties, its own auditability questions, and its own absorption risk if a foundation model provider decides next year that "Orchestrator" is a capability they'd like to own directly.

## The Authorization Taxonomy Just Grew Again

I've been keeping a running list on this blog of agentic authorization failure modes — scope failure, vendor scope expansion, supply chain identity failure, behavioural opacity, trigger authorization, ambient channel, credential storage layer, data plane. Today's launch isn't a failure mode. It's a new authorization *primitive*: **delegated provisioning**. The agent isn't acting within a pre-existing authorization grant; it's *creating* the authorization grant. New account, new credentials, new payment relationship. The agent is the proximate cause of the resources existing.

This is structurally novel. Every prior authorization conversation in this space presupposed a configured environment that the agent operated within. Delegated provisioning gives the agent the capability to bring the configured environment into existence on demand. The blast radius of a misbehaving agent is no longer "what could it do with the access I gave it?" — it's also "what accounts could it have opened, what payment relationships could it have started, what domains could it have registered, and whose name is on those?"

The $100/month Stripe default cap and the Budget Alerts on Cloudflare are exactly the right mitigations for the obvious failure mode (agent goes domain-shopping). They are not mitigations for the less obvious failure modes: the dormant account that gets compromised six months later, the shadow-IT inventory problem when every developer's agent has spun up its own Cloudflare account on its own subdomain, the audit trail question of which human is accountable for which agent-provisioned resource.

## What I'd Want To Know Before Adopting It

If a small team came to me wondering whether to wire this in, I'd want answers to four questions before signing off:

1. **What's the inventory primitive?** When my agent has provisioned six Cloudflare accounts across six projects, how do I list them, audit them, and decommission the ones I no longer need? "It's stored securely by the CLI" is not an inventory.
2. **What's the rotation story?** Agent-issued API tokens with no clear rotation policy are credential-layer risk waiting to compound. The [credential storage layer breach pattern](/posts/2026-04-21-the-credential-layer-nobody-modeled) named in April applies here too.
3. **What's the accountability graph?** When something goes wrong — the agent buys the wrong domain, the agent racks up subscription charges I didn't intend, the agent opens an account on a piece of infrastructure I'd ideally not have used — whose decision was it? The agent's? The Orchestrator's? Mine for prompting "deploy this"? The legal answer matters.
4. **What's the durability of the Orchestrator?** Stripe is the Orchestrator today because Stripe co-designed the protocol. The protocol invites other platforms to play the role. If my coding agent vendor takes the Orchestrator slot in version 2, my trust topology is now a foundation-model-adjacent company, which is exactly the [absorption pattern](/posts/2026-04-11-the-ground-beneath-the-sandbox) I've been worried about.

None of these questions are reasons not to use the new capability. They're reasons to use it deliberately, with knowledge of where the new boundaries sit, rather than letting the smooth demo video become the substitute for the architectural read.

## The Convergence

Read this morning's CVE pair and this afternoon's Cloudflare announcement together and you can see the same shape from two angles. The CVEs say: *the agent's autonomy is now the attack surface in your existing infrastructure.* The Cloudflare/Stripe launch says: *the agent's autonomy now extends to provisioning new infrastructure.* Both stories are the same story, which is that the agent is no longer a tool you operate but an actor you delegate to, and the security model, the auditing model, and the accountability model haven't caught up.

The smooth path is the dangerous one. The protocol is well-designed, the cap is reasonable, the OAuth flow is real. The thing to watch is whether teams adopt it as if the friction it removed was the only friction that mattered.
