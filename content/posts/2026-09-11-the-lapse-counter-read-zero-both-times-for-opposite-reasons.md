---
title: "The Lapse Counter Read Zero Both Times, for Opposite Reasons"
date: 2026-09-11
category: Ops Brief
excerpt: A benchmark swept cache age from 1 to 28 days and got a flat line. Switch off scheduled refresh and stale answers went from 4 to 45. The counter built to catch expiry read zero in both runs.
tags: [ai tooling, agents, rag, data freshness, observability, evaluation]
---

![](/images/2026-09-11-the-lapse-counter-read-zero-both-times-for-opposite-reasons-hero.png)

Here is an experiment that ought to work. Put an agent in front of enterprise data that keeps changing underneath it. Build its caches, then wait one day, fourteen days or twenty-eight days before asking it questions. Count how often it returns an answer that used to be true. Older cache, more stale answers. Obviously.

[ChurnBench](https://arxiv.org/abs/2609.11515), a benchmark Vivek Kumar Singh and Preeti Priyam posted to arXiv on 10 September, ran precisely that sweep and got a flat line: seven, four and four freshness errors at 1, 14 and 28 days. The tidy thing to do with a null like that is shelve it. The authors went looking for why the dial they were turning was not connected to anything, and what they found is the most useful thing I have read this week about running a retrieval layer under an agent.

## The instrument comes first

The mechanism is only interesting because the instrument can see it, so start there.

The paper's related-work section makes a blunt point about the retrieval benchmarks everybody grades against (BEIR, MS MARCO, the multi-hop question sets): they freeze a corpus and score against it. As the authors put it, "A frozen corpus cannot produce a stale answer at all." Under that design a stale answer cannot occur, so no score can ever reflect one.

ChurnBench generates the world as a timeline instead. A seeded simulator plays out a software-asset-management estate day by day (hires, offboardings, license reassignments, price changes, contract renewals) and writes every event to an append-only ledger. The four sources the agent queries are folds of that ledger at a chosen moment: a PostgreSQL warehouse, a MongoDB operational store, a mock SaaS API with 350 ms of added latency and a limit of sixty requests a minute, and a pile of contract documents rendered from the ledger so that renewal terms exist only in prose. Gold answers are computed from the ledger by a resolver with no model in it, never from the stores.

That buys a precise definition. An answer is a **freshness error** if and only if it is wrong against the world at evaluation time and correct against the world at the effective retrieval time of the facts it used, which is read off the trace as the last-refresh stamp of the entity actually consulted. An answer that matches neither world was never true of anything, and it is filed as a reasoning error. The authors resolved the ledger at both timestamps for every freshness error they report, so the label is checked rather than asserted.

Think of a newspaper. A reasoning error is a reporter who got the story wrong. A freshness error is an accurate story in yesterday's paper. They look identical to the reader holding the page, and they are fixed by entirely different departments: one goes to the newsroom, the other to the delivery schedule. The paper says as much. An answer that was true of an earlier world "points at the grounding layer and is fixed by a refresh policy."

## Why the dial was not connected

The system under measurement uses tiered refresh, which is about as standard as caching gets. Each entity class is registered with a time-to-live. License assignments and user status are hot, on a one-day TTL. Prices and cost-center membership are warm, at seven days. Contract terms and vendor dimensions are cold, at thirty. Every simulated day, the harness refreshes anything whose TTL has lapsed.

Now think about what "the cache was built 28 days ago" means for an entity on a one-day TTL. It was refreshed over and over on the walk to evaluation, and it arrives about a day old no matter when the cache was first built. The traces show exactly that. At a 28-day cache age with tiering on, assignments and user status had an observed age of one day, prices five, and contract terms twenty-nine, because a thirty-day TTL never lapses inside a 28-day window. Cache age, the variable the whole sweep existed to move, only ever reached the retrieval layer for the cold tier.

Then the ablation, one flag changed and everything else held fixed: turn tiered refresh off, build the cache once, never touch it again.

| Refresh | 1-day cache | 28-day cache |
|---|---|---|
| Tiered, on | 7 | 4 |
| Tiered, off | 7 | 45 |

At one day, identical: the same seven errors from the same seven tasks, because nothing has had time to drift and there is nothing for refresh to prevent. At 28 days, elevenfold. An effect that is exactly zero at the short window and large at the long one is what a TTL-bounded mechanism predicts, and it is not what an age-driven one predicts, since cache age differs by a factor of 28 across the columns in both rows.

The sentence from the paper that generalises well past agents: "A drift benchmark that sweeps the gap between index build and evaluation quietly assumes the index is never maintained." For anything running in production, that assumption is false, and the sweep measures nothing.

## The counter that read zero twice

This is the detail I would pin above the dashboard.

The harness counted TTL-lapse events, meaning queries that hit an entity past its expiry. That counter read zero in both configurations. With tiering on, it read zero because refresh always renewed every entity before its tier expired. With tiering off, it read zero because the staleness check was skipped entirely and never evaluated expiry at all. One healthy system and one with its safety check switched off, reporting the same number. The authors' verdict: "A metric that reports identical values for opposite behaviors is a measurement trap."

I wrote on 14 August about [a metric that was non-decreasing by construction](https://basil-brightmoor.github.io/posts/2026-08-14-the-metric-was-non-decreasing-by-construction-and-the-security-wasnt.html), a number that could not register the failure it was meant to watch. The lapse counter is its sibling: a zero that two different code paths produce, one because the check ran and found nothing and one because the check did not run. Once you have seen the shape, you start noticing candidates for it on ordinary operations boards. A failed-jobs tile that would also read zero if the scheduler stopped enqueueing jobs. A policy-violation count that would also read zero if the policy engine were disabled. Whether yours behave that way is an empirical question about your code, and that is the point: the number alone cannot tell you.

The paper's remedy is plain and cheap. Record per-entity refresh timestamps, not counts of expiry events. A timestamp cannot be zero by absence. An entity that was never refreshed shows its build time, twenty-nine days old, in plain sight.

## Where the staleness actually landed

The attribution is where this becomes operational advice rather than benchmark methodology.

With tiering on, fourteen of the fifteen freshness errors across all three windows came from a single entity class: prices, on the seven-day tier. Nine came from cost-center spend totals and five from finding the highest-spending cost center. The one-day entities produced none. The thirty-day contract terms produced none in the long windows either, despite being stale by construction, because contract terms barely change: twenty-seven renewals across a ledger of 56,370 events. (The fifteenth error was the only cold-tier error anywhere in the data, at the one-day window, where a contract mutation happened to fall inside the gap.)

Switch tiering off at 28 days and the picture inverts. Of the forty-five errors, fifteen came from user status and ten from assignments, the hot entities that had contributed nothing under tiering, and twenty from prices.

The authors' generalisation is that staleness exposure is governed by the product of tier width and entity mutation rate, and that neither factor predicts errors on its own. The widest tier was harmless because its data hardly moved. The fastest-moving data was harmless until its tier was removed. Their practical instruction is the sentence I would hand to anyone who owns a cache config: tiers "should be assigned from measured mutation rates rather than from intuitions about which data feels important."

If your TTLs were chosen by asking which data feels important, this is a measured result telling you to count changes instead.

## What the accuracy number is really measuring

The authors are unusually candid about what their headline accuracy figures do not show, and the candour is itself instructive.

The 180-task run exercises 22 distinct measures. Nine are registered in the system's semantic model; thirteen are not. A hundred and nine of the 180 tasks target unregistered measures and fall through to model-generated SQL, and between 49 and 53 of the 51 to 69 reasoning errors per run come from exactly those tasks. In their words: "Reported accuracy therefore largely measures registry coverage." They also ran no baseline comparison under the final design, used one model (Nemotron 3 Ultra through NVIDIA NIM, at temperature zero) and one framework (LangGraph), and worked on synthetic data from a single domain. The freshness counts under tiering are small, four to seven per run, and they say so, resting the negative finding on the per-entity timestamps and the 4-versus-45 ablation rather than on the sweep.

**Who this is for:** anyone running an agent over a staged grounding layer (vector indexes, materialized aggregates, cached pulls from rate-limited SaaS APIs), and anyone building an evaluation that claims to measure drift. The [repository](https://github.com/vsingh45/churnbench) is MIT-licensed, roughly 7,500 lines of Python with 316 tests, and a 180-task run costs about fifty cents in inference with reasoning mode off. That is cheap enough to fork and point at your own tier table.

**Who it is not for:** teams whose agents query everything live, who pay for freshness in latency and rate limits instead, and anyone hoping for a verdict on which grounding architecture wins. The paper declines to offer one, explicitly.

## What to do on Monday

**Log what the answer was built from, with timestamps.** On [8 September](https://basil-brightmoor.github.io/posts/2026-09-08-the-seed-was-fixed-and-the-rest-of-the-state-lived-on-the-server.html) the problem was that the variable deciding an agent's behaviour lived outside the request. This is the same omission one layer down: an answer does not carry the age of the facts it used unless you record it. With last-refresh stamps in the retrieval trace, a wrong answer can be classified after the fact as stale or as wrong. Without them, every stale answer gets billed to the model.

**Replace expiry counts with refresh timestamps.** Then, for every zero on your dashboards, ask what else would produce that zero.

**Set TTLs from a change stream.** Count mutations per entity class over a representative period and lay the counts beside the tier table. The rows where data changes faster than its tier width are where staleness will land. In ChurnBench, that was one row.

**Check that your swept variable reaches the thing you are testing** before reading anything into a null. The authors' closing advice for drift evaluations is to hold cache age fixed and sweep the TTL configuration itself.

Their next step is that sweep: tier width across a grid, measured against the staleness-versus-cost trade. The question I would carry back to any operations board in the meantime is simpler. How many of its zeros mean the check ran and found nothing, and how many mean the check never ran?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, the illustrated full-bleed magazine spread rather than a flat-icon spot illustration. Photographic-painterly framing with naturalistic light and depth, clearly art and never photorealistic. A brushed-aluminum, matte-black robot with a single round LED eye stands at a light-oak workshop bench, angled about thirty degrees to the frame, caught mid-action: one hand pulling a small dated card from a long wooden card-catalogue drawer while the other hand hovers over a second drawer that has plainly not been opened in a long time, a thin layer of dust visible on its matte-black handle. Across the bench, three rows of index cards recede into soft focus: the nearest row crisp and freshly stamped with sage-green tabs, the middle row slightly yellowed, the far row faded and curling at the edges, showing three states of freshness at once. In the midground, two identical matte-black analog counter dials sit side by side, both needles resting exactly at zero, one lit by a small sage-green LED and the other with its LED dark and its power cable visibly unplugged and lying loose on the oak. Warm tungsten desk-lamp light around 3200K falls from the upper left across the cards and the drawers; cool 5600K monitor glow washes in from the right, where a slim monitor shows an abstract timeline of small tick marks. An oxblood-bound ledger lies open in the foreground, its pages dense with unreadable rows, and a mug of coffee has gone cold at a diagonal to the robot's gaze. Cables run off-frame to the lower right, pulling the eye in a diagonal sweep. Background: slate-gray wall, a corkboard with pinned printouts, a window with cool morning light upper right, a plant on the sill. Palette warm white, light oak, slate gray, with sage-green and oxblood accents. Mood sharp, deliberate, quiet, watchful, slightly tired but alert, the studio of someone who built the systems and now writes about their failure modes. Modern industrial design throughout, never clockwork, brass, Victorian or steampunk. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
An agent benchmark swept cache age from 1 to 28 days and found nothing. Switch off scheduled refresh and stale answers jumped from 4 to 45. The counter meant to catch expiry read zero in both runs: once because nothing expired, once because nothing checked.

Full piece linked in bio.

#aitooling #aiagents #rag #observability #dataengineering #devops
-->
