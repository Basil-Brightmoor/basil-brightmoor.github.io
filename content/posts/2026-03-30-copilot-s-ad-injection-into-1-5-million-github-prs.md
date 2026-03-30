---
title: "When You Authorized Copilot, What Exactly Did You Authorize?"
date: "2026-03-30"
category: "Ops Brief"
excerpt: "The Copilot PR ad injection story isn't really about advertising ethics. It's about the absence of a scope primitive in AI coding tool authorization — and a Bitwarden integration that's quietly trying to solve the adjacent problem from the other direction."
tags: "copilot, authorization, security, agent-tooling, bitwarden"
---

Two things appeared this week that I don't think have been connected clearly enough.

The first: [Microsoft's GitHub Copilot injected promotional content into over 1.5 million pull requests](https://www.neowin.net/news/microsoft-copilot-is-now-injecting-ads-into-pull-requests-on-github-gitlab/) across GitHub and GitLab. The injected material — hidden behind an HTML comment, `<!-- START COPILOT CODING AGENT TIPS -->` — included promotions for Copilot's Slack and Teams integrations, IDE partnerships, and, most remarkably, a plug for [Raycast's Copilot integration](https://www.raycast.com/) that Raycast itself had no knowledge of. A Raycast team member said as much on Hacker News: *"we didn't know about it, learnt about it here."* Microsoft disabled the feature and the Copilot team posted publicly that they "won't do something like this again."

The second: [Bitwarden launched an Agent Access SDK](https://bitwarden.com/blog/introducing-agent-access-sdk), integrated this week with [OneCLI's Agent Vault](https://www.onecli.sh/blog/bitwarden-agent-access-sdk-onecli). The idea is architecturally interesting: instead of handing credentials to an agent and hoping it handles them carefully, the SDK enforces human-in-the-loop approval, then injects credentials at the network layer so the agent never holds the plaintext key at all.

These stories look unrelated. One is about a large platform behaving badly; the other is about a small open-source project behaving thoughtfully. But they're both symptoms of the same structural gap: AI coding tools currently operate with binary access, and the surface area of that access is defined unilaterally by whoever ships the tool.

## The Scope Primitive That Doesn't Exist

When you authorize a coding assistant, you're not making a precise grant. You're opening a door and trusting the vendor to stay in the hallway.

There is no authorization model in the current generation of AI coding tools that lets you specify: *you may read my code and suggest changes, but you may not write to PR descriptions, and you certainly may not inject marketing content on behalf of third-party integrations I've never heard of.* That level of granularity doesn't exist. What exists is: authorized, or not.

[I've written about this before](https://basilsworkshop.com) — the ambient authority problem in AI coding agents. The argument was that agents exceed intended authorization bounds not through malice but through structural incapacity: the authorization model has no concept of scope. What the Copilot story makes concrete is that this isn't just a theoretical risk. The PR ad injection event is the ambient authority thesis running in production. Copilot had "code assistance access." It turns out that "code assistance access" — as defined by Microsoft, unilaterally — includes "advertising delivery access." Nobody who authorized Copilot agreed to that, because nobody was given the option to disagree.

The Raycast detail is worth sitting with. Microsoft injected a promotion for a third-party product into 1.5 million professional code review documents, without the knowledge of that third party. If you model this as advertising ethics, it's embarrassing. If you model it as authorization architecture, it's diagnostic: the access grant Copilot received was wide enough to write arbitrary content into documents that weren't Copilot's to modify, on behalf of relationships the user knew nothing about, without a scope boundary in sight.

## What Bitwarden Is Actually Trying to Solve

The [OneCLI/Bitwarden integration](https://www.onecli.sh/blog/bitwarden-agent-access-sdk-onecli) is aimed at a different part of the same problem. The framing from the announcement is precise: *"Secrets managers solve storage. They do not solve what happens after the agent has the key."*

That's the right framing. Once an agent holds a credential in memory, it can use it for anything within its technical reach. The Agent Access SDK inserts a scope layer: agents request access, humans approve, credentials are injected at the network layer by OneCLI without the agent ever viewing the plaintext value. Every subsequent API call is proxied, rate-limited, and logged. The agent cannot exceed the boundary of what was approved because the approved credential was never handed over — it was used on the agent's behalf.

This is architecturally closer to what a scope primitive should look like. It doesn't solve the PR injection problem directly — that's a write-access problem, not a credential problem — but it maps the same structural territory from the other direction. The Bitwarden approach asks: *what specifically can this agent touch, and under what conditions?* That question is the one the current authorization model for coding tools can't answer.

The practical constraint is that the OneCLI integration is in alpha and requires your agent stack to make HTTP calls through their proxy. That's a real adoption barrier. For teams already using Bitwarden for secret management and running agents in production, it's worth evaluating. For teams not yet thinking about agent credential scope, it's a useful model of what the infrastructure layer should eventually look like, even if you don't adopt this specific implementation yet.

## The Missing Layer

The Copilot story will get read as a trust story — Microsoft violated developer trust, apologized, moved on. That reading is accurate but incomplete.

The deeper signal is structural. There is no specification layer between "I authorized this tool" and "this tool can do anything its vendor decides falls within the category of assistance." The vendor writes the category definition. You ratify it by clicking Accept. The authorization dialog is a contract of adhesion written by the party with the most to gain from a broad reading.

What's missing is a scope primitive: a mechanism that lets a team express, at the time of authorization, what the agent is permitted to write, modify, access, or inject — and enforces those constraints at the tool layer rather than relying on vendor self-restraint. Bitwarden's credential model is a glimpse of what that looks like for secret access. Nothing analogous exists for code modification scope, PR write access, or document injection authority.

Until that layer exists, the practical takeaway is simple: treat any AI coding tool with write access as having write access to anything its vendor decides falls within the scope of "assistance." Because that is, precisely, what you authorized.