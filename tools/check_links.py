#!/usr/bin/env python3
"""Check the portfolio's public HTML and local references without network access.

Usage: python tools/check_links.py [site-root]
The checker is also imported by tests/test_site.py. It intentionally excludes
templates and content fragments, which are not complete published documents.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_PATH = "Website-Portfolio"


@dataclass(frozen=True)
class Reference:
    tag: str
    attribute: str
    value: str
    line: int


@dataclass
class Document:
    path: Path
    ids: Counter[str] = field(default_factory=Counter)
    named_anchors: set[str] = field(default_factory=set)
    references: list[Reference] = field(default_factory=list)
    missing_image_alts: list[int] = field(default_factory=list)
    main_count: int = 0
    h1_count: int = 0
    lang: str = ""
    title: str = ""
    description: str = ""
    body_text: str = ""


class DocumentParser(HTMLParser):
    """Collect semantic landmarks and URLs, including references inside SVGs."""

    def __init__(self, path: Path):
        super().__init__(convert_charrefs=True)
        self.document = Document(path=path)
        self._in_title = False
        self._in_head = False
        self._in_body = False
        self._noncontent_tag: str | None = None

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attrs = dict(attributes)
        line = self.getpos()[0]
        doc = self.document
        if "id" in attrs:
            doc.ids[attrs["id"] or ""] += 1
        if tag == "a" and attrs.get("name"):
            doc.named_anchors.add(attrs["name"])
        if tag == "html":
            doc.lang = (attrs.get("lang") or "").strip()
        elif tag == "head":
            self._in_head = True
        elif tag == "body":
            self._in_body = True
        elif tag == "main":
            doc.main_count += 1
        elif tag == "h1":
            doc.h1_count += 1
        elif tag == "title" and self._in_head:
            self._in_title = True
        elif tag == "meta" and self._in_head and (attrs.get("name") or "").lower() == "description":
            doc.description = (attrs.get("content") or "").strip()
        elif tag == "img" and "alt" not in attrs:
            # Empty alt is valid for a deliberately decorative image.
            doc.missing_image_alts.append(line)
        if tag in {"script", "style"}:
            self._noncontent_tag = tag

        for attribute in ("href", "src", "poster"):
            if attribute in attrs:
                doc.references.append(Reference(tag, attribute, attrs[attribute] or "", line))
        if attrs.get("srcset") and not attrs["srcset"].lstrip().startswith("data:"):
            for candidate in attrs["srcset"].split(","):
                parts = candidate.strip().split()
                if parts:
                    doc.references.append(Reference(tag, "srcset", parts[0], line))

    def handle_startendtag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attributes)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "head":
            self._in_head = False
        elif tag == "body":
            self._in_body = False
        if tag == self._noncontent_tag:
            self._noncontent_tag = None

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.document.title += data
        if self._in_body and self._noncontent_tag is None:
            self.document.body_text += data


def public_pages(root: Path) -> list[Path]:
    """Return complete public documents, never template/content HTML fragments."""
    return sorted([*root.glob("*.html"), *(root / "projects").glob("*.html")])


def read_document(path: Path) -> Document:
    parser = DocumentParser(path)
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    parser.document.title = parser.document.title.strip()
    return parser.document


def local_target(
    reference: str, source: Path, root: Path, base_path: str = DEFAULT_BASE_PATH
) -> tuple[Path, str] | None:
    """Resolve a relative/root-relative URL; external URLs require no network test."""
    url = urlsplit(reference.strip())
    if url.scheme or url.netloc:
        return None
    path = unquote(url.path)
    if not path:
        target = source
    elif path.startswith("/"):
        relative = path.lstrip("/")
        prefix = base_path.strip("/")
        if prefix and (relative == prefix or relative.startswith(prefix + "/")):
            relative = relative[len(prefix):].lstrip("/")
        target = root / relative
    else:
        target = source.parent / path
    target = target.resolve()
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(url.fragment)


def audit_site(root: Path, base_path: str = DEFAULT_BASE_PATH) -> list[str]:
    root = root.resolve()
    pages = public_pages(root)
    errors: list[str] = []
    if not pages:
        return [f"No public HTML pages found in {root}"]
    documents: dict[Path, Document] = {}
    for path in pages:
        try:
            documents[path.resolve()] = read_document(path)
        except (OSError, UnicodeError) as exc:
            errors.append(f"{path.relative_to(root)}: cannot read HTML: {exc}")

    for path, doc in list(documents.items()):
        label = str(path.relative_to(root))
        for name, count in doc.ids.items():
            if not name:
                errors.append(f"{label}: empty id attribute")
            elif count > 1:
                errors.append(f"{label}: duplicate id {name!r} ({count} occurrences)")
        if doc.main_count != 1:
            errors.append(f"{label}: expected one main landmark, found {doc.main_count}")
        if doc.h1_count != 1:
            errors.append(f"{label}: expected one h1, found {doc.h1_count}")
        for field_name in ("lang", "title", "description"):
            if not getattr(doc, field_name):
                errors.append(f"{label}: missing or empty {field_name}")
        for line in doc.missing_image_alts:
            errors.append(f"{label}:{line}: image is missing an alt attribute")

        for ref in doc.references:
            location = f"{label}:{ref.line} ({ref.tag} {ref.attribute})"
            if ref.attribute in {"src", "srcset", "poster"} and not ref.value.strip():
                errors.append(f"{location}: empty media or script URL")
                continue
            try:
                resolved = local_target(ref.value, path, root, base_path)
            except ValueError as exc:
                errors.append(f"{location}: invalid URL {ref.value!r}: {exc}")
                continue
            if resolved is None:
                continue
            target, fragment = resolved
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(f"{location}: local URL escapes site root: {ref.value!r}")
                continue
            if not target.is_file():
                errors.append(f"{location}: missing local target {ref.value!r}")
                continue
            if fragment and target.suffix.lower() in {".html", ".htm", ".svg"}:
                if target not in documents:
                    try:
                        documents[target] = read_document(target)
                    except (OSError, UnicodeError) as exc:
                        errors.append(f"{location}: cannot inspect {ref.value!r}: {exc}")
                        continue
                target_doc = documents[target]
                if fragment not in target_doc.ids and fragment not in target_doc.named_anchors:
                    errors.append(f"{location}: missing fragment in {ref.value!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--base-path", default=DEFAULT_BASE_PATH)
    args = parser.parse_args()
    errors = audit_site(args.root, args.base_path)
    if errors:
        for error in errors:
            print(error)
        print(f"\nFound {len(errors)} issue(s).")
        return 1
    print(f"Checked {len(public_pages(args.root))} public HTML pages: local links and page semantics passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
