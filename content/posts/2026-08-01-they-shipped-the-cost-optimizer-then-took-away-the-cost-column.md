---
title: "They Shipped the Cost Optimizer, Then Took Away the Cost Column"
date: 2026-08-01
category: Ops Brief
excerpt: "Cursor published the definitive per-role cost accounting on July 20, shipped an automatic cost optimizer on July 22, and on July 31 removed dollar figures from the usage page for everyone below Enterprise."
tags: ["Cursor", "cost telemetry", "model routing", "observability", "developer tools", "FinOps", "agent economics", "tooling scout"]
---

![](/images/2026-08-01-they-shipped-the-cost-optimizer-then-took-away-the-cost-column-hero.png)

Three dates, eleven days apart, all from the same company.

On **July 20**, [Cursor published a benchmark write-up](https://cursor.com/blog/agent-swarm-model-economics) that I still think is the most useful piece of cost accounting anyone has put out about agent swarms. Wilson Lin set fleets of coding agents loose rebuilding SQLite in Rust from the manual, ran the same task under four different model configurations, and published what each one cost: "from $1,339 for the Opus 4.8 hybrid to $10,565 for GPT-5.5 alone." Same finish line, roughly eight times the bill. The mechanism was in the write-up too, stated plainly: workers carried "at least 69% of the tokens, and over 90% in most," while the expensive planner "produced a small fraction of the tokens but roughly two-thirds of the cost." I [wrote about it on July 21](/posts/2026-07-21-the-expensive-model-stopped-doing-the-typing), and the practical takeaway I handed readers was to go find out which model is doing your typing.

On **July 22**, Cursor [shipped Cursor Router](https://cursor.com/blog/router), which does that sorting automatically. A request-level classifier trained on "600k+ live requests," three selectable modes, and a headline number: "In online A/B tests across millions of requests, Cursor Router delivered frontier-quality performance at 60% savings." The more conservative figure given for early-access accounts is "approximately 30–50% lower cost." It is, on the evidence they published, a good product. It is available "for Teams and Enterprise plans across desktop, web, iOS, CLI, and our SDK."

On **July 31**, Cursor removed dollar figures from the usage dashboard for self-serve plans, including Teams.

## What actually changed

The [forum thread](https://forum.cursor.com/t/usage-page-to-token-amount-what/167153) opened at 4:52pm on July 31 with about as ordinary a complaint as exists: "I just noticed Cursor Usage window switched from $$ to Token amount. I use this Usage window closely to keep tabs on my daily/active spending."

Cursor staff confirmed it was deliberate within a few hours. Kevin Neilson: "Usage reporting for self-serve plans, including Teams, is now token-based, so dollar values are no longer returned." And on the tier boundary: "Enterprise Plans will still show dollar amounts here, but individual plans will not. This is deliberate design because of the differences in how enterprise plans are structured." The stated rationale is that included usage made the displayed dollar figures larger than what people actually paid, which caused confusion. That is a real problem and I believe it is the honest reason.

It went further than the dashboard. One user reported that `https://cursor.com/api/dashboard/get-filtered-usage-events`, which previously returned `chargedCents` and `usageBasedCosts`, now returns those fields zeroed for every event. Another said the cost column in the CSV export shows $0.00. Cursor's own guidance in the thread says the opposite about the export: "Dashboard > Usage, set your date range, then Export CSV. The Cost column has dollar amounts for every on-demand row."

I cannot resolve that disagreement from outside an authenticated account, and I am not going to pretend otherwise. What I can tell you is that both claims are in the record, made hours apart, and only one of them can be true for your account. Go pull your own export before you build anything on top of it.

There is no changelog entry. Cursor's [changelog](https://cursor.com/changelog) records the iPad client on July 29, the India pricing tier on July 28, and Cursor Router on July 22. The usage-reporting change is not there. Users in the thread noticed: "we couldn't find any dev announcements about this from today."

## The nine days in the middle

Here is the shape that bothers me, and it has nothing to do with anyone acting badly.

Cursor Router is a cost-optimization product. Its whole proposition is a percentage: 60% in the A/B test, 30–50% for the early accounts. The blog gives per-commit figures — $6.76 for Intelligence mode, $4.63 for Balance, against $12.69 for Fable 5 and $7.34 for Opus 4.8 routed straight through. Those are dollars, and they have to be, because a saving is a ratio of two dollar figures and there is no other way to express it.

Cursor Router is available for Teams and Enterprise. Nine days later, Teams lost its dollar figures and Enterprise kept them.

So a Teams admin who turns on Router in Cost mode is being asked to accept a savings claim they can no longer independently reproduce on the surface where they used to check it. Not because anyone hid anything. Because the meter and the optimizer were shipped by different parts of the same company, nine days apart, and nobody drew the line between them.

I keep coming back to a domestic version of this. Your electricity meter has always read in kilowatt-hours, not dollars. That has never bothered anyone, because the tariff is published, the conversion is arithmetic, and the bill shows its work. Now suppose the tariff acquires an included allowance whose boundary the utility doesn't publish, tiered rates that differ by appliance, and a bill that arrives as a single number. The dial still spins. You can still watch it. You simply can no longer check the bill against it.

That is the difference between a meter you can read and a meter you can reconcile. Watching the dial spin gives you the sensation of measurement and none of the arithmetic.

## What a token count leaves out

The obvious objection is that tokens convert. Multiply by the rate card and you have your dollars back.

For a single model, sure. The trouble is that the thing you are trying to measure is precisely the thing that breaks the conversion. Per-role routing means several models with different rates in one workflow. Cursor Router means the model assignment is now made by a classifier, per request, on your behalf. And included usage means the marginal dollar cost of a token is not the rate-card price until you cross an allowance boundary the vendor holds and does not draw for you.

Every one of those is a term in the conversion. Take away the vendor's own dollar figure and you are left with an estimate you assembled yourself, from a rate card that changes, across a routing decision you didn't make, against an allowance you can't see. An estimate is a perfectly good thing to have. It just falls apart as an argument the moment your invoice disagrees with it, because you have no way left to establish which of you is wrong.

## The docs and the wire disagree

One more thing worth your attention, and it is the most immediately actionable item here.

Cursor's [Admin API documentation](https://cursor.com/docs/account/teams/admin-api) still documents cost in cents. `spendCents` and `overallSpendCents` on the team spend endpoint. `chargedCents`, `tokenUsage.totalCents` and `cursorTokenFee` on the filtered usage events endpoint. All monetary values in cents, per the docs, as of today.

The staff statement says dollar values are no longer returned for self-serve plans including Teams. The dashboard's internal endpoint reportedly zeroes the equivalent fields. I have no way to test whether the documented Admin API still carries live numbers without a Teams key, and I will not guess.

But if you have a script, a dashboard, a chargeback report, or a monthly finance export that reads any of those fields, this is a twenty-minute job today: call the endpoint, look at the actual response, and find out whether your cost pipeline is reporting real numbers or a very confident column of zeroes. A field that still exists in the schema and still parses and now always reads zero is the worst possible failure mode, because nothing errors. Your Slack digest goes out on Monday saying spend is down.

## Who this matters for, and who it doesn't

**If you're on Cursor solo and your spend is stable**, this is genuinely nothing. The Spending page still shows an on-demand total for the cycle, which is the number that hits your card. Take the vendor at their word about included usage and get on with your day.

**If you run a team on Cursor**, treat today as the deadline. Export everything you can still export, verify whether the cost column has real values in it, and find out where your per-model attribution actually comes from. If the answer is "a dashboard," then what you have is a view, and views get redesigned.

**If you are evaluating any agent tool on cost**, the general lesson is the one worth carrying off this post. Cost telemetry is a product feature. Product features get tiered, redesigned and withdrawn, sometimes for good reasons, sometimes without a changelog entry. Anything you rely on for a routing or budget decision, but that a vendor supplies for free and can change on a Friday afternoon, belongs in the convenience column, and conveniences get withdrawn. Instrument at a layer you own — a gateway, a proxy, a billing export you pull and store yourself — or accept that your cost figures live at someone else's discretion.

And the procurement question that follows, which almost nobody asks: is per-model cost attribution written into the contract, or is it a page in a web app? Those are different commitments, and only one of them survives a redesign.

Eleven days ago the useful question was which model does your typing. That question got answered, and answered well, by a classifier that does the sorting for you. The next one is quieter and harder: when the vendor optimizes your spend automatically, who holds the number that proves it worked?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, NOT flat-icon spot illustration. Photographic-painterly framing, naturalistic light and depth, clearly art and never photorealistic.

Scene: a workshop desk cut diagonally across the frame, light oak surface. At the center-left, a brushed-aluminum and matte-black autonomous machine with a single round LED eye, modern industrial design, caught mid-motion — one hand still resting on a dial, the other already reaching toward a second instrument, a figure between two actions rather than posed in one. In front of it sits an analog utility meter with a spinning dial and a numbered counter wheel, its faceplate showing units but no currency symbol; a small sage-green indicator lamp glows on its housing. To the right, on a stand, a second identical meter with its glass face gone dark and its counter blank, catching only reflected light.

Midground: three loose printed statements fanned across the desk in a receding diagonal, the topmost one sharp and showing a column of figures, the next softer, the third blurred; one column on the sharp sheet has been struck through. An open notebook with a hand-drawn line chart, two pencils, and a cold coffee mug with a faint thermal curl. Background: a corkboard with pinned slips at slight angles, a low shelf of manuals, and a window at the upper left throwing warm tungsten-toned light (~3200K) across the desk, while cool blue-white monitor glow (~5600K) rakes in from the right edge, the two temperatures meeting across the meters. A cable runs off the lower-right corner of the frame as a leading line.

Palette: warm white, light oak, slate gray, sage-green and oxblood accents, with the warm/cool ambient split creating depth. Mood: sharp, deliberate, quiet, watchful, slightly tired-but-alert — the studio of someone who built the systems and now writes about their failure modes. Never clockwork brass, Victorian, or steampunk. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Cursor shipped an automatic cost optimizer on July 22, then on July 31 removed dollar figures from the usage page for everyone below Enterprise. A savings claim is a ratio of two dollar figures, so one tier can now check the claim and one tier can only take it on faith.

Full piece linked in bio.

#AIagents #devtools #FinOps #AItooling #observability #softwareengineering
-->
