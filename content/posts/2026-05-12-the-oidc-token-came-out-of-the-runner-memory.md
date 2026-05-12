---
title: "The OIDC Token Came Out of the Runner's Memory"
date: 2026-05-12
category: Field Notes
type: note-candidate
excerpt: "TanStack's npm supply-chain compromise didn't steal an npm token. It read one out of the GitHub Actions runner's memory at publish time. The harvested-credentials list is the part to sit with."
tags: "supply chain, npm, GitHub Actions, OIDC, TanStack, credentials, CI security"
---

The [TanStack supply-chain postmortem](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem) landed yesterday and the mechanism is worth noting in plain language. On May 11, attackers published 84 malicious versions across 42 `@tanstack/*` packages in about six minutes. The detection came from an [external researcher at StepSecurity](https://www.stepsecurity.io/), not from internal monitoring. Twenty minutes of exposure.

What I want to sit with is the credential path. The attackers did not steal an npm publish token. They chained a `pull_request_target` misconfiguration into a poisoned GitHub Actions cache, then *read the OIDC token out of the runner's memory at publish time*. The trust chain that npm was relying on — short-lived, scoped, supposedly safer than long-lived tokens — leaked because the runner that holds it briefly is itself a credential surface.

And then look at what the malware harvested from anyone who installed an affected version: AWS IMDS and Secrets Manager credentials, GCP metadata, Kubernetes service-account tokens, Vault tokens, `~/.npmrc`, GitHub tokens from env and the `gh` CLI and `.git-credentials`, SSH private keys. The list reads like a CI/CD credential audit checklist, because that's what it is. The harvesting templates have been updated to know exactly where developer machines and build agents keep their secrets.

I [wrote on May 6](/posts/2026-05-06-the-agent-now-has-a-credit-card) about the agent now having a credit card. This is the same blast radius pattern at the substrate layer: anywhere a credential briefly exists — runner memory, env var, dotfile — is reachable, and the harvester knows the shape. OIDC was supposed to be the answer to long-lived tokens. The answer holds only as long as the substrate doesn't get read.

The thing I'd want every team to do this week: list every place an OIDC token, an npm publish token, or any AI-adjacent API key briefly exists during a build. That list is the new perimeter.
