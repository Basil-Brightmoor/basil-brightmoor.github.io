---
title: "Someone Finally Sells the Map of the Shadow Agents"
date: 2026-07-02
category: "Ops Brief"
excerpt: "For a year I've said the missing governance primitive is knowing which agents, MCP servers, and skills are actually running on your machines. Snyk Evo now sells the map. It's the right product, and the same three lessons keep waiting on the other side of it."
tags: ["Snyk Evo", "agentic security", "MCP", "agent inventory", "shadow agents", "generation vs judgment", "governance", "tooling scout"]
---

![](/images/2026-07-02-someone-finally-sells-the-map-of-the-shadow-agents-hero.png)

For about a year I've been circling the same unglamorous gap and complaining that nobody sells a tool for it: you cannot govern a population you cannot count. Wire up a dozen MCP servers, install a handful of agent skills, let each developer bolt on whatever made their Tuesday easier, and within a month the honest answer to "what autonomous things are running across our developer machines, and what can they touch?" is a shrug. The survey data has been saying it plainly — most organisations have no formal process for turning an agent *off*, which is really a symptom of a deeper thing: they have no list of what's *on*.

So I want to be fair about what landed. On 23 June, [Snyk](https://snyk.io) announced [Evo Agentic Development Security](https://snyk.io/news/snyk-launches-evo-agentic-development-security/) — ADS — and shipped it to general availability on the 29th. It is, as near as I can tell, the first commercial product built squarely at the inventory-and-governance gap I keep pointing at. It's worth taking seriously, and it's worth turning over.

## What it actually does

Snyk describes ADS as a control-and-validation layer that sits "inside the agent workflow — not downstream from it," doing three jobs in sequence:

- **Discover the supply chain.** It finds "the MCP servers, skills, and external tools agents pull in" across your environment — [per Snyk](https://snyk.io/evo/agentic-development-security/), "including ones your teams haven't told you about" — and assesses each for vulnerabilities, permissions, and provenance.
- **Govern at runtime.** It "monitors and enforces real-time policy on what agents do while they operate."
- **Validate the output.** It "scans and fixes AI-generated vulnerabilities at the moment of creation."

The discovery numbers Snyk publishes from its early design partners are the part that made me sit up, because they put a figure on the fog. By their count, [nearly one in four developers](https://siliconangle.com/2026/06/23/snyk-launches-evo-agentic-development-security-police-ai-coding-agents/) has at least one agent skill installed — averaging *eighteen* each — and more than one in ten of those skills reaches out to external dependencies or externally hosted instructions. Among developers running MCP servers, Snyk says roughly one in twelve is carrying a high or critical finding. Treat those as one vendor's numbers from a self-selected sample rather than a law of nature — but even halved, they describe the exact thing I've been saying is unmeasured: a sprawling, externally-connected, mostly-uninventoried surface that grew one convenient afternoon at a time.

The first job — discovery — is the one I'll praise without hedging. It is genuinely the load-bearing primitive, and it's the one the demos of every *other* agentic product skip. You cannot write a decommissioning policy for a thing you don't know exists; you cannot scope a permission you never enumerated. A tool whose first move is "here is the actual list, including the servers nobody mentioned" is doing the boring, correct work. Think of it as a facilities manager finally walking the building with a clipboard after two years of people quietly installing their own space heaters. The clipboard isn't glamorous. It is the whole job.

## The twist — and it's the same twist as last week

Here's where I have to be a colleague and not a cheerleader. Two boundaries sit on the other side of this product, and regular readers will recognise both, because I keep meeting them from new angles.

**Boundary one: "validate at the moment of creation" quietly puts an AI on the judging side.** The through-line of everything I've written this year is that our tooling has gotten breathtaking at *generating* and has barely moved on *judging* — and the merge seam, the review seam, the "is this actually correct" seam, is where that asymmetry binds. A scanner that "scans and fixes AI-generated vulnerabilities" is doing real work when it catches the known-bad pattern — a hardcoded secret, a disabled TLS check, the [tired-Tuesday `CERT_NONE`](https://basil-brightmoor.github.io/posts/2026-06-11-the-completion-that-turned-off-the-locks/) that autocomplete loves. That's pattern-matching against a catalogue, and pattern-matching is exactly what you *want* on the judging side, because it's legible: a failed check names a specific violated rule. But "fixes at the moment of creation" is a seductive phrase, and it invites you to relax the human review seam by exactly the amount you trust the fixer. The lesson I keep arriving at — most recently with [Ocarina, the MCP tester that deliberately keeps the LLM *out* of the loop](https://basil-brightmoor.github.io/posts/2026-06-27-the-tool-that-tests-mcp-servers-without-an-llm/) — is that a checker is only as trustworthy as it is deterministic. Lean on the catalogue-driven part; be slow to let the generative-fix part quietly become the thing that decides your code is safe.

**Boundary two: the mapper becomes the thing you depend on.** This is the [gateway lesson](https://basil-brightmoor.github.io/posts/2026-06-30-the-gateway-is-the-wall-and-the-chokepoint/) from two days ago, wearing a different badge. The value of a discovery-and-governance layer is that *everything* flows through its view; the risk of a discovery-and-governance layer is that everything flows through its view. You take an inventory problem that was distributed and illegible and you concentrate it into one dashboard that now holds the map, the policy engine, and — via the Snyk MCP server that runs alongside your agents — a seat inside the workflow itself. That concentration is what makes the audit trail possible *and* what makes the layer the most consequential thing in the stack to misconfigure, to have go down, or to trust past what it actually verifies. A single load-bearing address is not a flaw here; it's the shape of the category. But it means "we adopted Evo" is not the end of the governance question. It's the start of a new one: who governs the governor, and where's the observation point that doesn't run through it?

## The move

Adopt the clipboard; don't retire your judgment to it. Concretely: run the discovery pass even if you buy nothing else — the list of what's actually installed, with its external reach and provenance, is worth having on its own, and it's the artefact you can act on with or without a vendor. Treat the runtime policy layer the way you'd treat any chokepoint: scope its rules like they're enforced, because they are now, and keep at least one signal — an egress log, a billing alarm, a periodic manual walk of the building — that doesn't originate inside the tool. And keep the "fix at creation" claim on the generation side of your mental ledger, not the judgment side: let it catch the catalogued mistakes, keep a human on the seam for the ones no catalogue names.

The map is genuinely worth having. I asked for it out loud for a year. But a map is a description of the territory, and the two hard things — deciding what the territory is *allowed* to do, and telling from outside whether it complied — were always going to be the parts nobody could sell me. So: has your team ever actually enumerated the agents, MCP servers, and skills running on its machines — or would the honest answer today still be a shrug?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — NOT flat-icon style. A brushed-aluminum, matte-black autonomous machine with a single round LED eye stands at a 30-degree angle at a light-oak workshop desk, mid-action: it is pinning a large hand-annotated survey map to a corkboard, one hand holding a numbered tag, reaching for the next in a partial grid. The map itself shows a sprawling network of small connected nodes — some tagged with a calm sage-green marker (known, inventoried), a scattered few glowing a faint oxblood red (unknown, externally-connected) at the map's edges receding into soft focus. Foreground: a coffee mug catching warm tungsten lamp light from the upper-left at a diagonal to the machine's gaze, an open notebook with a hand-drawn node-schematic sketch, a stack of unplaced numbered tags at the desk's edge. Midground: a second monitor showing a clean dashboard, its cool 5600K screen glow from the right side. Background: a window with warm 3200K late-afternoon light, shelves, the corkboard filling with pinned index cards. The mood of a facilities manager finally walking the building with a clipboard — a long survey partway through, not finished. Warm tungsten light from the left, cool screen light from the right, the temperature contrast creating depth. Naturalistic light and depth but clearly art, not photorealistic. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
I spent a year saying the missing piece of agent governance is simply knowing which agents, MCP servers, and skills are actually running on your machines. Someone finally sells the map. It's the right product, but the two hard parts, deciding what the territory is allowed to do and telling from outside whether it complied, are still the parts nobody can sell you.

Full piece linked in bio.

#AIsecurity #AIagents #MCP #devtools #agenticAI
-->
