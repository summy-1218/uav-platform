import streamlit as st
import pandas as pd
from PIL import Image
import os

st.set_page_config(
    page_title="无人机数字化资源平台",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚁 无人机数字化资源平台")

st.markdown("""
### 欢迎使用
本项目是一个针对《无人机系统设计》课程的数字化资源平台，集成机型库、子系统库、案例库及数据分析功能。
""")

# Load Hero Image
hero_path = os.path.join(os.path.dirname(__file__), "assets/hero.jpg")
if os.path.exists(hero_path):
    image = Image.open(hero_path)
    st.image(image, use_container_width=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✈️ 机型库", use_container_width=True, key="btn_uav"):
        st.switch_page("pages/1_✈️_机型库.py")
    st.caption("收录固定翼、多旋翼、VTOL等多种构型的典型无人机数据。")

with col2:
    if st.button("🔧 子系统库", use_container_width=True, key="btn_subsystem"):
        st.switch_page("pages/2_🔧_子系统库.py")
    st.caption("包含地面站、飞控、吊舱、发动机等关键子系统数据。")

with col3:
    if st.button("📊 统计分析", use_container_width=True, key="btn_stats"):
        st.switch_page("pages/4_📊_统计分析.py")
    st.caption("支持任意两项参数的散点图绘制与曲线拟合。")

st.divider()

st.markdown("### 快速开始")
st.markdown("""
请从左侧侧边栏选择相应的功能模块：
- **机型库**: 浏览和查询无人机型号详细参数。
- **子系统库**: 查询关键部件规格。
- **案例库**: 阅读经典机型的设计分析文档。
- **统计分析**: 进行参数相关性探索。
- **数据管理**: 下载模板并导入新数据 (Excel)。
""")
