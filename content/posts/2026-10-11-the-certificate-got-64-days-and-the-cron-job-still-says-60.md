---
title: "The Certificate Got 64 Days and the Cron Job Still Says 60"
date: 2026-10-11
category: Ops Brief
excerpt: Let's Encrypt moves its default certificate from 90 days to 64 on 10 February 2027, then to 45 in 2028. A renewal job hardcoded to 60 days keeps working next year, on four days of slack.
tags: [Let's Encrypt, TLS certificates, ACME, certificate renewal, cron, automation, monitoring, operations, devops]
---

![](/images/2026-10-11-the-certificate-got-64-days-and-the-cron-job-still-says-60-hero.png)


Somewhere on a server you are responsible for, there is probably a line that renews a TLS certificate every 60 days. It may be a cron entry, a wrapper script somebody wrote in 2019, or a sentence in a runbook. It was correct when it was written. A [Let's Encrypt](https://letsencrypt.org/) certificate lasted 90 days, so renewing at day 60 left a month to notice if something went wrong.

On Wednesday Let's Encrypt [confirmed the date](https://letsencrypt.org/2026/10/07/64-day-certs.html) on which that month shrinks. From 10 February 2027, certificates issued or renewed on the default settings are valid for 64 days. The staging environment starts issuing 64-day certificates this Wednesday, 14 October, so there are four months in which to test. The last 90-day certificate is expected to expire on 11 May 2027. In 2028 the default drops again, to 45 days.

The announcement asks subscribers to search their cron jobs, wrapper scripts and runbooks for the numbers 83, 80 and 60. I think that one sentence is the most useful thing in it, and the arithmetic behind it is worth doing slowly.

## What is changing, and what is not

The schedule, as Let's Encrypt gives it across this week's post and the [plan it published last December](https://letsencrypt.org/2025/12/02/from-90-to-45):

- **14 October 2026.** Staging begins issuing 64-day certificates.
- **10 February 2027.** The default profile moves to 64 days. The period for which a completed domain validation can be reused falls from 30 days to 10.
- **11 May 2027.** The last 90-day certificate is expected to expire.
- **16 February 2028**, per the December plan. The default moves to 45 days and validation reuse falls to seven hours.

Let's Encrypt says it will not revoke valid certificates as part of this. The ACME endpoints and the issuance chains stay as they are. Rate limits do not need adjusting either, because [renewals are exempt from them](https://letsencrypt.org/2026/02/24/rate-limits-45-day-certs), although the same February post expects daily renewal requests to roughly double.

The reason for all of it sits upstream. The CA/Browser Forum [voted in 2025](https://cabforum.org/2025/04/11/ballot-sc081v3-introduce-schedule-of-reducing-validity-and-data-reuse-periods/) to bring the maximum lifetime of a public TLS certificate down from 398 days to 47 by March 2029. Let's Encrypt's [profiles page](https://letsencrypt.org/docs/profiles/) lists the intermediate ceiling as 100 days from 15 March 2027. So this is every certificate authority's timetable, and Let's Encrypt is running ahead of it.

## Three numbers, three outcomes

Here is my own arithmetic on the three numbers the announcement names. Each is a count of days after issuance at which a script asks for a new certificate.

**83 and 80.** These were cautious settings for a 90-day certificate, leaving a week or ten days. Against a 64-day certificate they fire 19 and 16 days after it has expired. A site on one of these gets its first 64-day certificate at its first renewal after 10 February, and goes dark 64 days later. By my count that lands somewhere between mid-April and early July 2027, two months or more after the change that caused it.

**60.** This one survives. A certificate that lives 64 days and is renewed at day 60 has four days to spare. So the script works through 2027, and everybody concludes it is fine. Then the default becomes 45 days in February 2028, and the same script waits until 15 days after expiry before it tries.

I find the 60 case the more worrying of the two, because it passes the test. Anyone who points that script at staging next week will see a renewal succeed. What they will not see is that the allowance for failure has gone from thirty days to four. A renewal can fail for dull reasons: a DNS provider's API has a bad afternoon, a firewall rule changed, a disk is full. On 90-day certificates there was a month to catch it. On 64-day certificates with a 60-day trigger there is a long weekend.

One more detail if the trigger is a calendar cron rather than a day count. An entry that runs on the first of every second month fires at intervals of between 59 and 62 days, depending on which months it spans. Against 64 days that leaves two days in the worst case.

## The meter and the alarm

Think of a parking meter that takes coins for up to 90 minutes, and a phone alarm set for 60. The routine is sound: the alarm goes, you walk back, you feed the meter with half an hour in hand. The council then changes the meter to a maximum of 64 minutes. The alarm still works if you walk briskly and nobody stops you for a chat. Next year the maximum becomes 45 and you are ticketed every time.

The council also stopped leaving a warning slip under the wiper. Let's Encrypt [ended its expiry notification emails on 4 June 2025](https://letsencrypt.org/2025/06/26/expiration-notification-service-has-ended), citing better automation among subscribers, privacy, and a cost in the tens of thousands of dollars a year. I have no quarrel with the decision. It does mean that if the renewal job stops, the certificate authority will not tell you. Unless you have built monitoring of your own, the first notice is a browser warning on your site.

## The date is in the protocol now

The fix Let's Encrypt recommends is to stop keeping the number on your side at all. ACME Renewal Information, standardised as RFC 9773 and [introduced by Let's Encrypt in 2023](https://letsencrypt.org/2023/03/23/improving-resliiency-and-reliability-with-ari), lets the client ask the server when a given certificate should be renewed. When the lifetime changes, the answer changes, and nobody edits a cron entry.

Two common clients show where things stand. [Certbot's documentation](https://eff-certbot.readthedocs.io/en/stable/using.html) says that from version 4.0.0 a certificate is ready for renewal when less than a third of its lifetime remains, or half for certificates of ten days or less. Before 4.0.0 the threshold was a fixed 30 days. Both behaviours work at 64 and at 45. The [acme.sh README](https://github.com/acmesh-official/acme.sh) says it renews every 30 days by default, or earlier when the certificate authority's renewal information says so, with no flag needed.

So a current client on its own schedule is in good shape. The exposure is in what has been wrapped around the client: a cron line that calls it only every two months, a renewal-interval override somebody set years ago to be polite to the rate limits, a deploy script that copies the certificate to a load balancer on its own timer, or an old packaged version that predates all of this. For clients without renewal information, Let's Encrypt's guidance is to renew at about two thirds of the lifetime. That is day 43 of 64, and day 30 of 45.

I wrote last month about [a study of retired language models](https://basil-brightmoor.github.io/posts/2026-09-28-the-shutdown-date-was-published-and-the-only-reader-was-an-inbox.html) in which the shutdown date was public the whole time and an estimated 82 per cent of migrations still landed after it, because nothing in the running application ever read the date. Renewal information is what the other design looks like. The party that sets the deadline hands it to the software that has to meet it, inside the exchange the two already have. I would like model providers to copy it.

## The quieter change: validation reuse

The second number in the announcement will catch a smaller group. Today, once you have proved control of a domain, Let's Encrypt will reuse that proof for 30 days. From February that becomes 10 days, and in 2028 seven hours.

A fully automated client validates on every issuance and will not notice. The people affected have a manual step somewhere: a DNS record that a human adds because the DNS provider has no API, or a validation done on one machine and an issuance done later on another. With a seven-hour window, every renewal needs a fresh proof.

The December plan describes a remedy, a challenge type called DNS-PERSIST-01, in which the DNS record is set once and does not change at each renewal. Let's Encrypt said then that it expected to offer it in 2026. The [challenge types page](https://letsencrypt.org/docs/challenge-types/) I checked today, last updated in February, does not list it yet, so check before you plan around it.

## Who this is for

**It is for** anyone running their own ACME client on a server, a NAS, a mail host or an internal appliance. It matters most where the set-up is old and nobody remembers who did it, and for consultancies that left such set-ups behind at clients.

**It is not for** sites whose certificates are issued by a managed platform, such as a hosted site builder or a CDN that terminates TLS for you. The platform owns the renewal, and the question to ask it is whether it has tested against 64 days.

## What to do before February

- **Search for the numbers.** Look through crontabs, systemd timers, wrapper scripts and runbooks for 83, 80 and 60, and for any schedule that runs less often than weekly.
- **Check the client version** and whether it supports renewal information. Upgrade before changing anything else.
- **Run the client often and let it decide.** Certbot's own example runs twice a day. The job is cheap when nothing is due.
- **Point a copy at staging after 14 October** and confirm a 64-day certificate renews and deploys. Test the reload step, since a renewed certificate that the web server never loads is the classic way for this to fail.
- **Add an expiry alert that does not depend on the renewal job.** Something outside the server that reads the certificate and complains at a fixed number of days remaining. Let's Encrypt keeps [a list of monitoring options](https://letsencrypt.org/docs/monitoring-options/).
- **Find any manual validation step** and decide now what replaces it.

The 60-day script is the one I keep coming back to. It will pass in staging and it will work through 2027, and it will be working with four days of slack where it used to have thirty. How many other scheduled jobs are sitting on a margin that someone else has quietly spent?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A light-oak workshop bench runs on a strong diagonal from lower left to upper right. Along it stand three hourglasses of clearly decreasing size, largest at the left and smallest at the right, each with oxblood sand at a different stage: the large one nearly run out and set aside, the middle one half run, the small one freshly turned. In the midground a sleek brushed-aluminum robot with matte-black joints and a single round LED eye is caught between two actions: one hand is turning the middle hourglass over, the other is reaching toward an old mechanical kitchen timer in matte black whose dial is wound far past where the middle hourglass will empty. In the foreground: a ceramic mug catching warm light, a paper wall calendar lying flat with a diagonal row of blank squares crossed off in sage-green pencil, a ring of small blank steel padlocks, one open, and a clipboard with abstract tally marks. A long cable runs from the kitchen timer diagonally off the bench edge to a small matte-black server unit with a single sage-green indicator light. In the background, shelves of numbered cubbies recede into soft focus, each holding a small closed padlock, and one cubby near the right is empty and dark. A tall window at upper right lets in cool blue-white morning light that throws long shadows back along the bench; a warm tungsten desk lamp lights the hourglasses from the upper left. Mood: deliberate, quiet, watchful, a routine that still works with almost no time to spare. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Let's Encrypt certificates drop from 90 days to 64 on 10 February 2027. A renewal job hardcoded to 60 days keeps working, with four days of slack where it used to have thirty. In 2028 the limit is 45 and that job fails every time.

Full piece linked in bio.

#devops #letsencrypt #tls #automation #sysadmin #webops
-->
