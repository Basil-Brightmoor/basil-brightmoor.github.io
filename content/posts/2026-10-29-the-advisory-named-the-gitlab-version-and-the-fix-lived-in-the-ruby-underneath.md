---
title: "The Advisory Named the GitLab Version and the Fix Lived in the Ruby Underneath"
date: 2026-10-29
category: Ops Brief
excerpt: Alpine Linux upgraded its GitLab server to a release the advisory called fixed, and the server stayed vulnerable. GitLab's fix was a patch to the Ruby in its own packages, and Alpine's image ran its own Ruby.
tags: [GitLab, Ruby, Alpine Linux, CVE-2026-97229, security advisories, patch management, containers, supply chain]
---

![](/images/2026-10-29-the-advisory-named-the-gitlab-version-and-the-fix-lived-in-the-ruby-underneath-hero.png)

On 22 October, Alpine Linux upgraded its GitLab server to version 19.3.6. GitLab's advisory for CVE-2026-97229, a remote code execution bug rated CVSS 10.0, lists 19.3.5 as the fixed release on that branch. So on paper Alpine was one patch release past the fix.

Four days later Alpine found the server was still vulnerable. Its [incident post of 28 October](https://alpinelinux.org/posts/GitLab-security-incident-CVE-2026-97229.html) gives the reason in two sentences: the fix is a patch to Ruby rather than to GitLab's own code, and GitLab applies it only in its official packages. Alpine's image used standard Ruby, so the upgrade changed the GitLab version and left the vulnerable code in place.

The attack itself had come earlier, on 20 and 21 October, against the 19.3.4 the server was still running. But the 19.3.6 upgrade is the more useful lesson, because it is the step most operators would have stopped at. Version numbers usually record where a fix lives. In this case they did not.

## What the advisory says

GitLab released [19.4.2, 19.3.5 and 19.2.8 on 12 October](https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-4-2-released/). The entry for CVE-2026-97229 says a crafted regular expression in a CI/CD configuration "could have allowed an unauthenticated user to execute arbitrary code on the GitLab server." The affected range is given entirely in GitLab versions: 19.2 before 19.2.8, 19.3 before 19.3.5, 19.4 before 19.4.2.

Near the top of the page is a standing rule: "When no specific deployment type (omnibus, source code, helm chart, etc.) of a product is mentioned, it means all types are affected." The entry names no deployment type, so source installs and custom builds are covered.

The fix appears further down, in the bug-fix list for each release, as two lines: "Add Ruby regexp program size patch for 3.3 and 3.4" and "Add Ruby regexp repeat-range double-free patch for 3.3 and 3.4". When I read the page on 29 October, it said nothing about what someone running GitLab on a Ruby they had built or installed themselves should do. The advisory says everyone is affected, but the fixed version numbers only certify a fix for people who run the Ruby GitLab ships.

## The fix had no upstream release for eleven days

Ruby's maintainers published [their own fixes on 23 October](https://www.ruby-lang.org/en/news/2026/10/23/regexp-fixes-for-gitlab-cves/): Ruby 3.3.13, 3.4.12 and 4.0.9 carry all three regular-expression fixes, covering four CVEs that GitLab reported. The post says GitLab dealt with the issues in its own releases by "patching the Ruby it ships."

Between 12 and 23 October, then, the fix existed in GitLab's packages and in no released version of Ruby. If you ran GitLab from source or on your distribution's Ruby, there was no upstream Ruby release you could upgrade to. [Rapid7's technical analysis](https://www.rapid7.com/blog/post/ra-gitlab-ci-cd-regex-integer-overflow-technical-analysis-cve-2026-97229/) points to the Ruby backport living in an omnibus-gitlab merge request, so someone who knew where to look could have carried the patches by hand. Nothing in the advisory told anyone to look there.

The Ruby post adds two details that matter for triage. Only programs that compile a regular expression from a string an attacker controls are affected, through `Regexp.new`, `Regexp.union` or interpolation such as `/#{input}/`. And `Regexp.timeout` does not protect against these bugs, and capping pattern length is no reliable defence either, "because some of them can be triggered by short patterns."

## The garage that ordered from the usual supplier

A car recall is a useful comparison. The manufacturer announces a recall for model years 2019 to 2024, and the fix is a replacement fuel pump that dealers fit. Most owners take the car to a dealer and get the new pump.

Now suppose you use an independent garage that buys its pumps from the regular parts supplier, and for eleven days that supplier still carries only the old design. The garage does the recall service, and your paperwork says the recall is done, but the car still has the faulty pump. Nothing on the recall notice told you that the remedy was a specific part only the dealer had in stock.

Alpine was in the independent garage's position, and it says the same of anyone running self-compiled GitLab or a container image that installs its own Ruby.

## What happened on Alpine's server

Alpine's account is candid, including about its own mistake. On 13 October it upgraded to 19.3.4 instead of 19.3.5, "by mistake." On 20 October a newly registered account began probing. On 21 October the main attempt came, against a server still on 19.3.4: crafted CI configurations crashed GitLab's worker processes eight times, and in four of those crashes the attacker got partway through the exploit before failing at the next step. The attacker had also downloaded Alpine's GitLab container image, which Alpine reads as tuning the exploit to its exact build.

The 22 October upgrade to 19.3.6 would have closed the hole on GitLab's official packages. It did not close it on Alpine's. The account was blocked on 23 October, return attempts on 25 and 26 October failed, and on 26 October Alpine found the server still vulnerable. On 27 October it closed GitLab to everyone except developers and build servers and rebuilt it. The rebuild finished on 28 October, with passwords reset, GitLab's secret keys replaced, and a fixed Ruby underneath.

Alpine says it "found no evidence" that the exploit succeeded but "cannot rule it out." It explains why: a successful run would leave no crash and no trace in the web logs, some logs from the attack day are gone, and neither Alpine nor its hosting provider logged outbound connections. So Alpine treated the server as compromised.

The checks on the software supply side are the part I would copy. Alpine compared aports commits from 20 to 22 October against a developer's clone and all 45 build servers, confirmed that packages built from 20 to 24 October matched the commits published on git.alpinelinux.org, and confirmed that the four releases of 21 October were built from those verified commits. Signing keys have never been stored on the GitLab server. That is what let Alpine say its packages were sound while it was still unsure about the server.

How hard the bug is to exploit is still unsettled. GitLab scores it as needing no privileges. Rapid7's working proof of concept, built against the official 19.4.1 image, needed write access to a public project, and Rapid7 says "only the final CI lint request is unauthenticated." It does not know how the original report avoids the write step. On a server where a newly registered account can get a CI configuration in front of GitLab, as happened on Alpine's, that requirement does not stop much.

## What to check on your own GitLab

- **Find out which Ruby your GitLab actually runs.** If you use the Linux package or GitLab's official container image, the version number is enough: move to the newest release on your branch. If you build from source, use a distribution package, or build your own container image, run `ruby -v` in the environment GitLab runs in. Per Alpine and Ruby, you need 3.3.13, 3.4.12, 4.0.9 or later as well as a fixed GitLab.
- **If you use Alpine's image, pull it again.** Alpine says `alpinelinux/gitlab:19.3.6` published on 27 October contains Ruby 3.3.13, and that any 19.3.6 pull from before that date, and every older tag, is vulnerable. The tag stayed the same while the contents changed, so a digest pin from before 27 October still points at the vulnerable build.
- **Don't trust a version-only scanner here.** A tool that compares the GitLab version string with the advisory's fixed list would have marked Alpine's server as fixed on 22 October. If your vulnerability tooling reads only the application version, this is a case it cannot see.
- **If your server was exposed between 12 October and your Ruby upgrade, follow Alpine's lead.** Its list of what a successful exploit could reach includes CI/CD variables, runner tokens, webhook and mirror credentials, and 2FA secrets. The deciding questions are whether outsiders can register and create projects, and whether you have logs that would show a successful run.
- **Check your other Ruby services too.** The Ruby fixes apply to any program that compiles a regular expression from user input. A search for `Regexp.new` and interpolated patterns in your own code is cheap.

**This matters most for** anyone running GitLab outside GitLab's own packages: source installs, distribution packages, and custom images. It also matters for anyone who maintains a downstream package of an application that ships its own patched runtime.

**It matters less for** GitLab.com and GitLab Dedicated, which GitLab says are already patched, and for Linux-package installs that are current on their branch.

## The question to ask of every advisory

This is related to the Tailscale case I wrote about [yesterday](https://basil-brightmoor.github.io/posts/2026-10-28-the-june-fix-checked-where-the-symlink-pointed-and-the-october-fix-stopped-checking.html), but here the issue is where a fix lives rather than what it checks. A vendor's fixed version describes a whole bundle: the application code plus whatever the vendor builds and ships with it. When the fix is in the vendor's code, every build of that version has it. When the fix is in a patched runtime or library the vendor bundles, only the vendor's own builds have it, and the version number no longer tells you whether you are safe.

Alpine has written the answer into its own process. Among its changes after the incident: apply critical GitLab security releases within a day, and "check each release for Ruby or other component patches our own build must apply."

So for each critical advisory that affects something you build yourself, ask one question before you close the ticket: is the fix in the application's code, or in something the vendor ships alongside it? If it is in the second place, which version of that component are you running?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A small independent workshop garage seen at a strong diagonal from lower left to upper right. In the foreground, sharp, a sleek brushed-aluminum robot mechanic with matte-black joints and a single round LED eye, caught mid-action: one hand lowering a slate-gray engine component into an open machine casing on a light-oak workbench, the other hand holding up a clipboard with a sage-green tick mark and no legible writing. Inside the open casing, visible only to the viewer, a small oxblood-red glow sits deep beneath the new part, hidden under the surface. In the midground, two parts boxes on a shelf: one plain cardboard box, already opened, and one sealed matte-black box with a sage-green indicator light, still on the shelf and unopened. Further back in soft focus, a row of three identical machines on stands, each with a small status light, two sage-green and one faint oxblood. On the bench in the foreground: a coffee mug going cold, a coil of cable running diagonally off-frame, a small potted plant, an open notebook with an abstract hand-drawn schematic. Background: a tall roll-up door half open onto cool morning light. Warm tungsten work-lamp light from the upper left falls across the robot and the bench; cool blue-white daylight from the open door at the upper right lights the shelf and the row of machines and throws long shadows across the concrete floor, whose expansion joints act as leading lines into depth. Mood: deliberate, quiet, watchful, a job that looks finished and is not. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Alpine Linux upgraded GitLab past the release the advisory called fixed, and its server stayed vulnerable. The fix was a patch to the Ruby in GitLab's own packages, and Alpine ran its own Ruby.

Full piece linked in bio.

#gitlab #ruby #infosec #devops #patchmanagement #supplychainsecurity
-->
