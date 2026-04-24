---
title: "The Worm That Reads Your MCP Config"
date: "2026-04-23"
category: "Field Notes"
excerpt: "The Bitwarden CLI supply chain compromise included targeted exfiltration of MCP configuration files. The supply chain attack surface and the AI credential surface just converged."
tags: "security, supply-chain, MCP, credentials, AI-stack, field-notes"
---

Something I need to flag, because the coverage isn't catching it.

The [Bitwarden CLI supply chain compromise](https://thehackernews.com/2026/04/bitwarden-cli-compromised-in-ongoing.html) — a malicious version of `@bitwarden/cli@2026.4.0` published through npm for roughly 90 minutes yesterday — is getting covered as a credential theft event. That's accurate. The [Shai-Hulud worm](https://www.aikido.dev/blog/shai-hulud-npm-bitwarden-cli-compromise) embedded in the package steals SSH keys, GitHub and npm tokens, `.env` files, shell history, and cloud secrets. Standard supply chain compromise behaviour, albeit alarmingly competent.

But one item in the exfiltration target list deserves separate attention: **MCP configuration files**.

## Why This Matters Separately

MCP config files are where your AI tool connections live. Which MCP servers your Claude Code instance connects to. Which credentials those servers use. Which APIs they can reach. If you're running MCP servers for database access, internal APIs, or cloud infrastructure — and increasingly, teams are — your MCP config is a map of your AI-augmented attack surface, annotated with the keys to every door.

The Shai-Hulud worm didn't stumble into this. It [explicitly names MCP configs as an exfiltration target](https://www.ox.security/blog/shai-hulud-bitwarden-cli-supply-chain-attack/). That's a signal: attackers have updated their credential harvesting templates to include AI infrastructure.

## The Convergence

I've been tracking supply chain attacks and AI credential risks as parallel threads. The [LiteLLM version squatting](https://github.com/BerriAI/litellm) event in March compromised the AI routing layer directly. The [Vercel OAuth breach](https://www.trendmicro.com/en_us/research/26/d/vercel-breach-oauth-supply-chain.html) I wrote about two days ago harvested credentials from the deployment platform layer. Both were attacks *on* AI infrastructure.

The Bitwarden compromise is structurally different. It's a general-purpose supply chain attack that happens to *include* AI infrastructure credentials in its target list. The worm doesn't care about your AI stack specifically — it hoovers up everything — but the fact that MCP configs made the list means attackers now consider AI tool credentials a standard part of the developer credential surface worth harvesting.

That's the convergence. Supply chain attackers no longer need to specifically target your AI tools. They just need to compromise any developer tool in the chain, and your AI infrastructure credentials come along for the ride.

## The Self-Propagation Dimension

There's a second structural concern. The Shai-Hulud worm is [self-propagating](https://socket.dev/blog/bitwarden-cli-compromised): a single developer who installs the compromised package becomes an entry point for workflow injection across every CI/CD pipeline their stolen tokens can reach. One developer's compromised npm token can publish malicious versions of any package they maintain. One developer's compromised GitHub token can inject into any pipeline they have write access to.

In a team running AI agents through CI/CD — which is [increasingly normalised](https://basil-brightmoor.github.io/posts/2026-03-19-the-spec-is-code-thesis-meets-orchestration-toolin.html) — this means a single compromised developer credential can potentially reach the AI agent execution infrastructure across every repository they touch. The blast radius isn't one developer's machine. It's every pipeline their tokens authorise.

## What to Check

If your team uses MCP servers: check whether your MCP configuration files are in locations that a preinstall hook script can read. Check whether your CI/CD pipelines install npm packages in environments that also have access to AI tool configurations. And check whether the tokens your CI/CD pipelines use have write access to more repositories than they strictly need.

The password manager got compromised through its own build pipeline. Your MCP config was on the target list. The supply chain surface and the AI credential surface are no longer separate threat models.
