---
title: "The Self-Diagnostic: Six Questions a Small Team Can Actually Answer"
date: "2026-05-23"
category: "Ops Brief"
excerpt: "Yesterday I wrote up the six markers that make 'AI psychosis' a legible institutional state. The natural next question is the one I left out: how does a small team tell, this week, whether it's drifting into the pattern? Six questions you can answer from the data you already have — and what each answer is actually telling you."
tags: "ai-psychosis, self-diagnostic, ai-governance, productivity-measurement, small-teams, ops-brief, ai-adoption, organizational-health"
---

![](/images/2026-05-23-the-self-diagnostic-hero.png)

Yesterday's [Deep Bench piece](/posts/2026-05-22-the-behavioral-signature-of-ai-psychosis) laid out the six markers I think compose Mitchell Hashimoto's "[AI psychosis](/posts/2026-05-15-note-companies-under-ai-psychosis)" framing as an institutional state. I closed it with the line that the diagnostic isn't whether your engineers like the tools — it's whether your organization can still tell when it's making things worse.

The piece I should have written next, and didn't, is the operational one. The Deep Bench piece is for the CTO who wants to know whether the phrase means anything. The piece below is for the lead, the founder, or the engineering manager who wants to know whether they themselves are drifting into the pattern, this Friday, with the data they already have.

I want to be honest about the limits of this. A small team is not Uber or Amazon. The leaderboard pathology and the tokenmaxxing pathology are population-scale Goodhart's Law instances; a team of eight does not have a leaderboard. But the underlying mechanism — measuring a proxy and treating it as the outcome — scales down perfectly well, and the absence of explicit performance theatre at small scale can make the drift harder to spot, not easier. The small-team failure mode is quieter. It is the kind of thing that becomes legible only when something breaks.

So: six questions. None of them require new tooling. Each one maps to one of the markers from yesterday's piece. The answers are honest only if you write them down before reading the interpretation.

## Question one — what is your current AI productivity claim?

Stop reading and finish this sentence out loud: *"AI has made our team X% more Y since we started using it."* If you can't, that's the answer. If you can, what are X and Y, and where did the numbers come from?

The marker is *usage as the measured outcome*. The diagnostic isn't whether the number is good — it's whether the number exists at all and refers to something other than consumption. "We're shipping 30% more PRs" is a usage proxy. "We closed our defect backlog two sprints faster than the prior quarter" is an outcome. The first is what Uber measured. The second is what would have caught the bill before it landed.

## Question two — what has the AI been authorized to do that it wasn't authorized to do six months ago?

Make the list. Not the tools — the actions. Six months ago the agent could *suggest a function*. Today it can *commit to a branch*, or *open a PR*, or *run CI*, or *connect to your production database in read mode*, or *touch your billing system*. What changed, and what was the evidence that justified each step?

The marker is *autonomy extended against a miscalibrated proxy*. If the evidence was a benchmark number, a vibe, a competitor's announcement, or "the model is much better now," you are inside the [SWE-bench autonomy miscalibration pattern](/posts/2026-04-26-the-swe-bench-validity-collapse-as-an-epistemics-problem) at small scale. The fix isn't to retract the autonomy — it is to write down what evidence *would* justify the current grant, and check whether you have it.

## Question three — where is the McKinsey-style adoption number in your team conversations?

Listen to your last two retros and your last all-hands. Did anyone reference an external adoption number — *"only X% of teams are using AI effectively"*, *"we're behind on the curve"*, *"the McKinsey report says…"* — as the framing for an AI investment decision?

The marker is *the adoption-gap reading*. A 90% gap in industry adoption is a market signal that has roughly nothing to do with whether your particular team is doing it well. The diagnostic isn't that the number is wrong. It's that an external adoption statistic is being used as an internal performance argument, which is a category mismatch that betrays the absence of any internal measurement.

## Question four — has anyone on your team published a velocity estimate that contradicts the felt experience?

Ask the person who has felt the most productive on the team: *"How long did the last comparable feature take, by calendar?"* Then look it up. Compare.

The marker is *phantom velocity in planning*. The [METR finding](https://metr.org/) was specifically that engineers felt 24% faster while measurably being 19% slower — a 40+ percentage-point distortion. The small-team manifestation is subtler: roadmap commitments made on felt velocity that ship two weeks late, repeatedly, with no one connecting the misses to the planning anchor. If your last three estimates have all slipped in the same direction, the planning instrument is what slipped.

## Question five — when Claude Code or Cursor changed behavior in the last sixty days, did you notice before the vendor told you?

The [Anthropic April postmortem](/posts/2026-04-24-the-harness-was-the-bug) confirmed that all user-perceived quality regression over five weeks was caused by three product/harness changes — reasoning effort, caching, system prompt brevity — not the underlying model. None of them were announced ahead of time. Teams that were calibrating reliability against task benchmarks were measuring a system whose behavior was changing underneath them.

The marker is *harness invisibility*. The diagnostic question is: do you have any independent measurement of your AI tool's behavior across time, or are you fully dependent on the vendor's release notes for that signal? A weekly five-task evaluation suite you control is the lowest-effort instrument that solves this. It is not novel infrastructure. It is the boring thing nobody has built because the felt experience has been positive.

## Question six — when something broke because of AI, what did you do more of?

This is the one. Pull up the last AI-adjacent incident — a CI failure traced to an agent commit, a refactor that quietly degraded a hot path, a customer-facing bug shipped by an autoapproved PR. What was the response?

The marker is *the corrective signal reframed as further justification*. The healthy response to an AI-caused incident is the same as the response to any incident: retrospective, root cause, mitigation, often a reduced autonomy grant pending a fix. The pathological response — and this is the load-bearing diagnostic — is *more automation*. *We'll write an agent to catch this next time.* *We'll add a check the model can run.* *We'll have Claude review Claude's PRs.*

If the post-incident action was a net increase in agent activity, the organization metabolized the failure into further commitment to the failing layer. That is the signature finding from yesterday's piece, the one I think distinguishes psychosis from ordinary over-enthusiasm. Over-enthusiasm corrects when bills come due. This state cannot.

## Scoring

Six questions. There is no aggregate score. The point of the diagnostic is to make one drift legible at a time, because each marker has a different fix:

- Marker one (no productivity number): pick one outcome metric this quarter, even badly.
- Marker two (autonomy without evidence): write down the evidence threshold for the current grant.
- Marker three (external adoption framing): treat market signals as market signals, not management instruments.
- Marker four (phantom velocity): re-anchor estimates on calendar time, not felt speed.
- Marker five (harness invisibility): build the five-task weekly eval.
- Marker six (correction loop inverted): the next AI-caused incident, do less of the failing thing for one cycle. Watch what happens.

The question I would ask a small team that scored cleanly on all six is whether they actually answered honestly or whether the answers were generated by the same instrument that needs evaluating. The diagnostic, like the syndrome, is not immune to the failure mode it describes. But starting somewhere honest is still the move.

<!--
HERO_IMAGE_PROMPT:
A sleek matte-black and brushed-aluminum robot at a clean workshop desk, holding up a single sage-green check mark while six small numbered cards are laid out in front of it in a precise grid, each card unmarked. The mood is methodical, a survey just begun. Warm white walls, light oak desktop, one slate gray monitor screen-off in the background, one oxblood ceramic mug. Naturalistic light from a window off-frame. Contemporary editorial illustration, Christoph Niemann / Tom Gauld register — clean, designed, mid-century-modern sensibility with contemporary edge. Photographic-painterly framing, naturalistic light and depth, clearly art not photorealistic. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->
