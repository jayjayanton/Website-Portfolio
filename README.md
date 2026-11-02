# Geospatial Data Science Portfolio

I built this portfolio to present my work in geospatial analytics, machine learning, environmental research, and data engineering. Rather than only listing technologies, I want each project to explain the problem I worked on, the methods I used, and why the results matter.

The site uses HTML, CSS, and JavaScript, with a black, neon cyan, and bright-pink visual theme. It has separate pages for my projects, published research, background, and contact information.

## Explore the site

- [Homepage](index.html) — introduction and featured projects.
- [Projects](projects.html) — overview of my technical work.
- [Research](research.html) — peer-reviewed publications and related code.
- [About](about.html) — my background and technical tools.
- [Contact](contact.html) — professional links.
- [Land-use dynamics case study](projects/land-use-dynamics.html) — classification maps and harmonization methods from my 2025 *Scientific Data* publication.

## Land-use classification research

One of the featured projects is my work on U.S. land-use and land-cover base maps for Earth system modeling. The case study explains how I worked with the MSD classification and compared representations for GCAM, LUH2, and CLM.

I organized the figures in this order:

1. **Sankey diagram** — shows how source land-cover classes move through the harmonization workflow.
2. **MSD classes** — shows the distribution of land-cover classes across the conterminous United States.
3. **GCAM–MSD** — compares GCAM land-use categories with the MSD classification.
4. **LUH2–MSD** — shows the LUH2 land-cover representation.
5. **CLM–MSD** — shows the CLM plant functional type representation.

The corresponding images belong in [images/](images/) and are referenced by the [land-use case study](projects/land-use-dynamics.html).

The research was published in *Scientific Data* (Nature Portfolio, 2025): [read the paper](https://www.nature.com/articles/s41597-025-04713-6). The [research code](https://github.com/jayjayanton/oliver-mcmanamay_2025_scidata) is also available on GitHub.

## Deforestation research in Colombia

I also included a [Colombia deforestation case study](projects/colombia-deforestation.html) based on my WWF research examples. It includes a historical deforestation-risk map, the original GLM comparison table (Full, Stepwise, Naive and RAC), and my [R analysis script](research/colombia/wwf_Colombia_GLM_V3.R). The map is labeled as a Random Forest output in the source document, while the table and R script cover generalized linear models; I present them as related but distinct analyses.

The wider [land-use dynamics page](projects/land-use-dynamics.html) now connects land-cover mapping, deforestation, water resources and vegetation health, and health and air quality. Each research stream has its own scientific context rather than being presented as one publication.

## Other featured projects

My other case-study pages cover orphaned well prediction, carbon storage mapping, coal ash modeling, EPA greenhouse gas data automation, and webcam image extraction. Some of the underlying datasets and implementations are proprietary, so those projects focus on my technical contributions and permitted high-level descriptions.

## Running the website

Clone or download this repository and open `index.html` in a browser. No backend is required. The navigation links connect to the other HTML pages.

For GitHub Pages, go to **Settings → Pages**, select **Deploy from a branch**, and publish the `main` branch from the repository root.

## Figures and attribution

The HTML expects the five PNGs listed in [images/README.md](images/README.md). **Until those PNG files are uploaded, the figure gallery will display broken image links.** The images were supplied separately from the code and are not yet committed to this repository.

I retain attribution to the original research and follow the publication's applicable figure-reuse terms.
