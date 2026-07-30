---
title: "Google Found a Thousand Bugs, Then Went After the Restart Button"
date: 2026-07-30
category: Ops Brief
excerpt: "Google fixed 1,072 security bugs across two Chrome milestones, more than the previous 23 combined. The more interesting half of the announcement is about how long your browser sits open after the fix is ready."
tags: ["Chrome", "Google", "AI vulnerability discovery", "patch management", "Chromium", "Electron", "defender-side AI", "operations", "tooling scout"]
---

![](/images/2026-07-30-google-found-a-thousand-bugs-then-went-after-the-restart-button-hero.png)

Everyone is going to quote the big number, so let me put it up front and then hand you a different sentence from the same document.

The big number: in Chrome 149 and 150, both shipped in June, Google's security team [fixed 1,072 security bugs](https://blog.google/security/chrome-stronger-with-every-update/) — more, by their own accounting, than the total fixed across the prior 23 milestones combined. [TechCrunch's read](https://techcrunch.com/2026/07/30/google-says-it-fixed-more-chrome-bugs-in-june-than-over-the-past-two-years-thanks-to-ai/) is that two months of Chrome outpaced the preceding two years. Doug Turner, Chrome's engineering director, gives it the expected framing: by applying models like Gemini, they are preemptively fixing vulnerabilities and outpacing adversaries.

Now the other sentence, further down the same post, which nobody put in a headline. Google observe that the time spent waiting for the user to restart Chrome is a significant contributor to N-day exploitation risk.

That is a vendor saying, in public, that their own patch is not the safety event. Your restart is.

## What actually shipped

Two things landed together, and they belong to different halves of the problem.

The discovery half is the harness. In early 2026 the Chrome team built an agent harness using Gemini to hunt vulnerabilities across the wider Chrome codebase, developed alongside Google DeepMind and Project Zero and their existing [BigSleep and CodeMender](https://blog.google/security/chrome-stronger-with-every-update/) work. It runs inside continuous integration, every 24 hours, across all changelists. In May alone that pipeline blocked over 20 vulnerabilities from ever reaching production, including one rated critical.

One of its finds deserves a moment: a sandbox escape that let a compromised renderer trick the browser into reading local files, sitting quietly in the codebase for more than thirteen years. Thirteen years of code review, fuzzing, a bug bounty programme with a global audience of very motivated people, and one of the best-resourced security teams in the industry. The bug survived all of it and did not survive an agent reading the code every day.

The delivery half is the part I did not expect. Google are piloting a shift to **two security releases per week**. They are building something called dynamic patching, which uses Chrome's multi-process architecture to sequentially replace background child processes — the renderer, the GPU process — with updated binaries on the fly, removing the need for a full browser restart in most cases. On macOS, Chrome 150 will restart itself when an update is pending and no windows are open, then restore the session. All of it aimed at one variable: the gap between a fix existing and a fix executing on your machine.

## Grant it its due

I want to be plain that this is the good outcome, because I have been circling this beat since spring and it would be cheap to turn a genuine win into a complaint.

In May I wrote about [MDASH finding sixteen](/posts/2026-05-14-mdash-finds-sixteen) of the bugs in a Microsoft Patch Tuesday, and called it the moment defender-side AI stopped being a thesis and became a line item. In July I wrote about [Microsoft's record 570-patch release](/posts/2026-07-15-the-machine-found-the-bugs-and-the-patch-pipe-is-still-human) and argued the constraint had moved downstream, from finding bugs to deploying fixes. Google's post is the second vendor data point on that curve, and it is roughly twice the size of the first.

The open question at the time was whether other vendors would show the same inflation, or whether Microsoft was an outlier with an unusually old codebase. Answered. Chromium is a modern, aggressively fuzzed, continuously reviewed codebase with a mature bounty programme, and it turned out to be holding a thirteen-year-old sandbox escape. If Chromium has this much dormant surface, your dependencies do too. Nobody is going to find yours on a 24-hour cadence.

Google also do something in this post I would like to see become standard. They state that every security bug reaching Chrome Stable is documented and disclosed publicly, regardless of whether it was found internally or reported from outside. That commitment is why 1,072 is a figure you can go and check, and it is the reason this post can be written at all.

## The recall-completion problem

Here is the shape of the thing, borrowed from an industry that worked it out decades ago.

When a car manufacturer finds a defect, the discovery is not the safety event. The regulator does not congratulate them on the number of defects identified. The metric that matters, the one that gets reported and audited and occasionally litigated, is the **completion rate**: what percentage of affected vehicles actually came into a garage and had the part replaced. A recall with a 40% completion rate has left most of the danger on the road, no matter how good the engineering that found it.

Software has spent its entire history reporting the discovery number and treating the completion rate as somebody else's business. CVE counts, patch counts, "we fixed a record number of flaws" — all discovery. All vanity, in the strict sense that they measure the vendor's activity rather than the customer's exposure.

Google's post is the first one I have read from a major vendor that puts real engineering budget against the completion rate and says out loud why. Two releases a week shortens the interval between fix and availability. Dynamic patching and the macOS auto-restart shorten the interval between availability and execution. Neither of those makes Chrome better at finding bugs. Both of them reduce the window in which a published fix is a public exploitation recipe that your browser has not yet taken.

Because that is what a security release is, once you look at it from the attacker's side of the glass. The moment the fix is published, the diff is a map. AI-assisted patch diffing has been compressing that reconnaissance from days to hours all year. The vendor's discovery pipeline running at machine speed and the vendor's delivery pipeline running at "whenever the user closes their tabs" is an asymmetry with a fairly obvious beneficiary.

## Who owns your last mile

This is the part to take back to your own stack, and it is not really about browsers.

Chrome is the best case in the industry. Google own the discovery, the fix, the build, the release channel, the update mechanism, and now increasingly the restart. Fix to running, end to end, on infrastructure they control. When that vendor produces a thousand-bug quarter, it is a non-event for you.

Everything downstream of Chromium inherits the fixes on somebody else's clock. Edge, Brave, Vivaldi and Opera each rebase on their own cadence. Embedded WebViews follow the platform. And [Electron](https://www.electronjs.org/docs/latest/tutorial/electron-timelines) — which is to say a large fraction of the desktop applications your team has open right now — ships major versions roughly every eight weeks tracking alternate Chromium milestones, and supports the latest three majors, with the oldest of those on security fixes only. Then the application vendor decides when to adopt the new Electron. Then your users decide when to take the application update.

Same 1,072 bugs. Four sequential decisions between the fix and the machine, none of them made by Google, most of them made by people who have no idea the clock started.

So the audit is a short one, and I would run it this week:

- **List the things that execute untrusted content.** Browsers, chat clients, editors with plugin ecosystems, anything embedding a WebView, anything that renders a document someone else authored.
- **For each one, name who decides when a published fix starts running.** The vendor, your IT team, or the individual user. If the answer is "the individual user," write that down in a different colour.
- **Estimate the median gap** between a fix being published upstream and running on your fleet. Not the SLA. The actual observed number, which for anything gated on a person closing an application is probably far worse than anybody's dashboard suggests.

That third figure is your real exposure, and it is the one that changed this month. The bug count did not make you less safe. The bug count is the vendor doing their job unusually well. What changed is that the rate at which exploitable diffs get published upstream has gone up by a large multiple, and every extra day in your last mile now costs more than it did in May.

## Who this is for, and who it isn't

If you run a managed fleet with enforced browser updates and a real software inventory, this is a good news story and a small tuning exercise. Shorten your update-enforcement window, and check that your policy contemplates two security releases a week rather than one every four weeks.

If you ship an Electron or CEF application, this is your problem now in a way it was not in April. Your Chromium rebase cadence is a security control, and it is being measured against a supplier who just started shipping twice a week. Worth putting a number on how far behind you currently run.

If you are an individual or a very small team with no fleet management, the entire mitigation is: restart your browser. Today, and then more often than feels necessary. It is the single highest-return security action available to you and it takes four seconds. Google are quietly automating it because they have concluded that asking does not work.

## The takeaway

Write down the discovery number if you like. Then write down, next to it, the number of hours between a fix being published for each critical piece of your stack and that fix actually executing. The first number is the vendor's. The second one is yours, and only the second one appears in an incident report.

The question I will be watching through the autumn: whether any other vendor starts publishing a completion metric alongside the discovery metric. Time-to-running, patch adoption curves, the percentage of installed base on a fixed version thirty days out. Google have now made the argument for why that figure matters, using their own product as the exhibit. It would be a genuinely useful thing to be able to ask a supplier for, and at the moment there is nowhere on a procurement form to put it.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, NOT flat-icon style. A light-oak workbench runs on a strong diagonal from lower-left to upper-right. Foreground right: a sleek brushed-aluminum and matte-black robot with a single round sage-green LED eye, seen three-quarters from behind, caught mid-motion between two actions — one hand setting down a freshly finished small repaired component onto the bench, the other already reaching toward a large matte-black wall switch mounted at the frame's right edge, its sage-green indicator still unlit. Midground: three identical machine housings sit in a receding row, each at a different stage — the nearest open with its repaired part visibly seated and glowing faintly green, the middle one half-closed, the furthest still sealed and dark, the sequence readable as a process partway through. Between them, a small conveyor carries a dense stream of tiny numbered parts arriving far faster than the housings are being closed, several parts spilling into a shallow tray that is overfull. On the desktop: an open notebook with a hand-drawn two-column diagram, a coffee mug gone cold with a faint thermal curl, a stopwatch lying face-up, a pair of calipers at an angle. Background: a window at upper-left throwing warm tungsten light (~3200K) across the near bench; a monitor at the right casting cool blue-white glow (~5600K) onto the robot's shoulder and the wall switch, the two temperatures meeting mid-frame; a corkboard behind with overlapping pinned slips at angles. Palette: warm white, light oak, slate gray, sage-green accents, one oxblood tray. Photographic-painterly framing, naturalistic light and depth, clearly art and never photorealistic. Mood: sharp, deliberate, quiet, watchful, slightly tired but alert — the repairs are done and the switch has not been thrown. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Google fixed 1,072 security bugs across two Chrome releases in June, more than the previous 23 combined. Buried lower in the same announcement: Google say the time you spend not restarting your browser is a significant contributor to exploitation risk. The fix existing and the fix running are two different events, and only one of them shows up in an incident report.

Full piece linked in bio.

#AIsecurity #Chrome #patchmanagement #vulnerabilitymanagement #devops #cybersecurity
-->
