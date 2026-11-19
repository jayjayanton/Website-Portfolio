# Jay Oliver — Data Science & Geospatial Development

A professional portfolio of environmental research, predictive modeling, data engineering and independent software development. Each case study explains the problem, my contribution, the approach, the result and the evidence behind it. Technical progression is shown through the work: moving from observations and analysis to reusable data workflows and interactive applications.

**[Portfolio in English](https://jayjayanton.github.io/Website-Portfolio/)** · **[Portafolio en español](https://jayjayanton.github.io/Website-Portfolio/es/)** · [Projects](projects.html) · [Research](research.html) · [About](about.html) · [Contact](contact.html) · [Choose a CV · English / Español](cv.html) · [Complete master CV](cv/master-en.html)

## Selected work

- **PredioAI:** creator and sole developer of a web application connecting architectural plans, Quito property information, REST APIs and interactive spatial analysis. The case study links to the [public application](https://jayjayanton.github.io/Predio-AI/).
- **U.S. land-use basemaps:** first-author research published in *Scientific Data* in 2025, harmonizing 30-meter land-use information for multiple Earth system modeling frameworks.
- **Orphaned-well screening:** geospatial feature engineering, basin-specific XGBoost models, threshold selection and interpretation, with historical validation results kept in their original context.
- **Texas environmental flows:** watershed automation and modeling contributions to a coauthored 2026 *River Research and Applications* paper.
- **NASA DEVELOP, WWF and NETL work:** environmental observations, spatial research and data-processing workflows, presented with clear individual and team attribution.

## Build and preview

Use Python 3.12 and Node.js 22 with npm. The build uses the Python standard library; the JavaScript and tests have no package dependencies. There is no install step or bundler.

```bash
npm run build
npm run check
npm run serve
```

Open [http://localhost:8000](http://localhost:8000) for the local preview. `build` generates the public HTML, `check` verifies generated output and runs the Python and Node tests, and `serve` starts a static preview server.

The equivalent validation commands are:

```bash
python3 tools/build.py --check
python3 tools/render_cvs.py --check
python3 -m unittest discover -s tests -v
node --test tests/*.mjs
```

## Repository structure

| Location | Responsibility |
| --- | --- |
| `content/site.json` | Site metadata, project order, categories and publication records |
| `content/case-studies/*.json` | Canonical project summaries, contributions, methods, evidence and links |
| `content/es/site.json`, `content/es/case-studies/*.json` | Complete Spanish counterparts with matching source facts and structure |
| `templates/` | Shared page layouts and reusable presentation structure |
| `templates/es/`, `tools/localization.py` | Spanish page copy, language routing and translation validation |
| `tools/build.py` | Standard-library Python generator and freshness check |
| `assets/css/site.css` | Shared visual system and responsive layouts |
| `assets/js/` | Navigation, project interactions and filtering logic |
| `images/` | Existing research figures, screenshots and labeled illustrations |
| `index.html`, other root pages, `projects/*.html` | Generated public pages committed for GitHub Pages |
| `es/*.html`, `es/projects/*.html` | Spanish public pages, sharing assets and CV downloads |
| `tests/` | Offline checks for generated pages, links, content rules and filtering |
| `content/cv.html`, `content/cv/master-es.html` | Full English and Spanish master CVs |
| `content/cv/profiles/*.json`, `content/cv/common.json` | Paired English/Spanish role profiles and shared career facts |
| `tools/cv_collection.py`, `cv/*.html`, `assets/cv/manifest.json` | CV rendering, permanent language-specific pages and download catalogue |
| `tools/render_cvs.py`, `assets/cv/*.pdf` | Chrome PDF generation, content fingerprints and focused CV page limits |

Edit the canonical JSON and templates, then run `npm run build` and commit the regenerated HTML with the source changes. Direct changes to generated pages will be replaced by the next build. Keep the established case-study URLs and asset paths intact.

See [Design and content maintenance](docs/design-and-content.md) for the content model, evidence conventions and editing workflow.

## Evidence and project status

Published research, delivered work and projects in development are labeled separately. Original research figures, application screenshots and conceptual illustrations carry captions that explain what they show. Historical metrics retain their dataset, sample and model context; team findings are not presented as individual results.

Computer vision extensions for PredioAI and Quito urban expansion models remain described as planned work. The Yuyay Analytics website case study stays in the web category. PredioAI is attributed to Jay Oliver as its creator and sole developer, and its links point to the public application. Private implementations are not linked as public source code.

## Publications

- Oliver, J., and McManamay, R. A. (2025). **United States multi-sector land use and land cover base maps to support human and Earth system models.** *Scientific Data*, 12, 455. [DOI: 10.1038/s41597-025-04713-6](https://doi.org/10.1038/s41597-025-04713-6).
- Lueders, M. B., McManamay, R. A., Oliver, J. A., Young, D., Bean, P., and Mayes, K. (2026). **Reconstructing Long-Term Historical Hydrologic Alteration to Support Environmental Flows in Texas.** *River Research and Applications*. First published July 9, 2026. [DOI: 10.1002/rra.70172](https://doi.org/10.1002/rra.70172).

Case studies preserve the relevant reports, public code and research materials. Figure attribution and study limitations remain alongside the evidence.

## Validation and publishing

[Validate portfolio](.github/workflows/validate.yml) runs on pushes, pull requests and manual dispatch. It checks that generated pages match their sources and runs the Python and Node test suites using read-only repository access. It does not publish or commit files.

GitHub Pages continues to publish **the `main` branch from the repository root**. Commit the generated pages alongside canonical changes so deployment keeps the existing page and image URLs. No separate Pages deployment workflow is required for this build.

## Focused CVs and languages

[Choose a CV](cv.html) opens the Geospatial Data Scientist version by default. Five focused profiles are available in English and Spanish: Data Scientist, Spatial Analyst, Geospatial Data Specialist, Geospatial Data Engineer and Geospatial Data Scientist. The complete master CV remains a sixth option in both languages. Focused PDFs have a maximum of two pages.

The focus menu preserves the selected language; the language switch preserves the selected profile. Both use normal links and work without JavaScript. Every selection has a permanent `cv/<profile>-<language>.html` URL, its own matching PDF, document-language metadata and reciprocal language links. Spanish is reviewed content stored alongside English; no external translation API or runtime translation service is required. Official publication titles retain their original language.

Maintain the full record in `content/cv.html` and `content/cv/master-es.html`. Edit focused summaries, skills and selected bullets in `content/cv/profiles/*.json`; shared employers, job titles, dates, project links and education live in `content/cv/common.json`. Profile headlines describe the target role while historical job titles remain unchanged. Preserve NASA work, first-author/coauthor credit and the second publication's contribution statement in every focused version.

Run `npm run build`, then `python3 tools/render_cvs.py` where Chrome is available, and finally `npm run check`. The renderer reuses unchanged PDFs, using source and print-style fingerprints. `python3 tools/render_cvs.py --check` validates PDF presence and two-page limits without launching Chrome. Inspect the final PDF pages after editing; page-count checks alone do not verify layout.

The [PDF workflow](.github/workflows/build-cv.yml) generates and commits the twelve downloads and their render-state file. The read-only validation workflow renders any changed or missing PDFs in its temporary checkout before checking page limits, links and content. Keep `assets/Jay_Antonio_Oliver_CV.pdf` as the English master download for existing external links.

## English and Spanish throughout the portfolio

The homepage, project catalogue, all fifteen case studies, research, about, contact and CV chooser are available in both languages. Existing English URLs remain unchanged; their Spanish counterparts live under `es/`. The twelve language-specific CV pages retain their established URLs. The build generates 54 public HTML pages in total.

The header language control opens the corresponding page or project and preserves the current search/filter query and section anchor when JavaScript is available. Normal navigation, related projects and CV links stay in the selected language. Each language has complete static content, navigation, metadata and reciprocal `hreflang` links; reading and switching pages also work without JavaScript. No external translation service is required.

Project search accepts the reviewed English and Spanish terminology on either version. Result counts, filters, empty states, buttons, captions and accessibility labels follow the page language. Original publication titles, source-variable identifiers, figures and screenshots retain their published wording; their surrounding explanations and image descriptions are translated.

Edit English records and their complete Spanish counterparts together. `tools/localization.py` checks matching structure and immutable identifiers, source URLs and routing keys. Do not translate category or topic machine values; translate their displayed labels. Keep numerical results, individual/team attribution and implemented/planned boundaries consistent across languages. Extend both template sets when adding new visible copy.
