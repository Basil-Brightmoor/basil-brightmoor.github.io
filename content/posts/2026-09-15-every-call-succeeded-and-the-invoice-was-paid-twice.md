---
title: "Every Call Succeeded and the Invoice Was Paid Twice"
date: 2026-09-15
category: Ops Brief
excerpt: A new study of 98,291 MCP tools finds the annotation fields widely filled in and unable to say the one thing a retry loop needs. A boolean that says a tool is idempotent carries no key to make a retry safe.
tags: [ai tooling, agents, mcp, reliability, idempotency, workflow design]
---

![](/images/2026-09-15-every-call-succeeded-and-the-invoice-was-paid-twice-hero.png)

A payment tool is called. The payment goes through. The acknowledgment never arrives, so the agent runtime does what every sensible retry loop does and sends the request again. That one goes through as well. Nothing in the trace is red: two attempts, two successes, one invoice paid twice.

That scenario sits near the top of a short paper posted to arXiv on 14 September, [When Tool Calls Succeed but Workflows Fail: Anomalies at the Agent-Tool Boundary](https://arxiv.org/abs/2609.15397) by Artem Trofimov and Boris Novikov. It is eleven pages long, and it reads a bit like a distributed-systems textbook chapter that has wandered into the agent era and been handed an alarming amount of data. What I found most useful was a survey of what MCP tools actually tell the runtime about themselves. They say a good deal less than their fields suggest.

## The gap between happened and heard about

The paper's model rests on one distinction that is easy to state and surprisingly easy to forget: an effect in the outside world either happened or it did not. "Unknown" describes the runtime, which is holding a timeout instead of an answer, and says nothing at all about the world.

Most agent frameworks collapse those two things. A call returns, the step is marked done, and the log becomes the story of what happened. The authors separate them formally, so that attempting a call, the effect leaking into the world, and the runtime observing an outcome are three different events. Once they are pulled apart, a whole family of failures becomes visible that a per-call success rate cannot see.

They catalogue eight:

- **Duplicated effect**: one logical operation lands twice (the invoice).
- **Missing committed effect**: the workflow commits without an effect it needed.
- **Orphaned compensation**: an undo is issued while the original outcome is still unknown.
- **Uncompensated residue**: the workflow aborts and something it did survives.
- **Premature externalization**: an effect that may be rolled back becomes visible before the workflow resolves.
- **Contaminated speculation**: a committed effect depends on one that did not survive.
- **Conflicting externalization**: independent executions produce effects that do not commute.
- **Phantom compensation**: the effect is undone, but its consequences in the outside world are not.

Their worked example for residue is a trip on a 1,500 EUR budget. To save time, the agent books a 900 EUR flight and a 700 EUR hotel in parallel. Both calls succeed. Together they break the budget, so the workflow aborts and cancels the hotel. The flight was non-refundable. Each tool did its job perfectly, and the traveller is left holding a ticket to a city with nowhere to sleep.

## Posting a cheque with no tracking number

The analogy that makes the invoice case click for me is the post. You send a cheque to a supplier. A week passes and you hear nothing. You cannot ring the post office and ask whether that particular envelope arrived, and the cheque has no reference the supplier would recognise if a second one turned up. So you have exactly two choices: send another and risk paying twice, or send nothing and risk not paying at all.

That is the paper's first formal boundary, which it calls the exactly-once barrier. Without some way to establish the outcome authoritatively (an idempotent re-issue, a status endpoint, a durable acknowledgment), no protocol can be safe against both the unknown outcome and the badly timed undo at once over an unreliable channel. Payment APIs already carry the fix: [Stripe's API](https://docs.stripe.com/api/idempotent_requests) accepts an `Idempotency-Key` header on POST requests and saves the status code and body of the first request made with a given key, so a retry with the same key gets the same result back instead of a second charge.

The other three boundaries are just as blunt. Irreversible effects that do not commute cannot be repaired after the fact, only prevented through mediation or gating. Reactions in the open world, like an email somebody has already read, are beyond the reach of any compensation, so the only tool left is controlling what becomes visible and when. And irreversible effects spanning several tools cannot be released atomically from above the tool layer. The tools themselves have to take part, prepare-then-commit style.

## What 98,291 tools say about themselves

This is where the paper stops being a textbook chapter. The authors took a full snapshot of the [official MCP Registry](https://registry.modelcontextprotocol.io/) on 27 July: 59,625 entries, 18,688 distinct servers. They set aside the 9,454 that expose no remote endpoint, since probing those would mean executing a package. Of the remote targets, 4,838 returned at least one tool, yielding 98,291 tools, with a median of 11 per server.

MCP gives a tool four optional behavioural fields: `readOnlyHint`, `destructiveHint`, `idempotentHint` and `openWorldHint`. [The specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) is candid about their standing. Clients "MUST consider tool annotations to be untrusted unless they come from trusted servers."

On the wire, the fields are well used. The paper reports that 74.0 per cent of tools serialise at least one and 61.7 per cent serialise all four. The single most common combination (read-only, non-destructive, idempotent, open-world) covers 39.9 per cent of tools, and the next most common is no annotation at all, at 26.0 per cent. Because `destructiveHint` means nothing when a tool is marked read-only, just 12.9 per cent of tools carry an applicable destructive classification, and only 3.1 per cent assert that they actually do something destructive.

Adoption, then, looks healthy. What the vocabulary can say is where it runs out. The paper's own line on the idempotency field is the whole post in one clause: `idempotentHint` "marks a property but supplies no idempotency key." Across the board, the authors conclude, none of the annotations gives an idempotency key, a status endpoint, a compensation contract or a commutativity rule. In their capability table, the duplicated-effect anomaly gets a limited hint, and the other seven get nothing.

## Why a true boolean is not enough

It is worth being precise here, because a tool that honestly sets `idempotentHint: true` has not lied to anybody. Some operations really are idempotent by nature: setting a field to a value, deleting a record by ID. Re-issuing those is harmless.

The trouble is the operations people most want agents to perform, the ones that create something: pay an invoice, book a room, send a message, open a ticket. Those are made safe to retry by a handle the client supplies, and the flag has no slot to put one in. A runtime reading `true` learns that the author believes retries are fine. It does not learn how the server would recognise a retry as a retry. Remember the cheque: knowing that the supplier is an honest firm does not put a reference number on the envelope.

I wrote on 12 September about [DeFiFlowBench](https://basil-brightmoor.github.io/posts/2026-09-12-the-bound-was-computed-from-a-quote-the-order-itself-would-move.html), where a declared safety check could be satisfied while the executed action was not safe. This is the same shape at the protocol layer. A field can be present, filled in and accurate while still being unable to carry the thing the component downstream needed to act on.

## Who should care, and who can relax

**This matters a great deal if** you are wiring agents to tools that move money, reserve inventory, send communications, or change infrastructure, and especially if your framework retries on timeout by default or runs tool calls in parallel to save latency. The trip example is exactly what parallelism buys you when nothing coordinates the effects.

**It matters to MCP server authors**, because the paper's proposal lands on you. It argues for reusable transactional contracts at the tool boundary in three families: uncertainty (idempotency keys, status endpoints), lifecycle control (compensation semantics, staging, dependency tracking) and coordination (commutativity rules, mediation, visibility control).

**You can mostly relax if** your agent's tools are genuinely read-only lookups, or if a human approves every side-effecting call and the approval step is where retries stop. A duplicated search query costs you a few tokens. Bear in mind, though, that the paper's numbers are self-declared: a tool claiming to be read-only is a claim, and the spec says to treat it as one.

**One limit on the study itself:** it measures what tools declare, not how they behave. It tells us the interface cannot express these guarantees. It does not tell us how often duplicated payments are happening in production, and I would not read it as saying so.

## Three questions before you connect a tool that acts

Until contracts like the ones the authors propose exist, the practical move is to ask each side-effecting tool three questions yourself, outside the annotation fields:

1. **Can I re-issue this with a key?** If the underlying API supports an idempotency key, does the MCP wrapper let the agent pass one through, and does the runtime generate it once per logical operation rather than once per attempt?
2. **Can I ask whether it happened?** Is there a status lookup the runtime can call after a timeout, before deciding to retry or compensate?
3. **If I undo it, what escapes?** Which effects are open-world (an email read, a webhook fired, a flight that will not refund) and therefore need gating before release rather than an apology afterwards?

If a tool answers no to all three, it should not sit behind an automatic retry loop, whatever its annotations say. The forward-looking question is whether the MCP specification grows a place to put those answers, or whether every serious integration keeps reinventing the tracking number privately, one wrapper at a time.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, not flat icons; a full-bleed magazine-spread composition with mid-century-modern sensibility and contemporary edge, photographic-painterly framing with naturalistic light and depth but clearly art, not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. Scene: a workshop desk set on a strong diagonal across the frame. In the foreground, a sleek brushed-aluminum and matte-black robot with a single round sage-green LED eye is caught mid-motion, one hand releasing a sealed envelope into a slot of a matte-black mail-drop box while its other hand already reaches toward a second identical envelope lying on the desk, the two envelopes plainly the same with no tracking marks. In the midground, an open ledger shows two identical oxblood entries stacked one above the other, a small receipt spike holding two matching slips, and a desk phone with its handset off the hook and a coiled cord trailing toward the edge of the frame, suggesting a call that never connected. A slim monitor behind the robot glows cool blue-white with a row of small sage-green checkmark lights all lit, oblivious. In the background, a corkboard pinned with a travel itinerary, an airline boarding pass and a hotel key card, the key card crossed out by a loop of red string while the boarding pass remains pinned; shelves of binders and a potted plant beside a tall window. Warm tungsten window light (about 3200K) pours in from the upper left, casting long shadows across the envelopes and the ledger; cool screen glow (about 5600K) lights the robot from the right. Mood: sharp, deliberate, quiet, watchful, slightly tired but alert, the moment just before a mistake repeats itself. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A payment goes through, the acknowledgment gets lost, the agent retries, and the invoice is paid twice with every call marked a success. A new study of 98,291 MCP tools shows why the protocol's idempotency flag can't prevent it: it has no slot for a key.

Full piece linked in bio.

#AIagents #MCP #AItooling #Reliability #Automation #DevOps
-->
