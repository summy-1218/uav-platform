# GitHub 发布与 Streamlit 部署指南

## 步骤 1: 在 GitHub 创建新仓库

1. 访问 [GitHub](https://github.com/new)
2. 登录您的账号 `summy-1218`
3. 填写仓库信息：
   - **仓库名称**: `uav-python` (推荐) 或其他名称
   - **描述**: 无人机系统数字化资源平台 - 基于 Streamlit 的教学工具
   - **可见性**: 选择 Public (公开) 或 Private (私有)
4. 不要勾选 "Initialize this repository with a README" (因为本地已有)
5. 点击 "Create repository"

## 步骤 2: 本地 Git 操作

打开命令行（PowerShell 或 Git Bash），进入项目目录：

```bash
cd "d:\10 飞行学院日常工作\202405 教改项目\uav-python"
```

### 2.1 查看远程仓库

```bash
git remote -v
```

如果已有远程仓库，删除它：

```bash
git remote remove origin
```

### 2.2 添加新的远程仓库

将下面的 `YOUR_REPO_URL` 替换为您创建的仓库地址：

```bash
git remote add origin https://github.com/summy-1218/uav-python.git
```

### 2.3 查看当前状态

```bash
git status
```

### 2.4 添加所有文件

```bash
git add .
```

### 2.5 创建初始提交

```bash
git commit -m "Initial commit: 无人机系统数字化资源平台"
```

### 2.6 推送到 GitHub

```bash
git branch -M main
git push -u origin main
```

如果遇到用户名/密码提示，请使用您的 GitHub Personal Access Token：
- 创建 Token: Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
- 权限选择: `repo`
- 使用 Token 作为密码

## 步骤 3: Streamlit Cloud 部署

### 3.1 访问 Streamlit Cloud

1. 打开 [Streamlit Community Cloud](https://share.streamlit.io/)
2. 点击右上角 "Sign up" 或 "Sign in"
3. 使用 GitHub 账号登录（选择 `summy-1218` 账号）

### 3.2 创建新应用

1. 点击 "New app" 按钮
2. 填写部署配置：
   - **Repository**: 选择 `uav-python` (或您创建的仓库名)
   - **Branch**: `main`
   - **Main file path**: `Hello.py` (必须与实际文件名一致)
   - **App URL**: 自动生成（可自定义，如 `summy-uav-platform`）
3. 点击 "Deploy" 开始部署

### 3.3 部署过程

Streamlit 会自动：
1. 克隆您的代码仓库
2. 创建虚拟环境
3. 安装 `requirements.txt` 中的依赖
4. 启动应用

通常需要 2-5 分钟完成。

### 3.4 访问应用

部署成功后，您会看到：
- **应用 URL**: `https://summy-uav-platform.streamlit.app` (示例)
- **应用状态**: Running (运行中)

## 步骤 4: 项目优化建议

### 4.1 更新 README.md

确保 `README.md` 包含：
- 项目描述
- 功能特性
- 安装说明
- 部署链接（部署成功后添加）

### 4.2 requirements.txt 确认

确保包含所有必要依赖：

```
streamlit
pandas
plotly
scikit-learn
openpyxl
Pillow
requests
```

### 4.3 .gitignore 确认

确保 `.gitignore` 包含：

```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
# Streamlit
.streamlit/
# 数据文件 (可选)
# data/*.json
# data/cases/*.md
# 图片文件 (可选)
# assets/*
```

**注意**: 如果不想上传数据文件，取消注释最后几行。

## 步骤 5: 更新代码

当您修改代码后：

```bash
git add .
git commit -m "更新描述"
git push
```

Streamlit Cloud 会自动检测推送并重新部署。

## 常见问题

### Q1: 推送时出现身份验证错误

**解决方案**:
1. 使用 Personal Access Token 替代密码
2. 或使用 SSH 密钥（推荐）

### Q2: Streamlit 部署失败

**检查项目**:
1. `Hello.py` 文件名是否正确
2. `requirements.txt` 是否存在且格式正确
3. 代码是否有语法错误

### Q3: 数据文件访问问题

Streamlit Cloud 是无状态的，数据不会持久化。如果需要数据：

**选项 1**: 使用 Streamlit 共享目录
```python
import os
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
```

**选项 2**: 连接外部数据库
- 使用 PostgreSQL + Supabase
- 或其他云数据库服务

**选项 3**: 允许用户上传数据
- 已在"数据管理"页面实现

### Q4: 图片无法显示

确保图片路径正确：
- 本地图片放在 `assets/` 目录
- 使用相对路径: `"玄峰无人僚机.png"`
- 或使用网络 URL

## 增强功能建议

部署后可以考虑：

1. **添加用户认证**
   - Streamlit Cloud 支持的第三方认证
   - 或简单的密码保护

2. **添加日志记录**
   - 记录用户操作
   - 错误追踪

3. **性能优化**
   - 添加缓存机制
   - 优化数据加载

4. **多语言支持**
   - 中英文切换
   - 国际化文本管理

## 联系方式

- GitHub: https://github.com/summy-1218
- 项目地址: https://github.com/summy-1218/uav-python (推送后生效)
- Streamlit 应用: (部署成功后添加)

---

祝您发布成功！🚀
