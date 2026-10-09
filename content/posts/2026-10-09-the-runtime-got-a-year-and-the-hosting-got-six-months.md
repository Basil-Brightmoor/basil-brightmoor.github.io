---
title: "The Runtime Got a Year and the Hosting Got Six Months"
date: 2026-10-09
category: Ops Brief
excerpt: Deno's team is joining Cloudflare. The open source runtime gets a year of fixes and Deno Deploy shuts down in six months. The announcement names four things, and Deno KV is not among them.
tags: [Deno, Cloudflare, platform dependency, JavaScript runtime, Deno Deploy, migration, Durable Objects, operations]
---

![](/images/2026-10-09-the-runtime-got-a-year-and-the-hosting-got-six-months-hero.png)


Ryan Dahl's post this morning, ["Deno is joining Cloudflare"](https://deno.com/blog/cloudflare), has a section that begins "Here's what this means concretely." Four bullets follow. The Deno runtime gets "another year with monthly releases containing bug fixes and security updates," after which the team ends its development. [Deno Deploy](https://deno.com/deploy) "will continue operating for six months before shutting down." [JSR](https://jsr.io/) keeps running, with its infrastructure moving to Cloudflare. And [rusty_v8](https://github.com/denoland/rusty_v8) stays supported, with work toward integrating it into [workerd](https://github.com/cloudflare/workerd), Cloudflare's open source Workers runtime.

That is the whole list. If you run anything on Deno, the useful exercise today is to hold that list against your own stack and see which of your dependencies appear on it, which clock each one is on, and which do not appear at all.

## Two clocks, and the short one is on the part you cannot fork

The runtime gets twelve months of fixes, and the post adds that "Deno will remain open source, and we welcome others who want to continue its development." The hosted service gets six months.

The ordering makes sense from the company's side and it is worth seeing from the customer's side too. A runtime is source code. If its maintainers stop, the last release still runs, and anyone with the skill and the patience can carry it on. A hosting platform is machines, on-call rotas and a billing system. When it stops, nothing is left to carry on.

Think of a restaurant closing. The chef can publish every recipe, and you can cook from them for as long as you like. The kitchen itself still closes on the date on the door. Deno's customers got the recipe book and a year of corrections to it, and they got six months' notice on the kitchen.

Neither clock has a start date in the post. Counted from today, six months lands in early April 2027 and a year lands in October 2027. Deno's [stability and releases page](https://docs.deno.com/runtime/fundamentals/stability_and_releases/) still describes the earlier arrangement as of this morning: minor versions on a twelve-week schedule, and a long-term-support channel on the 2.9 line "maintained until January 31st, 2027." How that LTS promise sits beside the new one-year promise is not stated anywhere I could find. If a date matters to your planning, ask for it in writing.

## What the four bullets leave out

Deno's product shelf is longer than four items. Checking each against the announcement:

- **[Deno KV](https://docs.deno.com/deploy/kv/).** Not mentioned. On Deploy it is a managed database which the docs say is "backed by FoundationDB" in production. A database hosted on a platform that is shutting down has an obvious problem, and the post does not say what happens to the data.
- **[Deno Sandbox](https://deno.com/blog/introducing-deno-sandbox).** Not mentioned. Its February launch post describes the sandboxes as "lightweight Linux microVMs (running in the Deno Deploy cloud)" and bills them through the Deploy plan. I would assume it follows Deploy until someone says otherwise, and that is my inference.
- **[Subhosting](https://docs.deno.com/subhosting/manual/).** Not mentioned. This is the product other platforms use to run their own customers' code on Deno's infrastructure, so its fate reaches a second layer of people who may not know Deno is underneath them.
- **[Fresh](https://github.com/denoland/fresh)** and **[Claw Patrol](https://github.com/denoland/clawpatrol).** Not mentioned. Both are open source, so the code stays available whatever the team does next.

The [joint post on Cloudflare's blog](https://blog.cloudflare.com/deno-joins-cloudflare/), by Dahl and Cloudflare's Kenton Varda, does not fill these in. It is about the technology the two teams want to build, and it promises more announcements "in the coming months."

## This is the second move in a year

Deno Deploy customers have been through a migration recently. The platform that was [declared generally available](https://deno.com/blog/deno-deploy-is-ga) on 3 February replaced an older one, Deploy Classic, and Deno's [migration guide](https://docs.deno.com/deploy/migration_guide/) gives 20 July 2026 as the date Classic and the first subhosting API "will be shut down."

That guide is a fair preview of what a hosting move costs. Classic projects "are not automatically transferred," so each app had to be recreated and redeployed. Environment variables were re-entered by hand. Custom domains needed new DNS records. Existing KV data was not migrated automatically, and the guide's instruction was to contact support. Queues "are not supported on the new Deno Deploy," so anything that used them needed a replacement. The region count went from six to two.

Today's announcement comes 81 days after that July date. A team that finished the first move on the deadline has had under three months on the new platform before being told to plan the next one.

## Who gets help moving

The Deploy bullet ends with a qualifier: "We will provide migration support for paying customers moving to Cloudflare Workers."

Deploy's [pricing page](https://deno.com/deploy/pricing) lists a free plan with ten active apps, a million requests a month and a gibibyte of KV storage, then Pro at $20 a month and Builder at $200. Everyone on the free plan is on the same six-month clock, and the announcement does not say what, if anything, they are offered. I looked through Cloudflare's [Workers migration guides](https://developers.cloudflare.com/workers/static-assets/migration-guides/) this morning and found no page for Deno Deploy yet. One may well be coming. Today the documented path is a sentence in a blog post.

## The two letters that will catch people out

Here is the migration detail I would put on a sticky note. Deno has a product called KV. Cloudflare has a product called KV. They make different promises.

Deno's docs say "writes are always performed in strong consistency mode," that a strongly consistent read "will return the most recently written value," and that "Deno KV is capable of executing atomic transactions." Cloudflare's docs say [Workers KV](https://developers.cloudflare.com/kv/concepts/how-kv-works/) "achieves high performance by being eventually-consistent," that changes "may take up to 60 seconds or more to be visible in other global network locations," and that it "is not ideal for applications where you need support for atomic operations."

So an app that uses `kv.atomic()` to move a balance, claim a job or enforce a unique username cannot be pointed at the product with the matching name. Cloudflare's own page says where to look for stronger guarantees, which is [Durable Objects](https://developers.cloudflare.com/durable-objects/). That is a different programming model, and the port is a redesign of the data layer. The mapping from Deno KV to Durable Objects is my reading of the two sets of docs. Nobody at either company has published one.

For teams that want to keep the Deno KV API, there is [denokv](https://github.com/denoland/denokv), an MIT-licensed self-hosted backend built on SQLite. Its README is clear that backups and maintenance become yours.

## What is on the other side

The reason given for all this is [celld](https://celld.dev), a project Dahl started that Cloudflare's post says was released in August. It is an Apache-2.0 implementation of Workers and Durable Objects that you run yourself: one static binary of about 58 MB, with an object storage bucket as its only external dependency. The site labels the current version, v0.6.2, as beta.

The Cloudflare post is candid about why it wants this. Varda writes that workerd's Durable Objects support is "limited to a single instance," fine for local testing and unable to scale. The plan is to merge celld's code and ideas back into workerd so that self-hosting becomes "a first-class supported way" to run the Workers model.

I think that is a real gain for anyone worried about depending on Cloudflare. A credible way to run the same application on your own machines is the thing a platform customer should want most. It does have edges today. celld's [compatibility document](https://github.com/denoland/celld/blob/main/docs/cloudflare-compat.md) marks Node.js compatibility as partial, lists Workers AI, Vectorize, Hyperdrive and Browser Rendering as unsupported, and accepts only `wrangler.json` or `wrangler.jsonc` for configuration. The repository has pull requests disabled and takes patches by email.

There is an awkward symmetry here. The deal makes Cloudflare's platform easier to leave, and it does so by closing the platform Deno's customers were on.

## A call of mine that did not hold

I wrote in May, in a piece about [Bun and runtime governance](https://basil-brightmoor.github.io/posts/2026-05-04-the-execution-substrate-concentration-pattern-bun-.html), that Deno was "worth evaluating as the governance-stable alternative" for new MCP server projects. That recommendation was wrong on the exact property it claimed. Deno was a company-controlled runtime with a friendlier structure than Bun's, and a friendlier structure is no custody mechanism. The runtime in that comparison with one was [Node.js](https://nodejs.org/en), under the OpenJS Foundation.

The same post said forkability is a last resort and no substitute for governance. That part reads better today, since an open invitation for someone else to continue the runtime is now the stated plan for its future. And in June I wrote about [Cloudflare acquiring VoidZero](https://basil-brightmoor.github.io/posts/2026-06-04-the-javascript-toolchain-got-an-owner-too.html), the team behind Vite. Deno makes two JavaScript infrastructure teams joining the same company that I have covered.

## Who this is for

**It is for** anyone with an app on Deno Deploy, anyone whose product runs customer code through Subhosting, and anyone who chose the Deno runtime for a new service this year. It is also for people on Workers who have wanted a self-hosted exit and now have one in beta.

**It is not for** teams who only publish to or install from JSR, which continues, or teams running Deno on their own servers with no Deploy features. Those teams have a year of fixes and time to think.

## What to do this week

- **Search your code for the `Deno.` namespace.** `Deno.openKv` and `Deno.cron` are the calls that depend on the platform's own services. List the rest as well, since each one is something a new host has to provide.
- **Export your KV data now**, while support is staffed and nobody is in a hurry.
- **Find out which clock you are on.** Ask Deno for the shutdown date and the last-release date as dates.
- **Write down your consistency requirements** before choosing a storage target. Do it from the code, since the product names will mislead you.
- **Pin your Deno version in CI** and note when it stops receiving fixes.
- **If you are on the free plan, plan as though you are moving unassisted.**

The open question is who picks up the runtime. "We welcome others who want to continue its development" is an invitation with nobody named on it. Does a foundation, a fork or a company accept before October 2027?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A small restaurant kitchen being packed up mid-service, seen on a strong diagonal from lower left to upper right. In the foreground on a light-oak prep counter: an open ring-bound recipe book with pages of abstract diagram marks and one page lifted mid-turn, a ceramic mug with a faint curl of steam, a chef's knife on a folded cloth, a small potted herb in sage green, and two modern glass sand timers standing side by side, one tall and nearly full, one short and already half run, both catching warm light. In the midground a sleek brushed-aluminum robot with a single round LED eye is caught between two actions, one matte-black hand lowering a steel saucepan into a half-filled moving crate, the other hand still holding a ladle over a pot that is gently steaming on a slate-gray range. Three more crates sit along the diagonal in different states: one sealed and stacked, one open and half packed with pans, one empty with its flaps up. Behind the robot a second, smaller matte-black robot carries a stack of identical recipe books toward an open doorway. In the background, tall shelving stands half emptied, a row of oxblood enamel pots remains on the top shelf, and a glass door at the upper right lets in cool blue-white daylight with a blank card hanging in it, throwing long shadows back across the floor toward the counter. A warm tungsten pendant lamp lights the counter from the upper left; cool daylight holds the right side of the frame. A power cable from a matte-black stand mixer trails diagonally off the counter edge. Mood: deliberate, quiet, watchful, a move partway through. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Deno's team is joining Cloudflare. The open source runtime gets a year of fixes. The hosting platform gets six months. The announcement lists four things that have a plan, and the managed database is not one of them.

Full piece linked in bio.

#deno #cloudflare #javascript #devops #platformrisk #webdev
-->
