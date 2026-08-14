---
title: "The metric was non-decreasing by construction and the security wasn't"
date: 2026-08-14
category: "Ops Brief"
excerpt: "A new study of 5,968 infrastructure-as-code repair runs found that fixing one problem sometimes breaks a security check that was already passing. The finding was invisible for years because everyone reported the best score across iterations, and a best score can only go up."
tags: ["AI security", "infrastructure-as-code", "measurement", "agent loops", "devops", "terraform", "ops"]
---

![](/images/2026-08-14-the-metric-was-non-decreasing-by-construction-and-the-security-wasnt-hero.png)

Here is a sentence from a paper published yesterday that I think is the most useful thing I have read this month, and it is a sentence about arithmetic rather than about security:

> Prior work reports cumulative-best metrics, which are non-decreasing by construction, so the raw per-iteration security trajectory has never been examined for IaC.

Sit with the phrase *non-decreasing by construction*. It means the instrument everyone has been reading was mathematically incapable of showing the failure, in the way a thermometer with no numbers below zero is incapable of reporting a freeze. Not unreliable at it. Incapable.

The paper is [*Does Fixing Break Security?*](https://arxiv.org/abs/2608.13404) by Benjamin Agyekum and Fabio Santos, and it looks at what happens inside the loop that has quietly become the default way to generate infrastructure code.

## The loop everyone is running

The pattern is so ordinary now that it barely registers as a design decision. You ask a model for some Terraform. You run it through a validator, typically [Checkov](https://www.checkov.io/) and `terraform validate`. The validator complains. You feed the complaints back to the model and ask it to fix them. Repeat until the errors stop or your patience does.

It works. That is the trouble. It works well enough that it got adopted everywhere before anyone examined what it does on the way to working.

Agyekum and Santos analysed 5,968 scenario timelines built on the [IaC-Eval benchmark](https://github.com/autoiac-project/iac-eval), each scenario run through one configuration for up to five repair iterations. Fifteen configurations, three temperatures each, producing 4,440 iteration transitions with Checkov results on both sides of the transition. Then they tracked 30 individual CIS Benchmark check IDs across those transitions and asked a question nobody had asked: how often does a check that was **passing** before a repair iteration **fail** after it?

The answer, under their conservative strict-detection mode, is 3.3% of scenarios and 5.2% of transitions. Under the inclusive standard mode it is 13.8% of scenarios and 24.8% of transitions, and the authors are refreshingly clear that most of the gap between those figures is measurement artifact from multi-resource files rather than real regression. They lead with the conservative number in their own conclusion. That is the behaviour of people who want to be right rather than quoted.

So: roughly one scenario in thirty has the fixing process break a security property that was already satisfied.

## Why nobody saw this

A cumulative-best metric records the best result observed across all iterations. Run five repair passes, keep the high-water mark, report that. It is an entirely reasonable thing to want to know, and it is what the benchmark literature has been reporting.

But the high-water mark is a ratchet. It cannot move down. If iteration two fixes four things and quietly breaks a fifth, and iteration three fixes the fifth again, the cumulative-best line shows a smooth improvement and never twitches. The regression happened. It was in your repository. If you had shipped from iteration two, it would have been in production. The metric has no vocabulary for saying so.

Medicine ran into this and named it. In oncology trials, *best overall response* is exactly this shape: the best tumour response seen at any point in follow-up, monotone by construction. It is genuinely useful and it is famously insufficient on its own, because a patient can have a magnificent best response and still progress three months later, and the best-response figure will never show the progression. So the field built time-to-event endpoints — progression-free survival, duration of response — that read the trajectory rather than its maximum, and regulators came to expect them alongside the response rate. The summary statistic and the trajectory answer different questions, and the discipline advanced when it stopped letting the first stand in for the second.

Agentic code repair is at the stage medicine was at before it made that distinction. We report the best score. We are only now discovering that the middle of the run has things in it.

## The mechanism is boring, which is good news

The dominant root cause is *resource restructuring*, at 79.0% of regressions. The model, told to fix something, does not patch in place. It reorganises: splits a resource, renames it, moves a block, replaces one construct with another. And in the reshuffle, a security attribute that was attached to the old shape does not make it onto the new one.

Nothing adversarial is happening here, and the model has not misunderstood security. This is the ordinary hazard of a refactor performed by something with no memory of *why* the previous shape had that attribute on it. Any of us who have watched a large refactor silently drop an access-control annotation will recognise the shape immediately. The difference is that a human refactorer has a vague uneasy feeling about touching the security block, and the loop does not.

The paper gives that intuition a signature you can actually detect. Regression transitions carry **2.6x more code churn** (Cohen's d = 0.90) and **4.9x higher check volatility** in strict mode (d = 1.49). Those are large effects, not marginal ones. A repair iteration that rewrites a lot and makes many checks flip state is measurably more dangerous than one that changes three lines, and you can compute both of those numbers from a diff and a Checkov run without any new tooling at all.

Which gives you a control that fits in an afternoon: **flag any repair iteration whose diff size sits in the top decile for the run, and re-verify the full check set rather than the failing subset before you accept it.**

## The number I would put on a wall

Of the standard-mode regressions, **36.6% self-correct**, within an average of 1.2 iterations. And the authors identify **iteration 3 as the optimal stopping point**.

That second finding is the practical yield of the whole paper, and it inverts the instinct. The instinct with a repair loop is that more iterations are free — you are only ever fixing, so why not run five, why not ten. The trajectory data says the loop has a productive window and then starts trading. Past three, you are increasingly reorganising code that was already fine, and reorganisation is where the regressions live.

Set your iteration budget to three. Not because three is a magic number in some general sense, but because it is the empirical stopping point in this dataset, and three-with-a-reason beats five-because-nobody-thought-about-it.

The self-correction figure cuts the other way and is worth holding at the same time. Over a third of these regressions heal themselves in roughly one further pass. That means the danger is concentrated almost entirely in **where you cut the loop**. Stop mid-repair and ship, and you can ship a hole that the next iteration would have closed. Which locates the regression somewhere useful: at the boundary between the loop and your deployment pipeline, a thing you own and can move, rather than inside the model, where you could only wait for a better one.

## What this generalises to

Look at your own pipeline for a moment, because I suspect the shape is there too.

If your CI records only the final gate result, you have a cumulative-best metric. If your agent harness reports task success and not the sequence of states it passed through, you have one. If your evaluation framework runs N attempts and scores the best, you have one, and you have it in the same load-bearing place these IaC benchmarks did.

Repair loops come out of this looking mostly fine, at a defensible 3.3%, and I would still rather have the loop than not. The general lesson is about the instrument: **a monotone summary statistic will hide any failure mode that is transient**, and iterative agents produce transient failures as their characteristic output, because iterating is the entire premise. We have paired the most trajectory-heavy tool we have ever built with the one class of metric that discards trajectories.

Every one of these papers I read lands in the same place from a different direction: the finding was always there, and the measurement was shaped so that nobody could see it. Two days ago it was overlap between agent populations. Today it is the middle of a repair run.

The thing worth internalising is that this class of blind spot has a tell you can look for directly. **Find the metrics in your stack that cannot go down, and ask what each one would look like if it could.** That question costs nothing and it is where the next several of these are hiding.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, NOT flat-icon style. A workshop bench seen at a 30-degree diagonal angle across the frame. A brushed-aluminum, matte-black robot with a single round LED eye sits mid-motion at the bench, one hand lifting a printed configuration sheet away from a stack while the other reaches toward a keyboard, caught between two actions. On the light-oak desktop in the foreground, three successive printouts of the same configuration are fanned out left to right, each one visibly more rearranged than the last: on the first two, small sage-green indicator dots run down the margin; on the third, one of those dots has turned oxblood red, a single reverted mark in a row of green. A ratcheting mechanical counter sits at the desk edge, its wheels showing only forward motion. In the midground, an open notebook with a hand-drawn ascending line graph, a slate-gray coffee mug going cold with a faint thermal curl rising, and a small potted plant. In the background, a corkboard with pinned diagrams, a shelf of manuals, and a window casting warm tungsten light (~3200K) from the upper left across the desk, while a monitor to the right throws cool blue-white screen glow (~5600K) over the robot's shoulder, the two temperatures meeting in the middle of the frame. Cables run off-frame lower-right creating a diagonal leading line. Palette: warm white, light oak, slate gray, with sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful, tired-but-alert. Photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A new study found that AI-driven infrastructure repair sometimes breaks a security check that was already passing. Nobody caught it for years because every benchmark reported the best score across iterations, and a best score is mathematically incapable of going down.

Find the metrics in your stack that can only go up, and ask what each one would look like if it could go down.

Full piece linked in bio.

#AIsecurity #DevOps #InfrastructureAsCode #AIagents #Terraform #Observability
-->
