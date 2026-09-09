# -*- coding: utf-8 -*-
from pathlib import Path
import argparse
import json
import pandas as pd

REQUIRED_COLUMNS = ['Farm_ID', 'State', 'District', 'Crop', 'Season', 'Farm_Area_Hectares', 'Rainfall_mm', 'Avg_Temperature_C', 'Humidity_pct', 'Sunlight_Hours_Day', 'Soil_pH', 'Soil_Moisture_pct', 'Nitrogen_kg_ha', 'Phosphorus_kg_ha', 'Potassium_kg_ha', 'Irrigation_Method', 'Fertilizer_kg_ha', 'Pesticide_Litre_ha', 'Seed_Quality_Score', 'Yield_Tonnes_Ha', 'Production_Tonnes', 'Market_Price_INR_Tonne', 'Total_Cost_INR', 'Revenue_INR', 'Profit_INR', 'Water_Used_m3', 'Water_Efficiency_t_per_1000m3', 'Disease_Pest_Risk_pct']
TEXT_COLUMNS = {'Farm_ID', 'State', 'District', 'Crop', 'Season', 'Irrigation_Method'}
NUMERIC_COLUMNS = [c for c in REQUIRED_COLUMNS if c not in TEXT_COLUMNS]
SEASONS = ['Kharif', 'Rabi', 'Zaid']


def load_and_validate(path):
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df


def quality_report(df):
    return pd.DataFrame({
        'column': df.columns,
        'dtype': [str(df[c].dtype) for c in df.columns],
        'missing_count': [int(df[c].isna().sum()) for c in df.columns],
        'missing_pct': [round(float(df[c].isna().mean() * 100), 3) for c in df.columns],
        'unique_count': [int(df[c].nunique()) for c in df.columns],
    })


def season_summary(df):
    return df.groupby('Season', dropna=False).agg(
        records=('Farm_ID', 'count'), mean_yield_t_ha=('Yield_Tonnes_Ha', 'mean'),
        mean_production_t=('Production_Tonnes', 'mean'), mean_revenue_inr=('Revenue_INR', 'mean'),
        mean_cost_inr=('Total_Cost_INR', 'mean'), mean_profit_inr=('Profit_INR', 'mean'),
        mean_water_efficiency=('Water_Efficiency_t_per_1000m3', 'mean'),
        mean_water_used_m3=('Water_Used_m3', 'mean'),
        mean_disease_pest_risk_pct=('Disease_Pest_Risk_pct', 'mean'),
    ).reset_index()


def irrigation_summary(df):
    return df.groupby('Irrigation_Method', dropna=False).agg(
        records=('Farm_ID', 'count'), mean_yield_t_ha=('Yield_Tonnes_Ha', 'mean'),
        mean_profit_inr=('Profit_INR', 'mean'), mean_water_efficiency=('Water_Efficiency_t_per_1000m3', 'mean'),
        mean_water_used_m3=('Water_Used_m3', 'mean'),
    ).reset_index()


def crop_summary(df):
    return df.groupby('Crop', dropna=False).agg(
        records=('Farm_ID', 'count'), mean_yield_t_ha=('Yield_Tonnes_Ha', 'mean'),
        mean_profit_inr=('Profit_INR', 'mean'), mean_disease_pest_risk_pct=('Disease_Pest_Risk_pct', 'mean'),
    ).reset_index().sort_values('mean_profit_inr', ascending=False)


def correlations(df):
    features = ['Rainfall_mm', 'Avg_Temperature_C', 'Soil_Moisture_pct', 'Fertilizer_kg_ha', 'Seed_Quality_Score', 'Water_Efficiency_t_per_1000m3']
    return df[features + ['Yield_Tonnes_Ha', 'Profit_INR']].corr().loc[features, ['Yield_Tonnes_Ha', 'Profit_INR']].reset_index().rename(columns={'index': 'feature'})


def save_charts(df, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import seaborn as sns

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style='whitegrid')
    summary = season_summary(df)
    order = [season for season in SEASONS if season in summary['Season'].values]
    for metric, title, filename, color in [
        ('mean_yield_t_ha', 'Average Yield by Season', 'yield_by_season.png', '#2f855a'),
        ('mean_profit_inr', 'Average Profit by Season', 'profit_by_season.png', '#b7791f'),
    ]:
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.barplot(data=summary, x='Season', y=metric, order=order, color=color, ax=ax)
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out / filename, dpi=160)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df, x='Season', y='Profit_INR', order=order, ax=ax, color='#90cdf4')
    ax.axhline(0, color='black', lw=.8)
    ax.set_title('Profit Distribution by Season')
    fig.tight_layout()
    fig.savefig(out / 'profit_distribution_by_season.png', dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(df[['Rainfall_mm', 'Avg_Temperature_C', 'Soil_Moisture_pct', 'Fertilizer_kg_ha', 'Seed_Quality_Score', 'Yield_Tonnes_Ha', 'Profit_INR']].corr(), annot=True, fmt='.2f', cmap='RdYlGn', center=0, ax=ax)
    ax.set_title('Correlation Heatmap')
    fig.tight_layout()
    fig.savefig(out / 'correlation_heatmap.png', dpi=160)
    plt.close(fig)


def run(input_path, output_dir):
    df = load_and_validate(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    quality_report(df).to_csv(out / 'data_quality_report.csv', index=False)
    season_summary(df).to_csv(out / 'season_summary.csv', index=False)
    irrigation_summary(df).to_csv(out / 'irrigation_summary.csv', index=False)
    crop_summary(df).to_csv(out / 'crop_summary.csv', index=False)
    correlations(df).to_csv(out / 'correlations.csv', index=False)
    df.drop_duplicates('Farm_ID').to_csv(out / 'cleaned_dataset.csv', index=False)
    try:
        save_charts(df, out)
        charts_status = 'generated'
    except Exception as exc:
        (out / 'charts_skipped.txt').write_text(f'Charts skipped: {type(exc).__name__}: {exc}\nInstall matplotlib and seaborn or use a headless backend.', encoding='utf-8')
        charts_status = 'skipped'
    result = {
        'rows': int(len(df)), 'columns': int(len(df.columns)),
        'duplicate_farm_ids': int(df.Farm_ID.duplicated().sum()),
        'negative_profit_rows': int((df.Profit_INR < 0).sum()),
        'negative_profit_pct': round(float((df.Profit_INR < 0).mean() * 100), 2),
        'seasons': sorted(df.Season.dropna().unique().tolist()),
        'crops': sorted(df.Crop.dropna().unique().tolist()),
        'irrigation_methods': sorted(df.Irrigation_Method.dropna().unique().tolist()),
        'charts': charts_status,
    }
    (out / 'run_summary.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', default='outputs')
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output), indent=2))
