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
- **数据爬取**: Scrapy

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
│   ├── housing_spider/   # Scrapy 爬虫项目
│   │   ├── spiders/
│   │   │   └── housing_spider.py # 爬虫实现
│   │   ├── items.py      # 数据结构定义
│   │   ├── pipelines.py  # 数据处理管道
│   │   └── settings.py   # 爬虫配置
│   └── mock_data.html    # 爬虫使用的HTML模板
└── README.md
```

## 运行方式 (Windows 用户指南)

本指南将引导您在 Windows 系统上通过 PowerShell 终端运行此项目。

### 1. 环境准备

在项目根目录打开 PowerShell 终端，然后执行以下步骤：

1.  **创建虚拟环境**:
    ```powershell
    python -m venv .venv
    ```

2.  **激活虚拟环境**:
    ```powershell
    .\.venv\Scripts\activate
    ```
    > **PowerShell 错误处理**: 如果激活失败并提示“禁止运行脚本”，请先运行以下命令，然后重试激活。此命令仅为当前终端会话更改执行策略，是安全的操作。
    > ```powershell
    > Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    > ```
    成功激活后，您的终端提示符前应显示 `(.venv)`。

### 2. 安装依赖

确保您的虚拟环境已经激活，然后运行：
```powershell
pip install -r requirements.txt
```

### 3. 启动应用 (需要两个终端)

本项目的前后端需要分别启动。请打开 **两个** PowerShell 终端，并在 **每个终端中都激活虚拟环境** (`.\.venv\Scripts\activate`)。

-   **终端 1: 启动后端服务**
    ```powershell
    uvicorn backend.main:app --reload --port 8000
    ```
    *服务将在 `http://127.0.0.1:8000` 上可用。让此终端保持运行。*

-   **终端 2: 启动前端应用**
    ```powershell
    streamlit run frontend/app.py
    ```
    *应用将在浏览器中自动打开。*

### 4. 更新数据 (可选)

如果需要重新抓取或更新数据，请打开一个新的、已激活虚拟环境的终端，然后运行：
```powershell
cd scraper
scrapy crawl housing_spider
cd ..
```

### 5. 停止应用

当您想停止应用时，请在两个运行服务的终端中分别按下 `Ctrl+C`，或直接点击终端窗口旁的“垃圾桶”图标关闭它们。

## 运行方式 (Linux & macOS 用户指南)

本指南将引导您在 Linux 或 macOS 系统上通过终端运行此项目。

### 1. 环境准备

在项目根目录打开终端，然后执行以下步骤：

1.  **创建虚拟环境**:
    ```bash
    python3 -m venv .venv
    ```

2.  **激活虚拟环境**:
    ```bash
    source .venv/bin/activate
    ```
    *成功激活后，您的终端提示符前应显示 `(.venv)`。*

### 2. 安装依赖

确保您的虚拟环境已经激活，然后运行：
```bash
pip install -r requirements.txt
```

### 3. 启动应用 (需要两个终端)

请打开 **两个** 终端窗口，并在 **每个窗口中都激活虚拟环境** (`source .venv/bin/activate`)。

-   **终端 1: 启动后端服务**
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```

-   **终端 2: 启动前端应用**
    ```bash
    streamlit run frontend/app.py
    ```

### 4. 更新数据 (可选)

如果需要重新抓取或更新数据，请打开一个新的、已激活虚拟环境的终端，然后运行：
```bash
cd scraper
scrapy crawl housing_spider
cd ..
```

### 5. 停止应用

在每个运行服务的终端中按下 `Ctrl+C` 即可停止应用。

## API 接口

后端服务提供以下主要接口：

- `GET /search`: 根据城市名称搜索房价数据。
- `GET /trend`: 获取指定城市和区域的房价走势数据。
- `GET /compare`: 获取用于城市房价对比的数据。
- `GET /areas`: 根据城市名称获取其下属的区域列表。

## 更新日志

### 2025-06-27
- **爬虫重构**: 使用 `Scrapy` 框架完全重构了数据爬虫，替代了原有的 `BeautifulSoup` 脚本。
  - 新的爬虫项目位于 `scraper/housing_spider/`，结构更清晰、功能更强大。
  - 实现了与原脚本相同的去重和数据更新逻辑。
- **项目依赖更新**: 在 `requirements.txt` 中添加了 `scrapy`。
- **文档同步**: 更新了 `README.md` 中的技术栈、目录结构和运行说明。

### 2025-06-26
- 新增 requirements.txt 文件，统一管理项目依赖。
  - 依赖包括 fastapi、uvicorn、psycopg2-binary、pandas、requests、plotly、streamlit、streamlit-option-menu。
- 推荐使用 pip install -r requirements.txt 一键安装所有依赖。
- 优化了依赖管理，便于环境复现和部署。
