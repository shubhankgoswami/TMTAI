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
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Pre-Reads — Senior Leader Briefings</title>
<meta name="description" content="Five briefings to get the most out of Claude as a BCG senior leader.">
<style>
  :root {
    --navy: #1a3a52;
    --navy-dark: #0c1f30;
    --navy-light: #2c5070;
    --accent: #4f7d6a;
    --accent-soft: #e8efe9;
    --bg: #f6f3ed;
    --bg-deep: #ece7dc;
    --card: #ffffff;
    --text: #1a2530;
    --text-muted: #5e6873;
    --text-dim: #8a929c;
    --border: #e4ddcf;
    --shadow-sm: 0 1px 2px rgba(26, 58, 82, 0.04);
    --shadow-md: 0 4px 16px rgba(26, 58, 82, 0.06);
    --shadow-lg: 0 12px 32px rgba(26, 58, 82, 0.14);
    --radius: 10px;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    margin: 0;
    background: var(--bg);
    color: var(--text);
    line-height: 1.55;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }
  a { color: var(--navy); }

  /* Sticky topnav */
  .topnav {
    position: sticky;
    top: 0;
    z-index: 50;
    background: rgba(246, 243, 237, 0.92);
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
    font-size: 14px;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--navy);
    white-space: nowrap;
  }
  .chips {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }
  .chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 32px;
    height: 30px;
    padding: 0 10px;
    border-radius: 999px;
    background: transparent;
    color: var(--text-muted);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.02em;
    cursor: pointer;
    text-decoration: none;
    border: 1px solid transparent;
    transition: background .15s ease, color .15s ease, border-color .15s ease;
  }
  .chip:hover { background: var(--accent-soft); color: var(--navy); }
  .chip.watched { color: var(--accent); }
  .chip.watched::after { content: " ✓"; margin-left: 2px; }

  /* Hero */
  .hero {
    background: linear-gradient(170deg, var(--navy) 0%, var(--navy-dark) 100%);
    color: white;
    padding: 72px 24px 88px;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  .hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(60% 60% at 30% 0%, rgba(79, 125, 106, 0.18) 0%, transparent 60%);
    pointer-events: none;
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
    color: rgba(255,255,255,0.55);
    margin-bottom: 16px;
    font-weight: 600;
  }
  .hero h1 {
    font-size: clamp(30px, 5vw, 46px);
    margin: 0 0 16px;
    font-weight: 600;
    letter-spacing: -0.025em;
    line-height: 1.15;
  }
  .hero .tagline {
    font-size: clamp(15px, 1.8vw, 18px);
    color: rgba(255, 255, 255, 0.78);
    max-width: 620px;
    margin: 0 auto;
  }
  .stat-strip {
    margin: 28px auto 0;
    display: inline-flex;
    flex-wrap: wrap;
    gap: 0;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 999px;
    padding: 4px;
  }
  .stat {
    padding: 8px 18px;
    font-size: 12.5px;
    color: rgba(255,255,255,0.85);
    border-radius: 999px;
    font-weight: 500;
    white-space: nowrap;
  }
  .stat strong { color: white; font-weight: 600; }
  .how-to {
    margin-top: 20px;
    font-size: 13px;
    color: rgba(255,255,255,0.6);
  }
  .how-to kbd {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 4px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.18);
    font-family: ui-monospace, SFMono-Regular, monospace;
    font-size: 11px;
    color: rgba(255,255,255,0.85);
  }

  /* Cards grid */
  .container {
    max-width: 1180px;
    margin: -48px auto 80px;
    padding: 0 24px;
    position: relative;
  }
  .grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
  }
  @media (min-width: 720px) { .grid { grid-template-columns: repeat(2, 1fr); } }
  @media (min-width: 1080px) { .grid { grid-template-columns: repeat(3, 1fr); } }

  .card {
    background: var(--card);
    border-radius: var(--radius);
    border: 1px solid var(--border);
    box-shadow: var(--shadow-md);
    overflow: hidden;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    text-align: left;
    transition: transform .15s ease, box-shadow .2s ease, border-color .15s ease;
    position: relative;
  }
  .card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
    border-color: var(--navy-light);
  }
  .card:focus-visible {
    outline: 3px solid var(--accent);
    outline-offset: 2px;
  }
  .card.watched::after {
    content: "✓ Watched";
    position: absolute;
    top: 14px;
    right: 14px;
    font-size: 10.5px;
    color: var(--accent);
    background: var(--accent-soft);
    padding: 3px 9px;
    border-radius: 999px;
    font-weight: 600;
    letter-spacing: 0.02em;
  }
  .card-inner {
    padding: 26px 24px 22px;
    display: flex;
    flex-direction: column;
    flex: 1;
  }
  .card-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 14px;
  }
  .card-num { color: var(--navy); }
  .card-cat {
    color: var(--accent);
    padding: 2px 8px;
    background: var(--accent-soft);
    border-radius: 4px;
    font-size: 10px;
  }
  .card-title {
    font-size: 21px;
    font-weight: 600;
    color: var(--navy);
    margin: 0 0 8px;
    letter-spacing: -0.015em;
    line-height: 1.25;
  }
  .card-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin: 0 0 18px;
  }
  .card-hook {
    font-size: 13.5px;
    color: var(--text);
    border-left: 3px solid var(--accent);
    padding: 4px 0 4px 12px;
    margin: 0 0 18px;
    font-style: italic;
    line-height: 1.5;
  }
  .card-action {
    margin-top: auto;
    color: var(--navy);
    font-size: 13px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .card-action::after {
    content: "→";
    transition: transform .15s ease;
  }
  .card:hover .card-action::after { transform: translateX(3px); }

  /* Modal */
  .modal-backdrop {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(12, 31, 48, 0.65);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    z-index: 100;
    align-items: flex-start;
    justify-content: center;
    padding: 40px 16px;
    overflow-y: auto;
  }
  .modal-backdrop.open { display: flex; }
  .modal {
    background: var(--card);
    border-radius: 14px;
    max-width: 1080px;
    width: 100%;
    box-shadow: 0 24px 60px rgba(0,0,0,0.35);
    overflow: hidden;
    display: grid;
    grid-template-columns: 1fr;
  }
  @media (min-width: 920px) {
    .modal { grid-template-columns: 1.4fr 1fr; }
  }
  .modal-video {
    background: #000;
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
    color: var(--text-muted);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-right: 4px;
  }
  .speed-btn {
    background: var(--card);
    color: var(--text-muted);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 5px 9px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all .12s ease;
    font-family: inherit;
    min-width: 36px;
  }
  .speed-btn:hover {
    background: var(--accent-soft);
    color: var(--navy);
    border-color: var(--accent);
  }
  .speed-btn.active {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
  }
  .modal-placeholder {
    color: rgba(255,255,255,0.5);
    font-size: 14px;
    text-align: center;
    padding: 40px;
  }
  .modal-body {
    padding: 30px 32px 32px;
    overflow-y: auto;
    max-height: 70vh;
  }
  @media (max-width: 919px) {
    .modal-body { max-height: none; }
  }
  .modal-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 12px;
    color: var(--text-muted);
  }
  .modal-num { color: var(--navy); }
  .modal-cat {
    color: var(--accent);
    background: var(--accent-soft);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
  }
  .modal h2 {
    font-size: 24px;
    color: var(--navy);
    margin: 0 0 6px;
    font-weight: 600;
    letter-spacing: -0.015em;
  }
  .modal-sub {
    font-size: 14px;
    color: var(--text-muted);
    margin: 0 0 22px;
  }
  .perspective {
    font-size: 14.5px;
    line-height: 1.65;
  }
  .perspective h2, .perspective h3 {
    color: var(--navy);
    font-size: 15px;
    margin: 22px 0 8px;
    font-weight: 600;
  }
  .perspective p { margin: 0 0 14px; }
  .perspective strong { color: var(--navy); }
  .perspective ul, .perspective ol { padding-left: 22px; margin: 8px 0 16px; }
  .perspective li { margin-bottom: 6px; }

  .transcript-section {
    margin-top: 22px;
  }
  .transcript-toggle {
    background: transparent;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 600;
    color: var(--navy);
    cursor: pointer;
    width: 100%;
    text-align: left;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: background .12s ease;
    font-family: inherit;
  }
  .transcript-toggle:hover { background: var(--accent-soft); }
  .transcript-toggle::after {
    content: "▾";
    transition: transform .15s ease;
    color: var(--text-muted);
  }
  .transcript-toggle.open::after { transform: rotate(180deg); }
  .transcript-body {
    display: none;
    margin-top: 10px;
    padding: 16px 18px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 13.5px;
    line-height: 1.6;
    color: var(--text);
    max-height: 320px;
    overflow-y: auto;
    white-space: pre-wrap;
  }
  .transcript-toggle.open + .transcript-body { display: block; }

  .sources {
    margin-top: 22px;
    padding: 18px 18px;
    border: 1px solid var(--border);
    background: var(--bg);
    border-radius: 8px;
  }
  .sources-title {
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--text-muted);
    font-weight: 700;
    margin: 0 0 10px;
  }
  .sources ul { list-style: none; padding: 0; margin: 0; }
  .sources li { margin-bottom: 7px; font-size: 13px; line-height: 1.4; }
  .sources li::before {
    content: "→ ";
    color: var(--accent);
    font-weight: 600;
  }
  .sources a { color: var(--navy); text-decoration: none; }
  .sources a:hover { text-decoration: underline; color: var(--accent); }

  .modal-footer {
    grid-column: 1 / -1;
    border-top: 1px solid var(--border);
    padding: 14px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    background: var(--bg);
    font-size: 13px;
  }
  .modal-nav {
    display: flex;
    gap: 8px;
  }
  .modal-nav button {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
    font-weight: 500;
    color: var(--navy);
    cursor: pointer;
    transition: background .15s ease, border-color .15s ease;
  }
  .modal-nav button:hover:not(:disabled) {
    background: var(--accent-soft);
    border-color: var(--accent);
  }
  .modal-nav button:disabled { opacity: 0.4; cursor: not-allowed; }
  .modal-close {
    background: transparent;
    border: none;
    font-size: 22px;
    line-height: 1;
    cursor: pointer;
    color: var(--text-muted);
    padding: 4px 10px;
    border-radius: 4px;
  }
  .modal-close:hover { background: var(--bg-deep); color: var(--navy); }

  footer {
    text-align: center;
    padding: 32px 24px 56px;
    color: var(--text-muted);
    font-size: 12.5px;
  }
  footer a { color: var(--accent); text-decoration: none; }
  footer a:hover { text-decoration: underline; }
</style>
</head>
<body>

<nav class="topnav" aria-label="Pre-read navigation">
  <div class="topnav-inner">
    <div class="brand">Claude Pre-Reads</div>
    <div class="chips" id="chips">
      {% for t in topics %}
      <a href="#{{ t.number }}" class="chip" data-slug="{{ t.slug }}" data-num="{{ t.number }}">{{ t.number }}</a>
      {% endfor %}
    </div>
  </div>
</nav>

<header class="hero">
  <div class="hero-inner">
    <div class="eyebrow">For BCG Senior Leaders</div>
    <h1>Five briefings to get the most out of Claude</h1>
    <p class="tagline">Byte-sized pre-reads to land before the upcoming AI upskilling sessions. Watch in any order. Forward freely.</p>
    <div class="stat-strip">
      <span class="stat"><strong>5</strong> briefings</span>
      <span class="stat"><strong>~10 min</strong> total</span>
      <span class="stat">Watch in any order</span>
    </div>
    <div class="how-to">
      Click a card to open. Use <kbd>←</kbd> <kbd>→</kbd> to navigate · <kbd>Esc</kbd> to close
    </div>
  </div>
</header>

<main class="container">
  <div class="grid" id="cards">
  {% for t in topics %}
    <button class="card" id="{{ t.number }}" data-slug="{{ t.slug }}" data-index="{{ loop.index0 }}" aria-label="Open pre-read {{ t.number }}: {{ t.title }}">
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

<footer>
  Prepared by Shubhank Goswami · {{ generation_date }}
</footer>

<script>
  const TOPICS = {{ topics_json|safe }};
  const STORAGE_KEY = 'claude-prereads-watched-v1';

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
