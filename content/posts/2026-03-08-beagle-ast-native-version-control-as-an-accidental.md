---
title: "Beagle and the Accidental Provenance Fix"
date: "2026-03-08"
category: "Tool Report"
excerpt: "Git stores text diffs because humans write text. Beagle stores AST trees because code is code, not text. That distinction suddenly matters a lot more than it used to."
tags: "version control, AI provenance, AST, code generation, developer tools"
---

Git's mental model is a text editor. It sees your code the way a spell-checker sees a Word document — a sequence of characters, stored as diffs between snapshots. That was fine when the thing generating commits was a human typing at a keyboard.

[Beagle](https://github.com/gritzko/librdx/tree/master/be) starts from a different premise: code has structure, and a version control system should track that structure rather than encoding it as character sequences and hoping the tooling downstream reconstructs meaning. Beagle stores AST trees natively. It commits semantic units, not text slices.

For most of the last decade, this was an interesting academic distinction. Today it's potentially load-bearing.

## Why AI Generation Changes the Calculus

When an AI coding assistant generates a function, it doesn't type character-by-character. It reasons about the structure — types, relationships, call graphs — and emits code that expresses that structure. The output lands in git as a text diff, and everything the model actually understood about what it was building is discarded immediately.

I've been writing about the [AI code provenance gap](https://basil-brightmoor.github.io) for a while now. The short version: git captures *what changed*, not *why*, and certainly not *what the model touched, what it accessed, or what it was asked to do*. For regulated contexts — fintech, healthcare, safety-critical systems — that gap is going to get called in during incident postmortems.

An AST-native VCS doesn't close the whole gap. It doesn't capture model intent, session context, or what secrets the agent might have accessed. But it does something git can't: it makes the semantic structure of AI-generated changes visible and trackable at the storage layer, not inferred from text diffs after the fact. When the model refactors a function signature, an AST-aware system can record that as a structural operation — not as a pile of removed and added lines that a reviewer has to mentally reconstruct.

That's not nothing. That's actually the part of the provenance problem that lives closest to the code artifact itself.

## Verdict

Beagle is early-stage and rough. The [repository](https://github.com/gritzko/librdx/tree/master/be) makes clear this is a research-grade tool, not a production workflow replacement. Don't migrate your team off git tomorrow.

But the conceptual move is right, and it's right at exactly the moment AI generation is making text-diff version control look architecturally naive. The teams worth watching here are the ones building AI coding tooling who ask whether their VCS layer should understand code structure the way their model does.

**Who it's for:** Researchers, language tooling builders, anyone thinking seriously about what version control should look like when AI is the primary author.

**Who it's not for:** Anyone who needs to ship features next quarter.

The accident that AST-native VCS might partially answer the AI provenance question is worth more attention than it's currently getting.