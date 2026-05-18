# The Context Window: Stop Pasting Snippets

## What a context window actually is

Every AI model has a fixed amount of "working memory" — the total volume of text it can hold in mind at once during a single conversation. That includes everything you've typed, every document you've pasted, everything the model has said back, and the prompt the developer wired up behind the scenes. All of it lives in the same shared budget.

That budget is the **context window**, measured in tokens (roughly ¾ of a word each). Once you blow past the limit, the earliest content starts falling out of memory. The model is no longer thinking about it — it never sees those tokens again unless you re-paste them.

## Why older models forgot the middle of long documents

If you used GPT-3.5 or early GPT-4 with a long document, you may have noticed something strange: the model would summarize the first page well, the last page well, and completely miss everything in between. This isn't anecdote — it's a documented research finding called "lost in the middle." The attention mechanisms in older models gave disproportionate weight to the beginning and end of the input, and significantly less to the middle. So a 50-page document fed to those models effectively became a 10-page summary of the start and end.

Newer frontier models, including Claude, have been specifically trained to attend evenly across the entire context window. That training matters as much as the raw token count — a model with a 200K window that suffers from lost-in-the-middle is worse for real work than a smaller window that reads evenly.

## Why this changes how you should work with Claude

Most BCG users still treat Claude like a chatbot — small prompts, small attachments, short conversations. That's the habit from the GPT-3.5 era. It leaves the most valuable capability on the table.

**Claude's context window is roughly 200,000 tokens, or about 500 pages — and it reads the middle.** That's the entire client deck. The full RFP. The complete transcript stack. Together, in one conversation.

The mental shift: **Claude isn't a chatbot you ask quick questions. It's a workspace you load documents into.**

Once you make this shift, three things become possible that weren't before:

**1. Cross-cutting questions.** Drop the entire client RFP and your draft response. Ask: "Which requirements am I not addressing?" Claude reads both end-to-end and tells you.

**2. Synthesis across documents.** Paste five interview transcripts. Ask: "What did the executives disagree about?" Claude can hold all five and identify tensions you'd miss reading serially.

**3. Document-as-context conversations.** Once loaded, you can have a 20-minute conversation about a document. Each follow-up question stays grounded in the original material.

**Practical rule:** If you're tempted to paste a "summary" or a "section" — paste the whole thing instead. The model is fine with it. The work is in asking the right questions of the full corpus, not in pre-digesting it for the model.

This is the single biggest workflow change from chatbot-era usage to document-era usage. Make this shift and Claude becomes a fundamentally different tool.
