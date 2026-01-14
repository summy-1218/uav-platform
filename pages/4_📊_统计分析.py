import streamlit as st
import pandas as pd
import numpy as np
from utils import load_data, load_custom_params
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import os
import json

st.set_page_config(page_title="统计分析", page_icon="📊", layout="wide")

st.title("📊 统计与拟合分析")

# 添加选项卡
tab1, tab2 = st.tabs(["回归分析", "计算器"])

with tab1:
    df = load_data("uav_models.json")

    if df.empty:
        st.warning("请先导入数据。")
    else:
        # 加载自定义参数
        custom_params = load_custom_params()
        custom_param_cols = []
        custom_param_labels = {}

        # 提取自定义参数数据
        for _, row in df.iterrows():
            if isinstance(row.get('custom_params'), dict):
                for param_name, param_data in row['custom_params'].items():
                    if param_name not in custom_param_cols:
                        custom_param_cols.append(param_name)
                        # 从custom_params.json获取单位
                        unit = "无单位"
                        for cp in custom_params:
                            if cp.get('name') == param_name:
                                unit = cp.get('unit', '无单位')
                                break
                        custom_param_labels[param_name] = f"{param_name} ({unit})"

        # 展开自定义参数为单独列
        for col in custom_param_cols:
            df[col] = df.apply(lambda row: row.get('custom_params', {}).get(col, {}).get('value', np.nan) if isinstance(row.get('custom_params'), dict) else np.nan, axis=1)

        # 合并所有可用参数
        numeric_cols = ["mtow_kg", "max_payload_kg", "endurance_min", "range_km", "max_speed_kmh", "length_m", "wingspan_m"] + custom_param_cols
        labels = {
            "mtow_kg": "最大起飞重量 (kg)",
            "max_payload_kg": "最大载荷 (kg)",
            "endurance_min": "续航时间 (min)",
            "range_km": "航程 (km)",
            "max_speed_kmh": "最大速度 (km/h)",
            "length_m": "机长 (m)",
            "wingspan_m": "翼展 (m)"
        }
        labels.update(custom_param_labels)

        # 1. Configuration
        with st.container(border=True):
            st.subheader("🛠 参数配置")

            # 数据选择方式
            st.markdown("#### 数据选择")
            data_selection_mode = st.radio(
                "选择数据范围",
                ["按机型类型筛选", "自定义选择机型"],
                horizontal=True
            )

            if data_selection_mode == "按机型类型筛选":
                selected_types = st.multiselect(
                    "选择机型类型（留空表示全选）",
                    df["type"].unique(),
                    default=list(df["type"].unique()) if len(df["type"].unique()) > 0 else None
                )
                if not selected_types:
                    selected_df = df.copy()
                else:
                    selected_df = df[df["type"].isin(selected_types)].copy()
            else:
                available_models = df["name"].dropna().unique()
                selected_models = st.multiselect(
                    "选择要分析的机型",
                    available_models,
                    default=list(available_models) if len(available_models) > 0 else None
                )
                if not selected_models:
                    selected_df = df.copy()
                else:
                    selected_df = df[df["name"].isin(selected_models)].copy()

            st.divider()
            st.markdown("#### 回归分析配置")
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                x_axis = st.selectbox("X 轴参数", numeric_cols, index=0, format_func=lambda x: labels.get(x, x))
            with c2:
                y_axis = st.selectbox("Y 轴参数", numeric_cols, index=2, format_func=lambda x: labels.get(x, x))
            with c3:
                model_type = st.selectbox("回归模型", ["线性回归", "多项式回归 (2阶)", "多项式回归 (3阶)", "随机森林"])
            with c4:
                show_trendline = st.checkbox("显示拟合曲线", value=True)

            # 显示选中的数据信息
            if data_selection_mode == "按机型类型筛选":
                st.info(f"当前分析 {len(selected_df)} 个机型数据")
                if selected_types:
                    st.caption(f"已选择类型: {', '.join(selected_types)}")
            else:
                st.info(f"当前分析 {len(selected_df)} 个机型数据")
                if selected_models:
                    st.caption(f"已选择机型: {', '.join(selected_models)}")

        # 2. Data Prep
        chart_df = selected_df[[x_axis, y_axis, "name", "type"]].dropna()
        chart_df = chart_df[(chart_df[x_axis] > 0) & (chart_df[y_axis] > 0)]

        if chart_df.empty:
            st.error("所选参数在当前数据集中没有有效数值，无法绘图。")
        else:
            # 3. Plotting
            fig = px.scatter(
                chart_df,
                x=x_axis,
                y=y_axis,
                color="type",
                hover_name="name",
                labels=labels,
                title=f"{labels[y_axis]} vs {labels[x_axis]} ({model_type})"
            )

            # 添加回归拟合线
            if show_trendline and len(chart_df) > 1:
                X = chart_df[[x_axis]].values
                y = chart_df[y_axis].values

                if model_type == "线性回归":
                    model = LinearRegression()
                    model.fit(X, y)
                    x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
                    y_line = model.predict(x_line)
                    curve_name = "线性回归"
                    curve_color = "red"

                elif model_type == "多项式回归 (2阶)":
                    model = Pipeline([
                        ('poly', PolynomialFeatures(degree=2)),
                        ('linear', LinearRegression())
                    ])
                    model.fit(X, y)
                    x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
                    y_line = model.predict(x_line)
                    curve_name = "多项式回归 (2阶)"
                    curve_color = "blue"

                elif model_type == "多项式回归 (3阶)":
                    model = Pipeline([
                        ('poly', PolynomialFeatures(degree=3)),
                        ('linear', LinearRegression())
                    ])
                    model.fit(X, y)
                    x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
                    y_line = model.predict(x_line)
                    curve_name = "多项式回归 (3阶)"
                    curve_color = "green"

                elif model_type == "随机森林":
                    model = RandomForestRegressor(n_estimators=100, random_state=42)
                    model.fit(X, y)
                    x_line = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
                    y_line = model.predict(x_line)
                    curve_name = "随机森林"
                    curve_color = "purple"

                # 添加拟合线到图表
                fig.add_scatter(
                    x=x_line.flatten(),
                    y=y_line,
                    mode='lines',
                    name=curve_name,
                    line=dict(color=curve_color, width=2),
                    hoverinfo='skip'
                )

            st.plotly_chart(fig, use_container_width=True)

            # 4. Regression Stats
            if show_trendline and len(chart_df) > 1:
                y_pred = model.predict(X)
                r2 = r2_score(y, y_pred)
                mse = mean_squared_error(y, y_pred)
                rmse = np.sqrt(mse)

                st.subheader("📈 模型性能分析")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("R² (决定系数)", f"{r2:.4f}", help="越接近 1 表示拟合越好")
                with c2:
                    st.metric("均方误差 (MSE)", f"{mse:.4f}")
                with c3:
                    st.metric("均方根误差 (RMSE)", f"{rmse:.4f}")

                if model_type == "线性回归":
                    coef = model.coef_[0]
                    intercept = model.intercept_
                    st.info(f"""
                    **回归方程**: y = {coef:.4f}x + {intercept:.4f}
                    """)
                elif model_type.startswith("多项式回归"):
                    st.info("多项式回归模型已拟合，请参考图表中的拟合曲线。")
                elif model_type == "随机森林":
                    st.info("随机森林为非线性模型，使用集成学习方法预测。")

with tab2:
    st.subheader("🧮 无人机性能计算器")

    # 创建计算器选项卡
    calc_tab1, calc_tab2, calc_tab3 = st.tabs(["续航时间计算", "航程计算", "性能对比"])

    with calc_tab1:
        st.markdown("### 续航时间计算")
        st.info("基于燃油/电池容量和油耗计算续航时间")

        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                fuel_capacity = st.number_input("燃油/电池容量 (L 或 kWh)", min_value=0.0, value=100.0, step=1.0, key="calc_fuel")
                fuel_consumption = st.number_input("平均油耗/能耗 (L/h 或 kW)", min_value=0.0, value=20.0, step=0.5, key="calc_consumption")
            with c2:
                safety_factor = st.slider("安全系数 (保留燃油比例)", 0.0, 0.5, 0.15, 0.05, key="calc_safety")

            if st.button("计算续航时间", type="primary", key="calc_endurance"):
                if fuel_consumption > 0:
                    usable_fuel = fuel_capacity * (1 - safety_factor)
                    endurance_hours = usable_fuel / fuel_consumption
                    endurance_min = endurance_hours * 60

                    st.success(f"""
                    **计算结果**:
                    - 可用燃油/能量: {usable_fuel:.2f} L 或 kWh
                    - 续航时间: {endurance_hours:.2f} 小时 ({endurance_min:.1f} 分钟)
                    """)
                else:
                    st.error("油耗/能耗必须大于 0")

    with calc_tab2:
        st.markdown("### 航程计算")
        st.info("基于巡航速度和续航时间计算航程")

        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                cruise_speed = st.number_input("巡航速度 (km/h)", min_value=0.0, value=100.0, step=5.0, key="calc_speed")
                endurance_time = st.number_input("续航时间 (小时)", min_value=0.0, value=5.0, step=0.5, key="calc_time")
            with c2:
                wind_effect = st.slider("风速影响 (km/h, 负值为顺风)", -20.0, 20.0, 0.0, 2.0, key="calc_wind")

            if st.button("计算航程", type="primary", key="calc_range"):
                effective_speed = cruise_speed + wind_effect
                if effective_speed > 0 and endurance_time > 0:
                    range_km = effective_speed * endurance_time
                    round_trip = range_km * 0.9  # 考虑返航

                    st.success(f"""
                    **计算结果**:
                    - 有效巡航速度: {effective_speed:.2f} km/h
                    - 单程航程: {range_km:.2f} km
                    - 往返航程 (含安全余量): {round_trip:.2f} km
                    """)
                else:
                    st.error("速度和时间必须大于 0")

    with calc_tab3:
        st.markdown("### 性能参数对比")
        st.info("比较不同无人机的关键性能指标")

        df_calc = load_data("uav_models.json")
        if not df_calc.empty:
            param1 = st.selectbox("参数1", numeric_cols, index=0, format_func=lambda x: labels.get(x, x), key="calc_param1")
            param2 = st.selectbox("参数2", numeric_cols, index=1, format_func=lambda x: labels.get(x, x), key="calc_param2")

            # 准备数据
            compare_df = df_calc[["name", param1, param2]].dropna()
            compare_df = compare_df[(compare_df[param1] > 0) & (compare_df[param2] > 0)]

            if not compare_df.empty:
                # 计算比率
                compare_df["ratio"] = compare_df[param2] / compare_df[param1]
                compare_df = compare_df.sort_values("ratio", ascending=False)

                st.markdown(f"#### {labels[param2]} / {labels[param1]} 排名")
                st.dataframe(
                    compare_df[["name", param1, param2, "ratio"]].round(4),
                    column_config={
                        "name": st.column_config.TextColumn("机型名称", width="large"),
                        param1: st.column_config.NumberColumn(labels[param1], format="%.2f"),
                        param2: st.column_config.NumberColumn(labels[param2], format="%.2f"),
                        "ratio": st.column_config.NumberColumn("比率", format="%.4f", help=f"{labels[param2]} 除以 {labels[param1]}")
                    },
                    hide_index=True
                )

                # 可视化
                fig_compare = px.scatter(
                    compare_df,
                    x=param1,
                    y=param2,
                    hover_name="name",
                    labels=labels,
                    title=f"{labels[param2]} vs {labels[param1]}",
                    size="ratio",
                    size_max=20
                )
                st.plotly_chart(fig_compare, use_container_width=True)
            else:
                st.warning("没有足够的数据进行比较")
        else:
            st.warning("请先导入机型数据")
