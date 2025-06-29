# Windows 快速安装指南

本指南专为Windows用户提供最简单的安装和运行方式。

## 📋 系统要求

- Windows 10/11
- Python 3.8 或更高版本
- PostgreSQL 12+ (可选，用于用户管理功能)

## 🚀 一键安装和启动

### 方法一：PowerShell脚本 (推荐)

1. **下载项目到本地**
2. **右键点击项目文件夹，选择"在终端中打开"或"PowerShell"**
3. **运行启动脚本**：
   ```powershell
   .\start_system.ps1
   ```
4. **按照提示操作**

### 方法二：批处理脚本

1. **双击运行 `start_system.bat` 文件**
2. **按照提示操作**

### 方法三：手动安装

1. **打开PowerShell或命令提示符**
2. **导航到项目目录**：
   ```cmd
   cd path\to\house_price_analyizing
   ```
3. **创建虚拟环境**：
   ```cmd
   python -m venv .venv
   ```
4. **激活虚拟环境**：
   ```cmd
   .venv\Scripts\activate
   ```
5. **安装依赖**：
   ```cmd
   pip install -r requirements.txt
   ```
6. **启动后端** (新终端窗口)：
   ```cmd
   .venv\Scripts\activate
   uvicorn backend.main:app --reload --port 8000
   ```
7. **启动前端** (另一个新终端窗口)：
   ```cmd
   .venv\Scripts\activate
   streamlit run frontend/app.py
   ```

## 🐘 PostgreSQL 安装 (可选)

如果需要用户管理功能，请安装PostgreSQL：

### 自动安装脚本
```powershell
.\setup_postgresql.ps1
```

### 手动安装
1. **下载PostgreSQL**：访问 https://www.postgresql.org/download/windows/
2. **运行安装程序**，记住postgres用户密码
3. **设置数据库**：
   ```powershell
   .\setup_postgresql.ps1
   ```
4. **初始化应用数据库**：
   ```cmd
   python init_database.py
   ```

## 🌐 访问应用

安装完成后，在浏览器中访问：

- **前端应用**: http://localhost:8501
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## ❗ 常见问题

### PowerShell执行策略问题
如果遇到"无法加载文件，因为在此系统上禁止运行脚本"错误：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### Python未找到
确保Python已安装并添加到系统PATH中。从 https://python.org 下载安装。

### 端口占用
如果8000或8501端口被占用，可以修改端口：

```cmd
# 修改后端端口
uvicorn backend.main:app --reload --port 8001

# 修改前端端口  
streamlit run frontend/app.py --server.port 8502
```

### 数据库连接失败
1. 确认PostgreSQL服务正在运行
2. 检查用户名密码是否正确
3. 运行数据库设置脚本重新配置

## 📞 获取帮助

如遇到问题，请查看：
1. **详细文档**: README.md
2. **开发历程**: conversation_history.md
3. **错误日志**: 终端输出的错误信息

## 🔧 开发环境

如需进行开发或定制：

```cmd
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python test_user_management.py

# 更新数据
cd scraper
scrapy crawl housing_spider
```
