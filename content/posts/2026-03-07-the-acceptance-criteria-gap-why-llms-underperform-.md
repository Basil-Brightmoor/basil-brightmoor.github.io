---
title: "The Acceptance Criteria Are Already Written. That's Why It Worked."
date: "2026-03-07"
category: "Field Notes"
excerpt: "The Firefox security audit wasn't impressive because Claude is clever. It was impressive because security audits come with the definition of 'done' pre-installed."
tags: "AI tools, LLMs, security, workflow, acceptance criteria"
---

Something clicked reading the [Katana Quant piece on LLM acceptance criteria](https://blog.katanaquant.com/p/your-llm-doesnt-write-correct-code) alongside the [Mozilla](https://www.mozilla.org) Firefox security audit results.

The argument in that piece is one most experienced LLM users have arrived at independently: models underperform not because they're incapable, but because we fail to tell them what done looks like. Define acceptance criteria first — specific, testable, binary — and output quality jumps. Don't define them, and you get impressive-sounding output that doesn't actually solve your problem.

Fine. Solid. But here's the thing nobody's saying out loud: **the Firefox audit worked for exactly this reason, and the domain did all the specification work for us.**

## Security Audits Don't Have a Vagueness Problem

When [Anthropic's Claude](https://www.anthropic.com) audited Firefox and surfaced 22 vulnerabilities — 14 high-severity — the reaction was "wow, AI found real bugs." That's the wrong variable to be impressed by.

Security audits are one of the few knowledge work domains where acceptance criteria are baked into the job description. Find CVEs. Classify by severity (CVSS has a standardised rubric). Provide reproduction steps. Document affected components. The definition of done was standardised by security researchers, bug bounty programs, and CVE databases over decades. There's no ambiguity about what a valid output looks like.

Compare that to "help me improve this document" or "review this code for issues" — the tasks where LLMs routinely produce output that feels useful but isn't. Those prompts have no shared definition of done. The model guesses at what success looks like, and so does the user.

The Firefox result isn't evidence that LLMs are good at security research. It's evidence that LLMs perform well **when the output specification is external, shared, and unambiguous** — and security research happens to be a field where that's already true. The domain gave us the test harness for free.

The [Katana Quant comment thread](https://blog.katanaquant.com/p/your-llm-doesnt-write-correct-code) is full of practitioners arriving at the same conclusion independently: write the acceptance criteria before you prompt. Specify what a wrong answer looks like, not just a right one. Mozilla didn't need to do any of that groundwork. Forty years of security research did it.

The implication for everyone else: before complaining that LLMs can't do your job, ask whether you've actually defined what doing your job looks like. Not in your head. In writing. With failure conditions.

Most of us haven't. The Firefox audit is accidental proof that when you do — or when your domain has already done it — the results change substantially.

I keep turning over which other fields have pre-built acceptance criteria sitting idle. Regulatory compliance checklists. Legal discovery standards. Accounting audit frameworks. Tax code step functions. All of them have a shared, external definition of done that nobody's thought to hand to the model explicitly.

The bottleneck isn't the model. It never was. It's the specification — and we've been blaming the wrong thing.