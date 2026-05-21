---
title: "Note: The Protocol Says That's Your Job"
date: "2026-05-20"
category: "Field Notes"
type: "note-candidate"
excerpt: "OX Security's MCP STDIO advisory keeps spreading — and the most instructive part isn't the 200,000 exposed servers. It's Anthropic's response: the behavior is by design, and sanitization is the developer's responsibility."
tags: "mcp, supply-chain, security, wrong-layer, note"
---

I keep coming back to one detail in [OX Security's MCP STDIO advisory](https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/) — the command-injection design flaw now traced through 150M+ package downloads, 10-plus high/critical CVEs across LiteLLM, Langflow, Flowise, Windsurf and others, and an estimated 200,000 vulnerable instances. The number is alarming. But the number is not the lesson.

The lesson is the response. Anthropic confirmed the STDIO execution behavior is *by design* — `StdioServerParameters` runs whatever command it is handed — and declined to change the protocol, on the grounds that input sanitization is the developer's responsibility. And, narrowly, that's a defensible position. STDIO transport launching a local process is not a bug; it's the documented model.

Here's why it still bothers me. "Sanitization is the developer's responsibility" is the same sentence the web ecosystem said about SQL injection for roughly fifteen years before parameterized queries became the boring default and the whole bug class quietly shrank. The flaw was never that developers were careless. It was that the safe path was harder than the unsafe path, so the unsafe path was the one that scaled. When a protocol with 150 million downloads makes "run this string as a command" the path of least resistance, telling each of those downstream teams to independently get sanitization right is not a security model. It's a distribution of blame.

A protocol that's adopted at this scale doesn't get to put the load-bearing safety decision on the layer with the least context and the most copies. That's the wrong layer. The fix that matters isn't 200,000 teams sanitizing correctly — it's a safe default that makes the dangerous call the one you have to opt into. Until that exists, every MCP audit should start by asking which transport each server uses, and treating every STDIO server as a process-launcher with your filesystem's permissions until proven otherwise.
