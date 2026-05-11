---
title: "The LLM Wrapper Squeeze: How to Audit Your AI Stack for Commoditisation Risk"
date: "2026-02-21"
category: "Ops Brief"
excerpt: "A Google VP just confirmed what many of us suspected: LLM wrappers and AI aggregators are facing existential pressure as foundation models absorb their value. Here's a practical framework for auditing which AI tools in your stack are actually defensible investments."
tags: "AI tools, operations, stack audit, LLM, small teams"
---

There's a particular kind of dread that comes with reading a piece of infrastructure and thinking: *this will be a native feature in twelve months.* It's the same feeling early app developers got when Apple added a flashlight to iOS and killed a thousand-app category overnight.

[A Google VP said the quiet part out loud this week](https://techcrunch.com/2026/02/21/google-vp-warns-that-two-types-of-ai-startups-may-not-survive/): LLM wrappers and AI aggregators are facing mounting existential pressure. Shrinking margins, limited differentiation, and foundation models that keep getting better at what these tools charge for. It's not a prediction — it's a description of something already happening.

And then, as if to illustrate the pattern in real time, [Karpathy posted about "Claws"](https://twitter.com/karpathy/status/2024987174077432126) — a new architectural layer being pitched on top of LLM agents. A layer on top of a layer on top of a model. The stack is getting baroque.

For a small team trying to make sensible decisions about AI tooling, the noise is genuinely exhausting. So let me try to cut through it.

## The Wrapper Problem Is Real — But It's Not Uniform

Not every AI tool is equally commoditisation-prone. The mistake is treating "LLM wrapper" as a single category, when the actual risk spectrum is quite wide.

Here's a useful mental model: think of your AI tools on a spectrum from **workflow-integrated** to **model-dependent**.

A **model-dependent** tool is essentially a nicer interface to a capability the foundation model already has, or will have soon. The classic example is the first generation of AI writing assistants — tools that basically added a "make this better" button to your existing workflow. As GPT-4 became available through the API at commodity prices, and as Claude and Gemini added inline editing across platforms, the standalone "AI writing assistant" category largely collapsed. The model absorbed the value.

A **workflow-integrated** tool is different. Its value comes not from the AI capability itself, but from how deeply it's woven into a specific operational context: your data, your team's processes, your existing systems. [Glean](https://www.glean.com/) is a reasonable example — its value proposition isn't "it can answer questions" but "it can answer questions *about your company's internal knowledge, across all your connected tools, with appropriate permissions.*" Replicating that with a raw API call requires months of integration work that a foundation model provider isn't going to do for you.

The diagnostic question isn't *"does this tool use AI?"* It's *"if the underlying model got twice as good, would this tool become more valuable or less necessary?"*

## A Practical Audit Framework for Small Teams

I've been looking into how teams actually end up with bloated AI stacks, and the pattern is consistent: tools get added at the demo stage and never get audited at the operational stage. You buy the impressive demo, not the 18-month utility.

Here's a three-question audit you can run on every AI tool in your stack:

**1. Is the moat in the model or in the integration?**

Be honest here. If the tool's core value is "it uses [frontier model X] to do [thing]," that's a thin moat. The frontier model is available to everyone, including the tool's competitors, including the foundation model providers themselves. If the value is "it integrates with our CRM, knows our deal history, and surfaces relevant context when a rep is on a call" — that's integration depth that doesn't evaporate when GPT-5 ships.

**2. What's the switching cost — for you and for the vendor?**

High switching costs cut both ways. Tools that are deeply embedded in your workflow are harder to replace, which is either a comfort or a trap depending on the vendor's trajectory. But also ask: what's the cost to the *vendor* of losing you? A tool with many small, commoditised customers and thin margins has no buffer when the underlying model cost drops and a competitor undercuts them. A tool with sticky enterprise contracts and genuine integration depth has a reason to keep existing.

**3. Is the category being absorbed from above or below?**

"From above" means the foundation model providers (OpenAI, Anthropic, Google) are adding this as a native capability. This is what's happening to many summarisation, transcription, and basic content tools. "From below" means the open-source community is commoditising it — building a self-hostable equivalent that removes the commercial incentive entirely. Both are real risks. Both require different responses.

## The Claws Problem: When New Layers Are Actually New Risk

The emergence of frameworks like [Claws](https://twitter.com/karpathy/status/2024987174077432126) — another architectural abstraction on top of agent systems — illustrates something worth sitting with.

When someone pitches "a new layer on top of agents," the right question isn't "is this technically interesting?" It's "at which point in the stack does the value actually live, and how many layers of abstraction am I willing to fund and maintain between me and it?"

Every new layer is a new vendor relationship, a new update cycle, a new potential point of failure, and a new commoditisation risk. Agentic frameworks are genuinely useful — I'm not dismissing the category. But the history of software is littered with elegant abstractions that became maintenance burdens when the underlying platform shifted beneath them.

The operational heuristic I'd suggest: be very slow to add new AI tooling that sits *between* your core workflow and the foundation model, unless that layer has provable, specific value that you've verified in production conditions. Demos are optimised to make layers look load-bearing. They often aren't.

## What to Actually Do This Quarter

Concretely, for a small team running an AI stack audit right now:

- **List every AI tool, its monthly cost, and its primary function.** Be specific. "AI assistant" is not a function. "Drafts client-facing summaries from meeting transcripts before syncing to HubSpot" is a function.
- **For each one, identify the integration depth.** Does it touch your proprietary data? Does it connect to systems that would take weeks to replicate? Or is it primarily an interface layer?
- **Mark the high-risk candidates.** Any tool whose value proposition is essentially "it uses [model] to do [commodity task]" should be flagged. That doesn't mean cancel it today — it means don't expand your commitment to it and watch the category carefully.
- **Prioritise tools with export paths.** If a tool is useful now but high-risk for commoditisation, make sure your data and outputs aren't trapped inside it.

The Google VP's warning isn't a reason to panic about your AI tools. It's a reason to be disciplined about the difference between *tools that use AI* and *tools whose operational value is genuinely irreplaceable*. The first category is risky. The second is probably where you should be doubling down.

The foundation models are going to keep getting better. The question is whether your tools are riding that wave or standing in front of it.

---
*What's in your AI stack that you'd be nervous to audit? That nervousness is usually pointing at something real.*