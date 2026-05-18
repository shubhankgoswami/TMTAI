# APIs, MCPs, Skills, Connectors: What They Unlock

These four words come up constantly. Most senior leaders nod, then quietly admit they don't know the difference. The good news: you don't need the technical details. You need to know what each one **unlocks** — because that's the layer you make decisions at when planning AI investments.

The four primitives are not interchangeable. Each lives at a different layer of the stack. Here's the right mental model, in the order that makes sense to learn them:

## 1. API — the foundation

**An API (Application Programming Interface) is how other software talks to Claude programmatically.** Not through the chat interface — through code.

When a developer wants to build a custom internal tool that uses Claude under the hood — say, a deal-screening agent that runs in the background, or a research assistant inside your team's existing software — they call Anthropic's API directly from their code. The API takes a prompt, returns a response, charges per token. Everything else in this list ultimately sits on top of the API.

**Senior leader takeaway:** When someone says "we want to build a custom internal tool that uses Claude" — the answer is the API. You're approving a build, not a configuration. APIs are how engineering teams ship AI-powered software.

## 2. Connector — the easy "plug in to my tools" answer

**A Connector is a pre-built bridge from Claude to a specific SaaS tool.** Anthropic and partners ship them: SharePoint, Outlook, Salesforce, Google Drive, Slack, GitHub, and so on.

You enable a Connector in your Claude settings. Claude can now read from (and sometimes write to) that tool, using your existing permissions. No code. No engineering team. Five-minute setup. The Connector for SharePoint, for instance, lets Claude search your case folders and read documents when you ask it to.

**Senior leader takeaway:** When someone says "we want Claude to access our SharePoint / Outlook / Salesforce" — the answer is usually a Connector. Check if Anthropic already ships one. If yes, the work is configuration, not engineering.

## 3. MCP — the open standard under the Connectors

**MCP (Model Context Protocol) is the open protocol that powers Connectors and lets anyone build their own.** Think of it as the universal plug standard for AI tool integrations.

The key distinction from API: an **API** is how external code calls *into* Claude. **MCP** is how Claude calls *out to* tools and data sources. They run in opposite directions.

If you need Claude to integrate with a tool that doesn't have a Connector yet — say, your firm's internal knowledge platform, or a proprietary client system — your engineering team builds an "MCP server" for that tool. Once built, the integration is reusable: any MCP-compatible AI (Claude, others) can plug into it without rewriting the bridge.

**Senior leader takeaway:** When someone says "we want Claude to access [system that doesn't have a Connector]" — the answer involves MCP. It's a build, but the protocol is standardized, so the build is much smaller than a one-off integration.

## 4. Skill — packaged firm-specific expertise

**A Skill is packaged expertise that Claude can pull in on demand.** Different from a Connector (which connects to data). A Skill is methodology: a "BCG slide standards" Skill, a "competitive analysis framework" Skill, a "client memo voice" Skill.

When you ask Claude to "build a slide using BCG slide standards," the Skill loads the right templates, formatting rules, and tone-of-voice instructions automatically — without you re-typing them every time. Organizations use Skills to bake their methodology into Claude so every user gets the firm's voice and rigor by default.

**Senior leader takeaway:** When someone says "we want Claude to always follow [our way of doing X]" — the answer is a Skill.

## The pattern

- **API** = code talking to Claude (build a custom internal tool)
- **Connector** = ready-made bridge to a common SaaS tool (configure in 5 minutes)
- **MCP** = the protocol underneath Connectors, for custom integrations (build when no Connector exists)
- **Skill** = firm-specific methodology packaged for reuse (your BCG knowledge as a module)

Match the ask to the right primitive, and the rest is execution.
