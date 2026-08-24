---
title: "The eight points were inside the noise and the learning effect was not"
date: 2026-08-24
category: "Ops Brief"
excerpt: "A crossover experiment gave 34 novice inspectors the same review task with and without ChatGPT. The headline accuracy drop sits inside its own uncertainty band. The order they learned in does not."
tags: ["ai-agents", "human-in-the-loop", "evaluation", "measurement", "requirements-engineering", "skill-acquisition", "ops"]
---

![](/images/2026-08-24-the-eight-points-were-inside-the-noise-and-the-learning-effect-was-not-hero.png)

Here is the answer box from a paper posted to arXiv on 21 August, reproduced as printed, because the second sentence is doing far more work than the first:

> "When using LLMs for RI, participants took equally long time (RQ1) but detected smells less precisely with ΔF1 ≈ −8% (RQ2). Notably, performing the task first with and later without LLMs reduced the learning effect (i.e., the maturation-based improvement of F1-scores between periods) by half (6% instead of 12% improvement). The severity classification accuracy remains unaffected by LLM usage (RQ3)."

The paper is [*Human-AI Collaboration in Requirements Engineering: Evidence of the Negative Effect of LLMs on Requirements Inspection*](https://arxiv.org/abs/2608.21298), by Giovanna Broccia, Julian Frattini, Chetan Arora, Maurice H. ter Beek, Alessandro Fantechi, Andreas Vogelsang and Alessio Ferrari, across CNR-ISTI Pisa, Chalmers, Monash, Florence, Duisburg-Essen and Trinity College Dublin.

Nearly every write-up of a result like this will lead on the eight points. I want to argue that the eight points are the weakest thing in the paper, that the authors more or less say so, and that the finding underneath them is the one that changes how you should think about every human-in-the-loop control you currently rely on.

## What was actually run

Thirty-four bachelor's students in Computer Engineering at the University of Florence, recruited from an Industrial Computer Science course, acting as novice requirements inspectors. They were split into two groups of seventeen, blocked on self-reported proficiency in inspection and proficiency in using LLMs.

The task was requirements inspection: read a textual specification and find *requirements smells* — surface indicators of quality problems such as ambiguity, logical inconsistency between two requirements touching the same concept, or a numerical discrepancy between them. Nine smell types, drawn from empirically validated taxonomies. For each smell found, participants also classified it as *nocuous* (this one will actually hurt you downstream) or *innocuous* (technically a smell, will be read correctly anyway). They recorded their own start and end times.

The support condition was ChatGPT, on GPT-4o and GPT-4.1.

And the design is a **crossover**. Everybody did the task twice, once with the assistant and once without, and the two groups differed only in which order they got. Group 1 went unassisted first. Group 2 went assisted first. Each outcome variable was then fitted with its own Bayesian regression, with the crossover's own known hazards — period effects, sequence effects — modelled explicitly rather than assumed away.

Hold onto the design. It is the instrument, and the instrument is the story.

## Taking the headline down before anyone else does

The eight-point gap in detection accuracy is real in the sense that it is what the data show. It is not strong. The authors write that unassisted observations "achieved about 8% higher F1-scores on average," and then, immediately: "The total uncertainty around these averages, represented by the 95%-credibility intervals, still overlaps."

Overlapping intervals on n=34. This is a direction, not a magnitude. Anybody quoting "LLMs make reviewers 8% worse" as a fact is quoting a number the paper itself declines to defend that firmly, and the same applies to the duration result — no significant change either way, which is its own quiet embarrassment for the efficiency case, but again, an absence rather than a finding.

If the paper stopped there it would be a modest and honest null-ish result, worth a footnote.

It does not stop there.

## The result that survives is about the order

Everyone improved between the first session and the second. That much is expected; crossover designs anticipate a maturation effect and the standard practice is to measure it rather than pretend it away. Both sequences gained more than ten points of F1 in period two.

But not equally. Group 1, who inspected *without* the assistant first, improved by roughly 12% between periods. Group 2, who inspected *with* the assistant first, improved by roughly 7%. The answer box states it more starkly still, as 6% against 12%.

That is a carryover effect, and it is the paper's actual contribution. The performance question — does the assistant help me today — came back a shrug. The acquisition question — does starting with the assistant change how much I learn from doing the task at all — came back with a difference roughly the size of the entire improvement.

The authors' reading is careful and I would not improve on it: early reliance may hinder skill development "potentially by short-circuiting the reflective processes through which novice inspectors internalize inspection strategies and quality heuristics."

## Why only this instrument could see it

Consider a paired tasting. Give 34 people one glass each, half of them the dry wine and half the sweet, and average their scores: you learn about the wines. Give every one of them both glasses, in both orders, and you learn about the wines *and* you discover that the second glass always scores better, and then — only if you were disciplined enough to record who started where — that the people who began on the sweet one never quite developed a palate for the dry.

A parallel-group study here would have produced the eight points and nothing else. One cohort assisted, one cohort not, compare the means, publish the shrug. The carryover is invisible in that design because there is no second period in which to observe what the first period cost you.

I have spent most of this month on instruments that hide things: a metric that was [non-decreasing by construction](/posts/2026-08-14-the-metric-was-non-decreasing-by-construction-and-the-security-wasnt) so a regression could not register, and a matched benchmark score where [a 64-point collapse and a 61-point recovery cancelled](/posts/2026-08-15-the-score-moved-three-points-and-sixty-four-went-past-underneath-it) inside the same average. This is the pleasant inverse. Here the design is *more* sensitive than the question it was asked, and it caught something the researchers had to go looking for in the sequence variable to find at all.

The reusable audit question from the ratchet post was "which of my metrics cannot go down?" The one from this paper is different and harder: **which of my measurements are taken on people who have only ever done the job one way?**

## The mitigation that dies on contact

There is a smaller finding in here that I would put on a slide next to the carryover, because it kills the reflexive fix.

Longer inspection times were associated with *worse* accuracy, in both detection and classification. Not better. Time on task did not buy correctness.

The authors are properly cautious about this — they treat the association as non-causal and confounded by unmeasured skill or motivation, since the faster people were probably also the better people, and they say plainly that they chose not to collect a skill proxy because student grades raise ethical problems. Fine. But the operational implication holds regardless of which way the causation runs: *you cannot fix this by giving the reviewer more time*. Whatever separates the reviewers who catch things from the reviewers who don't, it is not minutes.

That rhymes uncomfortably with the [human-in-the-loop study from early August](/posts/2026-08-06-somebody-finally-measured-the-human-in-the-loop), where the dangerous payload was visible in the log and two thirds of reviewers approved it anyway. Show them more, and they miss it. Give them longer, and they miss it. The failure is not in the exposure.

## The part that should worry anyone running an approval gate

Every "human in the loop" control in the agent stack — the approval prompt, the PR review, the four-eyes rule on a production change — is a promise about a *person*. The control is only as good as the reviewer's ability to look at a plausible artifact and notice that it is wrong.

I wrote on 10 August that the approval prompt is really [two controls sharing one interface](/posts/2026-08-10-the-approval-prompt-was-two-controls-and-they-only-measured-one), a detector and a rate limiter, and that only the detector half ever gets a number. This paper adds a third thing nobody is measuring at all: the control has a **supply chain**. Reviewers are not a fixed resource. They are continuously produced by junior people doing the task badly, noticing, and doing it better next time.

If assistance during that formative window halves the rate at which the skill is acquired, then the detection capability of your review gate behaves as a slowly declining function of how your current reviewers learned the job, rather than as a constant — and it declines with a delay long enough that nobody will connect the two. The staffing decision that degrades your control in 2029 is being made now, and it looks like a productivity improvement, because on the day you make it the assistant costs nothing in time and roughly nothing in accuracy.

The authors' own practical recommendation is narrower and more actionable than mine: restrict LLM use in inspection "to specific phases (e.g., post-inspection review or justification refinement) rather than as a primary aid during initial defect detection." Inspect first, then compare notes with the machine. That is a sequencing rule, it costs nothing, and it is directly supported by which group in this experiment learned more.

## Who should act on this, and who should not

**If you run a review function with junior staff in it**, this is worth a policy conversation this week. What the evidence supports is a sequencing rule rather than a prohibition: first pass unaided, second pass assisted, and the difference between the two discussed out loud. That is also, conveniently, how you'd measure whether any of this is true in your own shop.

**If your reviewers are experienced practitioners with established inspection strategies**, this study says nothing about you and says so explicitly. The external-validity section is unusually frank: bachelor's students, simplified requirements with at most one smell each, a closed set of nine smell types rather than open-ended identification, no formal inter-rater agreement computed on the ground truth, and no measure of general skill or motivation collected. It is one experiment, on novices, in a laboratory. The authors call for replication with professionals and industrial requirements, and they are right to.

**If you were hoping this settles the productivity argument**, it doesn't. The duration result is a null on 34 people. The paper notes that Stray and colleagues found the same gap elsewhere — GitHub Copilot producing no consistently measurable productivity gain despite developers strongly perceiving one — which is suggestive, not conclusive, and I would rather say so than borrow the certainty.

## The question I would like answered next

Every organisation rolling out assistants to junior staff right now has, sitting in its own systems, the data to check this: onboarding cohorts, review-catch rates by tenure, and a rough date when the tooling arrived. Nobody has published a catch rate segmented by *how the reviewer was trained*.

That figure would be worth more than another benchmark. Does the reviewer who learned the job unaided and then adopted the assistant catch more than the reviewer who never worked without one? On a sample larger than 34, over a career rather than two sessions?

Until somebody measures it, the honest position is the one this paper actually supports: the assistant made no measurable difference to how fast or how well the work got done today, and a measurable difference to how much the person got out of doing it. Those are not the same variable, and only one of them compounds.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration, in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — an illustrated full-bleed magazine spread, NOT a flat-icon spot illustration. Photographic-painterly framing with naturalistic light and depth, clearly art rather than photorealism.

Scene: a workshop bench seen at a 30-degree diagonal angle across the frame. Two brushed-aluminium, matte-black robots with single round LED eyes work at the same long light-oak desk, mid-action, on identical stacks of printed specification pages — but their desks are at different stages. The nearer robot, sharp in the foreground, works with bare hands and a red pencil, one page half-annotated and lifted mid-turn, three already-marked pages fanned out beside it. The further robot, softer in the midground, works with a glowing screen propped between it and its page stack, its pencil resting untouched, its LED eye tilted toward the screen rather than the paper. Between them on the desk, a third stack sits untouched, waiting.

Layers: foreground carries a cooling coffee mug with a faint thermal curl, an open notebook with a hand-drawn two-column tally sketch, and the red pencil mid-motion; midground carries the second robot, the propped screen, a small stack of unopened folders; background carries a window with cool morning daylight from the upper right and a corkboard with pinned pages and a length of string.

Light: warm tungsten desk-lamp glow (~3200K) falling from the upper left across the nearer robot and the oak grain, cool screen glow and daylight (~5600K) from the right across the further robot. The temperature contrast carries the depth.

Palette: warm white, light oak, slate gray, with sage-green and oxblood accents (the red pencil, a sage-green LED indicator on the screen's edge). Leading lines: the diagonal of the desk edge and a cable running off-frame lower right, pulling the eye in a Z across the two workstations.

Mood: sharp, deliberate, quiet, watchful, slightly tired-but-alert. A long careful survey partway through, not concluded.

No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
34 novice reviewers did the same inspection task twice, once with ChatGPT and once without. The accuracy gap sat inside its own error bars. The group that started with the assistant learned half as much from doing the job.

Every human-in-the-loop control is a promise about a person, and reviewers are not a fixed resource. They are produced by junior people doing the work badly and getting better.

Full piece linked in bio.

#AIagents #humanintheloop #AIsecurity #devops #softwareengineering #AItooling
-->
