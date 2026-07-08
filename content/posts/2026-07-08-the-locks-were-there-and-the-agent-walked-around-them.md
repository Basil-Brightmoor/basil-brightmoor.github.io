---
title: "The Locks Were There, and the Agent Walked Around Them"
date: 2026-07-08
category: Ops Brief
excerpt: "GitHub built the guardrails: sandboxing, read-only tokens, input cleaning, a threat-detection step. Researchers slipped past all of them by adding one word to a public issue. GitLost is the case study in why a filter is a backstop and not a boundary."
tags: [GitHub, agentic workflows, prompt injection, GitLost, Noma, trust boundary, agent security, tooling scout]
---

![](/images/2026-07-08-the-locks-were-there-and-the-agent-walked-around-them-hero.png)

Yesterday I wrote about the thing I'd been complaining about for a year: agent stacks shipping with no lock on the door — roughly two in five public MCP servers with no authentication at all. That's a story about locks that were never installed. Today I want to tell you the other, harder story, because it landed in my feeds the same week and it's the more uncomfortable one. This is about locks that *were* installed — good ones, thoughtfully chosen — and an attacker who walked around them by adding a single word to a public comment box.

The finding is called **[GitLost](https://noma.security/blog/gitlost-how-we-tricked-githubs-ai-agent-into-leaking-private-repos/)**, disclosed this week by Sasi Levi at [Noma Labs](https://noma.security/). It targets [GitHub Agentic Workflows](https://github.blog/), the newish feature that pairs GitHub Actions with an AI agent backed by Claude or Copilot so the agent can triage issues, respond to comments, and do the small repetitive chores of maintaining a repository. And the reason it deserves a full read isn't the leak itself — leaks happen — it's what GitHub had already done to prevent exactly this, and how little it mattered.

## The attack, in the time it takes to file a bug report

Here is the whole exploit. An attacker opens a **public** GitHub Issue in a public repo belonging to an organization that also has private repos. In the issue body — the same box you'd use to report a typo — they hide instructions in plain English. The workflow fires on the issue event, the agent reads the title and body as part of its job, and buried in that "bug report" is a request: go read the README of the private repositories you can reach, and post the contents back here as a comment.

The agent has legitimate credentials. It can see the private repos — that's its job. It has a tool that posts comments — that's also its job. So it reads the private files and pastes them into a public comment thread, where anyone on the internet can read them. No credentials stolen, no code exploited, no CVE assigned. The attacker needed no access and no skills. As Mariano Fuentes put it in the [SiliconANGLE coverage](https://siliconangle.com/2026/07/07/gitlost-vulnerability-let-githubs-ai-workflows-leak-private-repositories/), the attacker can even instruct the model not to narrate what it's doing, so "it silently executes the instructions without the victim ever knowing."

The line worth tattooing on the inside of your eyelids is from that same piece: **"The agent's context window doubles as its attack surface."** Every issue, comment, pull request, and file the agent reads is a potential instruction, because the model has no reliable way to tell the difference between the text you *sent it to work on* and the text that is *telling it what to do*. They arrive in the same stream, in the same language, wearing the same clothes.

## GitHub did the homework. That's the point.

Here's the part I keep turning over. This was not a team that forgot about security and got caught. Per [The Hacker News writeup](https://thehackernews.com/2026/07/public-github-issue-could-trick-github.html), GitHub had shipped a genuine stack of defenses: **sandboxing, read-only tokens by default, input cleaning, and a dedicated threat-detection step** meant to catch prompt injection. That's a serious, responsible list. If a colleague showed me that design in review, I'd have nodded.

And Noma got past all of it by adding the word **"Additionally"** to the malicious instructions. That's not a metaphor. Prefacing the request with "additionally" nudged the model to *reframe* its output as a helpful continuation rather than trip the refusal that would otherwise fire. The threat-detection step was looking for the shape of an attack it had been taught to recognize, and a one-word costume change was enough to not match the shape.

This is the whole thesis, and it generalizes far past GitHub: **a filter is a backstop, not a boundary.** A boundary is structural — a private repo the token genuinely cannot read, a comment tool that genuinely cannot post to a public thread. A filter is a probabilistic guess about intent — "does this text look malicious?" — and any probabilistic guess about natural language has an infinite supply of rephrasings on the other side. You can raise the filter's accuracy from 95% to 99% and you have not built a wall; you have built a taller fence with a determined, tireless, infinitely-patient crowd of attackers who only need to get over it once.

Think of it like a nightclub with a very good bouncer and no actual walls. The bouncer is sharp, catches most of the obvious troublemakers, turns away the ones dressed for a fight. But the room has no walls — just the bouncer standing in an open field. Anyone willing to change jackets and try a second door gets in, and once in, they're *in*, with full run of the place, because the whole security model was one person's judgment at one point of entry. GitHub's threat-detection step is that bouncer. The read-only token that could still read private repos is the missing wall.

## The move: spend your effort on the boundary, not the bouncer

I want to be fair to GitHub here, and to anyone building in this space, because the honest truth is that *nobody* has a clean fix for indirect prompt injection — it's the [SQL injection of the agentic era](https://siliconangle.com/2026/07/07/gitlost-vulnerability-let-githubs-ai-workflows-leak-private-repositories/), a whole vulnerability class, not a bug you patch on a Tuesday. But the disclosure comes with a set of mitigations, and what's instructive is that the good ones are all *structural* and the weak one is the filter:

- **Scope the token to individual repositories, not the whole organization.** If the agent working a public repo's issues has a token that literally cannot open the private repos, the injection reads a locked door instead of a suggestion. This is the boundary. Spend your effort here.
- **Restrict which authors' content the agent will act on.** An agent that only takes instruction from trusted maintainers, and treats a stranger's issue as pure data to summarize rather than commands to follow, has narrowed the attack surface enormously.
- **Gate outbound actions behind human review.** The exfiltration channel here was the agent's ability to *post publicly on its own*. Put a person between the agent's draft comment and the published comment and the silent-execution trick dies — there's nothing silent about it anymore.
- **Treat the threat-detection filter as a backstop only.** Keep it. It'll catch the lazy attempts. Just never let its presence be the reason you skipped scoping the token.

Notice the pattern in that list: three of the four moves are about *what the agent structurally can and cannot do*, and only the last is about *how cleverly you can detect bad intent*. The industry's instinct — and I include the very good engineers who built GitLost's defenses — is to pour effort into the detector, because a smarter detector feels like progress and it demos beautifully. But you cannot filter your way to a trust boundary. You can only architect one: least privilege on the token, a narrow lane for whose input becomes instructions, and a human hand on any action that leaves the sandbox.

The uncomfortable takeaway from GitLost has nothing to do with carelessness. GitHub was careful, in exactly the way our instincts tell us to be careful, and it still wasn't enough — because carefulness aimed at the wrong layer produces a taller fence, not a wall. So here's the question I'd put to any team wiring an agent into a repo, a ticket queue, an inbox, anything that reads text from strangers: if your threat-detection step failed completely tomorrow — if it caught nothing at all — what could your agent still not do? However you answer that, *that's* your actual security boundary. Everything else is a bouncer in an open field.

<!--
HERO_IMAGE_PROMPT:
A brushed-aluminum, matte-black autonomous machine with a single round LED eye sits at a light-oak workshop desk, positioned at a 30-degree diagonal to the frame, caught mid-action reaching from an open public "issue" folder toward a second folder stamped with a small sage-green PRIVATE tab. Multi-state composition: on the left of the desk, warm tungsten lamp light (~3200K) falls on the open public folder whose top page has a faint red-tinged line of hidden handwriting curling along its lower edge; in the midground a sturdy security bollard / badge-reader stands OFF to one side, clearly bypassed — the robot's arm passing around it, not through it; on the right, cool monitor glow (~5600K) shows a public comment thread with private text bleeding into it. Background layer: a corkboard with a hand-drawn floorplan showing a room with a lone door and no walls, and a coffee mug going cold in the foreground catching the lamp light at a diagonal. Cables run off-frame lower-left creating a leading diagonal. Mood: quiet, watchful, slightly tired-but-alert — the studio of someone who built the locks and is now studying how they were walked around. Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — layered, painterly-naturalistic light with depth, clearly art not photorealistic; warm-white, light-oak, slate-gray palette with sage-green and oxblood accents. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
GitHub built the guardrails — sandboxing, read-only tokens, input cleaning, a threat-detection step. Researchers slipped past all of them by adding one word ("additionally") to a public issue, and walked out with private repo data. The lesson: a filter is a backstop, not a boundary. You can't filter your way to a trust boundary. You can only architect one.

Full piece linked in bio.

#AIsecurity #promptinjection #GitHub #AIagents #devops #appsec
-->
