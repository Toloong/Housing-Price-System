#!/usr/bin/env python3
"""
数据库初始化脚本
创建数据库和用户，初始化表结构
"""
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

# 添加backend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.database import DB_CONFIG, init_connection_pool, create_tables, UserManager

def create_database_and_user():
    """创建数据库和用户"""
    print("请输入PostgreSQL超级用户(postgres)的密码:")
    postgres_password = input("postgres密码: ").strip()
    
    if not postgres_password:
        print("密码不能为空")
        return False
    
    # 连接到默认的postgres数据库来创建新数据库
    try:
        # 首先连接到postgres数据库
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database='postgres',  # 连接到默认数据库
            user='postgres',      # 使用postgres超级用户
            password=postgres_password   # 使用用户输入的密码
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("正在创建数据库和用户...")
        
        # 创建用户（如果不存在）
        cursor.execute(f"""
            SELECT 1 FROM pg_roles WHERE rolname='{DB_CONFIG['user']}'
        """)
        if not cursor.fetchone():
            cursor.execute(f"""
                CREATE USER {DB_CONFIG['user']} WITH PASSWORD '{DB_CONFIG['password']}'
            """)
            print(f"用户 {DB_CONFIG['user']} 创建成功")
        else:
            print(f"用户 {DB_CONFIG['user']} 已存在")
        
        # 创建数据库（如果不存在）
        cursor.execute(f"""
            SELECT 1 FROM pg_database WHERE datname='{DB_CONFIG['database']}'
        """)
        if not cursor.fetchone():
            cursor.execute(f"""
                CREATE DATABASE {DB_CONFIG['database']} OWNER {DB_CONFIG['user']}
            """)
            print(f"数据库 {DB_CONFIG['database']} 创建成功")
        else:
            print(f"数据库 {DB_CONFIG['database']} 已存在")
        
        # 授予权限
        cursor.execute(f"""
            GRANT ALL PRIVILEGES ON DATABASE {DB_CONFIG['database']} TO {DB_CONFIG['user']}
        """)
        print("权限授予成功")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"创建数据库/用户失败: {e}")
        print("\n可能的解决方案:")
        print("1. 检查postgres用户密码是否正确")
        print("2. 尝试重置postgres用户密码:")
        print("   sudo -u postgres psql -c \"ALTER USER postgres PASSWORD 'newpassword';\"")
        print("3. 或者使用peer认证（仅限本地）:")
        print("   sudo -u postgres createuser Housing_Price_postgres")
        print("   sudo -u postgres createdb Housing_Price_postgres -O Housing_Price_postgres")
        print("4. 检查pg_hba.conf配置文件")
        
        # 提供一个备用方案
        print("\n是否尝试使用系统用户postgres直接创建？(y/n): ", end="")
        if input().lower() == 'y':
            return create_database_with_system_user()
        
        return False
    except Exception as e:
        print(f"未知错误: {e}")
        return False

def initialize_database():
    """初始化数据库表结构"""
    print("\n正在初始化数据库连接池...")
    if not init_connection_pool():
        print("数据库连接失败")
        return False
    
    print("正在创建数据库表...")
    if not create_tables():
        print("数据库表创建失败")
        return False
    
    print("数据库初始化完成！")
    return True

def create_admin_user():
    """创建管理员用户"""
    print("\n是否要创建管理员用户？(y/n): ", end="")
    if input().lower() == 'y':
        print("请输入管理员信息:")
        username = input("用户名: ").strip()
        email = input("邮箱: ").strip()
        password = input("密码: ").strip()
        full_name = input("全名: ").strip()
        
        if username and email and password:
            result = UserManager.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name if full_name else None
            )
            
            if result["success"]:
                print(f"管理员用户 {username} 创建成功！")
                return True
            else:
                print(f"创建管理员用户失败: {result['message']}")
                return False
        else:
            print("用户名、邮箱和密码不能为空")
            return False
    return True

def create_database_with_system_user():
    """使用系统用户postgres创建数据库（备用方案）"""
    import subprocess
    
    try:
        print("尝试使用系统用户postgres创建数据库...")
        
        # 创建数据库用户
        result = subprocess.run([
            'sudo', '-u', 'postgres', 'createuser', 
            '--no-createdb', '--no-createrole', '--no-superuser',
            DB_CONFIG['user']
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"用户 {DB_CONFIG['user']} 创建成功")
        elif "already exists" in result.stderr:
            print(f"用户 {DB_CONFIG['user']} 已存在")
        else:
            print(f"创建用户失败: {result.stderr}")
        
        # 创建数据库
        result = subprocess.run([
            'sudo', '-u', 'postgres', 'createdb',
            '-O', DB_CONFIG['user'],
            DB_CONFIG['database']
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"数据库 {DB_CONFIG['database']} 创建成功")
        elif "already exists" in result.stderr:
            print(f"数据库 {DB_CONFIG['database']} 已存在")
        else:
            print(f"创建数据库失败: {result.stderr}")
        
        # 设置用户密码
        result = subprocess.run([
            'sudo', '-u', 'postgres', 'psql', '-c',
            f"ALTER USER {DB_CONFIG['user']} PASSWORD '{DB_CONFIG['password']}';"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("用户密码设置成功")
        else:
            print(f"设置密码失败: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"使用系统用户创建失败: {e}")
        return False

def main():
    """主函数"""
    print("=== 房价分析系统数据库初始化 ===\n")
    
    # 步骤1: 创建数据库和用户
    print("步骤1: 创建数据库和用户")
    if not create_database_and_user():
        print("数据库/用户创建失败，退出")
        return False
    
    # 步骤2: 初始化表结构
    print("\n步骤2: 初始化表结构")
    if not initialize_database():
        print("数据库初始化失败，退出")
        return False
    
    # 步骤3: 创建管理员用户（可选）
    print("\n步骤3: 创建管理员用户")
    create_admin_user()
    
    print("\n=== 初始化完成 ===")
    print("现在可以启动应用了:")
    print("uvicorn backend.main:app --reload --port 8000")
    
    return True

if __name__ == "__main__":
    main()
