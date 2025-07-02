 # 房价分析系统

基于 FastAPI + Streamlit + SQLite 的房价数据分析系统，支持用户管理和数据可视化。

## 🎉 v3.0 重大更新

### ✨ 新增功能
- **🔮 深度学习房价预测**: 支持多种AI模型预测未来房价走势
- **🧠 三种预测模型**: DNN、LSTM和Prophet时序预测
- **📊 预测结果可视化**: 直观展示历史数据与预测趋势对比
- **📈 趋势分析报告**: 自动生成未来房价走势分析报告

### 🧠 AI预测能力
- 基于神经网络的房价趋势预测
- 长短期记忆网络时间序列分析
- Facebook Prophet时序预测模型支持
- 历史数据与预测数据对比图表

## 🎉 v2.0 重大更新

### ✨ 新增功能
- **🔐 独立登录页面系统**: 专业三标签页设计（登录/注册/游客模式）
- **👤 游客模式**: 一键体验系统核心功能，无需注册
- **🛡️ 管理员权限系统**: 基于用户姓名的权限控制，四层安全验证
- **🎨 用户体验优化**: 智能导航、权限状态显示、友好错误提示

### 🔒 安全特性
- 前后端双重权限验证
- 游客模式严格权限隔离  
- 多重安全检查机制
- JWT令牌认证保护

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
├── models/                # 预训练模型存储
│   └── [城市]/[区域]      # 按区域组织的模型文件
├── scraper/               # 数据爬虫(可选)
├── start.bat              # 一键启动脚本
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 🔐 测试账户 & 访问方式

| 用户类型 | 用户名/访问方式 | 密码 | 邮箱 | 权限级别 |
|---------|----------------|------|------|----------|
| **管理员** | admin | 123456 | admin@example.com | 完整系统权限 |
| **普通用户** | testuser | password123 | test@example.com | 基础数据分析权限 |
| **普通用户** | testuser2 | password123 | test2@example.com | 基础数据分析权限 |
| **游客模式** | 一键进入 | 无需密码 | - | 核心功能体验权限 |

### 功能体验路径
1. **新用户**: 选择"游客模式" → 体验系统功能
2. **注册用户**: 选择"注册" → 创建账户 → 完整功能  
3. **管理员**: 选择"登录" → admin/123456 → 管理权限

## 🔐 用户权限管理
- **管理员权限**: 姓名为"管理员"的用户享有完整系统权限
- **普通用户**: 可使用所有数据分析功能，无法访问用户管理
- **游客模式**: 一键体验系统核心功能，权限受限

## 📱 新增登录页面
- **独立登录界面**: 专业的三标签页设计（登录/注册/游客）
- **一键游客模式**: 无需注册即可体验系统功能
- **安全权限控制**: 四层安全验证，确保系统安全性

## 🔮 房价预测功能
- **多模型支持**: DNN、LSTM和Prophet三种预测模型
- **交互式预测**: 可选择城市、区域和预测周期
- **预测可视化**: 直观展示历史数据与预测对比
- **趋势分析**: 自动生成涨跌幅分析报告
- **数据下载**: 支持预测结果CSV导出

## 📊 功能覆盖

### ✅ 所有用户可访问
- 🏠 房价查询和可视化
- 📈 趋势分析和城市对比  
- 🤖 AI智能分析助手
- 📊 数据洞察和统计
- 🔮 房价深度学习预测

### 🔐 仅登录用户可访问
- 💾 个人偏好保存
- 📱 完整用户体验

### 👑 仅管理员可访问
- 👥 用户管理功能
- 📋 用户列表查看
- 📊 系统统计信息

## ⚡ 功能特性

### 🏠 房价分析
- 城市房价查询
- 历史趋势分析  
- 区域价格对比
- 数据可视化图表
- AI智能分析助手

### 🔮 深度学习预测
- DNN全连接神经网络预测
- LSTM长短期记忆网络预测
- Prophet时序预测模型
- 历史与预测数据对比
- 预测结果导出功能

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
- **AI模型**: TensorFlow, Prophet, scikit-learn
- **数据**: CSV数据源，支持爬虫扩展
- **认证**: JWT令牌认证

## 🌍 English Quick Start

### System Requirements
- Windows 10/11 or Linux/macOS
- Python 3.8 or higher
- Git (optional, for cloning repository)

### Installation & Setup
```bash
# Option 1: Automated Setup (Recommended)
git clone https://github.com/Toloong/Housing-Price-System.git
cd Housing-Price-System
setup.bat

# Option 2: Manual Setup
python -m venv .venv
.venv\Scripts\activate.bat  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
python -c "from backend.database import init_sqlite_database; init_sqlite_database()"
```

### Troubleshooting
```bash
# Port conflicts
netstat -ano | findstr :8000
taskkill /f /pid <process_id>

# Reset environment
rmdir /s .venv  # Windows
# rm -rf .venv   # Linux/macOS
python -m venv .venv
pip install -r requirements.txt
```

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

## 🧩 依赖包列表

```bash
# 核心依赖
pip install requests
pip install beautifulsoup4
pip install pandas
pip install fake-useragent

# 深度学习依赖
pip install tensorflow
pip install scikit-learn
pip install prophet
pip install joblib

# 可选但推荐的依赖
pip install lxml  # 更快的HTML解析器
pip install openpyxl  # 如果需要保存为Excel
pip install tqdm  # 进度条显示
```

## 🔧 开发说明

### 主要API接口

#### 房价分析接口
- `GET /search?city=城市名` - 房价查询
- `GET /trend?city=城市名&area=区域` - 趋势分析
- `GET /compare?city1=城市1&city2=城市2` - 城市对比
- `GET /stats?city=城市名` - 统计数据
- `POST /ai/analyze` - AI智能分析
- `POST /predict` - 房价深度学习预测

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

### 房价预测
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "深圳",
    "area": "南山区",
    "model_type": "DNN",
    "periods": 6
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

- [x] 添加更多城市数据
- [x] 实现房价预测模型
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
- ✅ 深度学习房价预测 (v3.0)
- ✅ 多种AI预测模型 (v3.0)
- ✅ 预测结果可视化 (v3.0)
- ✅ 独立登录页面系统 (v2.0)
- ✅ 游客模式一键体验 (v2.0)
- ✅ 管理员权限控制 (v2.0)
- ✅ 四层安全权限验证 (v2.0)
- ✅ 用户注册/登录系统
- ✅ JWT令牌认证机制
- ✅ 房价数据查询分析
- ✅ AI智能分析助手
- ✅ 数据可视化图表
- ✅ 多城市对比功能

### 项目优势
- **即开即用**: 无需复杂的数据库配置，一键启动脚本
- **跨平台**: 支持Windows/Linux/macOS
- **轻量级**: 资源占用极低，SQLite数据库
- **安全可靠**: 多层权限验证，经过全面测试
- **易于部署**: 单文件数据库，便于迁移
- **用户友好**: 游客模式 + 专业登录界面
- **AI预测**: 多种深度学习模型预测房价走势

## 📝 版本历史

### v3.0.0 (2025-07-02)
- 🔮 新增深度学习房价预测功能
- 🧠 支持DNN、LSTM和Prophet三种预测模型
- 📊 新增预测结果可视化与数据导出
- 📈 自动生成预测趋势分析报告
- 🗃️ 添加模型缓存与复用机制

### v2.0.0 (2025-06-29)
- ✨ 新增独立登录页面系统
- 👤 新增游客模式功能  
- 🔐 新增管理员权限控制
- 🛡️ 增强安全验证机制
- 🎨 优化用户界面和体验
- 🔧 修复字符编码问题

### v1.0.0
- 🏠 基础房价分析功能
- 📊 数据可视化和AI助手
- 👥 用户注册登录系统

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

