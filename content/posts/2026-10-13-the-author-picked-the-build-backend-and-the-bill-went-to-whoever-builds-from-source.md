---
title: "The Author Picked the Build Backend and the Bill Went to Whoever Builds From Source"
date: 2026-10-13
category: Ops Brief
excerpt: A Gentoo developer has asked Python authors to stop using uv-build. The backend is a megabyte of Rust that packages pure Python, and the cost lands on people the author never meets.
tags: [Python packaging, uv, build backends, PEP 517, Gentoo, flit, hatchling, dependencies, portability, open source maintenance]
---

![](/images/2026-10-13-the-author-picked-the-build-backend-and-the-bill-went-to-whoever-builds-from-source-hero.png)


Yesterday Michał Górny, a [Gentoo](https://www.gentoo.org/) developer who works on its Python packaging, published [a plea not to use uv-build](https://blogs.gentoo.org/mgorny/2026/10/12/a-plea-not-to-use-uv-build/). It opens with the event that prompted it: "yet another dozen packages lose keywords on Gentoo because of a single key dependency switching to uv-build." He is careful to say he has no quarrel with [uv](https://github.com/astral-sh/uv) or with [Astral](https://astral.sh/), whose tools he calls "good tools with a nice and responsive upstream." His complaint is about one line in a configuration file, and about who pays for it.

I think he is right on the narrow point, and the narrow point is worth five minutes of anyone's morning who publishes a Python package.

## What a build backend is, briefly

A Python project's `pyproject.toml` has a `[build-system]` table. It names a build backend, the program that turns a directory of source into an installable wheel. [PEP 517](https://peps.python.org/pep-0517/) made this pluggable: any front end (pip, uv, [build](https://build.pypa.io/en/stable/)) can drive any backend.

[uv-build](https://pypi.org/project/uv-build/) is Astral's backend. Its [documentation](https://docs.astral.sh/uv/concepts/build-backend/) describes it as "a great choice for most Python projects" and lists the benefits: sensible defaults with little configuration, tight integration with uv, validation of project metadata, and speed. The same page states that it "currently only supports pure Python code." Running [`uv init --lib`](https://docs.astral.sh/uv/concepts/projects/init/) writes it into a new library's `pyproject.toml` for you.

So the backend exists to package pure Python, and it is itself compiled Rust.

## The numbers, checked

Górny gives three figures. I checked each against PyPI today.

- **Size.** He says the 0.13.0 wheels run from 1.2 to 1.5 MiB. PyPI lists eighteen platform wheels for that release, from 1,236,734 bytes (macOS on Apple silicon) to 1,566,858 bytes (Linux on ppc64le). That matches.
- **The comparison.** He says the [flit-core](https://pypi.org/project/flit-core/) wheel is 45 KiB. The current release, 4.1.0, is 45,622 bytes, one file for every platform, with no dependencies declared. By my division the uv-build wheel is between 27 and 34 times the size.
- **Release rate.** He says twelve releases in the thirty days before he wrote. PyPI shows twelve, from 0.12.14 on 15 September to 0.13.0 on 9 October.

The third alternative he names, [hatchling](https://pypi.org/project/hatchling/), has a 78,748-byte wheel and declares five dependencies of its own on current Python.

The one figure I cannot check is his estimate that the speed advantage is "in the ballpark of 100 ms". Astral's page calls the backend "very fast" and gives no measurement, so that number is Górny's and should be read as an estimate from someone arguing a case.

## Who actually runs the backend

Most people who install a pure-Python package never run its backend at all. They download a wheel that was built once, on the author's machine or in CI, and unpack it. Górny says so himself.

The backend runs for the author, for contributors, for CI, and for anyone who builds from the source distribution. That last group includes distributions that build everything from source as a matter of policy. For them, a package that names `uv_build` in its build requirements now requires a Rust toolchain and a compile before a single Python file is copied. On Gentoo the compile is of uv itself: its [uv-build package](https://gitweb.gentoo.org/repo/gentoo.git/tree/dev-python/uv-build/uv-build-0.12.23.ebuild) is a thin wrapper that depends on the full uv executable, to avoid building two largely overlapping binaries.

Gentoo's [uv ebuild](https://gitweb.gentoo.org/repo/gentoo.git/tree/dev-python/uv/uv-9999.ebuild?id=a18e010bf93fcc1dcba9285f72c07890650508d7) shows what that costs. It asks for 3 GB of free disk before it starts. It rewrites the link-time optimisation setting from fat to thin, with a comment saying this "makes it possible to actually build uv on 32-bit PPC". On 32-bit Arm it turns optimisation off entirely, with the comment "otherwise, rustc/llvm runs out of address space". And three days ago Górny filed [a bug against rustix](https://github.com/bytecodealliance/rustix/issues/1700), a library uv depends on, because symbols it needs are missing on SPARC64. That issue is open.

This is where the keywords come in. A [keyword](https://wiki.gentoo.org/wiki/KEYWORDS) is Gentoo's per-architecture mark that a package is known to work there. The current uv-build ebuild carries nine: amd64, arm, arm64, loong, ppc, ppc64, riscv, s390 and x86. [Gentoo's page for the package](https://packages.gentoo.org/packages/dev-python/uv-build) shows alpha, hppa, mips and sparc as unknown. A package cannot be marked as working on an architecture where its build tool does not build. When a widely used library switches backend, every package above it on those architectures loses its mark too. That is the dozen in his opening sentence.

## The flat-pack problem

Think of flat-pack furniture shipped with screws that need an unusual driver bit. The manufacturer owns the bit, so its own assembly line is a fraction quicker. Every customer has to get hold of the bit before the first screw goes in. Most can order one. A few live where it has to be made by hand, and they are the ones writing in.

The manufacturer never sees that cost, because it does not arrive as a bug in the furniture. Here it arrives as a line removed from a distribution's package list, in a repository the author has probably never opened.

What makes this an operations question is the default. A build backend chosen deliberately is a trade-off the author has made. A build backend written into the file by `uv init` is a dependency nobody on the project decided to take, imposed on everyone downstream who builds from source.

## What to do with this

It takes about a minute to find out where you stand.

- **Read your own `[build-system]` table.** If it names `uv_build` and you did not put it there, a project template did.
- **Ask what you are using it for.** If the answer is the metadata validation or the zero-configuration layout, those are real benefits and the docs describe them accurately. If the answer is consistency with uv, PEP 517 already gives you that with any backend.
- **If you switch, verify the output.** Flit's documentation gives the replacement as `requires = ["flit_core >=3.11,<5"]` and `build-backend = "flit_core.buildapi"`. Backends differ in how they find your module and which files they include, so build a wheel before and after and compare the file lists (`python -m zipfile -l` on each wheel will print them). The package should be identical.
- **Count your build requirements as dependencies.** They rarely appear in a lock file or a dependency review, and they are code that must run on someone else's machine before yours can.

## Who this is for

**It is for** authors of pure-Python libraries, particularly ones that other packages depend on, and for anyone who keeps a project template that a team copies.

**It is not for** application developers who never publish a source distribution. If your code ships as a container image or a deployed service, your backend choice reaches nobody, and uv-build's defaults are a reasonable convenience. It is also only one side: Astral has not, as far as I can find, answered the post, and a backend that validates metadata before upload may prevent failures that a distribution packager would otherwise find later.

What I take from it is a question about defaults in scaffolding tools generally. The command that creates a project decides more than its layout. Which of the lines in your own project file were written by a generator, and who downstream is running them?

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, a full-bleed magazine spread rather than a flat icon. Mid-century-modern sensibility with a contemporary edge, photographic-painterly framing with naturalistic light and depth, clearly art and not photorealistic. Palette of warm white, light oak, slate gray, with sage-green and oxblood accents. A long light-oak packing bench runs on a strong diagonal from lower left to upper right. In the foreground, sharp, sits a very small flat cardboard parcel, open, holding a few thin plain wooden slats: the product, tiny and simple. Beside it, dwarfing it, stands a heavy oxblood cast-iron bench press machine with a large hand wheel, the tool required to assemble the slats, with a single small sage-green indicator lamp lit on its side. In the midground a sleek brushed-aluminum robot with matte-black joints and a single round LED eye is caught between two actions: one hand drops a small folded instruction slip into the tiny parcel, while the other is still resting on the hand wheel of the heavy press it is not sending along. Further down the bench, receding into soft focus, three more identical tiny parcels sit already sealed and waiting on a slatted conveyor that leads out through a hatch in the far wall. Through the hatch, in the cool distance, three small separate workbenches can be seen, each empty, one with a half-built iron frame of the same press under construction and loose castings on the floor around it. Foreground details: a ceramic mug catching warm light, a coil of packing twine trailing off the bench edge on a diagonal, a small brass postal scale with the tiny parcel's twin on it barely moving the needle, an open notebook with an abstract sketch of a wheel. Background: pegboard with tool silhouettes and a shelf of bound ledgers in soft focus. Warm tungsten lamp light from the upper left falls on the press and the robot; cool blue-white daylight comes through the hatch and a tall window at upper right, throwing long shadows back along the bench. Mood: deliberate, quiet, watchful, a small thing being sent out with a large unspoken requirement. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
A build tool for pure Python packages is now a megabyte of compiled Rust, and one command writes it into new projects by default. The author saves a fraction of a second. People who build from source on unusual hardware lose the package.

Full piece linked in bio.

#python #opensource #softwareengineering #devtools #packaging #devops
-->
