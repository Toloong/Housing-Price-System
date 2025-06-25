# 房价分析系统后端

本项目基于 FastAPI，提供房价数据的搜索、走势分析、对比等API接口，供前端调用。

## 主要接口
- `/search`：按城市名称搜索房价数据
- `/trend`：按区域、时间分析房价走势
- `/compare`：对比不同城市或品牌房价

## 运行方式
1. 安装依赖：`pip install fastapi uvicorn`
2. 启动服务：`uvicorn backend.main:app --reload`

## 目录结构建议
- backend/
  - main.py  # FastAPI主入口
  - api/     # 各功能API模块
  - services/# 业务逻辑
  - models/  # 数据模型
  - utils/   # 工具函数

## 说明
- 后续可扩展爬虫、数据分析、数据库等模块。
