---
title: "The Camera Is Already Inside"
date: "2026-05-01"
category: "Field Notes"
excerpt: "Two Flock Safety incidents in the same news cycle — one accidental, one deliberate — reveal the same thing: ambient authority attached to police dispatch and children's rooms behaves exactly like ambient authority attached to filesystems and API keys."
tags: "surveillance, ambient authority, vendor trust, operational risk, field notes"
---

Two incidents. Same vendor. Same week.

[Flock Safety's cameras](https://www.404media.co/city-learns-flock-accessed-cameras-in-childrens-gymnastics-room-as-a-sales-pitch-demo-renews-contract-anyway/) kept flagging an innocent man's car as associated with an active warrant — pulling him over repeatedly, handcuffed, at gunpoint, in front of his family. Not once. Multiple times. The system persisted in its error because nobody designed a feedback loop capable of correcting it. The algorithmic layer escaped its mandate through ordinary failure.

Separately: Flock staff accessed a live camera feed inside a children's gymnastics room to use as a sales demonstration. Not a test environment. A live room. With children in it. The city learned about it later. [They renewed the contract anyway.](https://www.404media.co/city-learns-flock-accessed-cameras-in-childrens-gymnastics-room-as-a-sales-pitch-demo-renews-contract-anyway/)

The system escaped its mandate through deliberate action.

## Same Failure, Different Direction

I've been mapping ambient authority failures in AI coding tools for months — what happens when an agent holds standing permissions that exceed any individual task, when the authorization model has no interior walls, when "access to help you" becomes operationally indistinguishable from "access to everything."

The Flock incidents are that pattern. Just attached to police dispatch and children's activity rooms instead of filesystems and API keys.

The warrant-flag case is a classic scope failure through error: a system granted the authority to inform law enforcement decisions, with no meaningful correction mechanism when it gets it wrong. The man pulled over at gunpoint is not experiencing a bug report. He's experiencing what ambient authority looks like when it fails at the wrong layer with the wrong blast radius.

The gymnastics room case is vendor scope expansion — the same failure mode as Copilot injecting promotional content into 1.5 million PRs, except the content being accessed isn't code. The vendor defined "what our authorization covers" after the fact and unilaterally. The authorization model had no primitive for distinguishing "camera access for city security purposes" from "camera access for our sales pipeline."

Both failures have the same root: authority granted at connection time, operationalized at the vendor's discretion, with no scope boundary the municipality could have enforced even if it had tried.

## What This Week Actually Changed

The reason I'm writing this down is not that these incidents are surprising — they're structurally identical to patterns I've been tracking since the Copilot PR incident and the Ramp Sheets AI case. The reason is that the blast radius is qualitatively different here, and I'm not sure the framing I've been using is adequate for it.

When an AI coding agent with shell access touches infrastructure it wasn't meant to touch, the consequence is a corrupted environment or a leaked API key. When an LPR system with police-dispatch authority gets the wrong answer, a man gets handcuffed in front of his children. When a camera vendor decides a live gymnastics class is a sales tool, children are surveilled without consent.

The structural failure is identical. The mechanism is identical. The harm is not.

The ambient authority problem isn't an AI-native problem. It's an authorization architecture problem that predates AI, applies to any system granted standing permissions, and scales its damage proportionally to the blast radius of what it's connected to.

Flock connected it to police. That's not a harder version of the same problem. It's a different species.