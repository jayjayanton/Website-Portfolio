"""Language routing for static pages, with stable existing English URLs."""
from __future__ import annotations

import html
import posixpath
import re
from urllib.parse import quote, unquote, urlsplit, urlunsplit

LANGUAGES = ('en', 'es')
ROOT_PAGES = {'index.html', 'projects.html', 'research.html', 'about.html', 'contact.html', 'cv.html'}


def localized_path(path: str, language: str) -> str:
    """CV documents already encode their language; other pages use es/ for Spanish."""
    if language == 'es' and (path in ROOT_PAGES or path.startswith('projects/')):
        return 'es/' + path
    return path


def relative_url(target: str, source: str) -> str:
    return posixpath.relpath(target, posixpath.dirname(source) or '.')


def localize_body(markup: str, source: str, destination: str, language: str, base_url: str) -> str:
    """Resolve generated body URLs from their logical source into the language route.

    Assets remain shared. Explicit CV EN/ES choices and external resources remain
    intact. Absolute portfolio links in CVs stay absolute for PDF portability.
    """
    base = urlsplit(base_url)

    def replace(match):
        attribute, raw = match.groups()
        value = html.unescape(raw)
        parts = urlsplit(value)
        if not parts.path or parts.scheme in {'mailto', 'tel', 'data'}:
            return match.group(0)
        absolute_site = parts.netloc == base.netloc and parts.path.startswith(base.path)
        if parts.scheme or parts.netloc:
            if not absolute_site or language == 'en':
                return match.group(0)
            target = unquote(parts.path[len(base.path):]) or 'index.html'
            target = localized_path(target, language)
            result = urlunsplit((base.scheme, base.netloc, base.path + quote(target, safe='/'), parts.query, parts.fragment))
        else:
            if parts.path.startswith('/'):
                target = unquote(parts.path).lstrip('/')
                base_path = base.path.strip('/') + '/'
                if target.startswith(base_path):
                    target = target[len(base_path):]
            else:
                target = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parts.path)))
            target = localized_path(target, language)
            result = urlunsplit(('', '', quote(relative_url(target, destination), safe='/'), parts.query, parts.fragment))
        return f'{attribute}="{html.escape(result, quote=True)}"'

    return re.sub(r'\b(href|src|poster)="([^"]*)"', replace, markup)


def validate_translation(original, translated, path='record'):
    """Reject incomplete translations or changes to provenance and routing keys."""
    invariant = {'slug', 'categories', 'topics', 'status_key', 'kind', 'src', 'url', 'link', 'related', 'doi', 'year', 'name', 'full_name', 'base_url', 'email', 'phone', 'phone_url', 'linkedin', 'github', 'cv', 'master_cv', 'featured', 'project_order'}
    if isinstance(original, dict):
        if not isinstance(translated, dict) or original.keys() != translated.keys():
            raise ValueError(f'{path}: translated fields must match the English source')
        for key, value in original.items():
            if key in invariant and not (key == 'categories' and isinstance(value, dict)) and translated[key] != value:
                raise ValueError(f'{path}.{key}: translation changed a source or identifier')
            validate_translation(value, translated[key], f'{path}.{key}')
    elif isinstance(original, list):
        if not isinstance(translated, list) or len(original) != len(translated):
            raise ValueError(f'{path}: translated list must preserve all entries')
        for index, (left, right) in enumerate(zip(original, translated)):
            validate_translation(left, right, f'{path}[{index}]')
    elif isinstance(original, str):
        if not isinstance(translated, str) or (original.strip() and not translated.strip()):
            raise ValueError(f'{path}: missing translated text')
    elif original != translated:
        raise ValueError(f'{path}: translated data value differs')
