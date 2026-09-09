from pathlib import Path
import streamlit as st
from src.analysis import load_and_validate,season_summary,irrigation_summary,crop_summary
st.set_page_config(page_title='Seasonal Agriculture Performance',layout='wide')
st.title('Seasonal Agriculture Performance Analysis')
st.caption('Badal Chaudhary · STU6a30b8115dd5c1781577745')
path=st.sidebar.text_input('CSV path','data/seasonal_agriculture_performance_dataset.csv')
if not Path(path).exists(): path='data/sample/seasonal_agriculture_performance_sample.csv'; st.warning('Full dataset not found. Showing smoke-test sample; add the supplied CSV for final results.')
try: df=load_and_validate(path)
except Exception as e: st.error(str(e)); st.stop()
with st.sidebar:
    seasons=st.multiselect('Season',sorted(df.Season.dropna().unique()),default=sorted(df.Season.dropna().unique())); crops=st.multiselect('Crop',sorted(df.Crop.dropna().unique()),default=sorted(df.Crop.dropna().unique())); irrig=st.multiselect('Irrigation',sorted(df.Irrigation_Method.dropna().unique()),default=sorted(df.Irrigation_Method.dropna().unique()))
view=df[df.Season.isin(seasons)&df.Crop.isin(crops)&df.Irrigation_Method.isin(irrig)]
a,b,c,d=st.columns(4); a.metric('Records',f'{len(view):,}'); b.metric('Mean yield (t/ha)',f'{view.Yield_Tonnes_Ha.mean():.2f}'); c.metric('Mean profit (INR)',f'{view.Profit_INR.mean():,.0f}'); d.metric('Negative-profit share',f'{(view.Profit_INR.lt(0).mean()*100):.1f}%')
st.subheader('Season comparison'); st.dataframe(season_summary(view).round(2),use_container_width=True)
st.subheader('Irrigation comparison'); st.dataframe(irrigation_summary(view).round(2),use_container_width=True)
st.subheader('Crop comparison'); st.dataframe(crop_summary(view).round(2),use_container_width=True)
st.bar_chart(view.groupby('Season').Profit_INR.mean())
