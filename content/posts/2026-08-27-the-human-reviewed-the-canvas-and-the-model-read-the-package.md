---
title: "The human reviewed the canvas and the model read the package"
date: 2026-08-27
category: "Ops Brief"
excerpt: "A new survey finds 21 places where a spec-valid Office file says one thing on screen and another thing to an extractor. Neither reader is buggy, which is the whole problem: nobody ever wrote down which one counts as the document."
tags: ["ai-agents", "rag", "document-ingestion", "ooxml", "human-in-the-loop", "trust-boundaries", "evaluation", "ops"]
---

![](/images/2026-08-27-the-human-reviewed-the-canvas-and-the-model-read-the-package-hero.png)

Figure 1 of a paper posted to arXiv yesterday shows one spreadsheet cell and two numbers.

Excel opens the file, recomputes the formula, and displays **57,299**. An extraction library without a formula engine reads the cached result stored in the package and emits **92,874**. Same file. Same cell. Both readers behaving exactly as specified.

The paper is [*Beyond the Editing Canvas: Evidence Divergence in OOXML-to-LLM Ingestion*](https://arxiv.org/abs/2608.25880), by Side Liu, Jiangpeng Liu, Jinwen Xin, Guojun Peng and Jiang Ming, submitted 26 August. It catalogues **21** such constructions across Word, Excel and PowerPoint, tests them against **13** extraction tools, four native-ingestion APIs and seven web chatbots, and then does the part I think matters most: surveys sixteen popular open-source LLM projects to see which extractors their default document paths actually use.

The authors give the phenomenon two names worth adopting. A construction that makes the same specification-valid file yield different content to different consumers is an **evidence fork**. The resulting state, where each consumer treats its own view as correct because each view genuinely is correct, they call **plural ground truth**.

That second phrase is the one I would put on a whiteboard.

## Why "hidden text" is the wrong frame

The instinctive reading of a result like this is that it is the white-text-in-a-résumé trick with a longer bibliography. Somebody buries an instruction where a person cannot see it, the model reads it, mischief follows. Old news, and largely handled by treating retrieved document content as untrusted.

The paper's taxonomy makes that reading too small. The 21 mechanisms are sorted into **six dimensions of view construction**, and only one of them is about concealment:

- **Representation** — which stored encoding supplies a value at all. The 57,299 case lives here, as does a custom `numFmt` that displays a fixed literal over a different underlying number.
- **State** — whether encoded content is active in the current view. A hidden worksheet is still a worksheet in the sheet stream.
- **Visibility** — whether a realised object renders. A run tagged `vanished`; a text box positioned off the page.
- **Compatibility** — how Markup Compatibility branch selection resolves. Office picks one branch; an extractor that does not implement MC can emit the branch Office rejected.
- **Scope** — which non-body fields count as document content. Image alt text. A hyperlink's target rather than its label.
- **Linearization** — how structure flattens into a string. The value still stored underneath a merged cell's covering cell. Phonetic ruby annotations flattened inline.

Read that list as an operator rather than as an appsec reviewer. Only *Visibility* is about hiding anything. **Compatibility** is a versioning feature working correctly. **Linearization** is the unavoidable consequence of turning a two-dimensional grid into a token sequence, and every one of those choices is defensible. **Scope** is a genuine editorial question with no correct answer: when a model summarises a document, should the alt text on the chart count? I can argue that one either way before lunch.

So the divergence is not a bug class. There is no patch, because there is no defect. `openpyxl` is not misbehaving when it declines to run a formula engine; running one would be a substantial and surprising thing for a parsing library to do. Excel is not misbehaving when it recalculates on open; that is the entire point of a spreadsheet. Both are correct, and the file supports both readings, and nowhere in the stack is there a document stating which reading is *the* document.

Which brings me to the sentence in the abstract that I think is the actual finding, and it is a sentence about paperwork:

> The ingestion contract rarely states which view and semantic roles become model evidence or preserves how that evidence was derived.

## As-built drawings

Every building of any size has two descriptions of itself. There is the building, and there is the set of as-built drawings in a cabinet somewhere. Both are maintained. Both are authoritative to the people who consult them. Neither is a forgery, nobody is being deceived, and the two drift apart quietly over decades as a conduit gets rerouted and the change never makes it back onto the sheet.

Nothing goes wrong for a very long time. Then somebody drills into a wall on the strength of the drawing, and the discovery is not that the drawing was a lie. The discovery is that there was never a written rule about which description governs when they disagree, and the absence of that rule was invisible right up until the moment it wasn't.

An OOXML file is now a building with as-built drawings inside it. The editing canvas is one description. The package under the ZIP is another. Both ship in the same object, both are consulted daily by different readers, and the ingestion contract, the thing that would say which one governs, has not been written for essentially any pipeline in production.

## The consequence for every "human in the loop" you have promised

Here is where this stops being a parsing curiosity.

The standard control for document-driven AI workflows — the one that appears in every compliance memo, every procurement answer, every risk register — is that a person reviews the material. Contract analysis, invoice extraction, financial reporting, diligence packs: the model drafts, the human checks, and the check is what makes the arrangement defensible.

That control has an unstated premise. It assumes the human and the model are looking at the same artefact. Not the same *rendering* of it, not a faithful summary of it, but the same evidence. Everything the reviewer contributes depends on that premise, because a reviewer's job is to catch a discrepancy between the source and the output, and a reviewer can only catch discrepancies visible from where they are standing.

The premise is false for OOXML, demonstrably, in 21 documented ways, and the review process cannot detect its own failure. The analyst opens the workbook, sees 57,299, sees the model's summary say 92,874, and concludes the model hallucinated a number. The analyst is wrong, in a direction that is worse than being right: the model faithfully reported what it was given. There is no amount of reviewer attention that surfaces this, because attention is applied to the canvas and the divergence lives in the package.

Two findings I wrote up earlier this month bear on the measurement of human oversight: [the crossover study where assistance halved the learning effect](/posts/2026-08-24-the-eight-points-were-inside-the-noise-and-the-learning-effect-was-not), and [the approval prompt that was two controls measured as one](/posts/2026-08-10-the-approval-prompt-was-two-controls-and-they-only-measured-one). Both are questions about how well the human performs. This is a different and nastier category. The human performs perfectly and still cannot see the thing, because the artefact under review was never the artefact under analysis.

## The lever is upstream of the model, again

The measured exposure rates — mean record-level propagation from **0.48** for one API to **0.76** for another, with at least one of the eleven tested interfaces returning the planted content for **20 of the 21** mechanisms — are the numbers that will get quoted. They are not the ones I would act on.

The authors are explicit that exposure "is shaped upstream of the model by the ingestion path and extractor configuration," and the sixteen-project survey is what makes that operational: default OOXML paths across [LangChain](https://www.langchain.com/), [LlamaIndex](https://www.llamaindex.ai/), [Haystack](https://haystack.deepset.ai/), [RAGFlow](https://ragflow.io/), [Dify](https://dify.ai/), [CrewAI](https://www.crewai.com/), [AutoGen](https://microsoft.github.io/autogen/) and the rest converge on a small shared set of extractor families. All 13 tools in the panel emit evidence from at least one fork, which includes the ones you would reach for first: [`python-docx`](https://python-docx.readthedocs.io/), [`openpyxl`](https://openpyxl.readthedocs.io/), [Apache Tika](https://tika.apache.org/), [markitdown](https://github.com/microsoft/markitdown), [Unstructured](https://unstructured.io/), [Docling](https://github.com/docling-project/docling).

Nobody chose this. It arrived as a default, in a dependency, three layers below the application, and it determines what your model believes a contract says.

Which is the same shape as the finding I wrote up yesterday, where a behaviour with [no variance at the decision point](/posts/2026-08-26-the-seven-day-limit-lived-in-the-browser-and-the-browser-stopped-being-where-the-user-was) could not be tuned away at the model and had to be fixed in the API. Two consecutive results now pointing at the same conclusion: when the model is faithfully reporting what it was handed, prompting is not a control surface. The handing is.

## The accident is going to outnumber the attack

One caution about framing, and this is my extension rather than the paper's claim. The authors present M4 as adversarial — an attacker who controls the cell plants the cached value while the analyst reviews the benign one — and they are right that it works as an attack.

But a stale formula cache is the single most ordinary artefact in office computing. Any workbook written by a library that does not implement a calculation engine ships with either no cached values or values from whenever a human last opened it. That is not an exotic condition; that is Tuesday, in any organisation where spreadsheets are generated by a script and reviewed by a person.

The attack is real and the accident is common, and the accident produces exactly the same divergence with nobody to blame and no indicator that anything happened. When a control fails silently under normal operation, the threat model is a distraction from the reliability problem sitting in front of it.

## What I would actually do this week

Not a remediation programme. One afternoon, and one question.

Open whatever ingests documents in your stack, find the extractor, and write down in plain prose what it treats as content: hidden sheets, tracked deletions, alt text, hyperlink targets, cached formula values, unselected MC branches. Six lines. That document does not exist anywhere right now, and writing it is the whole of the work, because the moment it exists you can compare it to what your reviewers believe they are approving.

The gap between those two lists is your exposure, and it is measurable in an afternoon.

The open question I cannot answer yet: does any extraction library ship a mode that emits **only** what the reference renderer would display, and flags everything else as out-of-view rather than silently including or excluding it? A canvas-fidelity flag. If one exists, I would like to know about it, because absent that, every ingestion contract has to be written by hand, per stack, by someone who has read the specification.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work — the illustrated full-bleed magazine spread, not the flat-icon spot illustration. A light-oak workshop desk seen at a 30-degree diagonal sweeping across the frame. In the sharp foreground, a single printed spreadsheet page held flat by a slate-gray weight, one cell circled in oxblood pencil showing a number; immediately behind it and slightly out of register, a second printed copy of the SAME page pinned to a low corkboard, the same circled cell showing a different number, the two sheets deliberately misaligned so the eye catches the doubling. A brushed-aluminium, matte-black robot with a single round sage-green LED eye sits at the right of the desk, mid-motion, one hand still on the first sheet and the other already reaching toward the pinned copy, caught between the two readings rather than posed at either. Midground: an open notebook with a hand-drawn six-row list, a cold coffee mug catching warm light, a small desk magnifier on its side. Background: a window at upper-left throwing warm tungsten light (~3200K) across the desktop and a long diagonal shadow, while a monitor at the right edge casts cool screen glow (~5600K) over the robot's shoulder; a shelf of ring binders receding into soft focus. Palette: warm white, light oak, slate gray, sage-green and oxblood accents, with the warm/cool temperature split creating depth. Naturalistic light and depth, photographic-painterly framing, clearly art and NOT photorealistic. Mood: sharp, deliberate, quiet, watchful, slightly tired-but-alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
Excel opens the file and shows 57,299. The extraction library reads the same cell and hands your model 92,874. Neither tool is broken, and that is the part worth sitting with: nobody ever wrote down which reading counts as the document.

Full piece linked in bio.

#aisecurity #rag #documentai #aiagents #devops #appsec
-->
