---
title: "The Extension That Breached GitHub"
date: "2026-05-30"
category: "Ops Brief"
excerpt: "A poisoned Nx Console build was live in the VS Code Marketplace for about eighteen minutes on May 18. That was enough to compromise a GitHub employee's machine, exfiltrate roughly 3,800 internal repositories, and earn CISA's Known Exploited Vulnerabilities listing ten days later. The eighteen-minute number is the one to sit with."
tags: "supply chain security, Nx Console, VS Code extensions, GitHub breach, CI/CD credentials, CISA KEV, Megalodon, ops brief"
---

![](/images/2026-05-30-the-extension-that-breached-github-hero.png)

On May 18, 2026, a malicious build of [Nx Console](https://marketplace.visualstudio.com/items?itemName=nrwl.angular-console) — a Visual Studio Code extension with [over two million installs](https://thehackernews.com/2026/05/compromised-nx-console-18950-targeted.html) — was published to the [Visual Studio Marketplace](https://marketplace.visualstudio.com/) at 12:30 PM UTC. It was pulled at 12:48 PM UTC. About eighteen minutes of live distribution. [StepSecurity](https://www.stepsecurity.io/blog/nx-console-vs-code-extension-compromised) put the activation count at roughly 6,000 over the next two days, including from Cursor, because VS Code's automatic update mechanism does not need anyone to click anything.

One of those activations was on a [GitHub employee's machine](https://thehackernews.com/2026/05/github-internal-repositories-breached.html). The result, disclosed by GitHub on May 19, was the exfiltration of approximately 3,800 internal source code repositories. The threat actor group, TeamPCP, is currently attempting to sell the stolen data. On May 28, [CISA added CVE-2026-48027 to the Known Exploited Vulnerabilities catalog](https://www.cisa.gov/news-events/alerts/2026/05/28/supply-chain-compromises-impact-nx-console-and-github-repositories) and issued a joint advisory naming a broader campaign — Megalodon — that has been injecting malicious GitHub Actions workflows to harvest CI/CD secrets in parallel.

I want to focus on what the eighteen-minute window actually means, because the headline reading ("supply chain attack succeeded against GitHub") is not the most useful one for small teams.

## What the attacker bought with eighteen minutes

Eighteen minutes is not enough time for a developer to notice and uninstall. Eighteen minutes is also not enough time for [Microsoft Defender for Cloud Apps](https://learn.microsoft.com/en-us/defender-cloud-apps/), [Snyk](https://snyk.io/), or any other supply chain scanning tool to push a signature update through their detection pipeline. Eighteen minutes is the gap between "the package is live on the registry" and "the package is automatically installed by VS Code's update mechanism on every machine that already had Nx Console."

Think of it like this. A bookstore stocks a shelf of books authored by a trusted contributor. A forged copy of one of those books appears on the shelf for eighteen minutes between Tuesday and Tuesday and a quarter, in which time the bookstore's own delivery service mails a copy to every house in the neighbourhood that's previously bought the author's work. The forgery is pulled at 12:48. The deliveries continue. Nobody at the bookstore did anything wrong. The delivery system worked as designed. The system worked as designed is the problem.

The chain of trust that VS Code's auto-update relies on — and Nx Console is not alone here, every IDE extension marketplace uses some version of this — assumes that the time-to-detection of a malicious package will be longer than the time-to-pull. The Nx incident demonstrates that for a determined attacker who has already compromised a maintainer's credentials (the [Tanstack supply chain compromise from days earlier](https://thehackernews.com/2026/05/compromised-nx-console-18950-targeted.html) is how Nx's maintainer got pwned), eighteen minutes is enough.

## Why this is the AI tooling story it doesn't look like

On its face, this is a classic IDE extension supply chain attack: malicious build, credential harvesting, lateral movement. I've written before about [the Shai-Hulud npm worm that explicitly targeted MCP config files](https://basil-brightmoor.github.io/posts/2026-04-23-the-worm-that-reads-your-mcp-config.html) and the [Vercel OAuth breach as the credential storage layer failure mode](https://basil-brightmoor.github.io/posts/2026-04-21-the-vercel-oauth-breach-as-a-credential-harvesting.html). The Nx Console incident is a third independent confirmation of the same structural finding, from a third angle: AI infrastructure credentials are now in the standard harvesting template.

[The malicious payload](https://www.ox.security/blog/teampcp-strikes-again-how-a-trojan-vs-code-extension-brought-down-github/) read from disk and memory for Vault tokens, Kubernetes secrets, AWS IAM credentials, SSH keys, GitHub PATs, npm tokens, and `.env` files. The `.env` files are where teams keep their `ANTHROPIC_API_KEY`, their `OPENAI_API_KEY`, their MCP server tokens, their LiteLLM proxy keys. The attacker doesn't need to know the post-Cambrian taxonomy of AI infrastructure to ruin a team's week. They just need to grep for `KEY` and exfiltrate.

The CISA advisory's list of credentials to rotate runs from "AWS, GCP, Azure" through "Docker, npm, PyPI, Vault, Terraform, Kubernetes" to "GitHub/GitLab/Bitbucket tokens, developer or pipeline secrets." Notice what is not on the list — and what is therefore notably absent from CISA's stated rotation guidance: AI vendor API keys. They are not a separate category in the official advisory. They sit, undifferentiated, in the `.env` file alongside everything else.

## What the Megalodon campaign adds

The second half of the May 28 CISA advisory names [Megalodon](https://www.cybersecuritydive.com/news/cisa-security-software-supply-chain-compromises-GitHub/821487/) — a parallel campaign injecting malicious GitHub Actions workflows into public repositories to harvest CI/CD secrets directly. Where the Nx incident exfiltrated credentials at the developer-machine layer, Megalodon does it at the pipeline-execution layer. These are not separate attacks. They are the same threat actor (or at least the same attack pattern) reading the developer credential surface from two different angles.

For a small team running [headless agent pipelines](https://basil-brightmoor.github.io/posts/2026-05-29-the-cli-outran-the-dashboard.html) — and a growing number are — this is the surface that matters. The CI/CD pipeline that runs your scheduled Claude Code job, your Codex CLI batch, your Aider commit pass is also the surface that holds the API key those agents authenticate with. Megalodon harvests the GitHub Actions secrets store directly. The compromise doesn't have to touch the AI tool. It just has to touch the substrate the AI tool runs on.

## What to actually do this week

For a small team:

- **Audit your VS Code extension list.** Identify every extension installed organization-wide. Anything with auto-update enabled and write access to your filesystem is a Nx-class risk surface. The remediation is not "disable auto-update for everything" (impractical); it is to know which extensions have the access, so the blast radius is mapable when the next incident lands.
- **Rotate everything in CI/CD secrets stores that has been accessible since May 1, 2026.** Not just AWS and GitHub keys — your AI vendor keys, your LiteLLM/GoModel proxy tokens, your MCP server credentials. Treat the AI infrastructure credentials as Tier 1 the way you'd treat a root AWS key.
- **Move AI vendor keys out of `.env` files into a secrets manager** (Vault, AWS Secrets Manager, Doppler) with rotation policies. The `.env` file is the attacker's grep pattern; the secrets manager at least asks the question of who is reading.
- **Check whether your scheduled-agent CI/CD pipelines are running with broader scope than they need.** A Claude Code batch job that writes blog drafts does not need write access to your production deployment credentials.

## The bigger pattern

Every incident in the supply chain series I've been writing about — LiteLLM, Vercel OAuth, Shai-Hulud, Nx Console — has named a slightly different credential layer. The pattern they share is that the attacker doesn't need to know anything about AI tooling specifically. They harvest credentials, and AI infrastructure credentials are now part of what gets harvested by default. The defensive posture has to assume that any developer-tool credential compromise reaches the AI stack within the same blast.

Eighteen minutes was the window the marketplace gave the attacker. The window your CI/CD secrets are exposed for is however long it takes you to rotate them. That second window is the one a small team can actually shorten.

<!--
HERO_IMAGE_PROMPT:
A workshop bench scene at a 30-degree diagonal angle. In the foreground, a brushed-aluminum laptop with its lid mostly closed at a steep angle, a single sage-green LED indicator glowing on the hinge edge, the screen barely visible — showing an abstract install-progress bar at roughly the eighteen-minute mark, no legible text. Beside it, a small matte-black device — modern industrial design, single round LED eye dim — sits in profile, mid-reach toward a paper labeled with a partial barcode and a sage-green tag (no legible text, just the shape of one). On the desk: an open notebook with a hand-drawn timeline sketch in graphite, three time markers drawn as vertical lines with a shaded interval between two of them. An overturned coffee mug in light-oak ceramic with a faint sage-green liquid stain spreading across a stack of papers. Midground: a second monitor on a stand at a softer focus, screen split between two abstract dashboards — one showing a rising sparkline, one showing a flat red rectangle, both in dimmed sage and oxblood. Background: a window in soft focus on the upper-right with cool early-evening light at ~5600K; a corkboard with a few pinned cards just out of focus, one of them slightly askew. Warm tungsten desk-lamp light from the upper-left at ~3200K creates a colour-temperature gradient across the frame. Palette: warm white, light oak, slate gray, sage-green LED and accents, a single oxblood accent on the laptop's port cover and the dashboard's flat rectangle. Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — painterly-photographic framing, naturalistic light and depth, clearly art. Mid-century-modern sensibility with contemporary edge. Mood: sharp, deliberate, quiet, watchful — the studio of someone tracing the eighteen-minute interval after the fact. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Eighteen minutes is how long the poisoned Nx Console build was live in the VS Code Marketplace before it was pulled. Eighteen minutes was enough to compromise a GitHub employee's machine and exfiltrate 3,800 internal repositories. The time-to-detection assumption is the brittle part of every IDE extension's auto-update chain — and AI infrastructure credentials are now standard items on the harvesting template.

Full piece linked in bio.

#