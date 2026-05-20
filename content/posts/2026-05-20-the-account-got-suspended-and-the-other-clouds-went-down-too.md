---
title: "The Account Got Suspended, and the Other Clouds Went Down Too"
date: "2026-05-20"
category: "Ops Brief"
excerpt: "On May 19, Google Cloud's automated systems suspended Railway's production account with no warning. Railway's API, dashboard, and databases went down — and so did workloads running on Railway Metal and AWS, because the routing tables those edges depend on were hosted in GCP. This is the failure mode multi-cloud was supposed to prevent. The lesson isn't 'don't use one vendor.' It's that a control plane on one vendor makes every data plane that reads from it single-vendor too."
tags: "platform-dependency, blast-radius, infrastructure, railway, gcp, multi-cloud, control-plane, vendor-risk, outage, ops"
---

![](/images/2026-05-20-the-account-got-suspended-and-the-other-clouds-went-down-too-hero.png)

On May 19 at 22:20 UTC, Google Cloud placed Railway's production account into a suspended status. There was no warning. Railway's [incident report](https://blog.railway.com/p/incident-report-may-19-2026-gcp-account-outage) describes it plainly: the suspension was part of an automated action that "extended to many accounts within Google Cloud," and "as this was a platform-wide action, there was no proactive outreach to individual customers prior to the restriction." Within ten minutes, Railway's API was failing health checks, the dashboard was returning 503s, and users could not log in. The full incident ran roughly eight hours.

That part is a familiar shape — a platform-as-a-service has a bad night because its underlying cloud had a bad night. What makes this one worth a full Ops Brief is the next sentence in the report, and it is the sentence I would put on a poster in every infrastructure team's office.

Workloads running on [Railway Metal](https://railway.com) and on AWS — *not* on Google Cloud — also went down.

## The blast radius escaped the suspended account

Here is the mechanism, in Railway's own words: "Railway's edge proxies maintain a cache of routing tables from the network control plane, which is hosted within Google Cloud. While that cache held, workloads on Railway Metal and AWS continued to serve traffic. Once the cache expired, the edge could no longer resolve routes to active instances, and workloads across all regions, including Metal and AWS, began returning 404 errors."

Read that twice. Railway had genuinely diversified its *data plane*. There were workloads running on Railway's own bare metal. There were workloads running on AWS. By every checklist definition of "multi-cloud," Railway had done the work. And all of it went dark anyway, on a roughly 15-to-25-minute delay, because the thing that tells the edge *where the workloads are* — the network control plane — lived entirely inside the account Google suspended. The cache was the only thing holding the lights on, and a cache is a countdown timer, not a fallback.

I want to be precise about what failed here, because the easy lesson ("don't depend on one cloud") is the wrong one and Railway, to their considerable credit, did not draw it. Railway depended on several clouds. What they had not done was make the *control plane* survive the loss of any one of them. And a single-vendor control plane silently converts every multi-vendor data plane into a single-vendor system. The diversification was real and it was also decorative, because the coordination layer above it had no redundancy at all.

## Why this is a different animal from an ordinary outage

I've written a fair amount about platform dependency — access revocation, access-method pricing, the [forge-layer dependency](/posts/2026-05-10-the-self-hosted-question-is-different-now.html) problem where GitHub's coordination layer is a single point of failure distinct from git itself. This incident belongs in that family, but it has two properties that ordinary cloud outages don't.

The first is that **it was not an outage in the technical sense.** Google Cloud's compute didn't fail. Its network didn't fail. A *policy system* fired. An automated account-suspension mechanism — the same general class of system that suspends accounts for billing problems, abuse reports, fraud signals, or terms-of-service flags — categorized Railway's account as one that should be switched off, and switched it off. The infrastructure did exactly what it was told. The instruction was wrong. You cannot SRE your way out of this. There is no amount of redundant compute that survives your account being administratively disabled, because the suspension applies to the account, and the redundant compute is *in* the account.

The second property: **the recovery clock was not yours to control.** Railway filed a P0 ticket at 22:22, two minutes after detection, and had their account manager engaged. GCP access was restored at 22:29 — seven minutes, which is genuinely fast for an account suspension appeal and speaks well of Railway's support relationship. But the *services* did not come back at 22:29. Persistent disks recovered sequentially, finishing at 23:54. Networking came back around 01:30. Edge traffic at 01:38. The dashboard was usable at 02:55. The whole thing closed out near 06:14. Restoring the account was a switch; restoring the *system* was a five-hour cold-start of a large distributed platform that had been hard-stopped mid-flight. The suspension is instantaneous. The recovery is not. That asymmetry is the actual cost structure of this failure mode, and it does not show up anywhere in a "99.9% uptime" SLA.

There's an analogy I keep reaching for. A diversified stock portfolio protects you against any one company failing. It does not protect you against the brokerage freezing your account. Those are different risks, they need different mitigations, and almost everyone who feels "diversified" has only addressed the first one. Railway's data plane was a diversified portfolio. The GCP account was the brokerage.

## What Railway is actually fixing — and why it's the right fix

The remediation section of the report is unusually good, so I want to dwell on it rather than just nod at it.

Railway is not promising to leave Google Cloud. They are doing two specific things. First: "remove the hard dependency on the GCP-hosted control plane API," and "remove Google Cloud services from our data plane's hot path, keeping them only for secondary/failover." Second: extend their high-availability database shards across AWS and Metal so that quorum survives "if one cloud region disappears entirely."

Notice what category of fix that is. It is not "add another vendor." It is "make the coordination layer tolerate the loss of any single vendor, including the one it currently lives on." They are moving the control plane from *hosted on GCP* to *hosted across enough places that no single suspension can take it out.* That is the correct structural response, and it is more expensive and more annoying than data-plane diversification, which is exactly why most teams do the data-plane part and quietly skip this part.

And the accountability line is the one I'd ask you to actually internalize, because it generalizes past Railway: "Your customers don't care whether the failure was Google or Railway; they see your product. Your uptime is our responsibility." A vendor's automated policy system is, from your customer's seat, indistinguishable from your own bug. Dependency does not delegate accountability. It only delegates the *cause*.

## The audit question this leaves on the table

If you operate anything with users, the takeaway is not "Railway did something foolish" — they manifestly did not, and their report is more honest than most. The takeaway is a question to run against your own stack this week, and it is a different question from the ones I've posed before.

Not "what does this tool hold and route?" Not "who owns this tool and what's the governance structure?" The question here is: **which single vendor account, if it were administratively suspended tomorrow with no warning and no technical fault on your part, would take down systems you believe are independent of it?**

Walk it through concretely:

- **Find your control plane.** Not your compute — your *coordination*. Routing tables, service discovery, the database that knows which instance is where, the config store, the DNS authority, the auth issuer. List where each one is hosted. If they cluster in one cloud account, your data-plane diversification is, like Railway's was, partly decorative.
- **Identify your caches as countdown timers.** Railway survived for 15-to-25 minutes on a route cache. That cache bought time; it did not buy independence. For every cache that's keeping you alive when an upstream is gone, ask: when this expires, what happens? A cache is a fallback only if something refills it.
- **Separate "the cloud failed" from "the account was disabled" in your risk model.** Redundant compute addresses the first. Only an account-suspension-survivable control plane addresses the second. Most disaster-recovery plans I've read about address the first and never name the second, because the second feels like someone else's mistake. It is — and it is still your outage.
- **Know your appeal path before you need it.** Railway's seven-minute account restoration was not luck; it was an existing support relationship and a named account manager. If your answer to "what happens when a vendor auto-suspends us" is "open a ticket and hope," you have found a gap. The recovery clock starts the moment you can reach a human who can reverse the policy action — and on a free or low-tier plan, that human may not exist.

The cloud era trained us to think of "the platform" as something that fails the way weather fails — occasionally, impersonally, recoverably. This incident is a reminder that the platform also fails the way a *bureaucracy* fails: a rule fires, a flag is set, and you are switched off by a system that was working perfectly. The fix for weather is redundancy. The fix for bureaucracy is making sure the part of your system that holds everything together is not sitting inside any single jurisdiction that can revoke it. Railway is doing that work now. The honest question is whether you'd have to find out the way they did.

<!--
HERO_IMAGE_PROMPT:
A precisely composed industrial workshop scene. On a long brushed-aluminum workbench, three identical matte-black server-module devices sit in a row, each with a small round LED eye — one LED sage-green and lit, two dark. Above and behind them, a single suspended control panel — the coordination layer — has been switched off, its surface gone dark, a small oxblood-red indicator showing it is disabled. Thin cables run from the dark control panel down to all three server modules, visually showing that all three depend on the one panel above. A faint translucent layer near the lit module shows a cache meter draining, like sand in an hourglass rendered as a glowing bar. The mood is post-shutdown: quiet, deliberate, slightly cold, the moment after the power policy fired. Contemporary editorial illustration in the style of Christoph Niemann or Tom Gauld — clean designed graphics, mid-century-modern sensibility, photographic-painterly framing, clearly art and not photorealistic. Palette: warm white, light oak bench inserts, slate gray, single sage-green accent, single oxblood accent. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->
