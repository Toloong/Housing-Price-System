"""
用户认证相关的API接口和中间件
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import re

try:
    from backend.database import UserManager, log_user_activity
except ImportError:
    from database import UserManager, log_user_activity

# HTTP Bearer token security
security = HTTPBearer()

# Pydantic 模型
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "username": "zhangsan",
                "email": "zhangsan@example.com", 
                "password": "password123",
                "full_name": "张三"
            }
        }

class UserLogin(BaseModel):
    username: str  # 可以是用户名或邮箱
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "username": "zhangsan",
                "password": "password123"
            }
        }

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: str
    last_login: Optional[str]

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    token: Optional[str] = None
    expires_at: Optional[str] = None

# 验证函数
def validate_username(username: str) -> bool:
    """验证用户名格式"""
    # 用户名长度3-20，只能包含字母、数字、下划线
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))

def validate_password(password: str) -> bool:
    """验证密码强度"""
    # 密码长度至少6位
    if len(password) < 6:
        return False
    return True

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前登录用户"""
    token = credentials.credentials
    result = UserManager.verify_token(token)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return result["user"]

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))):
    """获取可选的当前用户（不强制登录）"""
    if not credentials:
        return None
    
    token = credentials.credentials
    result = UserManager.verify_token(token)
    
    if result["success"]:
        return result["user"]
    
    return None
