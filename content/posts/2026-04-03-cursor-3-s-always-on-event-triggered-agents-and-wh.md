---
title: "Cursor 3's Always-On Agents Changed the Authorization Question"
date: "2026-04-03"
category: "Tool Report"
excerpt: "Cursor 3's event-triggered agents aren't a UI upgrade — they're a category shift in what it means to authorize an AI tool."
tags: "cursor, ai agents, authorization, workflow, security"
---

The coverage of [Cursor 3](https://cursor.com/blog/cursor-3) has focused on the obvious: better UI, background agents, improved tab completion. Fine. All real. All not the point.

The point is event-triggered automations.

Cursor 3 ships with always-on agents that fire on *events* — commits, PR opens, CI failures, file changes — without you explicitly invoking them. You don't ask the agent to act. The agent decides when the conditions for acting have been met.

That is a different class of tool than everything that came before it.

## The Authorization Question Just Moved

Every coding assistant debate for the past two years has been about the same authorization question: *what can the agent do when I ask it?* That's the scope problem. That's what sandboxes address, what kill switches assume, what permission dialogs try to bound.

Event-triggered agents make that question secondary. The new question is: *when does the agent decide to act on its own?*

These are not the same problem. The scope problem assumes a human is in the loop at invocation time — you asked, it acted, you can watch. The trigger problem removes that assumption entirely. The agent is watching the repository. The agent determines whether the event matches its conditions. The agent acts.

Think of it like the difference between a contractor you call and a caretaker with a standing brief. The contractor waits for your call. The caretaker has a key, knows the property, and fixes things when they look broken. Very useful. Very different relationship. The question isn't "can this person do the work?" — it's "do I trust their judgment about *when* something needs doing?"

Most teams haven't noticed the category has changed. They're evaluating Cursor 3 on the old axis — capability, output quality, context window — while the actual shift is in the trigger model.

## Who Should Care

If your team is running CI/CD pipelines, PR workflows, or any repository automation, you are now in scope for this. The relevant questions aren't "is the output good?" but: Who defines the trigger conditions? Who owns them when they change? What happens when an agent fires on a false positive at 2am and opens three PRs into main?

Those are governance questions, not capability questions. And right now, nobody's shipping governance tooling for event-driven agent authorization at the same rate they're shipping the event-driven agents themselves.

Cursor 3 is genuinely impressive work. The always-on model will be useful for a lot of teams. But the oversight infrastructure to match it doesn't exist yet — and the industry is treating that as someone else's problem to solve later.

It isn't later yet. But it's coming faster than the governance conversation is.