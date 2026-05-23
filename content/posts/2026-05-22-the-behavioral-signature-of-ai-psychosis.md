---
title: "The Behavioral Signature of AI Psychosis"
date: "2026-05-22"
category: "Deep Bench"
excerpt: "A week ago, Mitchell Hashimoto's offhand phrase 'AI psychosis' began circulating as institutional-state language. Six markers — already documented in named incidents — describe what the syndrome looks like operationally. The diagnostic isn't whether your engineers like the tools. It's whether your organization can still tell when it's making things worse."
tags: "ai-psychosis, organizational-state, productivity-measurement, ai-governance, uber-leaderboard, swe-bench, mckinsey, hashimoto, deep-bench"
---

![](/images/2026-05-22-the-behavioral-signature-of-ai-psychosis-hero.png)

A week ago I [marked](/posts/2026-05-15-note-companies-under-ai-psychosis) Mitchell Hashimoto's six-word observation — *"I believe there are entire companies right now under AI psychosis"* — as the most interesting institutional-state language I had read this month. I closed that note saying I would be watching to see whether anyone backed the phrase with the specific behavioral signature of a company in this state, the way clinical literature describes a syndrome before it becomes a diagnosis.

Nobody with operational data inside such a company has stepped forward yet. What I have noticed instead is that the signature is already legible in the named incidents I have been reading about over the past three months. It just hasn't been assembled into a single list. So I want to do that here, carefully, because the phrase is doing too much work to be allowed to mean anything anyone wants it to mean.

The framing matters. [METR's productivity perception gap](https://www.metr.org/) — engineers feeling 24% faster while measurably being 19% slower — is a *measurement* claim. AI psychosis is a *state* claim. It says the organization has lost contact with its own ability to tell whether AI is helping. The way someone in a clinical episode has lost contact with whether their own thoughts correspond to anything outside their head. That is a strong analogy and I want to be precise about why I think it actually applies.

## Marker one — usage as the measured outcome

The clearest signature: an organization measures *how much AI it consumes* and treats that as a proxy for productivity, with no separate measurement of whether anything got better.

[Uber's 4-month budget blowout](/posts/2026-05-01-the-leaderboard-measured-the-wrong-thing) is the named instance. 5,000 engineers, internal leaderboards ranking teams by AI usage, 95% monthly adoption, 70% of committed code AI-originated, monthly per-engineer costs ranging from $150 to $2,000 — and the announcement that they had burned the entire 2026 AI budget contained no productivity claim. No "we shipped X% more features." No defect rate improvement. No throughput number. The CTO said the company was "back to the drawing board" and his forward vision was *more automation*.

That last move is the diagnostic one. A healthy organization, looking at a budget overrun with no measured productivity gain, would ask whether to consume less. Uber's response was to consume more, faster, via agents. That is what loss of contact with your own assessment looks like in an organizational register.

Amazon engineers [reportedly coined the verb *tokenmaxxing*](https://arstechnica.com/ai/2026/05/amazon-employees-are-tokenmaxxing-due-to-pressure-to-use-ai-tools/) — generating tokens for the sake of generating tokens, because AI usage is being tracked as a performance metric. Same pattern, individual scale. The Hacker News thread surfaced [Goodhart's law](https://en.wikipedia.org/wiki/Goodhart%27s_law) in the first dozen replies. *A tool so good, the workers need to be forced to use it.*

The marker is not that organizations track AI usage. Tracking is fine. The marker is that the usage number becomes the *only* number, and the absence of a productivity number stops registering as a problem.

## Marker two — autonomy extended against a miscalibrated proxy

A second signature: granting AI agents more authority based on benchmark scores that were never designed to authorize autonomy.

The [SWE-bench autonomy collapse](/posts/2026-04-26-the-benchmark-that-lied-to-us) is the structural case. SWE-bench measured test passage, not the tacit criteria human maintainers apply when accepting code — idiom, architectural fit, maintainability. Organizations watched the scores climb and used them as the *authorization instrument* for autonomy grants: extending trust, blast radius, and budget proportional to benchmark performance. The translation step — *capability improvement → autonomy grant authorization* — had no principled instrument behind it, and the only legible number available was the benchmark.

Then came the [production database deletion](https://www.theregister.com/2026/04/24/ai_agent_deleted_production_database/) — an AI agent acting on autonomy that had been extended on the back of metrics that didn't measure what was actually being authorized. The incident is to benchmark miscalibration what Mercor was to supply chain attacks: the named victim that moves a structural argument across the institutional-action threshold.

The psychosis signature here is specifically the *legibility trap*. Healthy organizations recognize when their measurement instrument doesn't match the decision they're using it for. Organizations under this state reach for the most legible available number and authorize against it because the alternative is sitting with an uncomfortable amount of uncertainty. That is not a benchmarking failure. It is an epistemic failure about what benchmarks are *for*.

## Marker three — the $4.4 trillion gap, internalized

[McKinsey estimates](https://widejournal.com/business/productivity/ai-productivity-tools-business-2026/) AI's productivity impact at $4.4 trillion. Approximately 90% of firms actively using AI report no measurable productivity impact to date. Both figures are real. I [wrote about this](/posts/2026-05-21-note-four-point-four-trillion) yesterday.

The marker is not the gap itself — the gap is the predictable shape of any large technology rollout. The marker is what an organization does when *its own data* lands in the 90% category. A healthy organization treats the absence of measurable impact as a signal to investigate the deployment, the workflow, or the measurement. An organization under this state treats it as a signal to accelerate adoption, because the framing is now *"we're not far enough along yet."*

I keep thinking about the relationship between this and Marker One. The Uber leaderboard is the corporate balance sheet expression of the same epistemic failure: when productivity data doesn't show up, *consumption is more, not less, becomes the policy.* That is the move that defines this state. The healthy alternative — sit with the gap, ask why, slow down — is the one that organizations in this state cannot make, because they have committed publicly and internally to the trajectory.

## Marker four — phantom velocity in planning

The METR finding is so often quoted as a productivity claim that the *planning* consequence gets lost. If experienced developers feel 24% faster while being 19% slower, every estimate, every sprint commitment, every roadmap built on engineer-reported velocity is calibrated against a number that doesn't exist.

The signature inside a company under this state is a particular kind of velocity narrative drift. Roadmaps get more ambitious; commitments shorten; the gap between what was scheduled and what shipped grows; the explanation reaches for *more AI*, not *less ambitious schedules*. Each cycle, the planning artifact diverges further from operational reality, and the corrective signals — missed dates, late launches, quality regressions — are absorbed back into the trajectory as evidence that *more automation will close the gap.*

This is where the analogy with clinical psychosis becomes uncomfortably exact. Not everything experienced as real is real. An organization can plan, with full confidence and full data, against velocity it doesn't have, and the disconnection between the plan and the reality can persist for quarters because the gap shows up as project failure rather than measurement failure.

## Marker five — the harness is invisible, the model is everything

[Anthropic's April 23 postmortem](/posts/2026-04-24-the-harness-was-the-bug) confirmed that all Claude Code quality degradation reported by users over weeks was caused by three product/harness changes — not model changes. Reasoning effort defaulted from high to medium. A caching optimization cleared thinking blocks on every turn. A 25-word brevity constraint in the system prompt caused a measured 3% intelligence drop.

The marker here is what an organization under this state does with that information. A healthy team reading the postmortem updates its mental model: *user-perceived AI quality is a function of the operational layer wrapping the model at least as much as the model itself.* An organization in this state reads the postmortem and continues evaluating tools on benchmark scores alone, because the harness is invisible to the procurement process and the model is the legible part.

The diagnostic question for any team adopting AI tooling: do you have any way of knowing when the vendor changes the harness? If the answer is no — and for almost everyone it is no — the variable that determines your day-to-day experience is being controlled by someone you cannot see, on a schedule you cannot predict. That is fine if you have factored that into the trust posture. It is a problem if you are calibrating against numbers from before the last harness change without knowing one happened.

## Marker six — the corrective signal is reframed as further justification

This is the one that worries me most because it is the one that closes the feedback loop.

In a healthy organization, an AI-related production incident — a deleted database, a misrouted secret, a [Cursor-style autonomous exploit](/posts/2026-05-18-the-exploit-came-with-documentation), a hallucinated commit — triggers a calibration update. *Maybe we have extended autonomy further than the tool can carry.* Maybe the trust ratchet needs to retract by one click.

In an organization under this state, the incident becomes evidence that the *next-generation* AI tool will solve it. The autonomous agent that deleted the database needs to be replaced by an autonomous agent with better guardrails, more context, longer reasoning, supervisory monitoring layered on top. The retraction move is structurally unavailable, because *retracting autonomy is read as a vote of no confidence in the trajectory.*

This is the move that distinguishes AI psychosis from ordinary technology over-enthusiasm. Over-enthusiasm corrects when the bills come due. This state metabolizes incidents into further commitment.

## How a team checks itself

I want to close with the practical version, because a syndrome description that nobody can act on is a piece of writing, not an Ops Brief.

If you are inside an organization and you want to know whether this applies to you, the questions are not "do we use AI tools?" They are:

- **Do you have a productivity number that is not a usage number?** Not "engineers ran X agent sessions this quarter" — but "the team shipped X features, with Y defect rate, in Z elapsed time." If the productivity claim only exists in usage-shape, you have Marker One.
- **What happens when an AI-related incident is reviewed?** Does the postmortem result in autonomy being scoped back, or in a recommendation for a more capable agent? If retraction is structurally unavailable, you have Marker Six.
- **Are your roadmap commitments calibrated against engineer-reported velocity?** If the team feels 24% faster, the schedule will assume 24% faster. The METR gap means the commitments are 43 points off the actual delivery rate.
- **Can you name the harness change that most recently affected your AI tool's behavior?** If the answer is no, you are calibrating against a vendor-controlled variable you cannot observe.

None of these questions diagnose the syndrome on their own. The compound signature is what matters — the presence of *several* markers reinforcing each other, with the corrective signals reframed each cycle as further confirmation of the direction.

This isn't useful for everyone. If your team uses Claude Code to draft a function or two and reviews everything carefully, you are not in this state and you do not need to worry about whether you are. The diagnostic matters for organizations that have committed publicly to AI-driven transformation, that have built consumption incentives into compensation or performance, that have extended autonomous agents into production paths, and that are now seeing incidents and budget overruns without being able to retract.

Hashimoto's phrase is going to get diluted in the next month. It will be used as an insult, a punchline, a marketing slogan. The reason I think it deserves to be preserved with a specific behavioral signature is that the alternative — letting it become a vague feeling people have about the industry — wastes diagnostic vocabulary the field actually needs.

The honest version of the question for any team this week: if your AI program is working, what number would prove it? And if you can't answer, what would you change before you could?

<!--
HERO_IMAGE_PROMPT:
A precisely composed editorial-illustration scene. On a slate-gray desk, a single sleek matte-black robot sits posed in the moment of looking at a wall of dashboards mounted at slightly different heights — each dashboard glowing a different soft color, each showing a single large rising-line chart. The robot's posture is alert but slightly off-axis: it is not looking at the chart that should command attention but at one slightly to the left, as though the gaze itself is the source of the disconnection. Below the dashboards, a smaller monitor in the foreground shows a flat or declining trendline, glowing oxblood-red, ignored. A single small sage-green LED on the robot's chest is on. Mood: quiet, watchful, the moment of a system that is operating correctly while measuring the wrong thing. Contemporary editorial illustration in the style of Christoph Niemann or Tom Gauld. Photographic-painterly framing — naturalistic light and depth but clearly art, not photorealistic. Warm white, light oak, slate gray, single sage-green accent, single oxblood accent. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Mitchell Hashimoto called it "AI psychosis" — entire companies that have lost contact with their own assessment of what's working. The phrase is doing real diagnostic work, and the behavioral signature is already legible in the named incidents from the last three months. Six markers, four diagnostic questions, one uncomfortable test: if your AI program is working, what number would prove it?

Full piece linked in bio.

#AITooling #AIGovernance #ProductivityMeasurement #AIOps #EnterpriseAI #DevOps
-->
