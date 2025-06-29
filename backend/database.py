"""
SQLite数据库适配器 - PostgreSQL编码问题的替代方案
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import os

# SQLite数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'housing_price.db')

def init_sqlite_database():
    """初始化SQLite数据库"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # 创建用户令牌表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL
            )
        """)
        
        # 创建用户活动日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_tokens_token ON user_tokens(token)")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"SQLite数据库初始化成功: {DB_PATH}")
        return True
        
    except Exception as e:
        print(f"SQLite数据库初始化失败: {e}")
        return False

class SQLiteUserManager:
    """SQLite用户管理类"""
    
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
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 检查用户名是否已存在
            cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "message": "用户名或邮箱已存在"}
            
            # 创建用户
            hashed_password = SQLiteUserManager.hash_password(password)
            created_at = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, hashed_password, full_name, created_at, 1))
            
            user_id = cursor.lastrowid
            
            # 获取创建的用户信息
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = dict(cursor.fetchone())
            
            conn.commit()
            conn.close()
            
            return {
                "success": True, 
                "message": "用户创建成功",
                "user": user
            }
            
        except Exception as e:
            return {"success": False, "message": f"创建用户失败: {str(e)}"}
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Dict[str, Any]:
        """用户登录认证"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            hashed_password = SQLiteUserManager.hash_password(password)
            cursor.execute("""
                SELECT id, username, email, full_name, created_at, last_login
                FROM users 
                WHERE (username = ? OR email = ?) AND password_hash = ? AND is_active = 1
            """, (username, username, hashed_password))
            
            user_row = cursor.fetchone()
            if not user_row:
                conn.close()
                return {"success": False, "message": "用户名/邮箱或密码错误"}
            
            user = dict(user_row)
            
            # 生成访问令牌
            token = SQLiteUserManager.generate_token()
            expires_at = datetime.now() + timedelta(days=7)  # 7天过期
            
            # 保存令牌
            cursor.execute("""
                INSERT INTO user_tokens (user_id, token, expires_at)
                VALUES (?, ?, ?)
            """, (user['id'], token, expires_at.isoformat()))
            
            # 更新最后登录时间
            cursor.execute("""
                UPDATE users SET last_login = ? WHERE id = ?
            """, (datetime.now().isoformat(), user['id']))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": "登录成功",
                "user": user,
                "token": token,
                "expires_at": expires_at.isoformat()
            }
            
        except Exception as e:
            return {"success": False, "message": f"登录失败: {str(e)}"}
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """验证访问令牌"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT ut.user_id, ut.expires_at, u.username, u.email, u.full_name
                FROM user_tokens ut
                JOIN users u ON ut.user_id = u.id
                WHERE ut.token = ? AND ut.expires_at > ? AND u.is_active = 1
            """, (token, datetime.now().isoformat()))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {"success": False, "message": "令牌无效或已过期"}
            
            result_dict = dict(result)
            return {
                "success": True,
                "user": {
                    "id": result_dict['user_id'],
                    "username": result_dict['username'],
                    "email": result_dict['email'],
                    "full_name": result_dict['full_name']
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"令牌验证失败: {str(e)}"}
    
    @staticmethod
    def get_user_list() -> Dict[str, Any]:
        """获取用户列表"""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, email, full_name, created_at, last_login, is_active
                FROM users
                ORDER BY created_at DESC
            """)
            
            users = [dict(user) for user in cursor.fetchall()]
            conn.close()
            
            return {
                "success": True,
                "users": users
            }
            
        except Exception as e:
            return {"success": False, "message": f"获取用户列表失败: {str(e)}"}

def log_sqlite_user_activity(user_id: int, activity_type: str, activity_data: dict = None):
    """记录用户活动日志"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_activity_logs (user_id, activity_type, activity_data)
            VALUES (?, ?, ?)
        """, (user_id, activity_type, json.dumps(activity_data) if activity_data else None))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"记录用户活动失败: {e}")

if __name__ == "__main__":
    # 初始化数据库
    if init_sqlite_database():
        print("SQLite数据库初始化完成")
        
        # 创建测试用户
        result = SQLiteUserManager.create_user(
            username="admin",
            email="admin@example.com", 
            password="123456",
            full_name="管理员"
        )
        
        if result["success"]:
            print("测试管理员账户创建成功")
        else:
            print(f"创建测试账户失败: {result['message']}")
    else:
        print("SQLite数据库初始化失败")
