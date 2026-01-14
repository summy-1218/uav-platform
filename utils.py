import json
import os
import pandas as pd
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
CASES_DIR = os.path.join(DATA_DIR, "cases")

def load_data(filename):
    """Load JSON data as a pandas DataFrame."""
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return pd.DataFrame()

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return pd.DataFrame(data)

def save_data(filename, df):
    """Save DataFrame to JSON file."""
    filepath = os.path.join(DATA_DIR, filename)

    # Convert DataFrame back to list of dicts
    data = df.to_dict(orient="records")

    # 清理NaN值，转换为None
    def clean_nan(obj):
        if isinstance(obj, dict):
            return {k: clean_nan(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_nan(item) for item in obj]
        elif isinstance(obj, float) and (pd.isna(obj) or obj != obj):  # NaN检查
            return None
        else:
            return obj

    data = clean_nan(data)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def import_excel_data(uploaded_file):
    """Process uploaded Excel file and update JSON databases."""
    try:
        xls = pd.ExcelFile(uploaded_file)

        # 1. Process UAVs
        if "UAVs" in xls.sheet_names:
            new_df = pd.read_excel(xls, "UAVs")
            current_df = load_data("uav_models.json")

            # Ensure columns exist in current data for consistency
            if not new_df.empty:
                # Generate IDs for new items if not present
                if "id" not in new_df.columns:
                    new_df["id"] = new_df.apply(lambda x: f"uav-{int(datetime.now().timestamp())}-{x.name}", axis=1)

                # Merge: Update existing (by name) and Append new
                if not current_df.empty:
                    # Create a dictionary of existing items for quick lookup
                    existing_dict = current_df.set_index("name").to_dict(orient="index")

                    for _, row in new_df.iterrows():
                        name = row["name"]
                        if pd.isna(name): continue

                        # Clean row data
                        row_data = row.dropna().to_dict()
                        if "purpose" in row_data and isinstance(row_data["purpose"], str):
                             row_data["purpose"] = [p.strip() for p in row_data["purpose"].split(",")]

                        if name in existing_dict:
                            # Update existing
                            existing_dict[name].update(row_data)
                        else:
                            # Add new
                            new_item = row.to_dict()
                            if "purpose" in new_item and isinstance(new_item["purpose"], str):
                                new_item["purpose"] = [p.strip() for p in new_item["purpose"].split(",")]
                            new_item["id"] = f"uav-{int(datetime.now().timestamp())}"
                            # Add to current_df is complex here, simpler to rebuild list
                            existing_dict[name] = new_item

                    # Reconstruct DataFrame
                    final_uav_data = pd.DataFrame.from_dict(existing_dict, orient="index").reset_index(drop=True)
                else:
                    final_uav_data = new_df

                save_data("uav_models.json", final_uav_data)

        # 2. Process Subsystems
        if "Subsystems" in xls.sheet_names:
            new_df = pd.read_excel(xls, "Subsystems")
            current_df = load_data("subsystems.json")

            if not new_df.empty:
                 # Logic similar to above, simplified for demo
                combined_df = pd.concat([current_df, new_df]).drop_duplicates(subset=["name"], keep="last")
                save_data("subsystems.json", combined_df)

        return True, "导入成功！数据已更新。"
    except Exception as e:
        return False, f"导入失败: {str(e)}"

def get_image_path(image_url):
    """Get appropriate image path, supporting both URLs and local files."""
    if not image_url or pd.isna(image_url):
        return None

    image_url = str(image_url).strip()

    # If it's a URL, return as is
    if image_url.startswith("http"):
        return image_url

    # Handle local file paths
    # Try relative paths: assets/, data/, or absolute path
    possible_paths = [
        os.path.join(ASSETS_DIR, image_url),
        os.path.join(DATA_DIR, image_url),
        os.path.join(os.path.dirname(__file__), image_url),
        image_url if os.path.isabs(image_url) else None
    ]

    for path in possible_paths:
        if path and os.path.exists(path):
            return path

    return None

def get_case_files():
    """Get all markdown case files from the cases directory."""
    if not os.path.exists(CASES_DIR):
        os.makedirs(CASES_DIR, exist_ok=True)
        return []

    case_files = []
    for filename in os.listdir(CASES_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(CASES_DIR, filename)
            case_files.append({
                'name': filename[:-3],  # Remove .md extension
                'filepath': filepath,
                'filename': filename
            })

    return sorted(case_files, key=lambda x: x['name'])

def delete_case_file(filename):
    """Delete a case file by filename."""
    filepath = os.path.join(CASES_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False

def save_case_file(filename, content):
    """Save content to a case file."""
    if not os.path.exists(CASES_DIR):
        os.makedirs(CASES_DIR, exist_ok=True)

    # Ensure .md extension
    if not filename.endswith('.md'):
        filename += '.md'

    filepath = os.path.join(CASES_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath

def load_custom_params():
    """Load custom parameters definition file."""
    filepath = os.path.join(DATA_DIR, "custom_params.json")
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data

def save_custom_params(params):
    """Save custom parameters definition."""
    filepath = os.path.join(DATA_DIR, "custom_params.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(params, f, indent=2, ensure_ascii=False)

def add_custom_param(name, unit):
    """Add a new custom parameter."""
    params = load_custom_params()

    # Check if parameter already exists
    for param in params:
        if param['name'] == name:
            return False, "参数名称已存在"

    # Add new parameter
    new_param = {
        "name": name,
        "unit": unit,
        "created_at": datetime.now().isoformat()
    }
    params.append(new_param)
    save_custom_params(params)
    return True, "参数添加成功"

def delete_custom_param(name):
    """Delete a custom parameter by name."""
    params = load_custom_params()
    params = [p for p in params if p['name'] != name]
    save_custom_params(params)
    return True
