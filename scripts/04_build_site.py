#!/usr/bin/env python3
"""
Render docs/index.html — interactive gallery of the 5 Claude pre-read videos.
Designed for GitHub Pages deployment from /docs.

Reads:
    state/notebooks.json    — notebook IDs + UI URLs
    topics/<slug>/sources/perspective.md  — text body
    topics/<slug>/manifest.json  — title + sources
    docs/videos/<slug>.mp4  — video file (placeholder if missing)

Writes:
    docs/index.html  — self-contained static page (CSS + JS inline)
    docs/.nojekyll   — skip Jekyll processing on GitHub Pages

Usage:
    python scripts/04_build_site.py
"""
import json
import re
from pathlib import Path

import markdown
from jinja2 import Template

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "docs"
VIDEOS_DIR = SITE_DIR / "videos"

TOPICS = [
    {
        "slug": "1_chat_code_cowork",
        "number": "01",
        "category": "Fundamentals",
        "title": "Chat, Code & Cowork",
        "subtitle": "Three tools, three jobs. Match the tool to the work.",
        "hook": "Most people pick the wrong Claude product, then conclude Claude isn't very good. It's the interface mismatch, not the model.",
    },
    {
        "slug": "2_claude_vs_chatgpt",
        "number": "02",
        "category": "Watchouts",
        "title": "Claude vs ChatGPT",
        "subtitle": "What carries over from ChatGPT, what doesn't, and the one watch-out.",
        "hook": "80% of what you know transfers. Here's the 20% that doesn't.",
    },
    {
        "slug": "3_context_window",
        "number": "03",
        "category": "Power Moves",
        "title": "The Context Window",
        "subtitle": "Stop pasting snippets. Paste the whole thing.",
        "hook": "Claude isn't a chatbot. It's a workspace you load documents into.",
    },
    {
        "slug": "4_iteration",
        "number": "04",
        "category": "Power Moves",
        "title": "Iteration",
        "subtitle": "Why your first prompt is never your best.",
        "hook": "Your first prompt is a scaffold, not a deliverable. Real output lives in turns 2 through 5.",
    },
    {
        "slug": "5_apis_mcps_skills",
        "number": "05",
        "category": "Fundamentals",
        "title": "APIs, MCPs, Skills, Connectors",
        "subtitle": "What they unlock — and how to match the ask to the right primitive.",
        "hook": "You don't need to know how they work. You need to know what each one unlocks.",
    },
]


def md_to_html(md_text: str) -> str:
    return markdown.markdown(md_text, extensions=["extra", "smarty"])


def load_state() -> dict:
    state_path = ROOT / "state" / "notebooks.json"
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text())


def load_manifest(slug: str) -> dict:
    path = ROOT / "topics" / slug / "manifest.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def load_perspective_html(slug: str) -> str:
    path = ROOT / "topics" / slug / "sources" / "perspective.md"
    if not path.exists():
        return "<p><em>Perspective document not found.</em></p>"
    md_text = path.read_text()
    md_text = re.sub(r"^# .+?\n", "", md_text, count=1)
    return md_to_html(md_text)


def video_exists(slug: str) -> bool:
    return (VIDEOS_DIR / f"{slug}.mp4").exists()


def load_transcript(slug: str) -> str:
    path = SITE_DIR / "transcripts" / f"{slug}.txt"
    if not path.exists():
        return ""
    return path.read_text().strip()


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Pre-Reads — Senior Leader Briefings</title>
<meta name="description" content="Five briefings to get the most out of Claude as a BCG senior leader.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script>
  // Apply saved theme before paint to avoid flash
  (function() {
    var saved = localStorage.getItem('claude-prereads-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
  })();
</script>
<style>
  /* Dark theme (default) */
  :root, [data-theme="dark"] {
    --bg: #1a1a1a;
    --bg-2: #2a2a2a;
    --bg-3: #222;
    --bg-4: #161616;
    --border: #333;
    --border-soft: #2e2e2e;
    --accent: #00C47A;
    --accent-2: #7F77DD;
    --accent-soft: rgba(0,196,122,0.10);
    --accent-soft-2: rgba(0,196,122,0.05);
    --accent-glow: rgba(0,196,122,0.12);
    --text: #ffffff;
    --text-2: #d0d0d0;
    --text-3: #a0a0a0;
    --text-4: #888;
    --text-5: #666;
    --text-6: #555;
    --topnav-bg: rgba(26, 26, 26, 0.85);
    --video-bg: #000;
    --shadow-md: 0 4px 16px rgba(0,0,0,0.25);
    --shadow-lg: 0 24px 60px rgba(0,0,0,0.55);
    --radius: 10px;
  }

  /* Light theme */
  [data-theme="light"] {
    --bg: #f6f3ed;
    --bg-2: #ffffff;
    --bg-3: #faf8f3;
    --bg-4: #ece7dc;
    --border: #e4ddcf;
    --border-soft: #efe9dc;
    --accent: #00A36A;
    --accent-2: #7F77DD;
    --accent-soft: rgba(0,163,106,0.10);
    --accent-soft-2: rgba(0,163,106,0.04);
    --accent-glow: rgba(0,163,106,0.18);
    --text: #1a2530;
    --text-2: #2c3742;
    --text-3: #5e6873;
    --text-4: #7a838c;
    --text-5: #9aa3ac;
    --text-6: #b4bbc4;
    --topnav-bg: rgba(246, 243, 237, 0.85);
    --video-bg: #0a0a0a;
    --shadow-md: 0 4px 16px rgba(26, 58, 82, 0.06);
    --shadow-lg: 0 12px 32px rgba(0,0,0,0.18);
    --radius: 10px;
  }

  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    margin: 0;
    background: var(--bg);
    color: var(--text);
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
    transition: background-color 0.2s ease, color 0.2s ease;
  }
  a { color: var(--accent); }

  /* Sticky topnav */
  .topnav {
    position: sticky;
    top: 0;
    z-index: 50;
    background: var(--topnav-bg);
    backdrop-filter: saturate(180%) blur(10px);
    -webkit-backdrop-filter: saturate(180%) blur(10px);
    border-bottom: 1px solid var(--border);
  }
  .topnav-inner {
    max-width: 1180px;
    margin: 0 auto;
    padding: 12px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    justify-content: space-between;
  }
  .brand {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.02em;
    color: var(--text);
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .brand::before {
    content: "";
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 12px var(--accent-glow);
  }
  .topnav-right {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .chips {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
  }
  .chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 30px;
    height: 28px;
    padding: 0 9px;
    border-radius: 999px;
    background: transparent;
    color: var(--text-5);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
    cursor: pointer;
    text-decoration: none;
    border: 1px solid var(--border);
    transition: all .15s ease;
  }
  .chip:hover {
    background: var(--accent-soft);
    color: var(--accent);
    border-color: var(--accent);
  }
  .chip.watched { color: var(--accent); border-color: var(--accent-soft); }
  .chip.watched::after { content: " ✓"; margin-left: 2px; font-weight: 700; }

  .theme-toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-3);
    cursor: pointer;
    transition: all .15s ease;
    padding: 0;
  }
  .theme-toggle:hover {
    color: var(--accent);
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  .theme-toggle svg { width: 15px; height: 15px; }
  [data-theme="dark"] .theme-toggle .icon-sun { display: block; }
  [data-theme="dark"] .theme-toggle .icon-moon { display: none; }
  [data-theme="light"] .theme-toggle .icon-sun { display: none; }
  [data-theme="light"] .theme-toggle .icon-moon { display: block; }

  /* Hero */
  .hero {
    padding: 56px 24px 30px;
    text-align: center;
    position: relative;
  }
  .hero-inner {
    max-width: 880px;
    margin: 0 auto;
    position: relative;
  }
  .eyebrow {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--text-5);
    margin-bottom: 16px;
    font-weight: 600;
  }
  .hero h1 {
    font-size: clamp(26px, 4.2vw, 40px);
    margin: 0 0 14px;
    font-weight: 600;
    letter-spacing: -0.02em;
    line-height: 1.2;
    color: var(--text);
  }
  .hero h1 span.accent { color: var(--accent); }
  .hero .tagline {
    font-size: clamp(14px, 1.6vw, 16px);
    color: var(--text-3);
    max-width: 620px;
    margin: 0 auto;
    line-height: 1.6;
  }
  .stat-strip {
    margin: 24px auto 0;
    display: inline-flex;
    flex-wrap: wrap;
    gap: 0;
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 4px;
  }
  .stat {
    padding: 7px 16px;
    font-size: 12px;
    color: var(--text-3);
    border-radius: 999px;
    font-weight: 500;
    white-space: nowrap;
  }
  .stat strong { color: var(--text); font-weight: 600; }
  .how-to {
    margin-top: 16px;
    font-size: 12px;
    color: var(--text-5);
  }
  .how-to kbd {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    background: var(--bg-2);
    border: 1px solid var(--border);
    font-family: ui-monospace, SFMono-Regular, monospace;
    font-size: 11px;
    color: var(--text-3);
  }

  /* Spectrum bar */
  .spectrum-bar {
    max-width: 880px;
    margin: 32px auto 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 8px;
  }
  .spectrum-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-5);
    font-weight: 600;
  }
  .spectrum-line {
    flex: 1;
    height: 2px;
    margin: 0 16px;
    background: linear-gradient(90deg, var(--accent) 0%, var(--accent) 55%, var(--accent-2) 100%);
    border-radius: 1px;
    opacity: 0.7;
  }

  /* Cards grid */
  .container {
    max-width: 1180px;
    margin: 36px auto 64px;
    padding: 0 24px;
    position: relative;
  }
  .grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 14px;
  }
  @media (min-width: 720px) { .grid { grid-template-columns: repeat(2, 1fr); } }
  @media (min-width: 1080px) { .grid { grid-template-columns: repeat(3, 1fr); } }

  .card {
    background: var(--bg-2);
    border-radius: 12px;
    border: 1px solid var(--border);
    overflow: hidden;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    text-align: left;
    transition: transform .15s ease, background .2s ease, border-color .15s ease, box-shadow .2s ease;
    position: relative;
    padding: 0;
    font-family: inherit;
  }
  .card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
  }
  .card[data-cat="Watchouts"]::before {
    background: linear-gradient(90deg, var(--accent), var(--accent-2));
  }
  .card[data-cat="Power Moves"]::before {
    background: var(--accent-2);
  }
  .card:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
    box-shadow: 0 4px 20px var(--accent-glow);
    background: var(--bg-3);
  }
  .card:focus-visible {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
  }
  .card.watched .badge-watched { display: inline-flex; }
  .badge-watched {
    display: none;
    position: absolute;
    top: 12px;
    right: 12px;
    font-size: 10px;
    color: var(--accent);
    background: var(--accent-soft);
    padding: 3px 8px;
    border-radius: 4px;
    font-weight: 600;
    letter-spacing: 0.04em;
    align-items: center;
    gap: 4px;
  }
  .card-inner {
    padding: 18px 18px 16px;
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  .card-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 10px;
    color: var(--text-5);
  }
  .card-num { color: var(--text-4); }
  .card-cat {
    color: var(--accent);
    padding: 2px 7px;
    background: var(--accent-soft);
    border-radius: 3px;
    font-size: 9px;
  }
  .card[data-cat="Watchouts"] .card-cat { color: var(--accent-2); background: rgba(127,119,221,0.12); }
  .card[data-cat="Power Moves"] .card-cat { color: var(--accent-2); background: rgba(127,119,221,0.12); }
  .card-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 8px;
    letter-spacing: -0.01em;
    line-height: 1.3;
  }
  .card-subtitle {
    font-size: 12px;
    color: var(--text-4);
    margin: 0 0 12px;
    line-height: 1.5;
  }
  .card-hook {
    font-size: 12px;
    color: var(--text-2);
    border-left: 2px solid var(--accent);
    padding: 2px 0 2px 10px;
    margin: 0 0 14px;
    line-height: 1.5;
  }
  .card-action {
    margin-top: auto;
    color: var(--accent);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.03em;
    display: flex;
    align-items: center;
    gap: 6px;
    opacity: 0.85;
    transition: opacity .15s ease;
  }
  .card-action::after {
    content: "→";
    transition: transform .15s ease;
  }
  .card:hover .card-action { opacity: 1; }
  .card:hover .card-action::after { transform: translateX(3px); }

  /* Modal */
  .modal-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.72);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    z-index: 100;
    align-items: flex-start;
    justify-content: center;
    padding: 40px 16px;
    overflow-y: auto;
  }
  .modal-backdrop.open { display: flex; }
  .modal {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 14px;
    max-width: 1080px;
    width: 100%;
    box-shadow: var(--shadow-lg);
    overflow: hidden;
    display: grid;
    grid-template-columns: 1fr;
  }
  @media (min-width: 920px) {
    .modal { grid-template-columns: 1.4fr 1fr; }
  }
  .modal-video {
    background: var(--video-bg);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 280px;
  }
  .modal-video video {
    width: 100%;
    height: 100%;
    max-height: 70vh;
    object-fit: contain;
    display: block;
  }
  .speed-controls {
    display: flex;
    gap: 4px;
    align-items: center;
  }
  .speed-label {
    color: var(--text-5);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-right: 4px;
  }
  .speed-btn {
    background: var(--bg-3);
    color: var(--text-3);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all .12s ease;
    font-family: inherit;
    min-width: 34px;
  }
  .speed-btn:hover {
    background: var(--accent-soft);
    color: var(--accent);
    border-color: var(--accent);
  }
  .speed-btn.active {
    background: var(--accent);
    color: #0a0a0a;
    border-color: var(--accent);
  }
  .modal-placeholder {
    color: var(--text-5);
    font-size: 13px;
    text-align: center;
    padding: 40px;
  }
  .modal-body {
    padding: 26px 28px 28px;
    overflow-y: auto;
    max-height: 70vh;
    color: var(--text-2);
  }
  @media (max-width: 919px) {
    .modal-body { max-height: none; }
  }
  .modal-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 10px;
    color: var(--text-5);
  }
  .modal-num { color: var(--text-4); }
  .modal-cat {
    color: var(--accent);
    background: var(--accent-soft);
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 9px;
  }
  .modal h2 {
    font-size: 20px;
    color: var(--text);
    margin: 0 0 6px;
    font-weight: 600;
    letter-spacing: -0.015em;
    line-height: 1.3;
  }
  .modal-sub {
    font-size: 13px;
    color: var(--text-3);
    margin: 0 0 20px;
    line-height: 1.55;
  }
  .perspective {
    font-size: 13.5px;
    line-height: 1.65;
    color: var(--text-2);
  }
  .perspective h2, .perspective h3 {
    color: var(--text);
    font-size: 14px;
    margin: 20px 0 8px;
    font-weight: 600;
  }
  .perspective p { margin: 0 0 12px; }
  .perspective strong { color: var(--text); font-weight: 600; }
  .perspective ul, .perspective ol { padding-left: 22px; margin: 8px 0 14px; }
  .perspective li { margin-bottom: 6px; }

  .transcript-section {
    margin-top: 20px;
  }
  .transcript-toggle {
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 13px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-2);
    cursor: pointer;
    width: 100%;
    text-align: left;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: background .12s ease, border-color .12s ease;
    font-family: inherit;
  }
  .transcript-toggle:hover {
    background: var(--accent-soft);
    border-color: var(--accent);
    color: var(--accent);
  }
  .transcript-toggle::after {
    content: "▾";
    transition: transform .15s ease;
    color: var(--text-5);
  }
  .transcript-toggle.open::after { transform: rotate(180deg); color: var(--accent); }
  .transcript-body {
    display: none;
    margin-top: 10px;
    padding: 14px 16px;
    background: var(--bg-4);
    border: 1px solid var(--border-soft);
    border-radius: 6px;
    font-size: 12.5px;
    line-height: 1.65;
    color: var(--text-2);
    max-height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
  }
  .transcript-toggle.open + .transcript-body { display: block; }

  .sources {
    margin-top: 20px;
    padding: 14px 16px;
    border: 1px solid var(--border-soft);
    background: var(--bg-4);
    border-radius: 8px;
  }
  .sources-title {
    font-size: 9.5px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-5);
    font-weight: 700;
    margin: 0 0 8px;
  }
  .sources ul { list-style: none; padding: 0; margin: 0; }
  .sources li { margin-bottom: 6px; font-size: 12px; line-height: 1.45; }
  .sources li::before {
    content: "→ ";
    color: var(--accent);
    font-weight: 600;
  }
  .sources a { color: var(--text-2); text-decoration: none; }
  .sources a:hover { color: var(--accent); }

  .modal-footer {
    grid-column: 1 / -1;
    border-top: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    background: var(--bg-3);
    font-size: 12px;
    flex-wrap: wrap;
  }
  .modal-nav {
    display: flex;
    gap: 6px;
  }
  .modal-nav button {
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 500;
    color: var(--text-2);
    cursor: pointer;
    transition: all .15s ease;
    font-family: inherit;
  }
  .modal-nav button:hover:not(:disabled) {
    background: var(--accent-soft);
    border-color: var(--accent);
    color: var(--accent);
  }
  .modal-nav button:disabled { opacity: 0.35; cursor: not-allowed; }
  .modal-close {
    background: transparent;
    border: none;
    font-size: 20px;
    line-height: 1;
    cursor: pointer;
    color: var(--text-5);
    padding: 4px 10px;
    border-radius: 4px;
    transition: color .15s ease, background .15s ease;
  }
  .modal-close:hover { background: var(--bg-2); color: var(--text); }

  footer {
    text-align: center;
    padding: 26px 24px 48px;
    color: var(--text-5);
    font-size: 12px;
    border-top: 1px solid var(--border);
    margin-top: 32px;
  }
  footer a { color: var(--accent); text-decoration: none; }
  footer a:hover { text-decoration: underline; }
  .footer-signature {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
    color: var(--text-3);
    font-size: 13px;
  }
  .footer-signature::before {
    content: "✦";
    color: var(--accent);
  }
</style>
</head>
<body>

<nav class="topnav" aria-label="Pre-read navigation">
  <div class="topnav-inner">
    <div class="brand">Claude Pre-Reads</div>
    <div class="topnav-right">
      <div class="chips" id="chips">
        {% for t in topics %}
        <a href="#{{ t.number }}" class="chip" data-slug="{{ t.slug }}" data-num="{{ t.number }}">{{ t.number }}</a>
        {% endfor %}
      </div>
      <button class="theme-toggle" id="theme-toggle" aria-label="Toggle theme" title="Toggle light/dark mode">
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
        </svg>
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </button>
    </div>
  </div>
</nav>

<header class="hero">
  <div class="hero-inner">
    <div class="eyebrow">For BCG Senior Leaders</div>
    <h1>Five briefings to get the most out of <span class="accent">Claude</span></h1>
    <p class="tagline">Byte-sized pre-reads to land before the upcoming AI upskilling sessions. Watch in any order. Forward freely.</p>
    <div class="stat-strip">
      <span class="stat"><strong>5</strong> briefings</span>
      <span class="stat"><strong>~10 min</strong> total</span>
      <span class="stat">Any order</span>
    </div>
    <div class="how-to">
      Click a card to open · <kbd>←</kbd> <kbd>→</kbd> navigate · <kbd>Esc</kbd> close
    </div>
    <div class="spectrum-bar">
      <span class="spectrum-label">Fundamentals</span>
      <div class="spectrum-line"></div>
      <span class="spectrum-label">Power Moves</span>
    </div>
  </div>
</header>

<main class="container">
  <div class="grid" id="cards">
  {% for t in topics %}
    <button class="card" id="{{ t.number }}" data-slug="{{ t.slug }}" data-cat="{{ t.category }}" data-index="{{ loop.index0 }}" aria-label="Open pre-read {{ t.number }}: {{ t.title }}">
      <span class="badge-watched">✓ Watched</span>
      <div class="card-inner">
        <div class="card-meta">
          <span class="card-num">{{ t.number }}</span>
          <span class="card-cat">{{ t.category }}</span>
        </div>
        <h2 class="card-title">{{ t.title }}</h2>
        <p class="card-subtitle">{{ t.subtitle }}</p>
        <p class="card-hook">"{{ t.hook }}"</p>
        <div class="card-action">Watch &amp; read</div>
      </div>
    </button>
  {% endfor %}
  </div>
</main>

<div class="modal-backdrop" id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
  <div class="modal">
    <div class="modal-video" id="modal-video-player"></div>
    <div class="modal-body">
      <div class="modal-meta">
        <span class="modal-num" id="modal-num"></span>
        <span class="modal-cat" id="modal-cat"></span>
      </div>
      <h2 id="modal-title"></h2>
      <p class="modal-sub" id="modal-sub"></p>
      <div class="perspective" id="modal-perspective"></div>
      <div class="transcript-section" id="modal-transcript-section" style="display:none">
        <button class="transcript-toggle" id="transcript-toggle">Show transcript</button>
        <div class="transcript-body" id="modal-transcript"></div>
      </div>
      <div class="sources" id="modal-sources" style="display:none">
        <p class="sources-title">References</p>
        <ul id="modal-sources-list"></ul>
      </div>
    </div>
    <div class="modal-footer">
      <div class="modal-nav">
        <button id="prev-btn">← Previous</button>
        <button id="next-btn">Next →</button>
      </div>
      <div class="speed-controls" id="speed-controls" style="display:none">
        <span class="speed-label">Speed</span>
        <button class="speed-btn" data-speed="1">1×</button>
        <button class="speed-btn active" data-speed="1.25">1.25×</button>
        <button class="speed-btn" data-speed="1.5">1.5×</button>
        <button class="speed-btn" data-speed="2">2×</button>
      </div>
      <button class="modal-close" id="close-btn" aria-label="Close">✕</button>
    </div>
  </div>
</div>


<script>
  const TOPICS = {{ topics_json|safe }};
  const STORAGE_KEY = 'claude-prereads-watched-v1';
  const THEME_KEY = 'claude-prereads-theme';

  // Theme toggle
  document.getElementById('theme-toggle').addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem(THEME_KEY, next);
  });

  function getWatched() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }
    catch { return []; }
  }
  function markWatched(slug) {
    const w = getWatched();
    if (!w.includes(slug)) { w.push(slug); localStorage.setItem(STORAGE_KEY, JSON.stringify(w)); }
    paintWatched();
  }
  function paintWatched() {
    const w = getWatched();
    document.querySelectorAll('.card').forEach(c => {
      c.classList.toggle('watched', w.includes(c.dataset.slug));
    });
    document.querySelectorAll('.chip').forEach(c => {
      c.classList.toggle('watched', w.includes(c.dataset.slug));
    });
  }

  let currentIndex = -1;
  const modal = document.getElementById('modal');

  function openTopic(idx) {
    if (idx < 0 || idx >= TOPICS.length) return;
    currentIndex = idx;
    const t = TOPICS[idx];

    // Pause any playing videos elsewhere
    document.querySelectorAll('video').forEach(v => v.pause());

    document.getElementById('modal-num').textContent = t.number;
    document.getElementById('modal-cat').textContent = t.category;
    document.getElementById('modal-title').textContent = t.title;
    document.getElementById('modal-sub').textContent = t.subtitle;
    document.getElementById('modal-perspective').innerHTML = t.perspective_html;

    const vc = document.getElementById('modal-video-player');
    const speedCtl = document.getElementById('speed-controls');
    if (t.has_video) {
      vc.innerHTML = '<video controls autoplay playsinline preload="metadata" src="videos/' + t.slug + '.mp4"></video>';
      const v = vc.querySelector('video');
      v.addEventListener('ended', () => markWatched(t.slug));
      v.addEventListener('play', () => markWatched(t.slug));
      const savedSpeed = parseFloat(localStorage.getItem('claude-prereads-speed') || '1.25');
      v.addEventListener('loadedmetadata', () => { v.playbackRate = savedSpeed; });
      speedCtl.style.display = 'flex';
      document.querySelectorAll('.speed-btn').forEach(b => {
        b.classList.toggle('active', parseFloat(b.dataset.speed) === savedSpeed);
      });
    } else {
      vc.innerHTML = '<div class="modal-placeholder">Video pending — drop <code>' + t.slug + '.mp4</code> into <code>docs/videos/</code> and reload.</div>';
      speedCtl.style.display = 'none';
    }

    // Transcript
    const transcriptSection = document.getElementById('modal-transcript-section');
    const transcriptBody = document.getElementById('modal-transcript');
    const transcriptToggle = document.getElementById('transcript-toggle');
    if (t.has_transcript) {
      transcriptSection.style.display = 'block';
      transcriptBody.textContent = t.transcript;
      transcriptToggle.classList.remove('open');
      transcriptToggle.textContent = 'Show transcript';
    } else {
      transcriptSection.style.display = 'none';
    }

    const srcWrap = document.getElementById('modal-sources');
    const srcList = document.getElementById('modal-sources-list');
    srcList.innerHTML = '';
    if (t.sources && t.sources.length) {
      srcWrap.style.display = 'block';
      t.sources.forEach(s => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = s.url; a.target = '_blank'; a.rel = 'noopener';
        a.textContent = s.name;
        li.appendChild(a);
        srcList.appendChild(li);
      });
    } else {
      srcWrap.style.display = 'none';
    }

    document.getElementById('prev-btn').disabled = idx === 0;
    document.getElementById('next-btn').disabled = idx === TOPICS.length - 1;

    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
    if (location.hash !== '#' + t.number) {
      history.replaceState(null, '', '#' + t.number);
    }
    // focus the body for keyboard
    setTimeout(() => modal.querySelector('.modal-body').focus(), 60);
  }

  function closeModal() {
    const v = modal.querySelector('video');
    if (v) v.pause();
    modal.classList.remove('open');
    document.body.style.overflow = '';
    currentIndex = -1;
    history.replaceState(null, '', location.pathname + location.search);
  }

  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', () => openTopic(parseInt(card.dataset.index)));
  });
  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', (e) => {
      e.preventDefault();
      const idx = TOPICS.findIndex(t => t.number === chip.dataset.num);
      if (idx >= 0) openTopic(idx);
    });
  });

  document.getElementById('prev-btn').addEventListener('click', () => openTopic(currentIndex - 1));
  document.getElementById('next-btn').addEventListener('click', () => openTopic(currentIndex + 1));
  document.getElementById('close-btn').addEventListener('click', closeModal);
  modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });

  document.addEventListener('keydown', e => {
    if (!modal.classList.contains('open')) return;
    if (e.key === 'Escape') closeModal();
    else if (e.key === 'ArrowLeft' && currentIndex > 0) openTopic(currentIndex - 1);
    else if (e.key === 'ArrowRight' && currentIndex < TOPICS.length - 1) openTopic(currentIndex + 1);
  });

  // Speed buttons
  document.querySelectorAll('.speed-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const speed = parseFloat(btn.dataset.speed);
      const v = document.querySelector('#modal-video-player video');
      if (v) v.playbackRate = speed;
      localStorage.setItem('claude-prereads-speed', speed);
      document.querySelectorAll('.speed-btn').forEach(b => b.classList.toggle('active', b === btn));
    });
  });

  // Transcript toggle
  document.getElementById('transcript-toggle').addEventListener('click', (e) => {
    const btn = e.currentTarget;
    btn.classList.toggle('open');
    btn.textContent = btn.classList.contains('open') ? 'Hide transcript' : 'Show transcript';
  });

  // Deep link support
  if (location.hash) {
    const num = location.hash.replace('#', '');
    const idx = TOPICS.findIndex(t => t.number === num);
    if (idx >= 0) setTimeout(() => openTopic(idx), 80);
  }

  paintWatched();
</script>

</body>
</html>
"""


def main():
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

    state = load_state()
    enriched = []
    for t in TOPICS:
        slug = t["slug"]
        manifest = load_manifest(slug)
        nb = state.get(slug, {})
        transcript = load_transcript(slug)
        enriched.append({
            **t,
            "perspective_html": load_perspective_html(slug),
            "has_video": video_exists(slug),
            "sources": manifest.get("web_sources", []),
            "notebook_url": nb.get("ui_url", ""),
            "transcript": transcript,
            "has_transcript": bool(transcript),
        })

    from datetime import date
    template = Template(HTML_TEMPLATE)
    html = template.render(
        topics=enriched,
        topics_json=json.dumps(enriched, ensure_ascii=False),
        generation_date=date.today().strftime("%B %Y"),
    )

    out_path = SITE_DIR / "index.html"
    out_path.write_text(html)
    (SITE_DIR / ".nojekyll").touch()

    print(f"Wrote {out_path}")
    print(f"Wrote {SITE_DIR / '.nojekyll'}")
    print(f"Videos found: {sum(1 for t in enriched if t['has_video'])}/{len(enriched)}")
    for t in enriched:
        status = "✓" if t["has_video"] else "·"
        print(f"  [{status}] {t['slug']:30s} videos/{t['slug']}.mp4")
    print(f"\nOpen locally: file://{out_path}")


if __name__ == "__main__":
    main()
