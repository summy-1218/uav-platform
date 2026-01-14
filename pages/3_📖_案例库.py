import streamlit as st
from utils import get_case_files, delete_case_file, save_case_file, load_data, save_data
import os
import json
import re
from datetime import datetime
import requests
import pandas as pd

st.set_page_config(page_title="案例库", page_icon="📖", layout="wide")

st.title("📖 无人机设计案例库")


def extract_uav_info_from_ai(markdown_content, ai_service, api_key, model, base_url=None):
    """使用AI从Markdown内容中提取机型信息"""

    # 构建prompt
    prompt = f"""
请从以下无人机案例Markdown内容中提取机型信息，并严格按照JSON格式返回。如果某项信息在内容中未提及，请设置为null或0。

返回的JSON结构必须如下（不要添加任何额外文字）:
{{
    "name": "型号名称",
    "manufacturer": "厂商名称",
    "type": "Fixed-Wing/Multi-Rotor/VTOL/Helicopter/Other",
    "image_url": "图片URL或路径",
    "description": "简要描述",
    "length_m": 机长数值(数字),
    "wingspan_m": 翼展数值(数字),
    "height_m": 机高数值(数字),
    "mtow_kg": 最大起飞重量数值(数字),
    "empty_weight_kg": 空重数值(数字),
    "max_payload_kg": 最大载荷数值(数字),
    "max_speed_kmh": 最大速度数值(数字),
    "cruise_speed_kmh": 巡航速度数值(数字),
    "range_km": 航程数值(数字),
    "endurance_min": 续航时间数值(数字),
    "ceiling_m": 升限数值(数字),
    "purpose": ["用途1", "用途2"]
}}

案例内容：
{markdown_content}
"""

    # 调用AI API
    if ai_service == "DeepSeek":
        return call_openai_api(prompt, api_key, model, base_url or "https://api.deepseek.com")
    elif ai_service == "OpenAI":
        return call_openai_api(prompt, api_key, model, base_url or "https://api.openai.com/v1")
    else:  # 通义千问
        return call_qwen_api(prompt, api_key, model)


def call_openai_api(prompt, api_key, model, base_url):
    """调用OpenAI API"""
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个专业的无人机数据提取助手，请严格按照JSON格式返回提取的机型信息。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        # 提取回复内容
        content = result['choices'][0]['message']['content']

        # 解析JSON
        return parse_ai_response(content)
    except requests.exceptions.HTTPError as e:
        # 尝试从响应中提取错误信息
        error_msg = f"API请求失败 (HTTP {e.response.status_code})"
        try:
            error_detail = e.response.json()
            if 'error' in error_detail:
                error_msg += f": {error_detail['error'].get('message', str(error_detail['error']))}"
        except:
            error_msg += f": {str(e)}"
        raise Exception(error_msg) from e
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}") from e


def call_qwen_api(prompt, api_key, model):
    """调用通义千问API"""
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个专业的无人机数据提取助手，请严格按照JSON格式返回提取的机型信息。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()

        # 提取回复内容
        content = result['choices'][0]['message']['content']

        # 解析JSON
        return parse_ai_response(content)
    except requests.exceptions.HTTPError as e:
        # 尝试从响应中提取错误信息
        error_msg = f"API请求失败 (HTTP {e.response.status_code})"
        try:
            error_detail = e.response.json()
            if 'error' in error_detail:
                error_msg += f": {error_detail['error'].get('message', str(error_detail['error']))}"
        except:
            error_msg += f": {str(e)}"
        raise Exception(error_msg) from e
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}") from e


def parse_ai_response(content):
    """解析AI返回的内容，提取JSON数据"""
    try:
        # 尝试直接解析
        return json.loads(content)
    except json.JSONDecodeError:
        # 如果直接解析失败，尝试提取JSON部分
        # 查找JSON起始和结束位置
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        # 尝试查找markdown代码块中的JSON
        code_block_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', content)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass

        raise ValueError("无法解析AI返回的JSON数据")


def safe_float(value, default=0.0):
    """安全地转换为float，处理None和无效值"""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """安全地转换为int，处理None和无效值"""
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def display_extracted_data(data, case_name):
    """显示提取的机型数据，允许用户编辑"""
    st.markdown("### ✨ 提取的机型信息（可编辑）")

    with st.form("edit_extracted_data"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("型号名称*", value=data.get('name', case_name), key="ext_name")
            manufacturer = st.text_input("厂商*", value=data.get('manufacturer', ''), key="ext_manufacturer")
            type_ = st.selectbox("类型*", ["Fixed-Wing", "Multi-Rotor", "VTOL", "Helicopter", "Other"],
                               index=["Fixed-Wing", "Multi-Rotor", "VTOL", "Helicopter", "Other"].index(
                                   data.get('type', 'Other') if data.get('type') in ["Fixed-Wing", "Multi-Rotor", "VTOL", "Helicopter"] else 4),
                               key="ext_type")
            image_url = st.text_input("图片路径/URL", value=data.get('image_url', ''), key="ext_image_url")

        with col2:
            description = st.text_area("描述", value=data.get('description', ''), height=100, key="ext_description")
            purpose_input = st.text_input("主要用途 (用逗号分隔)",
                                         value=', '.join(data.get('purpose', [])) if isinstance(data.get('purpose'), list) else '',
                                         key="ext_purpose")

        st.divider()

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### 外形参数")
            length_m = st.number_input("机长 (m)", value=safe_float(data.get('length_m')), min_value=0.0, step=0.1, key="ext_length_m")
            wingspan_m = st.number_input("翼展 (m)", value=safe_float(data.get('wingspan_m')), min_value=0.0, step=0.1, key="ext_wingspan_m")
            height_m = st.number_input("机高 (m)", value=safe_float(data.get('height_m')), min_value=0.0, step=0.1, key="ext_height_m")

        with col4:
            st.markdown("#### 重量参数")
            mtow_kg = st.number_input("最大起飞重量", value=safe_float(data.get('mtow_kg')), min_value=0.0, step=0.1, key="ext_mtow_kg")
            empty_weight_kg = st.number_input("空重", value=safe_float(data.get('empty_weight_kg')), min_value=0.0, step=0.1, key="ext_empty_weight_kg")
            max_payload_kg = st.number_input("最大载荷", value=safe_float(data.get('max_payload_kg')), min_value=0.0, step=0.1, key="ext_max_payload_kg")

        st.divider()

        col5, col6 = st.columns(2)
        with col5:
            st.markdown("#### 性能参数")
            max_speed_kmh = st.number_input("最大速度", value=safe_float(data.get('max_speed_kmh')), min_value=0.0, step=1.0, key="ext_max_speed_kmh")
            cruise_speed_kmh = st.number_input("巡航速度", value=safe_float(data.get('cruise_speed_kmh')), min_value=0.0, step=1.0, key="ext_cruise_speed_kmh")

        with col6:
            range_km = st.number_input("航程", value=safe_float(data.get('range_km')), min_value=0.0, step=1.0, key="ext_range_km")
            endurance_min = st.number_input("续航时间", value=safe_int(data.get('endurance_min')), min_value=0, step=1, key="ext_endurance_min")
            ceiling_m = st.number_input("升限", value=safe_int(data.get('ceiling_m')), min_value=0, step=10, key="ext_ceiling_m")

        # 添加表单提交按钮
        submitted = st.form_submit_button("✅ 确认编辑内容")

        st.caption("💡 修改信息后点击【✅ 确认编辑内容】按钮保存修改，然后点击页面底部的【➕ 确认添加到机型库】按钮完成添加。")

        # 表单提交时才更新数据
        if submitted:
            # 构建更新后的数据
            updated_data = {
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
                "purpose": [p.strip() for p in purpose_input.split(",") if p.strip()] if purpose_input else [],
                "custom_params": {}
            }

            # 保存到session state
            st.session_state.extracted_data = updated_data
            st.success("✅ 已更新机型信息，请点击下方的【➕ 确认添加到机型库】按钮完成添加。")
        else:
            # 如果表单未提交，使用原始数据
            st.session_state.extracted_data = data


def add_extracted_model(data):
    """将提取的机型数据添加到机型库"""
    df = load_data("uav_models.json")

    # 数据验证
    name = data.get("name", "") or ""
    manufacturer = data.get("manufacturer", "") or ""

    # 必填字段验证
    if not name:
        raise ValueError("型号名称不能为空")
    if not manufacturer:
        raise ValueError("厂商不能为空")

    # 检查型号是否已存在
    if not df.empty and name in df["name"].values:
        raise ValueError(f"型号名称 '{name}' 已存在，请使用修改功能更新现有机型")

    # 类型枚举验证
    valid_types = ["Fixed-Wing", "Multi-Rotor", "VTOL", "Helicopter", "Other"]
    uav_type = data.get("type", "Other")
    if uav_type not in valid_types:
        raise ValueError(f"无效的机型类型: {uav_type}，必须是: {', '.join(valid_types)}")

    # 数值验证（确保为非负数）
    def validate_non_negative(value, field_name):
        if value is None:
            return 0.0
        try:
            return max(0.0, float(value))
        except (ValueError, TypeError):
            return 0.0

    # 创建新机型
    new_model = {
        "id": f"uav-{int(datetime.now().timestamp())}",
        "name": name,
        "manufacturer": manufacturer,
        "type": uav_type,
        "image_url": data.get("image_url") if data.get("image_url") else None,
        "description": data.get("description", "").strip(),
        "length_m": validate_non_negative(data.get("length_m"), "机长"),
        "wingspan_m": validate_non_negative(data.get("wingspan_m"), "翼展"),
        "height_m": validate_non_negative(data.get("height_m"), "机高"),
        "mtow_kg": validate_non_negative(data.get("mtow_kg"), "最大起飞重量"),
        "empty_weight_kg": validate_non_negative(data.get("empty_weight_kg"), "空重"),
        "max_payload_kg": validate_non_negative(data.get("max_payload_kg"), "最大载荷"),
        "max_speed_kmh": validate_non_negative(data.get("max_speed_kmh"), "最大速度"),
        "cruise_speed_kmh": validate_non_negative(data.get("cruise_speed_kmh"), "巡航速度"),
        "range_km": validate_non_negative(data.get("range_km"), "航程"),
        "endurance_min": max(0, int(data.get("endurance_min", 0))),
        "ceiling_m": max(0, int(data.get("ceiling_m", 0))),
        "purpose": [p.strip() for p in data.get("purpose", []) if isinstance(p, str) and p.strip()],
        "custom_params": data.get("custom_params", {})
    }

    # 添加到数据
    df = pd.concat([df, pd.DataFrame([new_model])], ignore_index=True)
    save_data("uav_models.json", df)

    return True


# Mode selection
mode = st.radio("选择操作模式", ["浏览案例", "添加案例", "删除案例", "AI提取机型"], horizontal=True)

if mode == "删除案例":
    st.warning("⚠️ 删除操作不可恢复，请谨慎操作！")
    cases = get_case_files()

    if not cases:
        st.info("暂无案例可删除")
    else:
        case_to_delete = st.selectbox("选择要删除的案例", [c['name'] for c in cases])
        if st.button("🗑️ 确认删除", type="primary"):
            case_info = next(c for c in cases if c['name'] == case_to_delete)
            if delete_case_file(case_info['filename']):
                st.success(f"已删除案例: {case_to_delete}")
                st.rerun()

elif mode == "添加案例":
    st.subheader("➕ 添加新案例")

    with st.form("add_case_form"):
        filename = st.text_input("文件名*", value="", placeholder="例如: DJI_Mavic_3").strip()
        st.caption("文件名将作为案例条目名称（无需添加.md后缀）")

        content = st.text_area("Markdown 内容*", value="", height=400, placeholder="输入案例的 Markdown 内容...")
        st.markdown("""
        **提示**: 支持标准 Markdown 语法：
        - 标题: # ## ###
        - 列表: - 或 1.
        - 图片: ![描述](图片路径)
        - 链接: [文字](链接)
        - 代码: ```代码```
        """)

        submitted = st.form_submit_button("✅ 添加案例", type="primary")

        if submitted:
            if not filename:
                st.error("请输入文件名")
            elif not content:
                st.error("请输入 Markdown 内容")
            else:
                try:
                    save_case_file(filename, content)
                    st.success(f"成功添加案例: {filename}")
                    st.rerun()
                except Exception as e:
                    st.error(f"添加失败: {str(e)}")

elif mode == "AI提取机型":
    st.subheader("🤖 AI智能提取机型信息")

    st.info("""
    💡 **功能说明**: 从Markdown案例中自动提取机型信息并添加到机型库。

    **支持的AI服务**:
    - DeepSeek (推荐，性价比高)
    - OpenAI (需要API Key)
    - 通义千问 (需要API Key)

    **使用方法**: 选择案例后点击提取，AI将解析内容并提取机型参数，你可以手动调整后确认添加。
    """)

    # 选择案例
    cases = get_case_files()

    if not cases:
        st.warning("暂无案例，请先添加案例。")
        st.stop()

    selected_case = st.selectbox(
        "选择要提取机型信息的案例",
        ["-- 请选择 --"] + [c['name'] for c in cases]
    )

    if selected_case != "-- 请选择 --":
        # 读取案例内容
        case_info = next(c for c in cases if c['name'] == selected_case)
        filepath = case_info['filepath']

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            # 显示案例内容
            st.divider()
            st.markdown("### 案例内容预览")
            with st.expander("📄 点击展开案例内容", expanded=False):
                st.markdown(markdown_content)

            st.divider()

            # AI服务配置
            st.markdown("#### 📝 AI服务配置")
            ai_service = st.selectbox("选择AI服务", ["DeepSeek", "OpenAI", "通义千问"])

            # 初始化变量
            base_url = None

            if ai_service == "DeepSeek":
                api_key = st.text_input("DeepSeek API Key", type="password", placeholder="sk-...")
                model = st.selectbox("模型", ["deepseek-chat", "deepseek-coder"], index=0)
            elif ai_service == "OpenAI":
                api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
                model = st.selectbox("模型", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0)
                custom_base_url = st.text_input("Base URL (可选)", value="", placeholder="例如: https://api.openai.com/v1")
                base_url = custom_base_url if custom_base_url.strip() else None
            else:  # 通义千问
                api_key = st.text_input("通义千问 API Key", type="password", placeholder="sk-...")
                model = st.selectbox("模型", ["qwen-turbo", "qwen-plus", "qwen-max"], index=0)

            if st.button("🤖 开始提取机型信息", type="primary"):
                if not api_key:
                    st.error("请输入API Key")
                else:
                    with st.spinner("AI正在分析案例内容，请稍候..."):
                        try:
                            # 调用AI提取函数
                            extracted_data = extract_uav_info_from_ai(
                                markdown_content,
                                ai_service,
                                api_key,
                                model,
                                base_url
                            )

                            if extracted_data:
                                st.success("✅ 提取成功！请确认提取的信息：")

                                # 保存提取结果到session state（初始数据）
                                st.session_state.extracted_data = extracted_data
                                st.session_state.current_case = selected_case

                                # 显示提取结果
                                display_extracted_data(extracted_data, selected_case)
                            else:
                                st.error("未能提取到有效的机型信息，请尝试其他案例或检查案例内容。")
                        except Exception as e:
                            st.error(f"提取失败: {str(e)}")

            # 如果有提取结果且是当前案例，显示确认添加按钮
            if ('extracted_data' in st.session_state and
                st.session_state.extracted_data and
                st.session_state.get('current_case') == selected_case):

                st.divider()
                if st.button("➕ 确认添加到机型库", type="primary"):
                    try:
                        add_extracted_model(st.session_state.extracted_data)
                        st.success(f"成功添加机型: {st.session_state.extracted_data.get('name', '未知机型')}到机型库！")
                        # 清除session state
                        st.session_state.extracted_data = None
                        st.session_state.current_case = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"添加失败: {str(e)}")
        else:
            st.error(f"无法读取案例文件: {filepath}")

else:  # 浏览案例
    cases = get_case_files()

    if not cases:
        st.info("暂无案例，请使用【添加案例】功能添加新案例。")
        st.stop()

    st.metric("收录案例数量", len(cases))

    # Case list view
    st.subheader("📚 案例列表")

    selected_case = st.selectbox(
        "选择要查看的案例",
        ["-- 请选择 --"] + [c['name'] for c in cases]
    )

    if selected_case != "-- 请选择 --":
        case_info = next(c for c in cases if c['name'] == selected_case)
        filepath = case_info['filepath']

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            st.divider()
            st.markdown(f"## 📖 {selected_case}")
            st.divider()
            st.markdown(markdown_content)
        else:
            st.error(f"无法读取案例文件: {filepath}")

    # Alternative: All cases as expanders
    st.divider()
    st.subheader("📄 所有案例预览")

    for case in cases:
        with st.expander(f"📚 {case['name']}"):
            filepath = case['filepath']
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                st.markdown(content)
            except Exception as e:
                st.error(f"读取失败: {str(e)}")
