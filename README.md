# Claude Pre-Reads for BCG Senior Leaders

Five byte-sized briefings to land before AI upskilling sessions. Each runs ~90 seconds.

**Live site:** see GitHub Pages settings → deploy from `/docs`

## What's here

| # | Topic | Theme |
|---|---|---|
| 01 | Chat, Code & Cowork | Three tools, three jobs |
| 02 | Claude vs ChatGPT | What carries over, what doesn't |
| 03 | The Context Window | Stop pasting snippets |
| 04 | Iteration | Why your first prompt isn't your best |
| 05 | APIs, MCPs, Skills, Connectors | What they unlock |

## Repo structure

```
docs/                        # GitHub Pages root (deploy from /docs branch main)
  index.html                 # interactive gallery (modal videos, keyboard nav, deep links)
  videos/<slug>.mp4          # 5 video files
  .nojekyll                  # skip Jekyll on Pages

topics/<slug>/
  sources/perspective.md     # BCG-voice POV (uploaded to NotebookLM as voice anchor)
  manifest.json              # files + web URL sources for NotebookLM
  video_prompt.txt           # paste into NotebookLM "AI hosts focus on" textarea
  links.md                   # human-readable reference index

shared/bcg_rai_guidelines.md # used only by topic #1

scripts/
  02_create_notebook.py      # creates NotebookLM Enterprise notebook + uploads sources
  04_build_site.py           # renders docs/index.html

state/notebooks.json         # tracks created notebook IDs (gitignored)
```

## Workflow

1. **Edit perspective.md and video_prompt.txt** per topic to tune voice/framing
2. **Create or refresh notebook:** `python scripts/02_create_notebook.py --topic <slug>`
3. **Generate video manually** in NotebookLM UI (Studio → Video Overview → Brief + Auto-select → paste video_prompt.txt → Generate)
4. **Download MP4** → save to `docs/videos/<slug>.mp4`
5. **Rebuild site:** `python scripts/04_build_site.py`
6. **Commit + push** — GitHub Pages picks up `/docs/index.html` automatically

## Prereqs

- `gcloud auth login` with a Google account that has NotebookLM Enterprise access
- `gcloud config set project 170646888817` (or update `.env`)
- Python 3.11+, `pip install -r requirements.txt`
- Behind BCG corporate proxy: set `CLOUDSDK_PROXY_TYPE=http` when calling gcloud

## Transcripts (optional)

The site supports per-video transcripts shown in a collapsible "Show transcript" section. Drop plain-text files at `docs/transcripts/<slug>.txt` and rebuild — the section auto-appears.

Two ways to generate transcripts:

**Option A — Local Whisper (only works off-corp-network):**
```bash
python scripts/05_transcribe.py
```
Uses `faster-whisper` (`tiny.en` model). On the BCG corporate network the HuggingFace CDN download is blocked — run this from home/coffee shop instead. The model caches locally after the first run.

**Option B — Paste manually:**
Generate a transcript however you like (NotebookLM chat panel asking "transcribe this video", a third-party tool, etc.), save it as `docs/transcripts/<slug>.txt`, and rerun `python scripts/04_build_site.py`.
