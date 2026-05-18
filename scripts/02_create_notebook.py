#!/usr/bin/env python3
"""
Create a NotebookLM Enterprise notebook and upload sources per the topic manifest.

Usage:
    python 02_create_notebook.py --topic 4_iteration
    python 02_create_notebook.py --topic 4_iteration --dry-run

Manifest format (topics/<topic>/manifest.json):
    {
      "title": "...",
      "files": ["topics/.../sources/perspective.md", ...],
      "web_sources": [{"url": "https://...", "name": "..."}]
    }

Prereqs:
    gcloud auth login
    gcloud config set project 170646888817
    Discovery Engine API enabled
    Cloud NotebookLM User IAM role
"""
import argparse
import json
import mimetypes
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

PROJECT_NUMBER = os.environ.get("NOTEBOOKLM_PROJECT_ID", "170646888817")
LOCATION = os.environ.get("NOTEBOOKLM_LOCATION", "us")
ENDPOINT_BASE = f"https://{LOCATION}-discoveryengine.googleapis.com"
STATE_FILE = ROOT / "state" / "notebooks.json"


def gcloud_token() -> str:
    try:
        out = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"], text=True
        ).strip()
        return out
    except FileNotFoundError:
        sys.exit("gcloud CLI not found.")
    except subprocess.CalledProcessError as e:
        sys.exit(f"gcloud auth failed: {e}")


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def create_notebook(token: str, title: str) -> dict:
    url = f"{ENDPOINT_BASE}/v1alpha/projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks"
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"title": title},
        timeout=60,
    )
    if not r.ok:
        print(f"create_notebook failed: {r.status_code}\n{r.text}", file=sys.stderr)
        r.raise_for_status()
    return r.json()


def upload_file_source(token: str, notebook_id: str, file_path: Path) -> dict:
    mime, _ = mimetypes.guess_type(str(file_path))
    if mime is None:
        mime = "text/plain" if file_path.suffix == ".md" else "application/octet-stream"
    url = (
        f"{ENDPOINT_BASE}/upload/v1alpha/projects/{PROJECT_NUMBER}"
        f"/locations/{LOCATION}/notebooks/{notebook_id}/sources:uploadFile"
    )
    data = file_path.read_bytes()
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "X-Goog-Upload-File-Name": file_path.name,
            "X-Goog-Upload-Protocol": "raw",
            "Content-Type": mime,
        },
        data=data,
        timeout=120,
    )
    if not r.ok:
        print(f"upload_file({file_path.name}) failed: {r.status_code}\n{r.text}", file=sys.stderr)
        r.raise_for_status()
    return r.json()


def add_web_sources(token: str, notebook_id: str, web_sources: list[dict]) -> dict:
    """Batch-add web URL sources. Per Google docs, uses userContents envelope."""
    url = (
        f"{ENDPOINT_BASE}/v1alpha/projects/{PROJECT_NUMBER}"
        f"/locations/{LOCATION}/notebooks/{notebook_id}/sources:batchCreate"
    )
    user_contents = []
    for ws in web_sources:
        user_contents.append({
            "webContent": {
                "url": ws["url"],
            }
        })
    body = {"userContents": user_contents}
    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body,
        timeout=180,
    )
    if not r.ok:
        print(f"batchCreate web sources failed: {r.status_code}\n{r.text}", file=sys.stderr)
        # Don't raise — log + return so the caller can decide
        return {"error": r.status_code, "text": r.text, "request_body": body}
    return r.json()


def load_manifest(topic_dir: Path) -> dict:
    manifest_path = topic_dir / "manifest.json"
    if not manifest_path.exists():
        sys.exit(f"manifest.json not found at {manifest_path}")
    return json.loads(manifest_path.read_text())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    topic_dir = ROOT / "topics" / args.topic
    if not topic_dir.exists():
        sys.exit(f"Topic dir not found: {topic_dir}")

    manifest = load_manifest(topic_dir)
    title = manifest["title"]
    files = [ROOT / p for p in manifest.get("files", [])]
    web_sources = manifest.get("web_sources", [])

    print(f"Topic: {args.topic}")
    print(f"Title: {title}")
    print(f"Files ({len(files)}):")
    for f in files:
        if not f.exists():
            sys.exit(f"  MISSING: {f}")
        print(f"  - {f.relative_to(ROOT)}")
    print(f"Web sources ({len(web_sources)}):")
    for ws in web_sources:
        print(f"  - {ws['name']}\n      {ws['url']}")

    if args.dry_run:
        print("\n[dry-run] would create notebook + upload files + add web sources")
        return

    token = gcloud_token()
    print(f"\nGot gcloud token (prefix: {token[:8]}...)")

    print("Creating notebook...")
    nb = create_notebook(token, title)
    notebook_id = nb.get("notebookId", "")
    notebook_name = nb.get("name", "")
    print(f"  notebook_id = {notebook_id}")

    state = load_state()
    state[args.topic] = {
        "notebook_id": notebook_id,
        "notebook_name": notebook_name,
        "title": title,
        "files_uploaded": [],
        "web_sources_added": None,
    }
    save_state(state)

    for f in files:
        print(f"Uploading file: {f.name}...")
        resp = upload_file_source(token, notebook_id, f)
        state[args.topic]["files_uploaded"].append({
            "file": str(f.relative_to(ROOT)),
            "response": resp,
        })
        save_state(state)

    if web_sources:
        print(f"Adding {len(web_sources)} web sources via batchCreate...")
        resp = add_web_sources(token, notebook_id, web_sources)
        state[args.topic]["web_sources_added"] = resp
        save_state(state)
        if "error" in resp:
            print(f"  WARN: web sources call returned error {resp['error']}")
        else:
            print(f"  OK: batchCreate accepted")

    ui_url = f"https://notebooklm.cloud.google.com/{LOCATION}/notebook/{notebook_id}?project={PROJECT_NUMBER}"
    state[args.topic]["ui_url"] = ui_url
    save_state(state)
    print(f"\nDone. State: {STATE_FILE}")
    print(f"Open: {ui_url}")


if __name__ == "__main__":
    main()
