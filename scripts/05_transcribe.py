#!/usr/bin/env python3
"""
Transcribe docs/videos/*.mp4 using faster-whisper and save transcripts.

Outputs:
    docs/transcripts/<slug>.txt   — clean readable transcript (paragraphs)
    docs/transcripts/<slug>.json  — segmented {start, end, text} for future use

Usage:
    python scripts/05_transcribe.py             # transcribe all missing
    python scripts/05_transcribe.py --force     # re-transcribe all
    python scripts/05_transcribe.py --topic 4_iteration
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIDEOS_DIR = ROOT / "docs" / "videos"
TRANSCRIPTS_DIR = ROOT / "docs" / "transcripts"

MODEL_SIZE = "tiny.en"  # ~75 MB; clean two-host narration transcribes fine

SLUGS = [
    "1_chat_code_cowork",
    "2_claude_vs_chatgpt",
    "3_context_window",
    "4_iteration",
    "5_apis_mcps_skills",
]


def transcribe_one(model, slug: str):
    video = VIDEOS_DIR / f"{slug}.mp4"
    if not video.exists():
        print(f"  SKIP (no video): {slug}")
        return False

    print(f"  Transcribing {slug}.mp4 ...")
    segments, info = model.transcribe(
        str(video),
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=True,
    )

    seg_list = []
    text_parts = []
    for s in segments:
        seg_list.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        text_parts.append(s.text.strip())

    # Rough paragraph grouping by gap > 1.2s
    paragraphs = []
    current = []
    last_end = 0
    for s in seg_list:
        if last_end and s["start"] - last_end > 1.2 and current:
            paragraphs.append(" ".join(current))
            current = []
        current.append(s["text"])
        last_end = s["end"]
    if current:
        paragraphs.append(" ".join(current))

    txt_out = TRANSCRIPTS_DIR / f"{slug}.txt"
    json_out = TRANSCRIPTS_DIR / f"{slug}.json"
    txt_out.write_text("\n\n".join(paragraphs).strip() + "\n")
    json_out.write_text(json.dumps({
        "slug": slug,
        "duration": info.duration,
        "language": info.language,
        "segments": seg_list,
    }, indent=2))
    print(f"    {info.duration:.1f}s, {len(seg_list)} segments → {txt_out.name}")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Re-transcribe even if .txt exists")
    ap.add_argument("--topic", help="Single topic slug (e.g. 4_iteration)")
    args = ap.parse_args()

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    slugs = [args.topic] if args.topic else SLUGS

    pending = []
    for slug in slugs:
        txt = TRANSCRIPTS_DIR / f"{slug}.txt"
        if txt.exists() and not args.force:
            print(f"  skip (exists): {slug}")
            continue
        pending.append(slug)

    if not pending:
        print("Nothing to transcribe (use --force to redo).")
        return

    print(f"Loading whisper model: {MODEL_SIZE} (downloads on first run)")
    from faster_whisper import WhisperModel
    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    print("Model ready.\n")

    for slug in pending:
        transcribe_one(model, slug)

    print(f"\nDone. Transcripts in {TRANSCRIPTS_DIR}")


if __name__ == "__main__":
    main()
