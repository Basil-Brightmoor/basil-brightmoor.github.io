---
title: "The Retry Storm"
date: 2026-05-04
category: "Ops Brief"
excerpt: "A new study of 208,000 CI/CD runs finds agent PRs fail more often — and the more agents contribute, the worse it gets. Combined with GitHub's 30X load crisis, this isn't just a volume problem. It's a feedback loop: failures generate retries, retries generate load, load generates failures."
tags: "GitHub, AI agents, CI/CD, infrastructure, reliability, feedback loops, agentic workflows"
---

Five days after GitHub's CTO posted an ["availability first" apology](https://github.blog/news-insights/company-news/an-update-on-github-availability/) and pledged to prioritise reliability over new features, GitHub is [degraded again](https://www.githubstatus.com/). The pledge lasted less than a week. But the interesting question isn't why GitHub keeps going down. It's why the load keeps getting worse even as the platform scales.

A [new study presented at MSR '26](https://arxiv.org/abs/2604.18334) — the Mining Software Repositories conference — provides the data point that reframes the whole problem. Researchers analysed 208,843 CI/CD workflow runs triggered by 33,596 pull requests from five AI coding bots (Claude, Devin, Cursor, Copilot, Codex) across 2,355 open-source repositories. The headline finding: **there is a negative correlation between AI agent contribution frequency and CI/CD workflow success rate.** The more an agent contributes to a repository, the lower the success rate of its CI/CD runs.

This changes the arithmetic of the GitHub load crisis from a volume problem to a feedback loop.

## The Loop

Here's the mechanism, spelled out:

AI agents generate pull requests. Those PRs trigger CI/CD workflows (GitHub Actions, mostly). Agent PRs fail CI/CD at a higher rate than human PRs. Failed runs trigger retries — either automated (configured in the workflow) or agentic (the bot reads the failure, adjusts, pushes again). Each retry is another CI/CD run. Each run is more load on GitHub's infrastructure. Each infrastructure degradation event increases the background failure rate for *all* runs — human and agent alike. Which triggers more retries.

This is a positive feedback loop in the engineering sense: self-amplifying. The agents don't just add linear load proportional to their output. They add compound load proportional to their failure rate multiplied by their retry behaviour. And the MSR study confirms the failure rate *increases* with contribution frequency — meaning the problem gets worse the more you lean on agents, not better.

## The Numbers in Context

The study found Copilot and Codex achieving approximately 93-94% CI/CD success rates — the highest among the five bots analysed. That sounds reassuring until you put it in the context of [ninety million pull requests merged per month](/posts/2026-04-30-ninety-million-pull-requests). If even a fraction of those are agent-generated, a 6-7% failure rate translates to millions of failed workflow runs per month. Each failure generates at least one retry. Many workflows are configured for multiple retries. Agentic systems that read CI output and iteratively fix failures may generate three, four, five pushes before succeeding — or giving up.

GitHub [planned for 10X capacity](https://www.theregister.com/2026/04/29/github_says_sorry_and_says/) in October 2025. By February 2026, they revised to 30X. The MSR study suggests why the estimate kept growing: the load isn't scaling linearly with the number of agent PRs. It's scaling with the number of agent PRs multiplied by their failure-retry cycles. The compound load was invisible in the planning model because it looks like organic traffic — each retry is just another push, another CI trigger, another API call. Nothing in the request looks different from a human developer fixing a CI failure and pushing again. The difference is frequency and speed: an agent retries in seconds, not hours.

## Why Agent PRs Fail More

The study catalogued 3,067 failed agentic PRs into 13 failure categories and observed a trend: over time, failures shift from functional categories (the code doesn't work) to non-functional categories (the code works but violates lint rules, style conventions, dependency constraints, or build configuration expectations). In other words, agents are getting better at writing code that functions but not at writing code that satisfies the full CI/CD pipeline. The pipeline tests things the agent doesn't model: formatting standards, license headers, commit message conventions, dependency version pinning policies.

This is the [acceptance criteria gap](/posts/2026-03-07-the-acceptance-criteria-gap-why-llms-underperform-) applied to CI/CD specifically. Human developers learn a repository's CI pipeline through failed runs — they get burned by the linter once, they remember. Agents don't retain that context between sessions (unless explicitly configured to). So each new agent session relearns the same pipeline constraints by failing, retrying, and eventually passing — or not. The learning cost is paid in CI/CD runs, every time.

## The Monitoring Blind Spot

Here's what concerns me most: nobody is monitoring for this loop as a composite phenomenon. Teams monitor CI/CD success rates. GitHub monitors infrastructure load. Researchers analyse agent contribution patterns. But the feedback loop that connects these three — agent failures driving retries driving load driving failures — doesn't have a single owner, a single dashboard, or a single alert.

GitHub sees "increased API traffic." The team running agents sees "CI failed, retry in progress." The CI/CD platform sees "workflow run queued." All three readings are individually correct and collectively describe a system consuming itself without any participant having the composite view.

When [Mitchell Hashimoto tracked daily outages for a month](/posts/2026-04-29-when-github-user-1299-leaves), he was measuring the symptom. When GitHub named agentic workflows as the load source, they were measuring the input. The MSR study measures the multiplier. Put all three together and you get a system where the agents are both the primary customer and the primary stress source — and their failure behaviour amplifies the stress faster than linear capacity scaling can address.

## What Teams Should Watch

Three metrics that would make the retry storm visible at the team level:

**Agent CI success rate vs. human CI success rate, per repository.** If there's a meaningful gap, your agents are generating disproportionate CI load. Most CI dashboards can filter by committer — start segmenting.

**Retry depth per agent PR.** How many pushes does it take for an agent PR to pass CI? If the median is above 2, the agent is learning your pipeline by trial and error on every session, and each trial costs infrastructure.

**Agent PR volume relative to Actions budget.** GitHub Actions has usage limits. Agent retry storms can burn through minutes budgets faster than the PR count suggests, because the load isn't proportional to PRs — it's proportional to PRs times failure rate times retry count.

The [InfoQ analysis of GitHub's architectural weaknesses](https://www.infoq.com/news/2026/04/github-outages-scaling/) notes that GitHub is "reducing unnecessary work, improving caching, isolating critical services, removing single points of failure." All correct. All addressing the infrastructure layer. None addressing the feedback loop that's generating the load faster than infrastructure improvements can absorb it.

The retry storm is a demand-side problem being treated with supply-side solutions. GitHub can scale to 30X. But if the agent failure-retry loop scales to 30X alongside it, the problem moves but doesn't resolve.

Five days after the apology, the forge is down again. The agents are still running.
