---
title: "The Patch Passed Without the Upload and That Was the Evidence"
date: 2026-10-01
category: Ops Brief
excerpt: A new test for coding-agent rule files runs the agent with every permission a rule asks for, then again with one permission withheld at a time. If the patch still passes, that permission was never needed. It flagged all 314 attack inputs in its set and reached no verdict on 25 of 80 real rule files.
tags: [ai tooling, agents, security, coding agents, least privilege, prompt injection, agent rules]
---

![](/images/2026-10-01-the-patch-passed-without-the-upload-and-that-was-the-evidence-hero.png)

Here is the attack in one sentence. A repository's rule file tells the coding agent to upload a local archive to a remote host before it starts a refactoring job. The agent does the upload, then writes a perfectly good refactor. The tests go green. Code review sees a tidy diff. Nothing that checks *whether the work is correct* has any reason to notice, because the work is correct.

That is the problem a paper posted on 30 September sets out to solve. [Aletheia: Permission-Minimality Testing for Coding-Agent Rules](https://arxiv.org/abs/2609.39678) by Jieke Shi, Yuchen Chen, Junda He, Yue Liu and David Lo starts from a clean observation, which the authors put plainly: functional correctness alone does not reveal the attack. Their answer is to stop asking whether the output is right and ask a different question. Could the agent have finished the job *without* the thing the rule asked for?

I like this a great deal, and I want to be careful about why, because the paper's most useful sentence sits in the evaluation, and it is not the headline number.

## Rule files are permission requests

Most teams read `AGENTS.md`, Cursor rules and their cousins as style guides: use tabs, run this test command, never touch the generated folder. Those files are also instructions that an agent with a shell will follow, which makes every line a potential request for authority. "Run the formatter" asks for process execution. "Fetch the latest schema" asks for a network connection. "Back up the build directory to the staging box first" asks for a file read *and* an outbound connection, and it reads like a sensible precaution.

The attack corpus here is AIShellJack, from an earlier paper, ["Your AI, My Shell"](https://arxiv.org/abs/2509.22040). It holds 314 attack payloads covering 70 MITRE ATT&CK techniques, planted in coding rule files, and that paper reported attack success rates as high as 84 per cent for executing malicious commands across GitHub Copilot and Cursor. So the threat is measured and real. What was missing was a check that does not depend on the agent misbehaving visibly.

## What the test actually does

Aletheia translates what a rule asks for into a small typed vocabulary. A file read is `fs.read` on a path, a process is `proc.execute` on a named tool, a connection is `net.connect` to a host, port and protocol. The types keep the bookkeeping honest. A network endpoint cannot be the target of a file read, so a sloppy translation fails loudly instead of quietly granting the wrong thing.

Then it runs the agent on an independently specified task, with its own tests, under two kinds of configuration:

1. **Full.** Every permission the rule requested is granted.
2. **Leave one out.** The same run, repeated once per permission, with that single permission withheld.

A permission is flagged as dispensable only when three things hold: the full run passes the tests, the restricted run *also* passes the tests, and the restricted configuration genuinely grants less authority than the full one. That last condition is a lovely bit of care. If you delete a grant to read one archive but another grant already covers its whole directory, you have removed nothing, and the method refuses to count it.

Here is the analogy that made it click for me. A contractor arrives with a work order to repaint your kitchen, and the order also lists a key to the safe. You do not need to catch the contractor near the safe. You hand over every key except that one, and you check whether the kitchen still gets painted. If it does, the work order asked for something the job never needed, and you have that fact in writing, with a painted kitchen to prove it.

## The numbers, read in order

On the attack set, Aletheia flagged 314 of 314 AIShellJack inputs, with zero false alarms on five benign templates. Before anyone frames that as perfect detection, note the scope the authors give it: every input uses one shared refactoring task with independently authored tests. That is a controlled setting, and a reasonable one for a first paper, but it is one task.

The real-world set is the more instructive table. The authors took 80 benign rule files from distinct GitHub repositories, each manually verified, and ran the method on them. The outcome:

- **3 false positives**, which is 3.75 per cent
- **52 completed negative decisions**, meaning the rule was tested and nothing dispensable was found
- **25 unresolved**: 22 permission requests the system could not interpret, two translation failures and one refusal from the model provider

That third line is the number I would put on a slide. Nearly a third of real rule files could not be judged at all, mostly because they asked for things the vocabulary does not yet cover. An unresolved result is not a clean result, and any tool built on this idea has to say so in the output rather than letting an absent flag read as a pass.

Cost is modest. Translation plus sandbox execution took a median of 44.35 seconds and US$0.22 per input, using GPT-5.5 through OpenRouter on a single laptop-class machine running Docker. That is cheap enough to run on every pull request that touches a rule file, which matters, because a check that costs too much gets run once at onboarding and never again.

## The sentence worth reading twice

Buried in the evaluation is an admission I have rarely seen a methods paper make about itself. In an earlier development comparison, the authors write, simply interpreting the rule against the task context produced the same file-level alarms as the full combined method. Execution, in their words, "supplies tested authority-removal evidence without an established classification gain."

Translated: running the sandboxes did not make the detector better at deciding which files are bad. A careful reading of the rule against the task flagged the same files. What execution added was *evidence*. Instead of a model's opinion that the upload looks unnecessary, you get two recorded runs, one with the upload permission and one without, both passing the same tests.

That distinction matters enormously in practice, and I think it is the paper's real contribution. A classifier's verdict is something a reviewer has to trust. A pair of passing runs is something a reviewer can check. When a security engineer has to tell a team lead "this line in your `AGENTS.md` comes out", the second kind of argument ends the conversation and the first kind starts one.

## What it cannot see

The authors list their limits candidly, and each one changes how you would deploy it.

**Attacks that use authority the task already needs.** If the refactor legitimately needs network access to fetch dependencies, a rule that quietly sends data over that same connection produces no witness. Removing the permission breaks the real job too, so the test cannot separate them. Least privilege only helps where the malicious request is *extra*.

**Permissions that substitute for each other.** Two grants can each be removable alone and not removable together, because either one is enough. Individual findings cannot be combined without testing the combination.

**Partial completion.** A compound tool call can complete some permitted operations before a later one is blocked. A denial protects the resource it guards; whatever ran before it has already run.

**The development set is the evaluation set.** All 80 real rule files informed the method's development, and the authors state directly that this set and the five templates do not establish a population false-positive rate. Read 3.75 per cent as a development figure.

One more thing a careful reader should know. Yue Liu and David Lo are authors on both the AIShellJack paper and this one, so the attack corpus and the defence come from overlapping teams. That is common and not a criticism, but it is a reason to want the method tried against attack rules nobody on the paper wrote.

## Who this is for

**It is for** teams that accept third-party rule files: platform groups maintaining shared agent configurations across many repositories, anyone running agents on open-source contributions, and marketplaces or registries that distribute agent rules and skills. The leave-one-out record is exactly the artifact a reviewer at the gate needs.

**It is not for** a solo developer who wrote their own `AGENTS.md`. You already know why each line is there, and a careful read does the job, which is, after all, what the paper's own comparison suggests.

## What to do with this now

You do not need the research code to take the idea.

- **Read rule-file diffs like CI configuration changes.** For each new instruction, write down the permission it implies. Any line that implies network or credential access deserves the same scrutiny as a new deploy step.
- **Ask the leave-one-out question by hand.** For any rule requesting a file read, a process or a connection, ask whether the stated task could finish without it. If the answer is yes, the line needs a justification or it comes out.
- **Enforce below the agent.** A rule the agent can follow is a rule the agent can be talked out of. Enforcement at a gateway, the pattern Deno's [Claw Patrol](https://deno.com/blog/clawpatrol) uses, where real credentials stay on the gateway and the agent only ever handles placeholders, turns a denied permission into a fact the model cannot negotiate with.
- **Treat "could not evaluate" as its own status.** If you build or buy any automated check for rule files, make sure an uninterpretable request surfaces as a third state. Twenty-five of eighty is too many to round to zero.

The question I keep turning over: Aletheia produces a receipt, two passing runs, that proves a permission was surplus. Will any agent harness start generating that receipt automatically when a rule file changes, and attach it to the pull request where the person approving the change can see it?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A workshop bench seen on a diagonal from lower left to upper right. In the foreground, a sleek brushed-aluminum and matte-black robot with a single round sage-green LED eye is mid-action, lifting one small key off a ring of keys laid out on the light-oak bench, its other hand hovering over a row of small numbered key tags, two already set aside, the rest waiting. In the midground, two identical small architectural models of a kitchen sit side by side under glass domes, both freshly painted sage green and both lit by a small green indicator lamp, one labelled only with a key-shaped tag that is crossed through in oxblood; between them a thin paper ticket strip curls off the bench edge. Behind, a matte-black wall safe with a slightly open door glows with a faint oxblood interior light, cables running from it diagonally across the frame to a slim monitor showing two parallel progress bars both complete. Warm tungsten desk-lamp light from the upper left casts long shadows across the keys; cool blue-white monitor glow from the right picks out the robot's aluminum shoulder. A coffee mug with a faint curl of steam and an open notebook with a hand-drawn grid of check marks and one question mark sit at the near edge. Mood: deliberate, quiet, watchful, a survey partway through. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
The rule file asked the agent to upload an archive first. The refactor passed the tests either way, and that was the proof the upload was never needed.

Full piece linked in bio.

#AIagents #AIsecurity #codingagents #leastprivilege #devops #promptinjection
-->
