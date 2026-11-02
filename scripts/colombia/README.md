# Colombia deforestation analysis

I used R to investigate factors associated with deforestation in Colombia as part of my WWF research work. The historical analysis compared binomial GLMs with different predictor sets and examined model evaluation under random and spatially grouped validation.

## Files

- [colombia_glm_analysis.R](colombia_glm_analysis.R) — portable GLM workflow with configurable input and output paths, model coefficients, holdout metrics, and optional geographically grouped validation.
- [wwf_Colombia_GLM_original.R](wwf_Colombia_GLM_original.R) — my original historical script, retained for provenance. It contains hard-coded paths, positional feature selection, and the historical residual-autocovariate (RAC) approach.
- [Original comparison table](../../tables/colombia-glm-model-comparison.csv) — historical Full, Stepwise, Naive, and RAC model coefficients from my work document.

## Running the updated script

From the repository root, with R installed:

```bash
Rscript scripts/colombia/colombia_glm_analysis.R \
  --input data/colombia.csv \
  --output-dir outputs/colombia \
  --target Deforestation
```

The input CSV is **not included**. It must contain a binary `Deforestation` target coded 0/1, a numeric `Elevation` column, and numeric predictor columns. If distance columns ending in `_Dist` are stored in metres, add `--distances-in-metres true`. Use `--predictors Slope,Elevation,Main_Cities_Dist` to specify an explicit set of columns. Otherwise, the script uses numeric columns except identifiers and coordinates.

The updated script uses base R, outputs `glm_coefficients.csv`, `holdout_predictions.csv`, and `holdout_metrics.csv`, and can produce `spatial_fold_metrics.csv` if valid latitude and longitude columns exist.

## Differences from my original analysis

I removed the personal Windows path and replaced fragile column-number exclusions with named predictor selection. The updated script uses complete-case filtering instead of silently setting all missing values to zero, a stratified 70/30 holdout, and a fixed 0.5 classification threshold. It keeps stepwise selection inside the training partition for holdout evaluation.

**The portable script currently implements Full, Stepwise, and Naive GLMs.** It does not recreate the historical RAC specification, HC3 robust standard errors, 10 × 10 repeated CV, or exact 150-km spatial fold definition. Those remain documented in the original script. The simplified geographic folds are not numerically equivalent to the original spatial CV.

The historical map is labeled as a **Random Forest** output in my WWF work document; the R script and coefficient table describe **GLMs**. These are separate modeling outputs and should not be treated as the same fitted model.

No historical results can be reproduced exactly without the original dataset, feature choices, and original package environment. Please check data permissions before sharing any input data.
