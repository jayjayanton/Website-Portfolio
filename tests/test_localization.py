"""Bilingual user-flow contracts for the generated portfolio.

Run after tools/build.py. These tests inspect the published documents, rather
than accepting a renderer's own route list as proof that navigation works.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_links import public_pages
from localization import localize_body, validate_translation

CORE_PAGES = {"index.html", "projects.html", "research.html", "about.html", "contact.html", "cv.html"}
CATEGORIES = {"geospatial", "data-science", "engineering", "web", "vision"}
STAGES = {"published", "delivered", "development"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def normalized(value: str) -> str:
    return " ".join(value.split())


@dataclass
class Element:
    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)

    def select(self, tag=None, **attributes):
        matches = []
        if (tag is None or self.tag == tag) and all(
            value in (self.attrs.get(key) or "").split() if key == "class"
            else self.attrs.get(key) == value for key, value in attributes.items()
        ):
            matches.append(self)
        for child in self.children:
            if isinstance(child, Element):
                matches.extend(child.select(tag, **attributes))
        return matches

    def one(self, tag=None, **attributes):
        matches = self.select(tag, **attributes)
        if len(matches) != 1:
            raise AssertionError(f"Expected one {tag} {attributes}, found {len(matches)}")
        return matches[0]

    def text(self, include_scripts=False):
        if self.tag in {"script", "style"} and not include_scripts:
            return ""
        return normalized(" ".join(
            child.text(include_scripts) if isinstance(child, Element) else child
            for child in self.children
        ))


class PageParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Element("document")
        self.stack = [self.root]
        self.feed(source)
        self.close()

    def handle_starttag(self, tag, attributes):
        node = Element(tag, dict(attributes))
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attributes):
        self.stack[-1].children.append(Element(tag, dict(attributes)))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, value):
        self.stack[-1].children.append(value)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def site_target(href, source, base_url):
    """Resolve browser URLs independently, including absolute links used in PDFs."""
    base = urlsplit(base_url)
    target = urlsplit(urljoin(base_url + source, href))
    if target.netloc != base.netloc or not target.path.startswith(base.path):
        return None
    path = unquote(target.path[len(base.path):])
    return path or "index.html"


def page_language(path):
    if path.startswith("es/") or (path.startswith("cv/") and path.endswith("-es.html")):
        return "es"
    return "en"


def corresponding_pages(path, default_profile):
    logical = path.removeprefix("es/")
    if logical == "cv.html":
        return {language: f"cv/{default_profile}-{language}.html" for language in ("en", "es")}
    if logical.startswith("cv/"):
        profile = logical[3:].rsplit("-", 1)[0]
        return {language: f"cv/{profile}-{language}.html" for language in ("en", "es")}
    return {"en": logical, "es": "es/" + logical}


class BilingualPublishedSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site = read_json(ROOT / "content/site.json")
        cls.spanish_site = read_json(ROOT / "content/es/site.json")
        cls.base_url = cls.site["base_url"]
        cls.manifest = read_json(ROOT / "assets/cv/manifest.json")
        cls.records = {
            language: {path.stem: read_json(path) for path in directory.glob("*.json")}
            for language, directory in (
                ("en", ROOT / "content/case-studies"),
                ("es", ROOT / "content/es/case-studies"),
            )
        }
        english = CORE_PAGES | {f"projects/{slug}.html" for slug in cls.site["project_order"]}
        cls.expected_pages = english | {"es/" + path for path in english} | {
            document["page"] for document in cls.manifest["documents"]
        }
        cls.pages = {
            path: PageParser((ROOT / path).read_text(encoding="utf-8")).root
            for path in sorted(cls.expected_pages)
        }

    def test_all_54_public_pages_are_discoverable_and_in_the_sitemap(self):
        self.assertEqual(len(self.records["en"]), 15)
        self.assertEqual(set(self.records["es"]), set(self.records["en"]))
        self.assertEqual(len(self.expected_pages), 54)
        self.assertEqual({path.relative_to(ROOT).as_posix() for path in public_pages(ROOT)}, self.expected_pages)
        sitemap = ET.parse(ROOT / "sitemap.xml")
        urls = [item.text for item in sitemap.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(len(urls), 54)
        self.assertEqual(set(urls), {self.base_url + path for path in self.expected_pages})

    def test_header_language_switch_and_hreflang_keep_the_current_page_or_cv_focus(self):
        for path, page in self.pages.items():
            with self.subTest(page=path):
                language = page_language(path)
                self.assertEqual(page.one("html").attrs["lang"], language)
                expected = corresponding_pages(path, self.manifest["default_profile"])
                links = [node for node in page.select("a") if "data-site-language" in node.attrs]
                self.assertEqual(len(links), 2)
                self.assertEqual({node.attrs["data-site-language"] for node in links}, {"en", "es"})
                for node in links:
                    choice = node.attrs["data-site-language"]
                    self.assertEqual(site_target(node.attrs["href"], path, self.base_url), expected[choice])
                    self.assertEqual(node.attrs.get("lang"), choice)
                    self.assertEqual(node.attrs.get("hreflang"), choice)
                    self.assertEqual(node.attrs.get("aria-current") == "page", choice == language)
                    self.assertTrue(node.attrs.get("aria-label", "").strip())
                alternate = {node.attrs.get("hreflang"): node.attrs["href"] for node in page.select("link") if node.attrs.get("rel") == "alternate"}
                self.assertEqual(alternate, {
                    "en": self.base_url + expected["en"],
                    "es": self.base_url + expected["es"],
                    "x-default": self.base_url + expected["en"],
                })
                self.assertEqual(page.one("link", rel="canonical").attrs["href"], self.base_url + expected[language])

    def test_spanish_navigation_and_internal_links_never_drop_back_to_english(self):
        for path, page in self.pages.items():
            if page_language(path) != "es":
                continue
            with self.subTest(page=path):
                nav = page.one("nav", id="site-nav")
                nav_targets = {site_target(node.attrs["href"], path, self.base_url) for node in nav.select("a")}
                self.assertTrue({"es/projects.html", "es/research.html", "es/about.html", "es/contact.html"} <= nav_targets)
                self.assertEqual(site_target(page.one("a", **{"class": "brand"}).attrs["href"], path, self.base_url), "es/index.html")
                for node in page.one("body").select("a"):
                    target = site_target(node.attrs.get("href", ""), path, self.base_url)
                    if target is None or not target.endswith(".html"):
                        continue
                    self.assertIn(target, self.expected_pages, f"{path}: unknown internal destination {target}")
                    explicit_english = node.attrs.get("data-site-language") == "en" or node.attrs.get("data-cv-language") == "en"
                    self.assertEqual(page_language(target), "en" if explicit_english else "es", f"{path}: {node.attrs.get('href')} loses the selected language")

    def test_spanish_cv_portfolio_and_case_links_remain_absolute_for_pdf_readers(self):
        documents = [item for item in self.manifest["documents"] if item["language"] == "es"]
        self.assertEqual(len(documents), 6)
        project_links = []
        for item in documents:
            path = item["page"]
            article = self.pages[path].one("article", **{"data-cv-document": item["profile"]})
            links = [node for node in article.select("a") if site_target(node.attrs.get("href", ""), path, self.base_url)]
            with self.subTest(page=path):
                self.assertTrue(any(site_target(node.attrs["href"], path, self.base_url) == "es/index.html" for node in links))
                for node in links:
                    self.assertTrue(node.attrs["href"].startswith(self.base_url), "CV body links must work after PDF export")
                    target = site_target(node.attrs["href"], path, self.base_url)
                    self.assertEqual(page_language(target), "es")
                    if target.startswith("es/projects/"):
                        project_links.append(target)
        self.assertIn("es/projects/quito-urban-expansion.html", project_links)
        self.assertIn("es/projects/predio-ai.html", project_links)

    def test_shared_assets_resolve_from_root_spanish_nested_case_and_cv_pages(self):
        for path, page in self.pages.items():
            for node in page.select():
                attributes = [name for name in ("src", "poster") if name in node.attrs]
                if node.tag == "link" and node.attrs.get("rel") in {"icon", "stylesheet"}:
                    attributes.append("href")
                for attribute in attributes:
                    target = site_target(node.attrs[attribute], path, self.base_url)
                    if target is None:
                        continue
                    with self.subTest(page=path, asset=node.attrs[attribute]):
                        self.assertTrue((ROOT / target).is_file(), f"Unresolved shared asset: {target}")
                        self.assertFalse(target.startswith(("es/assets/", "es/images/", "cv/assets/", "cv/images/")))

    def test_translated_records_keep_structure_sources_metrics_and_filter_identifiers(self):
        protected = {"slug", "categories", "topics", "status_key", "kind", "src", "url", "related"}

        def compare(left, right, path):
            self.assertIs(type(right), type(left), path)
            if isinstance(left, dict):
                self.assertEqual(list(left), list(right), path)
                for key, value in left.items():
                    if key in protected:
                        self.assertEqual(value, right[key], path + "." + key)
                    compare(value, right[key], path + "." + key)
            elif isinstance(left, list):
                self.assertEqual(len(left), len(right), path)
                for index, (a, b) in enumerate(zip(left, right)):
                    compare(a, b, f"{path}[{index}]")
            elif isinstance(left, str):
                if left.strip():
                    self.assertTrue(right.strip(), path)
                # Preserve quantitative evidence even when the surrounding prose changes.
                self.assertEqual(Counter(re.findall(r"\d+(?:\.\d+)?", left)), Counter(re.findall(r"\d+(?:\.\d+)?", right)), path)
            else:
                self.assertEqual(left, right, path)

        for slug, original in self.records["en"].items():
            with self.subTest(project=slug):
                translated = self.records["es"][slug]
                compare(original, translated, slug)
                self.assertTrue(set(translated["categories"]) <= CATEGORIES)
                self.assertTrue(set(translated.get("topics", [])) <= {"vision"})
                self.assertIn(translated["status_key"], STAGES)
                for key in ("summary", "problem", "contribution", "outcome", "learning"):
                    self.assertNotEqual(normalized(original[key]), normalized(translated[key]), f"{slug}.{key}: English fallback")
                for key in ("approach", "evidence"):
                    for index, entry in enumerate(original[key]):
                        if entry.get("body", "").strip():
                            self.assertNotEqual(normalized(entry["body"]), normalized(translated[key][index]["body"]), f"{slug}.{key}[{index}]: English fallback")
                for a, b in zip(original["limitations"], translated["limitations"]):
                    self.assertNotEqual(normalized(a), normalized(b), slug + ".limitations: English fallback")
                image_pairs = [(original["image"], translated["image"])]
                for a, b in zip(original["evidence"], translated["evidence"]):
                    image_pairs.extend(zip(a["images"], b["images"]))
                for a, b in image_pairs:
                    for key in ("alt", "caption"):
                        if a.get(key):
                            self.assertNotEqual(normalized(a[key]), normalized(b[key]), f"{slug}: untranslated image {key}")
                for a, b in zip(original["links"], translated["links"]):
                    self.assertNotEqual(normalized(a["label"]), normalized(b["label"]), f"{slug}: untranslated source-link label")

    def test_every_spanish_case_renders_the_complete_translated_narrative(self):
        sections = {"problem": "problem", "contribution": "contribution", "outcome": "results", "learning": "progression"}
        for slug, record in self.records["es"].items():
            with self.subTest(project=slug):
                page = self.pages[f"es/projects/{slug}.html"]
                self.assertEqual(page.one("h1").text(), normalized(record["title"]))
                self.assertIn(normalized(record["summary"]), page.one("main").text())
                for key, section_id in sections.items():
                    self.assertIn(normalized(record[key]), page.one("section", id=section_id).text())
                for item in record["approach"]:
                    self.assertIn(normalized(item["body"]), page.one("section", id="approach").text())
                for item in record["limitations"]:
                    self.assertIn(normalized(item), page.one("section", id="results").text())
                for item in record["evidence"]:
                    self.assertIn(normalized(item["title"]), page.one("section", id="evidence").text())
                    if item.get("body"):
                        self.assertIn(normalized(item["body"]), page.one("section", id="evidence").text())
                hrefs = {node.attrs.get("href") for node in page.one("main").select("a")}
                self.assertTrue({item["url"] for item in record["links"]} <= hrefs, "Original source URLs must survive rendering")

    def test_spanish_visible_sections_do_not_reuse_english_ui_or_paragraphs(self):
        official_titles = [item["title"] for item in self.site["publications"]]
        allowed_shared = {"Jay Oliver", "Jay Antonio Oliver", "PredioAI", "Yuyay Analytics", "Ra’az Borg", "LinkedIn", "GitHub", "NASA DEVELOP", "English", "Español", *official_titles}
        for path, spanish in self.pages.items():
            if page_language(path) != "es":
                continue
            english_path = corresponding_pages(path, self.manifest["default_profile"])["en"]
            english = self.pages[english_path]
            spanish_main = spanish.one("main")
            translated_blocks = {node.text() for tag in ("h1", "h2", "h3", "h4", "label", "legend", "button", "option", "summary") for node in spanish_main.select(tag)}
            with self.subTest(page=path):
                for tag in ("h1", "h2", "h3", "h4", "label", "legend", "button", "option", "summary"):
                    for node in english.one("main").select(tag):
                        value = node.text()
                        if value and value not in allowed_shared:
                            self.assertNotIn(value, translated_blocks, f"Untranslated {tag}: {value}")
                for node in english.one("main").select("p"):
                    value = node.text()
                    if len(value.split()) < 10 or not re.search(r"\b(the|with|from|this|that|through|these)\b", value, re.I):
                        continue
                    if any(title in value for title in official_titles):
                        continue
                    self.assertNotIn(value, spanish_main.text(), f"Untranslated paragraph: {value}")

    def test_filter_controls_and_project_index_use_the_same_machine_values_in_both_languages(self):
        for language, path in (("en", "projects.html"), ("es", "es/projects.html")):
            with self.subTest(language=language):
                page = self.pages[path]
                form = page.one("form", id="project-filters")
                self.assertIn("hidden", form.attrs, "Progressive controls should appear only after successful JS setup")
                self.assertEqual(form.one("input", id="project-search").attrs["name"], "q")
                stage = form.one("select", id="project-stage")
                self.assertEqual(stage.attrs["name"], "stage")
                self.assertEqual({option.attrs["value"] for option in stage.select("option")}, {"all", *STAGES})
                self.assertEqual({node.attrs["data-category"] for node in form.select("button") if "data-category" in node.attrs}, {"all", *CATEGORIES})
                index = json.loads(page.one("script", id="project-index").text(include_scripts=True))
                cards = page.select("article", **{"class": "project-card"})
                self.assertEqual([card.attrs["data-project-slug"] for card in cards], self.site["project_order"])
                self.assertEqual([item["slug"] for item in index], self.site["project_order"])
                for card in cards:
                    self.assertNotIn("hidden", card.attrs, "Every project must remain accessible without JavaScript")
                for item in index:
                    record = self.records[language][item["slug"]]
                    for key in ("title", "summary", "categories", "status_key", "role", "context", "technologies"):
                        self.assertEqual(item[key], record[key], f"{language}/{item['slug']}/{key}")
                    self.assertEqual(item["topics"], record.get("topics", []))

    def test_site_translation_preserves_identity_and_official_publications(self):
        self.assertEqual(list(self.site), list(self.spanish_site))
        for key in ("name", "full_name", "base_url", "year", "email", "phone", "phone_url", "linkedin", "github", "cv", "master_cv", "featured", "project_order"):
            self.assertEqual(self.site[key], self.spanish_site[key], key)
        self.assertEqual(set(self.site["categories"]), set(self.spanish_site["categories"]))
        for key in self.site["categories"]:
            self.assertNotEqual(self.site["categories"][key], self.spanish_site["categories"][key])
        for original, spanish in zip(self.site["publications"], self.spanish_site["publications"]):
            for key in ("slug", "title", "journal", "year", "url", "doi"):
                self.assertEqual(original[key], spanish[key], key)
            for key in ("role", "description"):
                self.assertNotEqual(original[key], spanish[key], key)


class LocalizationURLContracts(unittest.TestCase):
    BASE = "https://jayjayanton.github.io/Website-Portfolio/"

    def links_after(self, markup, source="projects/example.html", destination="es/projects/example.html", language="es"):
        page = PageParser(localize_body(markup, source, destination, language, self.BASE)).root
        return {node.attrs["id"]: node.attrs for node in page.select() if "id" in node.attrs}

    def test_nested_assets_and_filter_query_keep_their_meaning(self):
        links = self.links_after(
            '<img id="image" src="../images/a%20plot.png">'
            '<script id="script" src="../assets/js/projects.js?v=123"></script>'
            '<video id="video" poster="/Website-Portfolio/images/preview.jpg"></video>'
            '<a id="filter" href="../projects.html?q=agua%20y%20suelo&amp;category=geospatial#project-grid">Filter</a>'
        )
        self.assertEqual(links["image"]["src"], "../../images/a%20plot.png")
        self.assertEqual(links["script"]["src"], "../../assets/js/projects.js?v=123")
        self.assertEqual(links["video"]["poster"], "../../images/preview.jpg")
        self.assertEqual(links["filter"]["href"], "../projects.html?q=agua%20y%20suelo&category=geospatial#project-grid")

    def test_explicit_cv_language_choices_and_shared_pdf_are_not_reinterpreted(self):
        links = self.links_after(
            '<a id="english" href="cv/master-en.html">English</a>'
            '<a id="spanish" href="cv/master-es.html">Español</a>'
            '<a id="pdf" href="assets/Jay_Antonio_Oliver_CV.pdf">PDF</a>',
            source="cv.html", destination="es/cv.html",
        )
        self.assertEqual(links["english"]["href"], "../cv/master-en.html")
        self.assertEqual(links["spanish"]["href"], "../cv/master-es.html")
        self.assertEqual(links["pdf"]["href"], "../assets/Jay_Antonio_Oliver_CV.pdf")

    def test_absolute_portfolio_links_stay_absolute_and_external_provenance_stays_intact(self):
        urls = {
            "home": self.BASE,
            "project": self.BASE + "projects/predio-ai.html#contribution",
            "already_spanish": self.BASE + "es/about.html",
            "cv": self.BASE + "cv/master-en.html",
            "pdf": self.BASE + "assets/Jay_Antonio_Oliver_CV.pdf",
            "product": "https://jayjayanton.github.io/Predio-AI/",
            "source": "https://raw.githubusercontent.com/jayjayanton/NASA-Projects/main/figures/example.png",
        }
        links = self.links_after("".join(f'<a id="{key}" href="{value}">Link</a>' for key, value in urls.items()))
        self.assertEqual(links["home"]["href"], self.BASE + "es/index.html")
        self.assertEqual(links["project"]["href"], self.BASE + "es/projects/predio-ai.html#contribution")
        for key in ("already_spanish", "cv", "pdf", "product", "source"):
            self.assertEqual(links[key]["href"], urls[key])

    def test_fragments_contact_links_and_embedded_data_do_not_become_site_routes(self):
        values = {"anchor": "#contribution", "email": "mailto:jayjayoliver@hotmail.com", "phone": "tel:+15404069434", "data": "data:image/png;base64,AAAA"}
        links = self.links_after("".join(f'<a id="{key}" href="{value}">Link</a>' for key, value in values.items()))
        for key, value in values.items():
            self.assertEqual(links[key]["href"], value)

    def test_validation_allows_localized_category_labels_but_rejects_changed_filters_or_sources(self):
        validate_translation({"categories": {"web": "Web applications"}}, {"categories": {"web": "Aplicaciones web"}})
        for original, translated in (
            ({"categories": ["web"]}, {"categories": ["sitios-web"]}),
            ({"topics": ["vision"]}, {"topics": ["visión"]}),
            ({"url": "https://example.org/source"}, {"url": "https://example.org/other"}),
            ({"src": "images/research.png"}, {"src": "images/replacement.png"}),
            ({"summary": "Research contribution"}, {"summary": ""}),
        ):
            with self.subTest(original=original):
                with self.assertRaises(ValueError):
                    validate_translation(original, translated)


if __name__ == "__main__":
    unittest.main()
