"""Public-output checks for navigation, accessibility basics and content constraints.

Run after generating the site: python -m unittest discover -s tests -v
These checks do not require third-party packages, a browser or network access.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_links import audit_site, public_pages, read_document  # noqa: E402


CANONICAL_PROJECTS = {
    "carbon-storage-atlas",
    "coal-ash-modeling",
    "colombia-deforestation",
    "environmental-flows",
    "epa-emissions",
    "land-use-dynamics",
    "nasa-air-quality",
    "nasa-water-resources",
    "orphaned-wells",
    "predio-ai",
    "quito-urban-expansion",
    "raaz-borg",
    "texas-rrc-wellbore",
    "traffic-camera-pipeline",
    "yuyay-analytics",
}
CORE_PAGES = {"index.html", "projects.html", "research.html", "about.html", "contact.html", "cv.html"}

# Keep the private implementation out of visible links, embedded data and image
# sources. The live github.io application is deliberately not matched.
PREDIO_SOURCE_URL = re.compile(
    r"(?:github\.com|raw\.githubusercontent\.com|codeload\.github\.com)/"
    r"jayjayanton/predio-ai(?:\.git)?(?:[/?#\s\"'<>)]|$)"
    r"|api\.github\.com/repos/jayjayanton/predio-ai(?:\.git)?(?:[/?#\s\"'<>)]|$)",
    re.IGNORECASE,
)


class PublishedSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = {}
        for path in sorted((ROOT / "content" / "case-studies").glob("*.json")):
            cls.records[path.stem] = json.loads(path.read_text(encoding="utf-8"))

    def test_canonical_pages_and_project_records_are_preserved(self) -> None:
        missing_core = sorted(name for name in CORE_PAGES if not (ROOT / name).is_file())
        self.assertFalse(missing_core, f"Missing public pages: {missing_core}")
        missing_records = sorted(CANONICAL_PROJECTS - self.records.keys())
        self.assertFalse(missing_records, f"Missing canonical case-study records: {missing_records}")
        for slug in sorted(CANONICAL_PROJECTS):
            with self.subTest(project=slug):
                self.assertTrue((ROOT / "projects" / f"{slug}.html").is_file())
                self.assertEqual(self.records[slug].get("slug"), slug)

    def test_public_navigation_assets_and_page_semantics(self) -> None:
        errors = audit_site(ROOT)
        self.assertFalse(errors, "\n" + "\n".join(errors))

    def test_predio_source_is_not_published(self) -> None:
        paths = set(public_pages(ROOT))
        paths.update((ROOT / "content" / "case-studies").glob("*.json"))
        for directory in (ROOT / "assets", ROOT / "images"):
            paths.update(path for path in directory.rglob("*") if path.suffix.lower() in {".html", ".css", ".js", ".json", ".svg", ".txt"})
        violations = []
        for path in sorted(paths):
            text = unquote(html.unescape(path.read_text(encoding="utf-8"))).replace(r"\/", "/")
            if PREDIO_SOURCE_URL.search(text):
                violations.append(str(path.relative_to(ROOT)))
        self.assertFalse(violations, f"PredioAI implementation URLs must stay private: {violations}")

    def test_predio_role_preserves_sole_developer_attribution(self) -> None:
        self.assertIn("predio-ai", self.records)
        role = self.records["predio-ai"].get("role", "")
        self.assertRegex(role.casefold(), r"\bcreator\b")
        self.assertRegex(role.casefold(), r"\bsole\s+developer\b")
        published_text = read_document(ROOT / "projects" / "predio-ai.html").body_text
        self.assertRegex(published_text.casefold(), r"\bsole\s+developer\b")

    def test_yuyay_stays_in_web_category(self) -> None:
        self.assertIn("yuyay-analytics", self.records)
        self.assertEqual(set(self.records["yuyay-analytics"].get("categories", [])), {"web"})

    def test_quito_research_is_labeled_as_development(self) -> None:
        self.assertIn("quito-urban-expansion", self.records)
        self.assertEqual(self.records["quito-urban-expansion"].get("status_key"), "development")


if __name__ == "__main__":
    unittest.main()
