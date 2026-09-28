---
title: "The Shutdown Date Was Published and the Only Reader Was an Inbox"
date: 2026-09-28
category: Ops Brief
excerpt: A study of 5,139 migrations away from retired LLMs found an estimated 82 per cent landed after the shutdown date, when the application had already started failing. Popularity did not help, experience did not help, and an abstraction layer did not help. The date was public the whole time. Nothing in the running system ever read it.
tags: [ai tooling, llm ops, platform dependency, deprecation, observability, devops]
---

![](/images/2026-09-28-the-shutdown-date-was-published-and-the-only-reader-was-an-inbox-hero.png)

Every model retirement comes with a date. It is announced in advance, printed in a table on the provider's website, and usually emailed to somebody. Developers are told. The interesting question about model retirement is where the telling lands, and whether anything that runs in production is standing there when it does.

A paper posted to arXiv on 25 September answers that with unusual precision. [When the Model Retires](https://arxiv.org/abs/2609.31288), by Hyungjin Lukas Kim, mines GitHub for commits that move applications off officially deprecated models and endpoints from OpenAI, Anthropic and Google, then matches each commit to the provider's own announcement and shutdown dates. From 22,555 commits across 17,703 non-fork repositories, 5,139 match an official retirement event. Two independent coders validated a stratified sample of 300, with agreement between 0.89 and 0.95 kappa, and every estimate is reweighted by their labels.

The headline: an estimated 82 per cent (95% CI 79 to 84) of migrations away from a retired model were committed after the shutdown date. After the application had started failing.

## Three things that should have helped, and did not

What makes this paper worth your morning is the list of variables that ought to have moved that number and simply failed to.

**Popularity.** Repositories with zero stars and repositories with a hundred or more migrate late at essentially the same rate. Having more people watching the code does not mean anyone is watching the calendar.

**Experience.** Kim found 85 repositories that were hit by two or more retirements. Their post-shutdown share was 73 per cent at the first event and 73 per cent at the later ones. No learning. A team that was burned once got burned again at the same rate, which tells you the lesson from the first time was stored somewhere the second shutdown never consulted.

**An abstraction layer.** This is the one I suspect will sting. Tools like [LiteLLM](https://github.com/BerriAI/litellm) and [OpenRouter](https://openrouter.ai/) exist precisely so that swapping a model is a small change, and the paper confirms the change is small: migrations through an existing abstraction were the smallest non-trivial ones, a median of four files and twenty lines. They were also no less late. Seventy per cent of them landed after shutdown.

That last result is worth pausing on, because it looks like a contradiction and is actually a clean diagnosis. An abstraction layer reduces the *cost* of the change. The *timing* is a separate variable, and a gateway that routes calls has no reason to know what day the model stops answering. Only 3 per cent of migrations went through an existing abstraction at all; 93 per cent simply renamed the identifier where it sat. The cheapest possible change still waits until something breaks, because nothing tells anyone it is due.

## Where the notice went

So what does move the number? One variable, and it is on the provider's side of the table.

The late share tracks notice length almost mechanically. Anthropic's notices in the sample run 60 to 114 days, and the post-shutdown share for Anthropic retirements is 89 per cent. OpenAI's one-year notice for the Assistants API produced 13 per cent. Across the whole dataset, each e-fold increase in notice length cuts the odds of a post-shutdown migration by about three quarters. The paper also finds that the week after the Claude 3.5 Haiku, Claude 3 Haiku and Opus 4.1 shutdowns each carried 25 times the normal weekly volume of fix commits.

Now look at how notice is delivered: a page on the provider's documentation site ([OpenAI](https://developers.openai.com/api/docs/deprecations), [Anthropic](https://platform.claude.com/docs/en/about-claude/model-deprecations), [Google](https://ai.google.dev/gemini-api/docs/deprecations)) and an email to the account holder. Kim points out the obvious failure of the second channel. The account often belongs to a contractor, or to whoever set up billing, who may not be the person maintaining the code and may not be anybody at all by now.

It is a smoke detector whose low-battery chirp is posted as a letter to the previous tenant. The device knows. The date is known. The message is sent. It is simply addressed to a place the running system does not live.

Kim's recommendation to providers is the sentence I would pin above every API team's desk: surfacing deprecation in API responses, as a warning header, and in SDK logs "would reach the running system rather than an inbox." The model endpoint that is going to stop answering in sixty days is the one component guaranteed to be in contact with the application every single day. It is also the one component that currently says nothing.

## The identifier lives in the code, so the date has to

On the developer side, the paper supplies the reason the calendar never reaches the build. In 94 per cent of migrating applications the model identifier was hard-coded in source; only 6 per cent of migrations touched configuration or documentation alone. In 26 per cent the identifier appeared in three or more files.

The edit itself is small. Effort for the typical application is trivial: prompt-only applications, 78 per cent of the sample, needed a median of two files and six added lines. Agent and tool-using applications took five files and 63 lines, retrieval applications seven files and 155 lines, and the 2 per cent that were fine-tuned needed fourteen files and 693 lines. For most teams the fix is a string edit.

What hard-coding does is make the identifier invisible to every tool that could compare it with a date. A string literal in `app.py` is not something your CI knows is perishable. It carries no expiry, so nothing checks one.

And then the quiet failure makes it worse. Among genuine post-shutdown migrations, the coders labelled 40 per cent as production repairs and 45 per cent as planned changes with no breakage mentioned. The paper's reading is blunt: "graceful degradation" in exception handlers around model calls hid outages for weeks. The median migration landed 39 days after shutdown. Only 9 per cent landed within a week of it, 27 per cent within a month, 55 per cent within three months.

Thirty-nine days is a long time for a feature to be politely returning a fallback message while its dashboard stays green.

## Who hedged, and who left

One more finding, because it corrects a common assumption about lock-in. Only 8 per cent of migrations switched to a different provider (7 per cent reweighted), and the switch rate was the same whether the migration was reactive or proactive, and whether or not anything broke. Another 16 per cent added a second provider alongside the first. Most teams, 68 to 74 per cent, moved to the retiring provider's designated successor.

So a forced retirement, even a painful one, mostly produces a rename. The dependency survives the outage intact. That is a reasonable outcome for most applications. It is also a reminder that the next retirement from the same provider is already on its way, with the same notice policy attached.

## What to do with this before lunch

**If you maintain an application that calls a hosted model.** Move the identifier into one place: an environment variable or a small registry file. The paper's own estimate is that this would have made most of these migrations a one-line change. Then add a CI check that compares every identifier in that registry against the providers' deprecation tables and fails the build some weeks before a shutdown date. Kim argues a static check of exactly that shape "would have prevented most of the post-shutdown commits." Budget an afternoon.

**If you wrap model calls in exception handlers.** Make them fail loudly on a model-not-found or retired-model error, as distinct from a timeout or a rate limit. A retired model is a permanent condition, and treating it as a transient one is how thirty-nine days go missing.

**If you run an abstraction layer or gateway.** You are sitting at the one point where every identifier passes through. You could know the retirement dates and warn at request time. That would convert your product from a thing that makes the fix cheap into a thing that makes the fix happen on time, which is the half the data says is missing.

**If you run a model API.** Put the shutdown date in the response. A header costs you nothing, and the only reader you can be certain of is the application that is about to break.

**Who this is not for.** If your application pins an open-weights model you host yourself, nobody retires it but you. The calendar problem becomes a patching problem, which has its own failure modes and is a different post.

The study only counts migrations that eventually happened, so the true late share is if anything flattering: an application that broke and was abandoned never files a migration commit. Which leaves the question worth asking of your own stack this week: if your model's shutdown date were tomorrow, what is the first component that would tell you, and is it a person or a pager?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, NOT flat-icon style. Photographic-painterly framing with naturalistic light and depth, clearly art rather than photorealistic. A brushed-aluminum, matte-black robot with a single round LED eye stands at a 30-degree angle at a light-oak workshop bench, caught mid-motion between two actions: one hand is reaching up to tear a page off a large wall calendar, while its head is still turned toward a small server unit on the bench whose status lamp has just flickered from sage-green to oxblood. In the foreground a wire mail tray overflows with sealed envelopes nobody has opened, one envelope sliding off the edge at a diagonal. In the midground three identical small server units sit in a receding row: the nearest shows an oxblood lamp, the middle one a lamp mid-flicker, the farthest a steady sage-green lamp in soft focus, so three stages of the same failure are visible at once. Behind them a monitor displays a calm, entirely green dashboard grid, oblivious. A smoke detector is mounted on the wall near the calendar, its small indicator light glowing. Warm tungsten lamp light around 3200K from the upper left throws long diagonal shadows across the bench; cool 5600K monitor glow comes from the right. Populate the scene with a coffee mug catching the lamp light, an open notebook showing a hand-drawn timeline with one marked point, a small potted plant, a coiled patch cable, and cables running diagonally off-frame creating Z-pattern leading lines. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. Mood sharp, deliberate, quiet, watchful, slightly tired but alert. Foreground, midground and background all carry visual interest. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A study of 5,139 migrations off retired LLMs found an estimated 82 per cent happened after the shutdown date, once the app was already failing. Popular repos were just as late. Teams burned before were just as late. Teams with an abstraction layer were just as late. The date was published all along, and it was sent to an inbox. The only reliable reader would have been the API response itself.

Full piece linked in bio.

#llmops #aitooling #devops #platformengineering #observability #aiagents
-->
