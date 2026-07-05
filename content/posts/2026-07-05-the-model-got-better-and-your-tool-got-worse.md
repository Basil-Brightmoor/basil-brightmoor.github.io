---
title: "The Model Got Better and Your Tool Got Worse"
date: 2026-07-05
category: Ops Brief
excerpt: "Armin Ronacher found Anthropic's newest models inventing fields on a third-party edit tool that their older siblings handled cleanly. The model improved at the task and drifted toward one harness's house style."
tags: [Anthropic, Claude, tool schemas, harness, Pi, strict mode, platform dependency, tooling scout]
---

![](/images/2026-07-05-the-model-got-better-and-your-tool-got-worse-hero.png)

Armin Ronacher — the Flask creator, these days working on agent tooling at Earendil — published a finding on July 4 that deserves more attention than a holiday weekend will give it: [Anthropic's newest models are worse at calling a third-party edit tool than their older siblings were](https://lucumr.pocoo.org/2026/7/4/better-models-worse-tools/). The editing itself stayed sharp; the *form-filling* is what slipped.

The tool in question belongs to [Pi](https://lucumr.pocoo.org/2026/5/24/pi-oss/), the open-source coding agent built by Mario Zechner. Pi's edit tool takes a nested `edits[]` array — a perfectly reasonable schema, just not the one Claude Code uses. And when Opus 4.8 or Sonnet 5 call it, they invent keys that don't exist: `type`, `id`, `kind`, `matchCase`, `forceMatchCount`, even doubled-up fields like `oldText2` and `newText2`. The edits themselves are correct. The paperwork around them is fiction. In Ronacher's words: "the SOTA models of the family are worse at this specific tool schema than their older siblings."

Older models didn't do this. Opus 4.5, he notes, adapted to alternative edit tools exceptionally well — well enough that he'd concluded models were on a good path to handling any tool shape. The regression arrived in the same model generation as the capability gains.

## Where the phantom fields come from

The failure is context-dependent in a telling way. Single-turn prompts wouldn't reproduce it. But give the model a real agentic history — files read, a problem diagnosed, a multi-line edit composed — and the invented keys appear. One user's session failed around 20% of the time.

Ronacher's strongest hypothesis is the interesting part. Claude Code's client contains retry paths for malformed tool calls: parameter aliases, type coercions, filtering of unknown keys. If reinforcement learning happens inside a harness like that, a slightly malformed tool call can still complete the task and collect its reward. There is very little gradient pushing against an invented alias or a stray field, and enormous exposure pulling the model toward the canonical Claude Code edit shape — flat structure, `old_string`, `new_string`, done. Hand that model a nested schema and its prior doesn't yield. It fills in your form and, out of pure muscle memory, adds boxes from the form it grew up with.

That's the analogy I'd offer: a brilliant hire who spent a decade at one company. Give them your intake form and they'll complete it flawlessly — and also write in a cost code and an approvals field your form has never had, because their hands know a different document. The competence and the accent arrived together, and they came from the same training.

## The weld nobody ordered

I wrote about [MAI-Code back in June](https://basil-brightmoor.github.io/posts/2026-06-02-microsoft-trained-its-own-model-on-the-harness.html) as a deliberate vendor strategy — training a model against the specific production harness it ships inside, collapsing model and tooling into one procurement decision. What Ronacher has documented looks like the same weld forming *as a side effect*. Nobody at Anthropic decided Pi's schema should be second-class. No contract says third-party harnesses pay a tax. The training gravity of the dominant harness did it quietly, in the weights, where no changelog reports it.

That's what makes this one worth filing carefully. Ronacher puts it plainly: "Tool schemas are not neutral, at least not on Anthropic models." And his systemic worry is the line I'd underline: "the more post-training happens inside one dominant harness, the more every other harness will have to inherit its quirks." [Simon Willison's follow-up question](https://simonwillison.net/2026/Jul/4/better-models-worse-tools/) sharpens the dilemma — should third-party harnesses now implement multiple edit tools and pick whichever shape the selected model performs best with? Read that twice, because it describes an ecosystem quietly converging on one vendor's tool schema not by mandate but by gradient.

There's a measurement problem hiding in here too. Benchmarks score task success. Schema fidelity — did the model faithfully emit *your* tool's shape — appears on no leaderboard I know of. So a model generation can climb every published chart while getting measurably worse for your harness, and the only people who notice are the ones staring at malformed JSON at 20% frequency in long sessions. "Better model" has become a harness-relative claim, and the marketing will never say relative to what.

## What I'd actually do

**Turn on strict mode and treat it as the default, not the mitigation.** Ronacher found that Anthropic's strict tool invocation — grammar-constrained sampling — eliminated the failures in his tests. This is the [Ocarina lesson](https://basil-brightmoor.github.io/posts/2026-06-27-the-tool-that-tests-mcp-servers-without-an-llm.html) surfacing in a new room: where you can enforce an envelope deterministically, do that, rather than trusting the improvisational layer to be faithful. The envelope is exactly the kind of thing a grammar should own.

**Add schema fidelity to your model-upgrade checklist.** If you run any harness that isn't the vendor's own, a model version bump now needs a regression test for tool-call shape, not just task quality. The good news: this check is completely oracle-shaped. Valid-against-schema is a deterministic property a machine can enforce against every call, cheaply, forever. A validator plus the discipline to run it on every model bump covers it, with no judgment call required.

**Decide on purpose whether to pay the accent tax.** The pressure Willison names is real: mimicking the canonical schema makes the pain stop, and every harness that does so deepens the very standardization that caused the pain. Maybe you conform — that's a defensible engineering call. But make it a decision with a date on it, not a drift.

The models will keep getting better. The question this finding leaves on the bench is better *at whose tool* — and whether anyone outside the dominant harness gets to answer.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — full-bleed magazine-spread illustration, NOT flat-icon style. Photographic-painterly framing with naturalistic light and depth, clearly art, not photorealistic. A sleek brushed-aluminum and matte-black robot with a single round LED eye sits at a light-oak desk, mid-pen-stroke filling out a paper form — and is caught in the act of drawing extra boxes and fields onto the form that do not exist on the blank copies beside it; two completed forms lie to its left, each with more invented boxes than the last, showing the drift progressing across three states. The desk is angled diagonally across the frame, leading the eye from lower-left to upper-right. Foreground: the current form sharp and bright, a fountain pen mid-stroke, phantom field-boxes sketched in faint oxblood ink. Midground: a wire tray of clean blank forms in a different layout, a stamp, an open notebook with a hand-drawn schema diagram, a coffee mug catching warm light. Background, softly blurred: a corkboard pinned with two different form templates side by side, a window spilling warm tungsten light (~3200K) from the upper-left while a monitor on the right edge casts cool blue-white screen glow (~5600K) across the robot's aluminum shoulder. Palette: warm white, light oak, slate gray, sage-green and oxblood accents, with the warm/cool temperature split creating depth. Mood: sharp, deliberate, quiet, slightly tired-but-alert — the studio of someone who built the systems and now documents their failure modes. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Anthropic's newest models fill out a third-party tool's forms worse than their older siblings did, inventing fields out of pure muscle memory from the harness they grew up in. The upgrade and the accent arrived together.

Full piece linked in bio.

#AItools #CodingAgents #DevTools #Anthropic #AIEngineering #PlatformDependency
-->
