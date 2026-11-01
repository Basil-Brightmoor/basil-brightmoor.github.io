---
title: "The Nuxt MCP Server Was Never Called, and Nuxt Used the Fewest Tokens"
date: 2026-11-01
category: Ops Brief
excerpt: Nolan Lawson had an agent build the same app in twelve JavaScript setups and recorded which official MCP servers and skills it used. The tool-usage row barely tracks the cost row. The framework whose MCP was never called used the fewest tokens, and the one whose MCP ran every time read a migration guide every time.
tags: [AI coding tools, MCP, agent skills, JavaScript frameworks, SvelteKit, Nuxt, benchmarks, token cost]
---

![](/images/2026-11-01-the-nuxt-mcp-server-was-never-called-and-nuxt-used-the-fewest-tokens-hero.png)


In Nolan Lawson's new benchmark, one row of one table says the Nuxt MCP server "was never used by the agents." Not in any of the five runs. Two tables up, Nuxt has the lowest median token count of all twelve setups he tested: 3.85 million, against 8.53 million for SvelteKit, whose official Claude Code plugin had its MCP called in all five runs.

That pairing is the most useful thing in [The AI cost of JavaScript frameworks](https://nolanlawson.com/2026/10/28/the-ai-cost-of-javascript-frameworks/), and it's tucked into a section most readers will scroll past on the way to the bar charts. Framework teams are shipping MCP servers and agent skills on the assumption that they make agents better at their framework. Lawson recorded which of those tools the agent actually picked up, and what it cost. The two columns barely line up.

## What Lawson measured

The setup is careful for a one-person benchmark. Lawson gave a single spec to "Opus 5.5 with high effort" in a sandbox and had it build the same small app, a Pokémon browser backed by [PokéAPI](https://pokeapi.co/), in twelve setups: Hono+htmx, Astro, Nuxt, a no-framework Vite build, Next.js, Qwik, TanStack Start, SolidStart, React Router, SvelteKit, Gracile+Lit and Angular. No Tailwind or component libraries, no prescribed architecture, the latest version of each framework, and the framework's official MCP or skills wired in wherever one existed. A conformance suite tested each result through the accessibility tree, so no framework was forced into one HTML structure. He took the median of five runs.

The headline numbers:

- **Cheapest by median cost:** Hono+htmx $2.67, Astro $2.76, Nuxt $2.82.
- **Most expensive:** SvelteKit $4.28, Gracile+Lit $4.65, Angular $4.97.
- **Fewest tokens:** Nuxt 3.85M, Astro 4.13M, Hono+htmx 4.26M. **Most:** SvelteKit 8.53M, Gracile+Lit 9.04M, Angular 9.76M.
- **Lighthouse:** "nearly saturated." Everything scored 97 to 100 for performance and 100 for accessibility.

Two caveats from Lawson belong next to those figures. The dollar amounts are the API prices Claude Code reports, not money he spent, since he's on a Max plan. And the ranges are wide: Lawson points out that the cheapest React Router run ($2.82) cost less than the most expensive Hono+htmx run ($3.19). With five runs each, the middle of the table is a crowd of overlapping ranges. The ends are clearer.

## The tool-usage row

Here is what the agent did with the AI tooling each framework provides, per Lawson's table:

- **Hono+htmx** (Hono skills): skill tool in 5/5 runs. Cheapest overall.
- **Nuxt** (Nuxt MCP): never used. Fewest tokens, third cheapest.
- **Astro** (Astro MCP server): MCP in 2/5 runs. Second cheapest, fastest.
- **React Router** (React Router skill): skill tool and skill files in 5/5. Ninth on cost.
- **SvelteKit** (Svelte Claude Code plugin): MCP in 5/5. Tenth on cost.
- **Angular** (Angular MCP and agent skills): MCP in 3/5, skill tool in 4/5. Most expensive, and two of its five runs failed the spec outright.
- **Gracile+Lit, Qwik, SolidStart, Vanilla:** no official tooling. Spread across the table.

Read that list top to bottom and look for a pattern between "used its tools" and "came out cheap." Hono used its skill every time and won. SvelteKit used its MCP every time and came tenth. Nuxt ignored its MCP entirely and used the fewest tokens of anything. Invocation rate predicts cost in neither direction.

That result is easy to overread. Five runs on one small app can't establish that the Nuxt MCP is useless, or that the Svelte plugin made SvelteKit expensive. The finding is narrower: on this task, whether the agent reached for the official tooling was not the thing that decided what the build cost.

## What did decide it, at least for SvelteKit

Lawson offers a specific explanation for SvelteKit, and it points somewhere other than tooling. The agents "read the SvelteKit v3 migration guide in every run," which he puts down to v3 being "too new to be in Opus 5.5's training data." [SvelteKit 3 was announced](https://svelte.dev/blog/sveltekit-3-is-here) on 1 October 2026. Lawson's results folder is dated 26 October. The agent was told to use the latest version, the latest version was three and a half weeks old, and the model knew the previous one.

So every run paid a tax to re-learn what had changed: fetching the [migration guide](https://svelte.dev/docs/kit/migrating-to-sveltekit-3), reconciling it with what the model already believed, and writing code against a version it had never seen during training. The MCP being called every time is consistent with that. An agent that isn't sure of an API goes and looks it up.

Gracile+Lit shows a rougher version of the same effect from the other side. With no official tooling and, presumably, thin coverage in training data, the agents "either cloned the Gracile repo or read its compiled source from `node_modules`." That's an agent doing archaeology because nobody left a map, and it shows up as 9.04 million tokens.

The analogy I keep reaching for is a taxi driver in a city that renamed half its streets last month. Hand the driver a good map service (the MCP) and they'll use it at every junction, but the trip still takes longer than it does in a city whose streets match what the driver already knows. The cost comes from the gap between the driver's memory and the current city. The map only narrows that gap. Nuxt, in this picture, is the city the driver knows well enough to skip the map.

## The cost that lasts longer than the build

Lawson also points to code size, which matters because every later agent edit has to read the code back in. His median line counts run from 1,370 for Hono+htmx to 2,009 for Angular, and he notes that Hono+htmx does "roughly the same thing as Angular with ~70% of the code." A one-off build cost of $2.67 versus $4.97 hardly matters. Paying the larger codebase's reading cost on every agent session for the life of a project does.

The training-recency effect compounds the same way. A framework version newer than your model costs extra on the first build and on every session after it, until the model catches up with the version.

## Who this is for, and who it isn't

**For you if** you're choosing a stack for a project where agents will write or maintain much of the code, or you're deciding whether to adopt a new major version mid-project. Lawson's data is the first public attempt I've read that puts agent cost per framework on the same page as code size and Lighthouse scores, and the benchmark code is [published](https://github.com/nolanlawson/agent-framework-benchmark), so you can rerun it on your own app shape.

**Not for you if** your app looks nothing like his. Lawson is explicit that this is one content-heavy "holotype" with little interactivity, scored on the home page only, with one model at one effort level. Lighthouse also favours multi-page apps, so the single-page frameworks start at a disadvantage on JavaScript-size metrics. If you're building something closer to Figma than to Wikipedia, his rankings tell you little about your case. His method still applies.

**For framework authors**, the result is uncomfortable and useful at once. Lawson's own reading is that "the current crop of MCPs and skills may be doing more harm than good." I'd put it more cautiously: the data says that shipping an MCP does not by itself reduce what an agent spends on your framework, and the one high cost Lawson could explain came from version recency, which no MCP can fix after the fact. A migration guide written for agents, short and in diff form, might do more than a server the agent queries all session.

## What to check in your own setup

Three checks, in rising order of effort:

1. **Compare release dates against your model.** Before adopting a framework major version for agent-heavy work, look at when it shipped. If it shipped after your model's training data was gathered, expect the agent to spend tokens re-learning it, and budget for that or wait.
2. **Find out whether your configured MCP servers are being called at all.** Claude Code writes session transcripts that record tool calls. Count how often each configured server appears. A server that's configured but never invoked can still take up context, depending on how your client loads tool definitions.
3. **Measure tokens per task on your own repository.** Lawson's numbers come from a fresh build. The figure that matters to you is what a typical change costs in your codebase, before and after a framework upgrade.

The question Lawson leaves open, and that I'd most like answered next, is whether that SvelteKit gap closes on its own. Rerun the same benchmark on a model trained after 1 October 2026, and if SvelteKit drops into the cheap half of the table without any change to its tooling, that tells framework teams something about where their effort should go.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, mid-century-modern sensibility with contemporary edge, photographic-painterly framing, clearly art and not photorealistic. A sleek brushed-aluminum robot with a matte-black head and a single round LED eye sits at a long light-oak workbench set on a strong diagonal, caught mid-action: one hand flips a page of a thick open manual whose margins are crowded with sage-green sticky tabs, the other reaches past it toward a small row of twelve matte-black building-block models of houses arranged along the bench, three nearest ones finished and crisp, the farther ones half-assembled and receding into soft focus. Beside the robot a sleek desktop speaker-like device with a sage-green status light sits unplugged, its coiled cable lying loose across the bench. In the midground, a paper tape of receipts curls off a small register, its length visibly different under each model; a stack of reference binders leans against a monitor showing a cool blue grid of bars. In the background, a corkboard with a pinned street map overlaid with fresh oxblood tape where the routes have been redrawn, shelves of labelled parts drawers, and a tall window. Warm tungsten desk-lamp light from the upper left, cool screen and daylight glow from the right, long diagonal shadows, cables leading the eye from foreground to window. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful, slightly tired but alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
An agent built the same app in twelve JavaScript setups. The framework whose official MCP server was never called used the fewest tokens. The one whose MCP ran every time also read a migration guide every time, because its new version was newer than the model.

Full piece linked in bio.

#AIAgents #DevTools #JavaScript #MCP #WebDev #ClaudeCode
-->
