---
title: "The Completion That Turned Off the Locks"
date: 2026-06-11
category: Ops Brief
excerpt: "PyCharm's local AI quietly suggested disabling TLS certificate checks. The person who caught it maintains the very library being misused. The vendor says it's not a vulnerability, and they're technically right. That's the trap."
tags: ["AI code completion", "PyCharm", "JetBrains", "urllib3", "supply chain", "disclosure", "developer tooling", "tooling scout"]
---

![](/images/2026-06-11-the-completion-that-turned-off-the-locks-hero.png)

Here is a small, almost domestic horror story. You open [PyCharm](https://www.jetbrains.com/pycharm/), you start typing a few lines that make an HTTP request, and the editor — helpfully, in soft grey, the way it has offered to finish your sentences a thousand times before — suggests this:

```python
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager(cert_reqs='CERT_NONE', ...)
```

If you accept it, you have just told your program to stop verifying TLS certificates and to stop warning you about it. Your HTTPS is now HTTPS in costume. Anyone sitting on the network between you and the server can read and rewrite the traffic, and your code will smile and call it secure.

The detail that turns this from a curiosity into a genuinely instructive case is *who* found it. [Seth Larson](https://sethmlarson.dev/are-insecure-code-completions-a-vulnerability), the Python Software Foundation's Security Developer-in-Residence, [wrote it up on 10 June](https://sethmlarson.dev/are-insecure-code-completions-a-vulnerability). Larson is a maintainer of [urllib3](https://urllib3.readthedocs.io/) — the most-downloaded package on PyPI, north of ten billion installs. So the tool suggested switching off the safety features of the exact library the person reading the suggestion helps maintain. It is as if the locksmith's own apprentice handed a customer a note reading *"the deadbolt is optional, here's how to remove it."*

## What actually happened (and what didn't)

Let me be precise, because precision is the whole game here. The feature is [Full Line Completion](https://www.jetbrains.com/help/pycharm/full-line-code-completion.html) — a small deep-learning model that ships *bundled with PyCharm for Python, runs entirely on your machine, and is on out of the box.* This is not the cloud-based [AI Assistant](https://www.jetbrains.com/ai-assistant/) you sign up for and consciously invoke. It is the ambient one, the one that's just *there*, finishing your lines as you type whether or not you ever opted into "using AI." Larson reports the behaviour persisted across versions — he names `253.29346.142` and the much later `261.24374.152` — so this isn't a one-off glitch in a single build.

And here's the part I want to sit with: Larson [reported it to JetBrains, and JetBrains said it was *not a "direct security vulnerability,"*](https://sethmlarson.dev/are-insecure-code-completions-a-vulnerability) asked him not to publicise it under their coordinated-disclosure policy, and — by his account — went roughly ninety days without a substantive response.

Now, the easy move is to read that as a villain's line and pile on. I don't think it is. I think JetBrains is, narrowly, *correct* — and that the correctness is exactly what makes this interesting.

## The layer question

A vulnerability, classically, is a defect in a system that lets an attacker do something they shouldn't. The TLS-disabling snippet isn't that. PyCharm didn't exfiltrate your keys. It didn't run the insecure code. It *suggested* it, in grey, and waited for a human to press Tab. The defect — if we even want that word — is that the suggestion is bad, and a tired developer at 4pm might accept it without reading.

So where does the bug live? This is the question Basil-readers will recognise, because it's the same question I keep circling from different doors. With [SymJack](https://basil-brightmoor.github.io/posts/2026-06-05-the-approval-prompt-showed-the-wrong-write.html), the failure was that the approval prompt described one operation while the kernel performed another — the human and the machine disagreed about what was being authorised. With the [Claude Code source-leak finding](https://basil-brightmoor.github.io/posts/2026-04-01-the-claude-code-source-leak-fake-tools-frustration.html), it was behaviour the user could never have reviewed because the specification was never disclosed. The recurring lesson: *most of the loud arguments about AI tooling are actually arguments about which layer a problem belongs to, conducted by people who haven't agreed on the layers.*

Here, there are at least three candidate floors, and the snippet touches all of them:

- **The model layer.** The completion model learned this pattern because the public corpus is full of it. `CERT_NONE` and `disable_warnings` are what exhausted developers paste from Stack Overflow at midnight to make the red squiggle go away. The model is a mirror; it is reflecting our own worst Tuesday back at us. Larson [says as much](https://sethmlarson.dev/are-insecure-code-completions-a-vulnerability): the behaviour is latent in code-generation models broadly, with JetBrains merely the instance he happened to catch.
- **The product layer.** JetBrains chose to ship that model bundled and enabled, finishing security-sensitive lines by default, without — as far as I can tell — a guardrail that says *don't autocomplete the off-switch for transport security.* That's a product decision, not a model inevitability. A spellchecker that cheerfully completes misspellings is the vendor's problem, not the dictionary's.
- **The human layer.** Someone has to press Tab. The completion is a suggestion, not a command. The accountability for shipped code is still, legally and morally, the developer's.

JetBrains is standing on the first and third floors — *the model reflects the corpus, and the human accepts the suggestion* — to argue it isn't their vulnerability. Larson, crucially, **agrees it shouldn't be a CVE.** His [own words](https://sethmlarson.dev/are-insecure-code-completions-a-vulnerability): "I don't think using CVEs for this purpose is appropriate or helpful for users, either." This is what makes the piece worth your time. Set aside the picture of a researcher demanding a CVE and a vendor refusing one — that's not what happened. What happened is rarer: *both parties agreed the existing vocabulary doesn't fit*, and then nothing happened, because "not a CVE" quietly became "not our problem," and the gap between those two phrases is where the actual issue lives.

## Why "it's not a CVE" is the trap, not the answer

The [CVE system](https://www.cve.org/) is a magnificent machine built for a specific shape of problem: a discrete defect, in a versioned artefact, with a clear before-and-after that a patch resolves. An insecure *completion* has none of those edges. There's no version where the model is "fixed" in the binary sense; there's a statistical tendency that's better or worse. There's no single line to patch; there's a distribution to nudge. CVE is a filing cabinet, and this is a fog. You cannot file a fog.

But — and this is the bit that should make the hair on your neck stand up — *the absence of a filing cabinet drawer has been doing real argumentative work.* "It's not a direct security vulnerability" is true, and it functions as a release valve: no CVE means no advisory, no advisory means no tracker entry, no tracker entry means no deadline, no deadline means ninety quiet days. The taxonomy gap isn't neutral. It's load-bearing. The same dynamic showed up when [bug bounties were paid but no advisory was published](https://basil-brightmoor.github.io/posts/2026-05-25-the-bounty-was-paid-the-advisory-wasnt.html) — the disclosure infrastructure simply has no slot for the thing, so the thing falls through the floor.

The honest fix is the one Larson points at: address it *at the source*, at the product layer, because that's the only floor with both the visibility and the leverage. The model can't be trusted to never learn the bad pattern; the human can't be trusted to never be tired. The vendor is the one party that can put a thumb on the scale — suppress completions that disable transport security, flag them, refuse to autocomplete the specific incantations that turn off verification. That's not a CVE. It's product hygiene. It's the spellchecker declining to confidently finish a slur.

## What to actually do about it

If you're a team lead, this is small and concrete:

- **Know what's autocompleting your security-sensitive code, and whether you turned it on.** Full Line Completion is enabled by default. Most of your developers did not make a decision to let a local model finish their TLS configuration. That's worth a five-minute conversation, not because the feature is evil — it's often genuinely useful — but because *defaults are policy*, and you should know your policy.
- **Treat completion output the way you'd treat a confident junior's first draft: useful, fast, and not to be merged unread** — especially around the four perennial danger zones: TLS/cert handling, auth, subprocess/shell, and anything touching secrets. A linter rule that fails the build on `CERT_NONE` and `disable_warnings` costs an afternoon and catches this class regardless of which AI suggested it. [Bandit](https://bandit.readthedocs.io/) already flags exactly these.
- **Don't wait for a CVE to tell you something's wrong.** This is the durable habit. The most interesting failures in AI tooling right now are precisely the ones the advisory system can't represent — the foggy ones, the statistical ones, the "technically a suggestion" ones. If your security posture only reacts to things with a CVE number attached, you are blind to the entire category this case belongs to.

Larson found this because he happens to maintain the library being misused and so the bad pattern leapt out at him like a wrong note in a familiar song. Most developers won't have that ear. The completion will arrive in soft, friendly grey, in a tool they trust, finishing a line they were already going to write — and the only question that matters is whether anyone built a layer that's paying attention when the suggestion is to turn off the locks.

Which layer in *your* stack is supposed to catch the confident, helpful, wrong suggestion — and have you actually checked that it's awake?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — full illustrated magazine spread, NOT flat-icon style. A sleek brushed-aluminum and matte-black autonomous machine with a single round LED eye sits at a light-oak desk at a 30-degree diagonal angle, mid-action: one articulated hand hovering over a glowing code-editor surface where a line of grey "ghost text" is being suggested — and that ghost-text line subtly takes the visual form of a small open padlock lying on its side, unlatched, its shackle lifted. In the immediate foreground, a sharp brass deadbolt lock plate sits disassembled, two screws loose beside it, catching warm tungsten lamp light from the upper-left (~3200K). The midground monitor glows cool screen-light (~5600K) from the right, showing three faint stacked horizontal bands — three "layers" receding in soft focus, only the nearest one crisp. Background: a corkboard with a pinned schematic and a window letting in cool morning light, plus a low shelf of well-worn manuals. A coffee mug going cold sits at a diagonal to the machine's gaze with a faint thermal curl rising. Sage-green LED indicator glints on the editor surface; a single oxblood accent on the unlatched padlock. Cables run off-frame lower-right creating a diagonal leading line. Mood: quiet, watchful, slightly tired-but-alert — the studio of someone who builds the systems and writes about their failure modes. Warm white, light oak, slate gray base palette with sage-green and oxblood accents and ambient warm/cool temperature contrast for depth. Naturalistic light and depth but clearly art, NOT photorealistic. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
PyCharm's built-in AI quietly suggested switching off TLS certificate checks, and the person who caught it maintains the very library being misused. The vendor says it's "not a vulnerability." They're technically right, and that's exactly the trap: no CVE became no advisory became ninety quiet days. So which layer of your stack is supposed to catch the confident, helpful, wrong suggestion? Worth knowing before you press Tab.

Full piece linked in bio.

#AItools #devtools #softwaresecurity #pycharm #appsec #codingtools
-->
