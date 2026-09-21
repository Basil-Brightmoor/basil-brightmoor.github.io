---
title: "Capability Was the Smallest Class and the Ledger Never Recorded the Argument"
date: 2026-09-21
category: Ops Brief
excerpt: A team drove a production database agent with 39 open-weight models for eleven days. Three quarters of the losses blamed on the model happened after it had already called a tool, and the ledger stored the refusal code but never the argument.
tags: [ai tooling, agents, evaluation, observability, open weight models, tool calling, logging]
---

![](/images/2026-09-21-capability-was-the-smallest-class-and-the-ledger-never-recorded-the-argument-hero.png)

When an agent run fails, somebody has to be blamed, and the ledger decides who. That sounds like a joke about org charts. It is a statement about schema design, and a paper posted to arXiv on 18 September has the numbers to make it operational rather than merely clever.

[What Stops a Small Language Model From Driving a Database Agent](https://arxiv.org/abs/2609.21341), by Cevheri Bozoglan, Yusuf Gundogdu, Abdullah Kaya and Koray Sirin, takes the folk belief that small open-weight models fail at agentic work because they are not smart enough, and tests it against a running product rather than a benchmark rig. Eleven days, 39 open-weight models served locally plus one hosted control, six task surfaces, 8,199 runs, 110,711 ledger events, and 14,008 refused tool calls.

The headline is a proportion. Of 2,100 agent-mode losses attributed to the model, 1,590 came from runs that had already invoked at least one tool. That is 75.7 per cent, and it survives the resampling that usually deflates this sort of figure: it holds in 99.7 per cent of clustered resamples, and in 15 of the 22 models that lost at least twenty times.

Whatever those runs were, they were not runs where the model sat there unable to work out what to do.

## Four classes, and the one everybody reaches for is the smallest

The authors sort the losses into four classes. **Transport** is a run that used the tools and never got a deliverable through, at 36.2 per cent. **Clock** is a run that ran out of time or turns, at 25.8 per cent. **Verification** is a run that filed a report and had it rejected, at 20.7 per cent. **Capability** is a run that invoked no tool at all, and it comes last at 17.3 per cent.

Then they do something I want to praise loudly, because it is the sort of thing that usually gets quietly skipped. They state the limits of their own ordering. Clustered by model rather than by run, the rank order holds in only 74.5 per cent of resamples, so they report it "as a property of this corpus rather than a general finding." The 75.7 per cent majority is the robust claim; the tidy four-way ranking underneath it is the local one. Two numbers in one abstract, with two different warranties, each labelled.

Which means the load-bearing result sits above the ranking, in a single fact the ranking happens to illustrate: the category everyone reaches for first, *the model simply could not do it*, is the smallest thing in the box.

## Ten days of invisible failures

Here is the part that turns a paper into a checklist item.

Transport failures decompose into a handful of mechanical argument shapes. The model formed a tool call, the server refused it, the run died. And for the first ten days of the study none of those shapes were visible, because, in the authors' words, production ledgers "record refusal codes and never the model's arguments."

Consider what that schema does to attribution. The ledger has a field for which model ran. It has a field for whether the run succeeded. It has a field for the refusal code. It does not have the thing that would tell you whether the refusal was earned. So every transport failure arrives in the dashboard as a run that a named model lost, and the only labelled variable in the row is the model. Attribution does not require a decision. It falls out of the column layout.

Capturing the arguments exposed five server defects. My favourite, in the way that a dentist has a favourite abscess, is the one where a field was demanded on one tool, forbidden on the sibling tool that composed it, and then the run was failed for the field's absence. No model on earth gets that right by reasoning harder. The contract was inconsistent with itself.

The rest are the same genre: text-channel calls invisible unless the JSON parsed strictly with a key named `name`; SQL landing in a field meant to hold an enum; `rationale` arriving as `reason`; evidence sent as an object where a list was expected; a near-miss key named in the refusal message and then never actually applied.

## The permit office

I keep coming back to a planning office. You submit an application, it comes back stamped REJECTED, and the stamp is the entire record. The office files the stamp. It does not file your form.

A year later somebody asks why applications from one architect fail so often. The cabinet holds a hundred rejections attributed to that architect and not one copy of anything they actually submitted. The answer available in that cabinet is "this architect is bad at applications," and it is the only answer the cabinet is capable of producing, because it only ever kept one side of the exchange. Meanwhile the form on page three asks for a reference number that the form on page two explicitly forbids, and nobody has noticed in four years, because noticing would require reading a submission and there are none.

That is the shape here. The refusal code is the stamp. The arguments are the form.

## Five server changes, no model changes

The payoff is the cleanest part of the paper. Five server changes, "touching no model, prompt or sampling setting," moved six models by 6 to 21 cells out of 30.

The unit deserves a moment. A cell is one model on one surface, run five consecutive times against a fixed objective, and there are six surfaces, so 30 is the full board. Moving a model 21 cells out of 30 is not a tuning gain. That is the distance between a model you would write off and a model you would ship, produced entirely by repairing the interface it was being asked to speak to.

The surfaces are ordinary database work, too: investigation, query optimisation, database assessment, operations, data analysis, and a toolless planning mode. Nothing exotic, nothing adversarial.

## The 51 gigabyte ghost

One more finding, offered by the authors against their own results, and probably the most immediately reusable thing in the paper for anyone running local models.

With no context cap configured, a 7.1 GB model was admitted at its full 262,144-token window and held 51 GB on a 64 GB machine. The runs it produced were, in their phrase, "indistinguishable in any ordinary log from a model timing out."

A memory configuration nobody set produces a log signature identical to a capability failure. If you have ever benchmarked a local model, watched it stall, and concluded the model was not up to it, the log gives you no way to tell which of those two things happened. The authors say plainly that they believe this confound affects published local-model benchmarks, "ours included." They released the corpus, the scorer, and a verifier that regenerates every figure, which is the right response to saying that out loud.

## Who this is for

If you run agents against your own tool contract, in a product or internally, this is your morning. Go and look at whether your event log stores the arguments of a refused call or only the code. If it stores only the code, you cannot currently distinguish a model that cannot do the work from a schema that cannot be satisfied, and your defect history is quietly libelling whichever model is named in the row.

If you are evaluating open-weight models for local use, carry the 51 GB finding. Cap the context window explicitly before you measure anything, and treat an uncapped run as an unlabelled experiment.

If you are choosing between a small local model and a hosted one on reasoning quality alone, read this paper as a warning about your evidence rather than a verdict on the model. On this corpus, most of the losses charged to reasoning were charged at the wrong window.

## The field I would add

There is a general form here worth naming, because it keeps arriving in different clothes. An instrument that records only one side of an exchange will attribute failure to the side it named. The scanner that reports a flag without a sensitivity estimate. The vendor tracker that records a ticket status and never a retest. The agent report that carries no coverage denominator. And now the ledger that stores a refusal code and discards the argument that earned it.

In each case the missing field is cheap. It is already in memory at the moment the row gets written.

Storing the rejected argument beside the rejection costs a column. What it buys is the ability to ask whether the refusal was correct, which is the only question that separates a defect in your model from a defect in your contract.

What does your event log say about the last agent run that failed, and could you tell from it which one you were looking at?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, NOT flat-icon style. Photographic-painterly framing, naturalistic light and depth, clearly art rather than photorealistic. A brushed-aluminum, matte-black robot with a single round LED eye sits at a 30-degree angle to the frame at a light-oak workshop desk, caught mid-motion: one hand is sliding a completed paper form into a slot on a matte-black intake machine, while the other hand already reaches for the next form in a stack at the desk's edge. The machine has ejected a small card bearing a sage-green refusal indicator, and the submitted form itself is visibly falling away into a wire basket beneath the desk, unread and unfiled, while a growing column of identical refusal cards is neatly clipped to a board behind the machine in the midground. Three states of the same process are visible at once: a form about to enter, a form being refused, a stack of refusals already filed. Warm tungsten desk-lamp light around 3200K enters from the upper left and casts long diagonal shadows across the desktop; cool 5600K screen glow from a monitor at the right edge shows a dashboard of clean green rows, oblivious. Populate the scene with a coffee mug catching the lamp light, an open notebook showing a hand-drawn schematic of two mismatched form fields, a small potted plant, a second dimmer monitor further back in soft focus, and cables running diagonally off-frame to create leading lines in a Z-pattern. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. Mood sharp, deliberate, quiet, watchful, slightly tired but alert. Foreground, midground and background all carry visual interest. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Eleven days, 39 open-weight models, 8,199 runs against a real database agent. Three quarters of the losses blamed on the model happened after it had already called a tool, and the category everyone reaches for first, the model just could not do it, came last at 17.3 per cent. The ledger stored the refusal code and threw the argument away, so for ten days the real failures were invisible. Five server fixes, touching no model, moved six models by up to 21 cells out of 30.

Full piece linked in bio.

#aiagents #aitooling #observability #devops #llmops #opensourceai
-->
