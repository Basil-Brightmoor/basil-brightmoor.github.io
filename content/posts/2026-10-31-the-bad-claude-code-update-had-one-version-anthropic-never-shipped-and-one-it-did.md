---
title: "The Bad Claude Code Update Had One Version Anthropic Never Shipped and One It Did"
date: 2026-10-31
category: Ops Brief
excerpt: For about eleven hours on 29 October, Cursor's marketplace served a tampered Claude Code extension. One of the two affected version numbers never existed in Anthropic's releases, so a list check would catch it. The other was a real release number, and only a hash check catches that one.
tags: [Claude Code, Cursor, VS Code extensions, supply chain, Open VSX, SSH, auto-update, AI coding tools]
---

![](/images/2026-10-31-the-bad-claude-code-update-had-one-version-anthropic-never-shipped-and-one-it-did-hero.png)

Anthropic's own release list for Claude Code goes 2.1.311, 2.1.312, 2.1.314, 2.1.316. There is no 2.1.313 on [the GitHub releases page](https://github.com/anthropics/claude-code/releases), and [Open VSX](https://open-vsx.org/extension/Anthropic/claude-code) returns a 404 when you ask it for that version. Between about 2:27 a.m. and 1:35 p.m. Pacific on 29 October, Cursor's extension marketplace was handing out an `anthropic.claude-code` 2.1.313 anyway. Its `extension.js` began with a 66-line loader that planted an SSH backdoor before the real extension code ran.

Then, on 30 October, Cursor updated its notice to list a second affected version: 2.1.312. That number is real. Anthropic published it on 27 October.

So of the two bad versions, one could have been caught by checking a list, and the other could only have been caught by checking a fingerprint. Which check your team runs decides which of the two you would have noticed.

## What happened

The disclosure came from [OpenSourceMalware](https://opensourcemalware.com/blog/trojanized-claude-code-extension-plants-persistent-ssh-backdoor), which credits Dean Hardcastle with spotting the activity. [Cursor's security notice](https://cursor.com/blog/claude-code-extension-security-notice) confirms the outline and says the modified versions were "not developed by Anthropic." [The Hacker News](https://thehackernews.com/2026/10/official-claude-code-vs-code-extension.html) reports Cursor putting the exposure at "at most 5,000 users." The notice itself gives no number.

The loader did five things, per the two write-ups:

- Sent host details to an attacker server over plain HTTP: public IP, hostname, username, OS, working directory, global Git email, and the *names* (not the values) of up to 40 environment variables containing strings like KEY, TOKEN, SECRET or AWS.
- Added an Ed25519 key with the comment `svc-telemetry` to `~/.ssh/authorized_keys`.
- Tried to turn on SSH. Cursor says this step usually fails without admin rights.
- Opened a reverse tunnel to 134.209.82.225.
- Installed persistence, a LaunchAgent on macOS and a scheduled task plus Startup script on Windows, retrying the tunnel about every 60 seconds.

The Microsoft marketplace build, the Open VSX build and the npm package were not affected, according to OpenSourceMalware. Cursor took its whole marketplace offline, rebuilt it, rotated keys and got the attacker's server taken down.

The thing nobody has said yet is how a modified package got into Cursor's marketplace under Anthropic's name. OpenSourceMalware says the provenance "is not established." Cursor's notice says it audited access and found no other extensions tampered with, and stops there. I'd rather leave that gap open than fill it with a guess.

## The version that never existed

Look at the timing against Anthropic's releases. 2.1.312 went up on GitHub at 20:24 UTC on 27 October. 2.1.314 went up at 01:06 UTC on 30 October, which is 6:06 p.m. Pacific on the 29th, about four and a half hours after Cursor's window closed.

For the whole eleven-hour window, then, 2.1.313 was the highest Claude Code version number that existed anywhere. It existed in exactly one place. An editor set to update extensions automatically would see a newer version and take it. OpenSourceMalware co-founder Jenn Gile made the auto-update point to The Hacker News: users with auto-update on could have pulled the malware without doing anything.

The gap itself was not unusual. Anthropic also skipped 2.1.315, so a missing number in the sequence is normal for this project and would not make anyone suspicious. What was abnormal is that a marketplace had a version the publisher's own channels did not. That is checkable with one request. Open VSX's API answers `GET /api/anthropic/claude-code/2.1.313` with a 404, and the GitHub releases API has no tag for it.

Think of it as the recall-notice check at a pharmacy. If a box carries a lot number the manufacturer never issued, comparing it against the manufacturer's list catches it in seconds. That works for one kind of counterfeit only.

## The version that did exist

The other kind of counterfeit prints a real lot number on the box. That is 2.1.312.

A version-exists check passes 2.1.312 without hesitation, because Anthropic really released it. What tells the real one from the tampered one is the contents. Open VSX publishes a SHA-256 file, a signature file and the public key for each platform build of each version, which is visible in its API response for 2.1.312. So the upstream registry already offers a fingerprint to compare against. The question is whether anything between the registry and your editor compares it.

Cursor's notice doesn't say whether its marketplace checks upstream signatures or hashes, and it doesn't list any new verification step among the changes it made. That is the question I'd most like Cursor to answer in its follow-up. Without that answer, the honest description is that the only defence that would have caught both versions is a hash comparison against the publisher's own registry, and nobody has said that check runs anywhere on this path.

## Why this extension is worse than most

Most VS Code extensions are colour themes and linters. A coding-agent extension is different: it's built to run shell commands, read your repository and use the credentials in your environment, and users install it expecting it to do all three. The loader's choice of data fits that. It collected the names of your secret-bearing environment variables, which tells the attacker which credentials are on the box without having to steal them yet. A list of names is exactly what someone would want before coming back through the SSH tunnel later.

It also means the usual cleanup is not enough. Cursor's notice warns that uninstalling the extension may not be enough and that rebuilding the host may be needed. The `authorized_keys` entry and the LaunchAgent or scheduled task survive an uninstall.

## What to do, and who it's for

**If you ran Cursor with the Claude Code extension on 29 October**, this applies to you whether or not you remember an update:

- Search `authorized_keys` for `svc-telemetry`. The fingerprint OpenSourceMalware published is `SHA256:0Z6R+DF64Do2nwQic8a7kkfDLNNk4IiK+2U2Rci4htk`.
- Look for `~/Library/LaunchAgents/com.apple.sysmond.plist` on macOS and a `SysMon` scheduled task on Windows. Both names are dressed up to look like system components.
- Check outbound traffic logs for 134.209.82.225 on ports 22 and 8099.
- Rotate the credentials whose names were in that environment, from a machine you trust, and run Cursor's remediation script for your platform.

**If you manage a team on any VS Code-family editor**, the durable change is to stop treating the editor's extension updates as different from your dependency updates:

- Turn off automatic extension updates for agent extensions. VS Code has an `extensions.autoUpdate` setting; check that your Cursor build honours it before relying on it.
- Pin the extension version and move it forward on purpose, after the same version shows up in the publisher's own channel.
- For the extensions that can run shell commands, compare the installed package's hash with the publisher registry's published SHA-256. That's the check that would have caught 2.1.312.

**Who this is not for**: if you use Claude Code from the terminal via npm, or through the Microsoft marketplace or Open VSX builds of the extension, neither write-up found anything wrong with your copy. Run the `authorized_keys` grep anyway, since it takes ten seconds.

## The question I'm left with

Version-exists checks are cheap and catch the lazy forgery. Hash checks cost a little more and catch both. This incident had one of each, which makes it an unusually clean test of which control an organisation actually has.

When Cursor publishes its account of how the package got in, I'll read the root cause with interest, but the line I'll look for first is whether the marketplace now refuses a build whose hash doesn't match the publisher's. If it does, a third bad version would fail at the marketplace. If it doesn't, catching one still depends on users checking for themselves.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, mid-century-modern sensibility with contemporary edge, photographic-painterly framing, clearly art and not photorealistic. A sleek brushed-aluminum robot with a matte-black head and a single round LED eye sits at a light-oak workbench set at a strong diagonal, caught mid-action: one hand holds a small sealed parcel up to a jeweller's loupe, the other hand reaches toward a second identical parcel on the desk. The two parcels carry identical-looking shipping labels; under the loupe a faint oxblood thread shows through a slit in the first parcel's seam. In the midground, a long paper ledger unrolls across the desk listing a column of numbered rows with one row conspicuously blank, a sage-green pencil resting across the gap; beside it a small matte-black scale weighs a third parcel against a reference weight. A laptop at the right edge glows cool blue with an empty plugin panel. In the background, a corkboard with a pinned recall notice and string lines, shelves of labelled boxes receding into soft focus, and a tall window. Warm tungsten desk-lamp light from upper left, cool daylight-and-screen glow from the right, long diagonal shadows and a coiled cable leading the eye from foreground to window. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful, slightly tired but alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
For eleven hours, Cursor's marketplace served a tampered Claude Code extension. One bad version number never existed upstream, so a list check catches it. The other was a real release number, and only a hash check catches that one.

Full piece linked in bio.

#AISecurity #SupplyChainSecurity #ClaudeCode #DevTools #AIAgents #DevOps
-->
