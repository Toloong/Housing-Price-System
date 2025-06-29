#!/bin/bash

# PostgreSQL快速设置脚本

echo "=== PostgreSQL 快速设置脚本 ==="
echo ""

# 检查是否为root用户或有sudo权限
if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
    echo "此脚本需要sudo权限来设置PostgreSQL"
    exit 1
fi

echo "选择设置方式："
echo "1. 重置postgres用户密码为123456"
echo "2. 使用系统用户postgres直接创建数据库"
echo "3. 检查PostgreSQL配置"
echo "4. 完全重新安装PostgreSQL"
echo "请选择 (1-4): "
read -r choice

case $choice in
    1)
        echo "重置postgres用户密码..."
        sudo -u postgres psql -c "ALTER USER postgres PASSWORD '123456';"
        if [ $? -eq 0 ]; then
            echo "✅ postgres密码已重置为: 123456"
            echo "现在可以运行: python3 init_database.py"
        else
            echo "❌ 密码重置失败"
        fi
        ;;
    2)
        echo "使用系统用户创建数据库..."
        
        # 创建用户
        sudo -u postgres createuser --no-createdb --no-createrole --no-superuser Housing_Price_postgres 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ 用户 Housing_Price_postgres 创建成功"
        else
            echo "⚠️  用户 Housing_Price_postgres 可能已存在"
        fi
        
        # 创建数据库
        sudo -u postgres createdb -O Housing_Price_postgres Housing_Price_postgres 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ 数据库 Housing_Price_postgres 创建成功"
        else
            echo "⚠️  数据库 Housing_Price_postgres 可能已存在"
        fi
        
        # 设置密码
        sudo -u postgres psql -c "ALTER USER Housing_Price_postgres PASSWORD '123456';"
        if [ $? -eq 0 ]; then
            echo "✅ 用户密码设置成功"
        else
            echo "❌ 密码设置失败"
        fi
        
        echo "数据库设置完成！"
        echo "现在可以直接运行: python3 -c \"from backend.database import init_connection_pool, create_tables; init_connection_pool(); create_tables()\""
        ;;
    3)
        echo "检查PostgreSQL配置..."
        
        echo "PostgreSQL服务状态:"
        sudo systemctl status postgresql --no-pager -l
        
        echo -e "\nPostgreSQL版本:"
        sudo -u postgres psql -c "SELECT version();" 2>/dev/null || echo "无法连接到PostgreSQL"
        
        echo -e "\n当前数据库列表:"
        sudo -u postgres psql -l 2>/dev/null || echo "无法获取数据库列表"
        
        echo -e "\n配置文件位置:"
        sudo -u postgres psql -c "SHOW config_file;" 2>/dev/null || echo "无法获取配置文件位置"
        ;;
    4)
        echo "完全重新安装PostgreSQL..."
        echo "⚠️  这将删除所有现有数据！"
        echo "确认继续？(输入 YES 继续): "
        read -r confirm
        
        if [ "$confirm" = "YES" ]; then
            echo "停止PostgreSQL服务..."
            sudo systemctl stop postgresql
            
            echo "卸载PostgreSQL..."
            sudo apt remove --purge postgresql* -y
            sudo apt autoremove -y
            
            echo "清理数据目录..."
            sudo rm -rf /var/lib/postgresql/
            sudo rm -rf /etc/postgresql/
            
            echo "重新安装PostgreSQL..."
            sudo apt update
            sudo apt install postgresql postgresql-contrib -y
            
            echo "启动PostgreSQL服务..."
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            
            echo "设置postgres用户密码..."
            sudo -u postgres psql -c "ALTER USER postgres PASSWORD '123456';"
            
            echo "✅ PostgreSQL重新安装完成！"
            echo "postgres用户密码已设置为: 123456"
        else
            echo "操作已取消"
        fi
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "设置完成后，可以尝试运行:"
echo "python3 init_database.py"
