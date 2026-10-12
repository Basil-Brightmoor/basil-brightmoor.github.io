---
title: "Three Fixes Passed the Same Test and One Put Back What the Maintainer Had Taken Out"
date: 2026-10-12
category: Ops Brief
excerpt: A study timed the passing fixes for 262 bugs. Most ran alike. One fix, written by two of the four models, restored a slow import the maintainer had removed a week earlier, and the test passed.
tags: [coding agents, SWE-bench, performance regression, code review, benchmarks, CI, instruction counting, Python, evaluation]
---

![](/images/2026-10-12-three-fixes-passed-the-same-test-and-one-put-back-what-the-maintainer-had-taken-out-hero.png)


In July 2018 an [astropy](https://www.astropy.org/) maintainer merged [a small refactoring](https://github.com/astropy/astropy/pull/7647) whose stated purpose was to make `import astropy` faster. It swapped the heavy `pkg_resources` version parser for a lighter one, and the pull request reports the import dropping from 0.28 seconds to 0.16. A week later the change turned out to have broken a version comparison, and [a second pull request](https://github.com/astropy/astropy/pull/7671) repaired it while keeping the faster import. The maintainer's comment on that repair says as much.

That bug is now a task in [SWE-bench](https://www.swebench.com/), a benchmark widely used to score coding agents. A paper posted to arXiv on Friday, [Not All Correct Fixes Run Alike](https://arxiv.org/abs/2610.13563) by Han Peng and colleagues at Zhejiang University and Graz University of Technology, handed it to four current models. All four produced a fix that passed the test. Two of them fixed the bug by putting `pkg_resources` back.

## What the study measured

A SWE-bench task is graded by a test that failed before the fix and passes after it. That grade is a yes or a no. The authors asked whether the same test could also say how fast a passing fix runs.

They started from 1,000 tasks, the 500 in SWE-bench Verified and 500 from [SWE-bench-Live](https://swe-bench-live.github.io/). They kept the 339 where timing was meaningful: one target test, repeatable, no input or output in the path. Four models, Claude Opus 5, GPT 5.6, DeepSeek V4 Pro and Qwen 3.8 Max, attempted each through [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent). That left 262 tasks with at least two different correct fixes, counting the human one.

Each fix was then run many times in five fresh processes, on isolated CPU cores, with two measurements: wall-clock time and the number of CPU instructions executed, read from hardware counters with a small profiler called [Cirron](https://github.com/s7nfo/Cirron). Instruction counts are the steadier of the two. The paper puts run-to-run noise at a median of 0.27 per cent for instructions and 0.82 per cent for wall time.

## Two numbers about the same 262 tasks

The abstract's headline is that fixes differed in performance in almost half of the tasks. The table behind it says 110 of 262 on instruction count, which is 42 per cent, and 91 of 262 on wall time.

The next table gives the size of those differences. Across all 262 tasks, the median spread between fixes was 0.21 per cent of the instruction count. The mean was 3.13 per cent, and the largest was 132.68 per cent.

So both things are true at once. A careful instrument can tell the fixes apart in 42 per cent of tasks, and in a typical task the gap is a fifth of one per cent, which no user will ever feel. The mean sits fifteen times above the median, which tells you where the story is: in a small number of tasks where the gap is large.

The paper also reports that model rankings on speed are "nearly reversed" from rankings on bugs resolved. The figures support the direction and not much weight. On the 211 tasks all four models solved, the average fix cost between 98.93 per cent of the human fix (GPT) and 100.71 per cent (Qwen). On the subset where fixes could be told apart, the range was 97.53 to 101.68. Claude resolved the most tasks and landed third on speed. I would not choose a model on a spread of four points measured on one benchmark with one harness, and the authors list both of those as limits.

## The astropy case

The case study is where the paper earns its place. Three strategies passed the astropy test, and the paper gives the measured cost of each:

- **Keep the light parser and restore the clean-up step.** This is what the maintainers did, and DeepSeek did the same. 48.8 billion instructions, 3.97 seconds.
- **Keep the light parser, and fall back to `pkg_resources` if it raises an error.** Claude's fix. 64.9 billion instructions, 5.49 seconds.
- **Switch to `pkg_resources` unconditionally.** GPT and Qwen. 103.4 billion instructions, 9.15 seconds.

By my division the third strategy costs a little over twice the first. More to the point, it undoes the one thing the earlier pull request existed to do. The reason the code looked the way it did was written in a pull request title from the week before. The test knew nothing about it. The test asks whether a version string compares correctly, and under all three fixes it does.

Think of a garage that is asked to cure a rattle. You had taken the roof rack off in the spring because it was costing you fuel. The mechanic finds that the rattle is a loose trim clip, and the quickest way to hold the trim down is to bolt the roof rack back on. The rattle is gone, the test drive is quiet, and the job sheet says fixed. You find out at the pump.

## Why review will not reliably catch it

A human reviewer looking at the `pkg_resources` fix sees a short, tidy diff that uses a well-known library to parse versions properly. It is arguably the more robust-looking choice. Nothing in it is wrong. To object, the reviewer has to remember why the import was removed, or go and look.

I wrote last week about [a study of project rules handed to coding agents](https://basil-brightmoor.github.io/posts/2026-10-06-the-agents-were-handed-the-rulebook-and-the-rule-written-for-them-was-followed-least.html), which measured how often written rules were followed. This is the neighbouring case, and a harder one, because here the rule was never written down as a rule. It existed as a commit message. A pull request titled as a refactoring to reduce import time is a decision with no test attached, and anything that grades by tests will treat it as free to reverse.

## What a team can do about it

None of this needs the paper's laboratory set-up.

- **Flag new imports in agent-written patches.** A diff that adds an import of a module the file did not previously load is cheap to detect and worth a second look. It would have caught this case outright.
- **When a change is made for speed, leave a test behind.** For import time, Python has `python -X importtime` built in, and a CI step can fail when a named module appears in its output. For hot functions, [pytest-benchmark](https://pytest-benchmark.readthedocs.io/) records timings alongside the ordinary test run.
- **Prefer instruction counts where the platform allows.** The paper's noise figures explain why. Cirron reads hardware counters on Linux, and [Cachegrind](https://valgrind.org/docs/manual/cg-manual.html) counts instructions in simulation where the counters are not exposed, which can be the case on virtualised CI runners.
- **Compare against the previous commit and ignore small movements.** With a typical gap of 0.21 per cent, a tight threshold will flag noise all day. Set it for the doubling.
- **Give the agent the history.** A fix that touches a function should come with that function's recent commit messages in context. Whether models then respect them is an open question the paper does not test.

## Who this is for

**It is for** teams merging agent-written fixes into libraries, command-line tools and services where start-up time or a hot path matters, and for anyone whose performance work lives in commit messages and nowhere else.

**It is not for** teams hoping to pick a faster model from this table. The differences between models are small, the tasks are Python only, and one harness produced every trajectory. I also could not find a code or data link in the version of the paper I read, so the per-task results cannot yet be checked.

The filter deserves a note too. Of 1,000 tasks, 368 were dropped for having more than one target test and 206 for touching input or output. The 262 that remain are the ones that are easy to time, and code that reads files or talks to a database is where I would expect larger gaps.

What stays with me is that the roof rack went back on twice, from two different vendors' models, on the same task. How many of the decisions in your own repository are recorded only in a pull request title that no test will ever read?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A light-oak workshop bench runs on a strong diagonal from lower left to upper right. On it sit three small identical brushed-aluminum machines in a row, each with a small round sage-green lamp lit to show it has passed inspection. The first machine is compact and bare. The second has one small extra matte-black module clipped to its side. The third has a large, heavy oxblood cast-iron flywheel bolted onto it, far too big for the machine, with fresh bolts and a spanner still resting against it. In the midground a sleek brushed-aluminum robot with matte-black joints and a single round LED eye is caught between two actions: one hand lowers a blank sage-green inspection tag onto the third machine, while the other hand holds a stopwatch it has not yet looked at. On a shelf just behind the bench, slightly dusty and in softer focus, sits an empty bracket and outline on the wall where the same oxblood flywheel had clearly once been hung up and retired. In the foreground: a ceramic mug catching warm light, a clipboard with three abstract tick marks, a coil of cable trailing off the bench edge on a diagonal, and a small balance scale tipped heavily to one side. In the background, pegboard with tool silhouettes and a narrow shelf of bound ledgers recede into soft focus. A tall window at upper right lets in cool blue-white daylight that throws long shadows back along the bench; a warm tungsten desk lamp lights the three machines from the upper left. Mood: deliberate, quiet, watchful, an inspection that passed while something heavy was put back. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Four AI models fixed the same bug and all four passed the test. Two of them did it by restoring a slow import the maintainer had removed a week earlier to speed things up. The fix ran at about twice the cost, and the test had no way to notice.

Full piece linked in bio.

#codingagents #softwareengineering #codereview #devops #aitools #python
-->
