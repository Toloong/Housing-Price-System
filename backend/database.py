"""
数据库连接和模型定义
"""
import psycopg2
import psycopg2.extras
from psycopg2.pool import SimpleConnectionPool
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'Housing_Price_postgres',
    'user': 'Housing_Price_postgres',
    'password': '123456'
}

# 连接池
connection_pool = None

def init_connection_pool():
    """初始化数据库连接池"""
    global connection_pool
    try:
        connection_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=20,
            **DB_CONFIG
        )
        print("数据库连接池初始化成功")
        return True
    except Exception as e:
        print(f"数据库连接池初始化失败: {e}")
        return False

def get_connection():
    """从连接池获取数据库连接"""
    if connection_pool:
        return connection_pool.getconn()
    return None

def put_connection(conn):
    """将连接返回到连接池"""
    if connection_pool and conn:
        connection_pool.putconn(conn)

class UserManager:
    """用户管理类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def generate_token() -> str:
        """生成访问令牌"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_user(username: str, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
        """创建新用户"""
        conn = get_connection()
        if not conn:
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # 检查用户名是否已存在
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                return {"success": False, "message": "用户名或邮箱已存在"}
            
            # 创建用户
            hashed_password = UserManager.hash_password(password)
            created_at = datetime.now()
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, created_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, username, email, full_name, created_at
            """, (username, email, hashed_password, full_name, created_at, True))
            
            user = cursor.fetchone()
            conn.commit()
            
            return {
                "success": True, 
                "message": "用户创建成功",
                "user": dict(user)
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"创建用户失败: {str(e)}"}
        finally:
            cursor.close()
            put_connection(conn)
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Dict[str, Any]:
        """用户登录认证"""
        conn = get_connection()
        if not conn:
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            hashed_password = UserManager.hash_password(password)
            cursor.execute("""
                SELECT id, username, email, full_name, created_at, last_login
                FROM users 
                WHERE (username = %s OR email = %s) AND password_hash = %s AND is_active = TRUE
            """, (username, username, hashed_password))
            
            user = cursor.fetchone()
            if not user:
                return {"success": False, "message": "用户名/邮箱或密码错误"}
            
            # 生成访问令牌
            token = UserManager.generate_token()
            expires_at = datetime.now() + timedelta(days=7)  # 7天过期
            
            # 保存令牌
            cursor.execute("""
                INSERT INTO user_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            """, (user['id'], token, expires_at))
            
            # 更新最后登录时间
            cursor.execute("""
                UPDATE users SET last_login = %s WHERE id = %s
            """, (datetime.now(), user['id']))
            
            conn.commit()
            
            return {
                "success": True,
                "message": "登录成功",
                "user": dict(user),
                "token": token,
                "expires_at": expires_at.isoformat()
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"登录失败: {str(e)}"}
        finally:
            cursor.close()
            put_connection(conn)
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """验证访问令牌"""
        conn = get_connection()
        if not conn:
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT ut.user_id, ut.expires_at, u.username, u.email, u.full_name
                FROM user_tokens ut
                JOIN users u ON ut.user_id = u.id
                WHERE ut.token = %s AND ut.expires_at > %s AND u.is_active = TRUE
            """, (token, datetime.now()))
            
            result = cursor.fetchone()
            if not result:
                return {"success": False, "message": "令牌无效或已过期"}
            
            return {
                "success": True,
                "user": {
                    "id": result['user_id'],
                    "username": result['username'],
                    "email": result['email'],
                    "full_name": result['full_name']
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"令牌验证失败: {str(e)}"}
        finally:
            cursor.close()
            put_connection(conn)
    
    @staticmethod
    def logout_user(token: str) -> Dict[str, Any]:
        """用户登出"""
        conn = get_connection()
        if not conn:
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            cursor = conn.cursor()
            
            # 删除令牌
            cursor.execute("DELETE FROM user_tokens WHERE token = %s", (token,))
            conn.commit()
            
            return {"success": True, "message": "登出成功"}
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"登出失败: {str(e)}"}
        finally:
            cursor.close()
            put_connection(conn)
    
    @staticmethod
    def get_user_list() -> Dict[str, Any]:
        """获取用户列表（管理员功能）"""
        conn = get_connection()
        if not conn:
            return {"success": False, "message": "数据库连接失败"}
        
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute("""
                SELECT id, username, email, full_name, created_at, last_login, is_active
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = cursor.fetchall()
            
            return {
                "success": True,
                "users": [dict(user) for user in users]
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取用户列表失败: {str(e)}"}
        finally:
            cursor.close()
            put_connection(conn)

def create_tables():
    """创建数据库表"""
    conn = get_connection()
    if not conn:
        print("无法连接数据库")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # 创建用户令牌表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tokens (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        # 创建用户活动日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                activity_type VARCHAR(50) NOT NULL,
                activity_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_tokens_token ON user_tokens(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_tokens_expires ON user_tokens(expires_at)")
        
        conn.commit()
        print("数据库表创建成功")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"创建数据库表失败: {e}")
        return False
    finally:
        cursor.close()
        put_connection(conn)

# 记录用户活动
def log_user_activity(user_id: int, activity_type: str, activity_data: dict = None):
    """记录用户活动日志"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_activity_logs (user_id, activity_type, activity_data)
            VALUES (%s, %s, %s)
        """, (user_id, activity_type, json.dumps(activity_data) if activity_data else None))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"记录用户活动失败: {e}")
    finally:
        cursor.close()
        put_connection(conn)
