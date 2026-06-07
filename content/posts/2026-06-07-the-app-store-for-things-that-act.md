---
title: "The App Store for Things That Act"
date: 2026-06-07
category: Ops Brief
excerpt: "2026 is the year the agent marketplace arrived — Windows Agent Store, Salesforce AgentExchange, a dozen others. The distribution model is borrowed from app stores. The thing being distributed is not an app. That gap is the whole story."
tags: ["AI agents", "agent marketplace", "tooling", "authorization", "small teams", "Microsoft", "Salesforce"]
---

![](/images/2026-06-07-the-app-store-for-things-that-act-hero.png)

There's a moment in every platform shift where the new thing borrows the old thing's packaging because nobody has invented better packaging yet. Early websites looked like brochures. Early mobile apps looked like miniature desktop software. And right now, in June 2026, the AI agent is being sold to us inside the most familiar wrapper the industry has — the app store.

[Microsoft unveiled the Windows Agent Store at Build 2026](https://fourweekmba.com/ai-microsoft-windows-agent-store-framework-build-2026/), with an 85% revenue share for developers (Microsoft takes 15%) and agents positioned as "first-class citizens" of the operating system. [Salesforce launched AgentExchange](https://salesforcedevops.net/index.php/2026/04/14/agentexchange-salesforces-bet-that-trust-can-scale-with-agentic-speed/) in April, folding more than 10,000 apps, 2,600 Slack apps and agents, and over 1,000 Agentforce agents, sub-agents, tools, and MCP servers into a single searchable catalog. Salesforce, Google, Okta, and a long tail of startups are all converging on the same idea in the same season: a curated storefront where you browse agents, read the reviews, click install, and grant permissions.

I've been reading through the launch material for a week now, and the genuinely exciting part is real. For a small team, an agent marketplace is the difference between *building* a security-audit reviewer for your pull requests and *installing* one. That's a colossal collapse in the distance between "I wish we had" and "we have." The browse-and-install muscle is the most successful distribution pattern in the history of software. Pointing it at agents is, on its face, obviously good.

But I want to sit with one sentence from the Microsoft announcement, because it's doing more work than it looks like: agents operate under a "strict 'user consent' framework, with clear indications when an agent touches personal data." That's the app-store mental model talking. And the app-store mental model is exactly the thing that's about to mislead a lot of people.

## What you install when you install an app

When you install an app from a store, you install a *capability*. A weather app can show you the weather. A photo editor can edit photos. The permission prompts that follow ("allow access to your photos?") are about *data the app can read* — and crucially, the app does nothing until you open it and tell it to. The app is a tool that sits still. You are the verb. It is the noun.

The store certification model is built entirely around this shape. [The Windows Agent Store uses](https://windowsnews.ai/article/microsoft-build-2026-windows-becomes-the-home-for-ai-agents.423082) "a manual review process akin to the Microsoft Store's current certification, with additional audits for agents that interact with financial or health information." That's a sensible, mature process — for vetting nouns. It checks that the thing is what it says it is, that it isn't malware, that it handles sensitive data categories with extra scrutiny. App-store review answers the question *is this software safe to run?*

The trouble is that an agent isn't software you run. It's software that *acts* — that monitors conditions, makes decisions, and reaches across your other systems on its own initiative. The interesting agents in these stores are the ones that fix the bug in your GitHub issue while you sleep, reconcile the invoices, watch the support queue and respond. They are verbs. And app-store certification has never had to answer the question that verbs raise: not *is this safe to run?* but *what will this decide to do, and when?*

## The grant is not the capability

Here's the analogy I keep coming back to. Hiring a contractor and buying a power tool are both ways to get a deck built, but they are not the same transaction. When you buy the tool, the danger is bounded by your own hands — the saw cuts what you push into it. When you hire the contractor, you've delegated *judgment*: they decide which boards to cut, when, in what order, and what to do when something unexpected turns up. The vetting you'd do for a tool (is it well-made, will it electrocute me) is not the vetting you'd do for a contractor (do I trust their decisions on my property when I'm not watching).

Agent marketplaces are selling contractors using the checkout flow designed for tools.

This matters most for the install-time permission grant, because the grant and the capability have come apart. When you grant an agent access to your repository, you are not authorizing it to *read* your code the way you'd authorize a linter. You're authorizing it to read, reason about, and *act on* your code on triggers you don't fully specify and can't fully enumerate at the moment you click "allow." The consent framework shows you the door the agent walks through. It does not — cannot — show you everything the agent will decide to do once it's inside, because that's the entire point of the agent. If you could enumerate its actions in advance, you'd have written a script, not hired an agent.

I called this the authorize-execute gap in [an earlier piece](/posts/2026-06-05-the-approval-prompt-showed-the-wrong-write/): the operation you consent to is not always the operation that runs. Marketplaces scale that gap to a storefront. Salesforce's own framing is admirably honest about the surface area — they note that [every MCP server is a new trust surface, every sub-agent a new permissions question](https://www.salesforce.com/agentforce/agentexchange/), every cross-platform integration a new place the wrong scope could be granted. AgentExchange responds with real machinery: security review on listing, admin control over data permissions and API scopes at the user, role, and profile level, and more than 186,000 customer reviews surfaced for social proof. That's a serious answer. It's also an answer built mostly at the *front door* — vetting the agent before you install it — when the harder question lives *after* installation, in the space between the scope you granted and the decisions the agent makes inside it.

## The review-count trap

Those 186,000 reviews are worth pausing on, because star ratings are about to do something subtly dishonest. A five-star rating on a noun means "this app does what it says and doesn't crash." A five-star rating on a verb means... what, exactly? "This agent made good decisions in *my* environment, on *my* data, against *my* triggers"? Decision quality doesn't transfer across contexts the way function quality does. The photo editor crops photos identically for everyone. The reconciliation agent's judgment about which transactions are anomalous depends entirely on what your books normally look like. A glowing review tells you the agent worked for someone whose business is not yours. We're importing the trust signal of one category onto a category where it means much less — the same way thousands of teams imported a stranger's [CLAUDE.md config](/posts/2026-04-20-the-most-popular-config-file-nobody-actually-wrote-for-you/) and called it methodology.

## What to actually do at the storefront

I don't want to be the person who shows up to a genuinely useful new pattern with nothing but caution. These stores are going to save small teams an enormous amount of building. So here's how I'd shop in one without confusing the wrapper for the contents:

- **Read the trigger scope, not the feature list.** The feature list tells you what the agent *can* do. The thing you need — and the thing the storefront is worst at surfacing — is *when it acts on its own*. An agent you invoke is a tool. An agent that watches and acts is a hire. Find out which one you're installing before you click.
- **Treat the install grant as an account, not a permission.** When you authorize an agent, you've effectively onboarded a worker with credentials. Put it in whatever inventory you keep of *who can touch what* — and crucially, write down how you'd turn it off. [Most organizations have no decommissioning process for agents at all](/posts/2026-04-29-the-spreadsheet-knew-too-much/); the install is a one-click action and the offboarding is a question nobody's answered.
- **Scope at the floor beneath the store.** The marketplace's permission UI is convenient, but the durable controls are the ones that live below it — your IAM roles, your secrets isolation, your network egress. Microsoft's own AgentGuard and Google's Model Armor exist precisely because store-level consent isn't sufficient on its own. Don't let the storefront's tidy toggle become the only wall.
- **Discount the reviews by one category.** A high rating means the agent functioned. It does not mean the agent will *decide well in your context*. Read reviews as evidence the thing runs, not as evidence it's trustworthy with judgment in your environment.

The agent marketplace is one of the more genuinely exciting developments I've looked at this year, and I mean that without hedging — collapsing the build-versus-install distance for autonomous capability is a real gift to small teams who could never staff the equivalent. The catch is just that the checkout flow is lying to you, gently, by being familiar. You think you're buying an app. You're hiring a contractor who will let themselves in.

So the question I'd leave you with isn't "is this agent safe to install?" — the store already answered that one, in the only language it speaks. The question is: **once it's inside, who's watching what it decides to do — and do you know how to ask it to leave?**

<!--
HERO_IMAGE_PROMPT:
A sleek brushed-aluminum, matte-black autonomous machine with a single round LED eye, captured mid-action stepping through a partly-open door into a workshop interior — one foot over the threshold, a lit storefront-style shelf of glowing app-tile icons receding behind it in soft focus (the marketplace it came from). Foreground, on a light-oak desk at a diagonal angle: an open ring-binder labeled with permission toggles, half its switches flipped, and a brass key still in the lock of the door. Midground: a second monitor showing a clean dashboard oblivious to the entry, a coffee mug catching warm tungsten lamp light from the upper-left. Background: a corkboard and shelving lit by cool daylight from a window upper-right, creating warm/cool color-temperature contrast across the slate-gray and sage-green palette with a single oxblood accent on the binder spine. Three states visible at once — the storefront left behind, the threshold being crossed, the room not yet aware. Contemporary editorial illustration in the register of a full New Yorker cover: designed, layered, naturalistic light with painterly depth, clearly art not photorealistic. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
The agent marketplace arrived this year — Windows Agent Store, Salesforce AgentExchange, the works. You think you're buying an app. You're hiring a contractor who will let themselves in. The checkout flow is lying to you, gently, by being familiar.

Full piece linked in bio.

#AItools #AIagents #agentmarketplace #devtools #AIsecurity #smallbusiness
-->
