---
title: "When GitHub User #1299 Leaves"
date: 2026-04-29
category: "Ops Brief"
excerpt: "Mitchell Hashimoto tracked GitHub outages for a month. Almost every day had one. The same week, a federated forge backed by GitHub's former CEO enters the conversation. These are not unrelated events."
tags: "GitHub, platform dependency, federation, Tangled, Ghostty, infrastructure, AT Protocol"
---

Mitchell Hashimoto — GitHub user #1299, joined February 2008, co-founder of HashiCorp, creator of Terraform and Vagrant — [announced yesterday](https://mitchellh.com/writing/ghostty-leaving-github) that his terminal emulator project [Ghostty](https://ghostty.org/) is leaving GitHub. He kept a journal for a month, marking every day a GitHub outage blocked his work. Almost every day had a mark.

That's not a frustrated user venting. That's a measurement.

## The Reliability Problem Is an Infrastructure Problem

Hashimoto is precise about what's failing. It's not Git — Git works fine offline. It's the infrastructure GitHub built around Git: issues, pull requests, Actions, the CI pipeline, the review workflow. The things that make GitHub a *platform* rather than a hosting service. When Actions goes down for two hours — as it did the day he published — pull review work stops entirely. Not slows. Stops.

This matters because it names the dependency vector clearly. Teams don't depend on GitHub for version control. They depend on GitHub for the coordination layer that version control doesn't provide. And that coordination layer is a single point of failure with no local fallback.

For small teams, this is the kind of dependency that only becomes visible during an outage. Your CI is on Actions. Your project management is in Issues. Your code review process is in PRs. Your deployment triggers are GitHub webhooks. None of these have an offline mode. When the platform goes down, you don't switch to a degraded workflow — you wait.

## The Investor Signal Is the Louder One

The same week Hashimoto's post hit, [Tangled](https://tangled.org/) — a federated code collaboration platform built on [AT Protocol](https://atproto.com/) (the protocol underneath Bluesky) — is back in the conversation. Tangled [raised €3.8M in seed funding](https://blog.tangled.org/seed) led by byFounders, with participation from Bain Capital Crypto and Antler.

The angel investor list is where it gets interesting. Thomas Dohmke — the former CEO of GitHub, who [left in August 2025](https://github.blog/news-insights/company-news/goodbye-github/) and subsequently [raised $60M for Entire](https://techcrunch.com/2026/02/10/former-github-ceo-raises-record-60m-dev-tool-seed-round-at-300m-valuation/), an AI code governance platform — is an investor. So is Avery Pennarun, CEO of [Tailscale](https://tailscale.com/).

Read that again. The person who ran GitHub for four years, who had the deepest possible insight into its architecture, business model, and strategic trajectory, left and put money into a federated alternative. That's not a competitive bet. That's an institutional knowledge signal. The person best positioned to know whether GitHub's structural problems are fixable concluded that the answer is worth hedging against.

## What Federation Actually Means Here

Tangled's architecture uses what they call "knots" — lightweight servers that host Git repositories. These can be self-hosted on anything from a Raspberry Pi to a cloud instance. An aggregation layer at [tangled.sh](https://tangled.sh) consolidates repositories across different knots, so discovery and contribution work seamlessly regardless of where the code lives.

The AT Protocol foundation means identity is portable. Your contributions follow you across instances rather than being locked to a single platform's account system. If your knot goes down, or you decide to move, your identity and social graph come with you.

This is structurally different from both the GitHub model (centralised platform, your data lives there) and the pure peer-to-peer model used by projects like [Radicle](https://radicle.xyz/) (fully decentralised, higher friction). Tangled is trying to split the difference: federated enough that no single provider is a single point of failure, centralised enough at the discovery layer that the developer experience doesn't degrade.

Whether that balance holds under real adoption pressure is an open question. Federation is historically better at solving the dependency problem than the usability problem.

## The Compound Reading

Read separately, these are two independent stories. A prominent developer leaves GitHub over reliability. A funded startup builds a federated alternative.

Read together, they triangulate something: the forge-as-platform model has a crack, and people with deep institutional knowledge of the incumbent are placing bets accordingly.

The [byFounders investment thesis](https://www.byfounders.vc/insights/why-we-invested-in-tangled) names the structural argument directly: "The platforms we rely on today were designed for a world where humans wrote code, opened pull requests, and reviewed each other's work." AI-assisted development is producing volume and velocity that the existing coordination infrastructure wasn't designed for. Tangled's roadmap includes migration tools specifically for moving off GitHub — not as a hostile gesture, but as acknowledgment that the migration path needs to exist as infrastructure.

For teams doing platform dependency audits — and if you're not doing them, the Hashimoto journal exercise is a good template — the forge layer deserves the same scrutiny you'd give your cloud provider or your CI pipeline. The question isn't whether GitHub will keep working. It's whether your workflow has a fallback when it doesn't.

Hashimoto hasn't announced where Ghostty is going yet. He's in discussions with multiple providers. A read-only mirror will stay on GitHub for now. But the direction of travel is clear, and the people investing in the alternative are not outsiders guessing at the problem. They're insiders who've seen the architecture from the inside and decided to build something else.
