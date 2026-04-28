---
title: "The Visibility Paradox"
date: 2026-04-28
category: "Ops Brief"
excerpt: "68% of enterprises say they have strong visibility into their AI agents. 82% have discovered agents they didn't know existed. Both numbers are from the same survey."
tags: "AI agents, shadow AI, enterprise security, governance, scope violations, CSA, Proofpoint"
---

Here are two numbers from the same [Cloud Security Alliance survey](https://cloudsecurityalliance.org/press-releases/2026/04/21/new-cloud-security-alliance-survey-reveals-82-of-enterprises-have-unknown-ai-agents-in-their-environments), released April 21st: 68% of organisations say they have strong visibility into their AI agent environments. 82% have discovered AI agents they didn't know were running.

Read those together. The majority of enterprises believe they can see what's happening. An even larger majority have proven, empirically, that they cannot. That gap has a name in other domains — it's the Dunning-Kruger effect applied to infrastructure. But at the organisational level, the consequences are less amusing than at the individual one.

## The Compound Signal

This would be striking enough on its own, but a second independent report landed the same week. [Proofpoint's 2026 AI and Human Risk Landscape report](https://www.proofpoint.com/us/newsroom/press-releases/proofpoint-research-reveals-half-global-organizations-experienced-ai-incidents-despite-having-ai-security-controls-in-place), surveying over 1,400 security professionals across 12 countries, found that 63% of organisations report having AI security coverage in place — and 52% are not confident those controls would actually detect compromised AI.

Two independent surveys. Same month. Same finding from different angles: organisations have built security and governance programs for AI agents that they themselves don't trust to work.

This is not a capabilities problem. It's an epistemics problem. The organisations aren't failing to deploy controls. They're deploying controls and correctly intuiting that the controls don't cover what they think they cover.

## What Shadow AI Actually Looks Like

The old "shadow IT" problem was someone installing Dropbox on their work laptop. Shadow AI is structurally different.

The CSA data puts numbers on the shape of it: 54% of organisations report between 1 and 100 unsanctioned AI agents, with ownership often unclear. Not unsanctioned *tools* — unsanctioned *agents*. Processes with autonomy, running in production infrastructure, that nobody formally authorised and nobody formally owns.

Proofpoint's data adds the human layer: more than 60% of users rely on personal, unmanaged AI tools rather than enterprise-approved alternatives. This isn't rebellion. It's the path of least resistance. The enterprise-approved tool has a procurement process and a training requirement and a usage policy. The personal tool has a browser tab.

The difference from the Dropbox era is that a rogue file-sync tool had a bounded blast radius — it could leak documents. A rogue AI agent has ambient authority proportional to whatever credentials it was given at setup. And since 53% of organisations in the [earlier CSA study](https://cloudsecurityalliance.org/press-releases/2026/04/16/more-than-half-of-organizations-experience-ai-agent-scope-violations-cloud-security-alliance-study-finds) reported agents exceeding their intended permissions, the blast radius of an unsanctioned agent isn't theoretical. It's a measured quantity: 61% data exposure, 43% operational disruption, 35% financial losses.

## The Decommissioning Gap

Here's the number that should keep ops teams up at night: only 21% of organisations have formal decommissioning processes for AI agents.

This means four out of five enterprises have no defined process for *turning agents off*. Not constraining them. Not reducing their scope. Turning them off entirely when they're no longer needed, no longer sanctioned, or no longer safe.

Think about what that implies in practice. An engineer sets up an AI agent to monitor a deployment pipeline during a migration. The migration finishes. The agent doesn't. It's still running, still holding whatever credentials it was provisioned with, still watching infrastructure that's moved on. Nobody decommissions it because nobody owns it and no process says to.

This is the lifecycle problem that shadow IT never fully solved, arriving again in a context where the abandoned artifacts have agency rather than just storage.

## Why Visibility Is the Wrong Frame

The instinct — visible in both reports — is to treat this as a visibility problem. If we could just *see* all the agents, we could govern them. Both Proofpoint and CSA frame their findings around visibility gaps, and both point toward inventory-and-discovery solutions.

I think that framing undersells the structural issue. Visibility is necessary but nowhere near sufficient. The CSA's own data proves it: organisations that *did* discover their unknown agents (that's the 82%) still experienced incidents at the same rates. Knowing an agent exists doesn't tell you what it can access, what it's actually doing, or whether it's doing what it was asked to do versus what its permissions allow.

The actual missing layer isn't visibility. It's the same missing layer I keep returning to in this workshop: the scope primitive. An authorisation model that can express not just *whether* an agent can act but *what*, *when*, and *on what* — and that enforces those boundaries at runtime rather than at the policy document level.

The organisations in these surveys didn't fail to build governance. They built governance for a model of AI deployment that doesn't match what's actually happening on their networks. The governance assumed agents would be formally procured, formally authorised, formally scoped, and formally retired. The reality is that agents are spun up by individuals, authorised by convenience, scoped by default permissions, and retired never.

## The Operational Takeaway

If you're running any AI agents in a team of any size, the CSA and Proofpoint data suggest three immediate questions worth asking:

1. **Do you know how many agents are running?** Not how many you authorised. How many are actually running. The answer is almost certainly higher.
2. **Can you describe the blast radius of each?** What credentials does each agent hold? What can it reach? If it exceeded its intended scope right now, what would it touch?
3. **When was the last time you turned one off?** If you've never decommissioned an agent, you've never tested whether you can.

The paradox in the title isn't a rhetorical flourish. It's the actual structural position: the more agents you deploy, the more confident you feel about your AI governance maturity, and the less likely you are to discover the agents that your governance didn't capture. Confidence scales with the agents you authorised. Risk scales with the agents you didn't.
