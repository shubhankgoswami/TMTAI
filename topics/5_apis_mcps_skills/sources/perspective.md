# APIs, MCPs, Skills, Connectors: What They Unlock

These four words come up constantly. Most senior leaders nod, then quietly admit they don't know the difference. The good news: you don't need to know the technical details. You need to know what each one *unlocks* — because that's the part you decide about when planning AI investments.

Here's the mental model:

**API (Application Programming Interface)** — the way other software talks to Claude programmatically. If you want to build a custom tool that uses Claude under the hood — say, a deal-screening agent that runs in the background — the API is how it gets built. APIs are for engineering teams. You authorize the use case and the budget. They write the code.

**MCP (Model Context Protocol)** — a standard for giving Claude live access to your tools and data. Think of it as a universal adapter. When Claude needs to read your Outlook, your SharePoint, your Salesforce — MCP is the plumbing that makes it possible. Without MCP, every integration is custom. With MCP, integrations become standardized and reusable.

**Skills** — packaged expertise Claude can pull in on demand. A "BCG slide standards" skill, a "competitive analysis" skill, a "financial modeling" skill. Skills are how organizations bake their methodology into Claude so every user gets the firm's voice and rigor without re-typing instructions.

**Connectors** — pre-built MCP integrations to common SaaS tools. SharePoint, Outlook, Slack, Google Drive. Connectors are MCPs you don't have to build — Anthropic and partners ship them.

**The pattern:** APIs are the foundation (programmatic access). MCPs are the protocol (standard way to plug in). Skills are firm-specific expertise (your BCG knowledge as a module). Connectors are ready-to-use plug-ins to common tools.

**What this means for you as a senior leader:** you don't need to architect these. You need to know that when someone says "we want Claude to read our case folders," the answer involves a Connector or an MCP. When someone says "we want Claude to always follow BCG slide standards," the answer is a Skill. When someone says "we want a custom internal tool that uses Claude," the answer is the API. Match the ask to the right primitive, and the rest is execution.
