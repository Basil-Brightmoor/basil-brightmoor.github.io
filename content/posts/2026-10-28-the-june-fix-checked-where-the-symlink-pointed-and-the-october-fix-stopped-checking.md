---
title: "The June Fix Checked Where the Symlink Pointed and the October Fix Stopped Checking"
date: 2026-10-28
category: Ops Brief
excerpt: Tailscale patched its SSH socket forwarding twice this year. In June it made the root daemon check paths more carefully. In October it took the work away from root, and the careful check was deleted.
tags: [Tailscale, SSH, privilege separation, TOCTOU, security advisories, zero trust, headscale, Linux]
---

![](/images/2026-10-28-the-june-fix-checked-where-the-symlink-pointed-and-the-october-fix-stopped-checking-hero.png)

One line in a Tailscale commit message is worth more than most of the coverage of this week's release. In [the change that reroutes SSH forwarding](https://github.com/tailscale/tailscale/commit/4adc3c051cb2cfa792d29398bccde4408118ba9e), James Tucker writes that "the EvalSymlinks re-validation is dropped, and the kernel's DAC is the boundary."

That re-validation reads like the fix Tailscale shipped in June for the same feature. In October the company did not patch that check. It deleted it, because the code that needed it no longer runs as root.

## Two bulletins for one feature

Tailscale's [security bulletins page](https://tailscale.com/security-bulletins) has two entries about Unix socket forwarding in Tailscale SSH, five months apart.

**TS-2026-004, 3 June.** Permission checks matched socket paths lexically and did not follow symlinks, so an unprivileged user could make a symlink to a protected socket and reach it through SSH. The fix checks symlink destinations against the allowlist. Fixed in 1.98.9, credited to Tim Sageser of dtrsecurity.

**TS-2026-014, 26 October.** The SSH server inside the root-run `tailscaled` checked paths lexically "but then acted as root", so a user allowed to forward could reach root-only sockets such as the Docker socket or Tailscale's own local API. It affects people with Tailscale SSH enabled "who also allow local or remote forwarding in their access policies." Fixed in 1.104.4.

The October findings came from [Tailworm](https://tailworm.com/), a report by Erica Windisch of Cyberdione Labs that tested client 1.104.2 and headscale 0.29.5 in a lab. Its first finding is that Unix socket forwarding performed path checks and file operations as root, so an ordinary SSH session could replace, dial or delete privileged sockets. [The Hacker News reports](https://thehackernews.com/2026/10/tailscale-patches-ssh-flaws-that-could.html) that forwarding to the Docker socket gave Windisch a root shell, and that she described the disclosure as "reported but not coordinated." The proof of concept went only to Tailscale's security team.

## The concierge with the master key

An analogy helps me with the difference between the two fixes.

A hotel concierge holds a master key. A guest asks for a parcel to be left in room 214. The concierge checks the guest list, sees that room 214 belongs to this guest, and walks up with the master key. The June bug was a guest who had stuck a "214" card on the door of the manager's office. The June fix taught the concierge to look past the card at the real room number.

The October bug was that the room could change between the check and the delivery. The concierge reads the list, turns away, and by the time the master key goes into a lock the door behind the "214" card leads somewhere else. Look as carefully as you like. The check happens at one moment and the master key opens the door at another.

Tailscale's October fix stops sending the concierge. The guest gets their own key and does the delivery. If the door leads to the manager's office, the guest's key does not open it.

## What the October patch changed

The [1.104.4 release](https://github.com/tailscale/tailscale/releases/tag/v1.104.4) went up on GitHub at 01:05 UTC on 28 October. Comparing it with 1.104.2 shows 42 commits, 30 of them in `ssh/tailssh`. Three of them carry the main change.

- **Unix socket forwards** ([4adc3c0](https://github.com/tailscale/tailscale/commit/4adc3c051cb2cfa792d29398bccde4408118ba9e)). Forwarded sockets are now "dialed and bound by children with the authenticated local user's credentials, never by root tailscaled." The lexical allowlist (the user's home, `/tmp` and `/run/user/<uid>`) stays as coarse policy. The symlink re-validation goes, and ordinary Unix file permissions decide.
- **TCP forwards** ([342ebd6](https://github.com/tailscale/tailscale/commit/342ebd6f99ac5711db73b6a347d9c0fa5785b4cc)). TCP `-L` and SOCKS `-D` forwards are resolved and dialed in a child running as the logged-in user. Socket ownership survives the handoff, so, in the commit's words, UID-based firewall policy "sees the mapped user." Before this, a host firewall rule written against a user's UID was looking at traffic that belonged to root.
- **Agent forwarding** ([0284e16](https://github.com/tailscale/tailscale/commit/0284e166caabdcb1eb021f26432a717bd815bdbb)). The directory holding the forwarded agent socket "was left root-owned and chmod 0755, letting every local user reach other users' agent sockets." It is now owned by the session user, mode 0700, and removed when the session ends.

The tests show what the authors were worried about. The main commit adds two regression cases. In one, a symlink inside the allowlist points at a root-owned canary socket and must fail with permission denied. In the other, a directory is swapped mid-request and the canary must never be served. The first case is the June bug. The second is the race that a better check cannot close.

## The pattern for people who write daemons

The general lesson is an old one in Unix security, and this pair of bulletins illustrates it unusually well. When a privileged process checks a path on someone else's behalf and then opens it with its own privileges, the check and the use are two separate moments, and anyone who can change the filesystem between them wins. Each fix to the check closes the case someone found. Doing the operation with the requester's own credentials removes the gap, and the kernel's permission check runs at the moment of use.

You can see the cost in the diff stats. The main forwarding commit adds 2,217 lines and removes 110, with a new per-connection monitor and one-shot child processes, because doing the work as the user means starting a process as the user. A symlink check is a far smaller change. My guess, which nothing published confirms, is that the difference in size is part of why the small fix shipped first.

## What to do if you run Tailscale SSH

- **Upgrade the servers to 1.104.4 or later.** The SSH server runs only on Linux and the open-source macOS build, per [Tailscale's SSH documentation](https://tailscale.com/kb/1193/tailscale-ssh), so those are the machines to inventory.
- **If you cannot upgrade yet, turn off forwarding.** Tailscale's [investigation update](https://tailscale.com/ssh-investigation-update) gives `TS_SSH_DISABLE_FORWARDING=1` in the `tailscaled` service environment, followed by a restart. It leaves SSH working and, per Tailscale, "mitigates several of the more serious findings."
- **Do not count on check mode here.** Tailscale's documentation describes check mode as requiring re-authentication "before establishing an SSH connection," with a default window of 12 hours. Tailworm notes that it gates session setup, not the forwarding requests made inside an approved session.
- **Write SSH grants as device-to-device pairs.** Tailworm calls per-pair grants "the single control that stopped" spread in its lab, and advises against identity-wide or tag-wide accept rules.
- **If a node may already be compromised, delete it at the control plane.** The report says "reimaging alone is not containment": a node's identity is key material in its state file, and a copied key stays valid until the device is removed or the key expires.

**This matters most for** teams that use Tailscale SSH on shared Linux hosts, build servers, or anything with a Docker socket, and that allow forwarding in their policy.

**It matters less for** people who use Tailscale only for networking and run OpenSSH over the tailnet. These bulletins concern Tailscale's built-in SSH server.

**It is still open for headscale users.** The self-hosted control server is a separate project. Tailworm says that in headscale 0.29.5 forwarding is granted automatically on every SSH grant and cannot be switched off in policy, so it advises treating "every headscale SSH grant as root-equivalent." Its own fix table, dated 28 October, marks the client side of one finding fixed and headscale pending. The client upgrade still helps, since the root-dialing code lived in the client.

## The question for every other daemon

Tailscale's [update](https://tailscale.com/ssh-investigation-update) promises a technical write-up, and I would like it to say plainly why the June fix stayed at "check better" instead of "stop acting as root." The answer is useful to anyone who maintains a root daemon that opens files on behalf of a user: container runtimes, backup agents, desktop helpers, the local API of every agent tool that runs as a system service.

So here is the audit question for your own stack. For each root process that accepts a path from someone less privileged, does it open that path as root after checking it, or does it hand the open to something running as the person who asked?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A long hotel corridor seen at a strong diagonal from lower left to upper right, light-oak doors receding along the right-hand wall. In the foreground, sharp, a sleek brushed-aluminum robot concierge with matte-black joints and a single round LED eye stands at a 30-degree angle, caught between two actions: one hand lowering a heavy matte-black master key back into a tray, the other passing a small plain slate-gray key across to a second, smaller aluminum robot holding a parcel. In the midground, one door stands slightly ajar with a blank paper card taped over its number plate, and through the gap an oxblood-lit room is visible where a different door should be. Further down the corridor, two more doors in soft focus each carry a small sage-green indicator light. On a narrow console table in the foreground: an open ledger with abstract unreadable marks, a ring of keys, a small potted plant, a ceramic cup catching lamp light. Background: a tall window at the corridor's far end. Warm tungsten lamp light from a wall sconce at the upper left falls across the concierge and the console; cool blue-white daylight from the far window at upper right lights the ajar door and throws long shadows back along the patterned runner carpet, whose stripes act as leading lines into depth. Mood: deliberate, quiet, watchful, a responsibility being handed over at the right moment. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Tailscale fixed its SSH socket forwarding twice this year. The June patch taught the root daemon to check paths more carefully. The October patch stopped running that code as root, and deleted the careful check.

Full piece linked in bio.

#tailscale #infosec #linux #ssh #devops #zerotrust
-->
