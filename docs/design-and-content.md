# Design and content maintenance

## Purpose

The portfolio presents Jay Oliver’s proven work and technical progression through specific projects. A reader should be able to identify the problem, Jay’s responsibility, the method and the result before opening detailed figures or tables. Research evidence and implementation detail support the narrative without overwhelming the overview.

The site is a static publication. Canonical content and shared templates generate committed HTML, while a small amount of JavaScript provides navigation and project filtering. There is no application backend or build-time dependency installation.

## Portfolio color identity

The personal portfolio uses warm ivory, charcoal and indigo. This identity is independent of the brands shown inside its case studies, including PredioAI. Keep original application screenshots and research figures in their source colors.

| Token | Color | Use |
| --- | --- | --- |
| `--canvas` | `#F7F5F2` | Warm ivory page background |
| `--surface` | `#FFFFFF` | Cards and evidence surfaces |
| `--ink` | `#24232B` | Charcoal headings and dark panels |
| `--accent` | `#5146A6` | Indigo links, buttons and selected controls |
| `--accent-dark` | `#403585` | Hover and emphasized accent text |
| `--accent-soft` | `#EEEBFA` | Pale lavender supporting panels |
| `--muted` | `#625F6A` | Secondary text |

Use neutral borders for decoration and the stronger `--control-line` for input boundaries. Development badges use a warm amber treatment with a written status label. Dark panels use light text and focus outlines. When changing the palette, update the shared stylesheet, browser theme color and favicon, then rebuild all pages.

## Architecture

`tools/build.py` uses the Python standard library to read `content/site.json`, the records in `content/case-studies/`, and the shared templates. It generates the main site pages and the existing `projects/<slug>.html` case-study URLs.

| Layer | Edit here | Purpose |
| --- | --- | --- |
| Site content | `content/site.json` | Identity, navigation-related metadata, featured projects, categories, project ordering and publications |
| Project content | `content/case-studies/<slug>.json` | One canonical record for each project |
| Master CV content | `content/cv.html`, `content/cv/master-es.html` | Full professional record in English and Spanish |
| Focused CV content | `content/cv/profiles/*.json`, `content/cv/common.json` | Five paired role profiles, shared career facts and selected development evidence |
| Presentation | `templates/` | Base document, page layouts and consistent case-study structure |
| Visual system | `assets/css/site.css` | Typography, spacing, color, components and responsive behavior |
| Interaction | `assets/js/site.js`, `assets/js/projects.js`, `assets/js/filtering.mjs` | Site navigation, project controls and filter logic |
| Generated output | Root HTML pages and `projects/*.html` | Files served by GitHub Pages |
| Verification | `tests/` and `tools/check_links.py` | Offline structural, link, content and filtering checks |

Treat the generated HTML as a build artifact. Edit the canonical source, rebuild, review the output and commit both together. Preserve the existing project slugs, page URLs and image paths when changing presentation.

## Case-study model

Records use plain strings rather than embedded Markdown or authored HTML. Keep summaries concise enough to work on a project card as well as the case-study page.

| Fields | Content rule |
| --- | --- |
| `slug`, `title`, `summary` | Stable URL identifier, readable title and a short description of the work |
| `categories` | Applicable keys defined in `content/site.json`; use demonstrated work to choose categories |
| `status`, `status_key` | Human-readable status and its stable key: `published`, `delivered` or `development` |
| `role`, `context`, optional `period` | Individual contribution, institutional or product context, and verified timing only |
| `image` | Cover with `src`, `alt`, `caption` and `kind`; clearly identify its provenance |
| `technologies` | Tools or methods actually used in the described work |
| `problem`, `contribution` | The question or need, followed by what Jay was responsible for |
| `approach` | A sequence of objects with `title` and `body` explaining the method |
| `outcome`, `limitations` | What the work produced and the boundaries of the evidence |
| `learning` | Supported method transfer, technical progression or changes in approach |
| `evidence` | Supporting sections with `title`, `body`, `images` and an optional `table` |
| `links` | Labeled URLs with kind `publication`, `code`, `report` or `live` |
| `related` | Existing project slugs connected by subject or method |

An evidence table has `headers` and `rows`; every row must match the number of headers. Image records use repository-root-relative paths such as `images/figure-02-msd-classes.png`, or verified HTTPS URLs. Preserve descriptive alt text and captions when reusing an image.

## Truthful capability and progression

Describe completed implementation separately from planned work. A new tool, model or product direction belongs in a development statement until the supporting work exists. Status labels should make the distinction visible at both the card and case-study level.

Learning is demonstrated through the work itself: adapting a method to a new measurement, improving a reusable workflow, changing a modeling strategy or bringing analysis into an application. Avoid inventing courses, certifications, personal learning experiences, deployed models, clients, revenue or impact figures.

The following project boundaries are deliberate:

- **PredioAI:** preserve “creator and sole developer” attribution. Its public links lead to the application or the portfolio case study. Use the local screenshot and do not embed or link implementation-source locations. The current document workflow processes native PDF/CAD geometry; image-based computer vision is a planned extension.
- **Quito urban expansion:** distinguish the satellite-data pipeline from planned computer vision segmentation. Keep the project’s development status visible.
- **Yuyay Analytics:** the portfolio case study concerns building the consulting website and remains in the `web` category. The business services advertised on that website do not establish that its implementation is a data-science project.
- **Collaborative research:** identify Jay’s contribution separately from the team’s results. Coauthorship does not imply sole ownership of every analysis, figure or application.

## Evidence and metric provenance

Use explicit captions for original research figures, historical outputs, live-application screenshots and conceptual or synthetic illustrations. Illustrations explain an idea; they do not substantiate model performance or measurements. Do not recreate scientific results with generated imagery.

Keep numerical context beside the result. Name the model, dataset or sample, evaluation partition and historical checkpoint when available. Preserve the substantive evidence when revising a summary.

Some case-specific distinctions must survive future edits:

- Orphaned-well March baseline reports, the earlier presentation checkpoint and the later Appalachian enrichment study are separate results.
- NASA air-quality full-period regressions, matched-window comparisons and regional poster summaries use different samples.
- The Colombia deforestation risk map is a Random Forest output; the coefficient table documents GLM specifications.
- Environmental-flow tree-depth figures show training fit and candidate numerical inflections, not validated ecological thresholds.
- Coal-ash methodology is documented without treating private implementation details or unverified scores as public evidence.
- NETL atlas screenshots show a collaborative delivery environment; Jay’s case describes raster-to-vector automation and data preparation.

Prefer the publication or technical report as the primary source link when it is the strongest evidence. Offer public code when available. Do not send readers to private or unrelated repositories as the main project action.

## Editing workflow

1. Update the relevant canonical record, site metadata or shared template. Check any new factual claim against the research, implementation or source material.
2. Run `npm run build` to regenerate the public pages.
3. Run `npm run check` to verify freshness and execute the Python and Node tests.
4. Run `npm run serve` and inspect the affected pages in a browser. For layout or interaction changes, check narrow and wide viewports, keyboard navigation, focus visibility and project filters.
5. Review the diff. Commit the canonical changes, generated pages and any required assets together.

No `npm install` is needed. The validation environment uses Python 3.12 and Node.js 22. The underlying commands are:

```bash
python3 tools/build.py --check
python3 -m unittest discover -s tests -v
node --test tests/*.mjs
```

The freshness check detects output that no longer matches the canonical source. The offline checks cover local links, page structure and designated content constraints; they do not establish that external municipal services, research hosts or applications are currently available. Verify an external destination when changing its link or its claim.

## Deployment and stable URLs

### Master CV

The master CV pages and downloadable master PDFs are comprehensive professional records. Keep detailed Leidos/NETL contributions and separate NASA air-quality and water-resources subsections, alongside both Baylor roles, USGS, WWF, independent software development, earlier evaluation support and teaching. Individual projects may have different dates from the freelance practice; do not assign the practice start date to every project. Identify evaluation assignments as project support rather than direct employment by the named partner agencies.

Use supported contribution and method statements rather than unqualified performance claims. Keep future computer vision work explicitly planned, distinguish local prototypes from deployed services, and preserve PredioAI’s creator and sole-developer attribution and application-only links. Maintain full publication citations. Shorter application-specific CVs can be derived from this source without removing the master record’s detail.

The print layout uses a single reading column with 10-point body text and allows long roles to continue across pages. Headings, dates and scope introductions stay with following content, while individual bullets avoid page splits. Selected `cv-page-start` boundaries give the master CV coherent page openings; the short education section uses `cv-keep`. Named print-page margins add the CV name and page numbers in the Chrome-generated PDF. Review every rendered PDF page whenever content or print styling changes; a successful HTML build does not verify pagination.

### Publication workflow

GitHub Pages serves `main` from the repository root. Generated root pages and case-study pages remain committed to preserve the existing publication setup. The validation workflow has `contents: read`, runs on push, pull request and manual dispatch, and neither deploys nor writes repository content.

### Focused and bilingual CV collection

The default `cv.html` page displays the English Geospatial Data Scientist profile. Five focused profiles and the complete master are available through `cv/<profile>-<language>.html` for `en` and `es`. Each page exposes a focus menu, English/Spanish links and its matching PDF. Changing focus preserves language; changing language preserves focus. These controls work as native links without JavaScript. Site CV calls to action open the chooser rather than automatically downloading the long master.

Store focused text as paired `en`/`es` values in `content/cv/profiles/*.json`. Shared career facts and qualifications are in `content/cv/common.json`. The generator validates language completeness and known experience/project IDs, then escapes text into common templates. The source record and translations must agree on dates, quantities, scope and completed versus planned work. Keep official publication titles in English, with `lang="en"` markup in Spanish documents. Preserve first-author/coauthor labels and the specific contribution under the second publication.

The generated `assets/cv/manifest.json` maps all twelve pages to PDF paths. `tools/render_cvs.py` renders changed documents with Chrome, checks PDF structure and records source/style/renderer fingerprints in `assets/cv/render-state.json`. Its `--check` option enforces the two-page maximum for focused profiles. Master versions retain their full detail and have no artificial page limit. Review every changed PDF page after rendering.

The PDF workflow commits all downloads. The separate validation workflow has read-only permissions and can render changed or missing PDFs into its temporary checkout before checking page limits and links. For a new collection, render and review on a working branch before publishing its pages and PDFs together. The original English master path `assets/Jay_Antonio_Oliver_CV.pdf` remains stable; preserve all existing case-study and image URLs.


### Complete Spanish and English routes

Existing English pages retain their URLs. Spanish copies of the six general pages and fifteen case studies use `es/`; explicit CV language URLs remain under `cv/`. Generate all 54 pages together. A global header control links each document to its corresponding language version, including the same focused CV when applicable. Navigation and internal case-study links preserve the selected language, while assets and external sources remain shared.

`tools/localization.py` resolves body links from their logical source page into the destination route. Keep the two language links explicit and outside that rewrite so they remain language choices. The resolver also localizes absolute portfolio links in Spanish CVs while retaining absolute URLs for PDF portability. Do not redirect external application, repository or publication URLs.

The browser enhancement preserves query strings and fragment identifiers when switching language, including active project filters. Both English and Spanish source text is indexed for search so the carried query remains useful after switching. Native links and static translations continue to work without JavaScript. Avoid automatic language redirects: an explicit shared English or Spanish URL should always open that version.

Maintain matching `content/case-studies/*.json` and `content/es/case-studies/*.json` records, `content/site.json` and `content/es/site.json`, and the six body templates in `templates/` and `templates/es/`. Source URLs, image paths, metrics, project ordering, category/topic keys and responsibility claims must agree. Translate visible labels, captions, alt text, metadata, filter messages and summaries. Keep official publication titles and technical source-variable codes in their original wording; preserve original research figures with translated explanations.

The language tests check counterpart routes, navigation continuity, complete translations, provenance and nested asset links. Node tests cover search aliases and URL state preservation. Include `assets/js/navigation.mjs` in the shared JavaScript cache version. Review the live header, project filters, case studies and CV transitions after deployment.
