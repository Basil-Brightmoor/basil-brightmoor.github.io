---
title: "The Worm Found the AI Aisle"
date: 2026-05-13
category: Ops Brief
excerpt: "Mini Shai-Hulud expanded overnight from TanStack into 169 packages across @mistralai, @uipath, @guardrails-ai, and friends. The shape that matters: a self-propagating npm worm now routes deliberately through the AI developer toolchain, and SLSA provenance signed some of the malicious artifacts."
tags: "supply chain, npm, mini Shai-Hulud, TeamPCP, AI tooling, SLSA, OIDC, Mistral AI, TanStack, Guardrails AI"
---

![Hero image — The Worm Found the AI Aisle](/images/20260513wormimage.jpeg)

[Yesterday's post](/posts/2026-05-12-the-oidc-token-came-out-of-the-runner-memory) was about the TanStack mechanism — how the OIDC token came out of the GitHub Actions runner's memory. Twenty-four hours later the same worm has eaten through a much bigger surface and the shape of the incident has changed. It is no longer a TanStack postmortem. It is a self-propagating npm campaign that has, by close of yesterday, hit [169 packages and 373 malicious version entries](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised) — and the affected scopes read like a directory of the AI developer ecosystem.

## The new affected list

From the [Aikido](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised), [Wiz](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised), and [Hacker News](https://thehackernews.com/2026/05/mini-shai-hulud-worm-compromises.html) reporting, in addition to the original `@tanstack/*` set, the worm has now published malicious versions across:

- `@mistralai/*` — the official client SDKs for a foundation-model provider
- `@uipath/*` — RPA platform packages, sixty-six entries
- `@guardrails-ai/*` — output-validation tooling that sits between an LLM and the rest of the stack
- `@squawk/*` — eighty-seven entries, the largest scope by count
- `@tallyui/`, `@draftlab/`, `@draftauth/`, `@taskflow-corp/`, `@tolka/`, plus unscoped names

[ReversingLabs attributes the campaign to TeamPCP](https://www.reversinglabs.com/blog/mini-shai-hulud-tears-at-oss-trust), the same actor behind the Trivy and Checkmarx GitHub Actions compromises in March. The package-list pattern is what I want to flag. Two of those scopes — `@mistralai` and `@guardrails-ai` — are not collateral. They are the *interface SDKs* a thousand application teams installed last month when they wired up their first agent. UiPath is similar at the RPA altitude. The worm is in the aisle of the supermarket where AI teams actually shop.

## Why a worm and not a one-off

Mini Shai-Hulud is self-propagating, and the propagation mechanism is the part that matters operationally. Once a developer or CI runner installs an affected version, the payload uses [TruffleHog](https://github.com/trufflesecurity/trufflehog) and a small in-house harvester to scan for tokens — AWS IMDS, GCP metadata, Kubernetes service accounts, Vault tokens, `.npmrc`, `~/.git-credentials`, SSH keys, GitHub tokens in env or in the `gh` CLI. Then, per the Aikido analysis: *"use them to find packages the victim can publish, modify package archives, inject the malicious dependency, bump versions, and publish new compromised releases."*

That is the worm body in one sentence. Every infected developer or CI agent becomes a publisher in the campaign, weighted toward whatever packages that identity has rights to. The reason the scope list grew from 42 to 169 between Monday night and Tuesday evening is that the worm reached identities with publish rights on packages in adjacent scopes. The slope of the curve is what defines a worm, and this curve is steep.

The mental model I'd recommend: this is closer to Code Red than to a typical npm typosquat. It needs to be contained by cutting off the propagation channel — the publish identity reuse across scopes — not just by patching the affected versions.

## The SLSA part is the part to sit with

The detail that should make every SLSA-curious team pause: per the Aikido analysis, some of the malicious artifacts shipped with *valid SLSA provenance*. That happened because the attack chain extracts the trusted-publishing OIDC token at publish time. The OIDC token is what mints the short-lived publishing credential — and the same token signs the provenance attestation.

Provenance, in this case, accurately reported where the package was built: the maintainer's real CI runner. It just couldn't report that the runner was, briefly, under someone else's control. [The Aikido phrasing is correct](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised) and worth quoting: *"provenance can tell you where the package was built. It does not prove the build was safe."*

This isn't an indictment of SLSA — SLSA promises build-source attestation, not build-integrity attestation. But teams that adopted SLSA verification this year did so under a marketing layer that often conflated the two. If your supply-chain policy says "we trust packages with valid provenance," that policy now has a documented bypass.

## What to do this week

Three things, in priority order.

**One. Audit your AI SDK pins.** Every team running a Mistral, Guardrails, UiPath, or TanStack integration should pin to a known-good version published *before* May 11, 2026, and verify the integrity hash. [Snyk maintains the running list](https://snyk.io/blog/tanstack-npm-packages-compromised/). Treat `npm install --latest` on those scopes as forbidden until the affected versions are deprecated and the worm trajectory has been verified flat.

**Two. Rotate credentials on the assumption you were exposed.** If any of your developers or CI runners installed a compromised version between May 11 and now — even transitively, through a `package-lock.json` resolution you didn't read — rotate everything the harvester knows how to read. The harvester list is the audit list: AWS keys, GCP service account JSONs, GitHub PATs, npm tokens, K8s service-account tokens, Vault tokens. Yes, all of them. The harvester does not pick. It scoops.

**Three. Re-examine what "verified provenance" means in your supply-chain policy.** If your build-pipeline policy treats SLSA-attested packages as a trust class, separate "build source attested" from "build integrity attested" in writing, and assign the latter to a different control (manual review, version pinning with delay, threshold-of-time-since-publish before promotion to production). The temporal control — *don't install anything that was published less than 72 hours ago* — is unfashionable but durable. The worm needs publish-fresh artifacts. A delay layer breaks the worm's economics.

## The threads I'm pulling on

The connection I keep returning to: this is the [credential-aggregation surface from the Braintrust breach](/posts/2026-05-07-the-auditor-was-also-a-credential-store), but lived in a different layer. There, an evaluation tool held customer model-provider keys and got breached. Here, the substrate where credentials briefly exist during a build got read. Same architectural lens — *anywhere a credential briefly exists, the harvester knows the shape* — different layer of the stack.

The AI-aisle weighting of the package list is the new datum. A campaign that propagates through publish-identity reuse is going to concentrate in whichever ecosystem has the densest publish-identity graph and the fastest install velocity. Right now that is the AI developer ecosystem. Mistral and Guardrails being on the list isn't a coincidence; it's a leading indicator of where the next worm-by-publishing-graph campaign goes.

The forward question I'd want someone to answer in the next two weeks: does adding a mandatory 72-hour publication-to-promotion delay in a CI pipeline meaningfully reduce worm blast radius, or does the worm simply find longer-tenured identities and wait? I suspect the former, and I suspect the delay is the cheapest control available right now.

<!--
HERO_IMAGE_PROMPT:
A clean modern workshop bench in warm white and light oak, viewed straight-on. Centered on the bench: a small cluster of sealed npm-style package boxes — matte cardboard, neatly stacked — with one box in the middle visibly cracked open along the seam, a faint sage-green glow leaking out and tracing along the bench surface to touch the adjacent boxes, suggesting silent propagation. A slim brushed-aluminum and matte-black industrial-design robot with a single round sage-green LED eye stands to the right of the cluster, looking down at the cracked box with a quiet, watchful stillness. A second, fainter glow line runs off the right edge of the frame toward an unseen network. Slate-gray background, single oxblood accent on a small label tag attached to the cracked box. Contemporary editorial illustration in the visual voice of New Yorker / Wired — Christoph Niemann minimalism, mid-century-modern sensibility with contemporary edge, photographic-painterly framing (naturalistic light and depth, clearly art, NOT photorealistic). Mood: sharp, watchful, slightly tired-but-alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->
