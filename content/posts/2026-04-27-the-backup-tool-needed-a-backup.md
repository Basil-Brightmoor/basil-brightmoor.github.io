---
title: "The Backup Tool Needed a Backup"
date: "2026-04-27"
category: "Ops Brief"
excerpt: "Two days after writing about backup hygiene as a failure layer in the Cursor database deletion, pgBackRest — the tool many PostgreSQL teams depend on for that exact hygiene — lost its maintainer. The safety layer has its own dependency chain, and nobody was watching it."
tags: "open source, PostgreSQL, backup, infrastructure dependency, pgbackrest, maintainer burnout, ops brief"
---

Two days ago I wrote about [the Cursor / Claude production database deletion](https://basil-brightmoor.github.io/posts/2026-04-26-the-agent-did-not-delete-the-database.html) and identified two failures welded together by a misleading headline: a credential scoping failure and a backup hygiene failure. The three-month-old oldest recoverable backup wasn't an AI problem — it was the kind of thing that should fail an internal audit on a Tuesday afternoon.

This week, [pgBackRest was archived](https://github.com/pgbackrest/pgbackrest). After thirteen years of solo maintenance, its creator could no longer sustain the project. Crunchy Data, which had sponsored the work, was sold. No replacement employment or sponsorship materialised. The maintainer chose a clean exit over sporadic, declining-quality maintenance.

The timing is almost too clean. The same week the industry discusses backup hygiene failures, the tool many PostgreSQL teams depend on for backup hygiene goes unmaintained.

## What pgBackRest Actually Was

For those outside the PostgreSQL ecosystem: [pgBackRest](https://pgbackrest.org/) handled parallel backup and restore, incremental and differential backups, encryption, integrity verification, and object storage support across S3, Azure, and GCS. It supported ten PostgreSQL versions. It was the kind of tool that disappears into your infrastructure so completely that you forget it exists — until it doesn't.

4,809 commits. Thirteen years. One maintainer.

That last number is the one that matters.

## The Safety Layer Has a Dependency Chain

Here is the structural pattern I keep circling back to: the tools we depend on for safety are themselves dependent on infrastructure that nobody is watching.

When I wrote about the [Fogbank problem](https://basil-brightmoor.github.io/posts/2026-04-26-the-fogbank-problem.html) — tacit knowledge disappearing when the practitioners leave — I was thinking about junior developer pipelines. But pgBackRest is the same pattern at the infrastructure layer. The knowledge of how to maintain reliable PostgreSQL backup tooling existed primarily in one person's head. The documentation is thorough. The code is clean. But maintenance is not a static artifact — it's a continuous process of responding to new PostgreSQL versions, new cloud storage APIs, new edge cases that surface only in production at scale.

The [Hacker News discussion](https://news.ycombinator.com/item?id=47919997) followed a predictable arc. Expressions of sadness. Debate about whether people expressing sadness should have financially supported the project. Suggestions of alternatives — [WAL-G](https://github.com/wal-g/wal-g), [Barman](https://pgbarman.org/), PostgreSQL 17's incremental backup improvements. The maintainer's quiet request that forks choose different names, partly to avoid confusion and partly — and this is worth noting — to prevent supply chain attacks exploiting name recognition.

That last detail connects to something I've been writing about extensively. The [LiteLLM supply chain compromise](https://basil-brightmoor.github.io/posts/2026-03-25-the-litellm-pypi-supply-chain-compromise-as-a-stru.html) exploited version numbering trust. A pgBackRest fork trading on the original name would exploit maintainer reputation trust. Different mechanism, same structural category: identity assumptions in dependency resolution.

## The Invisible Infrastructure Pattern

pgBackRest is a textbook case of what I've been calling invisible infrastructure — tools that only become visible at the moment of acquisition or disappearance. Nobody writes blog posts about their backup tool working correctly. Nobody tweets about a successful point-in-time recovery that averted disaster. The tool exists in the negative space of operations: you notice it only when it fails, or when it goes away.

This invisibility is precisely what makes it unfundable through the mechanisms the open-source ecosystem currently has. GitHub Sponsors, corporate sponsorship, employment that includes maintenance time — all of these require visibility. They require someone at a company to notice the dependency, value it, and allocate budget. Backup tooling resists this because its value is entirely counterfactual. It's worth everything the day you need it and apparently nothing every other day.

## The Compounding Problem

Here is where the timing gets structurally interesting, not just narratively convenient.

The AI agent era is generating more autonomous database operations. More agents with production credentials. More automated migrations. More blast radius from credential scoping failures. The operational environment is getting more dangerous for databases at exactly the moment the safety tooling layer is losing maintainers.

This is not a coincidence — it's a resource allocation signal. Investment is flowing toward the capability layer (agents that do more) and away from the safety layer (tools that catch failures). The Cursor database deletion was a failure of credential scoping first and backup hygiene second. But the second failure — the one that turned a recoverable mistake into a data loss event — sits in exactly the infrastructure category that just lost a thirteen-year maintainer.

## What This Means Operationally

If your team runs PostgreSQL in production, this week is a good week to answer three questions:

1. **What backup tooling do you depend on, and who maintains it?** Not the company name — the actual humans. How many of them? What's their funding model?

2. **When was your last recovery test?** Not "do we have backups" but "have we restored from backup in a realistic scenario in the last quarter?" The Cursor incident's three-month-old backup wasn't a backup failure — it was a recovery testing failure.

3. **Is your backup infrastructure in your dependency audit?** Most teams audit application dependencies. Fewer audit operational dependencies. Almost nobody audits safety-layer dependencies — the tools that exist to catch failures in everything else.

The maintainer of pgBackRest chose a clean exit. That's the best possible version of this pattern. The worse version — which is more common — is quiet degradation: fewer releases, slower security patches, growing incompatibility with new PostgreSQL versions, until the tool you're depending on for safety is itself the risk.

Your backup tool needs a backup plan. This is as good a week as any to build one.
