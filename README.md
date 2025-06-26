# 房价分析系统

本项目是一个全栈房价分析应用，旨在提供一个集数据采集、分析与可视化于一体的平台。

- **后端**: 使用 **FastAPI** 构建，提供高效、标准的 API 接口。
- **前端**: 使用 **Streamlit** 构建，提供一个交互式、响应迅速的用户界面。
- **数据**: 包含从网络爬取的真实房价数据。

## 主要功能

- **房价查询**: 按城市快速搜索和展示房价数据。
- **趋势分析**: 可视化特定城市、特定区域的房价历史走势。
- **城市对比**: 并排比较多个城市的房价指标。
- **动态交互**: 前端页面可根据用户选择（如城市）自动刷新，无需手动点击按钮。

## 技术栈

- **后端**: Python, FastAPI
- **前端**: Python, Streamlit, streamlit-option-menu
- **数据处理**: Pandas

## 目录结构

```
.
├── backend/
│   └── main.py           # FastAPI 应用主文件
├── data/
│   └── housing_data.csv    # 房价数据
├── frontend/
│   ├── app.py            # Streamlit 应用主文件
│   └── style.css         # 前端自定义样式
├── scraper/
│   ├── scraper.py        # 数据爬虫
│   └── mock_data.html    # 爬虫使用的HTML模板
└── README.md
```

## 运行方式

### 1. 环境准备

确保已安装 Python。然后，在项目根目录下创建并激活虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .\.venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```
> **注意**: 如果 `requirements.txt` 文件不存在，请根据需要安装以下核心库：
> `pip install fastapi uvicorn streamlit pandas requests beautifulsoup4 streamlit-option-menu`

### 3. 启动后端服务

在项目根目录下运行：
```bash
uvicorn backend.main:app --reload --port 8000
```
服务将在 `http://127.0.0.1:8000` 上可用。

### 4. 启动前端应用

打开一个新的终端窗口，在项目根目录下运行：
```bash
streamlit run frontend/app.py
```
应用将在浏览器中自动打开。

## API 接口

后端服务提供以下主要接口：

- `GET /search`: 根据城市名称搜索房价数据。
- `GET /trend`: 获取指定城市和区域的房价走势数据。
- `GET /compare`: 获取用于城市房价对比的数据。
- `GET /areas`: 根据城市名称获取其下属的区域列表。

## 更新日志

### 2025-06-26
- 新增 requirements.txt 文件，统一管理项目依赖。
  - 依赖包括 fastapi、uvicorn、psycopg2-binary、pandas、requests、plotly、streamlit、streamlit-option-menu。
- 推荐使用 pip install -r requirements.txt 一键安装所有依赖。
- 优化了依赖管理，便于环境复现和部署。
