import streamlit as st
import pandas as pd
from utils import load_data, get_image_path
import os

st.set_page_config(page_title="子系统库", page_icon="🔧", layout="wide")

st.title("🔧 无人机子系统库")

df = load_data("subsystems.json")

if df.empty:
    st.warning("暂无数据，请前往【数据管理】页面导入数据。")
else:
    # Filters
    st.sidebar.header("筛选条件")
    categories = df["category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect("选择类别", categories, default=categories)
    
    filtered_df = df[df["category"].isin(selected_categories)]
    
    # Display Grid
    st.markdown(f"共找到 {len(filtered_df)} 个子系统")
    
    for _, row in filtered_df.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([1, 4])
            with c1:
                image_path = get_image_path(row.get("image_url"))
                if image_path:
                    st.image(image_path, use_container_width=True)
                else:
                    st.markdown("📷 暂无图片")
            with c2:
                st.subheader(f"{row['name']}")
                st.caption(f"**厂商**: {row['manufacturer']} | **类别**: {row['category']}")
                st.write(row["description"])
                
                # Show key specs
                if isinstance(row.get("key_specs"), dict):
                    specs = row["key_specs"]
                    cols = st.columns(len(specs)) if specs else []
                    for i, (k, v) in enumerate(specs.items()):
                        if i < 4: # Limit to 4 specs display
                            cols[i].metric(k, v)
