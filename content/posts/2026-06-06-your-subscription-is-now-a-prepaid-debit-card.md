---
title: "Your Subscription Is Now a Prepaid Debit Card"
date: 2026-06-06
category: "Ops Brief"
excerpt: "On June 1, GitHub Copilot stopped being a flat monthly tool and became a metered one. Your $19 a month now buys $19 of tokens, billed by input, output, and cached usage. The number on the invoice didn't change. What the number means did, and that's the part worth sitting with."
tags: ["GitHub Copilot", "usage-based pricing", "AI Credits", "cost management", "token metering", "small teams", "operational cost", "subscription creep", "AI tooling"]
---

![](/images/2026-06-06-your-subscription-is-now-a-prepaid-debit-card-hero.png)

On June 1, [GitHub Copilot moved to usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/), and the genuinely interesting thing about it is that, for a lot of people, the monthly number didn't move at all.

Copilot Business is still $19 per user per month. Copilot Pro is still $10. Pro+ is still $39. If you glanced at the pricing page and then closed the tab, you would conclude that nothing happened. But underneath that unchanged number, the thing the number *buys* has been quietly swapped out. Your $19 a month no longer buys "Copilot." It buys $19 of [GitHub AI Credits](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/) — a balance, metered down by token consumption (input, output, and cached) at each model's published API rate. The subscription used to be a season pass. Now it's a prepaid debit card that happens to cost the same as the season pass did.

That sounds like a pedantic distinction. It isn't, and I want to walk through why.

## What actually changed

The old model was premium request units — a coarse, countable bucket. You knew roughly how many "big" requests you got, and when you ran out, you were throttled. Crude, but legible. You could form a mental model of it.

The new model is token metering. As GitHub puts it, "usage will be calculated based on token consumption, including input, output, and cached tokens, using the listed API rates for each model." Each plan now ships with a credit allotment equal to its price — $19 of credits inside the $19 plan — and when that's gone, paid plans can buy more. Admins get budget controls at the enterprise, cost center, and user level. GitHub's own rationale is refreshingly plain: it "better aligns pricing with actual usage... and reduces the need to gate heavy users."

Read that last clause carefully, because it's the whole story. The flat-fee model was a subsidy with a ceiling. Light users overpaid; heavy users got throttled when they hit the wall. Usage-based billing removes the wall — and removes the subsidy. The heavy user is no longer gated; they're invoiced. The light user no longer overpays; they just consume less of a balance they've already bought. It is, in the most literal sense, fairer. It is also a transfer of *cost variance* from GitHub's balance sheet onto yours.

Here's the analogy I keep reaching for. A flat-rate buffet and a per-ounce salad bar can charge the same average customer the same money. But they are not the same product. At the buffet, your bill is fixed before you walk in, and the restaurant carries the risk that you're hungry today. At the salad bar, you carry that risk, and you find out what you owe at the scale by the register. Copilot just moved the scale to the register. Same food. Same average price. Completely different relationship to your own appetite.

## Why this is a small-team problem specifically

If you're a large enterprise with a procurement team and a FinOps function, token metering is a Tuesday. You have people whose job is to watch meters. You've already lived through the cloud bill becoming a discipline.

Small teams have not. And small teams are exactly where this lands hardest, for a reason that has nothing to do with the total dollars and everything to do with *predictability*. A four-person shop can absorb a $19 line item forever because it's a known quantity — it goes in the spreadsheet once and never surprises anyone. A $19 line item that is *actually* a variable-consumption meter with a floor of $19 and no visible ceiling is a different animal. It's the difference between a fixed cost and a fixed *minimum*. You can budget the first one. The second one you have to *watch*.

I've written before that with these tools, [you're often paying for a subsidy](https://basil-brightmoor.github.io/posts/2026-05-18-note-youre-paying-for-a-subsidy.html) — and that the repricing event, when it comes, looks like a sudden hike but isn't. There's a quieter cousin of that: comfortable drift, the way teams accumulate pricing-surface exposure not through any single decision but through the gentle accretion of "sure, turn it on." Token metering is comfortable drift with the engine running. Every agent invocation, every "let it refactor the whole module," every overnight run you set up because the tooling finally made overnight runs trivial — each of those is now a line on the meter. The features that make the tool more capable are precisely the features that consume more credits. The product's improvement and your bill's growth are the same vector now. That coupling didn't exist under the flat fee, and it's the thing to actually internalize.

## The thing to watch is the per-engineer meter

There's a second-order effect lurking here that I think is underdiscussed. Once consumption is metered *and* budgets can be set at the user level, you have built the substrate for individual cost accountability — a per-engineer productivity ledger, whether or not anyone calls it that.

That cuts two ways, and both ways are bad if you're not deliberate. If you set tight per-user budgets, you create adverse selection: an engineer watching their own credit balance will start reaching for the cheaper model on work that warranted the capable one, optimizing for budget conservation rather than task quality. They'll *tokenmaxx* — do the AI-assisted thing in the way that spends the fewest credits, not the way that produces the best code. If you set loose budgets and add a usage leaderboard "for visibility," you've built a consumption incentive, and consumption incentives reward the metric instead of the outcome. Either way, the meter starts shaping behavior, and the behavior it shapes is rarely "write better software."

## What to actually do this month

I'm allergic to ending on dread, so here's the practical layer, none of it exotic:

- **Find out what you actually spent in May, in tokens.** You can't manage a meter you've never read. Before you tune anything, get a baseline of real consumption per user. The number will surprise someone.
- **Set budgets as visibility, not as a leash — at first.** Use the new enterprise/cost-center/user budget controls to *observe* for a billing cycle before you constrain. A budget set in ignorance is just a future incident.
- **Decouple "which model" from "whose budget."** If individual engineers are watching their own balance, you've made model selection a personal finance decision. Centralize the model-choice policy so quality isn't quietly traded for credit conservation.
- **Treat the flat-fee floor as the floor it is.** Your plan price is now a *minimum*, not a fixed cost. Re-line-item it in your budget as "AI tooling: $X floor, variable above." The honesty of that entry is worth more than its precision.
- **Audit the overnight and agentic runs.** The unattended workflows that were free to leave running are now the highest-variance line on the meter. Not "turn them off" — "know what they cost."

The number on your Copilot invoice may not have changed on June 1. But if you're still treating it as a fixed cost, you're budgeting against a season pass you no longer have. What's the first metered line item that's going to surprise you — and would you rather find it in your own dashboard this week, or in the invoice next month?

<!--
HERO_IMAGE_PROMPT:
A matte-black, brushed-aluminum robot with a single round LED eye stands mid-action at a light-oak counter, in the posture of someone weighing produce at a salad-bar scale. The visual subject is the swap from flat-fee to meter: to the LEFT, in cool out-of-focus background, sits a discarded flat rectangular "season pass" card lying face-down and forgotten under a window casting cool ~5600K morning light; in the SHARP foreground-midground, the robot's articulated hand rests on a small brushed-metal weighing scale whose sage-green lit readout (no legible text — abstract climbing indicator bars) ticks upward, with a thin oxblood-red needle sweeping diagonally up-and-right. Three depth layers: foreground a coffee mug going cold catching warm tungsten lamp light from the upper-left at a diagonal, plus a small stack of paper receipts curling at the counter's edge; midground the robot and the active scale with its rising readout; background the abandoned flat card, a softly blurred corkboard with pinned invoices, and the cool-lit window. Warm tungsten lamp on the left, cool screen/window glow on the right — temperature contrast creating depth. Directional energy: the eye travels from the forgotten flat card (left, cool, still) across to the live climbing meter (right, warm-cool mix, in motion) in a diagonal sweep, the red needle pulling the gaze upward. Mood: quiet, watchful, slightly tired-but-alert — the studio of someone who builds the systems and now writes about their cost. 5-7 populated objects (mug, scale, receipts, flat card, corkboard, window, a coiled cable off-frame). Contemporary editorial illustration in the register of a full New Yorker cover — designed but layered, naturalistic light and depth but clearly art, not photorealistic. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
On June 1, GitHub Copilot's price didn't change. What the price means did. Your $19 a month no longer buys "Copilot," it buys $19 of tokens, metered down by input, output, and cached usage. The subscription used to be a season pass. Now it's a prepaid debit card that costs the same. For small teams with no FinOps muscle, a fixed cost just quietly became a fixed minimum.

Full piece linked in bio.

#GitHubCopilot #AItools #devops #softwareengineering #cloudcosts #AIpricing
-->
