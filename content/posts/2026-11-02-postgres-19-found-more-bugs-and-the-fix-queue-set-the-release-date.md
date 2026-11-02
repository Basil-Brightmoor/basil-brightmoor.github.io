---
title: "Postgres 19 Found More Bugs, and the Fix Queue Set the Release Date"
date: 2026-11-02
category: Ops Brief
excerpt: PostgreSQL 19 is running about a month behind the project's usual window. Robert Haas puts it down to LLM-found bugs, and his commit counts show where the time went. Commits to the stable branches rose by 60 to 74 percent. Commits that only touched new development went down.
tags: [PostgreSQL, open source maintenance, AI bug finding, release engineering, code review, LLMs]
---

![](/images/2026-11-02-postgres-19-found-more-bugs-and-the-fix-queue-set-the-release-date-hero.png)

PostgreSQL major releases have recently landed between mid-September and mid-October. PostgreSQL 19 is now [planned for 19 November 2026](https://www.postgresql.org/about/news/postgresql-19-rc-1-released-3409/), and the [project roadmap](https://www.postgresql.org/developer/roadmap/) still says "October 2026." Three major features were pulled out of it during beta, between 27 August and 15 September. Robert Haas, a PostgreSQL committer who works at Databricks, has written up why, under a title that doesn't hedge: [Postgres 19 is late, and it's AI's fault](https://neon.com/blog/postgres-19-is-late-and-its-ais-fault) (also [on his own blog](http://rhaas.blogspot.com/2026/10/postgres-19-is-late-and-its-ais-fault.html)).

The headline will get read as "AI broke Postgres." The commit counts in the post say something narrower and more useful. Finding bugs got much cheaper. Fixing them got only somewhat cheaper. A release ships when the fixing is done, so the release date followed the slower of the two.

## What was pulled, and when

The three reverted features, per Haas:

- `UPDATE`/`DELETE ... FOR PORTION OF`, the SQL-standard way to update part of a row's validity period
- SQL Property Graph Queries (SQL/PGQ)
- `ALTER TABLE ... MERGE PARTITION` / `SPLIT PARTITION`

PostgreSQL's feature freeze falls on 8 April each year. Pulling a major feature months after freeze is unusual for the project, and pulling three in one cycle is more so. The team reverts when it can't get a feature to release quality in time, which is the conservative choice. It does mean the decision ran into August and September, during the stretch normally spent preparing a release.

## The numbers that do the arguing

Haas counted commits between feature freeze (8 April) and 25 September, in 2025 and in 2026:

- **Master:** 1,037 commits in 2025, 1,443 in 2026. That's up by about 39 percent.
- **The branch being released** (REL_18_STABLE last year, REL_19_STABLE this year): 724, then 1,169. Haas puts it as "more than 60%."
- **The previous release's branch** (REL_17_STABLE, then REL_18_STABLE): 248, then 433. More than 74 percent.

The detail that carries the argument is the one Haas mentions almost in passing. Commits that landed on master *only*, the new-development work that wasn't back-patched to a stable branch, "declined slightly" year on year. All of the growth came from fixes going backwards into code that had already shipped or was about to.

This counts commits, not bugs. One fix can take several commits and one commit can close several bugs, so the percentages measure how busy the back-branches were. They can't tell you how many bugs there were. Taken that way, the counts fit Haas's reading closely. People shipped about the same amount of new work as last year, and spent a lot more effort fixing existing code.

## Why Haas blames finding, not the committers

Haas doesn't think the committers got sloppier. His reading is that they worked as carefully as before, and that LLM-assisted bug reports surfaced more of the mistakes already in the code. He writes that a huge number of people are now reporting PostgreSQL bugs they found using LLMs. He doesn't name particular tools, and neither will I. He describes the codebase as old and large, with git history converted from CVS that goes back more than 30 years. Old, heavily used C code is exactly where a tireless reader finds things.

His summary of the gap: it has "become vastly easier to find those bugs," and fixing them "has also gotten easier, but not to the same degree."

He gives two reasons the release slipped. LLMs can draft a patch, but the drafts "aren't always correct or compliant" with PostgreSQL's standards, so a committer still has to review and own every fix. And the same people who would have been deciding what to revert were busy with security issues and back-branch bugs. Several features were reverted late because the people who would have decided on them earlier were busy fixing bugs.

## The analogy: smoke detectors in an old house

Think of an old house that gets sensitive smoke detectors fitted in every room. The house was no more dangerous the day before. But now there are alarms all over the place, and the same single electrician has to check every one. Some alarms come with a suggested repair written on a sticky note, and some of those suggestions are wrong, so the electrician can't just follow them. Meanwhile, the extension you were planning to build waits, because the electrician is busy with the wiring you already have.

The detectors are a real improvement. The house ends up safer. The bottleneck is the electrician's hours, and nobody installed a second electrician.

## Who should care, and how much

**Teams planning a PostgreSQL 19 upgrade.** The practical effect is small. GA is planned for 19 November, about a month late, and the three reverted features are simply not in 19. If your plans depended on SQL/PGQ, temporal `FOR PORTION OF`, or partition merge and split, move them to a later release and watch whether they come back in 20. Haas himself says the delay doesn't worry him much. The fix counts on REL_18_STABLE also suggest the next few minor releases of 18 will carry more fixes than usual, which is worth reading in the release notes before you patch.

**Maintainers of any long-lived open-source project.** Read this as a capacity warning. If your codebase is old enough to have interesting bugs, outside readers with LLMs will start finding them whether or not you run the tools yourself. Your fix rate is set by how many people can review and commit, and that number did not change when the find rate did. The useful thing to measure is how far the incoming reports outrun what your reviewers can handle.

**Engineering leaders running LLM bug hunts on internal code.** The lesson carries straight over. Before you point a scanner at a twenty-year-old service, decide who will triage what it finds and how much of their week that takes. A list of 400 real bugs and nobody to fix them leaves you holding a liability you now know about, with no plan for it.

**Not much for you if** you're on a managed Postgres service and upgrade when your provider tells you to. Your provider takes on the timeline risk, and the extra stable-branch fixes reach you as routine patching.

## What to watch, and what to do

Three concrete things.

1. **Count your own back-branch traffic.** If you maintain anything with release branches, Haas's method is cheap: commits on each branch between two fixed dates, this year against last. A jump in back-patches while new-development commits stay flat is the same signature PostgreSQL saw, and you can spot it months before a release slips.
2. **Treat an LLM-drafted patch as part of the bug report until someone has reviewed it.** The PostgreSQL experience is that a drafted patch still needs a committer's full review. Budget the review time as if the patch weren't there, and count it as a bonus when the patch turns out to be right.
3. **Watch the 20 cycle.** Haas asks openly how the project will catch up on decades of latent bugs and keep adding features, and says he doesn't yet know. The next feature freeze is in April. If the reverted features return and the back-branch counts settle, the find rate was a one-off backlog being cleared. If the counts stay high, PostgreSQL's release dates will depend on how many people can review fixes.

Haas ends on a challenge to his own field. Every developer will need to "raise their game," because new features will now be read by machines that don't get tired. My question for every other project with a thirty-year history is a practical one: who on your team is the electrician, and how many hours a week do they have?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, mid-century-modern sensibility with contemporary edge, photographic-painterly framing, clearly art and not photorealistic. Cutaway view of an old wooden house interior rendered like a dollhouse cross-section on a strong diagonal across the frame: in several of its small rooms, sleek round ceiling smoke detectors glow with sage-green and oxblood indicator lights, some blinking. In the foreground, on a light-oak workbench, a sleek brushed-aluminum robot with a matte-black head and a single round LED eye is caught mid-action, holding a small multimeter probe to an exposed tangle of old cloth-wrapped wiring with one hand while reaching back with the other toward a growing stack of small paper tags, each tied with string, piled at the bench's edge; several tags carry pinned yellow sticky notes. In the midground, three partly built wooden room extensions sit unfinished on sawhorses under a dust sheet, one sheet half pulled back. In the background, a corkboard of pinned floor plans with oxblood string, shelves of labelled parts drawers, and a tall window. Warm tungsten lamp light from the upper left, cool blue-white daylight and monitor glow from the right, long diagonal shadows, wiring and cables leading the eye from the foreground bench to the window. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful, slightly tired but alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Postgres 19 is a month late. The commits that only touched new work went down a little this year, and fixes to code that had already shipped went up by more than 60 percent. LLMs made finding bugs cheap, and someone still had to fix them.

Full piece linked in bio.

#PostgreSQL #OpenSource #AIAgents #DevOps #SoftwareEngineering #CodeReview
-->
