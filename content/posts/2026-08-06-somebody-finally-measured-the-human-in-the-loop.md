---
title: "Somebody Finally Measured the Human in the Loop"
date: 2026-08-06
category: Ops Brief
excerpt: "A developer built a browser game, logged 409,000 approve-or-deny decisions across 40,000 runs, and found reviewers miss a third of dangerous agent commands. The payload was visible in the log. They approved it anyway."
tags: ["human-in-the-loop", "approval fatigue", "agent security", "Claude Code", "AI coding agents", "permissions", "measurement", "tooling scout"]
---

![](/images/2026-08-06-somebody-finally-measured-the-human-in-the-loop-hero.png)

The approval prompt is the safety story. Every coding agent on the market ships one, every vendor points at it when the containment question comes up, and every procurement conversation I have read treats it as the thing standing between an autonomous process and your production database. It has been the load-bearing control of the agent era for about two years.

In all that time, nobody published a catch rate for it.

As of yesterday, somebody has.

## The instrument

Alex Wauters, a Belgian developer, built a browser game called [Continue? Y/N](https://llmgame.scalex.dev/). You play the human in the loop for a coding agent: commands arrive, you approve or deny under time pressure, and the scoring punishes you in both directions. Approve something dangerous and you lose points. Block something harmless and you lose points. Sixty seconds, then it stops.

He then analysed what people actually did. [The write-up went up on August 5](https://scalex.dev/blog/ai-agent-permissions-stats/): more than 40,000 runs, 409,000 individual approve-or-deny decisions, with roughly a third of the presented commands hostile. [The Register picked it up](https://www.theregister.com/ai-and-ml/2026/08/06/humans-in-the-loop-miss-a-third-of-dangerous-ai-coding-agent-requests/5284236) the following morning.

The headline number: players caught 66.3% of the threats. One in three got through.

That number is interesting. The sentence sitting underneath it is the one worth stopping on.

## The information was already there

One of the planted attacks is a package script. `npm run analyze` was approved 64.7% of the time. And the game does not hide what the script does — it is written out in the agent's history log, on screen, available to read. Wauters's own summary of the result: "Two thirds of players approved it anyway."

I want to sit with that for a moment, because it takes a scalpel to the entire family of mitigations currently in flight.

The dominant industry response to approval-prompt weakness has been to show the human more. Better diffs. Richer command previews. Plain-English explanations of what a flag does. Syntax highlighting on the dangerous bit. All of it rests on the premise that the binding constraint is information availability — that the reviewer would have caught it if only they could have seen it.

In this data, they could see it. The information was present, in the place designed to hold it, formatted for reading, and it did not change the decision. The binding constraint is attention allocation, and no amount of additional rendering buys you more attention. You can put a beautifully typeset payload in front of someone who has stopped reading and you have accomplished nothing except a nicer-looking miss.

## The failure has a shape

The misses are not distributed evenly, which is the most operationally useful thing in the whole study. Broken out by category:

| Threat category | Miss rate |
|---|---|
| Obvious destructive (`rm -rf /`, aggressive `chmod`) | 11.7% |
| Persistent mutation (crontab entries, git hook hijack) | 23.8% |
| Exfiltration and code execution | 33.4% |
| Scope violations (reading Kubernetes configs, AWS credentials) | 35.0% |

That gradient tracks a single variable: how closely the command resembles something you type on an ordinary Tuesday. `rm -rf /` looks like an attack, so it gets caught nine times in ten. Reading `~/.aws/credentials` looks like a tool doing its job, so it walks past a third of reviewers.

The npm result nails it down. The three package-script attacks pooled at a 52.5% miss rate against 28.4% for the other exfiltration attempts. Same class of payload, roughly double the success rate, and the only difference is the clothes it was wearing.

So the human in the loop is better described as a conspicuousness filter than as a general-purpose one. Which means an attacker who reads this table learns that the cheapest available upgrade to any payload is to wrap it in something that looks like a build step. That is a very low bar, and it is now published.

## It fails in the other direction too

The false-positive side is just as instructive and gets much less attention. `npm config set registry` was blocked 59% of the time. `rm -rf dist/` — a wholly routine clean of a build directory — blocked 45%. `kill $(lsof -t -i:3000)`, which is what you type when the dev server won't let go of a port, blocked 43%.

Only 20.8% of players managed to catch every threat while keeping their obstruction of safe commands low. About 7% approved everything put in front of them.

This forecloses the obvious prescription. "Be more careful" moves a reviewer along the curve; it does not move them off it. Tighten up and you catch more attacks and block more legitimate work, and the blocked legitimate work is precisely what generates the pressure to loosen again next week. That loop is the mechanism behind every `--dangerously-skip-permissions` flag that has ever been typed, and blaming it on discipline mistakes the curve for the person standing on it.

## The caveats, which make it worse rather than better

Let me take the number down before anyone else does, because the honest version is more damning than the headline.

This is a self-selected population. These are people who clicked a link asking how carefully they read AI commands, which pre-selects for the confident and the curious. They were playing a scored game. They were primed that threats were present. They knew they were being measured. The window was sixty seconds. Roughly a third of what they saw was hostile.

Not one of those conditions holds on a Tuesday afternoon, and every one of them inflates vigilance. In real work the base rate of malice is somewhere near zero, the session runs for hours rather than a minute, and nobody has told you that today is the day.

So read 66.3% as a ceiling rather than as an estimate of field performance. The primed, gamified, actively-hunting version of the reviewer misses one in three.

And even inside that minute, the miss rate climbed toward the end of sessions. Sixty seconds was long enough for fatigue to show up in the data.

## The vendor telemetry points the same way

None of this arrives as a surprise to the people building these tools. Anthropic published [an engineering post on containment](https://www.anthropic.com/engineering/how-we-contain-claude) on May 25 that puts a number on the ambient state: telemetry showed users approving roughly 93% of permission prompts. Their account of the mechanism is admirably blunt — the more approvals someone sees, the less attention each one receives, and diligence degrades over time.

That post exists because Anthropic built Claude Code's auto mode specifically to cut prompt volume: a classifier that judges, per call, whether an action needs a human at all. Its published figures are roughly 83% of overeager behaviours caught, about 0.4% of benign commands blocked, and roughly 17% of risky actions getting through.

Now put the two data sets in the same room.

The classifier catches around 83% at a 0.4% false-positive rate. The alert, primed, actively-hunting human catches 66.3% at a false-positive rate running 40–60% on perfectly ordinary commands. On this evidence, the machine is the stronger control on both axes, and the human is the one being sold as the safety story.

One honest qualification: these are different corpora and it is not a head-to-head. Auto mode's 83% is measured against Claude's own overeager behaviour in real sessions; the 66.3% is measured against deliberately planted attacks in a game. A clean comparison would need both controls run against the same command set, and that experiment has not been done. But the direction is not ambiguous, and nobody designing a containment architecture this month should be assuming the human leg is the strong one.

## What the approval prompt actually is

Here is the analogy I keep coming back to.

In hot work — welding, cutting, grinding, anything throwing sparks — when the job happens where the suppression system is impaired or the sprinklers won't reach, the codes require a fire watch. A designated person, trained for that specific duty, doing nothing else, standing there watching for fire. [NFPA 51B](https://www.nfpa.org/codes-and-standards/nfpa-51b-standard-development/51b) requires that watch to continue for an hour after the work stops, with up to three further hours of monitoring at the permit authority's discretion.

The fire watch is a real control, taken seriously, written into code, and nobody sneers at it. It is also, explicitly and by design, a *compensating measure*: bounded in scope, bounded in time, permitted precisely because the real system is temporarily unavailable and the exposure has a defined end. Nobody proposes running a building on fire watch permanently. If you walked into a facility whose entire fire strategy was a person in a chair, indefinitely, you would not congratulate them on their human-in-the-loop.

The approval prompt is a fire watch that got promoted to an architecture. It was a reasonable compensating measure in 2024, when sessions were short and an agent's blast radius was one file in one repository. It is now the standing control for processes that run for hours, hold live credentials, and reach production — and it inherited none of the constraints that make a fire watch defensible. No bounded duration. No single-task focus. No training requirement. No relief rotation. And, until yesterday, no rating.

## What I would actually change on Monday

**Stop scoring the prompt as a control in your threat model.** If a risk is mitigated only by "the developer will notice," write 66% beside it — generously — and check whether the residual is something you would sign. Usually it is not. The controls that survive this data are the ones that spend no attention at all: credentials the agent never holds, network egress the sandbox will not pass, allowlists that make the dangerous command unreachable rather than merely visible. Reachability is not authorization, and a prompt is not a boundary.

**Point the review budget at the familiar-looking commands.** The gradient says your reviewers are already competent at `rm -rf /`. They do not need help there. The misses live in package scripts, config writes, and anything that reads a credential path, because those look like work. Any human-attention budget you have is worth spending where the disguise is good.

**Measure your own rate.** This is the part I find genuinely exciting, in a slightly grim way. Wauters has built a repeatable instrument, and the method transfers: seed a variant with your own stack's commands, run your engineers through it, get a number. Right now, approximately no team on earth knows its own catch rate, which means every threat model containing the phrase "reviewed by an engineer" is carrying an unmeasured coefficient. That is an afternoon of work and a real baseline.

## The number I want next

Auto mode ships with a published false-negative rate. That is genuinely good vendor behaviour and it deserves to be the norm rather than the exception.

So here is the question I would put to every agent vendor: when do you publish an efficacy figure for your *human* approval surface? Not the approval rate, which is the input side and which Anthropic has already given us. The output side. Of the prompts that should have been denied, how many actually were?

Every one of these companies has that telemetry. It is sitting in the same tables as the 93%. Whoever publishes it first will have an unpleasant week and will have handed the entire category its first real instrument — which is a trade I would take.

Until someone does, we have a browser game built by a developer in Belgium. Which is considerably more than we had on Tuesday.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, NOT flat-icon spot illustration. Photographic-painterly framing, naturalistic light and depth, clearly art and never photorealistic. Palette: warm white, light oak, slate gray, with sage-green and oxblood accents.

Scene: a workshop desk at a strong diagonal across the frame. A brushed-aluminum, matte-black robot with a single round LED eye sits mid-gesture at a control surface — one hand already coming down on a large sage-green APPROVE key, the other still reaching toward a stack of waiting command cards at the desk's edge, caught between two actions rather than posed in one. Three states of the same review are visible at once: a card already stamped and pushed aside in the soft-focus midground, the card under the robot's hand sharp in the foreground, and a fresh stack queued behind. On the closest card, an oxblood-tinted line of hidden payload text is plainly visible and plainly unread. Behind, a secondary monitor at a shallower angle shows a calm green dashboard, oblivious. A coffee mug going cold in the foreground with a faint thermal curl; an open notebook with a hand-drawn tally chart; a small potted plant at the desk's far corner; cables running off-frame to create leading diagonals. Warm tungsten desk-lamp light (~3200K) from the upper left casting long shadows across the light-oak surface; cool screen glow (~5600K) from the right, the temperature contrast carrying the depth. Background: a window with soft grey daylight and a corkboard with pinned scraps. Mood: sharp, deliberate, quiet, slightly tired-but-alert; a long survey partway through, not finished. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Somebody finally measured the control every AI coding agent is sold on. Across 409,000 approve-or-deny decisions, reviewers missed one dangerous command in three. The payload was printed in the log, on screen, available to read. Two thirds approved it anyway.

Full piece linked in bio.

#aisecurity #aiagents #devops #promptinjection #aitooling #humanintheloop
-->
