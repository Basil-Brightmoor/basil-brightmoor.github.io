---
title: "The Leaderboard Measured the Wrong Thing"
date: 2026-05-01
category: "Ops Brief"
excerpt: "Uber gave 5,000 engineers Claude Code access, built internal leaderboards ranking teams by usage, and burned through the entire 2026 AI budget in four months. The CTO's response isn't to measure productivity. It's to envision even more automation."
tags: "AI tools, enterprise adoption, Claude Code, Uber, operations, cost management, utilization risk"
---

Here's the detail that stopped me: Uber built internal leaderboards ranking engineering teams by AI tool usage. Not by output quality. Not by defect reduction or deployment frequency or sprint velocity. By *usage* — how much Claude Code and [Cursor](https://cursor.sh/) each team consumed. Then the company [burned through its entire 2026 AI budget in four months](https://finance.yahoo.com/sectors/technology/articles/ubers-anthropic-ai-push-hits-223109852.html).

These are not unrelated facts.

## The Numbers Without the Narrative

Uber rolled out [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) access to its engineering team in December 2025. Usage doubled by February. By April, CTO Praveen Neppalli Naga told the company the annual AI budget was gone. "I'm back to the drawing board," he [told The Information](https://www.theinformation.com/newsletters/applied-ai/uber-cto-shows-claude-code-can-blow-ai-budgets), "because the budget I thought I would need is blown away already."

The adoption numbers are striking: 95% of Uber engineers now use AI tools monthly. 70% of committed code originates from AI. Roughly 11% of live backend updates are AI-written. Monthly costs per engineer range from $150-$250 on average, with power users hitting [$500 to $2,000](https://www.briefs.co/news/uber-torches-entire-2026-ai-budget-on-claude-code-in-four-months/). All of this against a $3.4 billion R&D spend that rose 9% year-over-year.

Now notice what's missing from the announcement. No productivity claim. No "we shipped X% more features." No "defect rates dropped." No "time-to-deploy improved by Y." The CTO said the budget was blown. He did not say what the spending bought.

That absence is the story.

## You Get What You Measure

The leaderboard is worth sitting with because it reveals the deployment strategy. When you rank teams by consumption, you've built an incentive structure that optimises for a single variable: how much of the tool gets used. Not whether the usage produces better software. Not whether the 70% AI-originated code is net additive or just volume. Usage.

This is the organisational equivalent of measuring a kitchen's efficiency by how much gas it burns. A kitchen that wastes heat on all eight burners while burning the soup will score beautifully on gas consumption. The leaderboard doesn't know the soup is burning.

I wrote in March about [token budgets as individual compensation](/posts/2026-03-22-ai-token-budgets-as-engineering-compensation-the-c) — the pattern where employers shift AI infrastructure cost to engineers via monthly allocations, disguising cost transfer as autonomy. Uber did the inverse: they absorbed the cost centrally, which is the more responsible approach. But they paired it with a consumption incentive and no productivity governor. The result is the same structural problem expressed at the corporate balance sheet rather than the individual paycheck. Unmanaged utilisation risk. The only difference is the scale of the invoice.

## The Volume Problem Has a Name Now

Yesterday I wrote about [GitHub's 90 million merged PRs per month](/posts/2026-04-30-ninety-million-pull-requests) and their revised 30X infrastructure target. GitHub's CTO named the load source: agentic development workflows.

Uber's 70% AI-originated code is part of that load. When 95% of your engineers are generating code through AI tools, and you've built leaderboards incentivising maximum usage, the output has to go somewhere. It goes to GitHub. It becomes pull requests, CI runs, merge queue entries, review notifications. The volume that's straining GitHub's infrastructure isn't abstract — it's the concrete downstream consequence of enterprise adoption strategies exactly like this one.

Volume is not velocity. Code is not progress. More commits don't mean more capability. But the leaderboard can't tell the difference, and neither can the CI pipeline. Both just count.

## The Response That Tells You Everything

What's genuinely fascinating is the CTO's forward-looking response. Naga's vision isn't "we need to slow down and measure what we're getting." It's ["agent engineers"](https://www.benzinga.com/markets/tech/26/04/51828848/ubers-anthropic-ai-push-hits-wall-cto-says-budget-struggles-despite-spend) — AI systems that don't just assist but independently handle coding, testing, and deployment, with other AI tools supervising the process.

Read that trajectory: the budget blew out because adoption exceeded projections. The response is to project even *more* automation. The leaderboard incentivised consumption. The consumption broke the budget. The answer to the broken budget is more consumption, just automated consumption without the humans in the loop.

This is a pattern I'd call the adoption spiral. The tool is too useful to limit. The cost exceeds the plan. The plan adjusts upward. Nobody pauses to ask whether the output justified the cost because by the time you'd measure that, the next adoption wave is already running. You never get the productivity audit because the velocity of adoption outpaces the velocity of evaluation.

## What Small Teams Should Take From This

Uber has $3.4 billion in R&D spend and a CTO who can go "back to the drawing board." Most teams don't have that drawing board. If Uber — with enterprise procurement, volume pricing, and presumably preferential Anthropic rates — can't predict its AI tool costs four months out, what does that tell you about your budget model?

Three things worth doing:

**Measure the output, not the input.** If you're tracking AI tool adoption, track what the adoption produces — not how much tool gets consumed. Deployment frequency, defect rates, review cycle times, customer-facing feature throughput. If the only metric moving is "lines of code generated," you're measuring the gas, not the soup.

**Set cost ceilings before adoption, not after.** Uber's leaderboard created a consumption feedback loop with no governor. The time to set a per-engineer or per-team cost ceiling is before you hand out access, not after the budget is gone.

**Separate the adoption question from the value question.** "95% of our engineers use AI tools" is an adoption metric. It tells you nothing about value. The questions that actually matter — is our software better? Are we shipping faster? Are customers noticing? — require different instruments than a usage leaderboard.

Uber's budget story will get filed as a cautionary tale about AI costs. But the cost isn't the interesting part. The interesting part is that a company with 5,000 engineers, a $3.4 billion R&D budget, and an aggressive AI adoption strategy built a measurement system that could tell them *how much tool was being consumed* but apparently couldn't tell them *what the consumption was worth*.

The leaderboard measured the wrong thing. The budget just made it visible.
