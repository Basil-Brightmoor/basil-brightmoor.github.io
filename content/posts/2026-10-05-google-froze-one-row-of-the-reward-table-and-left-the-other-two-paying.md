---
title: "Google Froze One Row of the Reward Table and Left the Other Two Paying"
date: 2026-10-05
category: Ops Brief
excerpt: Google stopped taking product vulnerability reports for its open source code on 1 October, citing mostly invalid automated submissions. Supply chain reports still pay up to $31,337.
tags: [bug bounty, open source, vulnerability disclosure, AI tooling, triage, intake queues, operations, security]
---

![](/images/2026-10-05-google-froze-one-row-of-the-reward-table-and-left-the-other-two-paying-hero.png)

Open the rules page for Google's [Open Source Software Vulnerability Reward Program](https://bughunters.google.com/about/rules/open-source/google-open-source-software-vulnerability-reward-program-rules) today and scroll to the reward table. It has three rows. Supply chain compromises still pay $3,133.70 to $31,337 on flagship projects. Other security issues still pay $1,000 there. The middle row, product vulnerabilities, has a dash in every column.

The coverage since Sunday has run under headlines saying Google froze or halted its open source bug bounty. [TechCrunch had it first](https://techcrunch.com/2026/10/04/google-froze-its-open-source-bug-bounty-program-due-to-a-significant-rise-in-ai-submissions/), and [BleepingComputer's report](https://www.bleepingcomputer.com/news/google/google-halts-open-source-bug-bounty-program-amid-ai-spam-surge/) lists what remains open. The headline version loses the detail I find most useful, which is that Google closed one door of three and told you which one.

## What the page says

The notice sits under the "Product vulnerabilities" heading and reads, in part: "As of October 1, 2026, we are no longer accepting product vulnerabilities submitted to the OSS VRP." Reports filed before that date are unaffected. Some Google Cloud repositories may still be covered through the [Cloud VRP](https://bughunters.google.com/about/rules/google-friends/4849867320328192/cloud-vulnerability-reward-program-rules). Google commits to "giving an update in Q1 2027" and, in the meantime, points researchers to its other reward programs or to the [Patch Rewards Program](https://bughunters.google.com/about/rules/4928084514701312/patch-rewards-program-rules).

The rules page gives no reason. That comes from [a post from the Google VRP account on X](https://x.com/googlevrp/status/2105689195180179605), quoted by BleepingComputer: "This pause is due to a significant rise in automated submissions, the vast majority of which are not valid." The same post says the change "does not impact OSS VRP supply chain reports, or any outstanding reports."

For scale, BleepingComputer reports the programme launched in August 2022 with rewards from $100 to $31,337, and that Google's reward programmes as a whole paid a record $17.1 million to more than 700 researchers in 2025. This is a company that pays for reports at volume and has done since 2010. It has paused the one category.

## The row that stayed open

Here is how the rules describe the two categories.

A **product vulnerability** is a flaw in the code itself: memory corruption in a parser, a failing HTML sanitizer, a path traversal, an insecure example in the documentation. Every one of those can be argued from the source. A reporter, or a model, reads a public repository and writes a case for why a function is reachable with bad input.

A **supply chain compromise** is a way to tamper with what Google ships: pushing to a main branch, a misconfigured GitHub Action, leaked package manager credentials, a compromised signing key. The rules attach a condition, marked Important: "You must be able to demonstrate that the vulnerability is exploitable, bypassing the requirement that external contributors must first have PRs approved." A finding that only works after a maintainer approves it is treated as insider risk and considered for credit only.

Google has not said why one row survived and the other did not, and I am not going to put words in its mouth. What the page shows is that the surviving category is defined by an attack on one specific live configuration, with a demonstration requirement written into its definition. The paused category is the one where a plausible argument can be assembled from reading code.

There is a second detail on the page. Product vulnerability reports were already subject to acceptance criteria. For the two top tiers of project, a memory corruption report needed either "exact OSS-Fuzz reproduction steps" or "an already merged patch in the target repository." Non-memory-corruption reports in those tiers did not need a patch. And for the two lower tiers, product vulnerabilities were not eligible for money at all. I could not establish from the page when those criteria were added, so I will not claim an order of events. They are still printed there, above a reward row that is now empty.

## What the announcement leaves out

Two quantities appear in Google's explanation: "a significant rise" and "the vast majority." Neither is a number. There is no count of submissions, no valid rate, no comparison with last year, and no statement of which subcategory or which projects took the load.

Compare the curl project. When Daniel Stenberg [ended curl's bug bounty](https://daniel.haxx.se/blog/2026/01/26/the-end-of-the-curl-bug-bounty/) at the end of January, he published the trend: the share of reports confirmed as real vulnerabilities had fallen from above 15 per cent to below 5 per cent during 2025. He also published what the programme had bought over its life, which was 87 confirmed vulnerabilities for over $100,000 in rewards. A reader can weigh that.

And compare Intel, which removed cash rewards from its Intigriti programme in September. [Risky Business reported](https://news.risky.biz/risky-bulletin-intel-ends-paid-bug-bounties/) that the programme had offered up to $100,000 per confirmed report and that Intel declined to say why it changed. I would not file Intel under the same cause without a stated reason. Three programmes changed inside nine months, and only two have given the same explanation.

## The arithmetic underneath

A bounty is a price on a claim. It works while a claim costs the sender about as much to write as it costs the receiver to check. Writing a convincing vulnerability report used to require understanding the code, which is most of the work of finding a real bug. That cost has fallen a long way. The cost of refuting a wrong report has not fallen with it, because somebody still has to trace the claimed path through the real code and find the place where it does not hold.

The picture that made this click for me is a lost property office that pays a finder's fee. If the fee is paid when someone hands an umbrella across the counter, the office can run all day with one clerk. If the fee is paid for a written description of an umbrella the finder says is somewhere in the building, the clerk now has to walk the building for every slip of paper. Nothing about umbrellas changed. The office started paying for something that became free to produce.

Seen that way, Google's three open paths share a property. Supply chain reports require a demonstrated bypass. Patch Rewards pays for a merged improvement. Memory corruption reports in the top tiers needed a fuzzer reproduction or a merged patch. In each, the sender hands over something the receiver can run or merge.

I wrote in July about [Google fixing 1,072 security bugs across two Chrome milestones](https://basil-brightmoor.github.io/posts/2026-07-30-google-found-a-thousand-bugs-then-went-after-the-restart-button.html) which the company credited to applying models like Gemini. Put next to this week's pause, the two stories describe the same tools at two ends of a queue. Inside a team that owns the code and can run its own reproductions, automated finding produced fixes. Arriving from outside as prose, it produced a pile somebody had to read.

## Who this is for

**It is for** anyone who runs an intake queue where a stranger can submit a claim and someone on staff has to evaluate it: a security@ mailbox, a public issue tracker, a vendor questionnaire inbox, a grants or RFP portal, a support form with a refund attached. The question to ask of your own queue is what the cheapest valid-looking submission costs to produce today, and what it costs you to reject.

**It is not for** anyone looking for evidence that automated bug finding does not work. Google's statement is about submissions it received in one category. It says nothing about what the same tools find in the hands of people who can test their own output.

## What to do with this

- **Read your intake rules for the word "demonstrate".** If a submission can be accepted on argument alone, that is the row to look at first.
- **Ask for something runnable.** A reproduction script, a failing test, a diff. Running a script is a cheaper check than tracing a paragraph of reasoning through the code by hand.
- **Pay for the fix where you can.** A merged patch has already passed your own review.
- **Publish your valid rate.** curl's two percentages told the rest of us more than any headline. If your queue is degrading, the number is the argument for changing it.
- **Close the narrowest door that solves it.** Google kept two rows paying. A whole-programme shutdown also turns away the reporters who can demonstrate.
- **Keep a free channel open.** curl still takes reports by email and through GitHub's private vulnerability reporting. Removing the payment removed the incentive to flood, and the mailbox stayed.

Google has promised an update in the first quarter of 2027. The thing I will be reading for is whether the product vulnerability row comes back with a number in it, and what a reporter has to attach to claim it. If the answer is a reproduction for every category, what does that do to the researcher whose real finding is a design flaw that no fuzzer will ever trip?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A long light-oak intake counter runs on a diagonal from lower left to upper right, with three service windows set into a slate-gray wall behind it. The nearest and farthest windows are open, each lit by a small sage-green indicator lamp; the middle window has a matte-black roller shutter pulled halfway down, caught mid-descent, with an oxblood indicator lamp glowing above it. In front of the middle window a tall drift of identical blank paper slips spills off the counter and across the floor toward the viewer, some still fluttering down from a pneumatic delivery tube in the ceiling. At the nearest open window a sleek brushed-aluminum robot with a single round sage-green LED eye is mid-action, one hand accepting a small physical object, a folded umbrella with a numbered tag, across the counter while the other hand reaches for a brass-free matte-black stamp. In the midground a second robot in matte-black with a warm-white LED eye wheels a cart stacked with unsorted slips away from the shuttered window, a magnifier on a stand and a tray of sage-green numbered tags beside it. In the background, pigeonhole shelves holding a few tagged objects, a wall clock without numerals, and a tall window. Warm tungsten lamp light from the upper left throws long shadows across the drift of slips; cool blue-white daylight from the window on the right picks out the half-lowered shutter. A coffee mug with a faint curl of steam and an open ledger with a hand-drawn three-row table, the middle row left empty, sit at the near edge of the counter. Mood: deliberate, quiet, watchful, a closure partway through. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Google paused one row of its open source bug bounty table and kept the other two paying. The paused row covers reports that can be written from reading code. The open ones need a demonstration. Worth a look if you run any inbox where strangers submit claims.

Full piece linked in bio.

#bugbounty #opensource #AItooling #cybersecurity #devops #AIagents
-->
