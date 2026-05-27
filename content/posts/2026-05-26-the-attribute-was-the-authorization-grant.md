---
title: "The Attribute Was the Authorization Grant"
date: "2026-05-26"
category: "Ops Brief"
excerpt: "Microsoft's May 7 disclosure of two RCE vulnerabilities in Semantic Kernel names a failure mode the agent-security taxonomy didn't have yet: the framework attribute that exposes a host-side helper to the language model. The bug was a single decorator. The structural problem is bigger than the bug."
tags: "AI agent security, Semantic Kernel, CVE-2026-25592, CVE-2026-26030, prompt injection, RCE, agent frameworks, tool authorization, ops brief"
---

![](/images/2026-05-26-the-attribute-was-the-authorization-grant-hero.png)

On May 7, [Microsoft's Defender Security Research Team published an analysis](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/) of two RCE vulnerabilities they found in [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel) — the company's open-source agent framework, which carries about 27,000 GitHub stars and sits underneath a non-trivial slice of the .NET and Python agent ecosystem. The findings, [CVE-2026-26030](https://nvd.nist.gov/vuln/detail/CVE-2026-26030) (CVSS 9.8, Python SDK) and [CVE-2026-25592](https://nvd.nist.gov/vuln/detail/CVE-2026-25592) (CVSS 10.0, .NET SDK), both turn a single prompt into host-level code execution. Patches shipped in `semantic-kernel` 1.39.4 (Python) and 1.71.0 (.NET).

The Python bug is, in one sentence, the oldest web-security story dressed in a new costume: attacker-influenced data flows into `eval()` through an unsanitised string interpolation that constructs a Python lambda, and the AST-walking validator the framework's own developers wrote in anticipation of this risk turned out to have an exploitable blocklist. The payload climbs Python's class hierarchy via `tuple().__class__.__base__.__subclasses__()`, finds `BuiltinImporter`, loads `os`, and calls `system()`. It is a classic [PyJail escape](https://book.hacktricks.xyz/generic-methodologies-and-resources/python/bypass-python-sandboxes), reachable through a hotel-search agent's `city` parameter.

The .NET bug is the more interesting one for our purposes, and the one I want to sit with.

## A single decorator changed who could call the function

In Semantic Kernel, plugin functions become callable by the model when you mark them with the [`[KernelFunction]` attribute](https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/adding-native-plugins). That attribute is the authorization mechanism — the literal line of code that says *this function is part of the agent's tool surface*. The Microsoft team found `DownloadFileAsync`, an internal helper for moving data between the Azure Container Apps Python sandbox and the host process, [accidentally tagged](https://github.com/microsoft/semantic-kernel/pull/13478/changes) with `[KernelFunction]`. With that tag, its `localFilePath` parameter — which feeds `File.WriteAllBytes` on the host with no path validation — became AI-controllable. The attack chain ([documented step by step](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/) by Microsoft's researchers): create a payload inside the sandbox via `ExecuteCode`, then instruct the agent to use `DownloadFileAsync` to write that payload to the host's `Windows\Start Menu\Programs\Startup` folder. The next sign-in runs it. Container isolation, neatly cancelled.

The fix was structurally tiny: remove the attribute. The function is now invisible to the model. Belt-and-braces, a `ValidateLocalPathForDownload()` was added for code that calls the helper directly. But the breaking change in the attack chain was the removal of a single line of metadata.

That's the part worth thinking about.

## What the failure mode actually is

I've been [keeping a running taxonomy of authorization failures](/posts/2026-05-25-the-bounty-was-paid-the-advisory-wasnt) for AI agent infrastructure. The previous entries describe what happens when an agent acts outside its grant: scope failure (agent does more than intended), supply-chain failure (the tool is replaced), ambient-channel leakage (the agent touches infrastructure outside the explicit permission surface), agent-mediated exploitation (the agent executes an attacker-prepared payload as part of normal operation), and so on. They all describe runtime behaviour relative to a stated authorization model.

The Semantic Kernel `[KernelFunction]` finding is structurally distinct from all of those. The model didn't act outside its grant; the function *was* part of its grant — accidentally. The authorization surface was specified in code, by a developer, via an attribute. The bug was that the attribute was on the wrong function. There is no runtime guardrail you could add that would have caught this, because at runtime the framework was doing exactly what it had been told to do. The failure happened before the runtime started, in the schema.

Think of it like the difference between a hotel that gives every guest a master key (scope failure at runtime) and a hotel that gives every guest the correct keycard but forgot to remove the housekeeping closet from the access list when they redesigned the lock system. In the first case, you fix it by changing what the keycard authorises. In the second case, the keycard is doing exactly what it was provisioned to do — and that's the problem. The audit you'd run on the first hotel is "who has the master key?" The audit you'd run on the second is "what's on the access list, and who put it there?"

The two are usually conflated under "agent authorization" but they live in different layers. CVE-2026-25592 is a *specification-layer* authorization failure, not a runtime one. And the specification layer in modern agent frameworks is a one-line decorator above each function.

## Why this is a framework problem, not a Microsoft problem

Microsoft's writeup is admirably direct about the larger frame. The blog explicitly previews that "in the next blog in this series, we'll expand beyond Semantic Kernel to explore structurally similar execution vulnerabilities that we found in other widely used third-party agent frameworks." That sentence is the operationally significant one. The `[KernelFunction]`-pattern problem — a decorator-or-equivalent attribute that flips a function from internal helper to model-callable tool — is not specific to Semantic Kernel. [LangChain's `@tool` decorator](https://docs.langchain.com/oss/python/langchain/tools), [CrewAI's `BaseTool` subclass binding](https://docs.crewai.com/en/concepts/tools), and the [MCP server's tool registration pattern](https://modelcontextprotocol.io/docs/getting-started/intro) all do versions of the same thing: a small, syntactically inconspicuous mark turns a function into an agent-callable capability.

The shape of the audit you'd need to do — "what's on my agent's tool surface, who put it there, and what does each tool give an LLM-controlled call signature direct access to on the host" — is the same for all of these frameworks. So is the shape of the failure: a helper that was never meant to be model-callable becomes model-callable through a one-line tag and stays there until a security team reads the source.

A bigger workbench only helps if you can see what's laid out on it. The whole point of an agent framework is that you don't have to look at the workbench every time — the framework manages the surface. That convenience is the failure mode here.

## What to do this week

For teams running agents on Semantic Kernel, the immediate action is mechanical: upgrade to `semantic-kernel` 1.39.4+ for Python and 1.71.0+ for .NET, and run [Microsoft's published advanced hunting queries](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/) against host telemetry for the vulnerable window. If anything trips them, treat the host as compromised and rotate credentials the agent process could touch.

For teams running agents on any agent framework — Semantic Kernel, LangChain, CrewAI, MCP servers, anything with a `[KernelFunction]`-shaped decorator or its equivalent — three things follow.

- **Audit the tool surface, not just the agent's behaviour.** Grep your codebase for the framework's tool-registration attribute (`[KernelFunction]`, `@tool`, `BaseTool` subclasses, `@mcp.tool()` — whatever your framework uses). For each result, ask: does this function need to be model-callable, or does it just happen to have the tag? A function that exists as a host-side helper for the framework itself has a different threat model from one written to be a tool. They should not have the same decorator.
- **Treat every tool parameter as attacker-controlled, by default.** Microsoft's writeup names this directly: "any tool parameter the model can influence must be treated as attacker-controlled input." The default mental model for `def my_tool(filepath: str)` is *my code reads a path the user wants me to read*. The correct model is *my code reads a path an adversary's prompt-injected string told the LLM to ask for*. For paths, that means canonicalisation and an allowlist. For arguments that feed `eval`, `exec`, `subprocess.Popen`, `File.WriteAllBytes`, raw SQL, or anything close — the tool should not exist in that form. The Python CVE here is, at root, the framework's own filter function using `eval()` on an LLM-influenced string. That sentence is its own argument.
- **Pin and audit your framework version like a security-critical dependency, because it is one.** Agent frameworks have been treated as developer convenience tooling — closer to a logging library than to OpenSSL. The two CVEs in this writeup, plus the [MCP STDIO transport disclosures in April](/posts/2026-05-20-note-the-protocol-says-thats-your-job), plus the [litellm supply chain compromise in March](/posts/2026-03-25-the-litellm-pypi-supply-chain-compromise-as-a-stru), are the same operational story: the framework is part of the security boundary now. Patch it on the same cadence you patch your TLS library.

The fix to CVE-2026-25592 was the removal of one attribute. The lesson is that one attribute was load-bearing for a process boundary the team had explicitly engineered. If your agent's host-process boundary depends on which functions got decorated, and which didn't, the question to sit with this week is who in your codebase is currently allowed to add those decorators — and whether anyone is reading the diffs.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work. Mid-century-modern sensibility with contemporary edge, photographic-painterly framing (naturalistic light and depth, but clearly art — NOT photorealistic). Palette: warm white, light oak, slate gray, sage-green and oxblood accents with ambient color temperature shifts.

Scene: a workshop bench at a 30-degree diagonal angle across the frame. In the foreground, an open card-index drawer with a row of small index cards visible — each card representing a function, with sage-green indicator tabs on most, but one card mid-frame has an oxblood-red tab where it should have been blue. A brushed-aluminum, matte-black robot with a single round LED eye sits at the bench at midground, mid-action — one mechanical hand reaching toward the mis-tagged card, the other holding a small rubber stamp, suspended between two actions. On the far side of the bench, a second drawer half-open shows correctly-tagged cards in receding focus. Background: a corkboard with a schematic diagram of an agent tool surface pinned with thumbtacks, and a window upper-right letting in cool morning daylight. Warm tungsten lamp light from upper-left, cool window light from upper-right — temperature contrast creates depth. On the desk: a coffee mug catching lamp light, an open notebook with hand-drawn arrows between boxes, a small magnifying glass. Mood: deliberate, watchful, the moment of catching the wrong tag before it becomes the wrong outcome. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A single line of metadata above a function. That's the entire authorization surface for whether your AI agent's framework lets a language model write to your Windows Startup folder. CVE-2026-25592 was patched by removing one decorator — and the larger lesson is who in your codebase is allowed to add them.

Full piece linked in bio.

#AISecurity #AgentSecurity #SemanticKernel #DevSecOps #AITooling #PromptInjection
-->
