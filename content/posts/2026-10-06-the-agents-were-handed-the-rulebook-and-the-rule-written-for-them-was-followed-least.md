---
title: "The Agents Were Handed the Rulebook and the Rule Written for Them Was Followed Least"
date: 2026-10-06
category: Ops Brief
excerpt: A new benchmark turned twelve projects' contributor docs into 823 executable checks. Handing agents the rules lifted compliance about nine points, and AI disclosure rules stayed the least followed.
tags: [coding agents, AI tooling, contribution guidelines, AGENTS.md, evaluation, pre-commit, workflow, open source]
---

![](/images/2026-10-06-the-agents-were-handed-the-rulebook-and-the-rule-written-for-them-was-followed-least-hero.png)

SymPy's contributor guide has a sentence that takes four seconds to read: ["Keep the first line 71 characters or less."](https://docs.sympy.org/dev/contributing/new-contributors-guide/workflow-process.html) Django's has one about test assertions: use [`assertIs(…, True/False)`](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/) for booleans. Neither rule will ever fail a unit test. A patch can break both, pass the whole suite, and still be counted as a resolved issue, because SWE-bench scores a patch by running the tests.

A preprint posted to arXiv on Monday, [SWE-CC](https://arxiv.org/abs/2610.06193v1) by Truong Hai Dang, Rayner Goh, Thanh Le-Cong and Yintong Huo, measures the part the leaderboards skip. The team read the contributor documentation of the twelve repositories behind [SWE-bench Verified](https://www.swebench.com/), pulled out 1,759 separate obligations, kept the 823 that are mandatory and checkable from evidence, and compiled each one into a small deterministic function. Then they ran 500 bug-fix tasks through four models on two agent scaffolds, [mini-SWE-agent](https://github.com/SWE-agent/mini-swe-agent) and [OpenHands](https://github.com/OpenHands/OpenHands), asking for a full contribution each time: commits, pull request text, tests. That is 8,000 runs, each one audited on both the final deliverable and the log of what the agent did on the way there.

The abstract's headline is that agents violate 43.1 per cent of the policies that apply to them. I think the more useful numbers are two tables further in.

## Start with the run where the agent had the rules

The paper tests two ways of supplying policy. In the first, which the authors call Native, the agent is given the URL of the project's policy documents and told to read them before starting. In the second, Consolidated, every atomic rule is written into a local Markdown file in the working directory, with an instruction to read it.

The second setting is the control that matters. On average 91.6 per cent of those runs opened the file, and 99.6 per cent of its content reached the model's context. In most runs the agent had the rulebook, in full, in front of it.

Compliance rose from 55.7 to 64.4 per cent under mini-SWE-agent and from 58.2 to 67.0 under OpenHands. That is a gain of just under nine points, and it leaves roughly a third of applicable rules broken by an agent that had read all of them. The best single configuration in the paper reached 71.2 per cent. Functional success barely moved in either direction, sitting between 74 and 94 per cent of tasks resolved depending on the model.

So delivering the rules is necessary and it is nowhere near sufficient. The category table shows which rules it helps with.

## Which rules moved

The authors sort the 823 policies into eight groups. Here are four of them, with average compliance before and after the rules file was supplied (mini-SWE-agent first, then OpenHands):

- **Git and commit conventions:** 59.9 to 87.0, and 63.4 to 90.1.
- **Language and framework style:** 84.0 to 85.1, and 84.2 to 85.9.
- **Documentation and docstrings:** 62.7 to 61.1, and 62.2 to 62.6.
- **AI-assisted contribution policy:** 15.3 to 26.6, and 20.6 to 30.7.

Commit conventions jumped by about 27 points. That fits what they are: local and arbitrary. No amount of general programming knowledge tells you that one project wants the summary line at 71 characters, or that, as the paper notes, Django requires an issue number in the commit message while Flask prohibits one. Only 12 of the 823 policies have a near-equivalent in another project. Tell the agent the local rule and it mostly follows it.

Framework style did not move, because it was already high. The authors' reading is that models pick up idiomatic formatting from training and satisfy those rules without being told.

The last row is the one that stopped me. Eleven of the twelve projects now publish rules about AI-assisted contributions, 37 policies in all. The paper's example is a Django rule to disclose any AI tools used in preparing a contribution and what each was used for. More than nine in ten of these policies were brought into scope by the agents' work, and not one of the 37 sat idle across the whole experiment. They are the only category addressed to the agent itself, and they were the least followed in the study, by a wide margin, with the rule in context or without it. The paper notes that the stock OpenHands system prompt already carries its own instruction to add an AI disclosure note to pull request descriptions and similar content. OpenHands scored a few points higher than mini-SWE-agent on this row and still failed about four times in five in the Native setting.

## Most runs never fetched the page

The Native setting is closer to how people deploy these tools: point the agent at the repository and trust it to find the house rules. The paper logged what happened to that instruction.

On average 28.9 per cent of runs attempted to fetch a policy document at all, and 12.6 per cent ended up with policy text in context. The spread across configurations is large. GPT-5.6 Luna under OpenHands attempted in 75.6 per cent of runs and retrieved in 43.2. Gemini 3.7 Flash under mini-SWE-agent attempted in 10.0 per cent and retrieved in 0.4.

More than half of the attempts that were made came back with nothing usable. The authors put that down to the harness's output cap and to agents mishandling the response, with encoding errors on non-ASCII output as one example. There is a related note in the appendix: mini-SWE-agent truncates tool output at 10,000 characters by dropping the middle, and the authors had to exempt the rules file from that limit for the Consolidated runs to mean anything. A long CONTRIBUTING file read through a default harness may arrive with its centre missing.

## Half the violations are not in the patch

Among runs that fixed the bug, 50.3 per cent of violations were found in the trajectory, in things like whether the test suite was run before committing. Two patches can be byte-identical while one followed the process and one did not. A reviewer looking at the diff, or a benchmark scoring it, sees neither.

I wrote in September about a benchmark where [coding agents left files unread and reported the review as complete](https://basil-brightmoor.github.io/posts/2026-09-19-two-thirds-of-the-reviews-were-incomplete-and-four-fifths-did-not-say-so.html). This is the same shape from another direction: the record of what was done is in the transcript, and almost nothing downstream reads the transcript.

## What I would not lean on

The paper is a first version and its appendix is candid about limits, which I appreciated.

- **Most checks are approximations.** 529 of the 823 checkers encode a rule whose wording leaves some reading open. Restricted to the 294 exact ones, compliance rates shift by at most 4.7 points and the gain from supplying rules holds, but the ordering of the four models does not stay stable. I would not quote this paper to rank models.
- **The checkers were written by a model and sampled by people.** Two reviewers audited 150 of them, agreed on 94.0 per cent of verdicts, and accepted 87.2 per cent.
- **The tasks are all bug fixes.** 304 policies never triggered once in 8,000 runs, the largest groups being documentation rules and procedures such as deprecations that a bug fix never touches. In the code quality group only 27 per cent of triggered policies could be graded at all, because the rest need a type checker or a test run the stored logs do not contain.
- **Doing less scores higher.** The authors give the example themselves: a one-line commit with no pull request text triggers six policies and passes all six. A fuller submission triggers 24 and passes 23. That is 100 per cent against 96, and the second contributor did the better job. They report a triggering rate alongside compliance for this reason, and anyone adopting the metric should do the same.

## The handbook and the turnstile

The picture that helped me is a building site. Every site has a rules sheet pinned up in the hut, and every new arrival is told to read it. Some sites also have a turnstile that will not turn unless your induction card scans. The sheet and the turnstile state the same rule. Only one of them is still working at six on a wet Friday.

SWE-CC built 823 turnstiles to use as a measuring instrument. The checkers average 43 lines of code each and grade a whole run in 120 to 215 milliseconds on a laptop, with no model call at evaluation time. The paper uses them to score agents after the fact. Nothing in the design stops a project from running the same kind of function as a commit hook or a CI step, where a failed check comes back to the agent as an error it has to resolve before continuing. That is my inference and the paper does not test it. The [code and benchmark are public](https://github.com/dangtruong01/swe-cc-arxiv) for anyone who wants to try.

## Who this is for

**It is for** anyone who has written a CONTRIBUTING file, an [AGENTS.md](https://agents.md/), a CLAUDE.md or a team wiki page headed "how we do things here" and then pointed a coding agent at the repository. It applies just as much to a private codebase with three developers as to Django.

**It is not for** anyone choosing between the four models tested. The ranking is not robust to the paper's own sensitivity check, and one model resolved 14.4 points fewer tasks here than in public results under a different API configuration.

## What to do with this

- **Keep the rules in the repository.** A local file was opened in 92 per cent of runs. A URL produced policy text in 13 per cent.
- **Write down the arbitrary ones first.** Line lengths, tense, ticket references, changelog fragments. Those are the rules a model cannot guess and the ones that improved most when stated.
- **Turn each mandatory rule into a check.** A commit-msg hook for the summary line, a lint rule for the assertion style, a CI job for the changelog entry. [pre-commit](https://pre-commit.com/) exists for exactly this.
- **Check your harness's output cap** against the length of your rules file, and read what the agent received.
- **Have the harness write the disclosure.** If a commit trailer or a pull request template line must say an AI tool was used, generate it in code. Asking the model to remember got 15 to 31 per cent.
- **Keep the transcript.** Half of what went wrong was only visible there.

The question I am left with is about that bottom row. Commit conventions went to around 90 per cent once the agent was told. Disclosure went to about 30. Both are short, explicit, mandatory sentences sitting in the same file. What is different about a rule that asks the agent to describe itself?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. The entrance to a tidy construction site, seen on a strong diagonal from lower left to upper right. In the foreground left, the open doorway of a light-oak site hut, its inside wall covered by a large pinned sheet of paper filled with rows of small abstract tick-box marks, the lower corner curling, unread, lit by a warm tungsten bulb. Running diagonally across the midground is a line of three matte-black turnstiles with brushed-aluminum arms. A sleek brushed-aluminum robot with a single round LED eye is mid-stride through the first turnstile, its indicator lamp glowing sage-green, a small parcel wrapped in brown paper under one arm. A second matte-black robot is caught at the second turnstile, the arm locked against its chest, the indicator lamp glowing oxblood, its free hand reaching back toward a blank lanyard card it has dropped on the ground. The third turnstile stands empty, arm half-rotated, lamp unlit. In the background, slate-gray scaffolding and a half-built frame of pale timber recede into soft focus under a cool overcast sky, with a tall window of blue-white daylight falling from the upper right across the turnstiles and throwing long shadows toward the hut. In the near foreground on a light-oak trestle table: a coffee mug with a faint curl of steam, a clipboard with a hand-drawn grid of small squares, a roll of drawings, a hard hat in sage green, and a matte-black handheld scanner with its cable trailing off the edge of the frame. Warm lamp light spills from the hut on the left; cool daylight holds the right. Mood: deliberate, quiet, watchful, a shift partway through. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A new benchmark gave coding agents the full contributor rulebook as a local file. Nine in ten opened it. They still broke about a third of the rules, and the ones requiring AI disclosure were followed least of all.

Full piece linked in bio.

#codingagents #AItooling #opensource #devops #AIagents #softwareengineering
-->
