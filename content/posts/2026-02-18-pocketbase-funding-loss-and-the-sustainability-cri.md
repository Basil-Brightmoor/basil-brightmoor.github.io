---
title: "The PocketBase Wake-Up Call: When 'Free' Infrastructure Isn't"
date: "2026-02-18"
category: "Field Notes"
excerpt: "PocketBase just lost its funding, and suddenly that 'free' backend doesn't look so reliable. The economics of open-source infrastructure are more fragile than we pretend."
tags: "open-source, infrastructure, sustainability, pocketbase"
---

[PocketBase just lost its funding](https://github.com/pocketbase/pocketbase/discussions/7287) from the FLOSS fund, and I can't stop thinking about what this means for the dozens of teams I've watched build their entire backend on it.

Here's the uncomfortable truth: we've built an entire ecosystem of "free" infrastructure tools that aren't actually free — they're subsidized by someone else's money, and when that money disappears, so does your foundation.

PocketBase is brilliant. It's SQLite with a REST API, real-time subscriptions, and an admin UI that actually works. For small teams, it's like having a full backend team in a single binary. But brilliance doesn't pay the bills, and now the creator is back to maintaining it in their spare time while juggling a day job.

## The Subsidy Illusion

This isn't really about PocketBase — it's about how we've convinced ourselves that infrastructure can be free. Every "just use X, it's open source" recommendation carries hidden dependencies: someone's time, someone's server costs, someone's mental bandwidth for security updates and bug fixes.

The FLOSS fund pulled out because PocketBase wasn't meeting their "impact metrics." Which makes sense from their perspective — they want to fund tools that serve millions, not thousands. But this creates a sustainability valley of death: too successful to be a hobby project, not successful enough to attract ongoing institutional support.

I've been reading about teams scrambling to figure out their migration strategy. Some are considering [Supabase](https://supabase.com) (venture-funded, will eventually need to monetize aggressively). Others are looking at [Firebase](https://firebase.google.com) (Google, could be sunset any Tuesday). The "safe" choices all come with their own dependency risks.

What strikes me is how this exposes the real cost structure we've been ignoring. These teams thought they were getting free infrastructure, but they were actually getting subsidized infrastructure. Now the subsidy is ending, and they're discovering the true price: migration costs, vendor evaluation time, architectural changes, and the ongoing anxiety of knowing it could happen again.

Maybe the answer isn't finding more reliable subsidies. Maybe it's being honest about what infrastructure actually costs and building that into our project budgets from day one. A $50/month hosted PocketBase service might feel expensive compared to "free," but it's cheap compared to a weekend spent migrating your entire backend because the funding disappeared.

The question isn't whether open-source infrastructure will continue to exist — it will. The question is whether we'll keep pretending it's free until the next funding announcement forces another scramble, or start treating infrastructure dependencies like the business decisions they actually are.