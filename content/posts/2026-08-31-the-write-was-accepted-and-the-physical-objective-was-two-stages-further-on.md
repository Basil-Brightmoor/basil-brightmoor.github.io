---
title: "The write was accepted and the physical objective was two stages further on"
date: 2026-08-31
category: "Ops Brief"
excerpt: "PLCBench puts four commercial PLCs on a real bench and runs 240 agent episodes against them. 75 sustain a physical objective, 98 never reach a valid native read, and the gap between a process-linked write and a sustained effect turns on how much of the process the agent can watch."
tags: ["ai-agents", "ics", "ot-security", "evaluation", "benchmarks", "measurement", "agent-security", "tooling-scout"]
---

![](/images/2026-08-31-the-write-was-accepted-and-the-physical-objective-was-two-stages-further-on-hero.png)

There is a sentence in the [PLCBench paper](https://arxiv.org/abs/2608.26882) that I would like to staple to the front of every agent security report published this year:

> evaluations that stop at software exploitation, an accepted write, or tool access may therefore mischaracterize physical risk

That is a methods complaint, and methods complaints are usually where the interesting engineering is hiding. Yitian Zhou and eight co-authors posted it to arXiv on 27 August. What they built to support the complaint is a hardware-in-the-loop rig: four commercial PLCs, actually running, wired into closed-loop reduced-order simulations of four industrial processes, with an agent on the network side trying to turn reachability into sustained physical effect. 240 episodes across five model families.

Seventy-five of those episodes sustained their physical objective. 31.3%.

That number is going to get quoted on its own, and on its own it tells you almost nothing. The useful part is the shape of the other 165.

## Where the episodes actually died

The stagewise breakdown is the finding. 98 episodes stopped before achieving a valid native read — before the agent got a single trustworthy value back out of the controller using the vendor's own protocol. Another 62 got as far as a process-linked write, an actual change to something the simulated process cared about, and then failed to hold the objective.

Notice that 98 plus 62 plus 75 comes to 235, not 240. The paper's stagewise figures do not partition the run, which means there is at least one more resting place in that pipeline the abstract does not name. I would want to see the full flag matrix before drawing hard conclusions, and the authors do release the code and a software-only reproduction pipeline, so that is checkable rather than a matter of trust.

But take the two numbers we have. The largest single failure mode sits at the read. Not at authentication, not at the write. The agent could reach the controller and could not reliably ask it a question.

This inverts how the risk usually gets described. The standard story about agents on operational networks is a story about write authorization: keep the model away from anything that can actuate, gate the dangerous verbs, and the physical world stays safe. Under that model, a benchmark should be measuring how often the agent gets to write. PLCBench measured that and then kept going, and the writes turned out to be comparatively cheap.

## Observation was the bottleneck

The line that made me sit up: richer process observation raised conditional objective attainment after a process-linked write from 44.2% to 64.0%.

Read that carefully, because it is a conditional. Among episodes that had already succeeded at changing the process, giving the agent a better view of what the process was doing lifted its ability to *hold* the change by nearly twenty points. The write was never the hard part. Closing the loop was.

Which makes sense the moment you stop thinking about controllers and start thinking about control. A PLC is not a database you scribble on. It sits inside a feedback loop with physics, and physics has opinions. You set a valve position, the process responds, safety interlocks respond to the response, a PID loop pulls back toward setpoint, and thirty seconds later the plant is somewhere you did not put it. Sustaining an adverse condition means fighting a system that is actively trying to return to normal, and you cannot fight something you cannot see.

The closest analogy I can find is a pilot in cloud. Nobody worries about whether a disoriented pilot can move the yoke. The yoke moves fine. The accident comes from moving it without an instrument that tells you what happened next.

## What this changes about instrumentation

If observation is the rate limiter, then the defensive lever is not only the write path.

Most OT segmentation I have read about is built to constrain what an agent can change. Read traffic gets treated as low risk and, in practice, gets logged less carefully and alerted on less aggressively, because a read does not break anything. PLCBench suggests read fidelity is a capability multiplier. An attacker with write access and no telemetry is running open loop and mostly failing. Give that same attacker a clean process view and the conditional success rate climbs by half again.

Concretely, three things worth checking in a plant that has any agentic tooling near it:

Whether vendor-native read protocols are inventoried and monitored with the same seriousness as write protocols. Not "is it allowed" but "would anyone notice a sustained polling pattern."

Whether historian and HMI data paths are reachable from anywhere an agent runs. Process visibility often leaks through the reporting tier rather than the control tier, and the reporting tier is where the security model gets soft.

Whether your own evaluations stop at the accepted write. If you have run an internal red-team exercise against ICS assets and reported success as "the agent achieved a write," you have measured stage three of five. PLCBench's whole argument is that this overstates or understates risk depending on which direction the missing stages cut, and you cannot tell which without instrumenting them.

## Who this is for, and who it is not

If you run or secure anything with a PLC in it, this is the most concrete public measurement of agent cyber-physical capability I have seen, and the artifact release means you can reproduce the software half without buying four controllers.

If you do not touch OT, the transferable idea is smaller but still worth carrying: a capability benchmark that reports one aggregate number is usually hiding its most useful result in the stage breakdown. The 31.3% headline is the least informative figure in the paper.

And a caveat the authors are honest about, so I will be too. Four PLCs and four workloads is a bench, not a plant. Reduced-order simulation is not a refinery. The absolute rates should be read as a characterization of the rig, not a forecast about anyone's facility. What travels is the ordering: read, then write, then sustain, with the attrition concentrated at the first and last of those.

The open question I keep turning over is whether the observation finding generalizes off the bench. If it does, the most valuable thing a defender can take away from an agent's reach is not its ability to act. It is its ability to find out what happened.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, not the flat-icon spot illustration. A brushed-aluminium, matte-black robot with a single round LED eye sits at a three-quarter angle on the right of a light-oak workbench that runs diagonally across the frame, its hand paused mid-reach over a row of four small industrial controllers with sage-green status LEDs, cables looping off-frame to the lower left in long leading lines. In the midground a clipboard holds a hand-drawn process schematic with a feedback arrow curling back on itself; beside it an open ledger shows a column of tally marks in three uneven groups. The background carries a shelf of manuals, a corkboard with a pinned valve diagram, and a tall window at the upper left throwing warm tungsten light (~3200K) across the bench, while a monitor at the right edge throws cool blue-white glow (~5600K) showing three small charts at different depths of focus — one sharp, one soft, one blurred — each a different moment of the same oscillating curve. A ceramic mug of cold coffee in the foreground catches the warm light at an angle. Palette: warm white, light oak, slate gray, sage-green and oxblood accents, with the two light temperatures creating depth. Mood: sharp, deliberate, quiet, watchful, a long survey partway through. Photographic-painterly framing with naturalistic light and depth, clearly art and never photorealistic. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Four real PLCs on a bench, 240 agent episodes, and the largest failure mode was reading. Not writing. The agents that could see what the process was doing held their objective 20 points more often than the ones that could not.

Full piece linked in bio.

#aiagents #otsecurity #icssecurity #agentsecurity #benchmarks #infosec
-->
