---
title: "They Trained It on the Harness and Reported It as a Model"
date: 2026-08-09
category: "Ops Brief"
excerpt: "A paper on CLI agent scaffolding found that fine-tuned coding models degrade outside the harness they were trained on, while base models do not. The benchmark number describes a pair. You only buy half of it."
tags: ["ai-agents", "coding-agents", "benchmarks", "tooling", "evaluation", "mcp"]
---

![](/images/2026-08-09-they-trained-it-on-the-harness-and-reported-it-as-a-model-hero.png)

There is a sentence in an [arXiv abstract posted on 6 August](https://arxiv.org/abs/2608.06113) that I have now read about six times, because each pass makes it worse.

Kishanthan Thangarajah, Boyuan Chen and Ahmed E. Hassan were studying what happens when you take a coding model fine-tuned on one command-line agent's trajectories and run it inside a different one. The headline result is unsurprising: "Models fine-tuned on this data score well under OpenHands but degrade substantially when deployed under any non-training scaffold." Fine. Training data has a shape, the shape came from somewhere, moving the model somewhere else costs you something.

Then comes the control condition, and the control condition is the whole story:

> "Untrained base models do not show this divergence, indicating the gap is fine-tuning-induced and tied to the conventions of the training scaffold."

Read that again with an operations hat on. The base model ports cleanly. The improved model loses ground the moment it leaves home. A meaningful chunk of what the fine-tuning bought turns out to be fluency in one particular harness's conventions — its planning ritual, its turn structure, the implicit grammar of its agent loop — and that portion stays behind at the door when you change scaffolds.

Which means the number on the leaderboard belongs to a pair: the model and the scaffold together, measured as one object.

## The molecule and the tablet

Here is the comparison that made this click for me, and it comes from an industry that solved this problem forty years ago.

When a generic drug manufacturer wants to sell you a copy of an approved medicine, they are not permitted to point at the brand's clinical trial and say "same active ingredient, therefore same results." They have to run their own pharmacokinetic study on *their tablet* and demonstrate [bioequivalence](https://pubmed.ncbi.nlm.nih.gov/26132680/). As Chittaranjan Andrade lays it out in the *Journal of Clinical Psychiatry*, the FDA requires the 90% confidence interval of the pharmacokinetic ratio — generic against reference, on peak concentration and total exposure — to sit between 0.80 and 1.25.

The reason that requirement exists is that the inactive ingredients are not inert with respect to outcome. The binder, the coating, the compression force, the disintegrant — none of them are the drug, all of them measurably change how much drug arrives and how fast. So the regulator draws the boundary in exactly the right place: the claim attaches to the *formulation*, not to the molecule.

Software reports the molecule. Every time. "Model X scores N on SWE-bench" travels through procurement decks, vendor comparisons, internal build-versus-buy memos and my own reading with the scaffold silently deleted, and the scaffold is the coating.

I want to be careful not to overclaim here, because this is one paper and it does not put a number on the size of the drop. What it does establish is a direction and a mechanism, and the mechanism is the part that generalises: the authors identify **planning structure** as the load-bearing component, and split it into explicit planning (a pre-execution plan produced as a first-class artifact) and implicit planning (the structural conventions of the loop itself). They show the two are empirically separable in training data. That is a real finding, and it names the thing that was previously just vibes about "harness fit."

Drew Breunig [called the general shape of this in May](https://www.dbreunig.com/2026/05/10/overfitting-the-harness.html) from the vendor side — labs baking first-party harness behaviour into the weights, with the endpoint being models that "resemble appliances, not general platforms." DCAS is the measurement arriving under the argument. His concern was about lock-in. The operational version is smaller and more immediate: your evaluation is only valid for the rig you evaluated on, and you probably did not write down which rig that was.

## The other half of the pair is yours, and it drifts

If the number describes a model-plus-scaffold pair, and you supply the scaffold, then the sensible next question is: do you actually know what your scaffold contains?

Almost certainly not, and there is now a tool that will tell you how badly. Breunig also shipped [drskill](https://github.com/dbreunig/drskill) — MIT-licensed, Python, and pitched as `brew doctor` for your agent's loadout. It detects the coding agents on a machine or in a repo, works out which skills and MCP servers each one actually loads, and checks the whole set for problems. The [announcement post](https://www.dbreunig.com/2026/07/24/manage-your-agent-s-loadout-with-dr-skill.html) put it at 34 issue categories; the README now lists rather more, grouped into skill checks, MCP server checks, plugin manifest checks and description-quality checks.

The details that stopped me were in the examples of what it catches:

- Skills that shadow each other or load twice
- Descriptions overlapping so routers confuse them, which is why your agent reaches for the wrong tool and nobody can explain it
- Unpinned server packages, which means you run whatever that publisher ships next
- Secrets sitting in committable config files
- Tool descriptions that changed after approval
- Hidden instructions or credential paths in tool text
- Symlinks escaping plugin boundaries

And the anecdote from the announcement post: a developer whose enterprise agent had **over 600 skills loaded** without his explicit awareness. A personal agent shipping with nearly 100.

Six hundred. Nobody chose six hundred. Six hundred is what accumulates when every integration is one line of config, nothing ever gets removed, and no artifact anywhere in the organisation enumerates the current state.

The two commands worth separating: `drskill scan` reads the loadout as *configured*, while `drskill audit` reads the local session traces that Claude Code, Codex, Pi and Copilot already write to disk and ranks which skills and MCP tools were *actually invoked*. That gap — configured versus invoked — is the closest thing I have seen to a utilisation report for an agent's context budget. Most of those six hundred skills are paying rent in tokens and router confusion and returning nothing.

So the pair is unstable on both sides. The vendor half was tuned against conventions you cannot inspect. Your half accrues quietly and has never been inventoried.

## Who should care about this, and who genuinely shouldn't

**This matters to you** if you are choosing between coding agent models on published benchmark numbers, if you are running a fine-tuned or distilled coding model inside a CLI scaffold other than the one it was trained against, if you are planning a migration between agent harnesses, or if you have more than a couple of people adding MCP servers and skills to a shared configuration.

**This does not matter much to you** if you use one vendor's model inside that same vendor's own agent, have never touched a fine-tune, and load a handful of skills you personally chose. You are running the pair as it was measured. The finding is about mismatch, and you do not have one. Run `drskill scan` once for the credential and unpinned-package checks, then get on with your day.

## What to actually do about it

Three things, and only the first one is real work.

**Write the scaffold down as a versioned artifact.** Not prose in a wiki. The scaffold identity and version, the model, the skill list, the MCP server list with pinned versions. Commit it. The point is that six months from now, when the agent's behaviour changes, you can diff. Right now most teams cannot answer "what changed" because nothing was ever recorded as a state.

**Run `drskill audit` against your session traces and delete what never fires.** This is a twenty-minute job that will embarrass you, in the useful way. The traces already exist on disk; you have been generating this data for months without reading it.

**Treat a scaffold change as a re-qualification event, not a config edit.** If you swap CLI agents, the DCAS result says your model's measured performance does not necessarily come with you — particularly if that model was tuned on agent trajectories. Re-run whatever internal evaluation you trust. If you have no internal evaluation, that is the actual finding of this post.

The bigger question, and I do not think anyone has an answer yet: what would a bioequivalence standard even look like here? The regulator's version works because the outcome is measurable in a blood draw and the reference product is fixed and public. Agent scaffolds are neither — they are private, versioned weekly, and half the interesting behaviour lives in a prompt that vendors treat as a trade secret.

But the failure the standard prevents is exactly the failure we have. A number was produced by a formulation, and it is being read as a property of the ingredient.

What would you have to publish alongside a coding agent benchmark before the number meant anything to somebody running a different rig?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration, full-bleed magazine register in the manner of Christoph Niemann's New Yorker covers and Tom Gauld's richer panel work — illustrated and layered, not flat-icon, not photorealistic. A workshop bench seen at a 30-degree diagonal across the frame. A brushed-aluminium, matte-black robot with a single round LED eye is caught mid-motion, lifting one identical small machined component out of one test jig and reaching toward a second — the component is in the air between the two, its shadow cast long across the light-oak benchtop. Three jigs sit at receding depths along the diagonal: the nearest sharp with its brass gauge needle pinned high, the middle softer with the needle drooping, the furthest blurred with its needle near zero — three states of the same measurement visible at once. Midground: an open notebook with a hand-drawn schematic of the three jigs, a caliper, and a small stack of pinned index cards. Background: a corkboard with overlapping paper strips and a window throwing warm tungsten-orange light (~3200K) from the upper left, while cool blue-white monitor glow (~5600K) rakes in from the right across the robot's shoulder. A coffee mug in the foreground catches the warm light at an angle to the robot's gaze. Palette: warm white, light oak, slate gray, sage-green LED indicators, one oxblood accent on the notebook binding. Mood: sharp, deliberate, quiet, watchful, a survey partway through rather than concluded. Cables run off-frame lower right creating a leading line. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A new paper found that coding models fine-tuned on one agent harness fall apart inside a different one, while untrained base models port over fine. So a chunk of what the fine-tuning bought was fluency in one scaffold's conventions, and it stays behind at the door. The leaderboard number describes a pair. You only buy half of it.

Full piece linked in bio.

#aiagents #codingagents #devtools #mcp #aitooling #benchmarks
-->
