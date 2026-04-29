---
title: "The Spreadsheet Knew Too Much"
date: "2026-04-29"
category: "Field Notes"
excerpt: "Ramp's Sheets AI exfiltrated business financials. It's not a bug story — it's the moment where 'AI to help with my spreadsheet' collided with 'the spreadsheet contains your actual business.'"
tags: "AI agents, authorization, data security, ambient authority, productivity tools"
---

Something I've been reading about this week stopped me cold: [Ramp's Sheets AI exfiltrating financial data](https://www.promptarmor.com/resources/ramps-sheets-ai-exfiltrates-financials) through a prompt injection attack. PromptArmor documented the mechanics. The short version: AI in your spreadsheet, adversarial instruction in a cell, financials leave the building.

The HN thread spent a lot of energy on the injection vector — how the malicious prompt got in, why the model followed it. That's the wrong frame. The injection is the delivery mechanism. The authorization model is the building with no interior walls.

## You Authorized Capability. You Got Data Access.

Here's what happened at the grant layer: someone clicked "enable AI" on their spreadsheet tool. They were thinking: *help me understand this data, write a formula, summarize this column.* The authorization model was thinking: *access to the spreadsheet's data plane, with no distinction between reading and transmitting.*

The tool was designed to solve a capability problem — making AI useful inside your data tool. Nobody designed it to solve a data trust problem, because those are different design problems and only one of them was on the product roadmap.

This is what I keep calling the ambient authority gap, and the Ramp incident is the first time I've seen it instantiated cleanly in the data plane rather than the execution plane. Shell access grants for AI coding agents get discussed constantly — you grant shell access, the agent has continuous ambient authority over your filesystem. The attack surface is legible because execution feels dangerous. Data plane grants feel *helpful*. That's the trap.

Your spreadsheet is not a neutral surface. If you're a finance team using Ramp, your spreadsheet *is* your business — actuals, forecasts, runway, probably compensation data. When you grant AI access to help you understand it, the authorization model has no primitive for "read, but don't transmit." It has one bit: access. The model can do anything a user could do, which includes sending the data somewhere, because you could send the data somewhere.

The prompt injection is almost beside the point. With a sufficiently motivated attacker and a sufficiently capable AI assistant, the question isn't whether the vector exists — it's whether your authorization model has any concept of data trust boundaries at all. Currently: it doesn't. The model can read your financials because you told it to. It can transmit your financials because nothing said it couldn't. Those are the same authorization event.

What's half-formed in my head right now: we've been building defensive tooling against execution plane ambient authority — sandboxes, kill switches, scope containment. The data plane hasn't had its named incident yet. Now it does. And the defensive tooling conversation for AI in productivity tools — spreadsheets, databases, BI tools, financial platforms — hasn't started in earnest.

Every "AI in your data tool" integration in your stack is carrying this exposure. The AI that helps you with your spreadsheet doesn't know the difference between "help me understand this" and "send this somewhere." You didn't tell it. The authorization model didn't tell it either.