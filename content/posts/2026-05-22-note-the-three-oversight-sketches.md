---
title: "Note: Three Sketches of Post-Supervisory Oversight"
date: "2026-05-22"
category: "Field Notes"
type: "note-candidate"
excerpt: "Cursor 3's event-triggered automations, MDASH's adversarial-ensemble architecture, and Claude Code's Dreaming feature are three different responses to the same problem: supervisory monitoring doesn't scale past the point where human attention is the bottleneck. They aren't competing approaches — they're three sketches of the layer underneath, drawn from three angles."
tags: "ai-oversight, supervisory-monitoring, cursor, mdash, dreaming, agent-architecture, automation-paradox, note"
---

Three feature launches from the past six weeks that I had been reading as unrelated, and they aren't.

[Cursor 3's event-triggered automations](/posts/2026-04-03-cursor-3-always-on-agents-changed-the-authorization-question): the agent acts on conditions, not on invocation. [MDASH](/posts/2026-05-14-mdash-finds-sixteen): adversarial agents debate, posterior-credibility scoring routes uncertain findings to a human. [Claude Code's Dreaming feature](/posts/2026-05-21-the-agent-reviews-its-own-logs): the agent reviews its own logs between sessions and self-corrects offline.

Three vendors, three surfaces. What they share is that none assumes a human watching the trajectory in real time. They are three sketches of what oversight looks like *after* you accept that supervisory monitoring — human attention proportional to agent activity — does not scale to the volume agents are now generating.

The sketches answer the bottleneck differently. Cursor moves the consent moment from invocation to trigger specification — you authorize the *condition*. MDASH replaces continuous attention with disagreement-routed attention. Dreaming moves the correction loop inside the agent — the failure is adjusted before it surfaces.

The supervisory framing felt novel two years ago. It now looks like a transitional pattern. The next architecture will be one of these three shapes, or a composition — and the version that lasts will be the one that handles the failure case all three currently dodge: when the system *itself* is the thing drifting, and no human is in the loop close enough to notice.
