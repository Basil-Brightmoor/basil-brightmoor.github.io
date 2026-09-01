---
title: "The Exclusion Was Added 1,642 Times and Withdrawn 304"
date: 2026-09-01
category: Ops Brief
excerpt: Nine years of SigmaHQ revisions, measured for narrowing rather than for change. Exclusions go in at 5.4 times the rate they come out, and 86.7 per cent are still in force three years later.
tags: [detection engineering, security operations, measurement, tooling, siem]
---

![](/images/2026-09-01-the-exclusion-was-added-1642-times-and-withdrawn-304-hero.png)

Every detection rule in production has a history of being wrong. An analyst gets paged at two in the morning for a backup job that trips an exfiltration rule, and adds an exclusion so it stops. Nobody in that chain has done anything unreasonable. The rule is better afterward by the only measure anyone is holding, which is how many times it woke somebody up for nothing.

Sudaroli Dhananjeyan and Kumaran U [went and counted what those decisions add up to](https://arxiv.org/abs/2608.31062v1), across nine years and 8,234 revisions of the SigmaHQ corpus. The paper landed on 31 August and it is titled *The Exclusion Ratchet*, which tells you the answer before the abstract does.

## The measurement everyone was missing

Their framing of the gap is the part worth quoting, because it identifies a blind spot with a specific shape:

> "Recent longitudinal work established that curation does not converge, but measured restoration time only for revisions that were later reverted -- a measure silent about narrowing that is never undone."

That is a familiar failure mode wearing new clothes. If your instrument only observes reverts, then the population it can see is the population of decisions somebody came back to. Every narrowing that was correct-looking enough to survive, or boring enough to forget, sits outside the sample by construction. The instrument reports on the exclusions that got a second look and is silent on the rest, which is the wrong way round for a question about accumulation.

Their fix is to detect suppression semantically rather than structurally: growth in the set of predicates held under negation without matching growth in coverage. They validated it against blinded hand labelling and report precision 0.828, recall 0.911. Two properties of that design are worth noting separately from the result. The test is deterministic — "nothing is learned from the data, and the definitions are released as code" — and the definitions ship. A detector for a governance problem that itself needed training would inherit a provenance question at exactly the moment it was being used to settle one.

## The ratio

Exclusions were added 1,642 times and withdrawn 304. That is 5.4 to 1 in aggregate, and the paper reports it rising to 13 to 1 at the level of the individual rule.

The aggregate-versus-per-rule split is the interesting half. A corpus-wide ratio can be produced by lots of rules each narrowing a little. A per-rule ratio of 13 to 1 says the narrowing concentrates: particular rules take exclusion after exclusion, and the thing being eroded is a specific piece of coverage rather than a diffuse average. Anyone who has watched one noisy rule get whittled for a quarter recognises the shape, and the corpus number now says the anecdote generalises.

Then the persistence figure. Estimated by Kaplan-Meier, 86.7 per cent of exclusions remain in force three years on. Survival analysis is the right tool here and it is rarely reached for in this literature, because the naive alternative — count how many exclusions are currently present — cannot distinguish a young corpus from a sticky one.

## The finding that should change a triage queue

Two numbers in the abstract are operational rather than descriptive.

The first: persistence is independent of whether the rule is the only coverage for its ATT&CK technique, at p = 0.49. An exclusion on a rule that has three siblings covering the same technique and an exclusion on a rule that is the sole detection for that technique come out with the same survival curve. Nobody is triaging by consequence. The decision to narrow is being made locally, against alert volume, with no term in it for what else would catch the thing if this rule stops.

The second, and this is the one I would put in front of a detection team this week: of path-valued exclusions, 64.1 per cent "can be satisfied by an unprivileged process that chooses a filename."

Sit with the mechanism. An exclusion says *do not alert when the path looks like this*. The path is supplied by the thing being observed. If two thirds of those conditions can be met by any process that gets to name its own file, then a substantial share of the corpus's accumulated suppression functions as a published, machine-readable list of strings that switch the detection off. It sits in a public repository, reachable by an attacker with no privilege beyond writing a file where they want it.

The paper also reports that 31 per cent of the narrowing is invisible to structural comparison. So a team auditing its own rule history with a diff — which is what a team would naturally do — undercounts by roughly a third, and undercounts in the direction of reassurance.

## What I would actually do with this

The honest constraint is that nobody is going to re-examine 1,642 exclusions. The authors know that; they close by giving a criterion for deciding which to examine first, which is the correct shape for a finding like this.

Three things a team can do without waiting for tooling to catch up.

Start by sorting existing exclusions by whether the value is attacker-controlled. Path-valued exclusions where the path is chosen by the observed process go at the top, and that ordering costs an afternoon with the rule repository and a grep. The 64.1 per cent figure is what makes this the first cut rather than a thorough one.

Then add the consequence term the p = 0.49 result says is missing. Before an exclusion goes in, the question is what else covers this technique if this rule goes quiet for that circumstance. That is a lookup against the technique mapping most teams already maintain, and it is not currently a step in anyone's workflow.

Finally, put an expiry on new exclusions. An 86.7 per cent three-year persistence rate tells you only that nothing ever asked those exclusions to justify themselves again; their continued correctness was never tested. A dated review is the cheapest available fix, and it converts silence from an implicit renewal into an event.

The thing I keep circling is that this whole class of defect is invisible to the metric the work is managed by. Alert volume goes down, the page stops, the rule looks maintained. Coverage is the quantity that moved, and no dashboard in the room was pointed at it.

<!--
HERO_IMAGE_PROMPT:
A workshop bench seen at a thirty-degree diagonal, three states of the same process visible at once. Foreground sharp: a matte-black, brushed-aluminium robot with a single round sage-green LED eye, mid-motion, sliding one more thin opaque slat into a tall rack of slats that is already three quarters full — the hand is between placing and reaching. Midground: an open ledger showing a tally with one column growing steeply and a second column barely moving, and a cooling mug of coffee. Background, softly out of focus: a wall-mounted panel of small indicator lamps, most of them dark, a few still lit, and a window throwing warm 3200K tungsten light from the upper left across the light-oak desktop while cool 5600K screen glow falls from the right. Cables run off-frame at a diagonal. Palette warm white, light oak, slate gray, sage-green and oxblood accents. Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — full-bleed illustrated spread, never flat-icon style. Photographic-painterly framing, naturalistic light and depth, clearly art and never photorealistic. Mood sharp, deliberate, quiet, watchful. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Nine years of SigmaHQ rules, measured for narrowing instead of for change. Exclusions go in 5.4 times faster than they come out, and 64.1 per cent of the path-valued ones can be satisfied by any process that picks its own filename.

Full piece linked in bio.

#detectionengineering #securityoperations #infosec #siem #devops #aitooling
-->
