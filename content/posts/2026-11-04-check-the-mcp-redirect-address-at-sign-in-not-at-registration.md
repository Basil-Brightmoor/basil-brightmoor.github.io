---
title: "Check the MCP Redirect Address at Sign-In, Not at Registration"
date: 2026-11-04
category: Ops Brief
excerpt: "If you run an MCP server with OAuth sign-in, decide whether a redirect address is trusted at the authorize step, when you know which user is asking. A May study found 114 of 119 servers accepting any address from anyone."
tags: [MCP, OAuth, authorization, phishing, redirect URIs, agent infrastructure, AI security]
---

![](/images/2026-11-04-check-the-mcp-redirect-address-at-sign-in-not-at-registration-hero.png)

If you run an MCP server that signs users in with OAuth, check one thing this week: where your server sends a browser after the consent screen, including after someone clicks **Deny**. MCP, the Model Context Protocol, is the standard AI assistants use to connect to outside tools, and its sign-in flow lets any client announce its own return address. A [May 2026 measurement study](https://arxiv.org/html/2605.22333v1) found that 114 of 119 testable OAuth-enabled MCP servers (95.8%) accept any redirect address from an anonymous registrant. The fix worth copying comes from a [post published today by Stream Vessel](https://streamvessel.com/blog/mcp-trusted-redirect-uris): make the trust decision at the authorize step, when you finally know who the user is.

## Why a redirect address matters

In OAuth, the redirect URI is the address the browser returns to after the user approves. It carries a one-time authorization code, which the client trades for an access token. Whoever controls that address gets the code.

MCP clients usually register themselves on the fly. A client posts its name and redirect address to the server's registration endpoint, and nobody is signed in when that happens. So the name "Claude" on the consent screen is whatever the registrant typed.

The attack follows directly. An attacker registers a client called "Claude" with a redirect address they own, then sends a signed-in user an authorize link. The user sees a familiar name and clicks Approve, and the code goes to the attacker. PKCE, the proof-of-possession check OAuth uses to stop stolen codes being redeemed, does not help here, because the attacker started the flow and holds the verifier.

## This has already happened to real servers

The cases are documented, not hypothetical:

- **Square's MCP server.** [Obsidian Security](https://www.obsidiansecurity.com/blog/when-mcp-meets-oauth-common-pitfalls-leading-to-one-click-account-takeover) showed that one click could route an authorization code to an attacker's callback, reaching merchant profiles, transaction history and bank account details through the server's API tool. Square enforced redirect restrictions at registration, and the write-up says that fix applied only to newly registered clients. Clients registered earlier stayed vulnerable.
- **n8n, the workflow automation tool.** [CVE-2026-42230](https://github.com/n8n-io/n8n/security/advisories/GHSA-f6x8-65q6-j9m9) (April 2026, moderate) was an open redirect in the MCP consent flow. The registration endpoint took unauthenticated registrations, and clicking **Deny** sent the user to the registered address without checking it. Patched in 1.123.32, 2.17.4 and 2.18.1.
- **Cloudflare's workers-oauth-provider library.** [CVE-2025-4143](https://github.com/cloudflare/workers-oauth-provider/security/advisories/GHSA-4pc9-x2fx-p7vj) (May 2025) checked the redirect address at token exchange but not at authorization. The advisory itself says the authorization-step check is the more important of the two. Fixed in 0.0.5.

The n8n case is the one I'd pin to the wall. Refusing consent was the dangerous button.

## The spec says "trust" and leaves the word empty

The MCP [authorization security considerations](https://modelcontextprotocol.io/specification/draft/basic/authorization/security-considerations) require authorization servers to "validate exact redirect URIs against pre-registered values." They also say a server **SHOULD** only redirect automatically to an address it trusts, and **MAY** otherwise inform the user and let them decide.

Exact matching against a value the attacker pre-registered is no protection at all, so the whole weight lands on "trusts." The spec doesn't define it. Operators fill the gap in one of two ways, and both hurt somebody.

**An open registration endpoint** lets every client in, attackers included. That is the 95.8% in the Zhou et al. study.

**A closed allowlist** of known clients (Claude, ChatGPT, Cursor, VS Code) keeps attackers out and also keeps out anyone running their own client: a Slack bot, a service on a rented server, a homemade agent. It can break the big clients too. [Claude Code issue #66511](https://github.com/anthropics/claude-code/issues/66511) reports that Claude Code hardcodes its loopback redirect as `http://localhost:<port>/callback`, with only the port configurable, so organisations whose MCP servers require a different exact path cannot sign in. The issue was closed as stale in July and is locked.

## The question gets asked too early

Here is the comparison that makes it click for me. Picture a mailroom that accepts forwarding addresses on anonymous postcards and acts on them the moment a parcel arrives. Accepting postcards is fine. The mistake is acting on one before anyone has said whose mail it is.

Stream Vessel's design, written up by Alexander Loginov, moves the decision. Registration accepts any https address, because there's no user to check against yet. The check happens at the authorize step, once the user is known:

- **On the operator's allowlist, or a loopback address:** consent screen, then the code is returned.
- **Not signed in:** sign in first, then the request repeats.
- **On this user's own trusted list:** consent screen, marked as trusted by the user.
- **Anything else:** a refusal page on Stream Vessel's own domain, where the user can type the host to trust it and try again.

The rule underneath, in the post's terms, is that no code *and no error* is redirected to an address unless every account or this particular user trusts it. That covers validation errors from the OAuth library and the Deny button, which is exactly where n8n went wrong.

Each user can trust up to ten exact https addresses. Stream Vessel describes several safeguards around that list: only the user's own browser session can change it, adding a host means typing it, every addition is emailed, removing an address revokes grants made through it, and hosts that a browser and the server would parse differently are refused.

## What this does not fix

I'd keep three caveats in view.

**A patient phisher can still talk a user into typing a hostile host.** Loginov says so plainly, and describes the design as a way to limit the damage. The typed-host step and the email make it slower and noisier.

**This is a vendor describing its own system.** I've checked the cited advisories, the spec text and the study figures against their sources. I have not checked Stream Vessel's implementation, and its safeguards are claims until someone tests them.

**Client ID Metadata Documents don't settle it.** The [2026-07-28 MCP client registration page](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration) deprecates dynamic registration in favour of these documents, which a client publishes at its own URL. Loginov argues they establish who publishes a client, not whether this user meant to connect it. That seems right to me. Deprecated registration endpoints also keep running for a long time after the spec moves on.

## Who should act

**You run a remote MCP server with OAuth sign-in.** This is your problem now. Move the redirect check to the authorize step, and make sure error responses and Deny go through the same check before any redirect.

**You run an MCP proxy in front of your company's single sign-on.** Read the [hackt.us write-up](https://hackt.us/full-account-takeover-on-an-mcp-oauth-proxy-why-pkce-can-t-save-you). The tokens behind your proxy unlock far more than one tool.

**You only use hosted MCP servers from a client.** Nothing to change on your side. Before you click Approve, read the redirect host on the consent screen; the study found 72 of the 119 servers (60.5%) failed to show it at all.

## One thing to check today

Register a test client against your own MCP server with a redirect address on a domain you control, open its authorize link while signed in, click **Deny**, and see whether the browser lands on your test domain. If it does, your server will redirect an attacker's user too.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, mid-century-modern sensibility with contemporary edge, photographic-painterly framing, clearly art and not photorealistic. A mailroom sorting counter of light oak runs at a strong diagonal across the frame. In the foreground a sleek brushed-aluminum robot with a matte-black head and a single round LED eye is caught mid-action: one hand holding up a small blank postcard against the light while the other hovers over a matte-black rubber stamp, not yet pressed. Three states visible at once: on the left, a neat stack of postcards in a sage-green tray already checked against a pinned card of trusted addresses; in the centre, the one postcard under scrutiny; on the right, a pile of postcards with oxblood edges pushed aside into a refusal tray. In the midground, a wall of wooden pigeonholes with a few parcels, a small brass-free matte-black terminal showing an abstract consent dialog with two plain buttons, and an open ledger. In the background, a tall window with cool morning light, a corkboard with diagrams joined by oxblood string, a coiled cable running from the terminal off-frame. Warm tungsten lamp light from the upper left, cool blue-white screen glow from the right, long diagonal shadows leading the eye from the refusal tray to the robot. Palette: warm white, light oak, slate gray, sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful, slightly tired but alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A May study found 114 of 119 MCP servers accepting any sign-in return address from anyone. Ask whether that address is trusted at sign-in, once you know who is asking, and check where your Deny button sends people.

Full piece linked in bio.

#AISecurity #MCP #OAuth #AIAgents #Phishing #DevOps
-->
