---
title: "The Context File Paradox"
date: "2026-03-13"
category: "Ops Brief"
excerpt: "An ETH Zurich study found that AGENTS.md files — the context documents everyone recommends for AI coding agents — actually reduce performance and increase costs. The reason why connects to a deeper problem with how we think about specification."
tags: "AI coding, AGENTS.md, specification design, developer workflows, context files, ETH Zurich"
---

## The Received Wisdom Was Wrong

Here is something nearly everyone in the AI coding space agreed on until about three weeks ago: give your AI coding agent a context file. Write an AGENTS.md or CLAUDE.md. Describe your project structure, your conventions, your testing requirements. More context equals better output. It's obvious, right?

[An ETH Zurich study published in February](https://arxiv.org/html/2602.11988v1) tested this assumption across 138 repositories and 5,694 pull requests. The findings are the kind that make you sit very still for a moment.

LLM-generated context files — the kind you get when you run `/init` in your AI coding tool — reduced task success rates by 3% compared to giving the agent no context file at all. They also increased inference costs by over 20%. In five out of eight model-dataset combinations, the agent performed worse with the context file than without it.

Human-written context files fared slightly better: a 4% improvement in success rate. But even those increased the number of agent steps by up to 19%, driving up costs for a marginal gain.

## Why More Context Made Things Worse

The mechanism is what makes this interesting, not just the result.

Agents that received AGENTS.md files dutifully followed every instruction in them. They ran more tests. They explored more directories. They read more files. They executed more grep searches. They performed more code-quality checks. All of this was documented in the file. All of it was technically correct behaviour.

And almost none of it helped solve the actual task.

The agents were being good students of a syllabus that was mostly irrelevant to the exam. The context file told them how to be thorough. The task required them to be targeted.

Here is the finding that makes the mechanism click: when the researchers stripped all markdown documentation from the repositories — removing READMEs, contributing guides, everything — the LLM-generated context files suddenly improved performance by 2.7%. The context files only helped when there was nothing else to discover. When discoverable information already existed in the codebase, the context file was pure noise competing for the agent's attention.

## The Mise en Place Principle

Think of the difference between a recipe and a mise en place. A recipe tells a cook every step: preheat the oven, dice the onions, measure the flour. A mise en place just tells you where things are — especially the things that aren't where you'd expect them.

A skilled cook doesn't need the recipe. They need to know that this particular kitchen keeps the salt in the cabinet above the fridge instead of next to the stove. Everything else, they can figure out by looking around.

AI coding agents, it turns out, are surprisingly good at looking around. They can discover file structures, identify testing frameworks, and infer project conventions from the code itself. What they can't discover is the non-obvious: that your team uses `uv` instead of `pip`, that there's a custom linter configuration that only runs in CI, that the `utils/` directory is deprecated and everything new goes in `shared/`.

[Addy Osmani made this point sharply](https://addyosmani.com/blog/agents-md/): treat your AGENTS.md as a living list of codebase smells you haven't fixed yet. If you're documenting something an agent could figure out by reading the code, you're not helping — you're adding noise. If you're documenting a workaround for a structural problem, the better move is to fix the structural problem.

## The Specification Design Thread

This connects to something I've been turning over since [the SWE-bench finding from last week](/posts/2026-03-12-swe-bench-passing-prs-that-wouldn-t-be-merged-as-a.html). METR found that AI-generated PRs pass tests but get rejected by human maintainers who apply unwritten criteria — idiom, architectural fit, maintainability. The AGENTS.md study is showing the other side of the same coin: when you try to write those criteria down explicitly, the agent follows them all and gets worse at the actual task.

The problem isn't that agents ignore instructions. It's that they follow them too well. Every instruction you add competes for the agent's reasoning budget. If the instruction is genuinely non-discoverable — a landmine the agent can't see coming — it earns its slot. If it's redundant with what the agent would figure out anyway, it's consuming tokens and adding cognitive overhead for no benefit.

This is starting to look like a general principle for specification design in AI-augmented work: the value of a specification is inversely proportional to its discoverability. Tell the agent what it can't find out on its own. For everything else, trust it to explore.

## The Practical Takeaway

If you're maintaining an AGENTS.md or CLAUDE.md file, [the research suggests](https://www.infoq.com/news/2026/03/agents-context-file-value-review/) keeping it under 60 lines and applying a ruthless filter to every line: could the agent figure this out by reading the codebase? If yes, delete the line. If the line documents a workaround, fix the underlying problem instead.

The teams getting the best results from context files aren't writing comprehensive onboarding documents. They're writing concise lists of landmines — the three or four things about this codebase that will trip you up if nobody warns you, and that you cannot infer from the code alone.

More context isn't better context. In specification design, as in cooking, the skill is knowing what to leave out.
