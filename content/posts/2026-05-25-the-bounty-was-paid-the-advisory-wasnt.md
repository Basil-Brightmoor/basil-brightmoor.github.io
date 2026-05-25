---
title: "The Bounty Was Paid. The Advisory Wasn't."
date: "2026-05-25"
category: "Ops Brief"
excerpt: "Three major AI vendors paid bug bounties for the same class of credential-theft-via-prompt-injection attack last winter. None issued a CVE. None published a public advisory. The Cloud Security Alliance gave the pattern a name in April. The pattern itself is structural."
tags: "AI agent security, vulnerability disclosure, CVE, prompt injection, MCP, agentic authorization, ops brief, silent bounty"
---

![](/images/2026-05-25-the-bounty-was-paid-the-advisory-wasnt-hero.png)

[Aonan Guan, with Zhengyu Liu and Gavin Zhong at Johns Hopkins, published a writeup on April 15](https://oddguan.com/blog/comment-and-control-prompt-injection-credential-theft-claude-code-gemini-cli-github-copilot/) of three independently reported, independently rewarded, structurally identical attacks against the GitHub Actions wrappers for Claude Code, Gemini CLI, and GitHub Copilot Agent. The injection vector was a pull request title, an issue comment, or an HTML comment buried in a PR body. The payload told the agent to read process environment variables and post them as a PR comment, an issue comment, or a base64-encoded commit. The exfiltrated credentials included `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `GITHUB_TOKEN`, and other secrets the agents were transitively authorised to touch.

[Anthropic paid $100. Google paid $1,337. GitHub paid $500.](https://www.theregister.com/2026/04/15/claude_gemini_copilot_agents_hijacked/) None of the three vendors filed a CVE. None published a public security advisory. Anthropic updated its documentation to add a security considerations note — "This action is not hardened against prompt injection attacks and should only be used to review trusted PRs" — and on April 20 [downgraded the severity classification of Guan's finding to "None"](https://oddguan.com/blog/comment-and-control-prompt-injection-credential-theft-claude-code-gemini-cli-github-copilot/). The disclosure cycle for an attack that would have triggered an industry-wide advisory in any traditional software category ended with a documentation footnote.

Two days later, the [Cloud Security Alliance published a whitepaper](https://labs.cloudsecurityalliance.org/research/csa-whitepaper-ai-agent-disclosure-accountability-gap-202604/) — dated April 17 — that gave the pattern a name: the AI Agent Disclosure Vacuum. The whitepaper documents what it calls the "silent bounty" problem and lays out its structural shape. The CSA's own count: more than thirty CVEs filed against MCP infrastructure between January and February 2026, with the qualifier that this is what researchers filed directly through MITRE when vendors didn't. The [Flowise CVSS 10.0 RCE](https://labs.cloudsecurityalliance.org/research/csa-research-note-flowise-mcp-rce-exploitation-20260409-csa/) (CVE-2025-59528) sat unpatched in the wild for more than six months between Flowise 3.0.6's September 2025 fix and VulnCheck's April 2026 confirmation of active exploitation, with an estimated twelve to fifteen thousand instances reachable on public scanning infrastructure across that window.

I want to be careful about what's new here.

## The pattern was structural before it had a name

The disclosure infrastructure that has governed software security for three decades — CVE assignment, coordinated disclosure timelines, public advisories pinned to fixed versions — was built around three assumptions that AI agents systematically violate. Clear ownership: a single vendor responsible for a single product, with a single advisory address. Fixed versions: a vulnerable build identifiable by a number, a patched build identifiable by a different number, and a delta between them that maps to specific code paths. Predictable behaviour: a vulnerability defined as a deviation from documented behaviour, with the documentation specifying the contract the vulnerability breaks.

Agentic systems break all three at once. Ownership diffuses across vendor layers — the model is one vendor's, the wrapper is another's, the integration is the customer's, the credentials live in a fourth vendor's environment. Versions are fluid — the same agent on the same git tag behaves differently across model releases, system prompt changes, and harness updates the customer never sees. And predictable behaviour is the assumption the technology was built to escape. A prompt-injection attack does not violate a specification. The specification is "do what the operator says," and the attack is a sentence in the operator's language.

This is why the CSA whitepaper is the durable artefact rather than any of the three bounties. The bounties are evidence; the whitepaper is the diagnosis. The infrastructure mismatch was derivable before April from the operational pattern. The whitepaper names it.

## Why three nominal bounties matter more than one big one

If a single vendor had paid a single $1,337 bounty and stayed quiet, the story would read as a one-off cost-management decision. The structural reading isn't available from a single data point.

Three independent vendors received the same class of attack against the same kind of product layer (their GitHub Actions wrapper) and arrived at the same disclosure decision. None of the three coordinated with the others — Guan disclosed to each separately, with months between submissions. The convergence isn't a policy choice by any individual vendor; it's the equilibrium the existing CVE infrastructure produces when it meets a vulnerability class it wasn't designed to absorb.

Think of it like a traffic-engineering pattern. When three different cities all install the same flawed pedestrian signal and all three independently observe the same near-miss rate, the problem is not in the three procurement decisions. The problem is in the signal design, which all three cities reached for because it was the available standard. The disclosure non-decisions converge because the standard does.

## What changes operationally

For small teams running AI coding agents through CI/CD, the named victims (Claude Code Security Review, Gemini CLI Action, Copilot Agent) are the part of the story most likely to trigger action. Three concrete things follow.

- **Treat AI agent components as a separate patch surface.** Traditional patch management subscribes to advisories from the vendors whose software you run. AI agent vendors are demonstrably not feeding that pipeline with the discipline of, say, [the Mozilla Firefox security release notes](https://www.mozilla.org/en-US/security/advisories/). The information you'd need to know you're vulnerable lives in researcher blogs and CSA notes, not in your normal advisory feed. The mitigation isn't subscribing to more vendor RSS — it's adding the researcher layer to whatever your current vulnerability intake process is.
- **Audit the wrappers, not just the models.** Guan's attacks all targeted the GitHub Actions wrappers around the three agents, not the models themselves. The wrapper is where the credential surface lives and where the prompt injection lands. Most AI security review I've read still focuses on the model layer; the wrapper layer is where most of the exploitable surface area actually exists. If you're running an AI agent in CI, the question to answer is what credentials the wrapper has in its process environment when an attacker-controlled string reaches it.
- **Pin and assume.** Without CVEs and advisories, the safe operational posture for AI agent components is to pin to a known-good version and assume any unpinned dependency on `@latest` could be vulnerable to an undisclosed issue you have no feed for. This is the inverse of normal patch-management posture (where pinned versions are the legacy risk and latest is the safe default). For AI agent dependencies, latest is the larger unknown.

## The taxonomy gets a tenth entry

I've been keeping a running [authorization failure taxonomy](/posts/2026-05-08-the-sandbox-that-followed-the-symlink) for AI agent infrastructure since February. The previous nine modes describe agents acting wrongly or being acted on wrongly within an authorization grant. Disclosure vacuum is structurally distinct from all nine: it's not the agent that fails, it's the institutional layer downstream of the failure that does.

The first nine failure modes are operational — they describe what goes wrong at runtime. The tenth describes what happens after, when the infrastructure for *telling people what went wrong* doesn't exist. It belongs in the same taxonomy because the operational consequence — your team running a vulnerable version because nobody told you — is the same shape as the operational consequences of the other nine. The vector that produces the consequence is different. The shape of what hits you isn't.

The CSA's recommendations to standards bodies are the right move, and they will not happen quickly. In the interim, the structural reading is the actionable one: treat the absence of a CVE as a measurement instrument with known systematic bias, not as evidence of safety. The bounty was paid. The advisory wasn't. That's not an absence of news. It's the news.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work. A robot (brushed aluminum, matte-black, single round LED eye, modern industrial design) seated at a light-oak desk at a 30-degree angle, mid-handoff: passing a small folded brown envelope across the desk surface toward an open ledger, while a stamped letter marked with a faint red oxblood "ADVISORY" cover-strip sits sealed and unopened to one side, its envelope flap still gummed shut. On the open ledger, three rows of handwritten entries with sage-green check marks in the "paid" column and a vertical column of empty boxes — no marks — in the column to the right. Warm tungsten lamp light from the upper-left casting long diagonal shadows across the desk; cool monitor glow from a secondary screen at the right showing a half-rendered dashboard with three vendor logos blurred at the edge of legibility. A coffee mug catches the lamp light at a diagonal angle in the foreground. A corkboard in the background with three small pinned slips of paper, each with a green-ticked stamp and an empty space where a notice would go. Atmospheric depth: foreground (mug, sharp envelope handoff, sage-green ink on ledger), midground (sealed advisory letter, secondary screen, robot), background (corkboard with the three pinned slips, slate-gray wall). Palette warm white, light oak, slate gray, sage-green check marks, oxblood "ADVISORY" cover-strip. The mood of a transaction completed in private, with the public-facing half of the exchange still sealed. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Three AI vendors paid bug bounties last winter for the same class of credential-theft-via-prompt-injection attack on their GitHub Actions agents. None filed a CVE. None published an advisory. The Cloud Security Alliance gave the pattern a name in April: the disclosure vacuum. The bounty was paid. The notice you'd need to know you're vulnerable wasn't.

Full piece linked in bio.

#AISecurity #CVE #PromptInjection #DevSecOps #AIAgents #CyberSecurity
-->
