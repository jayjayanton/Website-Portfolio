# Design and content maintenance

## Purpose

The portfolio presents Jay Oliver’s proven work and technical progression through specific projects. A reader should be able to identify the problem, Jay’s responsibility, the method and the result before opening detailed figures or tables. Research evidence and implementation detail support the narrative without overwhelming the overview.

The site is a static publication. Canonical content and shared templates generate committed HTML, while a small amount of JavaScript provides navigation and project filtering. There is no application backend or build-time dependency installation.

## Architecture

`tools/build.py` uses the Python standard library to read `content/site.json`, the records in `content/case-studies/`, and the shared templates. It generates the main site pages and the existing `projects/<slug>.html` case-study URLs.

| Layer | Edit here | Purpose |
| --- | --- | --- |
| Site content | `content/site.json` | Identity, navigation-related metadata, featured projects, categories, project ordering and publications |
| Project content | `content/case-studies/<slug>.json` | One canonical record for each project |
| CV content | `content/cv.html` | Canonical CV fragment, with existing career and education details preserved |
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

GitHub Pages serves `main` from the repository root. Generated root pages and case-study pages remain committed to preserve the existing publication setup. The validation workflow has `contents: read`, runs on push, pull request and manual dispatch, and neither deploys nor writes repository content.

Maintain CV text in the canonical `content/cv.html` fragment and rebuild the generated `cv.html` page. Keep career dates, qualifications and historical metrics intact unless a content update explicitly covers them. The existing `build-cv.yml` action renders the generated page with Chrome/Chromium and commits the PDF to `assets/Jay_Antonio_Oliver_CV.pdf`. Its write permission belongs to that separate PDF job; the validation workflow does not need it. Preserve the PDF path, download links and existing case-study/image URLs.
