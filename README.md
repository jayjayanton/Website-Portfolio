# Jay Oliver — Data Science & Geospatial Development

A professional portfolio of environmental research, predictive modeling, data engineering and independent software development. Each case study explains the problem, my contribution, the approach, the result and the evidence behind it. Technical progression is shown through the work: moving from observations and analysis to reusable data workflows and interactive applications.

**[Explore the portfolio](https://jayjayanton.github.io/Website-Portfolio/)** · [Projects](projects.html) · [Research](research.html) · [About](about.html) · [Contact](contact.html) · [Download CV](assets/Jay_Antonio_Oliver_CV.pdf)

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
python3 -m unittest discover -s tests -v
node --test tests/*.mjs
```

## Repository structure

| Location | Responsibility |
| --- | --- |
| `content/site.json` | Site metadata, project order, categories and publication records |
| `content/case-studies/*.json` | Canonical project summaries, contributions, methods, evidence and links |
| `templates/` | Shared page layouts and reusable presentation structure |
| `tools/build.py` | Standard-library Python generator and freshness check |
| `assets/css/site.css` | Shared visual system and responsive layouts |
| `assets/js/` | Navigation, project interactions and filtering logic |
| `images/` | Existing research figures, screenshots and labeled illustrations |
| `index.html`, other root pages, `projects/*.html` | Generated public pages committed for GitHub Pages |
| `tests/` | Offline checks for generated pages, links, content rules and filtering |
| `content/cv.html`, `cv.html` and `assets/Jay_Antonio_Oliver_CV.pdf` | Canonical CV fragment, generated printable page and downloadable PDF |

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

Maintain CV text in `content/cv.html` and run the build to regenerate `cv.html`. The existing [printable CV workflow](.github/workflows/build-cv.yml) remains separate from site generation: changes to the generated `cv.html`, or a manual run, render and commit `assets/Jay_Antonio_Oliver_CV.pdf`. Keep that filename stable because the site’s download links use it.
