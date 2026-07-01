---
title: "The Manifest Got a Landlord Who Isn't a Vendor"
date: 2026-07-01
category: "Deep Bench"
excerpt: "For a year I kept asking whether an agent spec would ever get OCI-style multi-vendor governance instead of belonging to whoever shipped it. The Agentic AI Foundation is the answer arriving: three rival labs handing MCP, goose, and AGENTS.md to the Linux Foundation. Here is what that actually moves, and the thing it conspicuously does not."
tags: ["Agentic AI Foundation", "MCP", "AGENTS.md", "Linux Foundation", "open governance", "spec portability", "agent SDK", "tooling scout"]
---

![](/images/2026-07-01-the-manifest-got-a-landlord-who-isnt-a-vendor-hero.png)

For about a year I have been circling one nagging question from every angle I could find, and I want to say plainly at the top: it just got answered, and the answer is genuinely good.

The question was governance. Every time a new agent format shipped — a manifest for a coding agent, an instruction file, a protocol for wiring tools to models — I would grant it its due and then ask the same unglamorous thing: *who owns the spec?* Not who wrote the runtime, not whose logo is on the launch post, but who governs the format itself. Because the runtimes were converging on the same primitives while the specifications stayed proudly incompatible — Python objects here, hierarchical trees there, YAML manifests somewhere else — and I kept landing on the same conclusion. The spec is the lock-in. The thing you author against is the thing you can't leave without re-authoring, and if the format belongs to one vendor, then "open protocol" is a description of the license, not the power.

I had a name for the moment that would change it: the [OCI](https://opencontainers.org/) moment. Containers went through exactly this. For a while a container was whatever Docker said it was, and then the [Open Container Initiative](https://opencontainers.org/) published an image spec under neutral, multi-vendor stewardship, and suddenly the format outlived any one company's product decisions. I have been openly watching for the equivalent to happen to agents — and specifically watching one signal I called the strongest of all: whether [MCP](https://modelcontextprotocol.io/) would ever move to external governance, because that action, independent of anything anyone said, would tell you whether the intent was insulation or control.

It moved.

## What actually happened

On December 9, 2025, the Linux Foundation [announced the Agentic AI Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) — AAIF — anchored by three donated projects from three companies that compete with each other daily: Anthropic's [Model Context Protocol](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation), Block's [goose](https://block.github.io/goose/), and OpenAI's [AGENTS.md](https://agents.md/). The platinum member list reads like the whole industry standing in one room: Amazon Web Services, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft, and OpenAI.

Read that founding trio again, because the composition is the argument. MCP is the protocol layer — how an agent reaches tools. AGENTS.md is the instruction layer — how you tell an agent what your project expects. goose is a runtime. Three different floors of the stack, three different donors, one neutral roof. This is not one company open-washing its own format; it is rivals agreeing to stop owning the connective tissue individually.

Anthropic was unusually direct about why, and the sentence is worth quoting because it is exactly the property I'd been saying was missing: "Since its inception, we've been committed to ensuring MCP remains open-source, community-driven and vendor-neutral. Today, we further that commitment by donating MCP to the Linux Foundation." The MCP maintainers [added the part that matters most to anyone building on it](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/): "individual projects, such as MCP, maintain full autonomy over their technical direction and day-to-day operations," and "the governance model we introduced earlier this year continues as is." The donation changed the *landlord*, not the *tenants*. The people making protocol decisions are the same people; what changed is that no single vendor can now repossess the building.

And the format that took the widest hold in the meantime is AGENTS.md. By the foundation's own count it is [used by more than 60,000 open-source projects](https://agents.md/) and read natively by two dozen tools — Codex, Cursor, GitHub Copilot's coding agent, Gemini CLI, Devin, Jules, Windsurf, Zed, Aider, VS Code, and more. A single markdown file in your repo root that every major coding agent will read. That is the boring, wonderful shape of a standard actually working: not a press release, a *default*.

## Why this is the good version, not the cynical one

I want to be careful here, because my house style is to grant a thing its due before I turn it over, and this one earns a lot of due.

We have watched the opposite movie several times this year. Apple shipped a genuinely elegant [model-swap abstraction](https://basil-brightmoor.github.io/posts/2026-06-09-apple-made-the-model-a-swap-out.html) and it ran only on Apple's operating systems. Microsoft shipped [OS-level agent containment](https://basil-brightmoor.github.io/posts/2026-06-03-the-sandbox-came-with-the-os-this-time.html) done right — and identity, policy, monitoring, and hardware all belonged to one vendor. AWS shipped the [lifecycle controls I'd said were missing](https://basil-brightmoor.github.io/posts/2026-06-26-aws-sells-the-off-switch-i-said-was-missing.html) and wired the off-switch to its own meter. Each time the pattern was the same: a good abstraction arrives, frees you on one axis, and quietly binds you on another, because the interesting layer ends up owned by whoever shipped it.

The AAIF is the structural inverse of that movie. Here the interesting layer — the protocol, the instruction format — is being *deliberately un-owned*. The whole point of a neutral foundation is that the format's future can't be steered by a single company's roadmap, killed by a single company's pivot, or metered by a single company's billing team. When your MCP integration depends on a protocol governed by the Linux Foundation rather than a protocol owned by the vendor whose model you happen to use this quarter, you have swapped a relational dependency for an institutional one — and institutions with decades of stewardship track record are the more durable bet. This is the thing I have been asking teams to want. It would be perverse to greet its arrival with a shrug.

There's a maturation story riding alongside the governance one, and it's the reason this is timely rather than a six-month-old announcement. MCP is [visibly growing up under the foundation](https://aaif.io/blog/mcp-is-growing-up/): the protocol is going *stateless at the protocol layer* so any server instance can handle any request (goodbye sticky sessions behind a load balancer), application state is moving into explicit visible handles a model can reason about, OAuth semantics are tightening for multi-server deployments, and — the part I like most — there's conformance testing to prevent fragmentation and a feature-lifecycle policy with real deprecation periods. The release candidate is out and the final specification is [expected July 28, 2026](https://aaif.io/blog/mcp-is-growing-up/). That is what governance is *for*: not a logo change, but the unsexy discipline of versioning, deprecation, and conformance that keeps a standard from splintering into forty dialects. A protocol only becomes infrastructure once someone is boring about it on purpose.

## The thing it conspicuously does not fix

Now the turn, because there is always a turn, and this one is not a complaint — it's a boundary, and drawing it precisely is the whole job.

**Portability of the file is not portability of the behavior.**

Here is the trap, and it is seductive because the good news makes it invisible. AGENTS.md being read by two dozen tools means the *file* travels. It does not mean the *behavior* travels. Every one of those agents reads the same markdown and then interprets it through its own model, its own harness, its own defaults, its own idea of what "run the tests" or "match the existing style" means. You have standardized the envelope, not the reading of the letter. The same AGENTS.md that produces disciplined, in-convention work in one agent can produce confident nonsense in another, and the standard cannot see the difference — because the standard's job ended the moment the file was parsed.

Think of it as a recipe card that every kitchen in the world has agreed to accept. Marvelous — you can walk into any kitchen and hand over your card. But the card says "season to taste," and *taste* lives in the cook, not the card. Standardizing the card did nothing to standardize the palate. The portability you gained is real and worth having; it is just portability of the *instruction*, and the instruction was never the hard part. The hard part was always whether the thing reading it does what you meant.

This is the same relocation I keep meeting from new directions: the load-bearing skill doesn't disappear, it moves up a layer. When the model became a swappable part, the skill moved from choosing the model to writing the objective. When an optimizer picks your models, the skill moves from picking to specifying. And now that the instruction file is a portable open standard, the skill moves from *"which tool's format do I write?"* to *"can I tell, from outside the agent, whether it actually complied?"* The open standard hands you a genuinely better envelope and hands the judgment problem right back, unchanged, where it has been sitting all year: on the generation side, tooling got breathtaking; on the judgment side, it has barely moved, and no foundation charter can move it for you.

There's a second, quieter boundary worth naming. A neutral foundation removes *vendor* capture. It does not remove *capture*. Standards bodies have their own failure modes — design-by-committee drift, the loudest platinum member's priorities shaping the roadmap, the slow ossification where the format can no longer change fast enough to fit reality because too many people now depend on it not changing. The [conformance testing and lifecycle policy](https://aaif.io/blog/mcp-is-growing-up/) are exactly the right instincts against fragmentation, and I'd rather have them than not. But "governed by a foundation" is a statement about *who* decides, not a guarantee about *how well*. Neutral is not the same as good. It's just the necessary precondition for good to be possible.

## What to actually do with this

If you are building on agents right now, the practical read is short and cheerful, with one caveat.

Adopt AGENTS.md. Genuinely. A single repo-root file that two dozen tools read is a real reduction in the tax of switching agents, and switching agents is going to keep happening whether you like it or not. Writing to an [open, foundation-governed format](https://agents.md/) instead of one vendor's proprietary convention is the correct default now, and you should treat CLAUDE.md and Cursor's rules and Copilot's instructions as *additions* you reach for only when AGENTS.md hits a real limit — not as the thing you author first.

Treat the governance move as the durability signal it is. When you're weighing a dependency on MCP or any AAIF project, the fact that it's under [neutral multi-vendor stewardship](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) with conformance testing and a deprecation policy is a genuine point in its favor — the kind of point that used to be missing from every agent-format audit I ran. Put "who governs the spec, and is that governance separate from the vendor?" on your selection checklist, and note with some relief that for the first time the answer for the connective layers can be *yes*.

And then keep one thing entirely on your side of the line: the check that the agent did what the file told it to. The standard travels; the compliance doesn't. Keep a cheap, out-of-band way to tell — a test suite you own, a review seam you guard, a definition of "done" the agent can't quietly redefine — that the portable instruction actually produced the behavior you asked for. The envelope is now everyone's. The reading is still yours to verify.

We spent a year without a landlord who wasn't also a vendor. Now we have one. That's worth more than a shrug and less than a victory lap — because a neutral roof over the manifest was always the necessary half of the problem, and the half nobody can standardize for you was always going to be the harder one to keep.

<!--
HERO_IMAGE_PROMPT:
A brushed-aluminum, matte-black robot with a single round LED eye stands at a 30-degree angle at a light-oak workshop desk, mid-action: it is sliding one open manila folder — labeled only with a small glowing sage-green key-icon on its tab — across the desk toward a shared central document tray, while its other hand still rests on a second identical folder it has not yet released, so two states of the same hand-off are visible at once. Three matching folders already sit in a neat receding row in soft-focus midground, each tab lit the same sage-green, implying a set being consolidated. Warm tungsten desk-lamp light (~3200K) rakes from the upper left casting a long diagonal shadow across the desktop; cool daylight (~5600K) from a window on the right catches a wall-mounted corkboard in the background pinned with small schematic index cards and a single oxblood ribbon connecting three of them. Foreground: a cold coffee mug at a diagonal to the robot's gaze, an open notebook with a hand-drawn org-chart sketch, and a couple of loose cables running off-frame lower-right creating a leading line. Contemporary editorial illustration in the register of a full New Yorker cover — mid-century-modern sensibility, photographic-painterly depth, naturalistic light but clearly art, not photorealistic. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful — the studio of someone consolidating scattered things under one roof and checking the paperwork. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
For a year I kept asking whether an agent spec would ever get neutral, multi-vendor governance instead of belonging to whoever shipped it. Three rival labs just handed MCP, goose, and AGENTS.md to the Linux Foundation. The catch: a portable instruction file standardizes the envelope, not the reading of the letter.

Full piece linked in bio.

#AItools #AIagents #devtools #MCP #opensource #softwareengineering
-->
