"""End-to-end contracts for role/language choices and their downloadable CVs."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from check_links import local_target, read_document
from cv_collection import CVCollection


class CVLinks(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.role_links = {}
        self.language_links = {}
        self.download = None
        self.document = None
        self.experience = []
        self.feed(source)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'a':
            if 'data-cv-profile' in attrs:
                self.role_links[attrs['data-cv-profile']] = attrs['href']
            if 'data-cv-language' in attrs:
                self.language_links[attrs['data-cv-language']] = attrs['href']
            if 'data-cv-download' in attrs:
                self.download = attrs['href']
        if 'data-cv-document' in attrs:
            self.document = (attrs['data-cv-document'], attrs['data-cv-locale'])
        if 'data-experience' in attrs:
            self.experience.append(attrs['data-experience'])


class CVCollectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.collection = CVCollection(json.loads((ROOT / 'content/site.json').read_text()))
        cls.manifest = json.loads((ROOT / 'assets/cv/manifest.json').read_text())

    def test_fourteen_unique_documents_and_downloads(self):
        docs = self.manifest['documents']
        self.assertEqual(len(docs), 14)
        self.assertEqual(len({doc['page'] for doc in docs}), 14)
        self.assertEqual(len({doc['pdf'] for doc in docs}), 14)
        for doc in docs:
            with self.subTest(profile=doc['profile'], language=doc['language']):
                self.assertTrue((ROOT / doc['page']).is_file())
                self.assertTrue((ROOT / doc['pdf']).is_file(), 'Generate CV PDFs before running the full validation suite')

    def test_switches_preserve_focus_or_language_and_download_match(self):
        for doc in self.manifest['documents']:
            with self.subTest(page=doc['page']):
                path = ROOT / doc['page']
                links = CVLinks(path.read_text())
                self.assertEqual(links.document, (doc['profile'], doc['language']))
                self.assertEqual(read_document(path).lang, doc['language'])
                self.assertEqual(set(links.role_links), set(self.collection.order))
                for role, href in links.role_links.items():
                    target, _ = local_target(href, path, ROOT)
                    self.assertEqual(target, ROOT / f'cv/{role}-{doc["language"]}.html')
                self.assertEqual(set(links.language_links), {'en', 'es'})
                for language, href in links.language_links.items():
                    target, _ = local_target(href, path, ROOT)
                    self.assertEqual(target, ROOT / f'cv/{doc["profile"]}-{language}.html')
                target, _ = local_target(links.download, path, ROOT)
                self.assertEqual(target, ROOT / doc['pdf'])

    def test_default_is_focused_and_master_url_stays_available(self):
        default = CVLinks((ROOT / 'cv.html').read_text())
        self.assertEqual(default.document, ('geospatial-data-scientist', 'en'))
        master = next(doc for doc in self.manifest['documents'] if doc['profile'] == 'master' and doc['language'] == 'en')
        self.assertEqual(master['pdf'], 'assets/Jay_Antonio_Oliver_CV.pdf')

    def test_focused_cvs_retain_research_history_and_publication_credit(self):
        for doc in self.manifest['documents']:
            if doc['profile'] == 'master':
                continue
            with self.subTest(page=doc['page']):
                path = ROOT / doc['page']
                source = path.read_text()
                parsed = CVLinks(source)
                self.assertEqual(set(parsed.experience), {'leidos', 'baylor-lab', 'baylor-specialist', 'usgs', 'wwf', 'nasa'})
                self.assertIn('NASA DEVELOP', source)
                self.assertIn('10.1038/s41597-025-04713-6', source)
                self.assertIn('10.1002/rra.70172', source)
                for phrase in (('First author', 'Coauthor', 'Contribution:') if doc['language'] == 'en' else ('Primer autor', 'Coautor', 'Contribución:')):
                    self.assertIn(phrase, source)

    def test_translations_have_distinct_content_and_shared_career_facts(self):
        for profile in self.collection.profiles.values():
            self.assertNotEqual(profile['summary']['en'], profile['summary']['es'])
        for record in self.collection.common['experience'].values():
            for year in re.findall(r'\b20\d{2}\b', record['dates']['en']):
                self.assertIn(year, record['dates']['es'])


if __name__ == '__main__':
    unittest.main()
