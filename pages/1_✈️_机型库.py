import streamlit as st
import pandas as pd
from utils import load_data, save_data, get_image_path, load_custom_params, add_custom_param, delete_custom_param, ASSETS_DIR
import os
from datetime import datetime

st.set_page_config(page_title="机型库", page_icon="✈️", layout="wide")

st.title("✈️ 无人机机型库")

df = load_data("uav_models.json")

# Mode selection
mode = st.radio("选择操作模式", ["浏览数据", "添加机型", "删除机型", "添加参数", "修改机型"], horizontal=True)

if mode == "删除机型" and not df.empty:
    st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
    model_to_delete = st.selectbox("选择要删除的机型", df["name"].unique())
    if st.button("🗑️ 确认删除", type="primary"):
        try:
            # 重新加载数据确保获取最新状态
            df = load_data("uav_models.json")
            # 过滤掉要删除的机型
            df = df[df["name"] != model_to_delete].reset_index(drop=True)
            # 保存到JSON文件
            save_data("uav_models.json", df)
            st.success(f"已删除机型: {model_to_delete}")
            # 清除session state避免缓存问题
            if 'df' in st.session_state:
                del st.session_state['df']
            # 重新加载页面
            st.rerun()
        except Exception as e:
            st.error(f"删除失败: {str(e)}")

if mode == "添加机型":
    st.subheader("➕ 添加新机型")

    # 加载自定义参数
    custom_params = load_custom_params()

    with st.form("add_uav_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("型号名称*", value="").strip()
            manufacturer = st.text_input("厂商*", value="").strip()
            type_ = st.selectbox("类型*", ["Fixed-Wing", "Multi-Rotor", "VTOL", "Helicopter", "Other"])

            # 图片输入：支持文件上传或URL输入
            st.markdown("#### 图片设置")
            uploaded_image = st.file_uploader("上传本地图片", type=["jpg", "jpeg", "png", "gif", "webp"], key="add_upload_image")
            image_url_input = st.text_input("或输入图片URL/路径 (可选)", value="", help="支持网络URL或本地文件路径，如: uav1.jpg 或 https://...")

            # 如果上传了文件，使用文件名作为路径
            if uploaded_image:
                image_url = uploaded_image.name
            else:
                image_url = image_url_input

        with col2:
            purpose_input = st.text_input("主要用途 (用逗号分隔)", value="", placeholder="例如: Mapping, Survey").strip()
            description = st.text_area("描述", value="", height=100)

        st.divider()

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### 外形参数")
            length_m = st.number_input("机长 (m)", value=0.0, min_value=0.0, step=0.1)
            wingspan_m = st.number_input("翼展 (m)", value=0.0, min_value=0.0, step=0.1)
            height_m = st.number_input("机高 (m)", value=0.0, min_value=0.0, step=0.1)

        with col4:
            st.markdown("#### 重量参数")
            mtow_kg = st.number_input("最大起飞重量", value=0.0, min_value=0.0, step=0.1)
            empty_weight_kg = st.number_input("空重", value=0.0, min_value=0.0, step=0.1)
            max_payload_kg = st.number_input("最大载荷", value=0.0, min_value=0.0, step=0.1)

        st.divider()

        col5, col6 = st.columns(2)
        with col5:
            st.markdown("#### 性能参数")
            max_speed_kmh = st.number_input("最大速度", value=0.0, min_value=0.0, step=1.0)
            cruise_speed_kmh = st.number_input("巡航速度", value=0.0, min_value=0.0, step=1.0)

        with col6:
            range_km = st.number_input("航程", value=0.0, min_value=0.0, step=1.0)
            endurance_min = st.number_input("续航时间", value=0, min_value=0, step=1)
            ceiling_m = st.number_input("升限", value=0, min_value=0, step=10)

        # 自定义参数部分
        if custom_params:
            st.divider()
            st.markdown("#### 自定义参数")

            # 计算需要的列数，每行显示2个参数
            num_params = len(custom_params)
            num_cols = 2
            num_rows = (num_params + num_cols - 1) // num_cols

            custom_param_values = {}
            for row in range(num_rows):
                cols = st.columns(num_cols)
                for col_idx in range(num_cols):
                    param_idx = row * num_cols + col_idx
                    if param_idx < num_params:
                        param = custom_params[param_idx]
                        with cols[col_idx]:
                            param_value = st.number_input(
                                f"{param['name']} ({param['unit']})",
                                value=0.0,
                                min_value=0.0,
                                step=0.1,
                                key=f"custom_{param_idx}"
                            )
                            custom_param_values[param['name']] = {
                                "value": param_value,
                                "unit": param['unit']
                            }

        submitted = st.form_submit_button("✅ 添加机型", type="primary")

        if submitted:
            if not name or not manufacturer:
                st.error("请填写必填项（型号名称和厂商）")
            else:
                # Parse purpose list
                purpose = [p.strip() for p in purpose_input.split(",") if p.strip()] if purpose_input else []

                # 处理上传的图片文件
                if uploaded_image:
                    # 确保assets目录存在
                    if not os.path.exists(ASSETS_DIR):
                        os.makedirs(ASSETS_DIR, exist_ok=True)
                    # 保存上传的文件到assets目录
                    image_save_path = os.path.join(ASSETS_DIR, uploaded_image.name)
                    with open(image_save_path, 'wb') as f:
                        f.write(uploaded_image.getbuffer())
                    image_url = uploaded_image.name

                # Create new model
                new_model = {
                    "id": f"uav-{int(datetime.now().timestamp())}",
                    "name": name,
                    "manufacturer": manufacturer,
                    "type": type_,
                    "image_url": image_url if image_url else None,
                    "description": description if description else "",
                    "length_m": length_m,
                    "wingspan_m": wingspan_m,
                    "height_m": height_m,
                    "mtow_kg": mtow_kg,
                    "empty_weight_kg": empty_weight_kg,
                    "max_payload_kg": max_payload_kg,
                    "max_speed_kmh": max_speed_kmh,
                    "cruise_speed_kmh": cruise_speed_kmh,
                    "range_km": range_km,
                    "endurance_min": int(endurance_min),
                    "ceiling_m": ceiling_m,
                    "purpose": purpose,
                    "custom_params": custom_param_values if custom_params else {}
                }

                # Append to existing data
                df = pd.concat([df, pd.DataFrame([new_model])], ignore_index=True)
                save_data("uav_models.json", df)
                st.success(f"成功添加机型: {name}")
                st.rerun()

if mode == "修改机型":
    st.subheader("✏️ 修改机型")

    if df.empty:
        st.warning("暂无机型数据可修改")
        st.stop()

    # 选择要修改的机型
    model_to_edit = st.selectbox("选择要修改的机型", df["name"].unique())

    if model_to_edit:
        # 获取当前机型数据
        current_model = df[df["name"] == model_to_edit].iloc[0].to_dict()

        # 加载自定义参数
        custom_params = load_custom_params()

        with st.form("edit_uav_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("型号名称*", value=current_model.get("name", ""), key="edit_name").strip()
                manufacturer = st.text_input("厂商*", value=current_model.get("manufacturer", ""), key="edit_manufacturer").strip()
                type_ = st.selectbox("类型*", ["Fixed-Wing", "Multi-Rotor", "VTOL", "Helicopter", "Other"],
                                   index=["Fixed-Wing", "Multi-Rotor", "VTOL", "Helicopter", "Other"].index(current_model.get("type", "Fixed-Wing")),
                                   key="edit_type")

                # 图片输入：支持文件上传或URL输入
                st.markdown("#### 图片设置")
                uploaded_image = st.file_uploader("上传本地图片", type=["jpg", "jpeg", "png", "gif", "webp"], key="edit_upload_image")
                image_url_input = st.text_input("或输入图片URL/路径 (可选)", value=current_model.get("image_url", ""),
                                              key="edit_image_url", help="支持网络URL或本地文件路径，如: uav1.jpg 或 https://...")

                # 如果上传了文件，使用文件名作为路径
                if uploaded_image:
                    image_url = uploaded_image.name
                else:
                    image_url = image_url_input

            with col2:
                purpose = current_model.get("purpose", [])
                purpose_input = st.text_input("主要用途 (用逗号分隔)",
                                            value=", ".join(purpose) if isinstance(purpose, list) else str(purpose),
                                            key="edit_purpose").strip()
                description = st.text_area("描述", value=current_model.get("description", ""),
                                      height=100, key="edit_description")

            st.divider()

            col3, col4 = st.columns(2)
            with col3:
                st.markdown("#### 外形参数")
                length_m = st.number_input("机长 (m)", value=float(current_model.get("length_m", 0.0)),
                                        min_value=0.0, step=0.1, key="edit_length_m")
                wingspan_m = st.number_input("翼展 (m)", value=float(current_model.get("wingspan_m", 0.0)),
                                          min_value=0.0, step=0.1, key="edit_wingspan_m")
                height_m = st.number_input("机高 (m)", value=float(current_model.get("height_m", 0.0)),
                                         min_value=0.0, step=0.1, key="edit_height_m")

            with col4:
                st.markdown("#### 重量参数")
                mtow_kg = st.number_input("最大起飞重量", value=float(current_model.get("mtow_kg", 0.0)),
                                         min_value=0.0, step=0.1, key="edit_mtow_kg")
                empty_weight_kg = st.number_input("空重", value=float(current_model.get("empty_weight_kg", 0.0)),
                                            min_value=0.0, step=0.1, key="edit_empty_weight_kg")
                max_payload_kg = st.number_input("最大载荷", value=float(current_model.get("max_payload_kg", 0.0)),
                                            min_value=0.0, step=0.1, key="edit_max_payload_kg")

            st.divider()

            col5, col6 = st.columns(2)
            with col5:
                st.markdown("#### 性能参数")
                max_speed_kmh = st.number_input("最大速度", value=float(current_model.get("max_speed_kmh", 0.0)),
                                             min_value=0.0, step=1.0, key="edit_max_speed_kmh")
                cruise_speed_kmh = st.number_input("巡航速度", value=float(current_model.get("cruise_speed_kmh", 0.0)),
                                               min_value=0.0, step=1.0, key="edit_cruise_speed_kmh")

            with col6:
                range_km = st.number_input("航程", value=float(current_model.get("range_km", 0.0)),
                                       min_value=0.0, step=1.0, key="edit_range_km")
                endurance_min = st.number_input("续航时间", value=int(current_model.get("endurance_min", 0)),
                                            min_value=0, step=1, key="edit_endurance_min")
                ceiling_m = st.number_input("升限", value=int(current_model.get("ceiling_m", 0)),
                                         min_value=0, step=10, key="edit_ceiling_m")

            # 自定义参数编辑
            if custom_params:
                st.divider()
                st.markdown("#### 自定义参数")

                # 获取现有自定义参数值，确保是字典格式
                existing_custom_params = current_model.get("custom_params", {})
                if not isinstance(existing_custom_params, dict):
                    existing_custom_params = {}

                # 计算需要的列数，每行显示2个参数
                num_params = len(custom_params)
                num_cols = 2
                num_rows = (num_params + num_cols - 1) // num_cols

                custom_param_values = {}
                for row in range(num_rows):
                    cols = st.columns(num_cols)
                    for col_idx in range(num_cols):
                        param_idx = row * num_cols + col_idx
                        if param_idx < num_params:
                            param = custom_params[param_idx]
                            # 获取现有值，如果没有则使用0
                            existing_value = 0.0
                            if param['name'] in existing_custom_params:
                                existing_value = existing_custom_params[param['name']].get('value', 0.0)

                            with cols[col_idx]:
                                param_value = st.number_input(
                                    f"{param['name']} ({param['unit']})",
                                    value=float(existing_value),
                                    min_value=0.0,
                                    step=0.1,
                                    key=f"edit_custom_{param_idx}"
                                )
                                custom_param_values[param['name']] = {
                                    "value": param_value,
                                    "unit": param['unit']
                                }

            submitted = st.form_submit_button("💾 保存修改", type="primary")

            if submitted:
                if not name or not manufacturer:
                    st.error("请填写必填项（型号名称和厂商）")
                else:
                    # Parse purpose list
                    purpose = [p.strip() for p in purpose_input.split(",") if p.strip()] if purpose_input else []

                    # 处理上传的图片文件
                    if uploaded_image:
                        # 确保assets目录存在
                        if not os.path.exists(ASSETS_DIR):
                            os.makedirs(ASSETS_DIR, exist_ok=True)
                        # 保存上传的文件到assets目录
                        image_save_path = os.path.join(ASSETS_DIR, uploaded_image.name)
                        with open(image_save_path, 'wb') as f:
                            f.write(uploaded_image.getbuffer())
                        image_url = uploaded_image.name

                    # Updated model
                    updated_model = {
                        "id": current_model.get("id", f"uav-{int(datetime.now().timestamp())}"),
                        "name": name,
                        "manufacturer": manufacturer,
                        "type": type_,
                        "image_url": image_url if image_url else None,
                        "description": description if description else "",
                        "length_m": length_m,
                        "wingspan_m": wingspan_m,
                        "height_m": height_m,
                        "mtow_kg": mtow_kg,
                        "empty_weight_kg": empty_weight_kg,
                        "max_payload_kg": max_payload_kg,
                        "max_speed_kmh": max_speed_kmh,
                        "cruise_speed_kmh": cruise_speed_kmh,
                        "range_km": range_km,
                        "endurance_min": int(endurance_min),
                        "ceiling_m": ceiling_m,
                        "purpose": purpose,
                        "custom_params": custom_param_values if custom_params else {}
                    }

                    # Update existing data - 删除旧记录并添加新记录
                    df = df[df["name"] != model_to_edit].reset_index(drop=True)
                    df = pd.concat([df, pd.DataFrame([updated_model])], ignore_index=True)
                    save_data("uav_models.json", df)
                    st.success(f"成功修改机型: {name}")
                    st.rerun()

if mode == "添加参数":
    st.subheader("➕ 管理参数")

    # 标准参数列表
    st.markdown("#### 标准参数")
    standard_params = [
        {"name": "机长", "unit": "m", "category": "外形参数"},
        {"name": "翼展", "unit": "m", "category": "外形参数"},
        {"name": "机高", "unit": "m", "category": "外形参数"},
        {"name": "最大起飞重量", "unit": "kg", "category": "重量参数"},
        {"name": "空重", "unit": "kg", "category": "重量参数"},
        {"name": "最大载荷", "unit": "kg", "category": "重量参数"},
        {"name": "最大速度", "unit": "km/h", "category": "性能参数"},
        {"name": "巡航速度", "unit": "km/h", "category": "性能参数"},
        {"name": "航程", "unit": "km", "category": "性能参数"},
        {"name": "续航时间", "unit": "min", "category": "性能参数"},
        {"name": "升限", "unit": "m", "category": "性能参数"}
    ]

    standard_params_df = pd.DataFrame(standard_params)
    st.dataframe(standard_params_df[['name', 'unit', 'category']], use_container_width=True, column_config={
        'name': '参数名称',
        'unit': '单位',
        'category': '参数类别'
    })

    # 自定义参数
    st.divider()
    st.markdown("#### 自定义参数")

    custom_params = load_custom_params()

    if custom_params:
        custom_params_df = pd.DataFrame(custom_params)
        st.dataframe(custom_params_df[['name', 'unit']], use_container_width=True, column_config={
            'name': '参数名称',
            'unit': '单位'
        })

        # 删除参数功能
        st.divider()
        st.markdown("#### 删除自定义参数")
        param_to_delete = st.selectbox("选择要删除的参数", [p['name'] for p in custom_params] if custom_params else [])
        if st.button("🗑️ 删除参数", type="primary", key="delete_param"):
            if param_to_delete:
                delete_custom_param(param_to_delete)
                st.success(f"已删除参数: {param_to_delete}")
                st.rerun()
    else:
        st.info("暂无自定义参数，请添加新参数。")

    # 添加新参数表单
    st.divider()
    st.markdown("#### 添加新参数")

    with st.form("add_param_form"):
        col1, col2 = st.columns(2)
        with col1:
            param_name = st.text_input("参数名称*", placeholder="例如: 最大扭矩", value="").strip()
        with col2:
            param_unit = st.text_input("单位*", placeholder="例如: N·m", value="").strip()

        st.info("💡 提示：添加的参数将在添加/修改机型时可用，可以为每个机型填写对应的数值。标准参数由系统内置，不可删除。")

        submitted = st.form_submit_button("✅ 添加参数", type="primary")

        if submitted:
            if not param_name or not param_unit:
                st.error("请填写参数名称和单位")
            else:
                success, msg = add_custom_param(param_name, param_unit)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

if mode == "浏览数据":
    if df.empty:
        st.warning("暂无数据，请前往【数据管理】页面导入数据或使用【添加机型】功能。")
        st.stop()

    # Filters
    st.sidebar.header("筛选条件")

    # Type Filter
    all_types = df["type"].dropna().unique().tolist()
    selected_types = st.sidebar.multiselect("选择类型", all_types, default=all_types)

    # Manufacturer Filter
    all_manufacturers = df["manufacturer"].dropna().unique().tolist()
    selected_manufacturers = st.sidebar.multiselect("选择厂商", all_manufacturers, default=all_manufacturers)

    # Apply Filters
    filtered_df = df[
        (df["type"].isin(selected_types)) &
        (df["manufacturer"].isin(selected_manufacturers))
    ]

    st.metric("收录机型数量", len(filtered_df))

    # Display Dataframe
    st.dataframe(
        filtered_df[["name", "manufacturer", "type", "mtow_kg", "endurance_min", "max_speed_kmh", "purpose"]],
        use_container_width=True,
        column_config={
            "name": "型号名称",
            "manufacturer": "厂商",
            "type": "类型",
            "mtow_kg": st.column_config.NumberColumn("最大起飞重量 (kg)", format="%.1f"),
            "endurance_min": st.column_config.NumberColumn("续航时间 (min)", format="%d"),
            "max_speed_kmh": st.column_config.NumberColumn("最大速度 (km/h)", format="%d"),
            "purpose": "主要用途"
        }
    )

    st.divider()

    # Detail View
    st.subheader("🔍 机型详情")
    selected_model_name = st.selectbox("选择要查看详情的机型", filtered_df["name"].unique())

    if selected_model_name:
        model = filtered_df[filtered_df["name"] == selected_model_name].iloc[0]

        c1, c2 = st.columns([1, 2])

        with c1:
            image_path = get_image_path(model.get("image_url"))
            if image_path:
                st.image(image_path, caption=model["name"], use_container_width=True)
            else:
                st.info("暂无图片")

        with c2:
            st.markdown(f"### {model['name']}")
            st.caption(f"**厂商**: {model['manufacturer']} | **类型**: {model['type']}")
            st.markdown(f"**描述**: {model['description']}")

            t1, t2, t3 = st.tabs(["外形参数", "重量参数", "性能参数"])

            with t1:
                st.write(f"- **机长**: {model.get('length_m', 0)} m")
                st.write(f"- **翼展**: {model.get('wingspan_m', 0)} m")
                st.write(f"- **机高**: {model.get('height_m', 0)} m")

            with t2:
                st.write(f"- **最大起飞重量**: {model.get('mtow_kg', 0)} kg")
                st.write(f"- **空重**: {model.get('empty_weight_kg', 0)} kg")
                st.write(f"- **最大载荷**: {model.get('max_payload_kg', 0)} kg")

            with t3:
                st.write(f"- **最大速度**: {model.get('max_speed_kmh', 0)} km/h")
                st.write(f"- **巡航速度**: {model.get('cruise_speed_kmh', 0)} km/h")
                st.write(f"- **航程**: {model.get('range_km', 0)} km")
                st.write(f"- **续航时间**: {model.get('endurance_min', 0)} min")
                st.write(f"- **升限**: {model.get('ceiling_m', 0)} m")

            # 显示自定义参数
            custom_params_data = model.get('custom_params', {})
            if custom_params_data:
                st.divider()
                st.markdown("#### 自定义参数")
                for param_name, param_info in custom_params_data.items():
                    value = param_info.get('value', 0)
                    unit = param_info.get('unit', '')
                    st.write(f"- **{param_name}**: {value} {unit}")
