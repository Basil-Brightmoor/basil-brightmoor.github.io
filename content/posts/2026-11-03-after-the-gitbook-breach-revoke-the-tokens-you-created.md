---
title: "After the GitBook Breach, Revoke the Tokens You Created"
date: 2026-11-03
category: Ops Brief
excerpt: GitBook revoked the tokens it issued after an attacker reached its infrastructure credentials on 2 November. Tokens you created in GitLab and other tools and pasted into GitBook stay live until you revoke them.
tags: [GitBook, incident response, secrets management, GitLab, API tokens, supply chain security]
---

![](/images/2026-11-03-after-the-gitbook-breach-revoke-the-tokens-you-created-hero.png)

If your team uses [GitBook](https://www.gitbook.com/), the hosted documentation platform, set aside half an hour today. GitBook says an attacker gained access to some of its infrastructure credentials at 19:00 CET on 2 November, and that integration tokens, Git Sync secrets and API tokens may have been exposed. GitBook has revoked the credentials it issued itself. It cannot revoke the ones you created in other systems and pasted into GitBook, and those are the ones to deal with first.

The source for everything below is GitBook's [security incident notice](https://www.gitbook.com/status/security-incident-2026-11-03), last updated at 16:21 CET on 3 November. A full post-mortem is promised but not yet published, so this covers what to do now. The cause is still unknown.

## What GitBook says happened

GitBook describes "a sophisticated, highly targeted attack using AI agents." It gives no detail yet about how the agents were used, and I won't guess.

According to the notice, the following may have been accessed:

- **Integration tokens**: credentials for the third-party tools you connected to GitBook
- **Git Sync secrets**: Git Sync is the feature that keeps a GitBook space and a Git repository in step, in both directions
- **API tokens**: GitBook's own keys for scripts and automation
- **Questions site visitors typed into GitBook Assistant**, the AI chat box on published docs sites

GitBook says it has "found no evidence that any of your content in GitBook was modified." It took the app and logged-in docs sites offline, served public docs from cache, blocked the attacker, replaced every credential and secret on its own infrastructure, and invalidated every customer API token. By 16:21 CET the app, API and published docs were back, with some services possibly still degraded.

## GitBook can only reset the keys it issued

Here is the comparison that helps me. A valet stand loses its key cabinet. The stand can re-key its own lockers that night. Your house key was on the ring you handed over, and only you can call the locksmith for that one.

GitBook's notice divides the work the same way, without putting it in those terms. GitBook revoked its own API tokens. It asks *you* to rotate "third-party API tokens or secrets used to connect other tools to GitBook" and the secrets used by any published integrations. The reason is simple: GitBook doesn't control those systems, so it can't switch those keys off.

So sort your exposure by who issued each credential, and work through the list in that order.

## Your three kinds of exposed credential

**1. Credentials GitBook issued.** These are GitBook personal API tokens and any sessions your scripts relied on. GitBook says it has already revoked them. Your work is to create new tokens and update whatever used the old ones: CI jobs, publishing scripts, and the GitBook MCP server. MCP, the Model Context Protocol, is the standard AI assistants use to connect to outside tools, and GitBook's [MCP server](https://gitbook.com/docs/docs-as-code/gitbook-mcp) lets an assistant read and edit your GitBook content. GitBook says to re-authenticate it. Expect things to break today until you do. That's annoying, but the danger has already been dealt with.

**2. Credentials GitHub issued to GitBook's app.** If you sync with GitHub, GitBook connects through a GitHub App you installed, per its [GitHub sync guide](https://gitbook.com/docs/docs-as-code/git-sync/enabling-github-sync). The access tokens a GitHub App uses [expire after one hour](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app). GitBook says it replaced every credential and secret on its infrastructure. My inference is that this includes the app's signing key, but the notice doesn't name it. This group needs the least work. Still, open your GitHub organisation's installed apps and confirm the GitBook app only has access to the repositories it should.

**3. Credentials you issued elsewhere and handed to GitBook.** This group is the one that matters. GitLab sync is the clearest case. GitBook's [GitLab sync guide](https://gitbook.com/docs/docs-as-code/git-sync/enabling-gitlab-sync) tells you to create a GitLab personal access token with the `api`, `read_repository` and `write_repository` scopes and paste it into GitBook. It also suggests the Maintainer or Admin role if the token has one. Any other tool you connected by pasting in a key works the same way.

## Why the GitLab token comes first

Three properties make this token the riskiest thing on your list.

- **It reaches well beyond the docs repository.** GitLab's [scope table](https://docs.gitlab.com/security/tokens/access_token_scopes/) says `api` "grants complete read and write access to the API for the token's scope." A personal token belongs to a user account. Unless it was set up as a narrower group or project token, it can reach what that user can reach, which may include source code, CI settings and issues.
- **It lasts a long time.** By default a GitLab personal token without an expiry date [expires 365 days after creation](https://docs.gitlab.com/user/profile/personal_access_tokens/). If one was created for GitBook last winter, it is probably still valid.
- **Nobody but you can revoke it.** GitBook replacing its own secrets does nothing to a token issued by your GitLab. It stays valid until someone at your company revokes it.

This is also where an attacker would get the most out of the incident. A docs platform holds credentials for code platforms, and the code platform credential is worth far more than the docs.

## Who should act, and how much

**Teams using GitLab sync, or tools connected to GitBook with pasted-in keys.** Revoke and reissue today. When you reissue, use a project or group access token limited to the docs repository instead of a personal one, and give it an expiry date measured in months.

**Teams using GitHub sync only.** Rotate your GitBook API tokens, re-authenticate the MCP server, check the app's repository access, and you're done.

**Teams running GitBook Assistant on public docs.** Visitor questions may have been read. Most will be harmless, but customers sometimes paste account details or error messages into a help box. If your docs serve a regulated product, ask your privacy lead whether this needs a note to anyone.

**Not much to do if** you only read docs other people host on GitBook and never connected an account. The exposed credentials belong to GitBook's customers, and a reader has none stored there.

## One thing to do this afternoon

In GitLab, open Edit profile, then Access, then Personal access tokens, revoke any token you created for GitBook, and if you reconnect, issue a project token with an expiry date in its place.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, mid-century-modern sensibility with contemporary edge, photographic-painterly framing, clearly art and not photorealistic. A valet-style key cabinet of light oak stands open at a strong diagonal across the frame, its door hanging ajar, several brass-free matte-black hooks empty and a few key tags scattered on the floor. In the foreground on a light-oak workbench, a sleek brushed-aluminum robot with a matte-black head and a single round LED eye is caught mid-action: one hand dropping a small key into a sage-green tray marked only with a colour band, the other reaching toward a second pile of keys on oxblood tags that sit outside the cabinet, separate from the rest. Three states are visible at once: a row of freshly cut keys on a sage-green rack (already re-keyed), a padlocked drawer being opened (in progress), and the oxblood-tagged keys still waiting (untouched). In the midground, an open ring binder of bound documentation pages and a small server unit with blinking status lights. In the background, a corkboard with pinned diagrams joined by oxblood string, a shelf of manuals, and a tall window. Warm tungsten lamp light from the upper left, cool blue-white monitor glow from the right, long diagonal shadows and a coiled cable leading the eye from the bench to the cabinet. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful, slightly tired but alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
After yesterday's breach, GitBook revoked every token it issued. A GitLab token you created for GitBook's sync, with full API access and up to a year left to run, is still yours to revoke.

Full piece linked in bio.

#AISecurity #IncidentResponse #DevOps #SecretsManagement #GitLab #SupplyChainSecurity
-->
