---
title: "The notebook outranked the operator and nobody had run a cell"
date: 2026-08-25
category: "Ops Brief"
excerpt: "marimo promises that nothing executes until you run a cell. CVE-2026-75149 spawns a subprocess when you open the file. The promise held, because what ran was configuration rather than code."
tags: ["ai-agents", "mcp", "supply-chain", "configuration", "trust-boundaries", "cve", "developer-tooling", "ops"]
---

![](/images/2026-08-25-the-notebook-outranked-the-operator-and-nobody-had-run-a-cell-hero.png)

[marimo](https://marimo.io/) says something admirably specific in its [security documentation](https://docs.marimo.io/security/): "When you open a notebook, marimo assumes you might not trust its contents until you explicitly choose to run it." Edit mode sanitizes what it renders until the first cell runs. The overarching principle, stated in marimo's own words, is that no user code is executed without explicit user action.

Then read [CVE-2026-75149](https://nvd.nist.gov/vuln/detail/CVE-2026-75149), published 19 August by [VulnCheck](https://vulncheck.com/) and scored 8.8 on CVSS v3.1, 8.7 on v4. A crafted [MCP](https://modelcontextprotocol.io/) server entry embedded in a notebook, carrying an attacker-controlled command value, runs as a local subprocess when the file is opened in edit mode. Nobody clicked anything. No cell has run.

Both statements are true at once, and the reason they are both true is the interesting part. The documented promise is about **user code**. What executed was **configuration**.

## The bug is a precedence order, not a parser

The fix is [pull request #10281](https://github.com/marimo-team/marimo/pull/10281), merged 23 July and shipped in 0.23.15. Its title is modest — "additional pep 723 sanitization" — and its description contains the sentence that actually explains the vulnerability:

> Notebook (PEP 723) metadata embedded in a .py file is attacker-controllable and is merged with the highest precedence over the operator's own user config.

[PEP 723](https://peps.python.org/pep-0723/) is the inline script metadata standard: a commented TOML block at the top of a single-file Python script declaring what it needs to run. Tools are invited to read a `[tool.*]` table out of it, which is how a marimo notebook can carry its own settings in the same file as its cells. Handy, portable, exactly the sort of thing that makes single-file tooling pleasant.

Read that sentence again, though, because the vulnerability is the second clause rather than the first. Everyone already knew the file was attacker-controllable — it is a file, it came from somewhere. The defect is that it **won**. Not merged as a suggestion, not applied where the operator had left a gap. Highest precedence.

That precedence order was correct for a long time, and it was correct for a good reason: a notebook knows better than your global settings what column width its own dataframes want, what its own cells should look like formatted. Deferring to the file is the right default when the file can only decide cosmetics.

The config schema then grew. It grew an `ai` section, because notebooks got model integrations. It grew `secrets`, because notebooks needed credentials. It grew `mcp`, because notebooks got agent tooling, and an MCP stdio server entry is by construction a program name plus an argument vector. Every one of those additions is reasonable in isolation. Not one of them was accompanied by anybody re-deriving whether "the file wins" was still the right answer, because precedence had been settled years earlier and settled questions do not get re-opened by a feature PR.

## The half that isn't being reported

Most coverage — [The Hacker News](https://thehackernews.com/2026/08/marimo-notebook-flaw-could-run-mcp.html) included — leads with the MCP subprocess, which is fair enough, since arbitrary command execution is the loudest thing in the advisory. The PR blocks a longer list, and the rest of it is quieter and in some ways worse:

- `ai`, specifically `ai.open_ai.base_url`
- `completion`, including its `api_key` and `base_url`
- `mcp`
- `secrets`
- `package_management`
- `server`
- `runtime`, specifically `auto_instantiate`
- `experimental.isolate_apps`

Look at `ai.open_ai.base_url` for a moment. A notebook you opened, and did not run, could rewrite where your assistant's requests go. The PR names the consequence plainly: the operator's API keys walk out to whatever endpoint the file nominated. No subprocess, no shell, no alarm. Your own tool, working correctly, delivering your credentials to a hostname the document chose.

This is the mail-forwarding card of software security. Redirecting someone's post does not require breaking into their house, defeating a lock, or being present at all. It requires one low-friction form that outranks everything the building otherwise knows about where that person lives. `base_url` is that form. It is a single string, it looks like a preference, and it silently re-points every subsequent request the tool makes.

`runtime.auto_instantiate` deserves a second glance too. marimo documents a runtime setting governing "whether marimo notebooks opened with `marimo edit` automatically run on startup." A notebook supplying its own startup-execution setting is the sanitization promise eating itself.

## Why the boundary missed it

marimo's trust model is drawn well and drawn in the wrong place. Edit mode sanitizes *content*. Run mode trusts *content*. The distinction the documentation makes is between two modes of handling the executable material in the file.

Configuration is read strictly earlier than that. It is read in order to build the environment the sanitizer will run inside. So the boundary is real, it is enforced, and the config block is on the far side of it purely by arriving first — the way a security guard checks everyone entering the lobby while the building's fire panel is wired by whoever delivered it.

This is the same shape as the agent-tooling failures I keep coming back to: [an attribute that turned out to be an authorization grant](/posts/2026-05-26-the-attribute-was-the-authorization-grant), [an agent reading its instructions off the artifact it was sent to inspect](/posts/2026-08-04-the-bomb-disposal-robot-reads-its-orders-off-the-bomb). Every instance has a component whose inputs were once inert data and are now, because of a feature added later, an instruction surface. The security model does not update itself when the data format grows teeth.

marimo has had a hard year here. [CVE-2026-39987](https://github.com/marimo-team/marimo/security/advisories/GHSA-2679-6mx9-h9xc), published in April, was an unauthenticated terminal WebSocket handing out a full PTY shell, and [Sysdig clocked it](https://www.sysdig.com/blog/marimo-oss-python-notebook-rce-from-disclosure-to-exploitation-in-under-10-hours) at nine hours and forty-one minutes from advisory to first exploitation attempt — one of the three comparison points in [what I wrote in May about the collapsing patch window](/posts/2026-05-27-the-window-closed-to-four-hours). That one was a missing `validate_auth()` call, which is carelessness of an ordinary kind. This one is different in origin. This is what happens when a config system designed honestly acquires dangerous keys one merge at a time.

## The fix is the artifact worth stealing

The patch does not add validation to the `mcp` section. It does not sanitize the command string. It inverts the default.

Where notebook-supplied metadata previously applied unless someone had thought to exclude it, it now applies only if it appears on an explicit allowlist. The allowlist, per the PR, is: formatting, save, display, keymap, diagnostics, lint, snippets, datasources.

Read that list as prose and it says: **a stranger's file may decide how it looks and nothing else.** That is a written, checkable, one-line definition of what a document is permitted to change about the machine reading it, and it is the most portable thing to come out of this advisory. Any tool that reads settings out of a file it did not write can adopt that sentence today.

The distinction matters because a denylist here is unmaintainable in a specific way: the danger arrives with *new features*, and a denylist is only ever as current as the last person who remembered to update it while shipping something else. An allowlist of cosmetics fails closed on every future addition. Add a `payments` section next year and forget the security review, and it simply does not apply from an untrusted file, because nobody put it on the list.

## Who should act on this, and who shouldn't

**Upgrade to 0.23.15 or later if you run marimo at all.** The reporter, Grg0rry, also appears as a co-author on the hardening commits; the patch is clean and there is nothing here to weigh. If your team opens notebooks that arrived from anywhere other than your own repository — a client, a Slack thread, a public gist, an agent that generated one — treat that as the exposed path.

**The wider audit is for anyone whose repositories carry agent configuration**, which is now most of them. The question to ask is not "do we trust this repo." It is: *when someone on this team clones a branch and opens it in their editor, which files get read as settings before anything runs, and can any of those files name a command or a URL?* MCP server manifests, editor workspace settings, container definitions, agent instruction files — all of them ride along with a clone, all of them are read early, and several of them can nominate an executable. marimo is the instance that got a CVE number this month. The shape is not specific to notebooks.

**This is not an argument against file-local configuration**, and I want to be careful there, because the reflex response to an advisory like this is to strip a genuinely good feature. Portable per-project settings are why single-file tooling works. The defect was never that the notebook could carry configuration. It was that the notebook could carry configuration *that outranked the human running it*.

The question I would like a tool vendor to answer next: has anyone published the equivalent allowlist for the config their agent reads out of a cloned repository — a written list of the sections a stranger's checkout may set, with everything else refused by default? marimo now has one, arrived at the expensive way. It is eight words long and it took a CVSS 8.8 to write it down.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, not the flat-icon spot illustration. Photographic-painterly framing, naturalistic light and depth, clearly art and never photorealistic. A brushed-aluminum and matte-black robot with a single round LED eye, modern industrial design, sits at a light-oak workshop desk angled diagonally across the frame, caught mid-action: one hand still resting on a closed laptop lid it has only just opened, the other hand frozen halfway toward a keyboard it has not yet touched. On the primary monitor to the right, a document is displayed with its top few lines glowing a faint oxblood red while the body text below sits calm and grey — the header has already done something the body has not. Behind it, a second smaller screen at greater depth shows a soft sage-green terminal where a process has quietly spawned, its cursor blinking, unwatched. Midground: a stack of loose papers with a hand-drawn precedence diagram, arrows pointing upward from a small sheet to a large ledger — the small one on top. Foreground left: a coffee mug catching warm tungsten desk-lamp light at 3200K from the upper-left, an open notebook with a sketched checklist, and a small potted plant. Background: a window with cool 5600K morning daylight from the upper-right, and a corkboard with pinned index cards receding into soft focus. The warm lamp and the cool window create clear temperature contrast across the frame. Palette: warm white, light oak, slate gray, with sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful, slightly tired-but-alert — the studio of someone who built the systems and now writes about their failure modes. Cables run off the lower-right edge creating diagonal leading lines that sweep the eye across the composition. Six to eight distinct objects, populated rather than cluttered. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
marimo's docs promise nothing runs until you run a cell. A new CVE spawns a subprocess the moment you open the file, and the promise still held, because nothing that executed was code. It was a config key. The fix is one sentence worth stealing: a stranger's file may decide how it looks and nothing else.

Full piece linked in bio.

#aisecurity #devtools #mcp #supplychainsecurity #aiagents #devops
-->
