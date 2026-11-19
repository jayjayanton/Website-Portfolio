#!/usr/bin/env python3
"""Generate the public portfolio from canonical records and shared templates.

Uses the Python standard library only. Generated HTML stays in the repository
root so GitHub Pages can continue publishing the main branch without a build
service. Run with --check to detect stale output without changing files.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from string import Template
from urllib.parse import quote, urlsplit
from cv_collection import CVCollection, LANGUAGES
from localization import localized_path, relative_url, localize_body, validate_translation


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
CATEGORY_SHORT = {
    "geospatial": "Geospatial analysis",
    "data-science": "Data science",
    "engineering": "Data engineering",
    "web": "Web development",
    "vision": "Computer vision",
}
IMAGE_KINDS = {
    "research": "Research figure",
    "illustration": "Conceptual illustration",
    "screenshot": "Application screenshot",
    "satellite-imagery": "Satellite imagery",
    "camera-image": "Source camera image",
    "workflow-diagram": "Workflow illustration",
    "site-asset": "Website visual",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def render(name: str, template_language: str = "en", **values: object) -> str:
    path = TEMPLATES / ("es/" + name if template_language == "es" and name != "base.html" else name)
    return Template(path.read_text(encoding="utf-8")).substitute(values)


def asset_version(*paths: str) -> str:
    content = b"".join((ROOT / path).read_bytes() for path in paths)
    return hashlib.sha256(content).hexdigest()[:10]


def local_url(value: str, prefix: str = "") -> str:
    """Resolve repository-relative assets for both root and project pages."""
    if urlsplit(value).scheme or value.startswith(("//", "#")):
        return value
    return prefix + quote(value.lstrip("/"), safe="/%?#=&+:")


def link(label: str, url: str, class_name: str = "text-link", prefix: str = "") -> str:
    target = ' target="_blank" rel="noopener noreferrer"' if url.startswith("https://") else ""
    return f'<a class="{esc(class_name)}" href="{esc(local_url(url, prefix))}"{target}>{esc(label)}</a>'


class Site:
    def __init__(self, language: str = "en") -> None:
        if language not in LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        self.language = language
        source = CONTENT / ("es" if language == "es" else "")
        self.data = read_json(source / "site.json")
        self.images = read_json(CONTENT / "image-dimensions.json")
        self.records = {p.stem: read_json(p) for p in sorted((source / "case-studies").glob("*.json"))}
        self.order = self.data["project_order"]
        self.cvs = CVCollection(self.data)
        self.validate()
        self.css_version = asset_version("assets/css/site.css")
        self.js_version = asset_version("assets/js/site.js", "assets/js/navigation.mjs")
        self.projects_version = asset_version("assets/js/projects.js", "assets/js/filtering.mjs")

    def t(self, english: str, spanish: str) -> str:
        return spanish if self.language == "es" else english

    def template(self, name: str, **values: object) -> str:
        return render(name, template_language=self.language, **values)

    def category(self, key: str) -> str:
        return {"geospatial": "Análisis geoespacial", "data-science": "Ciencia de datos", "engineering": "Ingeniería de datos", "web": "Desarrollo web", "vision": "Visión por computadora"}[key] if self.language == "es" else CATEGORY_SHORT[key]

    def validate(self) -> None:
        if self.language == "es":
            validate_translation(read_json(CONTENT / "site.json"), self.data, "site")
        if len(self.order) != len(set(self.order)) or set(self.order) != set(self.records):
            raise ValueError("Project order must contain every canonical case study exactly once")
        required = {"slug", "title", "summary", "categories", "status", "status_key", "role", "context", "image", "technologies", "problem", "contribution", "approach", "outcome", "learning", "limitations", "evidence", "links", "related"}
        for slug, case in self.records.items():
            if self.language == "es":
                validate_translation(read_json(CONTENT / "case-studies" / f"{slug}.json"), case, slug)
            missing = required - case.keys()
            if missing:
                raise ValueError(f"{slug}: missing fields: {', '.join(sorted(missing))}")
            if case["slug"] != slug or not re.fullmatch(r"[a-z0-9-]+", slug):
                raise ValueError(f"Invalid case slug: {slug}")
            if not case["categories"] or set(case["categories"]) - CATEGORY_SHORT.keys():
                raise ValueError(f"{slug}: invalid categories")
            if case["status_key"] not in {"published", "delivered", "development"}:
                raise ValueError(f"{slug}: invalid work stage")
            if set(case["related"]) - self.records.keys():
                raise ValueError(f"{slug}: related case does not exist")
            for item in case["links"]:
                if not item["url"].startswith("https://"):
                    raise ValueError(f"{slug}: source links must use HTTPS")
            for group in case["evidence"]:
                table = group.get("table")
                if table and any(len(row) != len(table["headers"]) for row in table["rows"]):
                    raise ValueError(f"{slug}: inconsistent evidence table")

    def image(self, record: dict, prefix: str = "", class_name: str = "", eager: bool = False) -> str:
        source = record["src"]
        dimensions = self.images.get(source.lstrip("/"))
        size = f' width="{dimensions[0]}" height="{dimensions[1]}"' if dimensions else ""
        loading = ' fetchpriority="high"' if eager else ' loading="lazy"'
        return f'<img class="{esc(class_name)}" src="{esc(local_url(source, prefix))}" alt="{esc(record["alt"])}"{size}{loading} decoding="async">'

    def figure(self, record: dict, prefix: str, cover: bool = False) -> str:
        kinds = {"research": "Figura de investigación", "illustration": "Ilustración conceptual", "screenshot": "Captura de la aplicación", "satellite-imagery": "Imagen satelital", "camera-image": "Imagen de la cámara de origen", "workflow-diagram": "Diagrama del proceso", "site-asset": "Recurso visual del sitio"} if self.language == "es" else IMAGE_KINDS
        kind = kinds.get(record.get("kind"), self.t("Project evidence", "Evidencia del proyecto"))
        class_name = "case-cover" if cover else "evidence-figure"
        return (f'<figure class="{class_name} image-kind-{esc(record.get("kind", "research"))}">'
                f'<a class="figure-image" href="{esc(local_url(record["src"], prefix))}" target="_blank" rel="noopener noreferrer" aria-label="{esc(self.t("Open full-size image: ", "Abrir imagen a tamaño completo: ") + record["alt"])}">'
                f'{self.image(record, prefix, eager=cover)}</a>'
                f'<figcaption><span class="figure-kind">{esc(kind)}</span> {esc(record.get("caption", ""))}</figcaption></figure>')

    def card(self, slug: str, prefix: str = "") -> str:
        case = self.records[slug]
        url = prefix + f"projects/{slug}.html"
        title = esc(case["title"])
        tech = "".join(f"<li>{esc(item)}</li>" for item in case["technologies"][:3])
        category = self.category(case["categories"][0])
        secondary = ""
        live = next((item for item in case["links"] if item["kind"] == "live"), None)
        if live:
            secondary = link(self.t("Visit website", "Visitar el sitio"), live["url"], "project-live-link")
        return (f'<article class="project-card" data-project-slug="{esc(slug)}">'
                f'<a class="project-image-link image-kind-{esc(case["image"].get("kind", "research"))}" href="{url}" tabindex="-1" aria-hidden="true">{self.image(case["image"], prefix, "project-image")}</a>'
                f'<div class="project-card-body"><div class="project-meta"><span>{esc(category)}</span><span class="status status-{esc(case["status_key"])}">{esc(case["status"])}</span></div>'
                f'<h3><a href="{url}">{title}</a></h3><p class="project-role">{esc(case["role"])}</p><p class="project-summary">{esc(case["summary"])}</p>'
                f'<ul class="technology-list" aria-label="{self.t("Selected tools and methods", "Herramientas y métodos seleccionados")}">{tech}</ul>'
                f'<div class="project-card-links"><a class="text-link" href="{url}" aria-label="{esc(self.t("Read case study: ", "Leer caso de estudio: ") + case["title"])}">{self.t("Read case study", "Leer caso de estudio")}<span aria-hidden="true"> →</span></a>{secondary}</div></div></article>')

    def contact_band(self, prefix: str = "") -> str:
        return (f'<section class="container contact-band"><div><p class="eyebrow">{self.t("Let’s connect", "Conversemos")}</p><h2>{self.t("Have a data or geospatial problem in mind?", "¿Tienes un reto de datos o análisis geoespacial?")}</h2>'
                f'<p>{self.t("I’m interested in work that connects analytical depth with useful implementation.", "Me interesan los proyectos que conectan el análisis riguroso con aplicaciones útiles.")}</p></div>'
                f'{link(self.t("Start a conversation", "Conversemos"), "contact.html", "button", prefix)}</section>')

    def progression(self) -> str:
        return "".join(
            f'<article class="progression-card"><span class="progression-number" aria-hidden="true">0{i}</span><p class="eyebrow">{esc(item["label"])}</p>'
            f'<h3>{esc(item["title"])}</h3><p>{esc(item["body"])}</p>{link(item["link_label"], item["link"])}</article>'
            for i, item in enumerate(self.data["progression"], 1)
        )

    def page(self, file_name: str, title: str, description: str, body: str, active: str = "", og_image: str = "images/predioai-homepage.jpg", language: str | None = None, extra_head: str = "", canonical_path: str | None = None, language_paths: dict | None = None) -> str:
        language = language or self.language
        destination = localized_path(file_name, language)
        prefix = "../" * (len(Path(destination).parts) - 1)
        paths = language_paths or {lang: localized_path(file_name, lang) for lang in LANGUAGES}
        alternatives = "\n".join(f'<link rel="alternate" hreflang="{lang}" href="{self.data["base_url"]}{paths[lang]}">' for lang in LANGUAGES)
        alternatives += f'\n<link rel="alternate" hreflang="x-default" href="{self.data["base_url"]}{paths["en"]}">'
        language_links = ''.join(f'<a href="{relative_url(paths[lang], destination)}" lang="{lang}" hreflang="{lang}" data-site-language="{lang}" aria-label="{"English" if lang == "en" else "Español"}"' + (' aria-current="page"' if lang == language else '') + f'><span class="language-full">{"English" if lang == "en" else "Español"}</span><span class="language-short" aria-hidden="true">{lang.upper()}</span></a>' for lang in LANGUAGES)
        ui = ({"skip": "Saltar al contenido", "home": "Inicio de Jay Oliver", "brand": "Ciencia de datos y desarrollo geoespacial", "menu": "Menú", "close": "Cerrar", "nav": "Navegación principal", "cv": "Elegir CV", "footer": "Ciencia de datos, análisis geoespacial y software útil.", "email": "Correo", "code": "Código público", "contact": "Contacto"} if language == "es" else
              {"skip": "Skip to content", "home": "Jay Oliver home", "brand": "Data science & geospatial development", "menu": "Menu", "close": "Close", "nav": "Main navigation", "cv": "Choose CV", "footer": "Data science, geospatial analysis & useful software.", "email": "Email", "code": "Public code", "contact": "Contact"})
        labels = ("Proyectos", "Investigación", "Perfil", "Contacto") if language == "es" else ("Work", "Research", "About", "Contact")
        navigation = "".join(
            f'<a href="{relative_url(localized_path(path, language), destination)}"' + (' aria-current="page"' if key == active else "") + f'>{label}</a>'
            for (key, path), label in zip((("work", "projects.html"), ("research", "research.html"), ("about", "about.html"), ("contact", "contact.html")), labels)
        )
        return render("base.html", title=esc(title), description=esc(description),
                      canonical=esc(self.data["base_url"] + (canonical_path or destination)),
                      og_image=esc(og_image if og_image.startswith("https://") else self.data["base_url"] + quote(og_image.lstrip("/"), safe="/")),
                      prefix=prefix, css_version=self.css_version, js_version=self.js_version,
                      extra_head=alternatives + "\n" + extra_head, body_class="page-" + ("case" if file_name.startswith("projects/") else "cv" if file_name.startswith("cv/") else Path(file_name).stem),
                      language=language, cv_current=' aria-current="page"' if active == "cv" else "",
                      cv_href="#cv-chooser" if active == "cv" else relative_url(localized_path("cv.html", language), destination),
                      home_href=relative_url(localized_path("index.html", language), destination),
                      contact_href=relative_url(localized_path("contact.html", language), destination),
                      language_links=language_links, language_label="Idioma del sitio" if language == "es" else "Site language",
                      navigation=navigation, body=localize_body(body, file_name, destination, language, self.data["base_url"]), **{f"ui_{key}": esc(value) for key, value in ui.items()})

    def homepage(self) -> str:
        capability_data = [
            ("geospatial", "Geospatial & Earth observation", "Make spatial data comparable, combine satellite observations and connect analysis to geographic context.", "Land-use basemaps · NASA studies · PredioAI"),
            ("data-science", "Data science & modeling", "Build and interpret models around the question, the available evidence and the limits of the data.", "Orphaned wells · Coal ash · Environmental flows"),
            ("engineering", "Data engineering", "Turn fragmented files and services into repeatable processing and usable analytical datasets.", "Texas well records · EPA emissions · Carbon atlas"),
            ("web", "Applications & APIs", "Bring data and methods into working interfaces, from a public website to interactive geospatial software.", "PredioAI · Yuyay Analytics · Web development"),
        ]
        if self.language == "es":
            capability_data = [
                ("geospatial", "Análisis geoespacial y observación de la Tierra", "Hacer comparables los datos espaciales, combinar observaciones satelitales y conectar el análisis con su contexto geográfico.", "Mapas base de uso del suelo · Estudios de NASA · PredioAI"),
                ("data-science", "Ciencia de datos y modelación", "Construir e interpretar modelos según la pregunta, la evidencia disponible y los límites de los datos.", "Pozos huérfanos · Cenizas de carbón · Caudales ecológicos"),
                ("engineering", "Ingeniería de datos", "Convertir archivos y servicios dispersos en procesos reproducibles y conjuntos de datos listos para el análisis.", "Registros de pozos de Texas · Emisiones de la EPA · Atlas de almacenamiento de carbono"),
                ("web", "Aplicaciones y APIs", "Llevar los datos y métodos a interfaces funcionales, desde sitios públicos hasta aplicaciones geoespaciales interactivas.", "PredioAI · Yuyay Analytics · Desarrollo web"),
            ]
        capabilities = "".join(
            f'<a class="capability-card" href="projects.html?category={key}"><span class="capability-number" aria-hidden="true">0{i}</span><h3>{esc(title)}</h3><p>{esc(body)}</p><small>{esc(examples)}</small><span class="text-link">{self.t("Explore the work", "Explorar los proyectos")} <span aria-hidden="true">→</span></span></a>'
            for i, (key, title, body, examples) in enumerate(capability_data, 1)
        )
        body = self.template("home.html", project_count=len(self.records), featured_cards="".join(self.card(slug) for slug in self.data["featured"]), capabilities=capabilities, progression=self.progression(), contact_band=self.contact_band())
        return self.page("index.html", self.t("Jay Oliver | Data Science, Geospatial Analysis & Software", "Jay Oliver | Ciencia de datos, análisis geoespacial y software"), self.t("Jay Oliver’s portfolio: applied data science, geospatial research, reproducible data pipelines and independently developed software. Explore the work and the evidence.", "Portafolio de Jay Oliver: ciencia de datos aplicada, investigación geoespacial, procesos reproducibles y desarrollo independiente de software. Conoce los proyectos y su evidencia."), body)

    def projects(self) -> str:
        index = []
        for slug in self.order:
            case = self.records[slug]
            capabilities = dict.fromkeys([*case["categories"], *case.get("topics", [])])
            index.append({**{key: case.get(key, []) for key in ("slug", "title", "summary", "categories", "topics", "status", "status_key", "role", "context", "technologies")}, "category_labels": [self.data["categories"][key] for key in capabilities], "search_aliases": self.search_aliases(slug)})
        serialized = json.dumps(index, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        buttons = "".join(f'<button type="button" data-category="{key}" aria-pressed="false">{esc(label)}</button>' for key, label in self.data["categories"].items())
        body = self.template("projects.html", project_count=len(self.records), category_buttons=buttons, cards="".join(self.card(slug) for slug in self.order), project_index=serialized, projects_version=self.projects_version, contact_band=self.contact_band())
        return self.page("projects.html", self.t("Work & Case Studies | Jay Oliver", "Proyectos y casos de estudio | Jay Oliver"), self.t("Explore Jay Oliver’s data science, geospatial, data engineering and web development projects. Filter by capability, tools and work stage.", "Explora los proyectos de ciencia de datos, análisis geoespacial, ingeniería de datos y desarrollo web de Jay Oliver. Filtra por especialidad, herramientas y etapa."), body, "work")

    def search_aliases(self, slug: str) -> list[str]:
        # Both languages remain searchable when a query is carried across the switch.
        other = CONTENT / ("" if self.language == "es" else "es") / "case-studies" / f"{slug}.json"
        record = read_json(other)
        labels = read_json(other.parent.parent / "site.json")["categories"]
        capabilities = dict.fromkeys([*record['categories'], *record.get('topics', [])])
        return [record.get(key, '') for key in ("title", "summary", "role", "context", "status")] + record['technologies'] + [labels[key] for key in capabilities]

    def table(self, value: dict, caption: str) -> str:
        headers = "".join(f'<th scope="col">{esc(item)}</th>' for item in value["headers"])
        rows = "".join("<tr>" + "".join(f'<th scope="row">{esc(cell)}</th>' if i == 0 else f'<td>{esc(cell)}</td>' for i, cell in enumerate(row)) + "</tr>" for row in value["rows"])
        return f'<div class="table-scroll" tabindex="0" role="region" aria-label="{esc(caption)}"><table><caption>{esc(caption)}</caption><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>'

    def evidence(self, case: dict) -> str:
        groups = []
        for i, group in enumerate(case["evidence"]):
            group_images = group.get("images", [])
            # Preserve side-by-side comparisons even when one image is the cover.
            images = "".join(self.figure(item, "../") for item in group_images if len(group_images) > 1 or item["src"].lstrip("/") != case["image"]["src"].lstrip("/"))
            gallery = f'<div class="evidence-gallery">{images}</div>' if images else ""
            table = self.table(group["table"], group["title"]) if group.get("table") else ""
            open_attr = " open" if i == 0 else ""
            groups.append(f'<details class="evidence-group"{open_attr}><summary>{esc(group["title"])}</summary><div class="evidence-group-body"><p>{esc(group.get("body", ""))}</p>{table}{gallery}</div></details>')
        help_text = self.t("Expand a section to see methods, figures or detailed results. Select any figure to view it at full size.", "Despliega una sección para consultar métodos, figuras o resultados detallados. Selecciona una figura para verla a tamaño completo. Las figuras y capturas originales se acompañan de explicaciones en español.")
        return f'<p class="evidence-help">{help_text}</p>' + "".join(groups)

    def case(self, slug: str) -> str:
        case = self.records[slug]
        primary_link = next((item for kind in ("live", "publication", "report", "code") for item in case["links"] if item["kind"] == kind), None)
        actions = link(primary_link["label"], primary_link["url"], "button") if primary_link else ""
        actions += f'<a class="button button-secondary" href="#contribution">{self.t("My contribution", "Mi contribución")}</a>'
        period = f'<div><dt>{self.t("When", "Período")}</dt><dd>{esc(case["period"])}</dd></div>' if case.get("period") else ""
        approach = "".join(f'<article class="approach-step"><span aria-hidden="true">{i:02d}</span><div><h3>{esc(item["title"])}</h3><p>{esc(item["body"])}</p></div></article>' for i, item in enumerate(case["approach"], 1))
        limitations = f'<div class="scope-note"><h3>{self.t("Scope &amp; next steps", "Alcance y próximos pasos")}</h3><ul>' + "".join(f'<li>{esc(item)}</li>' for item in case["limitations"]) + "</ul></div>" if case["limitations"] else ""
        sources = f'<h3>{self.t("Sources &amp; further reading", "Fuentes y lecturas adicionales")}</h3><ul>' + "".join("<li>" + link(item["label"], item["url"]) + "</li>" for item in case["links"]) + "</ul>" if case["links"] else ""
        body = self.template("case-study.html", category_label=esc(" · ".join(self.category(key) for key in case["categories"])), status_key=case["status_key"], status=esc(case["status"]), project_title=esc(case["title"]), summary=esc(case["summary"]), project_actions=actions, role=esc(case["role"]), context=esc(case["context"]), period_fact=period,
                      technologies="".join(f'<span>{esc(item)}</span>' for item in case["technologies"]),
                      cover=self.figure(case["image"], "../", True), problem=esc(case["problem"]), contribution=esc(case["contribution"]), approach=approach,
                      result_heading=self.t("What works now, and what comes next.", "Lo que ya funciona y lo que sigue.") if case["status_key"] == "development" else self.t("What the work delivered.", "Los resultados del trabajo."),
                      outcome=esc(case["outcome"]), limitations=limitations, learning=esc(case["learning"]), evidence=self.evidence(case), source_links=sources,
                      related_cards="".join(self.card(other, "../") for other in case["related"][:3]), contact_band=self.contact_band("../"))
        return self.page(f"projects/{slug}.html", f'{case["title"]} | Jay Oliver', case["summary"], body, "work", case["image"]["src"])

    def about(self) -> str:
        groups = [
            ("Data science", "Python, pandas, NumPy, scikit-learn, XGBoost, model evaluation and SHAP.", "orphaned-wells", "See the modeling workflow"),
            ("Geospatial analysis", "ArcGIS Pro, QGIS, raster and vector processing, satellite imagery, spatial joins and coordinate transformations.", "land-use-dynamics", "See the published basemaps"),
            ("Data engineering", "Python processing, SQL, REST APIs, fixed-width extraction, validation and repeatable exports.", "texas-rrc-wellbore", "See the wellbore pipeline"),
            ("Application development", "React, FastAPI, Leaflet, API integration, document geometry and web deployment.", "predio-ai", "See the independent product"),
        ]
        if self.language == "es":
            groups = [
                ("Ciencia de datos", "Python, pandas, NumPy, scikit-learn, XGBoost, evaluación de modelos y SHAP.", "orphaned-wells", "Ver el proceso de modelación"),
                ("Análisis geoespacial", "ArcGIS Pro, QGIS, procesamiento ráster y vectorial, imágenes satelitales, uniones espaciales y transformaciones de coordenadas.", "land-use-dynamics", "Ver los mapas base publicados"),
                ("Ingeniería de datos", "Procesamiento con Python, SQL, APIs REST, extracción de archivos de ancho fijo, validación y exportaciones reproducibles.", "texas-rrc-wellbore", "Ver el procesamiento de registros de pozos"),
                ("Desarrollo de aplicaciones", "React, FastAPI, Leaflet, integración de APIs, geometría de documentos y publicación web.", "predio-ai", "Ver el producto independiente"),
            ]
        tools = '<div class="tool-grid">' + "".join(f'<article class="tool-group"><h3>{esc(title)}</h3><p>{esc(body)}</p>{link(label, f"projects/{slug}.html")}</article>' for title, body, slug, label in groups) + "</div>"
        body = self.template("about.html", progression=self.progression(), tool_groups=tools, contact_band=self.contact_band())
        return self.page("about.html", self.t("About & Approach | Jay Oliver", "Perfil y enfoque de trabajo | Jay Oliver"), self.t("An environmental research foundation and an expanding technical practice. Learn how Jay Oliver connects data science, geospatial analysis and application development.", "Una base en investigación ambiental y una práctica técnica en expansión. Conoce cómo Jay Oliver conecta ciencia de datos, análisis geoespacial y desarrollo de aplicaciones."), body, "about")

    def research(self) -> str:
        publications = []
        for publication in self.data["publications"]:
            case = self.records[publication["slug"]]
            publications.append(f'<article class="publication-card"><div class="publication-image">{self.image(case["image"])}</div><div class="publication-body"><div class="publication-meta"><span>{esc(publication["year"])}</span><span>{esc(publication["role"])}</span></div><p class="eyebrow">{esc(publication["journal"])}</p><h3 lang="en">{esc(publication["title"])}</h3><p>{esc(publication["description"])}</p><p class="publication-doi">DOI: {esc(publication["doi"])}</p><div class="actions">{link(self.t("Read the publication", "Leer la publicación"), publication["url"], "button button-secondary")}{link(self.t("My contribution & methods", "Mi contribución y metodología"), "projects/" + publication["slug"] + ".html")}</div></div></article>')
        body = self.template("research.html", publications="".join(publications), nasa_cards=self.card("nasa-air-quality") + self.card("nasa-water-resources"), contact_band=self.contact_band())
        return self.page("research.html", self.t("Research & Publications | Jay Oliver", "Investigación y publicaciones | Jay Oliver"), self.t("First-author Scientific Data research, coauthored environmental-flows research, NASA DEVELOP studies and ongoing remote-sensing work by Jay Oliver.", "Investigaciones de Jay Oliver como primer autor en Scientific Data y coautor en caudales ecológicos, estudios de NASA DEVELOP y proyectos de teledetección en desarrollo."), body, "research")

    def cv(self, profile: str | None = None, language: str = "en", file_name: str = "cv.html") -> str:
        profile = profile or self.cvs.default
        prefix = "../" if file_name.startswith("cv/") else ""
        body = self.cvs.controls(profile, language, prefix) + self.cvs.article(profile, language)
        title = f'{self.cvs.label(profile, language)} · {"Español" if language == "es" else "English"} | Jay Antonio Oliver'
        return self.page(file_name, title, self.cvs.description(profile, language), body, "cv", language=language, canonical_path=self.cvs.page_path(profile, language), language_paths={lang: self.cvs.page_path(profile, lang) for lang in LANGUAGES})

    def page_outputs(self) -> dict[str, str]:
        pages = {
            "index.html": self.homepage(), "projects.html": self.projects(),
            "about.html": self.about(), "research.html": self.research(),
            "contact.html": self.page("contact.html", self.t("Contact | Jay Oliver", "Contacto | Jay Oliver"), self.t("Contact Jay Oliver about data science, geospatial analytics, research and application development. Email, professional profiles and CV.", "Contacta a Jay Oliver para oportunidades en ciencia de datos, análisis geoespacial, investigación y desarrollo de aplicaciones. Correo, perfiles profesionales y CV."), self.template("contact.html"), "contact"),
            "cv.html": self.cv(language=self.language),
        }
        pages.update({f"projects/{slug}.html": self.case(slug) for slug in self.order})
        return {localized_path(path, self.language): value for path, value in pages.items()}

    def outputs(self) -> dict[str, str]:
        pages = {}
        for language in LANGUAGES:
            variant = self if self.language == language else Site(language)
            pages.update(variant.page_outputs())
        pages.update({self.cvs.page_path(profile, language): self.cv(profile, language, self.cvs.page_path(profile, language)) for profile in self.cvs.order for language in LANGUAGES})
        sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f'  <url><loc>{esc(self.data["base_url"] + path)}</loc></url>\n' for path in pages) + "</urlset>\n"
        return {**pages, "sitemap.xml": sitemap, "assets/cv/manifest.json": json.dumps(self.cvs.manifest(), ensure_ascii=False, indent=2) + "\n"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated files differ from canonical sources")
    args = parser.parse_args()
    try:
        outputs = Site().outputs()
    except (OSError, ValueError, KeyError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1
    stale = []
    for relative, contents in outputs.items():
        target = ROOT / relative
        if not target.exists() or target.read_text(encoding="utf-8") != contents:
            stale.append(relative)
            if not args.check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(contents, encoding="utf-8")
    if args.check and stale:
        print("Generated output is stale; run python3 tools/build.py:\n" + "\n".join(stale), file=sys.stderr)
        return 1
    print(f'{"Checked" if args.check else "Built"} {sum(path.endswith(".html") for path in outputs)} pages, sitemap.xml and CV manifest ({len(stale)} {"stale" if args.check else "updated"}).')
    return 0


if __name__ == "__main__":
    sys.exit(main())
