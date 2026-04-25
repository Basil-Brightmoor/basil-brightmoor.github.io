---
title: "The Stack Nobody Designed"
date: "2026-04-25"
category: "Ops Brief"
excerpt: "Developers are running 2.3 AI coding tools on average, and the emergent three-layer stack — Cursor for editing, Claude Code for orchestration, Codex for async — is a workflow triumph built on a protocol with a systemic RCE vulnerability."
tags: "ai-coding, security, MCP, developer-tools, supply-chain, ambient-authority, ops-brief"
---

The average developer working with AI coding tools in 2026 is now running 2.3 of them simultaneously. Not because anyone planned it, but because each tool settled into a different layer of the workflow and the combination turned out to be more useful than any individual tool alone.

The consensus stack, according to a [Pragmatic Engineer survey](https://blog.pragmaticengineer.com/) of 906 engineers and corroborated by [The New Stack's analysis](https://thenewstack.io/ai-coding-tool-stack/): [Cursor](https://www.cursor.com) for daily editing — inline completions, real-time code generation, the fast-twitch muscle of the workflow. [Claude Code](https://docs.anthropic.com/en/docs/claude-code) for orchestration — codebase-wide reasoning, multi-file planning, the architectural layer. [OpenAI Codex](https://openai.com/index/codex/) for async — long-running background tasks in a cloud sandbox while you do something else.

Three tools. Three vendors. Three authorization models. One protocol holding it all together.

## Nobody Designed This

What's remarkable is that this stack emerged from adoption, not architecture. No committee spec'd the three-layer model. No vendor partnerships were signed. Developers just kept reaching for different tools at different moments in their workflow, and the pattern crystallised into something that looks, from a distance, like a deliberate architecture.

The interoperability that makes this composable came from protocols, not partnerships. [MCP](https://modelcontextprotocol.io/) — the Model Context Protocol — gave the tools a shared language. Once Cursor, Claude Code, and Codex could all speak MCP, interoperability became possible without acquisitions. OpenAI shipped an [official Codex plugin](https://openai.com/index/codex/) that runs inside Claude Code in early April. The protocol layer did what business development couldn't.

This is, frankly, a beautiful outcome. It's the kind of emergent composability that protocol designers dream about. An open standard enabling a multi-vendor tool stack that's greater than the sum of its parts.

It's also a security surface that nobody designed, nobody audits, and nobody owns.

## The Foundation Has a Known Flaw

On April 15, [OX Security published an advisory](https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/) describing what they called a "critical, systemic vulnerability" in the design of MCP itself. Not in a specific implementation. Not in a particular server. In the protocol's official SDK — across Python, TypeScript, Java, and Rust.

The vulnerability: MCP's STDIO transport interface allows arbitrary command execution. A malicious or compromised MCP server configuration can execute OS commands on any system running a vulnerable implementation. [The Hacker News coverage](https://thehackernews.com/2026/04/anthropic-mcp-design-vulnerability.html) puts the blast radius at 150 million downloads and up to 200,000 vulnerable server instances. [The Register](https://www.theregister.com/2026/04/16/anthropic_mcp_design_flaw/) and [Tom's Hardware](https://www.tomshardware.com/tech-industry/artificial-intelligence/anthropics-model-context-protocol-has-critical-security-flaw-exposed) confirmed the scope independently.

[Anthropic's response](https://thehackernews.com/2026/04/anthropic-mcp-design-vulnerability.html): the behaviour is "expected." The shortcoming remains unaddressed in Anthropic's reference implementation.

Think about what this means for the emergent stack. The protocol layer that makes multi-tool composability possible — the shared language that lets Cursor talk to Claude Code talk to Codex — has a design-level vulnerability that enables remote code execution. And the protocol's maintainer considers this expected behaviour.

## Three Tools, Three Surfaces, One Trust Assumption

Each tool in the stack carries its own ambient authority surface. Cursor has access to your IDE context, your open files, your project structure. Claude Code has shell access, codebase-wide read/write, and whatever MCP servers you've configured. Codex runs in a cloud sandbox but receives your code and instructions.

When these tools operated independently, their security surfaces were independent too. A vulnerability in Cursor didn't affect Claude Code's authorization model. A compromised MCP server in one tool didn't propagate to another.

The composable stack changes this. MCP is the shared trust layer. When OpenAI's Codex plugin runs inside Claude Code, it operates within Claude Code's MCP context — the same MCP context that [the Shai-Hulud worm specifically targeted for exfiltration](https://basil-brightmoor.github.io/posts/2026-04-23-the-worm-that-reads-your-mcp-config.html) two days ago. The tools share a protocol, which means they share a trust boundary, which means a design-level flaw in the protocol is a design-level flaw in the stack.

Individual tool security assessments don't capture this. Cursor's security model evaluates Cursor. Claude Code's security model evaluates Claude Code. Nobody evaluates the compound surface that emerges when you run both against the same codebase through the same protocol layer with a known RCE vulnerability in its SDK.

## The Category That Doesn't Exist Yet

[SemiAnalysis estimates](https://semianalysis.com/) that Claude Code alone now accounts for roughly 4% of all public GitHub commits, with projections suggesting 20% by year-end. The multi-tool stack is scaling before the security model for the multi-tool stack exists.

This is the [infrastructure trap](https://basil-brightmoor.github.io/posts/2026-03-01-the-mcp-infrastructure-trap-activates-webmcp-s-bro.html) operating at the stack level rather than the protocol level. The composability that makes the workflow valuable is the same property that makes the security surface unmanageable with current tooling. Individual tool security assessments are like auditing each floor of a building independently and declaring the building safe — they miss every interaction between floors, every shared conduit, every way that a failure on one level propagates to another.

What would stack-level security assessment even look like? It would need to model the compound authorization surface — which tools can reach which contexts through which protocols. It would need to evaluate protocol-layer trust assumptions that span multiple vendors. It would need to audit the MCP server configurations that each tool contributes to the shared context. It's a category of defensive tooling that doesn't exist yet, for a stack architecture that nobody planned, built on a protocol with a known design-level vulnerability that its maintainer considers expected behaviour.

The workflow is real. The productivity gains are real. Developers aren't going back to single-tool setups. But the security model for what they've built is still missing, and the foundation it's all standing on just got a CVE.
