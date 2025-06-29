#!/bin/bash

# 房价分析系统启动脚本

echo "=== 房价分析系统用户管理功能启动脚本 ==="
echo ""

# 检查Python环境
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请先安装Python3"
    exit 1
fi

# 检查PostgreSQL
echo "检查PostgreSQL服务..."
if ! command -v psql &> /dev/null; then
    echo "⚠️  警告：未找到PostgreSQL，用户管理功能可能不可用"
else
    echo "✅ PostgreSQL 已安装"
fi

# 检查依赖
echo "检查Python依赖..."
if [ -f "requirements.txt" ]; then
    echo "安装依赖包..."
    pip install -r requirements.txt
else
    echo "❌ 未找到requirements.txt文件"
    exit 1
fi

# 数据库初始化选项
echo ""
echo "是否需要初始化数据库？(y/n)"
read -r init_db

if [ "$init_db" = "y" ] || [ "$init_db" = "Y" ]; then
    echo "正在初始化数据库..."
    python3 init_database.py
    if [ $? -eq 0 ]; then
        echo "✅ 数据库初始化完成"
    else
        echo "❌ 数据库初始化失败，但仍可启动基础功能"
    fi
fi

# 启动服务
echo ""
echo "启动选项："
echo "1. 启动后端服务"
echo "2. 启动前端应用"
echo "3. 同时启动前后端（推荐）"
echo "4. 运行功能测试"
echo "请选择 (1-4):"
read -r choice

case $choice in
    1)
        echo "启动后端服务..."
        uvicorn backend.main:app --reload --port 8000
        ;;
    2)
        echo "启动前端应用..."
        streamlit run frontend/app.py
        ;;
    3)
        echo "同时启动前后端服务..."
        echo "后端服务将在端口8000启动"
        echo "前端应用将在端口8501启动"
        echo ""
        # 启动后端服务（后台运行）
        uvicorn backend.main:app --reload --port 8000 &
        BACKEND_PID=$!
        echo "后端服务 PID: $BACKEND_PID"
        
        # 等待后端启动
        sleep 5
        
        # 检查后端是否启动成功
        if curl -s http://127.0.0.1:8000/ > /dev/null; then
            echo "✅ 后端服务启动成功"
        else
            echo "⚠️  后端服务可能启动失败"
        fi
        
        # 启动前端应用
        echo "启动前端应用..."
        streamlit run frontend/app.py
        
        # 清理后台进程
        trap "kill $BACKEND_PID" EXIT
        ;;
    4)
        echo "运行功能测试..."
        python3 test_user_management.py
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac
