#!/usr/bin/env python3
"""Render the CV catalogue with Chrome and check focused CV page limits.

Unchanged documents are reused using a fingerprint of their HTML, print CSS,
renderer script and Chrome version. --check validates committed PDFs locally
without launching a browser. The English master keeps its established PDF URL.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'assets/cv/manifest.json'
STATE = ROOT / 'assets/cv/render-state.json'


def pages(path: Path) -> int:
    data = path.read_bytes()
    if not data.startswith(b'%PDF-'):
        raise ValueError(f'{path.name}: not a PDF')
    count = len(re.findall(rb'/Type\s*/Page\b', data))
    if not count:
        raise ValueError(f'{path.name}: no readable Chrome PDF page objects')
    return count


def check(documents):
    errors = []
    for doc in documents:
        try:
            count = pages(ROOT / doc['pdf'])
            if doc.get('max_pages') and count > doc['max_pages']:
                errors.append(f'{doc["profile"]}/{doc["language"]}: {count} pages exceeds {doc["max_pages"]}')
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    if errors:
        raise ValueError('\n'.join(errors))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check PDF files and page limits without rendering')
    parser.add_argument('--force', action='store_true', help='Render every CV, including unchanged documents')
    args = parser.parse_args()
    documents = json.loads(MANIFEST.read_text())['documents']
    if args.check:
        check(documents)
        print(f'Checked {len(documents)} PDF files and focused CV page limits.')
        return
    chrome = next((shutil.which(name) for name in ('google-chrome', 'chromium', 'chromium-browser') if shutil.which(name)), None)
    if not chrome:
        raise SystemExit('Chrome/Chromium is required to render CVs. Use --check to validate existing PDFs.')
    version = subprocess.check_output([chrome, '--version'], text=True).strip()
    shared = (ROOT / 'assets/css/site.css').read_bytes() + Path(__file__).read_bytes() + version.encode()
    previous = json.loads(STATE.read_text()) if STATE.exists() else {}

    def render_document(doc):
        key = f'{doc["profile"]}:{doc["language"]}'
        source = ROOT / doc['page']
        destination = ROOT / doc['pdf']
        fingerprint = hashlib.sha256(shared + source.read_bytes()).hexdigest()
        old = previous.get(key, {})
        if not args.force and old.get('fingerprint') == fingerprint and destination.is_file():
            return key, {'fingerprint': fingerprint, 'pages': pages(destination)}
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='portfolio-cv-') as temp:
            output = Path(temp) / 'cv.pdf'
            command = [chrome, '--headless', '--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage', '--no-pdf-header-footer', f'--user-data-dir={Path(temp) / "profile"}', f'--print-to-pdf={output}', source.as_uri()]
            result = subprocess.run(command, capture_output=True, text=True, timeout=120)
            if result.returncode or not output.is_file():
                raise RuntimeError(f'{key}: Chrome render failed: {result.stderr[-1600:]}')
            count = pages(output)
            destination.write_bytes(output.read_bytes())
        print(f'Rendered {key}: {count} pages', flush=True)
        return key, {'fingerprint': fingerprint, 'pages': count}

    with ThreadPoolExecutor(max_workers=2) as pool:
        state = dict(pool.map(render_document, documents))
    STATE.write_text(json.dumps(state, indent=2, sort_keys=True) + '\n')
    print(f'Rendered or reused {len(documents)} CV PDFs. Run --check to enforce page limits.')


if __name__ == '__main__':
    main()
