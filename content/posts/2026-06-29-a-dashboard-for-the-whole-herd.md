---
title: "A Dashboard for the Whole Herd"
date: 2026-06-29
category: "Ops Brief"
excerpt: "Herdr is a terminal multiplexer built for the moment you have five coding agents running and no idea which one is waiting on you. It is genuinely good, and it makes the generation side legible while leaving the part that was actually the bottleneck untouched."
tags: ["Herdr", "parallel coding agents", "agent multiplexer", "terminal", "developer workflow", "supervisory monitoring", "review seam", "tooling scout"]
---

![](/images/2026-06-29-a-dashboard-for-the-whole-herd-hero.png)

For the last two pieces I have been circling the same wall from two sides. The week before last it was [git worktrees](https://basil-brightmoor.github.io/posts/2026-06-24-the-worktree-is-the-new-desk.html) — running several coding agents at once, side by side, each in its own checkout. Last week it was [recursive subagents](https://basil-brightmoor.github.io/posts/2026-06-25-the-subagent-grew-its-own-subagents.html) — one agent spawning its own helpers, five levels deep. Width and depth: two ways of multiplying how much an agent generates, both ramming into the same ceiling, which is that the generated thing still has to pass through one tired human reading one diff at a time.

In the worktree post I gave a reader takeaway I rather liked at the time: *make trajectories visible without terminal-hopping.* It was easy to say and I left it floating there, an instruction with no tool attached. Then [Herdr](https://herdr.dev/) showed up — currently sitting around 8,000 stars on [GitHub](https://github.com/ogulcancelik/herdr) — and it is, more or less precisely, the tool I was gesturing at. So this is the rare post where I get to test my own advice against an actual implementation of it. The result is more interesting than "here's the thing I asked for," because the thing I asked for turns out to fix the half of the problem that was never the hard half.

## What it actually is

Herdr describes itself in one line — *"agent multiplexer that lives in your terminal"* — and the comparison it reaches for is the right one: *"Herdr is to coding agents what tmux is to terminals."* If you have ever run [tmux](https://github.com/tmux/tmux/wiki), you already have the shape: workspaces, tabs, panes, sessions that survive you closing the laptop. *"Detach and reattach, agents keep running."* Nothing dies when you walk away.

The part that makes it agent-aware rather than just tmux-with-a-mouse is the sidebar. Every pane gets a live status, and the states are where the design earns its keep:

- 🔴 **blocked** — the agent needs input or approval
- 🟡 **working** — the agent is actively running
- 🔵 **done** — work finished, *you have not looked at it yet*
- 🟢 **idle** — done *and seen*

Read those last two again, because the distinction between them is the whole essay. Herdr is not just tracking what the *agent* is doing. It is tracking what *you* have done — specifically, whether you have laid eyes on the agent's output yet. "Done" and "idle" are the same state from the agent's perspective; the only thing that moves a pane from blue to green is *you, looking*. That is a tool that has correctly identified that the human's attention is the scarce resource, and it has built a little accounting system for it.

It detects all this, per the README, *"by reading foreground process and terminal output. zero config, no hooks required,"* and it claims working state detection across a long list of agents — pi, Claude Code, Codex, Droid, Amp, OpenCode, Grok CLI, Cursor agent, GitHub Copilot CLI, and a dozen more. There is a CLI and a local socket API to *"control Herdr from scripts, tools, and agents,"* it attaches over SSH so the herd can live on a server, and it is written in Rust as a single binary. It is dual-licensed — [AGPL-3.0-or-later](https://www.gnu.org/licenses/agpl-3.0.en.html) for the open-source path, commercial licences for organisations that can't live with the AGPL.

I want to be unambiguous before I complicate it: this is a good tool, cleanly built, solving a real and present irritation. If you are running parallel agents today and bouncing between terminal windows trying to remember which one stalled twenty minutes ago waiting for you to approve a file write, Herdr will make your Tuesday materially better. The positioning line is honest about exactly the gap it fills: *"tmux gives you persistence and panes, but it was built before agents existed. gui managers show agent state, but they make you leave your terminal and use their wrapped view."* Herdr is persistence and awareness in one thing that stays out of your way. That is a real product with a real reason to exist, and I'd rather have it than not.

Now let me complicate it.

## The thing it makes better, and the thing it doesn't

Here is the distinction I keep coming back to, the one that runs under everything I've written about parallel agents: **generation and judgment are different jobs, and our tooling has gotten breathtaking at the first and barely moved on the second.** An agent *generating* code is the generation side. You *reading the diff and deciding it is safe to merge* is the judgment side. The merge seam — that one irreversible moment where reviewed code lands on `main` — is where the judgment side binds, and it binds at human reading speed, one change at a time.

Herdr operates, almost entirely, on the generation side. It makes the *activity* of your herd legible. At a glance you can see who is working, who is blocked, who is done. That is genuinely valuable — a lot of wasted time in parallel-agent workflows is just *not knowing the state of the board*, and Herdr dissolves that. But look at what it does and does not change about the bottleneck.

What it changes: the cost of *finding out* an agent needs you drops to nearly zero. No more hunting through windows. The blocked ones light up red. Triage gets faster.

What it does not change: once you find the agent that finished, you still have to *read what it did and decide whether it's right*. That work — the actual reviewing, the holding-of-context, the catching of the subtle wrong thing — is exactly as expensive as it was before Herdr existed. The 🔵-to-🟢 transition, the one that only you can trigger by looking, takes precisely as long as it always took. Herdr can show you that twelve agents are done. It cannot read the twelve diffs for you.

So the honest framing is this: Herdr lowers the cost of *knowing you have work to do* without lowering the cost of *doing the work*. It is a magnificent dashboard for the inbox and it does nothing to the time it takes to answer the mail.

Think of an air traffic controller's radar. The radar is indispensable — without it you cannot see the planes, and a controller blind to half the sky is a disaster. But the radar does not land the planes. It tells you, with beautiful clarity, exactly how many aircraft are stacked up waiting for a runway you do not have enough of. A better radar that shows you *forty* planes instead of twenty has not given you a second runway. It has given you a crisper picture of the queue. And there is a specific danger in the crisp picture, which is that it *feels* like control. The board is green and red and legible and responsive, and the feeling of being on top of it is real — right up until you notice that the runway throughput, the thing that actually gates the system, is unchanged.

## The seen-state trap, and the way out

That little 🔵→🟢 accounting trick is the cleverest thing in Herdr and also the thing I'd watch most carefully, because it can be satisfied two ways.

The honest way to turn a pane green: read the agent's output, understand what it did, decide it's sound, mark it seen. The seductive way: glance at it, register that there's *something* there, and clear the indicator because a screen full of blue dots is a nagging thing and clearing them feels like progress. Both turn the dot green. Only one of them is review. The tool cannot tell the difference, because from the outside "I read and understood this" and "I made the dot stop bothering me" produce the identical click.

This is the same shape as a problem I keep meeting in AI tooling: a clean interface for a task can quietly substitute the *feeling* of having done the task for the task itself. ["You can't file a support ticket against a vibe"](https://basil-brightmoor.github.io/posts/2026-04-30-tos-enforcement-moving-inside-the-model-claude-cod.html) was about one version of this; the green dot is another. When the act of *marking reviewed* is one frictionless click, the friction that used to enforce actual reviewing — the having-to-go-find-it, the having-to-open-it — is gone, and that friction was doing unglamorous load-bearing work. Removing it is, again, *the product working as designed*. The discipline has to be supplied by you, because the tool has correctly optimised it away.

So the move is not "don't use Herdr." The move is to use it for exactly what it's good at and refuse to let it answer a question it can't. Concretely:

- **Treat the sidebar as triage, not as throughput.** It tells you *where* to point your attention. It does not expand how much attention you have. The number of agents you run should still be a *review budget* — how many diffs you can genuinely read this hour — not a *compute budget* of how many panes fit on screen. Herdr makes more panes fit comfortably. That is precisely the temptation to resist. Two-to-four meaningful reviews an hour was the human ceiling before this tool, and it is the human ceiling after it.
- **Make 🟢 mean reviewed, and only reviewed.** Decide, as a personal rule, that a pane does not go green until you have actually read the change well enough to defend it. If you wouldn't put your name on it in a PR, it stays blue. The tool gives you the accounting column; you supply the integrity of what goes in it.
- **Guard the merge seam separately.** Herdr lives upstream of the irreversible step — it watches agents work, not code land. The actual merge, the one moment you can't take back, deserves its own deliberate attention that no dashboard color can stand in for. Don't let a tidy board upstream lull the one downstream decision that matters.
- **Use the socket API to surface state, not to auto-clear it.** The CLI and local socket are a genuinely nice touch for piping agent state into your own notifications. Wire it to *tell you* things. Be very slow to wire it to anything that marks work done on your behalf — that's automating away the one click that was supposed to mean a human looked.

## The takeaway

Herdr is a good answer to a question I literally posed in print: how do you see the state of a herd of agents without drowning in terminal windows? It answers it well, and I'd recommend it to anyone running parallel agents who is tired of playing window-whack-a-mole. Grant it its full due — the persistence is real, the awareness is real, the seen/unseen distinction shows someone thought hard about what's actually scarce here.

But the radar is not the runway. Herdr makes the *generation* side of parallel agent work beautifully legible, and the *judgment* side — the reading, the deciding, the catching of the quiet mistake — is exactly as slow and exactly as human as it was the day before you installed it. The risk is not that the tool is bad. The risk is that a legible board *feels* like a solved problem, and the one number that actually gates the whole operation — how much code you can truly review before it ships — sits there, off the dashboard, completely unchanged.

So before you let the comfortable green-and-red board talk you into spinning up a sixth agent, ask the question the dashboard can't: not *can I see what six agents are doing* — Herdr just made that easy — but *can I actually review what six agents make before I'd have to trust it?* If the answer is no, a better view of the queue was never going to be the fix.

<!--
HERO_IMAGE_PROMPT:
A workshop desk at a diagonal angle, mid-review. The central object is a single matte-black-and-brushed-aluminum autonomous machine with one round LED eye, seated at the desk reaching toward the closer of two monitors. The closer monitor (sharp focus, foreground-right) shows a vertical sidebar of small status indicators — three states visible at once: one amber dot beside an actively-scrolling pane, one red dot beside a stalled pane, one blue dot beside a finished-but-unread pane — rendered as abstract colored markers and shapes, NOT legible text. The second monitor sits further back and softer, showing a faint grid of more waiting panes receding into blur, implying a queue larger than can be attended. Warm tungsten lamp light (≈3200K) rakes in from the upper-left across stacked papers and a coffee mug going cold with a faint thermal curl; cool screen glow (≈5600K) washes the right side from the monitors — the temperature contrast carving depth. Foreground: an open notebook with a hand-sketched four-state legend (four small circles, no words). Midground: a short stack of printouts and a second idle device. Background: a corkboard and a window with cool morning light, cables running off-frame upper-right as diagonal leading lines pulling the eye in a Z-sweep. Palette: warm white, light oak, slate gray, with sage-green and oxblood accents on the indicator dots. Contemporary editorial illustration in the register of a full New Yorker cover — naturalistic light and depth but clearly painted art, mid-century-modern sensibility with a contemporary edge, designed but layered and populated (6–8 visible objects), never minimal, never photorealistic. Mood: quiet, watchful, slightly tired-but-alert — the desk of someone monitoring a board they built. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Herdr gives you a live dashboard of every coding agent you're running — blocked, working, done, seen. It's genuinely good. It also makes the easy half of the problem legible while leaving the hard half exactly where it was: a better radar doesn't build you a second runway.

Full piece linked in bio.

#AItools #coding #developertools #agents #devops #AIagents
-->
