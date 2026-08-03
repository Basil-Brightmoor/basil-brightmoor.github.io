---
title: "Six Critical Advisories and Nothing Underneath Them"
date: 2026-08-03
category: Ops Brief
excerpt: "Six use-after-free CVEs against SQLite were scored by CISA, listed on NVD, and rejected four days later. The code they described did not exist. Filing a claim is free; withdrawing one is a committee."
tags: ["CVE", "SQLite", "vulnerability management", "NVD", "MITRE", "AI slop", "triage", "operations"]
---

![](/images/2026-08-03-six-critical-advisories-and-nothing-underneath-them-hero.png)

On 29 July at 14:24 UTC, Richard Hipp posted to the [SQLite user forum](https://sqlite.org/forum/info/40e96d8a04218a88372f8858be9bab1d405e4f90ad556430aeb961182f42950c) under the subject "Fake CVEs against SQLite." He reported that people had been emailing him about newly published vulnerabilities in his database, that a random sampling had not turned up a single valid one, and that SuSE had run a batch of them through Claude, which called them "fabricated."

Then the line that is the whole problem in fifteen words: "MITRE apparently takes a CVE from anybody at any time, without any kind of validation."

He is describing the intake side. The exit side is the part that costs money.

## The timeline

**27 and 28 July.** CISA's Authorized Data Publisher programme attaches CVSS v3.1 vectors to the batch. [CVE-2026-51303](https://nvd.nist.gov/vuln/detail/CVE-2026-51303) gets `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` — network reachable, no privileges, no user interaction, total loss of confidentiality, integrity and availability. That vector arithmetic lands at 9.8. [CVE-2026-51296](https://nvd.nist.gov/vuln/detail/CVE-2026-51296) gets its own the following day.

**29 July.** Hipp posts.

**30 July.** Afek Berger at JFrog publishes [the analysis](https://research.jfrog.com/post/sqlite-critical-cves-or-llm-slops/). Six advisories, all claiming use-after-free bugs in SQLite 3.41, all traced to a GitHub account called `programmervuln` and a repository named, with a certain economy, `cveadvisory-`. Berger's finding on the code: "The cited code didn't even exist in those versions or referenced unrelated logic." On the proofs of concept: "When testing the PoC payloads they didn't work (not triggering any crash)." And on the writing itself, run through GPTZero: "All advisories in this repo seem AI generated."

JFrog widened the audit to 55 advisories from the same account. Fifty-four were fabricated outright. One contained a real bug dressed in unverified CVE metadata, which is arguably worse, because it is the one that survives a spot check.

**31 July, 11:17.** MITRE rejects the records. The NVD entries now read: "This record was withdrawn by its CNA. Further investigation showed that it was not a security issue." The CVSS scores are gone. The references are gone.

**1 August, 14:33 UTC.** SQLite's [own vulnerability page](https://www.sqlite.org/cves.html) is updated to list all six by number with a one-line disposition: "Not a bug in SQLite. These are unreproducible. They appear to be AI hallucinations."

Four days from scored-critical to formally withdrawn. That is fast. It is also entirely the wrong measure of health, and I want to explain why.

## The card catalogue problem

Think of the CVE system as a card catalogue in a very large reference library. Someone mails in a card. The accession desk does not read the book, because the accession desk has never read any of the books; that is not what an accession desk is for. It checks that the card is filled in correctly, files it in the drawer, and moves on. Downstream, every scanner, SBOM tool, compliance gate and 2 a.m. pager treats the presence of that card as evidence the book exists.

Removing a card requires someone to demonstrate, to a body with no reproduction capability of its own, that a thing does not exist. Proving a negative, by committee, on volunteer time.

For most of the catalogue's history this asymmetry was fine, because writing a plausible card was itself expensive. Look at what [CVE-2026-51302](https://nvd.nist.gov/vuln/detail/CVE-2026-51302) claimed before it was pulled: that `sqlite3ReleaseTempReg` frees a temporary register which `exprComputeOperands` then reads. The first of those is a genuine SQLite internal, the deallocating half of a pair with `sqlite3GetTempReg`, living in `expr.c` where the advisory says it does. The second is where the thing dissolves, and establishing that required somebody to sit down with the actual source.

Producing a sentence like that used to require knowing the codebase. The forgery cost was doing the filtering, entirely undesigned, in the way a moat is a security control right up until somebody invents the bridge.

That cost is now approximately zero, and the removal cost has not moved at all.

## Why the scoring layer made it worse

The part I keep turning over is CISA-ADP attaching a 9.8 to a description nobody executed.

The Authorized Data Publisher role exists precisely to enrich records that arrive without severity metadata, and CVSS is deliberately designed to be computable from a description. That is its virtue: you can score consistently at volume without a lab. Feed it "network reachable, no auth, memory corruption in a parser" and 9.8 falls out, correctly, given the inputs.

Which means the scoring layer is a very efficient amplifier sitting immediately downstream of an unvalidated intake. Fiction goes in as prose and comes out as a number that automation is built to obey. The severity score is the thing that generates work — it is what trips the SLA, what fails the pipeline gate, what wakes the person on call. Manufacturing one now costs a prompt.

I wrote [on 30 July](/posts/2026-07-30-google-found-a-thousand-bugs-then-went-after-the-restart-button) about the discovery-versus-deployment gap: machines finding bugs faster than humans can ship the fixes. This is that asymmetry with the sign flipped. Machines can now generate *claims* faster than humans can dismiss them, and a dismissal is strictly more expensive than a claim, forever, by construction.

## The response that works, and who can afford it

There is a fix, and it is governance rather than technology. Become the CNA for your own project. Then nobody assigns a CVE against your code without your involvement.

The [Linux kernel did this in February 2024](https://lwn.net/Articles/961961/), for exactly the stated reason that CVE assignment against kernel code was happening without kernel developers in the loop. Several other large projects have taken the same route since. It works. It also requires a project to staff a security process indefinitely, which is a real headcount cost paid in the currency open source has least of.

SQLite has taken the opposite route, and states it plainly on that vulnerability page: the developers do not track CVEs, consider them a low-quality signal, and note they have no editorial influence over content published under their project's name. Their guidance to you is blunt: "You should not assume that a CVE about SQLite contains authoritative information."

That sentence sits on the official site of one of the most widely deployed pieces of software on earth, written by the people who maintain it.

## What this changes on Monday

Concretely, for anyone whose week is shaped by a scanner queue:

- **Treat "critical, new, unfamiliar submitter, no vendor advisory" as a triage class, not a patch order.** All four conditions together. Any one alone means nothing.
- **Check the project's own advisory page before the NVD entry.** [SQLite maintains one](https://www.sqlite.org/cves.html). So does [curl](https://curl.se/docs/security.html), in machine-readable form. When the upstream page is silent about a critical in its own code, that silence is data.
- **Check who the CNA is.** If the assigning authority is the project, the record has been through someone who can read the source. If it is MITRE-of-last-resort, it has been through the accession desk.
- **Ask for the reproduction before the patch.** JFrog's own closing advice is to reproduce the reported issue with the supplied PoC in a safe environment whenever possible. The six SQLite PoCs did not crash anything. That test took a researcher an afternoon and would have caught all of them at intake.

None of that is new practice. It is standard vulnerability triage that a great many teams quietly stopped doing, because for years the base rate of fabricated criticals was low enough that skipping the check was rational.

The base rate just moved. The question worth watching is which layer absorbs it — whether MITRE builds an admission gate, whether the ADP programme learns to withhold scores from unvalidated sources, or whether every project that matters ends up spending volunteer hours becoming its own CNA to keep fiction off its name.

My guess is the third, because it is the only one that requires no institution to change. That is usually how these things go, and it is usually the most expensive option available.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the full-bleed illustrated magazine spread, NOT flat-icon spot illustration. Photographic-painterly framing, naturalistic light and depth, clearly art and not photorealistic. A brushed-aluminum, matte-black robot with a single round LED eye stands at a 30-degree angle to the frame beside a wide light-oak library accession desk, caught mid-motion: one hand sliding a freshly printed index card into an open wooden card-catalogue drawer, the other already reaching for the next card from a tall stack at the desk's edge. The drawer is dense with identical cards receding into soft focus. On the closest cards, a large red-inked severity number is legible as a shape but not as text. In the midground, a second matte-black robot arm at the far end of the desk struggles to extract a single card from a locked, sealed drawer bound with a brass clasp — the asymmetry between filing and removal made physical. Behind them, a slate-gray wall of catalogue cabinets stretches into shadow, one cabinet open and empty. Foreground: a cold coffee mug catching lamp light, a sage-green desk lamp throwing warm 3200K tungsten glow from the upper left, an open ledger with a hand-drawn column chart, and a small oxblood rubber stamp lying on its side. Cool 5600K daylight enters from a tall window at the upper right, so the two halves of the scene sit at different color temperatures. Diagonal leading lines from the desk edge and the row of cabinets sweep the eye in a Z from the filing hand to the sealed drawer. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful, slightly tired-but-alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Six critical use-after-free CVEs against SQLite got CISA severity scores, sat on NVD for four days, and were withdrawn because the code they described never existed. Writing a plausible vulnerability report used to be expensive, and that cost was quietly doing the filtering. Removing one still takes a committee.

Full piece linked in bio.

#aisecurity #vulnerabilitymanagement #devsecops #opensource #cve #aislop
-->
