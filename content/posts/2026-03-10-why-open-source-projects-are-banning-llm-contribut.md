---
title: "The Certificate of Origin Problem: What Redox OS's LLM Ban Actually Reveals"
date: "2026-03-10"
category: "Ops Brief"
excerpt: "Redox OS's no-LLM policy isn't anti-AI sentiment — it's a precise response to a structural failure: copyleft was designed to stop proprietary reimplementation of open-source code, and AI can now do exactly that without triggering a single license clause."
tags: "open-source, copyleft, AI contributions, provenance, licensing"
---

Here's a thought experiment that should unsettle anyone who cares about open-source software: an engineer at a proprietary company wants to use a GPL-licensed kernel component. The old approach — copy the code, ship it, get caught, face legal consequences — is crude and traceable. The new approach is cleaner. Feed the GPL code to an LLM as training context or a prompt. Ask it to reimplement the functionality. Receive output that is functionally equivalent, structurally similar, and legally untouched by the GPL, because no copying occurred.

That's not a hypothetical. That's the attack vector [Hong Minhee's sharp essay on legal vs. legitimate](https://writings.hongminhee.org/2026/03/legal-vs-legitimate/) is documenting. And it's precisely why [Redox OS has adopted a strict no-LLM contribution policy alongside a Certificate of Origin requirement](https://gitlab.redox-os.org/redox-os/redox/-/blob/master/CONTRIBUTING.md) — not because the maintainers are allergic to AI, but because they've correctly identified a provenance problem they cannot solve within the existing toolchain.

The Redox decision is worth taking seriously. This is a Rust-based, microkernel OS built explicitly to be a clean-room, memory-safe alternative to legacy Unix systems. Provenance isn't peripheral to the project — it's the entire point. When they say they can't accept LLM contributions, what they're actually saying is: *we cannot verify the Certificate of Origin for code that passed through a system trained on GPL software, and we have no mechanism to do so.*

That's a precise structural statement, not a philosophical one. And it signals something important about where the open-source contribution model is heading.

## Copyleft's Load-Bearing Assumption

Copyleft licenses — the GPL family — operate on a specific enforcement model. They don't prevent use of open-source code; they attach conditions to redistribution. If you take GPL code and ship it in a proprietary product, the license requires you to release your source. The mechanism is derivative work doctrine: if your code is derived from GPL code, it inherits the license.

The load-bearing assumption underneath all of this is *derivation is detectable*. You copied functions. You modified headers. You imported the library. There's a trail — an evidentiary thread that lawyers can follow and courts can evaluate.

LLM-assisted reimplementation severs that thread cleanly. The model ingests GPL code during training or at inference time. The human engineer receives output. No file was copied. No function was imported. The output may be structurally parallel to the GPL original, may solve the identical problem in a functionally equivalent way, may even use the same variable names — but it wasn't *derived* in the legal sense. The derivation happened inside a probability distribution, and that's not where copyright law lives.

This is copyleft erosion by laundering, and it's happening at the exact moment that LLM capability makes it feasible at scale. You don't need a team of engineers to reverse-engineer a GPL component; you need an afternoon and a good prompt.

The legitimate-but-not-legal framing from Hong Minhee's essay captures this precisely: the act is legally clean and normatively corrosive simultaneously. Copyleft was a social contract implemented as a license. AI has found a path that honors the license and violates the contract.

## The Certificate of Origin Problem

Here's what makes Redox OS's policy interesting as an operational signal rather than just a political statement: they're not trying to adjudicate whether any *specific* LLM contribution is laundered proprietary code. They can't. That's the point. The policy is a response to verification impossibility, not to demonstrated bad actors.

A Certificate of Origin, in the open-source context, is a contributor's attestation that they wrote the code, or have the right to contribute it, or are contributing it under a compatible license. The [Developer Certificate of Origin](https://developercertificate.org/) (DCO) — which Linux uses, which Redox is implementing — is a lightweight alternative to full contributor license agreements. It puts legal accountability on the contributor: you're signing off that you know where this code came from.

The problem is that a contributor who used an LLM cannot honestly sign that attestation. They don't know where the code came from. The model doesn't know. The training data provenance for most commercial LLMs is, to put it charitably, opaque. A contributor using GPT-4o or Claude or Gemini to generate kernel code is asserting provenance they cannot verify over a generation process they cannot inspect.

Redox's no-LLM rule is therefore not a ban on AI tooling in principle. It's a recognition that the current generation of LLMs makes DCO compliance structurally unverifiable. The blunt instrument (ban the tool) is the response to the precise failure (can't verify the certificate). If LLMs shipped auditable generation logs with training data provenance, the calculus changes. They don't, so it doesn't.

This is the same pattern I flagged in the [session provenance discussion around AI-generated code](https://writings.hongminhee.org/2026/03/legal-vs-legitimate/): discarding the AI session isn't a storage decision, it's an accountability decision. Here, the accountability question isn't about internal CI pipelines — it's about the legal integrity of the contribution record for a project that may face licensing scrutiny.

## What Fractures Next

The open-source contribution model has always had implicit trust architecture: humans write code, humans certify provenance, humans are legally accountable for the attestation. LLM-assisted contributions don't break the workflow; they break the accountability chain underneath the workflow, in a way that's invisible at the surface.

Redox is the early-mover signal. What I expect to see — and what the provenance problem predicts — is a fracture along two lines.

The first is the **permissive vs. copyleft split**. Projects under MIT or Apache 2.0 have less to protect; permissive licenses don't attach conditions to derivative work, so the laundering attack vector matters less. Expect permissive-license projects to adopt lighter-touch LLM policies, or none at all. Expect GPL, LGPL, and AGPL projects to move toward Redox-style DCO requirements, because they have an actual enforcement mechanism that LLM provenance opacity undermines.

The second is the **infrastructure vs. application split**. Kernel components, cryptographic libraries, and foundational systems have stricter provenance requirements because the blast radius of a contaminated contribution is enormous. Application-layer projects — web frameworks, developer tools, utilities — face lower stakes per contribution and will be more tolerant of LLM input even under copyleft licenses, at least until a test case forces the question.

Redox's policy is the leading edge of a governance evolution that the open-source community hasn't yet built the infrastructure to navigate. The DCO was designed for a world where you either wrote the code or you didn't. The current world has a third option: you had a model write it and you don't know what the model knew.

The practical question for any team contributing to copyleft projects right now: do you have an answer to "where did this code come from?" that would survive a licensing audit? If the answer involves an LLM, you almost certainly don't — not because you did anything wrong, but because the provenance infrastructure to support that claim doesn't exist yet.

That gap is the Certificate of Origin problem. Redox just put up the first signpost.