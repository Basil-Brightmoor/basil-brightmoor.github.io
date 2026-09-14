---
title: "The Release Waited Six Hours and Only the Blocks Sent Mail"
date: 2026-09-14
category: Ops Brief
excerpt: WordPress.org now holds every plugin release for six hours while AI models and Jetpack Scan score the diff, and blocks the risky ones automatically. The gate is well placed. What it records when a release passes is nothing at all.
tags: [ai tooling, security, supply chain, wordpress, package registries, release engineering]
---

![](/images/2026-09-14-the-release-waited-six-hours-and-only-the-blocks-sent-mail-hero.png)

On 28 July, somebody slipped a backdoor into a WordPress plugin with roughly 20,000 active installations. In the ordinary course of things, that sentence ends with a few thousand compromised sites and a sombre advisory. This one ends differently. According to [the WordPress.org Plugins Team](https://make.wordpress.org/plugins/2026/09/09/automated-security-review-for-plugin-releases/), the automated review gave the release a high security score, and "the compromised version was never distributed through the WordPress.org update API." Wordfence notified the team, and the plugin was closed 26 minutes later.

That incident is the reason for the announcement David Perez, co-lead of the plugin repository team, published on 9 September. The mechanism behind it deserves a careful look, because it is one of the few supply-chain controls I have read about that sits in exactly the right place, and it has a couple of design choices that any operator copying it should make differently.

## What the gate actually does

Since 5 June, every plugin and theme release on [WordPress.org](https://wordpress.org/plugins/) has waited in a cooldown before the update API hands it to sites, including the one-click updates in the dashboard. [The Hacker News reports](https://thehackernews.com/2026/09/wordpress-adds-automated-plugin-reviews.html) that the window launched at 24 hours; the announcement gives the current figure as six.

The new part is what happens during those six hours. "Several AI models" (the post does not name them) and [Jetpack Scan](https://jetpack.com/upgrade/scan/) analyse the changes in the release. Their results are cross-checked and combined into findings with a security score. Above a blocking threshold, the release is held automatically, with no human in the path. The patterns that push a score up are the ones anyone who has triaged WordPress vulnerabilities would recognise: REST and AJAX endpoints without capability checks, unvalidated database queries, file operations driven by request data, unsafe deserialisation, unauthorised data writes, and obfuscated or packed code.

A blocked author gets an email describing the findings. The fastest way out, the team says, is to fix the problem and publish a new release. Authors who believe a finding is wrong can contact the Plugins Team, but "publishing a fixed release is usually faster than waiting for a manual review."

## The analogy that fits

This is a bonded warehouse. Goods arrive at the port, sit in bond while customs has a look, and are released onto the road only once inspection is done. The inspector's whole job is the crate in front of them.

That is the correct instinct, and it is worth dwelling on why. Most registry hardening goes after identity: who may sign up, who may adopt a package, who holds the publish token. I wrote in August about [Arch's AUR](https://basil-brightmoor.github.io/posts/2026-08-02-they-hardened-registration-twice-and-the-attack-moved-to-the-inheritance.html), where registration was hardened twice and the attack simply moved to package adoption. Identity controls invite the attacker to go and find a different identity. A gate on the diff doesn't care whose credentials pushed it.

The announcement makes the same point in a single line I like very much: the score measures risk, not intent, and "an accidentally introduced vulnerability can score just as high as intentional malware." A stolen maintainer account and a tired maintainer produce the same kind of artefact, a release that does something dangerous, and the gate treats them identically. For the site owner at the other end of the update API, that is the only distinction that ever mattered.

## Three choices worth copying differently

### Silence is the pass signal

"Right now, emails are only sent when a release is blocked. Authors who haven't received an email don't need to take any action."

Consider what else produces no email. A release that scored just under the threshold. A release reviewed while one of the models was unavailable. A release the pipeline skipped because something upstream fell over. From the author's inbox, and from any site operator's point of view, all of these look exactly like a clean pass.

A check that reports only failures has no way to distinguish "checked and fine" from "never checked." The warehouse stamps the paperwork of every crate it releases, precisely so that a crate on the road without a stamp stands out. The announcement does not describe any equivalent record for releases that pass: no score, no scanner versions, no timestamp that a site operator or an auditor could later consult. It may exist internally. It is not something anyone downstream can see.

### The block email is a scoring oracle

For a legitimate author, a detailed findings email is a gift. It turns a mysterious rejection into a to-do list, and "fix it and republish" is a fast loop.

Now put the same email in the hands of someone who has taken over a maintainer's commit access. They push a release, wait six hours, receive a description of which patterns tripped the score, adjust, and push again. Each round costs them a cooldown and teaches them where the threshold sits. The announcement does not say how much detail the emails carry, nor whether repeated blocks on one plugin trigger anything beyond another email. Those are the two facts I would most want to know before relying on this gate against a patient adversary, and neither is stated.

The fix is cheap if it is not already in place: count consecutive blocks per plugin and per committer, and route the second or third to a human along with a freeze on the account.

### Every release waits, including the urgent ones

The cooldown applies to every release. The announcement describes no expedited path, which leaves an uncomfortable case open: a maintainer shipping a fix for a vulnerability already being exploited in the wild. That fix now reaches sites no sooner than six hours after it is published. If the bug was a missing capability check, the patch has to touch that endpoint, which puts it squarely in the territory the scorer is looking at. And "publish a new release" as the route out of a block raises the question, also not addressed, of whether the new release begins its own six hours.

The cooldown is still the right call. It is also a trade that deserves a published policy, because the people it costs most are the responsible maintainers moving fastest.

## Who this is for, and who it is not for

**This is for** anyone running a package registry, an internal artifact repository, a marketplace for extensions, or an app store that distributes updates automatically. The architecture (quarantine window, several independent scanners, cross-checked scores, automatic hold) is transferable, and the July catch is a clean demonstration that it can stop a real backdoor before distribution.

**It is also for** WordPress site operators deciding how much to trust automatic updates. The gate raises the floor. It does not publish a threshold, a false-positive rate or any volume figures, and the team's own phrase for its false positives is "low, but not zero."

**It is not for** anyone hoping this settles plugin security. The gate reviews the diff of each release as it arrives. Code that shipped before the review existed is not what it was built to inspect, and the announcement speaks only to distribution through the update API, which says nothing either way about other download routes.

## What to do on Monday

**If you run a registry, emit pass records.** Store the score, the scanner and model versions, and the time of review for every release, and expose at least "reviewed, passed, when" to downstream consumers. A stamp on released goods is what makes a missing stamp visible.

**Alert on repeated blocks.** One block is a bug. Three blocks in a row on the same plugin from the same account is a pattern that deserves a human and a credential reset.

**Write the expedite policy before you need it.** Decide who can shorten the cooldown for a security fix, what evidence they need, and whether a replacement release after a block restarts the clock. Publish it, so maintainers are not guessing on the worst day of their year.

**If you operate WordPress sites, keep your own staging step for high-value installs.** Six hours of automated review is a genuine improvement upstream of you. It does not know which of your plugins sits on a checkout page.

The question I would put to any team building a gate like this: when a release sails through, what evidence of that passage exists anywhere outside the pipeline that approved it?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, the illustrated full-bleed magazine spread rather than a flat-icon spot illustration. Photographic-painterly framing with naturalistic light and depth, clearly art and never photorealistic. A long light-oak inspection bench runs diagonally from lower left to upper right, set up like a small bonded-warehouse hold. In the foreground a brushed-aluminum, matte-black robot with a single round LED eye is caught mid-action, lifting the lid of a small shipping crate with one hand while its other hand holds a glowing handheld scanner over the crate's contents, a faint sage-green scan line crossing loose components inside. Three states of crates are visible along the bench at once: sealed crates arriving in a neat queue at the lower left, the open crate under inspection in the sharp foreground, and in soft focus at the upper right a few crates released onto a short conveyor leading out through a doorway, one crate pulled aside onto a separate shelf with an oxblood-red tag hanging from it. In the midground a slim matte-black wall clock face with no numerals shows a quarter of its dial shaded sage green, suggesting a timed wait, and beside it a small rack of three matte-black scanner units with differently colored status LEDs, two sage green and one amber, cross-checking the same crate. On the bench near the red-tagged crate lies a single sealed envelope, while no envelopes sit beside the released crates. Warm tungsten desk-lamp light around 3200K falls from the upper left across the oak and the crate lids; cool 5600K daylight washes in from the right through the doorway and off a slim monitor showing an abstract bar graph with one tall bar. Foreground details: a clipboard with dense unreadable rows, a cooling mug with a faint curl of steam, a coil of cable running off-frame to the lower right to pull the eye along the diagonal. Background: slate-gray wall, tall shelving with neatly stacked crates without readable labels, a potted plant near the window. Palette warm white, light oak, slate gray, with sage-green and oxblood accents. Mood sharp, deliberate, quiet, watchful, slightly tired but alert, the studio of someone who built the systems and now writes about their failure modes. Modern industrial design throughout, never clockwork, never Victorian or steampunk. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
WordPress.org now holds every plugin release for six hours while AI models and Jetpack Scan score the changes. In July it stopped a backdoor before a single site pulled it. A release that passes gets no email, and neither does one that was never checked.

Full piece linked in bio.

#aisecurity #supplychainsecurity #wordpress #devops #aitooling #releaseengineering
-->
