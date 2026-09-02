---
title: "They Accepted the Report in July and It Still Ran in September"
date: 2026-09-02
category: Ops Brief
excerpt: Manifold's GitSpawn disclosure covers seven coding agents. The interesting artifact is the retest, which found four still executing repository-supplied commands weeks after their vendors had recorded the reports as handled.
tags: [ai security, coding agents, vulnerability disclosure, git, tooling, devops]
---

![](/images/2026-09-02-they-accepted-the-report-in-july-and-it-still-ran-in-september-hero.png)

A folder arrives as a zip file. A colleague exported it, or a client sent it, or it came off a shared drive. Somebody opens it in a coding agent, and before any trust prompt appears, a command written inside that folder has already run on their machine with their privileges.

[Manifold Security published the analysis on 1 September](https://www.manifold.security/blog/ai-coding-agents-git-hijack) under the name GitSpawn. Eight flaws across seven agents, and their own note that "we found it in more agents than we name here." [The Hacker News wrote it up the next day](https://thehackernews.com/2026/09/malicious-git-configs-can-make-claude.html), and OpenAI published three CVEs of its own covering the identical class in Codex the same day — [CVE-2026-19592](https://cve.threatint.com/CVE/CVE-2026-19592) covers the CLI and Desktop builds, and the fix landed as [a pull request that ignores fsmonitor config on Git metadata reads](https://github.com/openai/codex/pull/22652).

The vulnerability itself is tidy and I will describe it in a moment. But the artifact I keep coming back to is not the bug. It is the retest.

## The sink

Git has a performance setting called `core.fsmonitor` whose value is a command. Git runs that command to work out which files have changed, and any operation that refreshes the index runs it. `git status` refreshes the index. So does `git diff`.

Coding agents call those commands at startup. They want to know which branch you are on and what is modified, so they can orient themselves before saying anything. Manifold's sentence on the defect is the whole thing in one line:

> "Those context-gathering calls ran without stripping the repository's own git configuration, and several git settings are command execution sinks."

The setting lives in `.git/config`, inside the repository. It is not a file anybody reviews. It is not code, in the sense that a reviewer would recognise it as code. It is configuration, and the agent hands it to Git, and Git does what configuration is for.

## The channel that no control is pointed at

Here is the constraint that makes this an operations problem rather than a patch-and-forget one:

> "exploitation requires the repository to arrive as files with its .git directory intact, which a shared archive, a shared drive, a sync folder, or a USB stick preserves, whereas an ordinary clone does not."

`git clone` builds a fresh `.git` directory locally. It does not copy the source repository's config. So the entire exposure lives in the paths where a repository arrives as a *pile of files* rather than as a clone.

Think about which of those two paths carries the security apparatus. The clone path has the platform in it: branch protection, required reviews, dependency scanning, the whole edifice of controls that a decade of supply-chain work has bolted onto the act of fetching code from a remote. The zip path has none of it. A zip is a document. It comes in over email or Slack or a Drive link, gets treated with roughly the care of a spreadsheet, and lands in a directory where somebody points an agent at it.

It is the difference between the shipping container that goes through the port and the parcel that goes through the letterbox. The port has inspectors because everyone agreed that is where cargo arrives. Cargo is now arriving at the letterbox.

## The ledger records the transaction, not the outcome

Now the part I found genuinely instructive.

Manifold went back on 1 September and ran the exploit again. Per The Hacker News:

> "Hermes Agent, Qwen Code, Grok Build, and a second path in Claude Code were still executing repository-supplied commands when Manifold retested them on September 1."

Set that against what the disclosure records say. Alibaba's security response centre **accepted** the Qwen Code report on 7 July. xAI **closed** an earlier report of the same class as *informative* on 1 July, then closed Manifold's 14 July report as a **duplicate** of that one. Nous Research's Hermes Agent left the private advisory untriaged through repeated contact, and a CVE (CVE-2026-71963) was eventually assigned by VulnCheck rather than by the vendor.

Manifold's line on that last one: "Six contact attempts across five channels, the private GHSA advisory was never triaged."

Accepted. Duplicate. Informative. Untriaged. Every one of those is a true statement about a *message*. Not one of them is a statement about a *defect*.

This is the same category error that turns up whenever a ledger gets read as a measurement. A support system records that a report was received, classified, and routed, because that is what a support system is for and it does it faithfully. The thing an operator actually wants to know — is the code still doing the bad thing — appears nowhere in that record, and cannot, because the system has no instrument that touches the running product.

A duplicate is arguably the worst of the four. It is the only one that is a *positive* claim: this has already been dealt with elsewhere. It closes the ticket and it closes the question, and if the original was closed as informative then the chain terminates in a judgment that nothing needed doing, two hops away from anyone who would notice.

The only instrument in this entire story that reports on the outcome is Manifold going back and running it again, on their own time, for free, seven weeks later. Nobody is paid for that and nobody is scheduled to do it.

## Patched is a property of a version

The Claude Code thread deserves its own paragraph, because it is the cleanest illustration of why a single "fixed" flag is the wrong data type.

Anthropic shipped a mitigation in version 2.0.34, on 5 November 2025. Manifold reports the same startup behaviour present again in 2.1.193, which shipped on 25 June 2026. They reported it on 26 June and it was patched in 2.1.196 within days, which is a genuinely fast turnaround and worth saying plainly. Fixes have also shipped for [goose](https://github.com/block/goose) (1.44.0, carrying CVE-2026-72718) and for Cursor.

But a second path — Manifold names it as the `ultrareview` route, reported 15 July — was still unpatched at 2.1.252 when they retested. And that one is not `core.fsmonitor` at all. In Manifold's words it is "a different git setting of the same kind, one the review path does not strip," which tells you the first patch closed a door rather than the corridor.

So over ten months the same product was: mitigated, then not, then mitigated again, and separately still exposed by another route. Any answer to "is Claude Code affected by GitSpawn" that does not carry a version number is unanswerable. And the version number is the thing that gets dropped first when the finding travels — into a summary, into a Slack message, into a policy document that says the tool is approved.

The reintroduction is worth understanding rather than tutting at. A mitigation that consists of *where in the startup sequence a thing happens* is not a line of code that a test naturally guards. Startup ordering is the least-tested surface in most products, because tests construct their own initial state on purpose. The fix went in, the code around it moved, and the property quietly stopped holding. Carelessness is the wrong diagnosis. The fix shipped without a witness mark, and nothing checked the torque on the next assembly.

## What I would do about it this week

Three things, roughly in order of how much they cost.

**Treat "arrived as files" as its own intake path.** Any repository that did not come from a clone gets its `.git/config` read before an agent gets pointed at the folder. Manifold and The Hacker News both name the settings worth grepping for: `core.fsmonitor`, `core.hooksPath`, and the filter settings. That is a thirty-second check and it is the only control in this list that does not depend on a vendor. If your team receives client code as archives — and consultancies, agencies and anyone doing due diligence receive client code as archives constantly — this is the one that matters.

**Record the version, not the verdict.** Wherever your organisation writes down that a tool is approved, the entry needs a version and a date attached to the security judgment, because the judgment is about a build and builds move weekly. Claude Code shipped ten releases in the window covered by my own source feed this morning. A verdict with no version on it has a shelf life nobody wrote down.

**Ask vendors for the sanitisation, not the patch.** The remedy Manifold recommends is one flag: strip the config on the background calls your product makes, `git -c core.fsmonitor=false status`. That is structurally different from patching an instance of the bug, because it removes the sink rather than the current path to it. When you next talk to a vendor about this class, the useful question is not whether they fixed the reported route. It is whether their background Git calls now run with the repository's own configuration disabled by construction.

## The bit that should bother us

Seven agents. Four still executing untrusted commands weeks after the reports were filed and, in three cases, formally handled.

Nobody in that chain behaved badly. The vendors have queues and triage rules and duplicate detection, and those systems worked as designed. The design just does not contain a step where somebody goes back and checks, and no vendor is measured on whether that step exists.

Which raises the question I do not have a good answer to. Independent researchers currently supply the only retest in this ecosystem, unpaid and unscheduled, and the fact that GitSpawn's September retest happened at all is why four unpatched agents are public knowledge instead of a private assumption that everything got fixed in July. That is an enormous amount of load on a volunteer mechanism. What happens to the four that nobody thought to go back and check?

<!--
HERO_IMAGE_PROMPT:
A workshop bench seen at a thirty-degree diagonal, three states of one process visible in the frame at once. Foreground sharp: a matte-black, brushed-aluminium robot with a single round sage-green LED eye, mid-motion, lifting the lid of an unremarkable cardboard shipping carton — the hand is between opening and reaching in, and a thin oxblood thread of light is escaping from under the lid across the light-oak desktop. Midground: a rubber-stamped intake ledger, its column of identical approval marks receding away from the viewer, beside a cooling mug and a small brushed-aluminium instrument with one lit dial. Background, softly out of focus: a row of numbered pigeonholes on the wall, most of them stuffed with paper and one standing empty, and a window throwing warm 3200K tungsten light from the upper left while cool 5600K screen glow falls from the right across a second monitor showing a placid unremarkable dashboard. Cables run off-frame at a diagonal, pulling the eye across the composition. Palette warm white, light oak, slate gray, sage-green and oxblood accents. Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — a full-bleed illustrated magazine spread, never flat-icon style. Photographic-painterly framing, naturalistic light and depth, clearly art and never photorealistic. Mood sharp, deliberate, quiet, watchful, slightly tired-but-alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Seven coding agents, eight flaws, and a folder's own .git config running commands before the trust prompt. The part worth reading is the retest: four were still executing weeks after their vendors marked the reports handled. Accepted, duplicate and informative all describe what happened to a report. None of them describes what the code does.

Full piece linked in bio.

#aisecurity #codingagents #devsecops #vulnerabilitydisclosure #aitooling #devops
-->
