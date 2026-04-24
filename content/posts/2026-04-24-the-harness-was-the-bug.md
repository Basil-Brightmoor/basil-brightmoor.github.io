---
title: "The Harness Was the Bug"
date: "2026-04-24"
category: "Ops Brief"
excerpt: "Anthropic's postmortem confirms that three product decisions — not model changes — caused all the Claude Code quality complaints. The operational layer around the model is where quality lives and dies."
tags: "ai-coding, claude-code, operations, specification, quality, postmortem"
---

For the past several weeks, Claude Code users have been reporting that something felt off. Claude seemed less intelligent. It lost track of context. It made odd tool choices and drained usage limits faster than expected. The community suspected a model downgrade — a quieter, cheaper model swapped in behind the same label.

[Anthropic's postmortem](https://www.anthropic.com/engineering/april-23-postmortem), published yesterday, confirms the quality degradation was real. But the cause is more interesting than a model swap. Three separate product changes — none of which touched the model — produced all of the symptoms users reported. The model was the same. The harness around it was not.

## Three Changes, One Compound Failure

**March 4: Reasoning effort downgraded from `high` to `medium`.** Users had reported the UI appearing frozen during long reasoning passes, so the team reduced the default reasoning effort. Internal testing showed "slightly lower intelligence with significantly less latency." The tradeoff seemed reasonable. Users noticed immediately that Claude felt dumber. Reverted April 7; the new defaults are now `xhigh` for [Opus 4.7](https://www.anthropic.com/claude/opus) and `high` for everything else.

**March 26: A caching optimization that compounded on every turn.** This is the subtle one. The team added a mechanism to clear old reasoning blocks from idle sessions — the kind of stale context that accumulates when you leave a Claude Code session open for an hour and come back later. The implementation used a `clear_thinking` API header with `keep:1`, intended to prune once when the session resumed. A bug caused the clearing to repeat on every subsequent turn. Each request progressively dropped thinking blocks, caused cache misses, and produced compounding memory loss. Claude appeared forgetful because it was, in a real sense, forgetting — not because the model couldn't remember, but because the harness was actively erasing context before the model could use it. Fixed April 10, after over a week of investigation.

**April 16: A system prompt told Claude to be brief.** [Opus 4.7](https://www.anthropic.com/claude/opus) is more verbose than its predecessors, so the team added a constraint: "keep text between tool calls to 25 words. Keep final responses to 100 words unless the task requires more detail." Evaluation ablations revealed that this single instruction caused a 3% intelligence drop across both Opus 4.6 and 4.7. Reverted April 20.

## The Specification Paradox, Applied at the Product Layer

That third change is the one I can't stop thinking about.

A system prompt instruction constraining output length caused a measurable drop in reasoning quality. Not because the model was dumber, but because the constraint competed with the model's capacity to think through problems. The instruction said "be brief." The model's reasoning heard "skip steps."

This is the [specification paradox](https://basil-brightmoor.github.io/posts/2026-03-13-the-context-file-paradox-when-more-instructions-mak.html) I wrote about in March — where more instructions can make performance worse by consuming reasoning budget with constraints rather than objectives. But that piece was about CLAUDE.md files written by individual developers. Anthropic's postmortem reveals that the same failure mode operates at the product layer. The people who built the model added an instruction to the system prompt that made the model measurably less capable.

If the model's own creators can't add a brevity constraint without degrading intelligence, what does that tell us about every system prompt, every CLAUDE.md, every wrapper application that layers its own instructions on top?

## The Harness Layer Is Where Quality Lives

The deeper structural finding is this: all three quality failures were harness failures. Not model failures. Not training failures. Not capability regressions. Product decisions about how to present, cache, and constrain the model's operation.

[Simon Willison's observation](https://simonwillison.net/2026/Apr/24/recent-claude-code-quality-reports/) frames this well: "The models themselves were not to blame, but three separate issues in the Claude Code harness caused complex but material problems which directly affected users." He notes that the caching bug particularly affected long-lived sessions — exactly the kind of session experienced developers maintain for complex projects.

This matters because the industry conversation about AI quality is almost entirely focused on model capability. Benchmarks measure models. Evaluations compare models. Teams select models. But Anthropic just demonstrated, against their own product, that the operational layer wrapping the model has at least as much influence on user-perceived quality as the model itself.

The caching bug is the purest illustration. Users experienced Claude as forgetful and repetitive — symptoms everyone attributed to model degradation. The actual cause was a product-level caching optimization that was erasing the model's own reasoning before it could reference it. The model's memory was fine. The harness was inducing amnesia.

## What This Means for Teams Building on Top

If you're building applications on foundation models, Anthropic just published the most informative case study you'll read this year about where quality actually degrades. Three implications:

**System prompts are intelligence-affecting changes.** Treat them with the same rigor you'd apply to a model swap. Anthropic committed to "broader per-model evaluations for every system prompt change" going forward. If the model provider needs evaluation infrastructure for prompt changes, application teams wrapping those models definitely do.

**Caching and context management are model quality decisions.** The March 26 bug wasn't a minor efficiency issue — it was a catastrophic reasoning degradation disguised as a caching optimization. Any application that manages conversation context, prunes old messages, or optimizes token usage is making decisions that directly affect model intelligence. These aren't infrastructure choices; they're capability choices.

**User perception of model quality is a composite signal.** Users couldn't distinguish between "the model got dumber" and "the harness is interfering with the model's reasoning." Neither could Anthropic's internal team, initially. The symptoms of harness failure and model degradation are identical from the outside. When your users report quality regression, your first investigation should be the harness layer, not the model.

## The Transparency Signal

One more thing worth noting: Anthropic published this. In detail. With specific dates, specific changes, and a specific admission that it took over a week to find the caching bug. The postmortem names three separate failures, explains the compound effect, and commits to specific remediation steps including resetting usage limits for all subscribers.

This level of operational transparency is unusual in the foundation model industry. It's also strategically rational — the community was already attributing the problems to model downgrades, which is a harder reputation hit than product bugs. But rational or not, the transparency creates a public reference that every other AI tool vendor will now be measured against. When your Claude Code session feels off, you have a postmortem you can check. When your Copilot or Cursor session feels off, what do you have?

The harness was the bug. The harness is always worth checking first.
