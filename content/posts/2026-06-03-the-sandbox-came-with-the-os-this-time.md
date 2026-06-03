---
title: "The Sandbox Came With the OS This Time"
date: 2026-06-03
category: "Ops Brief"
excerpt: "Microsoft shipped agent containment as a Windows platform primitive at Build 2026. For two years it was a third-party product category. Now the OS vendor owns the floor the agent runs on, and that changes the audit question."
tags: ["AI agents", "agent containment", "Microsoft", "Windows", "MXC", "sandboxing", "platform dependency", "ops"]
---

![](/images/2026-06-03-the-sandbox-came-with-the-os-this-time-hero.png)

For about two years now, the people thinking hardest about how to keep an AI coding agent from torching a filesystem have been building their containment tools *beside* the operating system, never inside it. [Agent Safehouse](https://github.com/eugene1g/agent-safehouse) is a macOS-native, open-source utility — a single `sandbox-exec` policy wrapper with a deny-first model. The various Docker-wrapper patterns were bolt-ons. The whole "sandbox-first instead of kill-switch-first" design philosophy I keep circling back to has lived as a third-party project category — someone outside the platform deciding the scope problem was unsolved enough, and urgent enough, to build a standalone tool around.

At [Build 2026](https://blogs.windows.com/windowsdeveloper/2026/06/02/build-2026-furthering-windows-as-the-trusted-platform-for-development/) on June 2, Microsoft moved the floor. They announced **Microsoft Execution Containers (MXC)** — described, in their own words, as "a cross-platform, policy-driven execution layer for agents across Windows and WSL." Agent containment is no longer something you buy from a vendor who noticed the gap. It is becoming something the OS ships with.

That is a genuine maturity milestone, and it is worth taking apart carefully — because the thing that makes it good is the same thing that should make you read the fine print.

## What MXC actually is

Strip the keynote gloss off and MXC is a containment spectrum, not a single feature. Microsoft is shipping it as a range of isolation strengths you pick from per agent:

- **Process isolation** — separates the agent's execution from your desktop, clipboard, and input. The agent runs, but it can't reach into the session you're actively using.
- **Session isolation** — binds the agent to a strong user identity, which Microsoft frames as mitigating spoofing and data leakage.
- **Windows 365 for Agents** — the agent runs in a managed Cloud PC, fully separate from your machine. This one is already generally available.
- And on the roadmap: micro-VMs and Linux containers, for teams that want a harder wall than process boundaries provide.

The permission model is the part that matters most. Developers **declare** what an agent can access — files, networking — as policy, configurable through [Intune](https://www.microsoft.com/en-us/security/business/microsoft-intune). Each agent gets either a local or an Entra-backed identity, and "all container activity is attributed accordingly." Process and session isolation land for Windows Insiders shortly after Build.

If you've read this workshop for any length of time, you'll recognize every word of that as the thing I've been arguing the authorization model couldn't express. *Declare what the agent can touch. Attribute what it did. Contain it before it runs, not after it misbehaves.* This is the sandbox-first philosophy, written into the platform by the platform's owner.

Think of it like the difference between a restaurant that keeps a fire extinguisher by the stove and a restaurant whose stove was built with a flame-suppression line plumbed straight into the hood. The first is a reaction bolted onto an existing risk. The second is the risk designed out at the layer where the heat actually lives. MXC is Microsoft plumbing the suppression line into the hood.

## Why this is the right layer

The recurring argument here has been that you can't fix a containment problem at the wrong layer. A kill switch sits *above* the agent — it assumes the agent already had full ambient authority and gives you a button to stop it once you notice. A sandbox sits *beneath* the agent — it decides what the agent can reach before the agent does anything at all.

For invoked coding agents, beneath-the-agent is the honest layer, because the failure modes that actually hurt — symlink escapes, credential reads, a `git` operation that follows a path the model treats as one step and the kernel treats as two — all live in the gap between what the agent intended and what the OS permitted. You cannot patch that gap from above. You can only define it from below.

So Microsoft putting containment in the OS, with a declarative manifest and per-agent identity attribution, is the correct architectural move. The token-mediation detail — agents receive access through identity infrastructure rather than holding raw credentials — is exactly the design that closes the "one OAuth, all keys" failure I keep naming. When the runtime hands out scoped, attributable tokens instead of letting the agent hold the keychain, the blast radius of a compromised agent shrinks from *everything* to *what was declared*.

There is also a quiet second win here: a shared containment layer makes agent behavior *legible*. Windows assigns identity, attributes activity, and routes the lot through [Defender](https://www.microsoft.com/en-us/microsoft-365/windows/microsoft-defender), Entra, Intune, and Purview. For the first time the question "what did this agent actually do last night?" has a place to be answered that isn't the discarded session log.

## The cost buried in the win

Here's where I put the magnifying glass down and pick up the other one.

The whole reason third-party containment tools existed is that they were *independent of the thing they were containing*. Agent Safehouse doesn't care whose model you run inside it. A Docker wrapper is indifferent to your vendor. The containment layer and the agent layer were owned by different parties, and that separation was the property doing the work.

MXC collapses that separation. The containment layer, the identity layer (Entra), the policy layer (Intune), the monitoring layer (Defender, Purview), the agent runtime, the on-device models — [Aion 1.0 Instruct and the 14B Aion 1.0 Plan](https://blogs.windows.com/windowsdeveloper/2026/06/02/build-2026-furthering-windows-as-the-trusted-platform-for-development/) — and increasingly the developer hardware itself are all the same vendor. The sandbox is excellent. It is also a floor owned by the same company that owns everything standing on it.

I've named this before in a different context: when a foundation-model provider acquired a CI substrate, the substrate kept working fine. What changed was subtler. The *independence* of the substrate became contingent on the acquirer. MXC isn't an acquisition, but the shape is identical. Your containment guarantee is now only as durable, and as portable, as your relationship with Windows. Move the agent to a different OS and the manifest, the identity attribution, and the Intune policy don't come with it. The spec is the lock-in — same lesson, new floor.

This is not a reason to refuse it. Process isolation for Windows Insiders is going to prevent real incidents, and "prevents real incidents" beats "preserves theoretical portability" on most days of the week. It *is* a reason to write the dependency down where you can see it.

## The audit move

If you run agents on Windows, the question changes from "what containment tool should I bolt on?" to "what am I now structurally dependent on, and what's my exit?" Two concrete moves:

1. **Treat the MXC manifest as a portable spec, not a Windows config.** Keep your per-agent permission declarations — what files, what network scope — in a form you could re-implement on another containment layer. The day you can't reconstruct your agent's intended scope without the Intune console is the day the lock-in became load-bearing.
2. **Don't let first-party containment retire your independence reflex.** The native monitoring is good. It is also reporting to you about a system the reporter owns end to end. Keep at least one observation point — network-layer egress, ideally — that doesn't run through the same vendor's stack.

The sandbox came with the OS this time. That's the right place for it to live. Just remember whose house it is — and whether you'd know how to leave if you had to.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — full illustrated magazine spread, not flat icon. A sleek brushed-aluminum, matte-black robot with a single round LED eye sits mid-task inside a transparent glass-walled containment chamber on a light-oak desk, its hands reaching toward a control surface but stopping at the inner wall; the chamber is one of three chambers receding diagonally into soft focus, each glowing a slightly different sage-green from its status LED, showing the same robot at three stages of an isolated task. Foreground: a half-open declarative manifest document on the desk, its permission lines faintly visible, a coffee mug catching warm tungsten lamp light from the upper-left at a diagonal to the robot's gaze. Midground: a second monitor showing an attribution log scrolling, cool 5600K screen glow from the right. Background: a window with warm 3200K morning light, a corkboard with pinned policy notes, shelves in soft focus. The glass walls of the chamber catch both the warm and cool light, creating depth. Warm white, light oak, slate gray, sage-green and oxblood accents. Mood: sharp, watchful, deliberate — the studio of someone who built the containment and now studies who owns it. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
For two years, keeping an AI agent from torching your filesystem meant buying a containment tool from someone who noticed the gap. At Build 2026, Microsoft put the sandbox inside Windows itself. That's the right layer for it. It's also a floor owned by the same company that owns everything standing on it.

Full piece linked in bio.

#AItools #AIagents #devops #AIsecurity #automation #Windows
-->
