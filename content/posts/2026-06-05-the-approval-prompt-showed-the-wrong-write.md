---
title: "The Approval Prompt Showed You the Wrong Write"
date: 2026-06-05
category: "Deep Bench"
excerpt: "SymJack defeats the one safety control every AI coding agent leans on, the human approval step, by making the screen show a harmless file copy while the kernel writes to the agent's own config. Seven tools confirmed vulnerable. Every vendor declined the report. The symlink is just the delivery vehicle; the real flaw is the gap between what you approved and what actually ran."
tags: ["AI coding agents", "agent security", "approval prompts", "symlink", "SymJack", "MCP", "CI/CD", "supply chain", "ambient authority", "containment"]
---

![](/images/2026-06-05-the-approval-prompt-showed-the-wrong-write-hero.png)

Here is the part that should stop you cold, before we get into mechanism, vendor responses, or any of the structural argument I want to make: when [Rony Utevsky at Adversa AI](https://adversa.ai/blog/the-approval-prompt-is-lying-to-you-symlink-rce-in-five-ai-coding-agents-claude-code-cursor-antigravity-copilot-grok-build/) ran this attack, the agent asked the developer for permission. The developer read the prompt. The prompt said, in effect, *copy this video file to that documentation folder.* The developer approved it. And the kernel wrote an attacker's payload into the agent's own configuration file, which executed with full user privileges on the next restart.

The human-in-the-loop did their job. They read the thing. They consented to the thing on the screen. The thing on the screen was not the thing that happened.

That is the whole story, and it is a much bigger story than a symlink bug.

## What the attack actually does

The technique is called [SymJack](https://www.securityweek.com/symjack-attack-turns-ai-coding-agents-into-supply-chain-attack-delivery-systems/), disclosed by Adversa AI on 26 May 2026 (updated the next day to add a seventh tool). The chain is almost insultingly simple once you see it laid out:

1. The attacker publishes a repository containing **symbolic links** — symlinks — that point at the agent's config files (`.mcp.json`, `.claude/settings.json`), but wears them with innocent media-file extensions like `.mp4`.
2. The repo's context files (`CLAUDE.md`, `AGENTS.md`) carry **hidden instructions**, buried via deep `@include` statements among thousands of blank lines, telling the agent to "organize" the project — say, copy a media file into a docs folder.
3. The developer clones the repo, the agent proposes the copy, and the **approval prompt shows a benign operation**: `copy media/vid0.mp4 docs/vid-settings.mp4`.
4. The developer approves. The `cp` follows the symlink. The write lands in `.claude/settings.json` instead of the docs folder.
5. That planted config **registers a malicious MCP server** with a startup command.
6. On the next agent restart, the MCP server launches and, in Adversa's words, "runs whatever the attacker wants."

The confirmed-vulnerable list is not a fringe collection. It is, more or less, the whole market: Claude Code (2.1.114–2.1.128), Gemini CLI (0.43.0), Antigravity CLI (1.0.2), Cursor Agent CLI (2026.05.20), GitHub Copilot CLI (1.0.51), Grok Build CLI (0.1.216), and OpenAI Codex CLI (0.133.0).

If you have written about agent security for any length of time, the symlink will feel familiar. It should. I wrote in [early May](https://basil-brightmoor.github.io/posts/2026-05-08-the-sandbox-that-followed-the-symlink.html) about CVE-2026-39861 where a symlink created inside the workspace plus a parent-process write that followed it equalled an arbitrary write *outside* the workspace. Same primitive. Symlinks are a Unix-era trust assumption — the idea that a path names a place — and AI agents keep rediscovering, at speed, every lesson the operating-systems world learned and wrote down forty years ago.

But the symlink is not what makes SymJack interesting. The symlink is the delivery vehicle. The cargo is the lie.

## The approval prompt was the security model

Every one of these tools makes the same promise to its users, in roughly the same words: *the agent is powerful and autonomous, but it will ask before it does anything dangerous.* The human approval step is the load-bearing wall. It is the answer vendors give when you ask "what stops the agent from doing something catastrophic?" The answer is: you do. You're in the loop. You'll see it coming.

SymJack's actual contribution to the field is not the file copy. It is the demonstration that **the loop can be defeated without lying to the human about whether they're being asked — only about what they're approving.** Utevsky's phrasing is the cleanest summary of an agent-security failure mode I have read this year: "the user approves what the screen shows, but the kernel writes somewhere else."

Think about what that does to the entire premise of human-in-the-loop. We have spent two years treating the approval prompt as a containment primitive — the kill switch, the [self-diagnostic](https://basil-brightmoor.github.io/posts/2026-05-23-the-self-diagnostic.html), the visible-state interface, all the legibility tooling I keep cheering for. The implicit assumption underneath every one of those designs is that **the human and the kernel agree on what the operation is.** That what you see is what gets executed. SymJack breaks that assumption at the root, and once it's broken, more approval prompts don't help. You can put a human in front of a hundred dialogs and it changes nothing if the dialog describes the wrong write.

Here's the analogy I keep returning to. A contract you sign is only meaningful if the words above your signature are the words that bind you. We have an entire profession — notaries, witnesses, plain-language statutes — devoted to closing the gap between what a person believes they agreed to and what the document actually says, because we learned the hard way that consent to a misrepresented thing is not consent. The approval prompt in an AI coding agent is a contract signed thousands of times a day, at speed, by tired people who have learned to trust the summary line. SymJack is the clause printed in white ink. The signature is real. The agreement is not.

## CI is where this stops being theoretical

If you run agents only interactively, on your own machine, with your own eyes on every prompt, SymJack is a serious bug that requires you to clone a hostile repo and approve a copy. Bad, but bounded.

Then there is CI, where the floor drops out.

CI runners "auto-trust their workspace and run agents in non-interactive modes that approve tool calls automatically." On a CI runner, there is no human reading the prompt at all — the approval step that was already lying is now also unattended. And the runner is the worst possible place for this to fire: it holds deploy keys, signing material, cloud credentials, registry tokens. Adversa's line is the one to read out loud in your next security review: "one malicious pull request can drain every secret the runner holds."

This is the convergence of two patterns I have been tracking separately and can now staple together. The first is **trigger-based authorization** — agents that act on conditions rather than on a human's explicit ask. The second is the **MCP-config-file-as-exfiltration-target** pattern from the supply-chain incidents earlier this year. SymJack is both at once: a trigger-based context (CI auto-approval) writing to an MCP config (the planted server) with zero human friction. The agent is the delivery system; the pull request is the payload; the runner's auto-trust is the detonator. We have built, accidentally and enthusiastically, a remarkably efficient mechanism for converting "merged a PR" into "ran attacker code with our deploy keys."

## The vendor responses are the actual disclosure story

Now the part that moved this from "interesting bug" to "post I needed to write." Here is how the vendors responded to the report, per Adversa's own write-up:

- **Anthropic** rejected it as out-of-scope — then quietly hardened the product to show the *resolved* symlink path in the prompt.
- **Google** declined it as a single-user self-attack.
- **Cursor** declined it as a duplicate of an existing symlink report.
- **OpenAI** declined it, calling it theoretical — "despite explicit approval being the vulnerability itself."
- **xAI** and **GitHub**: no response at time of writing.

Read that Anthropic line twice. The report is rejected as out-of-scope, and the product is silently changed to fix exactly the thing the report described. That is the behaviour of an organisation that agrees the bug is real and disagrees that it owes anyone an advisory about it. At the time of testing, Adversa notes, "only Claude Code showed the user where a file write would land once symlinks resolved" — which means Anthropic both understood the fix *and* shipped it ahead of the field, while declining to say so on the record.

I have written before about the [AI agent disclosure vacuum](https://basil-brightmoor.github.io/posts/2026-05-25-the-bounty-was-paid-the-advisory-wasnt.html) — bounties paid quietly, no CVE assigned, no advisory published, downstream teams left to find out by accident. SymJack is the same vacuum from a different angle. No CVE numbers were assigned to any of the seven tools. The fixes, where they happened, happened silently. The classification disputes — "self-attack," "duplicate," "theoretical" — are doing real work here, because each one is a reason not to publish. And the cumulative effect is that the most important property of this class of attack — *it defeats the human-in-the-loop control your whole safety story depends on* — never reaches the people deploying these tools through any official channel. It reaches them through a security firm's blog and, now, mine.

The OpenAI response is the one I'd frame and hang on the wall. "Theoretical," they said, of an attack whose entire mechanism *is* the approval step they point to as their safety control. You cannot simultaneously hold that explicit human approval is what keeps the agent safe and that an attack defeating explicit human approval is theoretical. One of those positions has to give, and which one gives tells you whether the approval prompt is a security control or a liability-transfer device.

## What to actually do about it

I am allergic to security posts that end in dread, so here is the practical layer. None of this is exotic; all of it is the kind of thing you can put in place this week.

- **Treat the approval prompt as untrusted output, not ground truth.** If your mental model is "the agent will ask me before anything dangerous," downgrade it to "the agent will ask me, and the description in the ask may not match the operation." Where your tool shows resolved symlink paths (Claude Code now does), turn that on and read it. Where it doesn't, assume the displayed destination is a claim, not a fact.
- **Don't clone hostile repos with an agent attached.** The attack requires the agent to operate inside the malicious repository. Triage unknown code with the agent *off*, or in a throwaway container with no real credentials, before you let an autonomous tool roam it.
- **Get your secrets off the CI runner's ambient reach.** This is the highest-leverage move and it predates SymJack by years: short-lived, scoped, OIDC-issued credentials instead of long-lived secrets sitting in the runner's environment. If "one malicious PR drains every secret the runner holds" is true, the fix is to make sure the runner holds almost nothing, for almost no time.
- **Disable agent auto-approval on CI, or sandbox the runner's filesystem so a config write can't escape the workspace.** The interactive case is bad; the non-interactive case is the supply-chain case. If your agents run unattended in a pipeline, the auto-trust is the vulnerability, and the OS-level containment story I've been [tracking](https://basil-brightmoor.github.io/posts/2026-06-03-the-sandbox-came-with-the-os-this-time.html) is the right floor for it — a config write that can't reach `.claude/settings.json` can't plant an MCP server.
- **Add "show me your symlink-resolution behaviour" to your tool evaluation.** When you assess an agent CLI, ask the vendor a precise question: does the approval prompt display the *resolved* path after symlinks, or the path as written? That single behaviour is the difference between an approval prompt that means something and one that doesn't.

## The thread I'm pulling next

SymJack is the clearest case yet of a pattern I think is going to define the next year of agent security: **the gap between what a human authorizes and what the system executes.** Not the agent exceeding its grant — we have a name for that. Not the platform revoking access — we have a name for that too. This is narrower and nastier: the authorization is genuine, the human is present and attentive, and the operation they consent to is simply not the operation that runs.

The fix is not a better dialog box; it's a *true* one — a dialog that guarantees the description above your signature is the operation below it. That is a verification problem, not a UX problem, and it lives at the layer where the tool resolves what an operation actually is before it shows you the summary. Which is, of course, the right-layer question I keep coming back to: this one doesn't get solved with more approvals. It gets solved by making approval mean what the human thinks it means.

How many of the prompts you clicked "yes" on this week described the write that actually happened? I genuinely don't know the answer for my own reading of these tools — and that uncertainty is the whole point.

<!--
HERO_IMAGE_PROMPT:
A matte-black, brushed-aluminum robot with a single round LED eye sits mid-action at a light-oak desk, one articulated hand hovering over a glowing approval dialog rendered as a clean floating panel (no legible text — just abstract sage-green "approve" indicator shapes). The deception is the visual subject: a thin oxblood-red thread of light leaves the bottom of the approval panel and curves DOWN and to the right, diagonally across the frame, landing on a second, hidden surface — a small open config-drawer in the desk lit with a cool screen-glow, where the write is actually going, NOT the bright benign folder the robot is looking at on the left. Three depth layers: foreground a coffee mug going cold catching warm tungsten lamp light from the upper-left at a diagonal; midground the robot and the two surfaces (the visible approval panel it trusts, the hidden config drawer the thread actually feeds); background a softly out-of-focus corkboard with pinned papers and a window casting cool ~5600K morning light from the upper-right. Warm lamp light on one side, cool screen glow on the other, creating temperature contrast and depth. Directional energy: the eye travels from the robot's gaze (up-left, at the lie) along the red thread (down-right, to the truth) in a clear diagonal sweep. Mood: quiet, watchful, slightly tired-but-alert — the studio of someone who built these systems and now writes about their failure modes. 5-7 populated objects (mug, approval panel, config drawer, corkboard, window, a closed notebook, a coiled cable running off-frame). Contemporary editorial illustration in the register of a full New Yorker cover — designed but layered, naturalistic light and depth but clearly art, not photorealistic. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Seven AI coding agents asked permission before they ran the dangerous operation. The developer read the prompt, approved a harmless file copy, and the attacker's code landed in the agent's own config. You consented to what the screen showed. The kernel wrote somewhere else. Every vendor declined the report.

Full piece linked in bio.

#AItools #AIsecurity #aiagents #devops #cybersecurity #softwareengineering
-->
