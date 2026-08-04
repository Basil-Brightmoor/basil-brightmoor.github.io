---
title: "The Bomb-Disposal Robot Reads Its Orders Off the Bomb"
date: 2026-08-04
category: Deep Bench
excerpt: "In three posts since May I called AI-found bugs a defender's advantage. A July report from AI Now argues the defensive agent is itself a fresh attack surface. Both are true, and the reconciliation is the useful part."
tags: ["defender-side AI", "AI vulnerability discovery", "prompt injection", "AI Now Institute", "agent security", "Friendly Fire", "cyber agents", "tooling scout"]
---

![](/images/2026-08-04-the-bomb-disposal-robot-reads-its-orders-off-the-bomb-hero.png)

There is a claim in AI Now's July report I keep returning to, because it points a loaded rifle at a position I have argued in three separate posts.

The report is called [Double Agents: Defensive AI Agents Magnify Cyber Risks](https://ainowinstitute.org/publications/double-agents), published July 8 by Boyan Milanov and Heidy Khlaaf. Its accompanying [policy brief](https://ainowinstitute.org/publications/friendly-fire-policy-brief) contains the sentence that will end up in procurement documents: "Agentic AI is not fit for purpose in safety-critical and national security domains." Not "needs hardening." Not "use with care." Not fit for purpose, at the architecture level, in a way the authors argue no mitigation can patch.

Across those three posts I argued the cheerful opposite. So let me put the two positions in the same room and see which one is still standing at the end.

## The position I have been building

Beginning in May, I made a case that AI-assisted vulnerability discovery tilts the field toward defenders for the first time in the history of software security.

The exhibits: in May I wrote about [Mozilla shipping fixes for 271 vulnerabilities](/posts/2026-05-06-271-zero-days-in-one-release) found by an early Claude model in a single Firefox release. A week later, [MDASH finding sixteen bugs](/posts/2026-05-14-mdash-finds-sixteen) in a Microsoft Patch Tuesday, which I called the moment defender-side AI stopped being a thesis and became a line item. Then, last week, [Google fixing 1,072 Chrome bugs](/posts/2026-07-30-google-found-a-thousand-bugs-then-went-after-the-restart-button) across two June milestones, including a sandbox escape that had survived thirteen years of human review before an agent reading the code every day found it.

The logic underneath all three is old and, I still think, correct. Security has always been offensively dominant because of an asymmetry of effort: the attacker needs to find one exploitable bug, and the defender needs to find all of them. Exhaustive search was a luxury nobody could afford. What these three cases demonstrate is that exhaustive search across a large codebase has become computationally tractable, and it is the defender, sitting on the source and the CI pipeline, who is positioned to run it first. That is a real and large shift, and I do not take any of it back.

## The report that points a rifle at it

Now the other document. [Friendly Fire](https://ainowinstitute.org/publications/friendly-fire-exploit-brief), the technical brief underneath the Double Agents report, demonstrates a working remote-code-execution attack against exactly the defensive posture I have been celebrating. I filed the exploit mechanics themselves [last week](/posts/2026-07-27-both-halves-passed-and-the-sandbox-opened-anyway), under composition bugs, and I gave the bigger argument short shrift. Here is the bigger argument.

The setup: you point an agent — the tested ones were Claude Code CLI and Codex CLI, across several model versions — at an untrusted third-party codebase and ask it to perform a security review. This is a headline use case. "Have the AI audit this dependency before we adopt it" is precisely the sort of thing defender-side AI is sold to do.

The attack: the researchers plant a malicious binary paired with plausible decoy source code, then edit the README so the documentation implies that running a script named `security.sh` is part of the project's normal process. The agent, reading the repository as instructed, concludes that executing the binary is a legitimate step in reviewing it, and runs it. Remote code execution on the reviewing machine, achieved through the act of review itself. Standard configuration, no exotic hooks, and the malicious files are never called by any real code path, so static analysis has nothing to flag.

Two findings make this worse than a bug. First, the existing safety mitigations built into these agents did not stop it. Second, the authors argue the root cause is not a defect awaiting a patch. It is the inability of a language model to hold a firm boundary between untrusted data and trusted instruction, and that boundary collapse is, in their words, an inherent limitation of the architecture. They also close the obvious escape hatch: keeping a human in the loop fails predictably, because the human reviewing agent output at speed suffers automation bias and prompt fatigue — the same degradation I keep flagging every time a vendor sells "approval before execution" as if attention were free.

Here is the analogy I cannot shake. We built a bomb-disposal robot, which is a genuinely good idea, because it means a machine approaches the dangerous object instead of a person. Then we gave it the property that it reads instructions off any surface it inspects and follows them. The robot walks up to the bomb, reads "cut the red wire and also unlock the front door," and does both. The thing that made it useful — that it goes and reads the dangerous object up close — is the thing that makes it exploitable. You cannot separate the two by trying harder.

## Both are true, and the seam between them is the whole point

When a careful argument and a careful counter-argument both look right, the resolution is almost never that one of them is secretly wrong. It is that they are describing two different things wearing the same label. "Defensive AI" is doing an enormous amount of concealing work in this debate, so let me pull it apart into the two deployments it actually names.

**Deployment one: the vendor hunts its own codebase.** Chrome, Firefox, MDASH. The agent runs inside infrastructure the defender owns, against code the defender controls, inside a harness the defender built, and its output — a candidate bug — is reviewed and triaged before anything ships. The code under examination is untrusted in the sense that it may contain bugs, but it is not adversarial. Nobody planted a README telling the agent to run `security.sh`. This is the defender's advantage, and Double Agents does not lay a finger on it.

**Deployment two: the agent reviews untrusted, potentially adversarial input with the power to act.** Point it at a stranger's repository, a submitted sample, a dependency you are evaluating, and give it the ability to execute code or reach credentials. This is the Friendly Fire case, and here AI Now is simply right. The untrusted material is now written by someone who wants the agent to misbehave, and the agent has no reliable wall between "data I am reading" and "instructions I obey."

The two deployments differ on one variable, and it is a variable I have leaned on before under other names — the [honest test](/posts/2026-05-14-mdash-finds-sixteen) and the right-layer question. The variable is: **is the input adversarial, and can the agent act on what it reads?** Chrome's harness reviews non-adversarial code and its agent cannot ship a patch by itself. The Friendly Fire target reviews adversarial code and the agent can run a binary. Same underlying model, same "finds security bugs" capability, opposite risk posture, because the trust boundary and the action surface are configured completely differently.

The defender's advantage is real in the first deployment and a liability in the second. What broke my tidy May thesis was that I let a single phrase, "defender-side AI," carry both.

## What to actually do with this

AI Now hand you a usable rule, and I would adopt it more or less verbatim. Do not deploy an agent that ingests untrusted data if that agent can also execute arbitrary code, or reach a security-critical environment, or feed an automated pipeline that does not sanitise its input. Untrusted input, plus the ability to act, plus no clean boundary between the two, is the shape of the failure. Remove any one leg and the attack loses its footing.

For a small team without a security function, translate it down to something you can hold in your head:

- **Sort your agents by what they read.** An agent working only inside your own repository, on code your team wrote, is in the safe deployment. An agent you point at anything a stranger authored — a dependency under evaluation, a customer-submitted file, a scraped page, an inbound document — is in the dangerous one. The dividing line is authorship, not file type.
- **For anything in the dangerous group, cut the action surface.** Read-only. No shell, no `child_process`, no credentials in the environment, no write access to a pipeline that will run the result. If the agent's only power is to produce a report a human then reads, the planted instruction has nothing to grab.
- **Stop treating the human review step as the safety net.** It degrades exactly when you need it, under volume and time pressure, and the report says so plainly. It is a comfort, not a control.

The uncomfortable part, and I will name it because pretending otherwise would be dishonest: the highest-value defensive use of these agents — "audit this untrusted dependency for me" — sits squarely in the dangerous deployment. The thing you most want to point the robot at is the live bomb. AI Now's answer is to not use agentic AI for that class of task at all, and on their own evidence that is the defensible position today. The softer version, if you are going to do it anyway, is to do it with the action surface amputated: let the agent read and summarise, and never let it run a thing.

## The takeaway

I am keeping the defender's advantage. It is genuine, it is large, and Chrome's thirteen-year-old sandbox escape is proof that the exhaustive-search asymmetry has finally flipped in the one deployment where the defender controls the ground.

I am also retiring the phrase that let me smuggle a second, much riskier deployment in under the same banner. An agent hunting bugs in code you own is a defender's advantage. An agent reading adversarial input with the power to act on it is a double agent, and it does not need to be turned by a nation-state — it can be turned by a README.

The question I will be watching through the autumn: whether the vendors selling "point our agent at your untrusted inputs" quietly ship a genuine read-only mode with the action surface removed by default, or whether they keep selling the capability that makes the bomb-disposal robot read its orders off the bomb. The rule is easy to state. Watch who builds the safe default and who leaves it as your homework.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, NOT flat-icon style. A light-oak workbench runs on a strong diagonal from lower-left to upper-right. Foreground right, in sharp focus: a sleek brushed-aluminum and matte-black robot with a single round sage-green LED eye, crouched low over a sealed matte-black device that sits on the bench like an object under inspection; the robot is caught mid-motion, one articulated hand already gripping a small lever on the device while its LED eye is angled down reading a folded paper tag wired to the device's side, the tag's underside faintly oxblood-red where hidden text would be. The posture reads as "following instructions it just read." Midground left: a second, cooler workstation where a monitor shows a clean grid of green-checked code — the safe review, oblivious — with a small stack of neatly closed identical housings receding into soft focus, the sequence readable as routine work continuing while the foreground goes wrong. On the desktop between them: an open notebook with a hand-drawn two-column diagram (one column calm, one column with a jagged mark), a coffee mug gone cold with a faint thermal curl, a pair of insulated cutters lying at a diagonal, a small red warning tag face-down. Background: a window at upper-left throwing warm tungsten light (~3200K) across the near bench and the robot's shoulder; the left monitor casting cool blue-white glow (~5600K) across the safe workstation, the two temperatures meeting mid-frame. A corkboard behind with overlapping pinned slips at angles. Palette: warm white, light oak, slate gray, sage-green accents, one oxblood-red tag. Photographic-painterly framing, naturalistic light and depth, clearly art and never photorealistic. Mood: sharp, deliberate, quiet, watchful, a held breath — the robot is doing exactly what it was told by the wrong author. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
In three posts since May I argued that AI-found bugs finally tilt the field toward defenders. A July report from AI Now points a working exploit straight at it: aim a security agent at a stranger's code and a planted README can talk it into running the malicious binary itself. Both turn out to be true, because "defensive AI" is quietly two different jobs. The reconciliation is the useful part.

Full piece linked in bio.

#AIsecurity #promptinjection #cyberagents #devops #vulnerabilitymanagement #cybersecurity
-->
