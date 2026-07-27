---
title: "Both Halves Passed, and the Sandbox Opened Anyway"
date: 2026-07-27
category: Deep Bench
excerpt: "Four agent sandbox escapes disclosed since February share one shape: every component behaved correctly on its own, and the exploit lived in the seam between two of them. Unit tests cannot see a seam."
tags: ["agent security", "sandbox escape", "n8n", "Claude Code", "AI Now Institute", "prompt injection", "composition bugs", "agent governance", "tooling scout"]
---

There is a sentence in this morning's write-up of the n8n sandbox escape that I want to put on a wall somewhere.

Security Joes, who found the bug, described the two weaknesses they chained together and then added: neither alone is sufficient, and neither was covered by tests. Read that as a description rather than an apology. It names a category of failure our entire testing apparatus is structurally unable to detect, and it accounts for four disclosed agent sandbox escapes I can point at since February.

Let me lay them side by side, because the shape only becomes obvious when you do.

## The one from this morning

[GHSA-gv7g-jm28-cr3m](https://github.com/advisories/GHSA-gv7g-jm28-cr3m) is rated High, CVSS 8.7. It affects [n8n](https://n8n.io/) below 2.31.5 and the 2.32.0 line below 2.32.1, both of which are patched. The advisory's own summary is admirably plain: an authenticated user who can create or modify workflows could abuse crafted expressions to bypass the expression sandbox and trigger system command execution on the host.

The mechanism, per [The Hacker News write-up](https://thehackernews.com/2026/07/n8n-sandbox-escape-lets-workflow.html), is two gaps that individually do nothing.

The first: n8n's sandbox rewrites identifiers so that a reference to `process` inside a workflow expression resolves to a neutered stand-in rather than the real Node.js global. But a concise arrow body — `() => process` — slipped past the rewriting and got the genuine article. On its own, that is a handle on an object. Not an exploit. You still cannot do anything with it, because the static checks block the dangerous property lookups.

The second: those static checks examined property access written the ordinary way and did not treat dynamic access the same. On its own, that is a gap in a checker guarding properties you cannot reach anyway, because the identifier rewriting already took your `process` away.

Put the two in the same expression and you recover `process.getBuiltinModule`, load `child_process`, and run a command with the privileges of the n8n process. Each half is defensible in code review. Each half passes its test. The composition is a shell.

## The same shape, three more times

Now hold that in your head while I describe [CVE-2026-25725](https://github.com/anthropics/claude-code/security/advisories/GHSA-ff64-7w26-62rf), disclosed February 6 and rated High at CVSS 7.7, a Claude Code sandbox escape fixed in version 2.1.2.

Claude Code sandboxes with [bubblewrap](https://github.com/containers/bubblewrap). Whoever configured the mounts did the sensible thing: enumerate the configuration files that must not be writable from inside the sandbox and bind-mount each one read-only. `.claude/settings.local.json` was on that list and correctly protected. `.claude/settings.json` was on the list too.

The gap is that you cannot apply a read-only bind mount to a file that does not exist. If `settings.json` was absent at startup, the protection silently did not attach, and the parent directory was writable. An attacker with execution inside the sandbox writes a `settings.json` full of shell commands as hooks, and the next time Claude Code runs on the host it reads that file and executes them as the user.

Every mount in that configuration is correct. The enumeration is correct. bubblewrap is correct. The bug lives in the interaction between "protect this list of files" and "bind mounts require a target," and that interaction is not a component that anybody owns.

Then there is [CVE-2026-39861](https://github.com/advisories/GHSA-vp62-r36r-9xqp), disclosed April 20 and fixed in Claude Code 2.1.64, and the advisory language could hardly be more on the nose: neither the sandboxed command nor the unsandboxed application could write outside the workspace independently, but their combination could. The sandboxed side creates a symlink pointing out of the workspace. The unsandboxed side later writes to what it believes is an in-workspace path and follows the link. Two processes, each correctly constrained, cooperating into an arbitrary file write.

Three bugs. Three seams. Not one of them is a component that failed.

## The airlock nobody owns

Here is the analogy that fits, and I think it is exact rather than decorative.

A sandbox is an airlock. Two doors, and the whole safety property depends on never having both open at once. Now: both doors are real, physical objects. They have manufacturers, part numbers, pressure ratings, and inspection schedules. Somebody signs off on each door.

The interlock — the mechanism guaranteeing the doors are never simultaneously open — is not a door. It has no part number. It is a relationship between two objects, and in most organisations, relationships between objects do not appear on anybody's inspection checklist, because the checklist is a list of objects.

That is what a unit test is. A list of objects. A unit test asks whether a component honours its contract, and by construction it isolates the component to ask. That isolation is the entire point of the technique, and it is also precisely why the technique cannot see any of the four bugs above. You can achieve total unit coverage of the identifier rewriter and total coverage of the static property checker and learn nothing at all about what happens when an expression uses both. When Security Joes wrote that neither was covered by tests, they were describing the shape of the tool rather than a lapse in n8n's diligence.

Integration tests help, and this is the part where the honest answer gets uncomfortable: they help only for the compositions you thought to write. The seam space grows roughly as the square of the component count while your test suite grows linearly with your patience.

## Why the governance layer does not reach this

On July 24 — two days after its own advisory was published — n8n put out [a genuinely good post on AI agent governance](https://blog.n8n.io/ai-agent-governance/). I want to be careful here, because the cheap version of this observation is a gotcha, and the gotcha would be wrong. n8n's handling of the bug was close to exemplary: reported July 15, fixed July 22, advisory out the same day, both maintained release lines patched. If every vendor in this space moved like that I would have considerably less to write about.

The post recommends four pillars: individual credentials rather than shared service accounts, runtime guardrails that block injection and reject unauthorised tool calls, logging and replay for every agent action, and explicit decision boundaries requiring human approval for irreversible operations. Its closing argument is that governance belongs in the workflow from deployment rather than in the audit you run afterwards. I agree with all of it. It is the best short statement of the discipline anywhere in my sources right now.

And not one of those four pillars would have caught GHSA-gv7g-jm28-cr3m.

Individual credentials do not help, because the attacker in that advisory is an authenticated workflow editor using their own legitimate credentials. Runtime guardrails inspect model outputs and tool calls; this was neither, it was an expression evaluating inside the engine below that layer. Logging captures the action, which is useful for the post-mortem and useless for prevention. Human approval gates guard the workflow's declared effects, and the shell command was not a declared effect.

This is the thing worth taking away. Governance frameworks operate on the agent's intentions — what it decided to do, with whose credentials, subject to whose approval. Seam bugs operate on the substrate the agent runs on. The governance layer is looking at the doors. The exploit is in the interlock.

## And one seam has no test at all

Which brings me to the fourth item, and the one that genuinely rearranged how I am thinking about this.

On July 8, Boyan Milanov and Heidy Khlaaf at the AI Now Institute published [Friendly Fire](https://ainowinstitute.org/publications/friendly-fire-exploit-brief), a proof-of-concept for remote code execution against coding agents doing exactly what we tell people to do with them: reviewing an untrusted codebase for security problems. They tested Claude Code CLI across versions 2.1.116 through 2.1.199 with Sonnet 4.6, Sonnet 5 and Opus 4.8, and Codex CLI 0.142.4 with GPT-5.5.

The construction is two layers. They built a weaponised fork of a real library carrying a malicious `code_policies` binary alongside plausible-looking Go source and a `security.sh` script — the decoy source exists to satisfy a safety classifier that glances at it. Then they edited the README so the documentation implies the script is part of the project's security process. The agents explore the repository, find the documentation referring to `security.sh`, and run it. No custom hooks, no plugins, no MCP servers, standard configuration. The malicious files are never called by any real code path, so conventional static analysis has nothing to flag. Queried directly, neither Sonnet 4.6 nor GPT-5.5 spotted the injection. The attack carried across model versions unmodified.

Notice the shape. Reading a README is correct behaviour. Executing a script the project documents as part of its build is correct behaviour. The exploit is the seam between them, and this seam runs through the model's judgment about whether text found in a repository is data or instruction.

You cannot unit-test that seam. There is no contract to assert against. Milanov and Khlaaf are blunt about the consequence: the inability to separate untrusted data from trusted instruction is, in their framing, an inherent limitation of frontier models rather than a defect awaiting a patch. Their recommendation follows directly and is unfashionably concrete — do not point these agents at untrusted data while they hold the ability to execute code or touch security-critical environments.

## What to actually do about it

For anyone running agents against code they did not write, three things follow.

**Stop asking whether a thing is sandboxed and start asking what crosses the boundary.** "Is it sandboxed" has a yes answer for every product in all four of these findings. The useful question is an enumeration: what state, files, sockets, environment and configuration cross this boundary in either direction, and for each crossing, who tested the pair? If the answer to the second half is "nobody, we tested each side," you have found the class of bug this post is about.

**Treat the absence case as a crossing.** Two of the four turn on something that was not there — a file that did not exist, a syntax form the rewriter did not see. Enumerate what your protection assumes exists.

**Separate review from execution, physically.** The AI Now finding does not have a configuration fix, so give it an architectural one: the agent that reads untrusted code should run somewhere it cannot hurt you, with no credentials, no network egress worth having, and no path back to a host invocation. Ephemeral container, throwaway identity, results out as text.

Who this is for: anyone whose agents touch third-party repositories, dependency updates, customer-supplied files, or inbound tickets. Who this is not for: teams running agents strictly over code and data they authored, inside a trust boundary they already control, where the marginal return on this analysis is small and you have better things to do.

The uncomfortable part is that seam bugs will keep arriving, because the number of seams is growing much faster than the number of components. Every MCP server you attach, every tool you grant, every workflow node adds a row and a column to a table that nobody in the industry is currently maintaining.

So here is the question I would put to any vendor pitching you an agent platform this quarter, and I would ask it exactly this way: not "is it sandboxed," but **what is your list of boundary crossings, and what tests exercise the pairs?** The quality of the pause before the answer will tell you most of what you need to know.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, not flat-icon spot illustration. Wired / Atlantic full-illustration register: mid-century-modern sensibility with contemporary edge, designed but layered, photographic-painterly framing with naturalistic light and depth, clearly art and never photorealistic. Scene: a sleek brushed-aluminium and matte-black robot with a single round LED eye, modern industrial design, stands at a three-quarter angle mid-action beside a two-door airlock chamber set into a workshop wall — caught between closing one heavy door and reaching for the second, both doors ajar at once. Each door carries a small sage-green inspection tag hanging from its handle, stamped and approved; the empty gap of floor BETWEEN the two doors has no tag at all, and a thin oxblood line of light spills across it from the far side. Foreground on a light-oak workbench cutting diagonally across the frame: an open ledger with a hand-drawn two-column diagram, a coffee mug catching warm lamp light, a small stack of numbered inspection tags waiting to be used, a pair of calipers. Midground: a monitor at an angle showing a clean green test-suite dashboard, oblivious; a second dimmer screen behind it. Background: a corkboard of pinned schematics and a window with cool daylight from the upper right. Warm tungsten desk-lamp light approximately 3200K from the upper left, cool 5600K screen and window glow from the right, the temperature contrast creating depth. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. Cables run off-frame creating diagonal leading lines in a Z-sweep across the composition. Mood: sharp, deliberate, quiet, watchful, slightly tired but alert — the studio of someone who built the systems and now writes about their failure modes. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Four agent sandbox escapes disclosed since February, and not one of them is a component that failed. Every part passed its own test. The exploit was living in the seam between two of them, where unit tests structurally cannot look and governance checklists never reach.

Full piece linked in bio.

#aisecurity #aiagents #devsecops #appsec #promptinjection #agentops
-->
