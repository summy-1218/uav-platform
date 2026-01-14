# 无人机数字化资源平台 (Python版)

这是一个基于 Python Streamlit 的应用程序，提供了无人机机型库、子系统库、案例库以及交互式数据分析功能。它比静态网页更方便在本地运行，并集成了 Excel 数据导入功能。

## 🚀 快速开始

### 1. 确保已安装 Python
如果您尚未安装 Python，请前往 [Python官网](https://www.python.org/) 下载并安装。

### 2. 安装依赖库
打开终端 (Terminal) 或 命令提示符 (CMD)，进入本目录，运行以下命令安装所需组件：

```bash
pip install streamlit pandas openpyxl plotly scikit-learn
```

### 3. 运行应用
安装完成后，在终端运行：

```bash
streamlit run Hello.py
```

应用会自动在您的浏览器中打开 (默认地址 http://localhost:8501)。

---

## 📂 功能说明

1.  **机型库 & 子系统库**: 浏览、搜索和筛选数据库中的无人机和子系统。
2.  **统计分析**: 
    - 选择任意两个参数（如重量 vs 续航）绘制散点图。
    - 自动进行线性回归分析，显示 R² 相关系数。
3.  **案例库**: 阅读经典机型的设计分析。
4.  **数据管理**:
    - 下载 Excel 模板 (`import_template.xlsx`)。
    - 上传填写好的 Excel 文件，一键更新系统数据库。

## 📦 目录结构

- `Hello.py`: 应用程序入口
- `pages/`: 各个功能页面源码
- `data/`: 存放 JSON 数据文件和 Excel 模板
- `assets/`: 图片资源
- `utils.py`: 核心数据处理逻辑
