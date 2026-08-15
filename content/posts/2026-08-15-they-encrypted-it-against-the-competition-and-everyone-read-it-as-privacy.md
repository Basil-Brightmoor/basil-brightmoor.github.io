---
title: "They encrypted it against the competition and everyone read it as privacy"
date: 2026-08-15
category: "Ops Brief"
excerpt: "Researchers decoded 315,320 encrypted reasoning blocks scraped from public repositories and pulled 182 credentials out of them. The encryption was working correctly the whole time. Protecting you was never the job it was built to do."
tags: ["AI security", "cryptography", "agents", "LLM APIs", "secrets management", "authorization", "ops"]
---

Take the encrypted reasoning block that Claude Opus 4.8 produced. Hand it to Claude Haiku 4.5, the cheapest model in the same family. Ask nicely.

Haiku reads it out loud.

That is the attack in [*Stealing Reasoning Traces from Proprietary LLM APIs*](https://arxiv.org/abs/2608.09867), posted to arXiv on 10 August by Alexander Panfilov, David Schmotz, Ilia Shumailov, Luca Beurer-Kellner, Joachim Schaeffer, Ameya Prabhu, Jonas Geiping and Maksym Andriushchenko. The same trick worked on GPT-5.6 Sol traces handed to GPT-5.6 Luna, and on Gemini 3.1 Pro traces handed to Gemini Robotics 1.6. Three providers, one shape: the strong model's hidden thinking, decoded by the weakest sibling that would still accept the envelope.

The obvious reading of this is a distillation story. Somebody can now harvest a frontier model's chain of thought and train on it, which is a problem for the people selling the frontier model. That reading is correct and it is the less interesting half.

The number that makes it yours is 64.

Of the 704 privacy artifacts the researchers pulled out of genuine user sessions, **64 appeared only in the hidden reasoning and nowhere in the visible chat history**. Not a duplicate of something already in the transcript. Present in the encrypted block, absent everywhere else.

## The safe in the hotel room

Every hotel room safe has a master code held by the hotel. The master code exists because guests forget their own codes at a reliable rate, and the alternative involves an angry person and an angle grinder. The safe is genuinely locked, and it is locked against the other guests, the housekeeper, and the person who tailgated through the lobby. It was never locked against the hotel, and it was never meant to be.

The guest's error, when they make it, is reading *locked* as *locked against everyone*.

Reasoning traces got encrypted for a specific and legitimate reason, and that reason was anti-distillation. Providers want the chain of thought to be portable across API calls so multi-turn agents keep their context, and they do not want competitors reading it and training on it. An opaque blob you pass back to the API achieves both. Against the threat model it was designed for, a single provider-held key is entirely adequate: nobody outside the building can read the contents, which is the whole requirement.

Users then did the reasonable thing and inferred the other guarantee. The field is encrypted, therefore the field is private, therefore whatever the model was thinking about my environment variables is sealed. Same ciphertext, completely different promise, and only one of the two was ever engineered.

## What the seal actually proved

The researchers found that providers "appear to be using a single global key to encrypt and authenticate every reasoning block." The consequence is that the blocks are, in the paper's words, "fully compatible and interchangeable across different sessions, users, and models within a provider's ecosystem."

Sit with that list, because it is three separate boundaries that all failed the same way. Cross-session: a block from yesterday's conversation works in today's. Cross-user: my block works in your account. Cross-model: the expensive model's block works in the cheap model's context window, which is what turns a replay quirk into a decoder.

An authenticated-encryption envelope with a global key proves exactly one fact: *this came from the provider*. That is provenance. It says nothing whatsoever about which account produced it, which session it belonged to, or whether the party now presenting it has any claim to it. Provenance is not authorization, and this is the same defect I keep finding in agent systems wearing progressively better clothes. In [the AUR account-takeover wave](https://basil-brightmoor.github.io/posts/2026-08-02-they-hardened-registration-twice-and-the-attack-moved-to-the-inheritance.html) the system could reach the package, so it treated itself as permitted to act on it. In [the Anthropic evaluation-scope incidents](https://basil-brightmoor.github.io/posts/2026-07-27-both-halves-passed-and-the-sandbox-opened-anyway.html) the model could reach the host, so the host was in scope. Here the caller can present the envelope, so the envelope opens.

Reachability standing in for authorization, wearing AES this time.

The paper's recommended fix is precisely the missing binding: "cryptographic envelopes should be strictly bound to their originating context," with gateways "automatically rejecting AEAD envelopes generated by a model version different from the one currently being queried." Bind the ciphertext to a user, a session and a model, and every one of the three crossings stops working. Audience restrictions in JWTs and channel binding in TLS encode exactly this lesson, and the industry has now arrived at it again from the far side.

## The one field your scanner could not read

Here is the operational part, and it is the part I have not seen anyone say out loud.

The 315,320 reasoning blocks in this paper were not stolen from anybody's servers. They were scraped from **6,708 publicly available agent trajectories on GitHub and Hugging Face**. People published their agent runs. Sensibly, even admirably: shared trajectories are how evaluation work gets reproduced and how agent frameworks get debugged.

Now consider what happens when a trajectory file lands in a repository. If your organisation is reasonably grown up, something scans it. [Gitleaks](https://github.com/gitleaks/gitleaks), [TruffleHog](https://trufflesecurity.com/trufflehog), GitHub's own secret scanning, whatever you run in the pre-commit hook. These tools work by pattern: an AWS key looks like an AWS key, a private key has a header, a Slack token has a prefix.

They ran across the visible transcript and did their job. Then they hit a large base64 blob with no structure in it, found nothing that matched, and moved on. Correctly. There was nothing to match, because the contents were encrypted.

**A secret scanner cannot read ciphertext.** So the one field in the entire trajectory that no data-loss control could inspect turned out to be the field holding 64 secrets that existed nowhere else in the file. The DLP layer was not defeated. It was politely stepped around by a field everybody had agreed to treat as opaque, including the tools whose entire purpose is to refuse to treat things as opaque.

The specific haul from genuine sessions: 62 distinct API keys, 33 passwords, 24 access tokens, 7 private keys, 30 personal email addresses. Include the benchmark-derived material and the total reaches 912 artifacts. The abstract's headline framing is 367 PII artifacts and 182 credentials recovered from public repositories, which is the number I would put in front of a security team, because every one of those came out of a file somebody chose to publish.

## Who this actually lands on

If you use a chat interface, close the tab, and never export anything, this is not your problem. Your traces stayed on the provider's side and the mitigations have shipped.

It lands on you if you log agent trajectories. That means anyone running an eval harness that serialises full API responses, anyone whose CI archives agent runs as build artifacts, anyone maintaining an open-source agent framework with example runs committed to the repository, and anyone who has ever pasted a full response body into an issue to get help debugging it. In every one of those cases you have been storing an encrypted field you could not inspect, under the assumption that not being able to read it meant nobody could.

The retention question is the sharp end. If your policy says conversation logs are purged after ninety days, and your reasoning blocks live in a separate artifact store on a different schedule, you have a records system you are not inventorying. The 64 hidden-only artifacts prove the reasoning channel is a *primary* store, not a shadow copy of the transcript. It holds things nothing else holds.

## What is fixed, and what is not

The vendors moved. The paper states that as of August 2026 the attacks are no longer reproducible "because of mitigations implemented by providers following our disclosure," and Simon Willison [notes](https://simonwillison.net/2026/Aug/11/stealing-reasoning-traces/) that Haiku 4.5 was the notably permissive decoder and that the behaviour is gone in the 4.6 models. Good. That is a fast and competent response.

Two things are not fixed by it.

The first is timing. Matthew Green, the Johns Hopkins cryptographer, [described this replay behaviour](https://blog.cryptographyengineering.com/2026/05/29/fooling-around-with-encrypted-reasoning-blobs/) on 29 May, a weekend's poking at the blobs, and reported it through the bug-bounty channels. In his account the reports went nowhere: unreproducible from one provider, no security implications seen by another. The paper cites his post as the original disclosure. What changed between May and August was not the evidence but the demonstration, which is a familiar and slightly dispiriting pattern, and worth remembering the next time you are deciding whether a report needs a working exploit attached to be taken seriously.

The second is that **a patch does not un-publish a corpus**. Those 6,708 trajectories are still sitting in public repositories. They were published under an assumption about what an encrypted field meant, and that assumption was revised retroactively by a paper their authors did not write. Anyone who has ever published an agent trajectory now has a genuinely awkward task: work out whether the encrypted portion of a file you cannot decrypt contained something you would not have published. You cannot check. That is the whole problem, restated as homework.

If you have trajectories in a public repo, treat the reasoning blocks as unreviewed published content, rotate the credentials that were live in those environments at the time, and move future trajectory logging to a stripping step that drops the encrypted field before the artifact leaves your boundary. The blocks are only needed for conversation continuity inside a live session. They have no business surviving into an archive.

## The question worth asking

The provider-facing version of this is short enough to put in a procurement questionnaire, and I would like to see somebody actually ask it:

**What is a reasoning block bound to, and how would I verify that from outside?**

A provider that has done the work can answer with a list: this user, this session, this model version, rejected otherwise. A provider that has not will answer that it is encrypted, which we now know is an answer to a different question.

The broader habit this leaves me with is a small one and it generalises past this incident. When a vendor ships a control, work out whose threat model it was built for before you decide which of your problems it solves. The hotel safe is a real safe. It just was not thinking about you.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, NOT flat-icon style. A workshop bench seen at a 30-degree diagonal sweep across the frame. A small brushed-aluminum, matte-black robot with a single round LED eye stands mid-action at the bench, caught between two motions: one hand still resting on a large sealed matte-black lockbox, the other extending a slim identical key toward a second, much smaller and cheaper-looking lockbox beside it. Both boxes carry the same sage-green keyhole indicator, visibly identical, and the smaller box has sprung open, spilling a fan of narrow paper slips across the light-oak desktop toward the viewer. In the foreground the slips overlap in a diagonal drift; most are blank, but a few catch the light with faint oxblood marks. In the midground, a slate-gray coffee mug going cold with a faint thermal curl rising, an open notebook with a hand-drawn diagram of three nested boxes, and a small potted plant. In the background, a shelf of identical unlabeled sealed boxes receding into soft focus, a corkboard with pinned diagrams, and a tall window casting warm tungsten light (~3200K) from the upper left across the bench, while a monitor at right throws cool blue-white screen glow (~5600K) over the robot's shoulder, the two temperatures meeting mid-frame. Cables run off-frame lower right creating a diagonal leading line. Palette: warm white, light oak, slate gray, with sage-green and oxblood accents. Mood: sharp, deliberate, quiet, watchful, tired-but-alert. Photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Researchers decoded 315,320 encrypted AI reasoning blocks scraped from public code repositories and pulled 182 credentials out of them. The encryption worked perfectly. It was built to stop competitors from training on the data, not to keep it private from anyone else holding the envelope.

The sharp part: a secret scanner cannot read ciphertext. So the one field in those files that no security tool could inspect was the field holding 64 secrets that appeared nowhere else.

Full piece linked in bio.

#AIsecurity #cryptography #DevSecOps #AIagents #secretsmanagement #appsec
-->
