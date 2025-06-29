# 🪟 Windows下运行房价分析系统完整指南

本文档为Windows用户提供详细的安装和运行指南，确保您能够顺利在Windows环境下使用房价分析系统。

## 📋 前提条件

### 必需软件
1. **Windows 10/11** - 操作系统
2. **Python 3.8+** - 编程环境
   - 下载地址: https://python.org
   - ⚠️ 安装时务必勾选"Add to PATH"

### 可选软件（用于完整功能）
3. **PostgreSQL 12+** - 数据库（用户管理功能）
   - 下载地址: https://www.postgresql.org/download/windows/
   - 安装时记住postgres用户密码

## 🚀 安装方式选择

### 方式1: 一键安装程序（推荐新用户）

**适用场景**: 首次使用，希望全自动安装

**操作步骤**:
1. 下载项目到本地
2. 双击 `install.bat` 文件
3. 按照提示完成安装
4. 自动启动系统

**特点**:
- ✅ 全自动安装流程
- ✅ 友好的图形界面
- ✅ 智能错误检测
- ✅ 可选数据库配置

### 方式2: PowerShell脚本（推荐日常使用）

**适用场景**: 日常启动，需要灵活控制

**操作步骤**:
1. 右键项目文件夹 → "在终端中打开" 或 "PowerShell"
2. 运行启动脚本:
   ```powershell
   .\start_system.ps1
   ```
3. 选择启动模式（推荐选择"1.自动启动"）

**特点**:
- ✅ 智能环境检测
- ✅ 自动依赖管理
- ✅ 多种启动模式
- ✅ 详细状态提示

### 方式3: 批处理脚本（兼容模式）

**适用场景**: 无法运行PowerShell脚本的环境

**操作步骤**:
1. 双击 `start_system.bat` 文件
2. 选择启动模式
3. 等待系统启动

**特点**:
- ✅ 最大兼容性
- ✅ 无需PowerShell权限
- ✅ 图形化选择界面

### 方式4: 手动安装（高级用户）

**适用场景**: 需要自定义配置或学习系统结构

**操作步骤**:
1. 创建虚拟环境:
   ```cmd
   python -m venv .venv
   ```

2. 激活虚拟环境:
   ```cmd
   .venv\Scripts\activate
   ```

3. 安装依赖:
   ```cmd
   pip install -r requirements.txt
   ```

4. 配置数据库（可选）:
   ```cmd
   python init_database.py
   ```

5. 启动后端（新终端）:
   ```cmd
   .venv\Scripts\activate
   uvicorn backend.main:app --reload --port 8000
   ```

6. 启动前端（另一个新终端）:
   ```cmd
   .venv\Scripts\activate
   streamlit run frontend/app.py
   ```

## 🐘 PostgreSQL数据库配置

### 自动配置（推荐）
```powershell
.\setup_postgresql.ps1
```

### 手动配置
1. **安装PostgreSQL**:
   - 访问 https://www.postgresql.org/download/windows/
   - 下载适合您系统的版本
   - 安装时记住postgres用户密码

2. **配置数据库**:
   ```cmd
   python init_database.py
   ```

### 数据库配置信息
- **数据库名**: Housing_Price_postgres
- **用户名**: Housing_Price_postgres  
- **密码**: 123456
- **主机**: localhost
- **端口**: 5432

## 🌐 访问系统

安装完成后，在浏览器中访问：

| 服务 | 地址 | 用途 |
|-----|------|------|
| **前端应用** | http://localhost:8501 | 🎨 主要用户界面 |
| **后端API** | http://localhost:8000 | 🔧 RESTful API服务 |
| **API文档** | http://localhost:8000/docs | 📚 交互式API文档 |

## 🎯 功能概览

### 核心功能
- **房价查询** 🏠: 按城市搜索最新房价数据
- **趋势分析** 📈: 查看房价历史走势和变化趋势
- **城市对比** 🏙️: 对比不同城市的房价水平
- **数据洞察** 📊: 深入分析房价数据统计信息
- **AI助手** 🤖: 智能分析和投资建议

### 高级功能（需要PostgreSQL）
- **用户注册** 👤: 创建个人账户
- **用户登录** 🔐: 安全身份验证
- **用户管理** 👥: 查看用户列表和活动日志
- **个性化设置**: 保存个人偏好和历史记录

## ❗ 常见问题解决

### PowerShell脚本执行受限

**问题**: 提示"无法加载文件，因为在此系统上禁止运行脚本"

**解决方案**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

然后重新运行脚本。

### Python未找到错误

**问题**: 提示"'python' 不是内部或外部命令"

**解决方案**:
1. 从 https://python.org 下载安装Python
2. 安装时务必勾选"Add to PATH"选项
3. 重启命令提示符窗口
4. 验证安装: `python --version`

### 端口被占用

**问题**: 提示端口8000或8501已被占用

**解决方案**:
```cmd
# 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# 结束占用进程（替换<PID>为实际进程ID）
taskkill /PID <PID> /F
```

### PostgreSQL连接失败

**问题**: 数据库连接失败或用户管理功能不可用

**解决方案**:
1. 检查PostgreSQL服务是否运行:
   ```cmd
   sc query postgresql-x64-13
   ```

2. 启动PostgreSQL服务:
   ```cmd
   net start postgresql-x64-13
   ```

3. 重新配置数据库:
   ```powershell
   .\setup_postgresql.ps1
   ```

### 依赖安装失败

**问题**: pip安装依赖时出错

**解决方案**:
```cmd
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 🔄 更新和维护

### 更新数据
```cmd
cd scraper
scrapy crawl housing_spider
```

### 重置数据库
```cmd
python init_database.py
```

### 清除缓存
在应用界面中点击"刷新页面缓存"按钮，或：
```cmd
# 停止应用后运行
rmdir /s %USERPROFILE%\.streamlit\cache
```

## ⏹️ 停止系统

### 正常停止
在运行脚本的命令行窗口中按 `Ctrl + C`

### 强制停止
```cmd
taskkill /IM python.exe /F
taskkill /IM uvicorn.exe /F
```

### 图形化停止
直接关闭命令行窗口

## 📚 获取更多帮助

- **详细文档**: README.md
- **开发记录**: conversation_history.md  
- **快速参考**: QUICK_START_WINDOWS.md
- **功能测试**: `python test_user_management.py`

## 🎉 成功标志

当看到以下内容时，说明系统启动成功：

**后端启动成功**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

**前端启动成功**:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

浏览器会自动打开，显示房价分析系统主页。

---

🎯 **快速启动**: 双击 `install.bat` → 选择数据库配置 → 访问 http://localhost:8501

✨ 享受使用房价分析系统！
