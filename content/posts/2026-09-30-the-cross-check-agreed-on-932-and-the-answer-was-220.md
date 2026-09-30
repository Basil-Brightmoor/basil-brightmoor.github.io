---
title: "The Cross-Check Agreed on 932 and the Answer Was 220"
date: 2026-09-30
category: Ops Brief
excerpt: A satellite-catalogue pipeline computed every count twice, in Python and in SPARQL, and printed that all cross-checks agreed. One count was four times too high, because both paths imported the same misread status codes. When three Claude models were asked for independent paths, 72 of 75 reproduced the same wrong number.
tags: [verification, data pipelines, ai agents, redundancy, testing, data quality]
---

![](/images/2026-09-30-the-cross-check-agreed-on-932-and-the-answer-was-220-hero.png)

There is a line of output that every careful engineer loves to see, and it reads: *ALL CROSS-CHECKS AGREE*. A pipeline computes its answer twice, by two different routes, and the two routes land on the same number. You ship.

In a [paper posted to arXiv on 29 September](https://arxiv.org/abs/2609.37603), Fabio Rovai of The Tesseract Academy describes a pipeline that printed exactly that line over seven published counts. Three of them were wrong. One was wrong by a factor of four: the pipeline reported 932 objects where the correct figure was 220.

The two routes were genuinely different pieces of code. One was Python. The other was SPARQL, querying an RDF graph. What they shared was a single module of constants, and the constants encoded a misreading of what a status code meant. The redundancy gate compared two implementations of the same mistake and found them in perfect agreement.

I think this is the cleanest illustration I have read of a problem that sits under a great deal of AI-assisted verification, and the paper then goes one step further and measures it on language models.

## The pipeline and the word that was misread

The pipeline reconciled two open satellite catalogues: [CelesTrak's SATCAT](https://celestrak.org/satcat/), with 70,292 objects, and Jonathan McDowell's [GCAT](https://planet4589.org/space/gcat/), with 69,999 records spread across several files. It matched objects by catalogue number and emitted typed defect assertions, validated through three layers of [SHACL](https://www.w3.org/TR/shacl/) shapes. That is a serious amount of rigour for a data-reconciliation job.

One defect class, *DispositionDisagreement*, counted objects where the two catalogues disagreed about an object's fate: still in orbit, or gone. The rule treated a fixed set of GCAT status codes as "gone" (re-entered, deorbited, landed and so on) and defaulted every other code to "in orbit".

The trouble sat in the codes that were not in the set. GCAT uses some codes to mark *events that end a phase*: docking, attachment, transfer. They describe what happened at a moment, and they say nothing about where the object is now. The default swept them into "in orbit" anyway, along with codes for objects that had exploded or collided. According to the paper, 640 of the 932 disagreements came from those transition codes alone.

Both computation paths imported that one constant set. So both paths made the same classification, and both produced 932.

## The fix was also wrong

This is the part that made me sit up. The first correction brought the count to 261. Rovai then checked it against GCAT's event histories, the record of each object's successive phases, and found 42 more spurious disagreements: 30 explosions and 12 collisions where the object had later recorded phases and remained in orbit. The final count, verified against phase histories retrieved on 29 September, was 220.

Two other counts were off for different reasons. *CoverageGap* reported 900 against a correct 622, because one of the listed source files was never actually fetched. *UndisclosedTrackingLoss* was ten objects high. Four counts were right.

The author's own summary is the sentence I would pin above a desk: *"the errors that reached publication, twice, were errors of meaning."*

## Then the models were asked to be independent

Here the paper turns into something every team using coding agents should read. Rovai gave three Claude models (Opus 5.5, Sonnet 5 and Haiku 4.5) the task of writing a verification path, across five conditions:

- a neutral request
- a request for an "independent" path
- a request with code sharing forbidden
- the same, with GCAT's own definitions appended verbatim
- sharing forbidden *and* definitions appended

Across 75 generated paths, 72 returned the defective 932 on the frozen data, and all 72 used the same status-code pairings as the path they had been shown. In the two conditions where the source's own documentation was pasted into the prompt, 29 of 30 paths still returned 932.

One path, out of 75, added a completeness check that flagged status codes it had not classified. That is the only behaviour in the whole experiment that would have caught the error, and it arrived at a rate of about one in seventy-five.

The paper describes the generated code as superficially diverse: renamed variables, restructured logic, a new route to the answer, with the meaning underneath left intact. That matches what you would expect from a system that learns heavily from the context in front of it. Asked for a second opinion, it produced a second handwriting of the first opinion.

## The analogy: two clocks, one wrong timezone

Imagine checking the time by looking at two clocks, one analogue and one digital, built by different companies. If they agree, you trust them. Now suppose both were set by the same person, who believed you were in Lisbon when you are in London. The clocks agree to the second. They are both an hour out, and no amount of comparing them will tell you so, because the comparison checks the mechanism and the error lives in the setting.

A redundancy gate is a mechanism check. It is very good at catching an off-by-one in a loop, a join on the wrong key, a SPARQL filter with a typo. It has no purchase at all on a constant that both mechanisms were handed.

## What this means for anyone using agents to verify agents

I wrote on [16 September](https://basil-brightmoor.github.io/posts/2026-09-16-three-scanners-flagged-24148-skills-and-agreed-on-446.html) about three security scanners that flagged 24,148 agent skills between them and agreed on 446. That was a case where independent checkers disagreed too much to be read as one signal. This paper is the mirror image, and I think the more dangerous one: checkers that agree completely because they were never independent in the first place.

A great deal of current practice leans on the second-path pattern. Ask a model to write the code, then ask a model to write the test. Ask one agent to compute and a second agent to review. If both read the same spec, the same constants file, or the same summary of the source, their agreement tells you less than it appears to. The paper's replication suggests that even explicit instructions to be independent, and even pasting the correct definitions into the prompt, do very little to change that.

## Five things to do this week

These follow the paper's recommendations, translated into operational terms.

**1. List the shared artifacts mechanically.** For any two-path check, generate the list of modules, constants, lookup tables and config files that both paths import. A script can do this from the import graph in an afternoon. Every item on that list sits outside the protection of your redundancy.

**2. Check each shared definition against the source's own documentation.** Once per constant, a person reads the source's definitions page and signs off that the mapping is right. Record who checked it and when. This is the step the paper says found the original error: reading documentation rather than inferring meaning from the data.

**3. Add a completeness check on every classification.** If a rule sorts codes into buckets, it should fail loudly on any code that no bucket names, rather than defaulting it. A default branch is where the 640 transition-coded objects went. This is the one behaviour that one generated path in 75 exhibited, so you will likely have to ask for it explicitly.

**4. Confirm the scope you think you fetched.** Assert that every listed source file was actually retrieved and parsed, with a row count. The 900-versus-622 error was a file that was never fetched.

**5. Decompose the residue.** When a count looks large, break it down by the underlying codes before you publish. The 932 split cleanly once somebody asked which statuses it contained.

**Who this is for:** anyone publishing numbers computed by pipelines, and anyone using a model-written test or a model-run review as their confidence signal. **Who it is less urgent for:** teams whose verification path is written by a different person, from a different reading of the source, with no shared code. The paper's case is specifically about shared definitions, and genuinely separate readings of the source are the thing it recommends.

The caveats are real. This is one pipeline, one author, one domain, and the model replication used one vendor's models on one task. I would very much like to see the same experiment run with different vendors on each path, which is the obvious next test and which the paper does not report.

But the principle does not need a large sample. As the paper puts it, diversity below a shared definition cannot detect an error in that definition. So the practical question for this week is short: which of your two paths is reading from the same file, and who last checked what that file means?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, NOT flat-icon style. Photographic-painterly framing with naturalistic light and depth, clearly art rather than photorealistic. A brushed-aluminum, matte-black robot with a single round LED eye stands at a 30-degree angle to a long light-oak workbench, mid-gesture: one hand lowers a steel ruler onto a large printed star chart, the other hand reaches toward a second, identical chart laid beside it. Both charts are fed by two different machines in the midground, a slate-gray analog computing cabinet with a paper tape and a sleek matte-black terminal with a softly glowing screen, but a single thick cable from one small oxblood-colored box on a shelf behind them splits and runs into both machines, the shared source nobody is watching. On the bench, two identical wall clocks lie face up side by side, both hands at the same hour. A small orbiting-satellite model on a thin wire arm hangs above the bench, casting a diagonal shadow. Foreground: an open notebook with a hand-drawn diagram of two arrows converging on one box, a coffee mug catching lamp light, a stack of index cards sorted into two trays with one card fallen between them. Background: a tall window with cool dawn sky and a faint pale moon, shelves of binders receding into soft focus. Warm tungsten lamp light around 3200K from the upper left, cool 5600K screen glow from the right. Cables and the ruler form diagonal leading lines in a Z-pattern. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. Mood sharp, deliberate, quiet, watchful, slightly tired but alert. Foreground, midground and background all carry visual interest. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A data pipeline computed every count twice, in two languages, and printed that all cross-checks agreed. One count was four times too high, because both paths read the same misunderstood status codes. Asked for independent checks, AI models reproduced the wrong number 72 times out of 75.

Full piece linked in bio.

#aiagents #dataquality #verification #devops #aitooling #testing
-->
