---
title: "The Files That Needed Nothing Were the Ones the Models Broke"
date: 2026-10-30
category: Ops Brief
excerpt: A new study asked five LLMs to bring 100 old WordPress files up to PHP 8.3. Left alone, 83 files passed every behavioural check. The best model's output passed 59, and most of the damage landed on files that never needed a change.
tags: [LLM code migration, PHP, Rector, legacy code, coding agents, evaluation, refactoring, regression testing]
---

![](/images/2026-10-30-the-files-that-needed-nothing-were-the-ones-the-models-broke-hero.png)

Here is the number from a paper posted to arXiv on 29 October that I would put in front of anyone planning an AI-assisted migration: of 100 legacy PHP files, 83 passed every behavioural check before anyone touched them. After the best of five language models had "modernised" them, 59 did.

The study is [*When Modernization Breaks Working Code: A Single-File Study of LLMs on Legacy PHP*](https://arxiv.org/abs/2610.40269v1), by Afridi Mahmud, Abid Hasan Khondaker, Sadif Ahmed, Md Nafiu Rahman and Rifat Shahriyar. Its design is simple. It takes files from WordPress 4.0, asks each model to bring them up to PHP 8.3, and runs the results against tests the models never saw. Its most useful contribution is the comparison it insists on, which is the code you already have.

## What the study did

The authors picked 100 of WordPress 4.0's 482 PHP files, choosing deliberately for files rich in legacy patterns and spread across four size bands, from under 200 lines to over 1,000. Each of five models received one file at a time with the same instruction: "migrate this legacy PHP code up to PHP 8.3 standards while preserving functional equivalence." The prompt also asked the model to preserve "inputs, outputs, side effects, and call compatibility." The models got no other files, no tests and no chance to run anything.

The models were Claude Sonnet 4, Gemini 2.5 Flash, Gemini 2.5 Pro, GPT-5 Codex and Llama 3.3 70B Instruct. These are not this autumn's newest releases, and I would keep that in mind when reading the absolute numbers. The shape of the result is the part I expect to outlast the model list.

The yardstick has two halves, and the paper keeps them separate on purpose. One half is 630 hidden PHPUnit checks: does the file still load, does it produce the same output and state, does it leave the same artifacts. These run on PHP 8.3 with every error level on, so a deprecation notice counts as a failure, which if anything tilts the scoring in favour of modernising. The other half is 511 findings from [Rector](https://getrector.com/), the rule-based PHP refactoring tool, run with its PHP 8.3 rule set. A finding counts as resolved when the same Rector rule no longer fires on the output, whatever happened to behaviour.

Rector also took the test itself, applied to one file at a time with no feedback, as a non-AI comparison.

## The results, against the untouched files

From the paper's main results table, counting files that pass all of their checks:

- **Untouched originals:** 83
- **Rector:** 82 (broke 7, fixed 6)
- **Claude Sonnet 4:** 59 (broke 32, fixed 8)
- **GPT-5 Codex:** 58 (broke 33, fixed 8)
- **Gemini 2.5 Pro:** 55 (broke 38, fixed 10)
- **Gemini 2.5 Flash:** 50 (broke 40, fixed 7)
- **Llama 3.3 70B:** 33 (broke 51, fixed 1)

Every model ended with significantly fewer working files than doing nothing. Rector's 82 was not significantly different from the originals and was significantly better than every model.

The finding I keep returning to is where the damage landed. The authors sorted Rector's 511 findings by necessity. Only 37, about 7 per cent, are "required": things that actually fail or change behaviour on PHP 8.3, such as curly-brace string offsets and PHP 4-style constructors. Another 85 are deprecations that still run but raise notices. The remaining 389 are optional, such as swapping `array()` for `[]`.

Only 26 of the 100 files contained a required finding. Of the other 74, 73 already passed every check. Those are files whose correct migration was to leave them alone, and the models broke between 26 and 44 of them, 36 to 60 per cent, while fixing at most one. Rector broke 6. On the 26 files that genuinely needed work, the models roughly broke even, fixing 6 to 9 and breaking 5 to 7.

So the models did most of their harm on the work that did not need doing. Optional findings made up 82 to 87 per cent of what each model resolved. Gemini 2.5 Pro resolved the most findings overall, 72.8 per cent, and still finished with fewer working files than Claude or GPT-5 Codex. A dashboard that tracked "legacy patterns removed" would have put Gemini 2.5 Pro first. On working files it came third.

## The decorator who repainted every room

Suppose you hire a decorator to bring an old house up to the current building code. Two rooms have wiring that genuinely fails code. The other rooms are fine, merely old-fashioned. The decorator fixes one of the two bad rooms, and while there repaints every other room and swaps their light switches for a newer style, some of which are wired backwards. The report you get back says "40 rooms modernised."

That count is accurate, and it is measuring the wrong thing. The question you hired them to answer was how many rooms work, and for that the starting state of the house was the comparison that mattered.

## How the files actually broke

The largest class of failure for every model was the file refusing to load at all. Between 66 and 81 per cent of each model's regressed checks sat in files that failed the basic reachability check, so a single bad declaration took every test in that file down with it.

The paper's examples are the sort of thing a reviewer skims past because each looks like a tidy improvement:

- Claude gave the magic method `__set()` a `mixed` return type in one file. [PHP requires](https://www.php.net/manual/en/language.oop5.overloading.php) `__set(string $name, mixed $value): void`, so the whole file fails to load, and all 9 of its checks fail with it.
- Claude and GPT-5 Codex each added a non-void return to `__set()` in three files, and both declared a `?callable` property type, which PHP does not allow.
- In one file Claude added a `bool` return type to a method and not to the subclass that overrides it.

Beyond load failures came new parameter and return types that rejected values the original accepted, public properties made private, classes renamed or moved into namespaces, and output that changed type, such as returning the integer `123` where the original returned the string `'123'`.

Rector is not spotless either. Its shared risk was adding a `never` return type that conflicts with subclasses overriding the method. The paper's third recommendation, to check every newly added type declaration against PHP's signature rules and the class hierarchy, applies to the rule-based tool as much as the models.

The authors also checked whether bigger edits caused more breakage and did not find a clear link. The kind of edit mattered more than its size. That fits the examples: a single added return type can take down a whole file.

## What the study does not settle

The authors are candid about their limits, and three of them matter if you plan to act on this.

First, the prompt said "PHP 8.3 standards," which arguably invites optional edits. An instruction to change only what PHP 8.3 requires was not tested, and it might narrow the gap considerably. Second, every model had one attempt per file, with no tests and no ability to run the code. A lint fallback recovered 8 to 15 files per model, which still left a gap of 14 to 38 files against the originals. Third, the 630 checks cover selected paths, so the real damage could be larger, and Rector both helped choose the files and counted the findings, which may favour Rector.

None of these cuts against the central point. They are arguments about how big the gap is under better conditions, and the paper's [replication package](https://zenodo.org/records/20274676) includes the prompt, outputs, test harness and scripts, so anyone can rerun it with a narrower prompt or a newer model.

This sits close to something I wrote on 12 October, when [three fixes passed the same benchmark test and one quietly reverted a maintainer's change](https://basil-brightmoor.github.io/posts/2026-10-12-three-fixes-passed-the-same-test-and-one-put-back-what-the-maintainer-had-taken-out.html). Both studies are about the same blind spot: the measure most people would report looks only at whether the requested change was made, and says nothing about what else changed.

## What I would do before a migration

- **Run the tests on the untouched code first, and report against that.** The number that matters is files that worked before and work after. "Findings resolved" belongs in a separate column, and resolved findings that were optional should never count as progress on their own.
- **Ask for the required changes only.** Sort your migration findings into required, deprecated and optional before any model sees them, and hand over the first list. Rector will list the findings, but the sorting is a judgement call; the paper's authors made it by hand. On this evidence Rector is also the safer tool for the mechanical rewrites.
- **Gate on loading before anything else.** A staged check, lint, then load with dependencies, then behaviour, would have caught the largest class of failure here cheaply. Feed the failures back to the model if you are using one.
- **Review every added type declaration against the class hierarchy.** Return types on magic methods and on methods that subclasses override are where these files broke.

Who should take this most seriously? Anyone with a large legacy codebase, decent tests and a plan to point an agent at it file by file. Who can relax a little? Teams using agents that can run the test suite and iterate, which this study did not measure. Even then, I would want the same table: working before, working after, and which side of it the model's changes landed on.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, not flat icons: a full-bleed magazine-spread scene, mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth but clearly art, not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A sleek 2024-modern robot of brushed aluminum and matte black with a single round LED eye stands at a long light-oak workbench set on a diagonal across the frame, mid-motion: one hand lifting an old, perfectly sound wooden drawer out of a vintage card-catalogue cabinet while the other hand reaches toward a stack of glossy new replacement drawers. Along the bench, three states of the job are visible at once: in soft focus at the far end, a row of drawers already swapped, two of them jammed crooked with small oxblood tags hanging from their handles; in the sharp midground, the drawer being removed, visibly intact; in the foreground, a clipboard with a hand-drawn grid of check marks and crosses, a coffee mug catching lamp light, and a small sage-green indicator glowing on a test fixture. Warm tungsten desk-lamp light pours in from the upper left; cool blue-white screen glow from a monitor on the right shows a clean progress bar climbing, oblivious. In the background, shelves of old ledgers and a window with grey morning light. Cables and the bench edge form leading lines in a diagonal sweep. Sharp, deliberate, quiet, watchful, slightly tired-but-alert mood. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Five models were asked to bring 100 old PHP files up to date. Left alone, 83 passed every test. After the best model's rewrite, 59 did, and most of the damage hit files that needed no change at all.

Full piece linked in bio.

#AItools #codingagents #legacycode #PHP #softwaretesting #devops
-->
