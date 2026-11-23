"""Render role-specific, bilingual CVs from reviewed content.

The same profile and language determine the document, navigation and PDF path.
All controls are ordinary links and work without JavaScript or translation APIs.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ('en', 'es')
UI = {
    'en': {
        'collection': 'CV collection', 'intro': 'Choose the CV that fits the role.',
        'help': 'Five role-focused CVs highlight transferable technical skills. An environmental specialization and the complete career record are also available, all in English and Spanish.',
        'focus': 'Focus', 'language': 'Language', 'role_nav': 'CV focus',
        'focused': 'Focused CV', 'master': 'Master CV', 'master_desc': 'Complete professional history, projects and publications.',
        'download': 'Download PDF', 'print': 'Print / Save PDF', 'contact': 'Contact Jay',
        'summary': 'Profile', 'skills': 'Core skills', 'experience': 'Relevant experience',
        'projects': 'Selected development', 'publications': 'Publications', 'education': 'Education & languages',
        'portfolio': 'Portfolio & case studies', 'languages': 'Languages: English and Spanish.',
        'first_author': 'First author', 'coauthor': 'Coauthor', 'contribution': 'Contribution',
        'contribution_text': 'Watershed delineation, spatial data preparation and reference-stream classification.',
        'sections': 'CV sections', 'earlier': 'Earlier experience', 'evaluation': 'Program evaluation', 'nasa': 'NASA DEVELOP',
        'all_experience': 'Experience', 'all_projects': 'Software & web', 'all_education': 'Education',
    },
    'es': {
        'collection': 'Versiones del CV', 'intro': 'Elige el CV que mejor se ajuste al puesto.',
        'help': 'Cinco CV por perfil profesional destacan competencias técnicas transferibles. También puedes elegir la especialidad ambiental o la trayectoria completa, en español e inglés.',
        'focus': 'Enfoque', 'language': 'Idioma', 'role_nav': 'Enfoque del CV',
        'focused': 'CV especializado', 'master': 'CV completo', 'master_desc': 'Trayectoria profesional, proyectos y publicaciones completos.',
        'download': 'Descargar PDF', 'print': 'Imprimir / Guardar PDF', 'contact': 'Contactar a Jay',
        'summary': 'Perfil', 'skills': 'Competencias principales', 'experience': 'Experiencia relevante',
        'projects': 'Desarrollos seleccionados', 'publications': 'Publicaciones', 'education': 'Formación e idiomas',
        'portfolio': 'Portafolio y casos de estudio', 'languages': 'Idiomas: inglés y español.',
        'first_author': 'Primer autor', 'coauthor': 'Coautor', 'contribution': 'Contribución',
        'contribution_text': 'Delimitación de cuencas, preparación de datos espaciales y clasificación de cauces de referencia.',
        'sections': 'Secciones del CV', 'earlier': 'Experiencia anterior', 'evaluation': 'Evaluación de programas', 'nasa': 'NASA DEVELOP',
        'all_experience': 'Experiencia', 'all_projects': 'Software y desarrollo web', 'all_education': 'Formación',
    },
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def translated(value: dict, language: str) -> str:
    return esc(value[language])


class CVCollection:
    def __init__(self, site_data: dict):
        self.site = site_data
        self.common = json.loads((ROOT / 'content/cv/common.json').read_text())
        self.profiles = {path.stem: json.loads(path.read_text()) for path in sorted((ROOT / 'content/cv/profiles').glob('*.json'))}
        self.order = self.common['profile_order']
        self.default = self.common['default_profile']
        self.validate()

    def validate(self):
        if set(self.profiles) != set(self.order) - {'master'} or self.default not in self.profiles:
            raise ValueError('CV profiles must match the configured focus list')
        for key, profile in self.profiles.items():
            if profile['id'] != key or not re.fullmatch(r'[a-z0-9-]+', key):
                raise ValueError(f'Invalid CV profile: {key}')
            pairs = [profile[name] for name in ('label', 'description', 'summary')]
            for group in profile['skills']:
                pairs.extend([group['label'], group['text']])
            for category in ('experience', 'projects'):
                ids = [entry['id'] for entry in profile[category]]
                if len(ids) != len(set(ids)) or set(ids) - self.common[category].keys():
                    raise ValueError(f'{key}: invalid {category} entries')
                for entry in profile[category]:
                    pairs.extend(entry['bullets'])
            if any(set(pair) != set(LANGUAGES) or any(not pair[lang].strip() for lang in LANGUAGES) for pair in pairs):
                raise ValueError(f'{key}: every CV statement must have English and Spanish text')

    def label(self, profile: str, language: str) -> str:
        return UI[language]['master'] if profile == 'master' else self.profiles[profile]['label'][language]

    def description(self, profile: str, language: str) -> str:
        return UI[language]['master_desc'] if profile == 'master' else self.profiles[profile]['description'][language]

    def page_path(self, profile: str, language: str) -> str:
        return f'cv/{profile}-{language}.html'

    def pdf_path(self, profile: str, language: str) -> str:
        if profile == 'master' and language == 'en':
            return 'assets/Jay_Antonio_Oliver_CV.pdf'
        name = '_'.join(word.title() for word in profile.split('-'))
        return f'assets/cv/Jay_Antonio_Oliver_{name}_{language.upper()}.pdf'

    def manifest(self) -> dict:
        return {'schema_version': 1, 'default_profile': self.default, 'documents': [
            {'profile': profile, 'language': language, 'label': self.label(profile, language),
             'page': self.page_path(profile, language), 'pdf': self.pdf_path(profile, language),
             'max_pages': None if profile == 'master' else 2}
            for profile in self.order for language in LANGUAGES
        ]}

    def controls(self, profile: str, language: str, prefix: str) -> str:
        ui = UI[language]
        choices = ''.join(
            f'<a href="{prefix}{self.page_path(key, language)}" data-cv-profile="{key}"' +
            (' aria-current="page"' if key == profile else '') +
            f'><strong>{esc(self.label(key, language))}</strong><span>{esc(self.description(key, language))}</span></a>'
            for key in self.order
        )
        languages = ''.join(
            f'<a href="{prefix}{self.page_path(profile, lang)}" lang="{lang}" hreflang="{lang}" data-cv-language="{lang}"' +
            (' aria-current="page"' if lang == language else '') +
            f'>{"English" if lang == "en" else "Español"}</a>' for lang in LANGUAGES
        )
        sections = [('cv-summary', ui['summary']), ('cv-experience', ui['all_experience']), ('cv-software', ui['all_projects']), ('cv-publications', ui['publications']), ('cv-education', ui['all_education']), ('cv-skills', ui['skills'])]
        if profile == 'master':
            sections.insert(2, ('cv-nasa', ui['nasa']))
            sections.insert(3, ('cv-evaluation', ui['evaluation']))
            sections.insert(5, ('cv-additional', ui['earlier']))
        else:
            sections.insert(1, sections.pop())
        index = ''.join(f'<a href="#{anchor}">{esc(label)}</a>' for anchor, label in sections)
        return (f'<section class="container cv-picker" id="cv-chooser" aria-label="{esc(ui["collection"])}">'
                f'<div class="cv-picker-heading"><p class="eyebrow">{esc(ui["collection"])}</p><p class="cv-picker-title">{esc(ui["intro"])}</p><p>{esc(ui["help"])}</p></div>'
                f'<div class="cv-picker-controls"><details class="cv-role-picker"><summary><span>{esc(ui["focus"])}</span><strong>{esc(self.label(profile, language))}</strong></summary><nav aria-label="{esc(ui["role_nav"])}">{choices}</nav></details>'
                f'<div class="cv-language-picker"><span>{esc(ui["language"])}</span><nav aria-label="{esc(ui["language"])}">{languages}</nav></div></div>'
                f'<div class="cv-actions actions"><a class="button" href="{prefix}{self.pdf_path(profile, language)}" download data-cv-download>{esc(ui["download"])} · {"English" if language == "en" else "Español"}</a><button class="button button-secondary" type="button" data-print hidden>{esc(ui["print"])}</button><a class="text-link" href="{prefix}contact.html">{esc(ui["contact"])}</a></div></section>'
                f'<nav class="container cv-index" aria-label="{esc(ui["sections"])}">{index}</nav>')

    def header(self, profile: str, language: str) -> str:
        ui = UI[language]
        return (f'<header class="cv-header"><p class="cv-kicker">{esc(ui["focused"])}</p><h1>{esc(self.site["full_name"])}</h1>'
                f'<p class="cv-title">{esc(self.label(profile, language))}</p><div class="cv-contact"><span>Quito, Ecuador</span>'
                f'<a href="mailto:{esc(self.site["email"])}">{esc(self.site["email"])}</a><a href="{esc(self.site["phone_url"])}">{esc(self.site["phone"])}</a>'
                f'<a href="{esc(self.site["linkedin"])}">LinkedIn</a><a href="{esc(self.site["base_url"])}">{esc(ui["portfolio"])}</a></div></header>')

    def publications(self, language: str) -> str:
        ui = UI[language]
        return (f'<section class="cv-section" aria-labelledby="cv-publications"><h2 id="cv-publications">{esc(ui["publications"])}</h2>'
                f'<div class="cv-publication"><p><strong>Oliver, J.</strong>, &amp; McManamay, R. A. (2025). <span lang="en">United States multi-sector land use and land cover base maps to support human and Earth system models.</span> <em>Scientific Data</em>, 12, 455. <strong>{esc(ui["first_author"])}.</strong> <a href="https://doi.org/10.1038/s41597-025-04713-6">doi:10.1038/s41597-025-04713-6</a></p></div>'
                f'<div class="cv-publication"><p>Lueders, M. B., McManamay, R. A., <strong>Oliver, J. A.</strong>, Young, D., Bean, P., &amp; Mayes, K. (2026). <span lang="en">Reconstructing Long-Term Historical Hydrologic Alteration to Support Environmental Flows in Texas.</span> <em>River Research and Applications</em>. <strong>{esc(ui["coauthor"])}.</strong> <a href="https://doi.org/10.1002/rra.70172">doi:10.1002/rra.70172</a></p><p><strong>{esc(ui["contribution"])}:</strong> {esc(ui["contribution_text"])}</p></div></section>')

    def article(self, profile: str, language: str) -> str:
        if profile == 'master':
            path = ROOT / ('content/cv.html' if language == 'en' else 'content/cv/master-es.html')
            source = path.read_text()
            source = re.sub(r'<article\b[^>]*>', f'<article class="cv-sheet cv-master" lang="{language}" data-cv-document="master" data-cv-locale="{language}">', source, count=1)
            return source
        p = self.profiles[profile]
        ui = UI[language]
        sections = [self.header(profile, language), f'<section class="cv-section" aria-labelledby="cv-summary"><h2 id="cv-summary">{esc(ui["summary"])}</h2><p>{translated(p["summary"], language)}</p></section>']
        skills = ''.join(f'<p><strong>{translated(group["label"], language)}:</strong> {translated(group["text"], language)}</p>' for group in p['skills'])
        sections.append(f'<section class="cv-section cv-compact-skills" aria-labelledby="cv-skills"><h2 id="cv-skills">{esc(ui["skills"])}</h2>{skills}</section>')
        experience = []
        for entry in p['experience']:
            meta = self.common['experience'][entry['id']]
            bullets = ''.join(f'<li>{translated(bullet, language)}</li>' for bullet in entry['bullets'])
            experience.append(f'<div class="cv-entry" data-experience="{entry["id"]}"><h3>{esc(meta["employer"])} — {translated(meta["role"], language)}</h3><p class="cv-dates">{translated(meta["location"], language)} | {translated(meta["dates"], language)}</p><ul>{bullets}</ul></div>')
        sections.append(f'<section class="cv-section" aria-labelledby="cv-experience"><h2 id="cv-experience">{esc(ui["experience"])}</h2>{"".join(experience)}</section>')
        projects = []
        for entry in p['projects']:
            meta = self.common['projects'][entry['id']]
            name = meta.get('name_es', meta['name']) if language == 'es' else meta['name']
            heading = f'<a href="{esc(meta["url"])}">{esc(name)}</a>' if meta.get('url') else esc(name)
            bullets = ''.join(f'<li>{translated(bullet, language)}</li>' for bullet in entry['bullets'])
            projects.append(f'<div class="cv-entry" data-project="{entry["id"]}"><h3>{heading} — {translated(meta["role"], language)}</h3><ul>{bullets}</ul></div>')
        sections.append(f'<section class="cv-section" aria-labelledby="cv-software"><h2 id="cv-software">{esc(ui["projects"])}</h2>{"".join(projects)}</section>')
        sections.append(self.publications(language))
        degrees = ''.join(f'<p><strong>{esc(degree["institution"])}</strong> — {translated(degree["degree"], language)} ({degree["year"]}).</p>' for degree in self.common['education'])
        sections.append(f'<section class="cv-section cv-keep" aria-labelledby="cv-education"><h2 id="cv-education">{esc(ui["education"])}</h2>{degrees}<p>{esc(ui["languages"])}</p></section>')
        return f'<article class="cv-sheet cv-targeted" lang="{language}" data-cv-document="{profile}" data-cv-locale="{language}">' + '\n'.join(sections) + '</article>'
