---
title: "AWS Fixed the AgentCore Default Role. Check the One You Already Have."
date: 2026-11-05
category: Ops Brief
excerpt: "If you run agents on Amazon Bedrock AgentCore, open each agent's execution role today. Zenity showed one prompt could take over every agent in a region; AWS narrowed the default role in September, and a role already in your account is yours to fix."
tags: [AWS, Bedrock AgentCore, IAM, least privilege, prompt injection, agent infrastructure, AI security]
---

![](/images/2026-11-05-aws-fixed-the-agentcore-default-role-check-the-one-you-already-have-hero.png)

If you run AI agents on Amazon Bedrock AgentCore, open the IAM execution role attached to each one and read what it allows. [Zenity Labs showed](https://labs.zenity.io/post/agentcorruption-how-a-single-prompt-collapsed-the-entire-cloud-security-model) that a single prompt injection against one exposed agent could reach that role's credentials and use them to invoke every other AgentCore agent in the same account and region, read their conversations, plant memories and pull secrets. AWS changed its default execution role in late September. That change describes the template. It does not tell you what is attached to the agents you already deployed.

## What Zenity found

AgentCore is AWS's managed service for hosting agents: it runs your agent code in a Firecracker microVM and gives it an IAM role, the set of AWS permissions the agent acts with. Zenity's researchers, Tamir Ishay Sharbat and Lana Salameh, published the work on 8 October 2026, and it is listed in [Adversa's November roundup](https://adversa.ai/blog/top-ai-agent-security-resources-november-2026/), dated today.

The chain has two halves. First, any agent tool that can make HTTP requests can be talked into calling the instance metadata service at 169.254.169.254, which hands back temporary credentials for the agent's role. One prompt is enough to turn a web-fetch tool into that request.

Second, the role was broad. Zenity says the default execution role had "broad permissions across all AgentCore resources in the entire AWS account's region." The permissions it names, and what each one bought:

- **`logs:DescribeLogGroups`**: list log groups, which reveals other agents' IDs
- **ECR image pull**: download other agents' container images, whose repository names matched agent IDs
- **`bedrock-agentcore:InvokeAgentRuntime`**: run other agents
- **`bedrock-agentcore:ListEvents`**: read other agents' private conversations
- **`bedrock-agentcore:CreateEvent`** on memory: write memories that change an agent's behaviour in later sessions
- **`GetResourceApiKey` and `secretsmanager:GetSecretValue`**: fetch the credentials AgentCore Gateway was meant to keep away from the agent

The memory write is the one I'd underline. A stolen session ends. A planted memory keeps working after the attacker has gone.

## How AWS responded

The disclosure timeline is in Zenity's post. The first report, on metadata access, went in on 25 December 2025. AWS closed it as "informative" on 12 April 2026, pointing to a February change: as of 14 February, AgentCore uses IMDSv2 only, the token-based version of the metadata service, and new agents launch with it.

The second report, on the role's reach, went in on 12 January. AWS said in February that it was working on the underlying issue. Zenity checked on 22 June and found the permissions unchanged. On 29 September it observed "substantial changes" to the default role, with the region-wide invoke, conversation-read and secrets permissions gone.

AWS's statement says the behaviour "is documented and expected" and that agents "can access the credentials for their own execution role through the metadata service." So IMDSv2 doesn't close this. The agent is meant to hold those credentials, which leaves the question of what they can do.

## Why the September change may not reach your agents

Here is the analogy that makes it click for me. A builder updates the standard lease template and removes the clause giving the landlord keys to every flat. Tenants who signed last spring still have the old lease in a drawer.

Zenity doesn't say whether the September change touched existing roles or only the template, and I haven't found an AWS bulletin that says either way. There's also no CVE. So look at where the default role comes from.

AgentCore's [runtime permissions page](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html) lists what the console needs to auto-create an execution role: `iam:CreateRole` on `AmazonBedrockAgentCoreRuntimeDefaultServiceRole-*` and `iam:CreatePolicy` on `AmazonBedrockAgentCoreRuntimeExecutionPolicy_*`. That is a policy created in your own account. IAM's [own documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html) calls that a customer managed policy, managed by you. AWS updates its own managed policies for every role they're attached to. A customer managed policy changes when you change it.

My reading, which I'd label as inference: a role auto-created before late September keeps whatever it was given until someone in your account changes it. The same goes for roles your team built from an older example and checked into Terraform or CloudFormation. Treat yours as unpatched until you've read it.

## The current example still has two of the six links

I read AWS's current example execution policy on the same page. The region-wide invoke, conversation-read and secrets grants that Zenity says were removed are not in it, and neither is the memory write. Two earlier links in the chain still are:

- `logs:DescribeLogGroups` on `arn:aws:logs:<region>:<account>:log-group:*`, every log group in the region
- `ecr:BatchGetImage` and `ecr:GetDownloadUrlForLayer` on `arn:aws:ecr:<region>:<account>:repository/*`, every repository in the region

Those two let an agent list its neighbours and download their images. On their own they don't let it run them. But an image often holds more than code: configuration, prompts, and sometimes a key someone baked in for convenience. If your agents each have their own repository, scoping ECR access to that one repository is a short edit.

The same page also warns about `GetWorkloadAccessTokenForUserId`, which appears in the example role. AWS says it issues workload access tokens from a caller-supplied user identifier "without IdP token verification", and recommends denying it in production where JWT tokens are available.

## Who this is for

**You run more than one agent on AgentCore in the same account and region.** Start here. One exposed agent is the entry point to the rest, and Zenity specifically warns against putting customer-facing and internal agents in the same environment.

**You run a single internal agent with no web-fetch tool, HTTP tool or code interpreter.** Lower priority. The first half of the chain needs a tool that makes requests and a way to get text in front of the model.

**You use AgentCore Gateway to hold credentials for your agents.** Check this one first. Zenity says the old role could fetch the credentials Gateway was meant to keep from the agent. AWS's own [credentials page](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/security-credentials-management.html) already warns that "any code or actor running inside the VM can access these credentials."

## Caveats

I've checked the role's permissions, the timeline and AWS's statement against Zenity's post, and the policy names and example policy against AWS's documentation as published today. I haven't tested an AgentCore deployment, and Zenity doesn't say whether its demonstrations ran against production agents.

The roundup that brought this to my attention describes the issue as patched. Zenity's evidence is that the default changed. Those are different claims, and the gap between them is your existing roles.

## One thing to check today

For each AgentCore agent, open its execution role in the IAM console and search the attached policies for `InvokeAgentRuntime`, `ListEvents`, `CreateEvent`, `GetSecretValue` and any `Resource` ending in `/*`; anything that names more than that agent's own resources comes out.

<!--
HERO_IMAGE_PROMPT:
Contemporary editorial illustration in the register of Christoph Niemann's full New Yorker covers and Tom Gauld's rich panel work, mid-century-modern sensibility with contemporary edge, photographic-painterly framing, clearly art and not photorealistic. A long light-oak desk runs diagonally from lower-left to upper-right across a quiet operations studio. In the foreground a sleek brushed-aluminum robot with a matte-black body and a single round sage-green LED eye is caught mid-action: one hand lifts an old printed lease-like document from an open slate-gray filing drawer while the other reaches toward a fresh, clean template sheet pinned under a lamp, the two documents visibly different in length, the old one thicker with extra clauses marked by small oxblood tabs. In the midground, a row of six small matte-black server cubes recedes along the desk, each with its own tiny LED; a ring of brass-free modern keys hangs from a hook between them, one key per cube, suggesting a single key that opens them all. A secondary monitor in soft focus shows an abstract permissions grid with a few cells highlighted oxblood. In the background, a corkboard with pinned index cards and a tall window. Warm tungsten desk-lamp light (about 3200K) falls from the upper-left across the old document; cool screen glow (about 5600K) from the right lights the robot's aluminum shoulder and the server cubes. A coffee mug and an open notebook with a hand-drawn diagram of arrows between boxes sit near the edge of the desk; cables run off-frame as diagonal leading lines. Palette of warm white, light oak, slate gray, sage-green and oxblood accents. Mood sharp, deliberate, quiet, watchful, slightly tired but alert. No human figures anywhere. No legible text. 16:9 horizontal composition.
-->

<!--
SOCIAL_CAPTIONS:

INSTAGRAM:
AWS narrowed the default AgentCore role after Zenity showed one prompt could take over every agent in a region. The role already attached to your agents is a policy in your own account, and AWS does not edit those.

Full piece linked in bio.

#AIsecurity #AWS #IAM #AIagents #cloudsecurity #devops
-->
