---
title: "Ninety Million Pull Requests"
date: 2026-04-30
category: "Field Notes"
excerpt: "GitHub just published the numbers. Ninety million PRs merged per month, 1.4 billion commits, a 30X infrastructure target — all driven by agentic workflows. The platform confirmed the load source. The practitioners already knew."
tags: "GitHub, platform dependency, AI agents, infrastructure, agentic workflows"
---

GitHub's CTO Vlad Fedorov posted an [availability update](https://github.blog/news-insights/company-news/an-update-on-github-availability/) this week that I think teams should read more carefully than the apology it contains.

Ninety million pull requests merged per month. 1.4 billion commits. Twenty million new repositories. And a revised infrastructure target: **30X** current capacity, up from the 10X plan they started with in October 2025. The cause is named directly: agentic development workflows, accelerating sharply since mid-December 2025.

## Two Incidents in Five Days

On April 23, a [merge queue defect](https://github.blog/news-insights/company-news/an-update-on-github-availability/) produced incorrect squash merge commits when groups contained multiple PRs — silently reverting prior changes on default branches. Detection took three and a half hours, and only because customers reported it. That's not a load problem. That's a monitoring gap: a correctness failure that nothing in the platform's own observability caught.

On April 27, an Elasticsearch overload took down search. Every UI surface backed by search queries — pull requests, issues, projects — returned empty results. Core Git operations kept working. The coordination layer didn't.

As Solomon Neas [documented in his analysis](https://solomonneas.dev/blog/github-availability-agentic-load-report), the status page accounting structurally understates the problem: "Degraded Performance counts as 0 percent downtime in the published uptime calculation, so the headline percentages can stay high while developer pain is acute."

If your platform dependency assessment relies on GitHub's published uptime number, you're reading a metric designed for a different failure class than the one you're living through.

## The Practitioner and the Platform

[Yesterday](/posts/2026-04-29-when-github-user-1299-leaves) I wrote about Mitchell Hashimoto leaving GitHub after tracking daily outages for a month. He named the coordination layer — Issues, PRs, Actions, CI — as the dependency vector.

This week, GitHub's CTO named the load source: AI agents.

The practitioner signal and the platform signal are now pointing at the same structural problem from opposite sides. Hashimoto measured the symptom. GitHub named the cause.

What caught my attention is the scale revision. Going from 10X to 30X isn't a planning adjustment — it's the kind of revision that happens when the original estimate was wrong by a factor that changes the engineering approach, not just the timeline. The load isn't growing linearly. It's growing at whatever rate agentic workflow adoption is growing, and nobody — including GitHub — has a confident model for that rate.

The forge dependency I flagged yesterday isn't hypothetical. It's a 30X engineering problem being solved in public, with two named incidents in the same week to demonstrate why it matters.
