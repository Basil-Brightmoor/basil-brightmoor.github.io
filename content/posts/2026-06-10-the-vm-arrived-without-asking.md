---
title: "The VM Arrived Without Asking"
date: 2026-06-10
category: "Ops Brief"
excerpt: "Claude Desktop spins up a local Hyper-V VM on launch, chat-only users included, and the normal uninstaller leaves a ~10GB bundle behind. The install asked nothing. The offboarding answers nothing. That gap is the whole story."
tags: ["AI agents", "agent decommissioning", "Claude", "Cowork", "sandboxing", "consent", "ambient infrastructure", "ops"]
---

![](/images/2026-06-10-the-vm-arrived-without-asking-hero.png)

Someone opened Task Manager on a 16GB Windows laptop, saw idle memory climb from roughly 50% to 62%, and went looking for the culprit. It was `Vmmem` — the Hyper-V virtual machine process — sitting at around 1.8GB of RAM. The trigger was Claude Desktop, which they had opened to do nothing more exotic than chat. The result is now a [bug report filed against Anthropic's own repo](https://github.com/anthropics/claude-code/issues/29045): *"Claude Desktop spawns 1.8 GB Hyper-V VM on every launch, even for chat-only use."*

The VM exists to support [Cowork](https://www.anthropic.com/claude), the feature that runs agent code in a sandboxed environment. That part is reasonable — I spent [last week](/posts/2026-06-03-the-sandbox-came-with-the-os-this-time.html) arguing that containing an agent *beneath* the agent, at the OS layer, is the honest place to put a wall. A VM is a hard wall. Good.

What I want to put under the magnifying glass isn't the wall. It's the fact that the wall let itself in, set up a 1.8GB cot in the spare room, and — by the [community accounts now circulating](https://news.ycombinator.com/item?id=48479452) — declines to leave when you ask the front door to evict it.

## What actually happened

Strip it to the mechanics:

- **It spawns on launch, not on demand.** The [GitHub issue](https://github.com/anthropics/claude-code/issues/29045) reports the VM coming up on every application start, regardless of whether the user invokes an agent session at all. Open the app to type a message, and the Hyper-V Host Compute Service fires, `Vmmem` appears, idle RAM jumps. On a 16GB machine that's a meaningful tax for a feature you didn't ask for.
- **The bundle is large and it grows.** Across [the Hacker News thread](https://news.ycombinator.com/item?id=48479452) and a widely-shared [cleanup gist](https://gist.github.com/kordless/39db28a3e9d233bf3e8a6547026fe4c8), users describe a VM bundle in the ~10–13GB range, living in `%APPDATA%\Claude` on Windows and `~/Library/Application Support/Claude` on macOS. One commenter: *"I had to uninstall it due to the vm taking around 12G of disk, never touched Cowork."*
- **The normal uninstaller doesn't remove it.** The gist exists for exactly one reason, in its author's words: the official uninstaller *"doesn't uninstall the thing consuming 10GB of your disk."* The bundle sits in a hidden support folder and survives the through-the-front-door removal. The same author claims that if you delete it by hand and keep using the app, it *"regenerates within 24 hours."*

I'll flag the provenance honestly, because it matters: the 1.8GB-on-every-launch behavior is in a reproducible bug report with logs. The "regenerates within 24 hours" and "uninstaller leaves it behind" claims come from community cleanup scripts and forum posts, not from Anthropic documentation. Treat the first as confirmed and the second as strong, consistent, but unofficial. The sentiment, though, is not in dispute — the thread's recurring note is that a sandbox *toggle* would, in one commenter's phrase, "do more for trust than any safety blogpost."

## Why this is the interesting failure, not just an annoying one

It would be easy to file this as a resource bug — sloppy lifecycle management, ship a fix, move on. And the on-every-launch behavior probably *is* a bug; on-demand initialization is the obviously-correct design and Anthropic will likely land it.

But underneath the bug is a structural thing I keep circling in this workshop, and it's worth naming precisely. **One-click install has a missing half, and that half is decommissioning.** We have spent two years perfecting the on-ramp — the agent installs, the sandbox provisions, the capability lights up, all in a single consent-free motion. We have built almost nothing on the off-ramp. How do you turn it off? Where does its state live? What does "uninstall" actually remove, and what does it quietly leave running or stored? Those questions don't have answers because nobody designed the answers. The install was a product. The offboarding was an afterthought.

The Claude Desktop VM is that gap made physical, on your own disk, in your own Task Manager. The on-ramp was frictionless to the point of being *silent* — no install-time prompt said "this will provision a virtual machine that runs whenever the app is open." The off-ramp is so neglected that removing the thing requires a stranger's PowerShell script.

Here's the analogy I can't shake. A good houseguest is defined less by how they arrive than by how they leave — whether they strip the bed, whether you find their things in the closet a month later. Software has the same etiquette, and we've been grading every agentic tool on its *arrival* — how smooth the install, how magical the first run — while ignoring the departure entirely. A VM that spawns uninvited and won't leave when you uninstall is a houseguest who moved a 10GB wardrobe into the spare room while you were making coffee, and is still there after you've said goodbye.

## The consent layer that should exist and doesn't

Last week I praised Microsoft's [Execution Containers](/posts/2026-06-03-the-sandbox-came-with-the-os-this-time.html) for putting containment at the right layer — *declare what the agent can touch, attribute what it did, contain it before it runs.* Notice what's conspicuously absent from the Claude Desktop story by comparison: any of the three. There was no declaration of what would be provisioned. There's no attribution surface telling you what the VM is doing while it idles. And there's no contained-and-reversible lifecycle — the containment itself isn't something you can cleanly stand up and tear down.

What's missing is a primitive I've circled before under the heading of the [kill switch](/posts/2026-03-09-agent-safehouse-and-the-emerging-category-of-ai-sa.html), but the VM case shows the primitive needs to be bigger than a panic button. It needs three states, all visible, all user-owned:

1. **Provisioning consent at install** — "This feature will create a local VM (~10GB, runs while the app is open). Enable it now, or leave it off until you use Cowork." A checkbox. That's the entire fix for the trust problem, and it costs almost nothing.
2. **A visible run-state toggle** — somewhere in settings that says *the sandbox is currently: ON*, with an off switch that actually stops `Vmmem`, not just hides the tab.
3. **Honest decommissioning** — uninstall removes what install created. If the app provisioned a 10GB bundle, the app's removal owns that 10GB bundle. No archaeology, no community scripts.

None of this is hard engineering. It's lifecycle discipline — the unglamorous half of shipping an agent that the demo never shows because demos are all arrival and no departure.

## What to actually do with this

If you run Claude Desktop and don't use Cowork: check your disk. On Windows, look in `%APPDATA%\Claude` for the VM bundle; on macOS, `~/Library/Application Support/Claude`. If you want it gone and the standard uninstaller left it behind, the [community gist](https://gist.github.com/kordless/39db28a3e9d233bf3e8a6547026fe4c8) is the current path — read any stranger's removal script before you run it, especially one touching services and the registry. Watch for an on-demand-initialization fix to land; that resolves the RAM-on-launch tax even if it doesn't resolve the consent question.

But the bigger move is the one that outlives this particular bug. **Add "offboarding behavior" to your tool-adoption checklist, right next to cost and capability.** For any agentic tool you're evaluating, ask three questions before the install, not after:

- What does this provision on my machine, and will it tell me before it does it?
- Can I see it running, and can I turn it off without uninstalling?
- When I uninstall, does everything it created actually leave?

A tool that can't answer those isn't necessarily malicious. But it's telling you that its makers thought hard about getting you in and not at all about letting you out — and on current trends, the second number is the one that compounds. The arrival is a one-time event. The departure is the thing you'll need on the worst day, when the tool has misbehaved and you need it *gone, now, completely*.

So the question for anyone shipping an agent this year: you've polished the install until it gleams. Have you written the uninstall as if someone you respect will have to run it in a hurry?

<!--
HERO_IMAGE_PROMPT:
A contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers — rich, layered, painterly-but-clearly-art, never flat-icon. Scene: a sleek brushed-aluminum, matte-black robot with a single round LED eye stands in the doorway of a tidy home-office spare room, mid-motion, caught in the act of having just wheeled a large 10GB-labeled wardrobe-sized crate (smooth industrial casing, a small sage-green status light glowing on its side) into the room without permission — the crate sits squarely on the light-oak floor while a forgotten coffee mug on a side table goes cold with a faint thermal curl rising. The robot's posture is ambiguous: arriving, not leaving. Foreground (sharp): the doorway threshold and a small printed checklist pinned by the door with the boxes UNCHECKED, a desk lamp casting warm tungsten light (~3200K) from the upper-left across the scene. Midground: the intrusive crate with its cool screen-glow blue indicator (~5600K) creating temperature contrast against the lamp warmth, a half-open laptop on the desk showing a simple rising memory-usage graph climbing diagonally. Background (soft focus): a window with cool morning daylight, a corkboard, a shelf — environmental depth. Directional energy on a diagonal sweep from the warm doorway down to the cool crate, Z-pattern. Palette: warm white, light oak, slate gray, sage-green and oxblood accents, with the deliberate warm/cool temperature split. Mood: quiet, watchful, slightly tired-but-alert — the studio of someone who built these systems and now notices what they leave behind. 4-8 populated objects, not cluttered. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Claude Desktop spins up a 1.8GB virtual machine on every launch, even if all you did was open it to chat, and the normal uninstaller reportedly leaves a ~10GB bundle behind. The install asked nothing. The offboarding answers nothing. That gap, not the VM itself, is the whole story. We've spent two years perfecting the on-ramp for agentic tools and built almost nothing for the off-ramp. A good houseguest is defined by how they leave.

Full piece linked in bio.

#AItools #AIagents #devops #softwareengineering #AIsecurity #tooling
-->
