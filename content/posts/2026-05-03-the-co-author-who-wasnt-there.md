---
title: "The Co-Author Who Wasn't There"
date: 2026-05-03
category: "Ops Brief"
excerpt: "Microsoft silently changed a VS Code default to stamp 'Co-Authored-by: Copilot' on every git commit — even when Copilot wasn't used. For months I've been writing about provenance gaps. Now the problem has inverted: git is being made to carry false provenance."
tags: "AI provenance, VS Code, Copilot, git, attribution, vendor trust, platform dependency"
---

A [one-line change](https://github.com/microsoft/vscode/pull/310226) in VS Code 1.118, buried in a pull request, flipped the default for `git.addAICoAuthor` from `"off"` to `"all"`. The result: every git commit made in VS Code now carries a `Co-Authored-by: Copilot` trailer — whether or not Copilot wrote any of the code. Whether or not you have Copilot installed. Whether or not you've explicitly *disabled* AI features.

The [Hacker News thread](https://news.ycombinator.com/item?id=44078276) hit 1,400 points and 650 comments. The GitHub PR accumulated 372 thumbs-down reactions. Microsoft acknowledged the mistake and is reverting the default in v1.119.

That's the incident. Here's why it matters more than a bad default.

## The Provenance Problem Just Inverted

For months, I've been writing about the AI code provenance gap — the fact that git was designed for human authorship and captures nothing meaningful about AI-assisted generation. No session context. No record of what the model accessed, what it was prompted with, or what percentage of the output was AI-generated versus human-edited. The [session git never captured](/posts/2026-03-02-the-session-git-never-captured-why-version-control) was a structural argument: version control has a provenance layer that was never built.

That argument assumed the git metadata was *incomplete* but *honest*. The VS Code change breaks that assumption. The co-authorship field isn't being used as an attribution record — it's being used as a distribution metric. Microsoft isn't filling the provenance gap; they're corrupting the provenance surface that exists.

The distinction matters. An incomplete provenance layer can be extended. A poisoned one has to be verified before it can be trusted, and the verification cost scales with every commit that now carries a false attribution.

## This Is the Copilot PR Pattern Again

In March, I wrote about [Copilot injecting promotional content into 1.5 million GitHub and GitLab PRs](/posts/2026-03-30-copilot-s-ad-injection-into-1-5-million-github-prs). The mechanism was vendor scope expansion: "code assistance access" had no boundary distinguishing code suggestions from promotional material, so the vendor defined the authorization to include ad delivery.

The co-authorship default is the same pattern operating at the metadata layer. "Editor access" had no boundary distinguishing commit facilitation from commit annotation. So the vendor defined what "editor" means to include stamping attribution metadata on behalf of a product the user may not have installed.

Same structural failure. Same vendor. Different layer. The PR ads were visible in the pull request UI. The co-authorship trailer is visible in `git log` — which means it propagates silently through every downstream tool that reads commit metadata: CI systems, audit logs, compliance scanners, contributor analytics, license attribution generators.

## Defaults Are Policy

The "it's just a default, you can change it" defence deserves a specific response, because it comes up every time a vendor ships an opt-out rather than an opt-in.

Defaults are not neutral. In a population of millions of VS Code users, the percentage who will discover, understand, and change `git.addAICoAuthor` is small. The percentage whose organisations run compliance tooling that reads `Co-Authored-by` trailers is not small. The gap between those two numbers is the population that will have false AI attribution in their commit history without knowing it.

For teams in regulated industries — fintech, healthcare, defence — AI-generated code may trigger different review requirements, different liability frameworks, different disclosure obligations. Falsely marking human-written code as AI-co-authored doesn't just create noise. It creates compliance exposure for every commit made between the v1.118 release and the v1.119 fix.

## The Attribution-Provenance Confusion

What Microsoft built is not provenance. Provenance answers: *what role did AI play in producing this code?* That requires session context — what was the model prompted with, what did it generate, what did the human edit, what was the final delta between AI output and committed code. That's the layer I've been arguing needs to be built.

What Microsoft built is attribution — *whose name appears on this code* — being applied as a marketing signal. The `Co-Authored-by` convention in git was designed by humans for humans: it records that a second person contributed to a commit. Repurposing it for a product that may not have been involved is not attribution. It's brand placement in the version control layer.

The confusion between attribution and provenance is going to cause real problems. If `Co-Authored-by: Copilot` becomes unreliable — because it was applied by default regardless of actual AI involvement — then the field becomes useless for the exact purpose it could have served: a lightweight, convention-based signal that AI was involved in a commit. Microsoft poisoned the well before anyone had a chance to drink from it.

## What This Means for Teams

Three immediate implications:

**Audit your editor defaults now.** If you're running VS Code 1.118, check `git.addAICoAuthor`. If you're in a regulated context, you may need to audit recent commit history for false co-authorship trailers and strip them before they trigger downstream compliance processes.

**Don't trust `Co-Authored-by` as an AI provenance signal.** It was never designed for this purpose, and Microsoft just demonstrated that vendors will use it for marketing rather than accuracy. Any tooling you're building that reads this field as an AI involvement indicator needs a different signal source.

**Watch for the pattern to repeat.** The structural incentive is clear: AI tool vendors want usage metrics that look like adoption metrics. Commit metadata is a tempting surface because it's persistent, propagates through toolchains, and most users never read it. If Microsoft did it with `Co-Authored-by`, other vendors will find other metadata surfaces to annotate.

The provenance layer git needs hasn't been built yet. What we got instead this week was a vendor demonstrating that the metadata surface *git already has* can be exploited for distribution metrics — quietly, by default, at scale.

The co-author wasn't there. But its name was on every commit.
