# 无人机系统数字化资源平台

## 项目概述

本项目是一个基于 **Streamlit** 框架开发的无人机数字化资源平台，专门为《无人机系统设计》课程设计。平台提供无人机机型库、子系统库、案例库以及交互式数据分析功能，支持本地运行和Excel数据导入。

### 技术栈

| 技术/库 | 版本 | 用途 |
|---------|------|------|
| Streamlit | - | Web应用框架 |
| Pandas | - | 数据处理与分析 |
| Openpyxl | - | Excel文件读写 |
| Plotly | - | 交互式数据可视化 |
| Scikit-learn | - | 线性回归分析 |
| Pillow | - | 图片处理 |
| Requests | - | HTTP请求（AI API调用） |

## 项目结构

```
uav-python/
├── Hello.py                 # 应用程序入口文件
├── utils.py                 # 核心工具函数模块
├── requirements.txt         # Python依赖列表
├── README.md               # 项目说明文档
├── pages/                  # 功能页面目录
│   ├── 1_✈️_机型库.py
│   ├── 2_🔧_子系统库.py
│   ├── 3_📖_案例库.py
│   ├── 4_📊_统计分析.py
│   └── 5_⚙️_数据管理.py
├── data/                   # 数据存储目录
│   ├── uav_models.json    # 机型数据
│   ├── subsystems.json    # 子系统数据
│   ├── custom_params.json # 自定义参数定义
│   ├── import_template.xlsx # Excel导入模板
│   └── cases/             # 案例库Markdown文件
└── assets/                # 图片资源目录
    ├── 玄峰无人僚机.png
    └── RQ-4.jpg
```

## 功能模块

### 1. 首页 (Hello.py)

应用主入口，展示欢迎界面和快捷导航。

**功能特性**:
- 三个快捷导航按钮：机型库、子系统库、统计分析
- Hero图片展示（如果存在）
- 侧边栏导航说明

### 2. 机型库 (1_✈️_机型库.py)

无人机型号的完整管理系统。

#### 操作模式

##### 2.1 浏览数据
- 按类型筛选：Fixed-Wing, Multi-Rotor, VTOL, Helicopter, Other
- 按厂商筛选
- 机型列表展示（关键参数：型号、厂商、类型、最大起飞重量、续航时间、最大速度、用途）
- 机型详情视图：图片、描述、外形参数、重量参数、性能参数、自定义参数

##### 2.2 添加机型
**基本信息**:
- 型号名称*（必填）
- 厂商*（必填）
- 类型
- 图片设置：支持上传本地图片或输入URL/路径

**用途描述**:
- 主要用途（支持逗号分隔的多用途）

**外形参数**:
- 机长 (m)
- 翼展 (m)
- 机高 (m)

**重量参数**:
- 最大起飞重量 (kg)
- 空重 (kg)
- 最大载荷 (kg)

**性能参数**:
- 最大速度 (km/h)
- 巡航速度 (km/h)
- 航程 (km)
- 续航时间 (min)
- 升限 (m)

**自定义参数**:
- 动态加载自定义参数类型
- 支持数值输入

##### 2.3 删除机型
- 选择要删除的机型
- 确认删除（不可恢复）
- 自动更新数据文件

##### 2.4 修改机型
- 选择要修改的机型
- 预填充现有数据
- 支持修改所有字段
- 保存后自动更新

##### 2.5 添加参数
**标准参数列表** (11个):
- length_m (机长)
- wingspan_m (翼展)
- height_m (机高)
- mtow_kg (最大起飞重量)
- empty_weight_kg (空重)
- max_payload_kg (最大载荷)
- max_speed_kmh (最大速度)
- cruise_speed_kmh (巡航速度)
- range_km (航程)
- endurance_min (续航时间)
- ceiling_m (升限)

**自定义参数管理**:
- 显示现有自定义参数
- 添加新参数（名称 + 单位）
- 删除自定义参数

### 3. 子系统库 (2_🔧_子系统库.py)

无人机关键部件规格查询系统。

**功能特性**:
- 按类别筛选子系统
- 网格卡片形式展示
- 每个卡片包含：子系统图片、名称、厂商和类别、描述文本、关键规格指标

**数据结构**:
```json
{
  "name": "Example Motor",
  "manufacturer": "Company B",
  "category": "Engine/Power",
  "image_url": null,
  "description": "High power motor",
  "key_specs": "{\"Power\": \"500W\", \"Weight\": \"200g\"}"
}
```

### 4. 案例库 (3_📖_案例库.py)

无人机技术文档管理系统，支持AI智能提取。

#### 操作模式

##### 4.1 浏览案例
- 显示案例数量统计
- 选择单个案例查看完整内容
- 所有案例可展开预览

##### 4.2 添加案例
- 输入文件名（无需.md后缀）
- 输入Markdown格式内容
- 支持标准Markdown语法：
  - 标题（#, ##, ###）
  - 列表（-, *, 数字列表）
  - 图片
  - 链接
  - 代码块
  - 表格
- 自动保存到 `data/cases/` 目录

##### 4.3 删除案例
- 选择要删除的案例
- 确认后删除文件

##### 4.4 AI提取机型 🤖（特色功能）

**支持的AI服务**:
- **DeepSeek** (推荐)
- **OpenAI** (支持自定义Base URL)
- **通义千问**

**提取的机型信息**:

| 类别 | 参数 |
|------|------|
| 基本信息 | 型号名称、厂商、类型、图片URL、描述 |
| 外形参数 | 机长、翼展、机高 |
| 重量参数 | 最大起飞重量、空重、最大载荷 |
| 性能参数 | 最大速度、巡航速度、航程、续航时间、升限 |
| 用途 | 用途列表 |

**提取流程**:
1. 选择案例文件
2. 预览案例内容
3. 配置AI服务（API Key + 模型选择）
4. AI分析并提取结构化数据
5. 用户编辑确认
6. 添加到机型库

### 5. 统计分析 (4_📊_统计分析.py)

无人机参数相关性分析与可视化工具。

**功能特性**:

##### 5.1 参数选择
**X轴和Y轴参数（7个数值型参数可选）**:
- 最大起飞重量 (kg)
- 最大载荷 (kg)
- 续航时间 (min)
- 航程 (km)
- 最大速度 (km/h)
- 机长 (m)
- 翼展 (m)

##### 5.2 可视化功能
- 交互式散点图（Plotly Express）
- 按机型类型着色显示
- 鼠标悬停显示机型名称
- 可选显示/隐藏线性回归拟合线
- 自动过滤无效数据（0值和NaN）

##### 5.3 回归分析结果
- R² (决定系数)
- 回归方程

### 6. 数据管理 (5_⚙️_数据管理.py)

批量数据导入与管理系统。

#### 操作模式

##### 6.1 下载模板
- 下载 `import_template.xlsx` Excel导入模板

##### 6.2 上传数据
- 上传填写好的Excel文件
- 自动解析并更新数据库

**导入逻辑**:
- 根据机型名称匹配现有数据
- 如果名称已存在：更新现有记录
- 如果名称不存在：创建新记录
- 支持 "UAVs" 和 "Subsystems" 两个工作表

## 数据存储

### 数据文件结构

| 文件 | 格式 | 用途 |
|------|------|------|
| `uav_models.json` | JSON | 机型库数据 |
| `subsystems.json` | JSON | 子系统库数据 |
| `custom_params.json` | JSON | 自定义参数定义 |
| `cases/*.md` | Markdown | 案例文档 |
| `import_template.xlsx` | Excel | 数据导入模板 |

### 机型数据结构

```json
{
  "id": "uav-1768356460",
  "name": "玄峰无人僚机",
  "manufacturer": "北京航空航天大学飞行学院T01小组",
  "type": "Fixed-Wing",
  "image_url": "玄峰无人僚机.png",
  "description": "一款具备高速、远航程、大载荷能力的无人僚机...",
  "length_m": 15.463,
  "wingspan_m": 8.2179,
  "height_m": 0.0,
  "mtow_kg": 13479.0,
  "empty_weight_kg": 8314.0,
  "max_payload_kg": 2000.0,
  "max_speed_kmh": 0.0,
  "cruise_speed_kmh": 0.0,
  "ceiling_m": 22000,
  "range_km": 3100.0,
  "endurance_min": 60,
  "purpose": ["远距离打击", "协同作战"],
  "custom_params": {
    "翼载荷": {"value": 300.0, "unit": "kg/m2"},
    "推重比": {"value": 1.2, "unit": "无量纲"}
  }
}
```

### 自定义参数结构

```json
{
  "name": "翼载荷",
  "unit": "kg/m2",
  "created_at": "2026-01-13T21:34:51.662163"
}
```

## 工具函数 (utils.py)

### 数据加载与保存

| 函数 | 功能 | 返回类型 |
|------|------|----------|
| `load_data(filename)` | 从JSON文件加载数据 | DataFrame |
| `save_data(filename, df)` | 保存DataFrame到JSON文件 | - |

**特点**:
- 自动处理 NaN 值转换为 None
- 支持 UTF-8 编码
- 格式化输出（indent=2）

### Excel导入处理

| 函数 | 功能 |
|------|------|
| `import_excel_data(uploaded_file)` | 处理上传的Excel文件并更新JSON数据库 |

**导入逻辑**:
1. 解析Excel文件
2. 处理 UAVs 工作表（支持更新和新增）
3. 处理 Subsystems 工作表（追加并去重）
4. 自动生成ID（基于时间戳）
5. 解析purpose字段（逗号分隔转列表）

### 图片处理

| 函数 | 功能 |
|------|------|
| `get_image_path(image_url)` | 获取图片路径，支持URL和本地文件 |

**支持的路径格式**:
- HTTP/HTTPS URL（直接返回）
- assets/ 目录相对路径
- data/ 目录相对路径
- 项目根目录相对路径
- 绝对路径

### 案例文件管理

| 函数 | 功能 |
|------|------|
| `get_case_files()` | 获取所有Markdown案例文件列表 |
| `delete_case_file(filename)` | 删除案例文件 |
| `save_case_file(filename, content)` | 保存案例内容到文件 |

### 自定义参数管理

| 函数 | 功能 |
|------|------|
| `load_custom_params()` | 加载自定义参数定义 |
| `save_custom_params(params)` | 保存自定义参数定义 |
| `add_custom_param(name, unit)` | 添加新自定义参数 |
| `delete_custom_param(name)` | 删除自定义参数 |

### AI API调用

| 函数 | 功能 |
|------|------|
| `extract_uav_info_from_ai(markdown_content, ai_service, api_key, model, base_url)` | 从Markdown内容中提取机型信息 |
| `call_openai_api(prompt, api_key, model, base_url)` | 调用OpenAI兼容接口 |
| `call_qwen_api(prompt, api_key, model)` | 调用通义千问API |
| `parse_ai_response(content)` | 解析AI返回的内容，提取JSON数据 |

**特点**:
- 支持 DeepSeek、OpenAI、通义千问
- 自动处理多种JSON响应格式（直接JSON、代码块中的JSON）
- 详细的错误信息提取

### 数据验证

| 函数 | 功能 |
|------|------|
| `safe_float(value, default)` | 安全转换为float |
| `safe_int(value, default)` | 安全转换为int |

## 安装与运行

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆或下载项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 运行项目

```bash
streamlit run Hello.py
```

浏览器会自动打开 `http://localhost:8501`

## 项目特色功能

1. **AI智能提取** - 支持使用多种AI服务从案例文档中自动提取机型参数
2. **自定义参数扩展** - 可以动态添加自定义参数类型
3. **Excel批量导入** - 支持通过Excel模板批量更新数据
4. **交互式数据分析** - 支持任意两个参数的散点图绘制和线性回归
5. **Markdown案例库** - 支持富文本格式的技术文档存储
6. **图片灵活管理** - 支持本地图片和网络URL
7. **完整的CRUD操作** - 机型和案例支持增删改查
8. **筛选搜索** - 机型和子系统支持多维度筛选

## 当前数据统计

### 机型库 (2款)
1. **玄峰无人僚机** - 北航飞行学院T01小组设计
2. **RQ-4 "Global Hawk"（全球鹰）** - 诺斯罗普·格鲁曼

### 子系统库 (1个)
1. **Example Motor** - Company B

### 案例库 (2个)
1. **哨卫无人机.md** - 察打一体无人机系统设计报告
2. **无人僚机"玄锋".md**

### 自定义参数 (2个)
1. **翼载荷** - kg/m²
2. **推重比** - 无量纲

## 数据流示意图

```
用户操作
   ↓
Streamlit界面
   ↓
utils.py (工具层)
   ↓
JSON文件 (数据持久层)
   ├── uav_models.json
   ├── subsystems.json
   ├── custom_params.json
   └── cases/*.md
   ↓
Excel文件 (批量导入)
```

## 模块依赖关系

### 核心依赖树

```
Hello.py (入口)
├── utils.py (工具模块)
├── streamlit (Web框架)
├── pandas (数据处理)
├── PIL (图片处理)
└── pages/*.py (功能页面)
    ├── utils.py (共享工具)
    ├── streamlit (Web框架)
    ├── pandas (数据处理)
    ├── plotly (可视化)
    ├── sklearn (机器学习)
    ├── json (JSON处理)
    ├── os (文件操作)
    ├── datetime (时间处理)
    ├── requests (HTTP请求)
    └── re (正则表达式)
```

### 各页面依赖

| 页面 | 主要依赖 |
|------|----------|
| 机型库 | `load_data`, `save_data`, `get_image_path`, `load_custom_params`, `add_custom_param`, `delete_custom_param`, `ASSETS_DIR` |
| 子系统库 | `load_data`, `get_image_path` |
| 案例库 | `get_case_files`, `delete_case_file`, `save_case_file`, `load_data`, `save_data`, AI API |
| 统计分析 | `load_data`, plotly, sklearn |
| 数据管理 | `import_excel_data` |

## 注意事项

1. **数据备份**: 定期备份 `data/` 目录下的JSON文件
2. **图片管理**: 上传的图片会保存到 `assets/` 目录，注意磁盘空间
3. **API密钥**: 使用AI提取功能需要配置相应的API密钥
4. **编码格式**: 所有文件使用UTF-8编码
5. **数据格式**: 导入Excel时请严格按照模板格式填写

## 开发者信息

本项目为《无人机系统设计》课程设计项目，由北航飞行学院开发。

## 许可证

本项目仅供教学使用。
