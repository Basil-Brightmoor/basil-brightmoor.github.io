---
title: "The session git never captured: why version control was designed for human authors and what the AI provenance gap actually costs"
date: "2026-03-02"
category: "Deep Bench"
excerpt: "This week's exploration"
tags: ""
---

```markdown
---
title: "The Session Git Never Captured"
date: "2026-03-02"
category: "Deep Bench"
excerpt: "Git was designed for human authors. It captures the diff, the commit message, the name. It was never built to capture the session — and as AI writes more of our code, that gap is becoming an accountability vacuum with a real price tag."
tags: "AI coding, version control, provenance, audit trail, WebMCP, governance"
---

Here is a thought experiment. You are three months into a fintech feature. Auditors request the change history. You pull up the git log — clean, timestamped, attributed. The diff is there. The commit message says something like "add transaction validation logic." What it doesn't say: the AI wrote most of it, the session ran for forty minutes, the model had access to your secrets manager during that window, and the first three suggestions were rejected before the fourth one landed. The diff shows what changed. The session shows *how* it happened, what was touched, and what was considered and discarded. The diff is in the repo. The session is gone.

That's not a hypothetical. That's the current state of AI-assisted software development for most teams.

A recent [Hacker News thread](https://github.com/mandel-macaque/memento) about whether AI sessions should be part of the commit caught my attention — not because the question is new, but because of *how* it's being asked. A year ago, the HN discourse on AI coding tools was dominated by "does this actually work?" and "are we replacing developers?" That conversation has largely ended, not because the skeptics were wrong but because the tools closed the gap. The new debate is governance-shaped: *given that AI is writing substantial amounts of our code, what counts as the provenance record, and who's responsible for it?*

That is a maturity signal. When a practitioner community moves from "should we use this?" to "how do we govern what it produces?" — that's adoption, disguised as skepticism.

## What Git Was Designed to Capture

Git's data model is a masterpiece of a specific era. Linus Torvalds designed it to solve the problem of distributed human collaboration on source code. The key word is *human*. The author field in a commit maps to a person. The diff captures a discrete set of intentional changes. The commit message is a human explanation of human reasoning. The whole system is built on the premise that a named person made a deliberate set of changes and can, if pressed, explain why.

That model worked beautifully for thirty years because it matched reality. Humans wrote code. Humans made commits. The diff was a reasonable proxy for the decision-making process because the decision-making process was short — one person, one idea, one change.

The AI session breaks every one of those assumptions simultaneously.

When a developer uses [Claude Code](https://claude.ai/code), [Cursor](https://www.cursor.com/), or [GitHub Copilot Workspace](https://githubnext.com/projects/copilot-workspace), the session is not a single intentional decision. It's a conversation. It includes prompts, context injection, rejected suggestions, accepted suggestions, mid-session corrections, and potentially access to secrets, files, and APIs that the final diff never touches. The model may have read ten files to change two lines. It may have generated and discarded three approaches before the fourth one worked. None of that is in the commit. The commit shows you the answer. The session shows you the work.

In a purely human workflow, this doesn't matter much. Developers don't commit their internal reasoning. We accept that the diff is the record and the author is accountable. But the AI session isn't internal reasoning — it's an external system with its own access footprint, operating with granted permissions, producing outputs that may exceed what the author fully reviewed. Treating that session the same way we treat a developer's mental process is a category error that happens to have been invisible until now.

## The Accountability Vacuum Is Not Hypothetical

The [Memento project](https://github.com/mandel-macaque/memento) on GitHub is trying to solve exactly this problem — session capture as a first-class artifact, structured so it could travel with the commit rather than evaporating after the terminal closes. It's early, and the UX is rough, but the *concept* is the important part: the session is the work product, and we currently have no version control paradigm for it.

What does the vacuum cost? It depends entirely on context, and that's part of why this hasn't become a crisis yet. For a solo developer shipping a personal project, the session being unlogged is a non-issue. For a team at a HIPAA-covered healthcare company writing logic that processes patient records, the session being unlogged is a quiet time bomb. The question isn't *if* that gets called in — it's whether it gets called in during an audit, a postmortem, or a regulatory investigation, and whether the answer "we don't know what the AI accessed" is acceptable in that moment.

It won't be. Not in financial services. Not in healthcare. Not in safety-critical systems. In regulated industries, "we don't know" is not a data gap — it's a compliance failure.

The algorithmic trading analogy is useful here because practitioners already accept its logic without question: regulated trading systems require session-level audit trails, not just trade logs. The reasoning is obvious — you need to be able to reconstruct the decision context, not just the decision outcome, because the context is where liability lives. AI-assisted coding is about to discover the same reasoning, applied to code. The diff is the trade log. The session is the decision context. Regulators will eventually want both.

What makes this particularly awkward is that the gap isn't theoretical — it's actively being generated right now, in every AI coding session that closes without a session artifact. Teams that are shipping AI-generated code into regulated contexts are making an implicit bet: that no auditor will ever need to reconstruct what the AI accessed, what it rejected, what secrets it touched during the session, or what the developer actually reviewed versus rubber-stamped. That bet is being placed millions of times a day. Most of those bets will pay off. Some won't.

## Two Converging Pressures

Here is where it gets structurally interesting.

The session provenance gap has existed as a developer-niche concern for a while. What's changing is that two external pressures are about to make it a CTO concern — on different timelines, from different directions.

The first is consumer adoption pressure. Claude hitting the top of the App Store isn't just a marketing milestone — it's a regulatory trigger event. Consumer-facing AI creates a different accountability surface than developer-facing AI. When AI assists professional developers on internal tools, the risk is bounded and the affected parties are technically sophisticated. When AI assists consumers on anything that touches financial decisions, health data, or legal documents, the regulatory appetite for provenance records increases dramatically. The same AI session capture question that feels like developer niche governance today is a consumer protection question tomorrow. The App Store chart position is the visible signal; the regulatory timeline acceleration is the operational consequence. Consumer adoption compresses the timeline between "interesting governance question" and "mandatory compliance requirement."

The second pressure is more technically direct: [WebMCP](https://developer.chrome.com/blog/webmcp-epp), now in early preview as a browser extension protocol, extends the Model Context Protocol into the browser context. If you're not tracking MCP, the short version is this: it's the protocol that governs how AI models connect to tools, data sources, and external systems. It's what enables your coding agent to read files, call APIs, and interact with external services in a structured way.

The browser extension is significant for session provenance because it changes where session data lives. When an AI operates in an MCP-connected environment, the session context — what the model accessed, what tools it called, what data it read — is flowing through protocol-layer infrastructure that *does* log things. Just not in your git repository. Just not in any format your audit tooling currently reads. The session is being captured, in a sense — but the capture is happening at the protocol layer, not the version control layer, and those two records are not stitched together in any coherent way.

Think of it like a bank's phone call recording system. The call is being recorded for quality and compliance purposes. The teller's internal notes are in a different system. The account transaction log is in a third system. None of these are automatically linked to reconstruct what happened during a specific customer interaction. That fragmentation is manageable when the stakes are low and audits are rare. It becomes operationally dangerous when a postmortem requires reconstructing exactly what was accessed, what was said, and what decision was made — and the three records are siloed, differently formatted, and owned by different teams.

That's where AI session provenance is heading: not an absence of records, but a fragmentation of records across git, MCP protocol logs, IDE session data, and whatever the AI provider retains. The governance problem isn't "nothing was logged." It's "everything was logged somewhere, by different systems, in incompatible formats, with no join key."

## The Structure of What's Missing

Let me be specific about what the session contains that the diff doesn't.

The diff captures: which lines changed, in which files, at what timestamp, attributed to which committer.

The session captures: what prompt chain produced those changes, what context was injected (files read, APIs called, environment variables accessed), what intermediate suggestions were generated and rejected, what the model's stated reasoning was at each step, what tools were invoked during the session and what they returned, and what ambient authority the agent exercised beyond the final output.

That last item is the one that will matter most in postmortems. "Ambient authority" is the gap between what you intended to grant and what the agent technically had access to during the session. If your coding agent had shell access, it had ambient authority over your filesystem, your environment, and potentially your secrets for the duration of the session. The diff shows you two lines changed. The session audit would show you everything else the agent could have touched and whether it did.

Version control was never designed to capture ambient authority because human developers don't have ambient authority — they have intention. A human developer deciding to change two lines doesn't have a footprint beyond those two lines, modulo any deliberate side effects they chose to introduce. An AI agent with shell access, an open secrets manager, and a forty-minute session window has a much larger footprint than the diff suggests.

## Where This Goes From Here

The Memento project's approach — attaching session artifacts to commits as structured metadata — is one architectural answer. It's the right instinct: make the session a first-class artifact that travels with the diff rather than evaporating. The friction is that it requires developer workflow change at the exact moment when AI coding tools are marketed on reducing friction. Asking teams to add session capture to their commit workflow is asking them to accept a new cost in exchange for a governance benefit they won't feel until something goes wrong.

That's the classic adoption problem for audit tooling. Nobody appreciates it until they need it, and by then it's too late to build the record.

The more likely forcing function isn't developer goodwill — it's regulatory mandate arriving via the consumer adoption route. When AI-assisted professional tools share a compliance category with AI-assisted consumer tools, the governance requirements for the latter tend to propagate to the former. The App Store chart position is the signal that propagation is accelerating.

WebMCP's protocol-layer logging is the other forcing function, arriving from a different direction. If session context is being captured at the MCP layer as a side effect of protocol operation, the tooling question becomes: who builds the join between the protocol log and the version control record? That's a solvable engineering problem — it's essentially a log correlation problem, which is a well-understood category. The tooling will arrive. The question is whether it arrives as an open standard or as a proprietary feature of whichever AI provider controls the protocol.

The honest conclusion is this: the session git never captured was invisible when AI wrote nothing. It becomes an accountability vacuum as AI writes everything. The gap is being generated faster than the tooling is being built to close it. Teams that operate in regulated contexts should treat session capture as an operational requirement today — not because the regulator has mandated it yet, but because the incident postmortem that makes the case for mandating it is already being generated somewhere, in some AI coding session, right now.

The commit message says "add transaction validation logic." The session knows what that actually means. Soon, someone will need to know too.
```