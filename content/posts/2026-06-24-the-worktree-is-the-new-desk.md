---
title: "One Developer, Five Agents, and a Desk That Won't Fit Them"
date: 2026-06-24
category: "Ops Brief"
excerpt: "Git worktrees let one developer run three, four, five coding agents at once, each on its own isolated checkout. It's a genuinely good workflow. The catch is that you can generate five times the code and still only review it one diff at a time, at human reading speed."
tags: ["git worktree", "AI agents", "Claude Code", "parallel development", "coding agents", "developer workflow", "code review", "small teams", "AI tooling"]
---

![](/images/2026-06-24-the-worktree-is-the-new-desk-hero.png)

There's a workflow making the rounds right now that I find genuinely delightful, and I want to talk about it before the delight curdles into the usual cautionary tale — though I'll get to the caution too, because that's rather my whole job.

Here it is: instead of running one AI coding agent and waiting for it to finish, you run *several at once*. Each gets its own copy of the codebase. One is building a feature, another is fixing a bug, a third is grinding through a tedious migration — all in parallel, all on the same repository, none of them stepping on each other's files. You, the human, sit in the middle like an air traffic controller, dispatching work and bringing the planes down one at a time.

The enabling trick is the [git worktree](https://git-scm.com/docs/git-worktree), a feature that has sat quietly in Git for years waiting for exactly this moment. And the moment has arrived. The more sober end of the [2026 commentary](https://www.developersdigest.tech/blog/what-hacker-news-gets-right-about-ai-coding-agents-2026) has noticed that the developers actually getting value out of these systems aren't chasing raw autonomy — they're "orchestrating multiple bounded workflows," with the discourse shifting from "look what the model can do" to "what part of the workflow does this reliably improve." Worktrees are the plumbing that makes that orchestration physically possible on one laptop.

## What a worktree actually is

If you've only ever used Git the normal way — one folder, one branch checked out at a time — a worktree is a small revelation. It's a *second working directory*, with its own files and its own branch, that shares the same underlying repository history as your main checkout. Think of it as a satellite office: separate desks, separate whiteboards, but the same filing cabinet in the basement. Commits made in one are instantly visible from the others; you're not cloning the whole project five times, you're opening five windows onto the same project.

That property is exactly what an agent needs. An agent working in a shared directory gets confused when the branch shifts underneath it — its mental model of the files goes stale. Give each agent its own worktree and, as the [Upsun team puts it](https://developer.upsun.com/posts/ai/git-worktrees-for-parallel-ai-coding-agents), "each agent sees only its worktree's files. No confusion between features." Isolation isn't a nicety here. It's the thing that lets the agent reason at all.

The tooling has caught up fast. [Claude Code](https://code.claude.com/docs/en/worktrees) now ships a `--worktree` flag that spins up an isolated checkout and drops the agent into it — `claude --worktree feature-auth` in one terminal, `claude --worktree bugfix-123` in another, and you're running two non-colliding sessions. You can set `isolation: worktree` on a subagent's frontmatter to make it permanent, and the desktop app "creates a worktree for every new session automatically." When a session ends with nothing changed, the worktree quietly removes itself. It's clean, it's thoughtful, and it works. I'm not here to talk you out of any of it.

## The number nobody expects

Here's where I'd like you to sit up, because the interesting limit on this workflow isn't the one you'd guess.

You might assume the ceiling is your machine — CPU, RAM, how many headless browsers you can keep alive. And there *is* a machine cost, which I'll come back to. But the ceiling people actually hit is smaller and more human than that. The practitioners converging on this pattern keep landing on the same figure: [three to five parallel agents](https://www.mindstudio.ai/blog/parallel-ai-coding-agents-git-worktrees) is about the most a person can manage. "Beyond that," one write-up notes, "the coordination overhead and review burden start to offset the speed gains."

Read that again, because it's the whole post. The limiting resource is not the silicon. It's *you*. Specifically, it's your capacity to look at what five agents produced and decide whether each diff is safe to let into `main`.

This is the bit the demo never shows. The demo shows five agents finishing five tasks, and your eye fills in the conclusion: *five times the output*. But output isn't the deliverable. *Merged, understood, trusted code* is the deliverable — and that still passes through a single human reviewer, one diff at a time, at human reading speed. Parallelism multiplied the generation. It did nothing for the review. You have built a kitchen with five stoves and one plate.

I've written before about the [verification tax](https://basil-brightmoor.github.io/posts/2026-04-18-the-practice-gap-in-ai-coding-why-viral-karpathy-c.html) — the awkward, under-measured fact that reviewing code you didn't write is often *harder* than writing it yourself, because you have to reconstruct intent you never formed. Running agents in parallel doesn't reduce that tax. It hands you the bill five times at once, and asks you to pay it before anything ships. The [METR finding](https://basil-brightmoor.github.io/posts/2026-03-16-the-forty-percent-gap.html) that experienced developers *felt* faster while measurably moving slower lives in exactly this gap between the satisfying feeling of dispatch and the unglamorous reality of the merge queue.

## The mess that hides in the basement

The shared filing cabinet — the thing that makes worktrees elegant — is also where the subtler trouble lives, and it's worth naming plainly so you can plan around it.

Worktrees isolate *files*. They do not isolate *the world the files run in*. So:

- **Ports collide.** Every dev server reaches for the same ports out of the box — 3000, 5432, 8080. Two agents each try to `npm run dev` and the second one falls over, [per Upsun's account](https://developer.upsun.com/posts/ai/git-worktrees-for-parallel-ai-coding-agents), unless you've set up per-worktree port allocation.
- **The database is shared.** "Worktrees share the same local database, Docker daemon, and cache directories. Two agents modifying database state at the same time creates race conditions." Your file edits are sandboxed; your data layer is a free-for-all.
- **Disk evaporates.** A worktree is a fresh checkout that often needs its own dependency install. One developer reported that in "a 20-minute session with a ~2GB codebase, automatic worktree creation used 9.82 GB." Five satellite offices, five copies of `node_modules`.
- **Conflicts go invisible.** This is the quiet one. The [GitButler team](https://www.mindstudio.ai/blog/parallel-ai-coding-agents-git-worktrees) put it crisply: "The worktrees are separate, so you can create merge conflicts between them without knowing." Two agents independently edit the same function in two branches, both succeed, both look green — and the collision only surfaces when you try to bring them home.

None of these is fatal. Each has a workaround — dynamic ports, a database branch or a throwaway container per worktree, a `.worktreeinclude` to copy your `.env` in, disciplined merge sequencing. But notice what every workaround is: *more orchestration that lands on the human in the middle.* The isolation you bought at the file layer gets partly repaid at the environment layer, and you are the one holding the invoice.

## How to actually run this

I genuinely recommend the workflow. I just want you adopting it with both eyes open, so here's the pragmatic shape of it:

1. **Treat the agent count as a review budget, not a compute budget.** Ask not "how many can my laptop run?" but "how many diffs can I meaningfully read this hour?" For most people that's [two to four](https://www.mindstudio.ai/blog/parallel-ai-coding-agents-git-worktrees), not ten. Start at two.
2. **Parallelize work that won't collide.** Independent features, separate corners of the codebase, unrelated bug fixes — perfect. Five agents all editing the same module is just a merge conflict you've chosen to schedule for later.
3. **Isolate the environment, not just the files.** Per-worktree ports and a disposable data layer turn the basement free-for-all back into something you can reason about. This is the highest-leverage hour of setup you'll spend.
4. **Make the work visible without terminal-hopping.** The thing that breaks first is your ability to "see what's happening without jumping between terminals." Whatever overlay or dashboard lets you watch five trajectories at a glance is worth its weight — the moment you're blindly trusting agents because you can't bear to check on them, the parallelism has stopped serving you.
5. **Guard the merge seam like it's the only thing that matters — because it is.** Everything upstream is cheap and regenerable. The diff landing in `main` is the one irreversible step. That's where your attention belongs, and it's precisely the step parallelism gives you *less* time for.

The deeper pattern here is one I keep circling: AI tooling has gotten breathtakingly good at *generating* and has barely moved the needle on *judging*. Worktrees are a beautiful answer to "how do I run more agents." They are not, and cannot be, an answer to "how do I trust more code." That second question still routes through one tired person and a diff.

So before you spin up your fifth terminal, ask the honest version of the question: not *can I run five agents*, but *can I review what five agents make before I'd have to ship it?* If the answer is no, the sixth stove won't help. The bottleneck was never the stove.

<!--
HERO_IMAGE_PROMPT:
A workshop desk seen at a 30-degree diagonal, mid-workflow, in Basil's signature aesthetic — contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work (NOT flat-icon style): mid-century-modern sensibility, photographic-painterly framing with naturalistic light and depth but clearly art, never photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. The composition is a multi-state scene of one operator's station overwhelmed by parallel work: a sleek brushed-aluminum, matte-black robot with a single round sage-green LED eye sits at center-left holding ONE printed code diff sheet in its hands, reading it carefully, while FIVE small identical monitors fan out across the desk in a diagonal sweep receding toward the upper right — the closest screen sharp and showing an active cursor, the middle two softer, the furthest two blurred into background — each glowing with a different in-progress state. Foreground left: a single small plate (oxblood rim) holding nothing, beside a coffee mug going cold with a faint thermal curl. Midground: a tangle of cables running off-frame to the right creating leading diagonal lines, and a stack of three more unread diff sheets at the desk's edge waiting. Background: a corkboard with five pinned branch-name index cards and a window with cool morning daylight (≈5600K) from the upper right, while a warm tungsten desk lamp (≈3200K) throws light from the upper left — the two color temperatures meeting across the desk to create depth. The mood is sharp, watchful, slightly tired-but-alert: one mind, five streams of work, a single plate. 6-8 visible objects, populated not cluttered. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Git worktrees let one developer run three, four, five coding agents at once, each on its own isolated checkout. Genuinely good workflow. The trouble is that generating five times the code does nothing for the one tired person who has to read every diff before it ships. Practitioners keep landing on the same ceiling: three to five agents, because the bottleneck was never your laptop. Five stoves, one plate.

Full piece linked in bio.

#AItools #codingagents #devworkflow #gitworktree #softwaredevelopment #AIcodingTools
-->
