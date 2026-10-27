---
title: "Deleting the Agent's Old Turns Cut the Tokens and Broke the Discount"
date: 2026-10-27
category: Ops Brief
excerpt: A study of 9,400 coding-agent runs found that trimming old turns can keep the solve rate and still raise the bill. Under flat pricing 26 of 42 setups got cheaper. Once prompt caching is priced in, none did.
tags: [AI agents, coding agents, prompt caching, context management, LLM cost, SWE-bench, agent evaluation, token economics]
---

![](/images/2026-10-27-deleting-the-agents-old-turns-cut-the-tokens-and-broke-the-discount-hero.png)


A paper posted to arXiv this week has a cost table I'd like every agent-harness author to see. In [The Hidden Costs of Forgetting](https://arxiv.org/abs/2610.35496), Fernando Vallecillos-Ruiz, Islem Bouzenia, Michael Pradel and Leon Moonen test the obvious way to make a coding agent cheaper: delete parts of its old turns before each model call so it resends less. They tried 42 ways of doing it across 9,400 runs. Priced the simple way, 26 of the 42 came out cheaper than leaving the history alone. Priced the way providers actually bill once prompt caching is involved, none of the 42 did.

The runs and the tokens are identical in both columns. Only the method of computing the bill differs, so that is where this post goes.

## The setup

A coding agent works in turns. Each turn it sends the model the task, everything it has done so far, and the latest tool output, then gets back some reasoning and a tool call. The authors put the premise plainly: these agents resend their entire trajectory to the model at every turn. By turn forty that is a long prompt, and most of it is old file listings and test logs the agent has already read.

The study ran two open agents, [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) (one shell tool) and Trae agent (a file viewer, an editor and a shell), on a fixed 100-task subset of [SWE-bench Verified](https://www.swebench.com/). Both used DeepSeek-V4-Flash, self-hosted on [vLLM](https://github.com/vllm-project/vllm), at temperature zero.

The variables were what to delete (the model's reasoning text, the tool output, or both), how much (25 to 100 per cent), at what grain (whole turns or random tokens within them), and when. "Immediate" means a turn is rewritten before the next call, so the agent never sees the original of anything deleted. "Delayed" means the two most recent turns are always left intact and only older ones are trimmed.

## Result one: you can throw away a great deal, if you wait

Delay was the variable that mattered most for whether the agent still solved tasks. With the two-turn delay, 37 of 42 configurations showed no statistically significant drop in tasks solved. Several matched or beat the baselines of 72.6 tasks (mini-SWE-agent) and 74.6 (Trae). Deleting up to all of the reasoning text, the abstract notes, can leave effectiveness intact.

Immediate deletion was a different story: significant drops in 19 of 42. At the extreme, Trae with every tool output deleted immediately solved zero tasks. An agent that reads a file and has the contents removed before it can act on them is not going to fix much.

## Result two: the agent goes back for what you took

The authors measured how often an agent re-reads something it has already read. In the baseline that happens 19 times per 100 reads for mini-SWE-agent and 9 for Trae. Under the heaviest delayed deletion, Trae's re-fetch ratio climbed to 7.5 times the baseline. Deleted outputs were re-fetched 1.5 to 5 times as often as retained ones.

The agent notices, in its way: it opens the file again. Each re-read is another turn and another tool output, and Trae's median run under 100 per cent delayed tool-output deletion was 73 per cent longer than its baseline. Full-price input tokens rose in all 42 delayed configurations, by about 1.25 times up to nearly ten.

## Result three: the cache

This is the result I would put in front of anyone shipping a context-trimming feature.

Providers bill prompt tokens at two rates. Tokens matching a prefix the provider has already cached are cheap; everything else is full price. [Anthropic's prompt-caching documentation](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) lists cache reads at 0.1 times the base input price for most models, and says that changes at each level of the prompt "invalidate that level and all subsequent levels." The paper's pricing model uses a ratio of 1 : 0.1 : 5 for input, cached input and output, and notes that the cached rate falls between 0.05 and 0.5 across the providers it checked.

An agent that only ever appends gets close to the best case. Every turn, the whole previous prompt is an exact prefix of the new one, so almost everything it resends is billed at a tenth. Trimming an old turn changes the prompt in the middle, and everything after the change is billed at full price again.

The paper's two pricing models capture this:

- **Flat pricing** bills every prompt token at the input rate. Under it, 26 of 42 delayed configurations were cheaper than baseline.
- **Caching-aware pricing** bills only the longest exact match with the previous call's prompt at the cached rate. Under it, all 42 were more expensive, 26 of them significantly.

One configuration shows the flip on its own: mini-SWE-agent with all old tool output deleted cost 0.71 of baseline under flat pricing and 1.20 under caching-aware pricing. The worst case, Trae with 75 per cent of tokens removed from both scopes, came to about five times baseline.

The authors call their figure a lower bound. It assumes every matching prefix is already cached and leaves out cache-write premiums. Anthropic's page lists writes at 1.25 times base for a five-minute cache and 2 times for an hour. My own inference, which the paper does not compute: an agent that rewrites its history pays those premiums again each time, so the real gap is probably wider than the table shows. The same page lists cache reads at 0.05 times base for some newer models, which would widen it further.

## The stack of photocopies

An analogy helps me here. Picture a print shop that charges a tenth of the price for any page identical to the job you sent last time, in the same position, counting from the front. Every day you add a page to the end of a growing report and send the whole stack. Nearly all of it costs a tenth.

Then one day, to save paper, you pull page three out. Page three is gone, but page four is now in position three, page five in position four, and so on to the end. None of them matches its old position, so all of them are billed as new. You saved one page and paid full price on everything after it. And, as the second result showed, you will probably have to ask for page three again next week.

## What to do with this

If you build or tune an agent harness, or you pay for one:

- **Price your experiments the way you are billed.** A token count is a proxy, and this paper shows it pointing the wrong way. The authors recommend comparing every compression method against an uncompressed baseline under caching-aware pricing and reporting cost per task solved. It needs one extra column in the spreadsheet.
- **Check whether your context manager edits the middle.** Summarisation, sliding windows and "drop stale tool output" features all change earlier parts of the prompt. Each change resets the cached prefix from that point on. Rewriting less often reduces how many times you pay that, though the authors point out that a batched rewrite still invalidates the prefix when it happens.
- **Keep recent output until it has been used.** The two-turn delay separated the configurations that kept working from the ones that collapsed. If you cut anything, cut only what is old.
- **Count re-reads.** If your traces show the agent reopening the same file, the deletion may simply be moving cost from the prompt to extra turns.

**This is for** anyone running coding agents at volume on a provider that discounts cached input, and anyone evaluating a context-compression feature on the strength of a smaller token count.

**It is less useful for** short tasks. A run of a few turns never builds a long prefix, so there is little cache to break. It also has clear limits. It is one model, self-hosted, on 100 tasks, with a stylised price model. A provider whose cached rate is near the top of the paper's 0.05 to 0.5 range would narrow the gap. And there are reasons to trim context that have nothing to do with cost: a context window has a ceiling, and a trajectory that will not fit has to lose something.

## At least one vendor already says so

To its credit, the documentation for one shipping feature already warns about this. Anthropic's [context editing](https://platform.claude.com/docs/en/build-with-claude/context-editing) can clear the oldest tool results automatically once a conversation passes a threshold. Its page says the clearing "invalidates cached prompt prefixes when content is cleared," tells you to clear enough tokens each time to make that worthwhile, and provides a `clear_at_least` parameter for the purpose. That is the same trade-off the paper measures, written down as a configuration knob. What the documentation cannot tell you is where the break-even sits for your agent, on your tasks, with your re-read rate. The paper's method gives you a way to find out.

The paper's own conclusion is that token counts alone are misleading, and the evidence supports it. The question I'm left with is about the dashboards. If a context-management feature is sold on tokens saved, does anything in your usage reporting show the cache writes it caused and the extra turns it bought?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A long light-oak counter in a small print shop runs on a strong diagonal from lower left to upper right. In the foreground, sharp, a tall neat stack of paper pages sits on the counter with one page pulled halfway out from near the bottom, its edge sticking out like a tongue. A sleek brushed-aluminum robot with matte-black joints and a single round LED eye stands at a 30-degree angle, caught between two actions: one hand still holding the corner of the pulled page, the other reaching toward a matte-black counting machine whose small sage-green lamp has just switched to oxblood. In the midground, three earlier stacks recede into soft focus along the counter, each slightly taller than the last, each topped with a small sage-green tag, showing the report growing day by day. Beside the counting machine, a long paper tally strip curls off the counter edge on a diagonal, the marks along its length changing from small and sparse to dense and heavy partway along, without legible text. Foreground details: a ceramic mug catching warm lamp light, a stapler, a single loose page on the floor, an open notebook with an abstract sketch of stacked rectangles. Background: wooden pigeonhole shelves of paper reams, a tall window. Warm tungsten lamp light from the upper left falls across the stack and the robot; cool blue-white daylight from the window at upper right lights the counting machine and the tally strip, throwing long shadows back along the counter. Mood: deliberate, quiet, watchful, a small saving that has just set off a much larger charge. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Trimming a coding agent's old turns made it cheaper in 26 of 42 setups when every token cost the same. Priced with the prompt-cache discount providers actually give, none of the 42 came out cheaper.

Full piece linked in bio.

#aiagents #llm #promptcaching #devtools #softwareengineering #aitools
-->
