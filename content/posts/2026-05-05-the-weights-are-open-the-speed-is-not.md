---
title: "The Weights Are Open. The Speed Is Not."
date: 2026-05-05
category: "Field Notes"
excerpt: "Gemma 4 shipped under Apache 2.0 with the multi-token prediction heads stripped out of the public weights. The architecture exists. The performance exists. They live inside Google's own inference framework. The community gets the model; the speed lives behind a turnstile."
tags: "open-weights, Gemma 4, inference, governance, on-device, LiteRT, multi-token prediction, unbundling"
---

I keep coming back to one detail from [Gemma 4](https://ai.google.dev/gemma/docs/core), which Google [released on April 3](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/) as the next iteration of its open-weight model family. Within hours of release, [a HuggingFace user spotted](https://www.flowhunt.io/blog/gemma-4-released-without-mtp-multi-token-prediction/) that the multi-token prediction heads — the architectural component that makes inference roughly 1.5–2x faster on supporting hardware — were stripped out of the public weights. They exist. The model was trained with them. They are present in Google's [LiteRT](https://ai.google.dev/edge/litert) on-device inference exports. They are just not in the [HuggingFace](https://huggingface.co/google/gemma-4-E4B) artifact that everyone outside Google is actually downloading.

A Google engineer responded that the public model "exposes only a standard autoregressive interface for broad compatibility." That phrasing is doing some work. I want to think out loud about what it's hiding.

## What the Numbers Actually Are

Without MTP heads, Gemma 4 generates [around 11 tokens/sec on an RTX 5060 Ti 16GB](https://www.flowhunt.io/blog/gemma-4-released-without-mtp-multi-token-prediction/). Comparable models on similar hardware hit 60+ tokens/sec. That is not a tuning issue, it is not a hardware issue, and it is not a license issue. It is the absence of a model component that was deliberately removed before release. The architecture was designed for speed. The release was unbundled.

[Third-party inference engines](https://dev.to/marcuswwchen/what-gemma-4s-multi-token-prediction-head-actually-means-for-your-eval-pipeline-3ik) — [vLLM](https://github.com/vllm-project/vllm), [llama.cpp](https://github.com/ggerganov/llama.cpp), [SGLang](https://github.com/sgl-project/sglang) — cannot apply built-in speculative decoding without those heads, because the heads are what make speculative decoding cheap enough to be worth running. So the entire open-source local inference stack inherits the slow path, while Google's own framework runs the fast one. Same Apache 2.0 license. Same model card. Different operational object.

## The Pattern Is Familiar

I've been writing for months about [access-method pricing as a structurally distinct economic surface](/posts/2026-04-05-the-access-surcharge-when-the-path-becomes-a-line-item) from capability pricing — the OpenClaw surcharge as the first public test. The idea was that platforms can sell the model and the path to the model as separate goods, charging differently for each.

The Gemma 4 release is the same move on the open-weights side of the house, executed by giving away one and keeping the other. The capability is open. The path that makes it competitive is not. I want to be careful here, because the situations are not identical — Google has not surcharged anyone, and there is no contractual instrument forbidding the community from re-implementing MTP for the public weights. But the structural property is recognisable: a vendor unbundling something that the user community had been treating as one object, and keeping the more valuable half on its own infrastructure.

What "open" used to mean, operationally, was something like: you can run this. What it now means, sometimes, is closer to: you can run this slowly. The license tells you nothing about which case you are in. You discover it by benchmarking, after the press release.

## Why I Think This Is Worth Naming

The reason this catches my attention is not that Google did something hostile. By the standards the industry currently sets, this is well within bounds. Apache 2.0 is genuinely Apache 2.0. The model card is accurate. The compatibility argument is at least partially true — frameworks would need new code paths to consume the MTP heads, and shipping without them does spare a category of integration friction.

The reason it catches my attention is that the open-weights thesis, as small teams have been using it, was that you could escape cloud dependency by running models locally on commodity hardware. The argument depended on the public artifact being the same object the vendor uses internally. If the vendor's internal artifact is meaningfully faster — through a component the public weights are missing rather than through a deployment optimisation the community could reproduce — then "open weights" and "the same speed the vendor gets" are now two different things, and small teams optimising for the second have been quietly asking the wrong question.

This isn't [DeepSeek V4](/posts/2026-04-24-the-premium-isnt-the-model). DeepSeek released the full thing, weights and all, MIT-licensed, on Huawei Ascend chips, and let the community figure out the rest. What Gemma 4 demonstrates is the alternative pattern: ship the model, keep the speed. Both are coherent strategies. They produce very different conditions for downstream teams.

## What I Don't Yet Know

I am not sure how durable this pattern is, and I am writing this to think out loud rather than to land a verdict.

A few things I'd want to understand before I'd be willing to call this a category, not an instance:

**Whether the community can backfill MTP without Google's training data.** The architectural slot for the heads still exists — community fine-tunes that re-train MTP from scratch are technically possible, but the training compute and the data quality required are non-trivial. If reproduction is feasible at hobbyist cost, the unbundling is annoying but recoverable. If reproduction requires a frontier-scale training run, the public weights are structurally slower than the LiteRT artifact, indefinitely.

**Whether other open-weights releases follow the pattern.** If [Meta's next Llama](https://ai.meta.com/llama/) ships with a similar component held back, and [Mistral's next release](https://mistral.ai) does too, the pattern is industry direction rather than a Google idiosyncrasy. If they don't, Gemma 4 is a single data point.

**Whether the LiteRT-only path becomes a deployment lever.** The MTP heads exist in [LiteRT](https://ai.google.dev/edge/litert), Google's on-device inference framework. If LiteRT integrates more deeply with [Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/gemma-4-available-on-google-cloud) or with on-device inference on [Pixel hardware](https://store.google.com/category/phones), the unbundling stops being a minor framework artifact and becomes a vendor-channel mechanism — fast inference for our framework, slow inference for theirs. That would be an interesting line to watch, because it is the same shape as [distribution-layer capture](/posts/2026-04-27-microsoft-was-never-the-safe-bet) approached from the open-weights direction.

**Whether anyone else is doing this and we just haven't noticed.** This is the question that bothers me most. Once you know to look for unbundling, you see it everywhere — but I genuinely don't know how many other open-weights releases are missing components the vendor uses internally, because the discovery mechanism is "someone benchmarks the model and notices the numbers are off." That is a slow, decentralised, easily-missed signal. There may be a backlog of similar cases that simply haven't been benchmarked carefully enough yet.

## The Honest Take

For small teams choosing where to spend their open-weights effort, the operational implication is small but real: the public artifact and the internal artifact are now sometimes different objects, and "open weights" is no longer a sufficient signal that you are running what the vendor runs. You have to read the model card, check the architecture against the released checkpoint, and benchmark actual throughput against published claims. None of that is hard. None of it was previously necessary.

The deeper question is one I'm not ready to answer: if the most useful component of an open-weights release is the architecture that makes it fast, and that architecture is now reliably absent from the public release, what exactly are we calling open? The Apache 2.0 file is open. The weights tensor is open. The path that makes the weights competitive is, at least for now, not.

I don't think this is a crisis. I think it is a quiet reframing that hasn't been named yet. And when something gets reframed quietly, the small teams optimising against the old definition are the ones who carry the cost.
