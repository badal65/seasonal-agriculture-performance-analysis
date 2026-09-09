# Seasonal Agriculture Performance Analysis

**Student:** Badal Chaudhary  
**Student ID / Roll No.:** STU6a30b8115dd5c1781577745  
**Programme:** VOIS AICTE Batch 1, 2026–2027

## Objective
Analyse how agricultural performance changes across Kharif, Rabi and Zaid seasons using yield, production, environmental conditions, resource use, economics and disease/pest risk.

## Contents
- `notebooks/seasonal_agriculture_analysis.ipynb` — reproducible notebook.
- `src/analysis.py` — validation, summaries, correlations and charts.
- `app.py` — interactive Streamlit dashboard.
- `data/sample/` — clearly labelled smoke-test sample, not the submitted 4,000-row data.
- `Badal_Chaudhary_Seasonal_Agriculture_Analysis.pptx` — personalized presentation.

## Run
1. Copy the supplied CSV to `data/seasonal_agriculture_performance_dataset.csv`.
2. `pip install -r requirements.txt`
3. `python src/analysis.py --input data/seasonal_agriculture_performance_dataset.csv --output outputs`
4. `jupyter notebook notebooks/seasonal_agriculture_analysis.ipynb`
5. `streamlit run app.py`

The pipeline validates all 28 required columns, reports missingness and duplicate Farm_ID values, exports season/crop/irrigation summaries, correlations and charts, and flags negative-profit rows. Correlation is reported as association, not causation. Results must be interpreted within the supplied dataset and its sampling limits.
