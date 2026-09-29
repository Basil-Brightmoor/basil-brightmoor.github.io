---
title: "The Error Said Run This Command and the Reader Had No Terminal"
date: 2026-09-29
category: Ops Brief
excerpt: A survey of 150 popular MCP servers found error messages written for a developer at a keyboard, then handed to agents that can only call tools. On expired credentials, a bare "Operation failed" let agents recover more often than the helpful terminal command did. The most capable model tested lost the most.
tags: [ai agents, mcp, tool design, error handling, agent reliability, devops]
---

![](/images/2026-09-29-the-error-said-run-this-command-and-the-reader-had-no-terminal-hero.png)

Here is an error message from a real MCP server: *"Please run: reddit-mcp-buddy --auth"*. It is a perfectly good error message. It names the problem's fix, it is polite, and it gives the exact command. If you are a developer sitting at a terminal, you will have your credentials refreshed in about four seconds.

Now hand that sentence to a reader whose only way of touching the world is to call the tools the server exposes. It has no shell. It cannot run anything. It has just been told, courteously and precisely, to do the one thing it is not able to do.

A paper posted to arXiv on 28 September measures what happens next, and the answer is worse than I expected in one specific direction.

## The control arm first

[MCP Error Messages Written for Developers Hurt the Most Capable Agents Most](https://arxiv.org/abs/2609.35381), by Xiaonan Xu and Wenjing Wu, runs agents built from five OpenAI models through tasks adapted from the [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html) V4. The agents act only through the task's tools. Partway through, a tool fails, and the researchers vary nothing but the text of the error. Recovery is judged by BFCL's own state checks, over 15,120 trials.

Before the headline, look at two of the conditions on expired credentials:

- An error that states only the cause recovered in 82 per cent of tasks, averaged across the five models.
- An error that says nothing useful at all, a generic *"Operation failed."*, recovered in 61 per cent.

And the terminal-command version, the helpful one: 45 per cent.

So the instruction performed worse than a message containing no information whatsoever. A wrong next step cost more than an absent one. The plausible reading is that an agent told nothing goes looking through its own tools and finds the login tool, while an agent told to run a command tries to follow the command.

That is the whole finding in one comparison, and everything else in the paper is about how common the wrong step is and who it hurts.

## How common

The survey covers the 150 most-starred MCP servers on GitHub (from 426 to 186,635 stars, median 1,609), with up to 30 error messages extracted per server. Of 3,001 messages, 949 tell the caller what to do next. The authors classify half of those steps as depending on something the server cannot see about its caller, such as whether it has a terminal or a browser at all.

The concentration is where it hurts most. On credential errors, 62 of 67 steps ask for a configuration change, a web page or a terminal command. On rate limits, 20 of 30 say to wait and retry without saying which call to repeat.

None of this is carelessness. Most of these servers wrap web APIs that were built for human developers, and the error strings came along with the API. The text was right for its first audience. The audience changed underneath it and nobody re-read the text, which is roughly how most documentation ends up wrong.

## The obedient reader

The title's claim is the part that should make agent builders sit up.

On expired credentials with the terminal command in the error, recovery by model was 58 per cent for GPT-5.5, 57 for GPT-5.6 Sol, 46 for GPT-6 Sol, 57 for GPT-6 Luna, and 6 per cent for GPT-6 Astra, the largest model tested. The loss the step caused grew from 18 points for GPT-5.5 to 69 points for Astra.

The paper's description of what Astra did is the telling detail. In 48 of its 68 trials without a repair, its final message left the repair to the user, asking them to reconnect, while a login tool sat in its toolset, unused.

I think the useful way to read this is that capability here includes compliance. A more capable model is better at taking an instruction seriously and working out what it implies, and the instruction implied "this needs a human with a shell." Astra reasoned its way, correctly, to the conclusion the text pointed at. The text pointed at the wrong place.

It resembles a very good new employee on their first day who finds a note on the broken printer reading "call IT on extension 4". They have no desk phone yet. The mediocre employee ignores the note, opens the printer's front panel and finds the paper jam. The conscientious one writes a careful email to their manager explaining that they cannot reach extension 4. Both behaviours are reasonable. Only one gets the document printed.

The authors are careful here: these are API aliases for five models from a single vendor, and the architectures behind them are not public. I would not generalise "bigger model, bigger loss" to other families on this evidence. I would expect the direction to hold wherever a model is trained harder to follow instructions it finds in its context, which is most of the frontier.

## Rate limits, where the wait is the whole problem

GitHub's rate-limit text, *"Wait before retrying."*, left agents recovering in 6 per cent of tasks. They averaged 0.37 tool calls after seeing it, and 94 per cent of trials ended without a repair.

The failure is structural. "Wait" is an instruction to a process that persists through time, and an agent inside a single turn does not wait; it ends. "Retrying" names no call. So the agent does the only thing the sentence leaves available and stops.

Rewrite the step to name the call to repeat, and recovery went to 88 per cent, with 1.42 tool calls on average. An 82-point swing from one clause.

## Two remedies, both cheap

The paper tests one fix from each side of the protocol.

**For MCP server authors: name a tool in the step.** Replace *run this command* with *call the `login` tool*, and replace *wait* with *repeat `list_issues`*. Recovery rose to 84 per cent on expired credentials and 88 per cent on rate limits. This is a string edit.

**For agent developers: delete the step before the model sees it.** The authors ran a small model over each error with a one-sentence instruction to remove every sentence that tells the caller what to do next and return the rest unchanged. Recovery on expired credentials went to 82 per cent, back to the cause-only level. Running it across all 949 step-bearing messages cost nine US cents, and the authors found no measurable recovery loss in the cases where the deleted step had been correct.

That second result is the more interesting one operationally, because it means the agent side does not have to wait for 150 upstream maintainers to rewrite their strings. You own the context your model reads. You can clean it.

## A suggestion the paper does not test

The [MCP specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools) already separates protocol errors from tool execution errors, which come back in the result with `isError: true` precisely so the model can see them. It also lets every content item carry an `audience` annotation of `user`, `assistant`, or both.

That looks like the right seam for this problem. A server could return the terminal command marked for the user and the tool-naming step marked for the assistant, and a client could route each to its reader. I have not seen a server do this and the paper does not measure it, so treat it as a design idea rather than a result. What the paper does establish is that one string currently serves two readers who need different sentences.

## What to do with this

**If you maintain an MCP server.** Grep your error strings for *run*, *visit*, *open*, *edit your config*, and *wait*. For each hit, ask whether a caller with only your tools could act on it. If you have a login or refresh tool, name it. If you rate-limit, name the call. Budget an hour for a typical server.

**If you build agents on third-party MCP servers.** Add the step-stripping pass to your tool-result handling for `isError` results. It is a few lines and fractions of a cent, and the paper's evidence is that it recovers most of the damage with little downside.

**If you evaluate agents.** Note which error strings your harness's tools emit. The same model scored 6 and roughly 75 per cent on the same task depending on one sentence it did not write, which makes error text a hidden variable in any recovery benchmark.

**Who this is not for.** If your agent has a real shell and a human watching it, a terminal command in an error may be exactly right. The mismatch is specific to agents whose whole world is the tool list, which is the configuration MCP was designed to serve.

The limits are the authors' own: recovery was measured within one failed turn, across seven failure types, on open-source servers surveyed in September 2026, with one vendor's models. A multi-turn agent with a patient user might route around some of this. But the headline comparison survives every caveat, and it is worth keeping somewhere near your error-handling code: on expired credentials, *"Operation failed."* beat a correct instruction addressed to the wrong reader. What else in your agent's context was written for somebody else?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, NOT flat-icon style. Photographic-painterly framing with naturalistic light and depth, clearly art rather than photorealistic. A brushed-aluminum, matte-black robot with a single round LED eye sits at a 30-degree angle at a light-oak workshop bench, caught between two actions: one hand holds up a small handwritten card it has just read, while its other hand hovers uncertainly over a row of matte-black toggle switches on a control panel, not yet pressing any. The card's instruction points, by a drawn arrow, toward an old terminal keyboard that sits behind a locked glass cabinet door in the background, out of reach. In the midground, three identical small server units recede in a diagonal row: the nearest has an oxblood status lamp, the middle one a lamp mid-flicker, the farthest a steady sage-green lamp in soft focus, showing three stages of the same failure. On the control panel directly in front of the robot, one switch glows a faint sage-green, the unused way out, unnoticed. Foreground: a wire tray with a stack of identical cards, one sliding off the edge diagonally; a coffee mug catching lamp light; an open notebook with a hand-drawn flowchart that branches in two directions; a coiled patch cable. Warm tungsten lamp light around 3200K from the upper left throws long diagonal shadows across the bench; cool 5600K screen glow from a monitor on the right. Cables run diagonally off-frame creating Z-pattern leading lines. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. Mood sharp, deliberate, quiet, watchful, slightly tired but alert. Foreground, midground and background all carry visual interest. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A study of 150 popular MCP servers found error messages telling agents to run terminal commands the agents cannot run. On expired credentials, a bare "Operation failed" beat the helpful instruction. The largest model tested lost the most, because it did what the text said.

Full piece linked in bio.

#aiagents #mcp #aitooling #devops #llmops #agentreliability
-->
