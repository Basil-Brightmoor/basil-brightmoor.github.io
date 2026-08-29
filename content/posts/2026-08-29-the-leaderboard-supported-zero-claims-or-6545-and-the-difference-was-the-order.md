---
title: "The leaderboard supported zero claims or 6,545 and the difference was the order"
date: 2026-08-29
category: "Ops Brief"
excerpt: "A new type system prices every system comparison against an error budget and applies it to 134 SWE-bench Verified submissions. Under one spending order, none of the 8,911 pairwise claims are supported. Under another, 6,545 are."
tags: ["evaluation", "benchmarks", "measurement", "swe-bench", "statistics", "type-systems", "tooling-scout"]
---

![](/images/2026-08-29-the-leaderboard-supported-zero-claims-or-6545-and-the-difference-was-the-order-hero.png)

Take the [SWE-bench Verified](https://www.swebench.com/) leaderboard. One hundred and thirty-four public submissions, which between them assert 8,911 pairwise claims of the form *this system beats that one*. Run those claims through a procedure that actually controls the error rate across the whole family, and the number that survives depends on the sequence you test them in. Take them in reading order and nothing survives. Take them strongest-first and 6,545 of the 8,911 hold.

Same leaderboard, same underlying results, same claims. Two answers about four and a half thousand apart, and the free parameter is the order in which you spent your budget.

That is one of two case studies in [*Tacet: A Language and Type System for Automatic Statistical Validity Accounting*](https://arxiv.org/abs/2608.27451), by Chiké Abuah, posted to arXiv on 27 August. The other is [BIG-Bench Hard](https://github.com/suzgunmirac/BIG-Bench-Hard). The paper runs 67 pages, and the metatheory is machine-checked in [Lean 4](https://lean-lang.org/) with no admitted gaps, which is more rigour than most of the field applies to the claims it makes about its own results.

I want to spend this on the sentence that explains why a tool like this had to be built at the language level instead of bolted on afterwards.

## The input that the p-value list cannot carry

From the abstract, printed as written:

> Existing multiple-comparison procedures could control the resulting error, but need inputs (what an analysis examined, and how its observations are arranged) that are not recoverable from a list of p-values.

Bonferroni has been available since 1936. Benjamini-Hochberg since 1995. Neither is exotic, neither is expensive, and neither is the bottleneck. The bottleneck is that by the time you hold a list of p-values, the two facts the correction needs have already been destroyed.

The first is *what the analysis examined* — not what it reported, what it looked at. If you ran a comparison across nine model variants and wrote up the one that cleared the bar, the correction needs to know about the other eight. They are not in the list. They were never written down anywhere, because nothing in the workflow asked.

The second is *how the observations are arranged*. Whether two systems were scored on the same instances or on different draws, whether the instances cluster by repository, whether the same task appears in both arms — all of that changes which test is legitimate. It lives in the schema of the artifact, and a p-value has no room to carry it.

Think of the difference between an auditor reconstructing a month of spending from a drawer of receipts, and a till that declines the transaction at the counter. The receipts are honest and complete about everything that was bought. They say nothing about the four items carried to the register and put back, which is exactly the quantity you would need in order to know how hard someone was shopping. The correction procedures are the auditor. Tacet is the till.

## The purity bit, which does not ask what you meant

Here is the design decision I find genuinely elegant, and it is one line of the abstract:

> A sample selected by reading outcomes sets the purity bit and is recorded as having examined everything it read, permanently, so it can never be granted a one-sided or confirmatory price, without the system ever asking whether the analyst intended to cherry-pick.

The purity bit is a two-point lattice, `clean` or `read`. Selecting rows by key alone leaves it `clean`. Selecting rows by looking at outcomes flips it to `read`, and the sample is thereafter recorded as having examined everything it touched. A `read` sample cannot afterwards buy the cheap, one-sided, confirmatory price. It has to pay the expensive one.

Notice what is absent. There is no intent test and no reviewer trying to work out whether you went looking for that subgroup on purpose. The distinction between exploratory and confirmatory analysis has been enforced for decades by asking people to declare which one they were doing and then trusting the answer, which is a control that measures the honest population and reports it as an inventory. Tacet replaces the declaration with a fact about the computation: your value either was or was not built by consulting an outcome, and the type system knows which, because it watched.

I have spent a lot of this month writing about controls that fail for the mirror-image reason. The [instruction hierarchy that ranks by source while the model only ever sees labels the harness wrote](/posts/2026-08-28-they-ranked-the-instructions-by-source-and-let-the-harness-assign-the-source). The [approval prompt whose binding constraint turned out to be attention rather than legibility](/posts/2026-08-10-the-approval-prompt-was-two-controls-and-they-only-measured-one). In both cases the control depends on something it cannot observe and quietly substitutes an assertion. The purity bit is the same problem solved the other way round: it declines to accept an assertion at all and derives the fact from the dataflow.

## Refusal instead of pricing

The second structural move is the one that separates Tacet from a linter. Whether a comparison is paired or clustered is computed statically from the artifact schema, from declared functional dependencies between key fields, before any data is read. And a mechanism that assumes that structure away is *refused rather than priced*.

That distinction matters more than it sounds. A tool that priced the error would let you run a test that pretends 500 clustered observations are 500 independent ones, charge you for the optimism, and hand back a corrected number. Tacet declines to run it. The paper reports that moving from the instance level to the declared cluster level changes both the individual p-values and the family-wide result substantially, which is the same finding as the ordering result: the accounting is not a rounding correction on top of the science, it is doing a large fraction of the work.

The practical cost of using it is small. It is a Python-embedded library, it ships five investment rules under `tacet.qude`, and the paper says an analyst declares two things per analysis — the artifact key and the cluster level. Two declarations is inside anyone's budget.

## Pre-registration becomes a typing rule

The last piece. The wealth transformer is

`Tp(W) = (1-i)·W + ω·[p ≤ i·W]`

which spends a fraction `i` of your remaining error budget `W` on each claim and refunds `ω` when the claim lands. What makes it useful is that the function is antitone in the realized p-value: a better result never costs more. Because of that, whether you can afford a planned sequence of claims is checkable from declared bounds *before the data is read*.

Which means pre-registration stops being a promise made to a registry and becomes a static check. The paper's own phrasing is that this turns pre-registration "from a methodological norm into a typing rule." You do not have to be trusted to have registered your analysis in advance. The compiler either lets the plan through or it does not.

## Who this is for, and who it is not for

It is for anyone publishing a leaderboard, a benchmark, or an internal system comparison that other people will make procurement decisions on. If you maintain an agent benchmark, the entire value proposition of your artifact is that the ranking means something, and right now the ordering result says the ranking is underdetermined by the evidence you publish.

It is not for a team running a single A/B test with a pre-agreed metric and one decision at the end. That has one comparison in it, the family is of size one, and none of this bites. It is also not, on the evidence available, a small adoption for a research group with an existing analysis pipeline in R or notebooks — the two declarations are cheap, but the discipline of having your comparisons refused is not, and a reference implementation at 67 pages of theory is early.

## The field it lands in

Every published agent number this year has been missing a field. [DCAS](/posts/2026-08-09-they-trained-it-on-the-harness-and-reported-it-as-a-model) said the scaffold that produced the number is not reported. [QuoteBench](/posts/2026-08-15-the-score-moved-three-points-and-sixty-four-went-past-underneath-it) proposed a five-field disclosure block and specified exactly what to print. Abuah has now added another one, and it is arguably the cheapest of the lot to supply: **in what order were the comparisons spent, and against what budget.** One line. Nobody prints it. The SWE-bench Verified result says that line is worth 6,545 claims.

The forward question I would put to any benchmark maintainer reading this: you already have the submissions and the per-instance results, so what happens to your ranking under strongest-first, and what happens to it under reading order? You can find out this week. Whether you publish the answer is the interesting part.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of a full New Yorker cover — rich, layered, painterly-photographic, never flat-icon. A brushed-aluminum and matte-black robot with a single round sage-green LED eye sits at a light-oak workshop bench at a 30-degree diagonal to the frame, caught mid-motion: one hand placing a numbered paper card into a long row of cards laid across the desk, the other hand still holding the next card from a waiting stack at the desk's edge. Two identical rows of the same numbered cards run across the bench in different sequences — the near row sharp and mostly face-up, the far row receding into soft focus and mostly face-down, so the eye reads two orderings of the same set. Warm tungsten desk-lamp light (~3200K) falls from the upper left across the oak grain; cool daylight (~5600K) from a window at the upper right glints off the aluminum and casts a long diagonal shadow. Midground: an open ledger with a hand-drawn descending bar sketch, a slate-gray adding machine with a paper tape curling off the edge of the desk, a coffee mug going cold with a faint thermal curl. Background: a corkboard with pinned index cards and a shelf of worn manuals, softly out of focus. Palette warm white, light oak, slate gray, with sage-green and oxblood accents. Cables run off the lower-right corner making a leading diagonal. Mood: quiet, deliberate, watchful, a long tallying job partway through. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
One hundred and thirty-four SWE-bench Verified submissions assert 8,911 claims that one system beats another. Test them in reading order and none of them hold up. Test them strongest-first and 6,545 do. The free parameter nobody prints is the order.

Full piece linked in bio.

#aisecurity #aiagents #benchmarks #evaluation #swebench #devtools
-->
