import streamlit as st
import os
from utils import import_excel_data

st.set_page_config(page_title="数据管理", page_icon="⚙️", layout="wide")

st.title("⚙️ 数据管理")

st.markdown("""
在此页面，您可以下载标准数据模板，并在本地编辑后上传，以更新数据库。
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 下载模板")
    st.markdown("下载 Excel 模板文件 `import_template.xlsx`。")
    
    template_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/import_template.xlsx")
    if os.path.exists(template_path):
        with open(template_path, "rb") as f:
            st.download_button(
                label="📥 下载 Excel 模板",
                data=f,
                file_name="import_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error("模板文件丢失。")

with col2:
    st.subheader("2. 上传数据")
    st.markdown("上传填写好的 Excel 文件以更新数据库。")
    
    uploaded_file = st.file_uploader("选择 Excel 文件 (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        if st.button("开始导入", type="primary"):
            with st.spinner("正在处理数据..."):
                success, msg = import_excel_data(uploaded_file)
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)

st.divider()

st.info("""
**💡 说明**:
- 系统会根据名称自动匹配现有数据。
- 如果名称已存在，将更新现有记录；如果不存在，将创建新记录。
- 请勿修改模板中的表头名称。
""")
