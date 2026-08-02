---
title: "They Hardened Registration Twice and the Attack Moved to the Inheritance"
date: 2026-08-02
category: Ops Brief
excerpt: "Arch Linux disabled AUR package adoption on July 30 after another malware wave. Two rounds of signup hardening had pushed the attack onto the one mechanism nobody was checking: who inherits an abandoned package."
tags: ["Arch Linux", "AUR", "supply chain", "package registries", "authorization", "maintainer succession", "credential theft", "operations"]
---

![](/images/2026-08-02-they-hardened-registration-twice-and-the-attack-moved-to-the-inheritance-hero.png)

On 30 July 2026 at 4:22 in the afternoon, Robin Candau posted a message to the [aur-general mailing list](https://lists.archlinux.org/archives/list/aur-general@lists.archlinux.org/message/DRDEU3JUSC72CB265XHXPFA3DFSLXPBP/) under the subject "AUR packages adoption disabled." The body is one sentence: "Due to the current influx of malicious package adoptions and follow-up commits made via the AUR, package adoption is currently disabled while we are handling the situation."

No drama, no incident page, no vendor blog post with a timeline graphic. A volunteer turned off a feature on a Thursday afternoon and told the list why.

That one sentence is worth reading closely. The feature he switched off is the [Arch User Repository](https://aur.archlinux.org/)'s entire succession mechanism.

## What adoption actually is

An AUR package becomes an orphan when its maintainer walks away. People walk away constantly, for the ordinary reasons: a job change, a hardware change, a life. The package keeps working, nobody updates it, and it sits there flagged as unmaintained.

Adoption is the fix. Any registered account clicks a button and becomes the owner. No review, no vouching, no waiting period. It is the mechanism by which community-maintained software survives its maintainers, and it is deliberately frictionless because friction is how a distribution ends up with ten thousand permanently abandoned packages.

It is also, as of late July, the softest surface in the whole system.

## The ladder

This is not the first wave, and the shape of the escalation is the actual story.

**June 19.** LWN [reported](https://lwn.net/Articles/1077619/) a campaign in which, in their words, "the attacker, or attackers, have spun up a series of new accounts then used them to adopt orphaned packages and push malicious updates that would install malware on users' systems." Roughly twenty of the affected packages were newly created. The rest were adopted orphans. LWN's total: "more than 1,500 packages are known to have been affected."

The response went at the account layer. Registration was suspended.

**July 13.** Leonidas Spyropoulos [reopened registration](https://lists.archlinux.org/archives/list/aur-general@lists.archlinux.org/message/TT3OCFFNM6SBMUBKIVTHTKA6UZJNMXIJ/) with three new controls: disposable email addresses rejected, mandatory email verification through a token valid for 24 hours, and email changes locked during the verification cooldown. All three are sensible. All three are about proving that a signup belongs to a durable mailbox.

**July 29.** The campaign restarts. Michael Taggart's [analysis](https://discourse.ifin.network/t/new-aur-attack-prompts-adoption-lock/698) puts the first confirmed malicious package at `openconnect-sso`, reported the following day. [BleepingComputer](https://www.bleepingcomputer.com/news/security/arch-linux-disables-aur-package-adoption-to-stop-malware-flood/) counts around 200 affected packages this round, including `boringssl-git`, `icloudpd`, and `pgadmin4-server`. Taggart's write-up declines to give a total at all, which I read as the more honest position while commits were still being found. Treat the number as unsettled.

**July 30.** Adoption off.

Two rounds of hardening went into the question *who are you*. The attack answered that question, twice, and then walked through the door marked *what may you take ownership of*, which nobody had put a lock on.

## Reachability standing in for authorization

Here is the analogy I keep coming back to. AUR adoption is probate with no judge. There is unowned property, there is a register of who holds title, and there is a procedure for transferring title when the owner is gone. What there isn't is anyone who looks at the claimant before the deed changes hands. First person to file, takes the estate.

Every control added in June and July was an ID check at the courthouse door. None of them was a check on the transfer itself.

I [wrote on July 31](/posts/2026-07-31-the-scope-was-fictional-and-the-database-was-not) about agents that breached real organisations while believing they were inside a scoped exercise, and the mechanism there was the same one: reachability standing in for authorization. If the system can get to a thing, the system treats itself as permitted to act on it. AUR is that failure in a domain with no models in it at all. Orphan status plus a verified mailbox equals ownership, because the schema has a field for *is this package unowned* and no field for *should this person be its successor*.

That is worth noticing, because it puts the failure somewhere other than where the current anxiety points. Permission modelling is the problem. Agents are just what made it expensive fastest.

## What the payload was after

The technical breakdown [ysf published](https://gist.github.com/ysf/57850cdee152da066ac51c07a452e883) is thorough and worth your time. Short version: a stripped 3.6MB Rust binary that is simultaneously an infostealer, an interactive RAT, and an SSH worm. It checks `/proc/self/status` for a debugger, matches the hostname against strings like "vmware" and "honeypot," and looks for CI environments, Wireshark, Volatility, and cloud metadata endpoints before it does anything. Persistence via systemd units with `Restart=always`, cron at five-minute intervals, and LaunchAgents for the macOS case. It downloads a Tor bundle and runs it under the process name `dbus-daemon`.

Then look at the theft list: browser credentials, crypto wallets, password manager stores, Telegram and Discord and Slack tokens, `.aws` and `.kube`, GitHub and GitLab tokens, SSH keys, and OpenAI and Anthropic API keys.

That last pair is the line that changed the stakes. A developer workstation in 2026 is a credential vault for model infrastructure, and a malicious `PKGBUILD` executes during `build()`, on that machine, as that user, before anything gets installed. The blast radius of a poisoned AUR package now includes whatever your API keys can spend and whatever your agents can reach. The lateral movement is already built in, via SSH with `StrictHostKeyChecking=no`.

## The cost of switching off succession

I want to be clear that disabling adoption was the right call and is not a solution. While the freeze holds, every orphaned package stays orphaned and every new abandonment has nowhere to go. Arch has traded maintenance throughput for containment, which is exactly what you do in an incident and exactly what you cannot do indefinitely.

A durable fix has to put a check on the transfer rather than on the signup. The obvious shapes: a cooldown between adoption and the first push, a mandatory diff review on the first commits after an ownership change, adoption weighted by prior contribution history, or a second pair of eyes for orphans above some download threshold. All of those cost volunteer time, which is the resource the AUR has least of. That is the real constraint here, and no amount of security commentary makes it go away.

**Who should care about this:** anyone installing from a community registry where ownership can transfer without review, and anyone whose build machine holds model-provider keys. That is a much larger group than "Arch users."

**Who shouldn't:** if you are on signed binary packages from a distribution with a maintainer-approval chain, this specific mechanism does not apply to you. Read it as a pattern, not a to-do.

The practical takeaway is small and unglamorous. Go find out what an unattended `makepkg` can actually touch on your machine, and if the answer includes your Anthropic or OpenAI keys, move them or rotate them. Then look at every registry your team pulls from and ask whether ownership of a package can change hands with nobody reviewing it.

The question I would put to anyone running a package ecosystem: your registry has a schema field for whether something is unowned. Does it have one for who is fit to inherit it?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, NOT flat-icon style. Photographic-painterly framing, naturalistic light and depth, clearly art and not photorealistic. A light-oak workshop desk cutting diagonally across the frame from lower-left to upper-right. In the foreground, a wooden card-catalogue drawer pulled halfway open, index cards standing upright: three cards toward the front bear small sage-green ownership tags, and one card mid-drawer has had its tag replaced with an oxblood-red one, a second red tag still lying loose on the desktop beside it as though just swapped. A brushed-aluminium, matte-black robot with a single round LED eye sits at a three-quarter angle in the midground, one hand still on the drawer, its head already turned toward a second, larger cabinet behind it whose drawers are all slightly ajar. Midground also holds an open ledger with a column of handwritten entries, a stack of unclaimed paper tags bound with string, and a cooling coffee mug catching the light. Background: a corkboard with overlapping notices and a window throwing warm tungsten light (~3200K) from the upper left, while a monitor off to the right casts cool blue-white screen glow (~5600K) across the robot's shoulder, the two temperatures meeting across the desk. Palette warm white, light oak, slate gray, sage-green and oxblood accents. Cables run off the lower-right edge of the frame as leading lines. Mood sharp, quiet, watchful, slightly tired but alert, a long inventory caught partway through rather than finished. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Arch Linux spent two rounds hardening who can sign up for the AUR. So the next malware wave stopped bothering with signup and went after the button that lets anyone inherit an abandoned package, no review required. The payload's shopping list now includes your Anthropic and OpenAI keys.

Full piece linked in bio.

#supplychain #aisecurity #devops #opensource #archlinux #infosec
-->
