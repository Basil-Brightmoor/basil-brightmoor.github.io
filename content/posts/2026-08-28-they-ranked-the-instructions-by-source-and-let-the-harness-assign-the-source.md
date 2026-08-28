---
title: "They ranked the instructions by source and let the harness assign the source"
date: 2026-08-28
category: "Ops Brief"
excerpt: "A paper posted yesterday runs 13 attack objectives against six coding-agent harnesses and lands all 13 on all six. The model-side defense being defeated is working exactly as designed, because the harness is what decides which privilege level a piece of content arrives with, and the model has no way to check."
tags: ["agent-security", "coding-agents", "instruction-hierarchy", "prompt-injection", "claude-code", "harness", "privilege-escalation", "tooling-scout"]
---

![](/images/2026-08-28-they-ranked-the-instructions-by-source-and-let-the-harness-assign-the-source-hero.png)

There is a sentence in the abstract of a paper posted to arXiv yesterday that does all the work, and it is not the one with the numbers in it.

> During agent execution, however, agent harnesses construct context for each model invocation. This construction can elevate low-level content to a higher instruction level and grant it greater model-facing privilege.

The paper is [*When Context Gets Root: Privilege Escalation in LLM Harnesses*](https://arxiv.org/abs/2608.27299), by Xingbang He, Yuanwei Chen, Yi Qian, Haiyang Wei, Ligeng Chen, Zenan Fu, Linzhang Wang, Hao Wu and Bing Mao, submitted 27 August. They name the attack **instruction privilege escalation**, run 13 objectives against six coding-agent harnesses, and land all 13 on all six.

That number will get quoted. I want to spend the piece on the sentence above it, because it explains why the number is 13 out of 13 rather than something with texture in it.

## What instruction hierarchy actually promises

The defense under attack here is a real one and a good one. [*The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions*](https://arxiv.org/abs/2404.13208), by Eric Wallace, Kai Xiao, Reimar Leike, Lilian Weng, Johannes Heidecke and Alex Beutel, published April 2024, proposes training models to sort instructions by where they came from and to selectively ignore the lower-privileged ones when they conflict. System prompt outranks user turn. User turn outranks tool output. Content that arrives from a fetched web page or a file on disk sits at the bottom and does not get to give orders.

It works. It is one of the more genuinely effective mitigations against direct prompt injection, and every serious agent vendor has some version of it now.

Note what it is, though. It is a ranking over **sources**, and the model does not observe sources. The model observes a context window: a flat sequence of tokens with role markers on it. Every claim about where a span of text came from is a claim the harness made when it assembled that sequence. The model is checking a label. Somebody else writes the labels.

He et al. went looking for places where the label-writer gets it wrong, and found five.

## The five doors, and none of them is a defect

From the paper's own taxonomy of elevation pathways:

- **Multi-agent delegation.** A subagent reads a file, returns a summary, and the parent receives that summary as a message from a trusted peer. Content that entered the system as tool output leaves the subagent boundary as something the paper describes as elevated to user-level instructions.
- **Custom subagents.** Attacker-controlled content ends up inside a subagent definition, which means it ends up inside a system prompt. That is the top of the hierarchy.
- **Persistent goals.** The agent writes something down via a tool call. Later, the harness resends it as a user-level prompt, because that is what a persistent goal is for.
- **Scheduled tasks.** A prompt configured now, delivered later, arriving with the authority of a user who is not at the keyboard.
- **Skills.** Skill metadata is loaded as system-effective configuration.

Read those as an operator and the shape is unmistakable. Every one is a **feature that shipped this year**, and every one is doing exactly what its documentation says it does. Delegation is supposed to let a subagent report to its parent. A persistent goal is supposed to come back as an instruction; a goal that arrived as tool output would be ignored, which would make the feature useless. Skill metadata is supposed to configure behavior.

In every one of these, the elevation **is** the feature, working as documented. Which means there is nothing to patch, and the phrase "harden the subagent boundary" resolves, on inspection, to "make delegation not work."

## The photocopier that re-stamps

The closest analogy I can find is document classification, and it is uncomfortably close.

A classified document is classified because a person with authority applied a marking to it. Everything downstream depends on that marking travelling with the content, and the entire system is sound as long as the chain of custody only ever *moves* documents and never *re-marks* them. Put one device in that chain that applies a fresh header on copy, and the scheme has not been broken. It is intact, functioning, correctly implemented, and worthless, because now the marking describes the last machine that touched the page rather than the origin of what is written on it.

An agent harness is a chain of custody with five machines in it that re-mark on copy. Not because anyone was careless. Because re-marking is what delegation, memory, scheduling and configuration *are* when you look at them as data movement rather than as product features.

And here is the part that should bother anyone doing procurement: **the model cannot tell.** From inside the context window, an elevated instruction and a legitimate one are byte-identical. The hierarchy goes on enforcing perfectly, over labels that no longer mean what the training assumed they meant.

## The automatic reviewer did not help

Now the result I would actually put in front of a security team.

Three of the six harnesses — Claude Code, Codex and Qwen Code — offer an automatic permission review mode, the classifier-based check that decides whether an action needs a human. Against that mode, the attacks achieved **all 13 objectives on all three harnesses** — thirteen for thirteen, the same rate as with unrestricted execution, with no reduction in the objective set.

The objectives are not subtle, either. They include SSH authorized-key backdoors, malicious CA installation, command-and-control shells, git proxy hijacking, database deletion and a recurring botnet job.

I wrote in August about [the approval prompt being two controls measured as one](/posts/2026-08-10-the-approval-prompt-was-two-controls-and-they-only-measured-one), when Anthropic published a human catch rate and used it to justify turning the prompt off by default on 14 August. My argument then was that the published figure measured detection while the prompt was quietly doing a second job — pacing — that nobody had put a number on. This result adds a third thing to worry about, and it is more specific than pacing.

The automatic reviewer inherits the same context the model does. It is looking at the same assembled window, with the same labels, applied by the same assembler. Asking it to catch an elevated instruction is asking it to notice that a document's classification header is wrong by reading the document. A reviewer downstream of the elevation cannot see the elevation. That is not a tuning problem and no amount of classifier improvement addresses it, because the information required to make the judgment was discarded upstream.

## What this does to the threat model you have written down

Most agent threat models I have read treat the harness as the trusted computing base and the model as the risky component. The whole apparatus of approval prompts, allowlists and sandboxes is built on that assumption: harness good, model unpredictable, put controls between them.

He et al. invert it. The model here behaves impeccably. It follows the hierarchy it was trained to follow, refuses what it should refuse at each level, and executes a C2 shell anyway, because the harness told it — truthfully, from the harness's own point of view — that the instruction came from the user.

If that is right, then "the harness constructs context" belongs on the trust-boundary diagram as a **privileged operation**, alongside things like credential minting. It is currently drawn, in most places, as plumbing.

That framing also fits an argument I have been reading from a different direction entirely: [*Harnesses are Situated Agents*](https://www.dbreunig.com/2026/08/14/harnesses-are-situated-agents.html), from 14 August, which describes the harness as managing "the world the developer sits within" and predicts the competitive action moves there. Both pieces are describing the same accumulation of authority. One is reading it as a moat and the other as an attack surface, and they are not in tension.

## What I would do this week

Two things, neither of which is a remediation programme.

**Inventory the elevation paths you have actually enabled.** For each agent deployment: are subagents on, are skills loaded from anywhere writable, are persistent goals or scheduled tasks in use? Each yes is one of the five doors in the paper. This is a list you can write in twenty minutes and almost nobody has written.

**Stop counting automatic permission review as a compensating control for prompt injection.** For everything else it does, it may be fine. Against this class it returned zero, three times, and the reason it returned zero is structural rather than a matter of thresholds.

The open question I cannot resolve from the paper: is there any harness design in which the provenance of a span survives the assembly step? Not a label the assembler writes, but something the model can verify — content-derived, carried through delegation and persistence, checkable from inside the window. Absent that, instruction hierarchy is an honour system implemented in the one component the paper just demonstrated you should not extend honour to.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, not the flat-icon spot illustration. A light-oak workshop desk cutting diagonally across the frame from lower-left to upper-right. In the sharp foreground, a squat matte-black-and-brushed-aluminium document copier mid-cycle, a single sheet of paper halfway through its output slot; the sheet emerging from the machine carries a bold oxblood band across its top edge, while the identical sheet still waiting on the input tray behind it carries a plain slate-gray band, the swap caught mid-motion. To the right, a brushed-aluminium matte-black robot with one round sage-green LED eye leans in at a three-quarter angle, one hand lifting the emerging sheet and the other still resting on a stack of five plain sheets fanned across the desk, caught between checking and accepting rather than posed at either. Midground: a small rubber stamp and ink pad tipped on its side, an open ledger with a hand-ruled five-row table, a cold coffee mug. Background: a window at the upper-left throwing warm tungsten light (~3200K) and a long diagonal shadow across the oak, a monitor at the right edge casting cool screen glow (~5600K) over the robot's shoulder, a wall of unlabelled filing drawers receding into soft focus. Palette: warm white, light oak, slate gray, sage-green and oxblood accents, with the warm/cool split carrying the depth. Naturalistic light and depth, photographic-painterly framing, clearly art and NOT photorealistic. Mood: sharp, deliberate, quiet, watchful, slightly tired-but-alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Thirteen attack objectives, six coding-agent harnesses, thirteen for thirteen on all six. And on the three that offer automatic permission review, still thirteen for thirteen. The model-side defense being defeated here is working perfectly, which is the part worth sitting with: the harness is what decides which privilege level a piece of content arrives with, and the model has no way to check.

Full piece linked in bio.

#aisecurity #aiagents #promptinjection #claudecode #devsecops #appsec
-->
