# 房价分析系统

基于 FastAPI + Streamlit + SQLite 的房价数据分析系统，支持用户管理和数据可视化。

## 🚀 快速开始

### 环境安装（首次使用）
```bash
# Windows一键安装
setup.bat
```

### 一键启动（推荐）
```bash
# Windows
start.bat
```

### 手动启动
```bash
# 1. 激活虚拟环境
.\.venv\Scripts\activate

# 2. 启动后端API
python -m uvicorn backend.main:app --reload --port 8000

# 3. 启动前端界面（新终端）
streamlit run frontend/app.py --server.port 8501
```

## 📱 访问地址

- **前端界面**: http://localhost:8501
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 🗂️ 项目结构

```
Housing_Price/
├── backend/                 # 后端API服务
│   ├── main.py             # FastAPI主应用
│   ├── database.py         # SQLite数据库管理
│   └── housing_price.db    # SQLite数据库文件
├── frontend/               # 前端界面
│   ├── app.py             # Streamlit主应用
│   └── style.css          # 样式文件
├── data/                  # 数据文件
│   └── housing_data.csv   # 房价数据
├── scraper/               # 数据爬虫(可选)
├── start.bat              # 一键启动脚本
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 🔐 测试账户

| 用户名 | 密码 | 邮箱 |
|--------|------|------|
| testuser | password123 | test@example.com |
| testuser2 | password123 | test2@example.com |

## ⚡ 功能特性

### 🏠 房价分析
- 城市房价查询
- 历史趋势分析  
- 区域价格对比
- 数据可视化图表
- AI智能分析助手

### 👥 用户管理
- 用户注册/登录
- JWT令牌认证
- 用户权限管理
- 活动日志记录

### 🤖 AI助手功能
- 房价趋势智能分析
- 投资建议生成
- 市场洞察报告
- 自然语言查询

### 🔧 技术栈
- **后端**: FastAPI, SQLite, Pydantic
- **前端**: Streamlit, Pandas, Plotly
- **数据**: CSV数据源，支持爬虫扩展
- **认证**: JWT令牌认证

## 📦 安装依赖

### 自动安装（推荐）
```bash
# Windows - 一键安装环境
setup.bat
```

### 手动安装
```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
# Windows
.\.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 3. 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 4. 初始化数据库
python -c "from backend.database import init_sqlite_database; init_sqlite_database()"
```

## 🔧 开发说明

### 主要API接口

#### 房价分析接口
- `GET /search?city=城市名` - 房价查询
- `GET /trend?city=城市名&area=区域` - 趋势分析
- `GET /compare?city1=城市1&city2=城市2` - 城市对比
- `GET /stats?city=城市名` - 统计数据
- `POST /ai/analyze` - AI智能分析

#### 用户管理接口
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录
- `GET /auth/me` - 获取当前用户信息
- `GET /auth/users` - 获取用户列表

### 数据库
- 使用SQLite本地数据库
- 自动创建表结构
- 支持用户数据和日志存储
- 数据库文件：`backend/housing_price.db`

## 🎯 使用示例

### 用户注册
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "full_name": "新用户"
  }'
```

### 房价查询
```bash
curl "http://localhost:8000/search?city=深圳"
```

### AI分析
```bash
curl -X POST "http://localhost:8000/ai/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "深圳的房价趋势如何？",
    "city": "深圳"
  }'
```

## 🐛 问题排查

### 端口被占用
```bash
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# 终止进程
taskkill /f /pid <进程ID>
```

### 依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 数据库问题
- 如果数据库文件损坏，删除 `backend/housing_price.db` 后重启系统
- 系统会自动重新创建数据库和表结构

## 🚀 部署说明

### 本地开发
1. 克隆项目到本地
2. 安装Python依赖：`pip install -r requirements.txt`
3. 运行启动脚本：`start.bat`

### 生产部署
1. 配置环境变量
2. 使用 Gunicorn 或 Uvicorn 部署后端
3. 配置反向代理 (Nginx)
4. 设置HTTPS证书

## 🛠️ 开发计划

- [ ] 添加更多城市数据
- [ ] 实现房价预测模型
- [ ] 优化AI分析算法
- [ ] 添加邮件通知功能
- [ ] 实现数据导出功能
- [ ] 移动端适配

## 📄 许可证

MIT License

## 📋 项目历程

### 问题解决过程
本项目最初设计使用PostgreSQL数据库，但在Windows环境下遇到了字符编码问题。经过多次尝试修复PostgreSQL的编码配置后，最终采用SQLite作为主要数据库解决方案，不仅解决了编码问题，还简化了部署流程。

### 技术选型对比

#### SQLite vs PostgreSQL
| 特性 | SQLite | PostgreSQL |
|------|--------|------------|
| 安装复杂度 | ⭐⭐⭐⭐⭐ 无需安装 | ⭐⭐ 需要安装配置 |
| 编码问题 | ⭐⭐⭐⭐⭐ 无编码问题 | ⭐ Windows环境编码复杂 |
| 启动速度 | ⭐⭐⭐⭐⭐ 即时启动 | ⭐⭐⭐ 需要服务启动 |
| 资源占用 | ⭐⭐⭐⭐⭐ 极低 | ⭐⭐⭐ 中等 |
| 并发支持 | ⭐⭐⭐ 有限 | ⭐⭐⭐⭐⭐ 优秀 |
| 数据完整性 | ⭐⭐⭐⭐ 良好 | ⭐⭐⭐⭐⭐ 企业级 |

### 已验证功能
- ✅ 用户注册/登录系统
- ✅ JWT令牌认证机制
- ✅ 房价数据查询分析
- ✅ AI智能分析助手
- ✅ 数据可视化图表
- ✅ 多城市对比功能

### 项目优势
- **即开即用**: 无需复杂的数据库配置
- **跨平台**: 支持Windows/Linux/macOS
- **轻量级**: 资源占用极低
- **稳定可靠**: 经过全面测试验证
- **易于部署**: 单文件数据库，便于迁移

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📞 联系方式

如有问题，请通过 GitHub Issues 联系。

---

⭐ 如果这个项目对您有帮助，请给个Star支持一下！