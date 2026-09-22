---
title: "The Field They Were Missing Carried No Information and the Fields They Wrote Were Discarded"
date: 2026-09-22
category: Ops Brief
excerpt: A census of 68,072 agent plugin bundles found 6.2 per cent validate against the standard, and 96.6 per cent would load after adding one boilerplate field. The gap is a scoring artifact. The real finding is the 40.2 per cent whose authors wrote declarations the specification instructs the client to throw away.
tags: [ai tooling, agents, standards, plugins, mcp, interoperability, observability]
---

![](/images/2026-09-22-the-field-they-were-missing-carried-no-information-and-the-fields-they-wrote-were-discarded-hero.png)

When a conformance rate comes in at 6.2 per cent, the reflex is to write about an industry that will not follow its own rules. Resist it for about ninety seconds, because a paper posted to arXiv on 20 September contains the number that makes the first one meaningless, and then a third number that nobody is going to quote.

[Packaged, But Not Portable](https://arxiv.org/abs/2609.23809), by Tezan Sahu, asks the two questions a practitioner would actually ask about the [Agent Plugins specification](https://agent-plugins.org/specification) that landed on 24 July 2026. Is anyone adopting it, and if a plugin did conform, would that make it work alongside the other plugins a user already has installed?

To answer the first he built AgentPluginZoo: 68,072 plugin bundles across 30,655 repositories, released with its discovery ledger, its scoring code, and its analysis. That last clause is not a formality. A conformance census is an instrument, and an instrument whose scoring rules are not published produces a number you cannot argue with. This one you can.

## Two numbers, one corpus, and the distance between them is a schema identifier

Only 6.2 per cent validate. And 96.6 per cent would load after adding one missing boilerplate field.

Same corpus. Same bundles. Nothing changed between the two measurements except the strictness of the check. So before anything else, notice what kind of quantity a conformance rate actually is. It belongs to the validator. Its value is set by which of the required fields you decide to insist on, which makes it a description of your scoring rule that happens to be reported in units of other people's software. Two honest people can publish 6.2 and 96.6 about the same 68,072 things and both be correct.

Now go and look at what the missing field is, because [the specification](https://github.com/agentplugins/agent-plugins-spec/blob/main/spec/1.0.0.md) makes this short work. Section 5.3 requires exactly two fields in `plugin.json`. One is `name`. The other is `$schema`, a canonical identifier pointing at the manifest schema.

Every plugin ever packaged has a name. So the ninety-point gap between "does not conform" and "would load" is, to a very close approximation, a pointer to the document that describes the file you are already reading. It carries no information about the plugin. It tells a client nothing it could not have assumed. It is the standards equivalent of a form that will not process until you have written your own address in the corner of an envelope you handed over in person.

I want to be clear that I am not mocking the field. Explicit schema identification is good practice and costs nothing to add. The point is about what the resulting statistic can support. If you read "6.2 per cent conformance" and concluded that the plugin ecosystem is structurally incompatible with the standard, the corpus says the opposite: it is almost entirely compatible and almost entirely unstamped.

## The number that describes actual behaviour

Here is the third figure, and it is the one worth your morning.

40.2 per cent of bundles would load while the specification obliges the client to discard fields their authors wrote, and Sahu notes these are mostly declarations of what the plugin ships.

That obligation is not an inference. Section 5.2 of the spec says clients "MUST report and ignore each unknown field and MUST continue loading the plugin if the manifest otherwise satisfies this section," and adds that clients "MUST NOT assign semantics to unknown fields." It is a deliberate and defensible design choice. Unknown-field tolerance is how a format survives version skew instead of shattering on it.

But watch what it produces in combination with the scope of v1.0.0. The specification defines exactly two component types: skills, discovered under `skills/` as directories containing a `SKILL.md`, and MCP servers, described in `mcp.json` across the `stdio`, `streamable-http` and `sse` transports. Sahu's own opening sentence describes what plugin authors are actually shipping: skills, sub-agents, commands, hooks, and tool servers.

Three of those five have no home in the manifest. So authors write the declaration anyway, in a field of their own invention, and the standard instructs every conforming client to read it, refuse to interpret it, and move on. Two out of every five bundles are in that state right now.

The measurement most people will cite describes a stamp. The measurement that describes a behaviour, a client silently dropping an author's statement of what is inside the box, is sitting right beside it at 40.2 per cent and will be the one that gets skipped.

## Nobody is watching the one report the spec already requires

And now the part that genuinely delighted me, in the way that only a badly-routed obligation can.

The specification does not say clients may ignore unknown fields. It says clients MUST **report** and ignore them. The reporting duty is already mandatory, already written down, already in force on every conforming client, and it fires on 40.2 per cent of the corpus.

Ask yourself where that report goes.

In practice it goes to a debug log nobody reads, or to a stream nobody has plumbed anywhere, or, most likely, to a code path that was never implemented because the loading behaviour it accompanies is the one the client cared about. The obligation was written for a reader who does not exist.

Sahu's closing recommendation is that "conformance must be made observable before it can become common," and I would sharpen it by one turn: a large part of the observability is already specified. It has been specified since July. It has no destination.

This is a shape I keep running into from different directions. A scanner that reports a flag and never its sensitivity. A vendor tracker that records that a report was accepted and never that the exploit was re-run. An agent that files a final report with no coverage denominator. In each case the missing artifact is cheap, and in each case it is available at the exact moment the system declines to record it. The unknown-field report is a purer version of the same defect, because here the artifact is not merely cheap, it is already required.

## The question conformance cannot answer

The second half of the paper is the part that should reset how you think about the standard, and it comes down to one figure: 81 per cent of capability-exporting bundles share a name with another plugin, with no namespace or precedence rule to decide which one answers.

Sit with that. A user installs two plugins. Both export a capability under the same name. Both are perfectly conformant. The specification, having successfully standardised the shape of the package, has nothing at all to say about which of them wins.

Reverse-domain namespacing does appear in v1.0.0, under section 8, but it governs *client-specific* extension data, keeping Client A's private manifest keys from colliding with Client B's. The collision the user actually hits, between two plugins competing to answer the same capability name, falls outside it.

Sahu names four concepts the format is missing: qualified capability identity, a declared capability surface, a precedence rule, and inter-plugin relations. He argues they fit an additive v1.1 profile of the same specification rather than a rival standard, which strikes me as exactly right and unusually disciplined. The temptation when you find a hole in a standard is to propose a better standard. The useful move is a profile that a conforming client can ignore and a sophisticated one can honour.

His framing of the underlying error is the sentence I will be repeating: the community standardised a packaging format when composition needs a model. Packaging is a property of one artifact in isolation. Composition is a property of a set. No amount of rigour about the first produces the second, which is why a bundle can be 100 per cent conformant and still be a coin-flip at install time.

## What to do with this before lunch

**If you maintain a plugin.** Add `$schema`. It takes a minute and moves you from the 6.2 to the 96.6. Then go and look at whatever you declared outside the two sanctioned component types, because the standard currently guarantees a conforming client will not read it, and you should know which of your declarations are decorative.

**If you build a client that loads plugins.** You already owe the user the unknown-field report. Route it somewhere a person can see, ideally at install time rather than in a log, phrased as what it is: this plugin told us something we are not allowed to interpret. On this corpus that surfaces on two bundles in five, which makes it a real feature rather than an edge case.

**If you run an agent platform with a marketplace.** The 81 per cent figure is your install-time collision risk, and it is not fixed by raising your conformance bar. Decide your precedence rule now and publish it, because the specification has deliberately left it to you and your users will discover your answer by being surprised by it.

**If you were about to quote 6.2 per cent in a slide deck.** Quote 40.2 instead. It is the one that describes what the software does.

The best standards work of the next year is probably not going to be new specifications. It is going to be making the obligations in the existing ones produce an artifact somebody reads. What would your plugin loader tell you, if you asked it what it threw away this morning?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, NOT flat-icon style. Photographic-painterly framing with naturalistic light and depth, clearly art rather than photorealistic. A brushed-aluminum, matte-black robot with a single round LED eye stands at a 30-degree angle to the frame at a light-oak workshop bench, caught mid-motion between two actions: one hand presses a small round rubber stamp onto the lid of a plain shipping crate, while the other hand is already lifting the lid of the next crate in a diagonal row receding into soft focus. Out of the opened crate, several handwritten paper labels are drifting loose into the air and falling toward a wire basket at the bench's edge, unread, while the stamped lid beside it sits closed and approved. Two further crates further back carry identical stamps and identical loose labels spilling from their seams, so three stages of the same process are visible at once. Two crates in the midground are stencilled with matching blank sage-green circular marks that are indistinguishable from each other, hinting at a collision with no way to tell them apart. Warm tungsten lamp light around 3200K comes from the upper left, throwing long diagonal shadows across the bench; cool 5600K monitor glow from the right edge shows a clean grid of green rows, oblivious to the falling labels. Populate the scene with a coffee mug catching the lamp light, an open notebook showing a hand-drawn schematic of a box with three unlabelled compartments, a small potted plant, a second dimmer screen deep in the background, and cables running diagonally off-frame creating Z-pattern leading lines. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. Mood sharp, deliberate, quiet, watchful, slightly tired but alert. Foreground, midground and background all carry visual interest. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A census of 68,072 agent plugin bundles found 6.2 per cent validate against the new standard. Also that 96.6 per cent would load after adding one boilerplate field, which turns out to be a pointer to the schema describing the file you are already reading. So the scary number measures a stamp. The number worth your morning is 40.2 per cent: bundles whose authors declared what the plugin ships in a field the specification instructs every conforming client to read, refuse to interpret, and discard. The spec already requires the client to report that. Nobody has plumbed the report anywhere.

Full piece linked in bio.

#aiagents #aitooling #mcp #devtools #standards #llmops
-->
