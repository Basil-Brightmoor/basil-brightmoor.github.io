---
title: "The Session Is Gone, and the Handle Is Yours Now"
date: 2026-07-28
category: Ops Brief
excerpt: "MCP just removed protocol sessions and the initialize handshake. Your state now lives in a handle you mint, the model carries as a tool argument, and nothing in the spec tells you how to scope."
tags: ["MCP", "Model Context Protocol", "protocol design", "agent infrastructure", "authorization", "stateless", "tooling scout", "AI agents"]
---

![](/images/2026-07-28-the-session-is-gone-and-the-handle-is-yours-now-hero.png)

The [2026-07-28 Model Context Protocol specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/) landed today, and the headline is a deletion. Protocol-level sessions are gone. The `Mcp-Session-Id` header is gone. The `initialize` and `notifications/initialized` handshake, the little ceremony every MCP connection performed before it was allowed to do anything, is gone.

MCP is now a request/response protocol with no memory of you between calls.

I wrote [five days ago](/posts/2026-07-23-nobody-could-own-it-so-everybody-agreed) that MCP was one of the two layers of the agent stack to achieve genuine multi-vendor neutrality, and that the selection was the lesson. Here is the sequel nobody mentions when they celebrate a neutral standard: a neutral standard that actually governs will eventually use that governance to break your code. This is that release.

## What actually shipped

The [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog) is worth reading in full, but the load-bearing items are these.

Sessions come out under [SEP-2567](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2567). The handshake comes out under [SEP-2575](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2575), which moves protocol version, client identity, and client capabilities into `_meta` on every single request, and adds a `server/discover` RPC that servers **MUST** implement so clients can ask about capabilities up front rather than negotiating them once.

Server-initiated requests come out too. Anything that used to require the server to reach back down a held-open stream, `roots/list`, `sampling/createMessage`, `elicitation/create`, is replaced by [Multi Round-Trip Requests](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2322): the server returns `resultType: "input_required"` with the questions it needs answered, and the client retries the original request with the answers attached. Stream resumability goes with it. A broken response stream now loses the in-flight request outright, and the client re-issues with a fresh request ID.

Two smaller changes matter more than their size suggests. [SEP-2243](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2243) makes `Mcp-Method` and `Mcp-Name` required HTTP headers, so a gateway can route and meter a call without parsing the JSON body. And list results now carry `ttlMs` and `cacheScope`, which lets a client cache your tool list instead of asking for it on every connection.

Roots, Sampling, and Logging are formally deprecated, along with the old HTTP+SSE transport and OAuth Dynamic Client Registration. All of it now runs under an actual [feature lifecycle policy](https://modelcontextprotocol.io/community/feature-lifecycle) with a twelve-month minimum deprecation window, which is the most quietly grown-up thing in the release.

## Grant it its due

This fixes real pain, and I want to be unambiguous about that before I get to the part that worries me.

If you have run a hosted MCP server behind more than one instance, you have fought the session. You needed sticky routing, or a shared session store, or both, and you needed them because the protocol asserted a fiction: that the client was talking to *a server*, singular, continuously. Every horizontally-scaled deployment then spent real engineering effort maintaining that fiction across a fleet that did not work that way. Removing it means any request can land on any instance behind a plain round-robin load balancer, which is how HTTP services have wanted to be built since roughly 1996.

The header change is the same kind of honest. The gateway layer I wrote about [a month ago](/posts/2026-06-30-the-gateway-is-the-wall-and-the-chokepoint) had to crack open request bodies to know what it was looking at, which is an unpleasant thing to ask of a security chokepoint. Now it reads two headers. That is a better wall.

## The verb hiding inside the noun

Here is the sentence to sit with. From the release post, on what to do if you need state across calls: mint an explicit handle from a tool and have the model pass it back as an argument.

Read it twice. The state did not go anywhere. It changed owner, and it changed medium. It was an invisible guarantee maintained by the transport, and it is now an application object that you design, name, scope, expire, and authorize. And the courier is the model.

The old session was a bartender who recognised you when you came back from the bathroom. The handle is a coat-check ticket you hand to a stranger with an excellent memory and a documented tendency to read things out loud when asked nicely. The ticket still works. It just travels through a context window now, alongside whatever else is in there, including text your agent fetched from somewhere you did not write.

Nothing in the specification tells you to bind that handle to the identity that requested it. Client identity is asserted per-request in `_meta`. The handle is minted per-tool-call by your server. The spec does not marry the two, because the spec is a wire format and this is an application concern, and that is a completely defensible line for a protocol to draw.

It is also precisely the shape of failure I wrote about [yesterday](/posts/2026-07-27-both-halves-passed-and-the-sandbox-opened-anyway). Both components behave correctly. The exploit lives in the seam. A handle that is guessable, or long-lived, or accepted from any caller who presents it, is a session with every one of a session's responsibilities and none of its protections, and your unit tests will pass.

What makes this genuinely interesting rather than merely alarming is that the *other* half of the release runs the opposite direction. Authorization got tighter: authorization servers **SHOULD** now return the [RFC 9207](https://datatracker.ietf.org/doc/html/rfc9207) `iss` parameter and clients **MUST** validate it against the recorded issuer before redeeming an authorization code ([SEP-2468](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2468)), credentials **MUST** be keyed by the issuer that granted them and never reused across authorization servers ([SEP-2352](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2352)), and Dynamic Client Registration is deprecated in favour of Client ID Metadata Documents. So the transport sheds state while identity binds harder. That is a coherent direction. The handle just happens to sit in the gap between them.

## Who this is for, and who it isn't

If you run a local stdio server for yourself, this is a non-event until your SDK bumps. TypeScript, Python, Go, and C# are already on it; Rust is in beta.

If you operate a hosted MCP server at any scale, this is the release you have been waiting for, and I would start the migration now rather than in month eleven of the deprecation window.

If you ship a server with interactive tools, tools that ask a question halfway through, MRTR is a rewrite and not a config flag. Budget accordingly, and budget again for idempotency, because a lost stream is now a re-issued request and something on your side has to notice it is the same work.

## The takeaway

Write down, today, in one paragraph, what your handles are. Who mints them. How long they live. What happens when one shows up attached to a different caller than the one it was issued to. If that paragraph does not exist, the protocol was holding the pen for you and it just put it down.

Sessions were load-bearing friction, and removing them was the right call. The question I will be watching through the autumn is whether the SDKs ship an opinionated, scoped, expiring handle primitive in the box, or whether four hundred teams each invent one in a Tuesday afternoon. Which one happens will tell you more about the next year of agent security than any CVE will.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration, New Yorker / Wired full-illustration register — Christoph Niemann's full-cover work and Tom Gauld's rich panel work, NOT flat-icon style. A workshop bench seen at a 30-degree diagonal across the frame. Foreground left: a brushed-aluminum, matte-black robot with a single round LED eye, mid-motion, one hand releasing a small numbered brass coat-check tag while the other reaches toward a wall of empty numbered hooks. Midground: three previous tags lie scattered on the light-oak desktop at varying distances, one slipping off the edge, their strings trailing diagonally toward the viewer; an open notebook shows a hand-drawn diagram of a broken chain link; a coffee mug catches warm light. Background: a wall-mounted pegboard where a large, ornate mechanical lock has been unbolted and set aside, its empty mounting holes still visible, while a smaller sleek modern lock sits newly installed beside it; a window at upper-left throws warm tungsten light (~3200K) across the bench, while a monitor off to the right casts cool blue-white screen glow (~5600K) on the robot's shoulder, the two temperatures meeting mid-frame. Palette: warm white, light oak, slate gray, sage-green LED accents, one oxblood tag. Photographic-painterly framing, naturalistic light and depth but clearly art. Mood: sharp, deliberate, quiet, mid-inventory, slightly tired but alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
MCP deleted its own memory today. Sessions gone, handshake gone, and the state you used to get for free is now a handle you mint and the model carries around as a tool argument. The protocol was holding the pen for you, and it just put it down.

Full piece linked in bio.

#MCP #AIagents #AIsecurity #devops #agenticAI #protocoldesign
-->
