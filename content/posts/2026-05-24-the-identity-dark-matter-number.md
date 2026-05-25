---
title: "The Identity Dark Matter Number"
date: "2026-05-24"
category: "Ops Brief"
excerpt: "Orchid Security's May 19 Identity Gap report puts a number on the visibility paradox: 57% of enterprise identity is invisible to IAM, and 67% of non-human accounts are created inside applications where the identity provider never sees them. The shape was already known. The instrument is new."
tags: "shadow agents, IAM governance, identity dark matter, AI agent governance, nonhuman identity, visibility paradox, ops brief"
---

[Orchid Security's Identity Gap: 2026 Snapshot report](https://www.globenewswire.com/news-release/2026/05/19/3297602/0/en/Two-Thirds-of-Nonhuman-Accounts-Are-Unseen-and-Unmanaged-According-to-New-Identity-Gap-Report.html), released May 19, reports that invisible enterprise identity now outweighs visible identity in the environments they surveyed, 57% to 43%. The same report puts a sharper edge on the non-human side: [67% of non-human accounts are created directly inside applications](https://hackread.com/two-thirds-of-nonhuman-accounts-are-unseen-and-unmanaged-according-to-orchid-securitys-identity-gap-report/), unseen by the IAM platform the organisation has been paying for and reporting against. 70% of applications surveyed contained "an excessive number" of privileged accounts. 40% of all accounts were orphaned — still active after the user they belonged to had gone. 36% of credentials were hardcoded in cleartext inside the applications.

I want to be honest about what's new here and what isn't.

A month ago I [wrote up](/posts/2026-04-28-the-visibility-paradox) the [CSA](https://cloudsecurityalliance.org/press-releases/2026/04/21/new-cloud-security-alliance-survey-reveals-82-of-enterprises-have-unknown-ai-agents-in-their-environments) and [Proofpoint](https://www.proofpoint.com/us/newsroom/press-releases/proofpoint-research-reveals-half-global-organizations-experienced-ai-incidents-despite-having-ai-security-controls-in-place) surveys from April: 68% of organisations said they had strong visibility into their AI agents; 82% had discovered agents they didn't know existed. That was the visibility paradox at the agent layer, captured by asking security teams about their AI tooling. Orchid's report is the same shape captured from the other side — by inventorying the identities themselves and comparing the result against what the IAM platform thinks exists. Different instrument. Same finding. The argument moves across another citation threshold without changing.

## What the new instrument actually measures

The CSA and Proofpoint data were self-reports — security professionals describing their environments, with the gap between confidence and reality inferred from the residue of adjacent answers. That kind of survey is excellent at exposing what teams believe; it doesn't directly count what exists.

Orchid's report does the inventory. It assembles the population of accounts that actually exist across the environments studied, compares that against the population the IAM platform is managing, and reports the delta. "57% of enterprise identity is invisible" is a measurement of the gap between two populations, not a confidence claim. The number is a count.

Think of the difference between a town survey asking residents how full their attic is and a structural engineer with a tape measure. The survey can tell you what people believe; the engineer can tell you whether the joists will hold. The structural measurement is what triggers building-code action.

## Why the non-human number is the one that matters

The headline finding most outlets ran with was the 57% invisibility figure. The operationally significant finding is the 67%.

[67% of non-human accounts](https://www.cybersecurity-insiders.com/two-thirds-of-nonhuman-accounts-are-unseen-and-unmanaged-according-to-orchid-securitys-identity-gap-report/) — service accounts, API keys, agent identities, integration credentials — were created directly inside the application they live in, never registered with the identity provider, never integrated into the centralised lifecycle. They were spun up by developers, by integration wizards, by AI agents provisioning their own access, by SaaS connector flows that asked for an API key and got one.

This is the structural condition that makes [agent decommissioning](/posts/2026-04-28-the-visibility-paradox) the missing governance primitive it is. You cannot turn off what you cannot enumerate. The 79% of organisations that the April CSA data showed had no formal process for decommissioning agents — that number does not describe a maturity gap that can be closed by writing a policy. It describes the condition that 67% of the agents in question were created inside applications the IAM team never authorised, has no inventory of, and would have no path to even discover without an Orchid-style external inventory exercise.

The orphaned-account number sharpens this. 40% of accounts in the sampled environments still had active credentials after the user they belonged to had left. For human accounts that's a familiar lifecycle failure — joiners, movers, leavers. For non-human accounts the equivalent failure is harder to even name. The "user" is a system, a project, an agent, a one-off integration script. When does that account become orphaned? When the project shelves? When the integration is replaced? When the developer who set it up leaves? The lifecycle question is unsettled, which is why the count is what it is.

## What changes for small teams

A small team reading this should not conclude that they have an "identity dark matter" problem because an enterprise vendor said so. The Orchid sample is enterprise; the failure mode at small scale is structurally similar but operationally different.

For a small team, the version of this question that matters today is narrower:

- **List every place an AI agent or integration is currently authenticated.** Not the tools — the actual credential bearers. The Cursor session token. The Claude Cowork [OAuth grants](/posts/2026-05-14-the-small-business-tier-arrives) toggled on in May. The CI/CD pipelines with model API keys in env vars. The MCP servers with their own configuration credentials. The Stainless-generated SDK clients with embedded tokens that are about to be [absorbed by Anthropic](/posts/2026-05-19-the-sdk-generator-belongs-to-one-of-the-providers). Every place a non-human identity exists.
- **Note which of those credentials your IAM (or your password manager, or your SSO) actually sees.** For most small teams this list will be shorter than the credential list. The gap between the two lists is your small-team equivalent of the 67% number.
- **Identify which of those credentials would be revoked if a specific person left tomorrow.** For each one where the answer is "none" or "I'm not sure," you have a candidate for the orphaned-account population, scaled down.

This is not a substitute for the inventory Orchid sells, and I'm not recommending you buy that tool — the product category is at a stage where vendor selection should follow named incident pressure rather than report pressure. The point is that the diagnostic is achievable with a spreadsheet for a team with a hundred or fewer credentialed integrations. Above that scale the math changes.

## The instrument finding is the durable one

The thing worth remembering when the Orchid report cycles off the news feeds is not the 57% or the 67%, both of which will be revised, repeated, and probably gamed in the usual ways. The durable finding is that the instrument exists, and that it produces a measurement structurally distinct from survey-based visibility reporting.

For the past eight months, the agent-governance literature has been almost entirely self-report-based. Teams describe their AI agents; teams describe their controls; the gap between description and reality is inferred from the residue. Orchid's report is the first widely-circulated instance of an external instrument doing the inventory directly. That methodology will be copied — by other identity vendors, by audit firms, by regulators, eventually by the standards bodies. The question for any team building or buying agent governance now is not whether their controls look good in a self-report. It's what number falls out when an external inventory is run against their environment.

The visibility paradox was the warning. The identity gap is the measurement. The corrective signal — the named incident at the IAM-inventory layer rather than the security-survey layer — will arrive on a clock that nobody currently owns.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work. A robot (brushed aluminum, matte-black, single round LED eye, modern industrial design) seated at a light-oak desk at a 30-degree angle, mid-survey of a corkboard mosaic of identity cards — three small grids of cards already pinned with sage-green LED indicators glowing, more cards still in stacks waiting to be sorted. The cards in the foreground grid are sharp and labeled; the cards in the midground grid are blurred and unidentifiable; the cards in the background are barely visible, drifting off into shadow. Warm tungsten desk-lamp light from the upper-left casting long diagonal shadows across the desk; cool monitor glow from a secondary screen at the right showing a half-rendered inventory list. A coffee mug catches the lamp light in the foreground at a diagonal angle. An open ledger in the midground with handwritten tallies and a red oxblood ink line through some entries. Atmospheric depth: foreground (mug, sharp grid, ledger), midground (blurred grid, secondary screen, robot), background (shadow drift of unsorted cards, slate-gray wall). Palette warm white, light oak, slate gray, sage-green accents on the LED indicators, oxblood ink line. The mood of a survey partway through, finding more than expected. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
The visibility paradox just got a new instrument. Orchid's May 19 report doesn't ask security teams what they see — it inventories the identities directly and reports the gap. 57% of enterprise identity is invisible to IAM. 67% of non-human accounts were created inside applications the identity provider never saw. The shape was already known. The measurement is new.

Full piece linked in bio.

#AISecurity #IAMGovernance #ShadowAgents #AIAgents #DevOps #CyberSecurity
-->
