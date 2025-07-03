from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import datetime
import os
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime, timedelta
# 导入数据库模块（使用SQLite）
from backend.database import init_sqlite_database, SQLiteUserManager, log_sqlite_user_activity
UserManager = SQLiteUserManager
log_user_activity = log_sqlite_user_activity
DB_TYPE = "sqlite"

import os
import json
import requests
from typing import Dict, Any, Optional
import pandas as pd

class AIService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "MDc3YWI0YjUtMDdlYi00Y2Y3LTgzMTAtZTA4OGQ5NTBkOGFh"
        self.api_url = "https://chat3.eqing.tech/v1/chat/completions"

        if not self.api_key:
            raise ValueError("AI API密钥未设置")

    def chat_with_ai(self, prompt: str, system_prompt: str = None, temperature: float = 0.3) -> Dict[str, Any]:
        """
        调用AI API进行对话 - 修复版本
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            messages = []

            # 添加系统提示
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            # 添加用户消息
            messages.append({
                "role": "user",
                "content": prompt
            })

            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 1500,  # 减少token数量避免超限
                "stream": False
            }

            print(f"🔄 发送AI请求...")
            print(f"📝 Prompt长度: {len(prompt)} 字符")

            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            print(f"📊 API响应状态: {response.status_code}")

            if response.status_code != 200:
                print(f"❌ API错误响应: {response.text}")
                return {"error": f"API调用失败: {response.status_code} - {response.text}"}

            result = response.json()
            print(f"✅ API调用成功")

            # 提取AI回复内容
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]

                # 直接返回文本内容，不要尝试解析JSON
                return {
                    "text": content,
                    "raw_response": True,
                    "model_used": result.get("model", "gpt-3.5-turbo"),
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0)
                }
            else:
                print(f"❌ API返回格式异常: {result}")
                return {"error": "API返回格式异常"}

        except requests.exceptions.Timeout:
            print("❌ 请求超时")
            return {"error": "请求超时，请稍后重试"}
        except requests.exceptions.ConnectionError:
            print("❌ 网络连接错误")
            return {"error": "网络连接失败"}
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求错误: {str(e)}")
            return {"error": f"网络请求失败: {str(e)}"}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {str(e)}")
            return {"error": f"响应解析失败: {str(e)}"}
        except Exception as e:
            print(f"❌ 未知错误: {str(e)}")
            return {"error": f"AI API调用失败: {str(e)}"}

    def analyze_housing_trend(self, city: str, area: Optional[str], data: pd.DataFrame) -> Dict[str, Any]:
        """
        使用AI分析房价趋势 - 修复版本
        """
        try:
            if data.empty:
                return {"error": "没有足够的数据进行分析"}

            # 数据预处理和统计计算
            data_sorted = data.sort_values('date')
            recent_data = data_sorted.tail(12)  # 最近12个月

            # 计算基础统计
            current_price = float(recent_data['price'].iloc[-1]) if not recent_data.empty else None
            avg_price = float(recent_data['price'].mean()) if not recent_data.empty else None
            price_change = None
            price_change_pct = None

            if len(recent_data) >= 2:
                old_price = float(recent_data['price'].iloc[0])
                price_change = current_price - old_price
                price_change_pct = (price_change / old_price) * 100

            location = f"{city}市{area}区域" if area else f"{city}市"

            # 简化的分析提示，避免过长
            system_prompt = """你是专业的房地产分析师。请用中文分析房价数据，提供简洁实用的分析和建议。"""

            user_prompt = f"""分析{location}房价趋势：

当前价格：{current_price:.0f}元/㎡
平均价格：{avg_price:.0f}元/㎡
价格变化：{price_change_pct:.1f}%
数据期间：{len(recent_data)}个月

请提供：
1. 趋势判断（上涨/下跌/平稳）
2. 价格水平评估
3. 投资建议（3-4条）
4. 风险提示

请用简洁专业的语言回答，重点突出。"""

            print(f"🤖 开始AI分析: {location}")

            # 调用AI API
            result = self.chat_with_ai(user_prompt, system_prompt)

            # 处理AI响应
            if "error" not in result:
                # 添加基础统计数据
                result["basic_stats"] = {
                    "current_price": round(current_price, 2) if current_price else None,
                    "average_price": round(avg_price, 2) if avg_price else None,
                    "price_change": round(price_change, 2) if price_change else None,
                    "price_change_percentage": round(price_change_pct, 2) if price_change_pct else None,
                    "sample_count": len(recent_data),
                    "price_range": {
                        "min": round(float(recent_data['price'].min()), 2),
                        "max": round(float(recent_data['price'].max()), 2)
                    }
                }
                print(f"✅ AI分析完成")
            else:
                print(f"❌ AI分析失败: {result['error']}")

            return result

        except Exception as e:
            print(f"❌ 房价趋势分析出错: {str(e)}")
            return {"error": f"分析失败: {str(e)}"}

# 创建全局服务实例
ai_service = AIService()



# Auth相关模型和函数
from pydantic import BaseModel, EmailStr
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import re

security = HTTPBearer(auto_error=False)

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str  # 可以是用户名或邮箱
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None

class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    token: str
    expires_at: str

def validate_username(username: str) -> bool:
    """验证用户名格式"""
    if not username or len(username) < 3 or len(username) > 50:
        return False
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))

def validate_password(password: str) -> bool:
    """验证密码强度"""
    if not password or len(password) < 6:
        return False
    return True

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前登录用户"""
    token = credentials.credentials
    result = UserManager.verify_token(token)
    if not result.get("success"):
        raise HTTPException(status_code=401, detail="Invalid token")
    return result["user"]

# 添加管理员权限检查函数
def is_admin_user(user: dict) -> bool:
    """检查用户是否为管理员"""
    return user.get("full_name") == "管理员"

def require_admin_permission(current_user: dict = Depends(get_current_user)):
    """要求管理员权限的依赖项"""
    if not is_admin_user(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足：需要管理员权限"
        )
    return current_user

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        return None
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


app = FastAPI(title="房价分析系统后端API")

# 允许跨域，便于前端本地开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    print("正在初始化SQLite数据库...")
    try:
        if init_sqlite_database():
            print("SQLite数据库初始化完成")
        else:
            print("SQLite数据库初始化失败")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        print("系统将以基础模式运行，用户管理功能可能不可用")

# 数据加载
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'housing_data.csv')
df = pd.read_csv(DATA_PATH)
df['date'] = pd.to_datetime(df['date'])


@app.get("/")
def read_root():
    return {"message": "欢迎使用房价分析系统API"}

@app.get("/search")
def search(city: str):
    """按城市名称搜索房价数据"""
    city_df = df[df['city'] == city]
    if city_df.empty:
        return {"city": city, "data": []}
    
    # 获取最新月份的数据
    latest_date = city_df['date'].max()
    latest_df = city_df[city_df['date'] == latest_date]
    
    data = latest_df[['area', 'price']].to_dict(orient='records')
    return {"city": city, "data": data}

@app.get("/areas")
def get_areas(city: str):
    """获取指定城市的所有区域列表"""
    city_df = df[df['city'] == city]
    if city_df.empty:
        return {"city": city, "areas": []}
    
    areas = sorted(city_df['area'].unique().tolist())
    return {"city": city, "areas": areas}

@app.get("/trend")
def trend(city: str, area: str):
    """按区域分析房价走势"""
    trend_df = df[(df['city'] == city) & (df['area'] == area)].copy()
    if trend_df.empty:
        return {"city": city, "area": area, "trend": []}
        
    # 按月分组并计算均价，确保每个月只有一个数据点
    trend_df['date'] = pd.to_datetime(trend_df['date'])
    trend_df['month'] = trend_df['date'].dt.to_period('M')
    monthly_avg = trend_df.groupby('month')['price'].mean().reset_index()
    
    # 格式化日期为 'YYYY-MM' 以便前端展示
    monthly_avg['date'] = monthly_avg['month'].dt.strftime('%Y-%m')
    monthly_avg.sort_values('month', inplace=True)
    
    trend_data = monthly_avg[['date', 'price']].to_dict(orient='records')
    return {"city": city, "area": area, "trend": trend_data}

@app.get("/city_all_trends")
def get_city_all_trends(city: str):
    """获取指定城市所有区域的房价走势数据"""
    try:
        city_df = df[df['city'] == city].copy()
        if city_df.empty:
            raise HTTPException(status_code=404, detail=f"未找到城市 '{city}' 的数据")
        
        # 获取该城市的所有区域
        areas = sorted(city_df['area'].unique())
        
        # 为每个区域计算趋势数据
        all_trends = {}
        for area in areas:
            area_df = city_df[city_df['area'] == area].copy()
            if not area_df.empty:
                # 按月分组并计算均价
                area_df['month'] = area_df['date'].dt.to_period('M')
                monthly_avg = area_df.groupby('month')['price'].mean().reset_index()
                monthly_avg['date'] = monthly_avg['month'].dt.strftime('%Y-%m')
                monthly_avg.sort_values('month', inplace=True)
                
                trend_data = monthly_avg[['date', 'price']].to_dict(orient='records')
                all_trends[area] = trend_data
        
        return {
            "city": city,
            "areas": areas,
            "trends": all_trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取城市趋势数据失败: {str(e)}")

@app.get("/compare")
def compare(city1: str, city2: str):
    """对比不同城市最近6个月的房价走势"""
    
    # 获取数据中最近的日期，并计算6个月前的日期
    latest_date = df['date'].max()
    # 获取最近6个不同的月份
    recent_months = df['date'].dt.to_period('M').unique()
    if len(recent_months) < 6:
        six_months_ago = recent_months.min().to_timestamp()
    else:
        six_months_ago = recent_months[-6].to_timestamp()


    def get_city_trend(city):
        # 筛选出对应城市和最近6个月的数据
        city_df = df[(df['city'] == city) & (df['date'] >= six_months_ago)].copy()
        if city_df.empty:
            return []
        # 按月分组并计算均价
        city_df['month'] = city_df['date'].dt.to_period('M')
        monthly_avg = city_df.groupby('month')['price'].mean().reset_index()
        monthly_avg['date'] = monthly_avg['month'].dt.strftime('%Y-%m')
        monthly_avg.sort_values('month', inplace=True)
        # 确保我们只返回最近6个月的数据
        return monthly_avg.tail(6)[['date', 'price']].to_dict(orient='records')

    trend1 = get_city_trend(city1)
    trend2 = get_city_trend(city2)

    return {
        "trend_data": {
            city1: trend1,
            city2: trend2
        }
    }

@app.get("/stats")
def get_stats(city: str):
    """获取指定城市的最新房价统计数据"""
    try:
        city_df = df[df['city'] == city]
        if city_df.empty:
            raise HTTPException(status_code=404, detail=f"未找到城市 '{city}' 的数据")

        # 获取最新月份的数据
        latest_date = city_df['date'].max()
        latest_df = city_df[city_df['date'] == latest_date]

        if latest_df.empty or latest_df['price'].count() < 2:
            return {"city": city, "stats": {}, "message": f"'{city}' 的最新数据不足(少于2个)，无法进行有效的统计分析"}

        # 计算统计数据
        stats_raw = latest_df['price'].describe()
        stats = stats_raw.to_dict()
        
        # 将 numpy 类型转换为 python 原生类型，确保JSON兼容性
        for key, value in stats.items():
            if isinstance(value, np.integer):
                stats[key] = int(value)
            elif isinstance(value, np.floating):
                stats[key] = round(float(value), 2) # 保留两位小数

        # 添加一些自定义的、更易读的统计项
        stats['range'] = stats['max'] - stats['min'] # 极差
        stats['variance'] = round(latest_df['price'].var(), 2) # 方差
        stats['coefficient_of_variation'] = round(stats['std'] / stats['mean'], 2) if stats['mean'] > 0 else 0 # 变异系数

        return {"city": city, "stats": stats}
    except Exception as e:
        # 通用错误处理
        raise HTTPException(status_code=500, detail=f"处理请求时发生内部错误: {str(e)}")

# Pydantic 模型
class AIQueryRequest(BaseModel):
    query: str
    city: Optional[str] = None
    area: Optional[str] = None



# ==================== 用户管理API接口 ====================

@app.post("/auth/register", response_model=dict)
def register_user(user_data: UserRegister):
    """用户注册"""
    try:
        # 验证用户名格式
        if not validate_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名格式不正确，长度3-20位，只能包含字母、数字、下划线"
            )
        
        # 验证密码强度
        if not validate_password(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="密码长度至少6位"
            )
        
        result = UserManager.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "user": result["user"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@app.post("/auth/login")
def login_user(login_data: UserLogin):
    """用户登录"""
    try:
        result = UserManager.authenticate_user(
            username=login_data.username,
            password=login_data.password
        )
        
        if result["success"]:
            # 记录登录活动
            log_user_activity(
                user_id=result["user"]["id"],
                activity_type="login",
                activity_data={"ip": "127.0.0.1"}  # 在实际部署中可以获取真实IP
            )
            
            return {
                "success": True,
                "message": result["message"],
                "user": result["user"],
                "token": result["token"],
                "expires_at": result["expires_at"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )

@app.post("/auth/logout")
def logout_user(current_user: dict = Depends(get_current_user)):
    """用户登出"""
    try:
        # 注意：这里需要从请求头获取token，实际实现可能需要调整
        # 为简化，我们记录登出活动
        log_user_activity(
            user_id=current_user["id"],
            activity_type="logout"
        )
        
        return {"success": True, "message": "登出成功"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        )

@app.get("/auth/me")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    # 添加管理员身份标识
    user_info = current_user.copy()
    user_info["is_admin"] = is_admin_user(current_user)
    
    return {
        "success": True,
        "user": user_info
    }

@app.get("/auth/users")
def get_all_users(current_user: dict = Depends(require_admin_permission)):
    """获取所有用户列表（管理员功能）"""
    try:
        result = UserManager.get_user_list()
        
        if result["success"]:
            # 记录查看用户列表活动
            log_user_activity(
                user_id=current_user["id"],
                activity_type="view_users"
            )
            
            return {
                "success": True,
                "users": result["users"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )

# ==================== 需要登录的房价分析接口 ====================

@app.get("/protected/search")
def protected_search(city: str, current_user: dict = Depends(get_current_user)):
    """需要登录的房价搜索（示例）"""
    # 记录用户活动
    log_user_activity(
        user_id=current_user["id"],
        activity_type="search",
        activity_data={"city": city}
    )
    
    # 调用原有的搜索功能
    return search(city)

@app.get("/protected/trend")
def protected_trend(city: str, area: str, current_user: dict = Depends(get_current_user)):
    """需要登录的趋势分析（示例）"""
    # 记录用户活动
    log_user_activity(
        user_id=current_user["id"],
        activity_type="trend_analysis",
        activity_data={"city": city, "area": area}
    )
    
    # 调用原有的趋势分析功能
    return trend(city, area)

# 创建预测相关的路由
prediction_router = APIRouter()

# 预测请求模型
class PredictionRequest(BaseModel):
    city: str
    area: str
    model_type: str = "DNN"  # DNN, LSTM, Prophet
    periods: int = 6  # 预测未来几个月
    features: List[str] = ["month", "year", "price"]

# 预测结果模型
class PredictionResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    predictions: Optional[List[dict]] = None
    metrics: Optional[dict] = None

# 加载房价数据
def load_housing_data():
    csv_path = os.path.join("data", "housing_data.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV文件不存在: {csv_path}")

    return pd.read_csv(csv_path)

# 获取预训练模型路径
def get_model_path(city: str, area: str, model_type: str):
    model_dir = os.path.join("models", city, area)
    os.makedirs(model_dir, exist_ok=True)

    filename = f"{model_type.lower()}_model.pkl"
    return os.path.join(model_dir, filename)

# 训练并获取模型
def get_or_train_model(city: str, area: str, model_type: str, df: pd.DataFrame):
    model_path = get_model_path(city, area, model_type)

    # 如果模型已存在并且不超过7天，则直接加载
    if os.path.exists(model_path):
        model_time = os.path.getmtime(model_path)
        if (datetime.now() - datetime.fromtimestamp(model_time)).days < 7:
            return joblib.load(model_path)

    # 否则重新训练模型
    if model_type == "DNN":
        model = train_dnn_model(df)
    elif model_type == "LSTM":
        model = train_lstm_model(df)
    elif model_type == "Prophet":
        model = train_prophet_model(df)
    else:
        raise ValueError(f"不支持的模型类型: {model_type}")

    # 保存模型
    joblib.dump(model, model_path)
    return model

# DNN模型训练函数
def train_dnn_model(df):
    # 简化版实现，实际项目中需要更复杂的模型
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.model_selection import train_test_split
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout

    # 特征工程
    df['month'] = pd.to_datetime(df['date']).dt.month
    df['year'] = pd.to_datetime(df['date']).dt.year

    # 准备数据
    X = df[['month', 'year']].values
    y = df['price'].values

    # 归一化
    X_scaler = MinMaxScaler()
    y_scaler = MinMaxScaler()

    X_scaled = X_scaler.fit_transform(X)
    y_scaled = y_scaler.fit_transform(y.reshape(-1, 1))

    # 模型定义
    model = Sequential([
        Dense(64, activation='relu', input_shape=(X.shape[1],)),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')
    model.fit(X_scaled, y_scaled, epochs=100, verbose=0)

    return {
        'model': model,
        'X_scaler': X_scaler,
        'y_scaler': y_scaler
    }

# LSTM模型训练函数
def train_lstm_model(df):
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from sklearn.preprocessing import MinMaxScaler
    import numpy as np

    # 准备数据
    df = df.sort_values('date')
    prices = df['price'].values.reshape(-1, 1)

    # 归一化
    scaler = MinMaxScaler()
    prices_scaled = scaler.fit_transform(prices)

    # 创建序列数据
    lookback = 6
    X, y = [], []

    for i in range(len(prices_scaled) - lookback):
        X.append(prices_scaled[i:i+lookback])
        y.append(prices_scaled[i+lookback])

    X = np.array(X)
    y = np.array(y)

    # 模型定义
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(lookback, 1)),
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=100, verbose=0)

    return {
        'model': model,
        'scaler': scaler,
        'lookback': lookback
    }

# Prophet模型训练函数
def train_prophet_model(df):
    from prophet import Prophet

    # 准备数据
    prophet_df = df[['date', 'price']].rename(columns={'date': 'ds', 'price': 'y'})

    # 训练模型
    model = Prophet()
    model.fit(prophet_df)

    return model

# 预测接口
@prediction_router.post("/predict", response_model=PredictionResponse)
async def predict_prices(request: PredictionRequest):
    try:
        # 从CSV加载数据
        try:
            all_data = load_housing_data()
        except FileNotFoundError as e:
            return {"success": False, "message": str(e)}

        # 筛选指定城市和区域的数据
        df = all_data[(all_data['city'] == request.city) & (all_data['area'] == request.area)]

        if df.empty:
            return {"success": False, "message": f"没有找到{request.city}{request.area}的历史数据"}

        # 确保日期列为日期类型
        df['date'] = pd.to_datetime(df['date'])

        # 获取或训练模型
        model_data = get_or_train_model(request.city, request.area, request.model_type, df)

        # 生成预测
        last_date = df['date'].max()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=30), periods=request.periods, freq='M')

        if request.model_type == "DNN":
            predictions = predict_with_dnn(model_data, future_dates)
        elif request.model_type == "LSTM":
            predictions = predict_with_lstm(model_data, df, future_dates)
        elif request.model_type == "Prophet":
            predictions = predict_with_prophet(model_data, future_dates)
        else:
            return {"success": False, "message": f"不支持的模型类型: {request.model_type}"}

        # 评估指标
        metrics = calculate_metrics(df)

        return {
            "success": True,
            "predictions": predictions,
            "metrics": metrics
        }

    except Exception as e:
        return {"success": False, "message": f"预测失败: {str(e)}"}

# DNN预测函数
def predict_with_dnn(model_data, future_dates):
    model = model_data['model']
    X_scaler = model_data['X_scaler']
    y_scaler = model_data['y_scaler']

    # 准备未来数据
    future_features = []
    for date in future_dates:
        month = date.month
        year = date.year
        future_features.append([month, year])

    future_features = np.array(future_features)
    future_features_scaled = X_scaler.transform(future_features)

    # 预测
    future_pred_scaled = model.predict(future_features_scaled)
    future_pred = y_scaler.inverse_transform(future_pred_scaled)

    # 返回结果
    predictions = []
    for i, date in enumerate(future_dates):
        predictions.append({
            "date": date.strftime("%Y-%m-%d"),
            "predicted_price": float(future_pred[i][0])
        })

    return predictions

# LSTM预测函数
def predict_with_lstm(model_data, df, future_dates):
    model = model_data['model']
    scaler = model_data['scaler']
    lookback = model_data['lookback']

    # 准备最后一个序列
    prices = df['price'].values.reshape(-1, 1)
    prices_scaled = scaler.transform(prices)
    last_sequence = prices_scaled[-lookback:].reshape(1, lookback, 1)

    # 预测未来
    predictions = []
    current_sequence = last_sequence

    for date in future_dates:
        next_pred = model.predict(current_sequence)[0][0]
        next_pred_original = scaler.inverse_transform([[next_pred]])[0][0]

        predictions.append({
            "date": date.strftime("%Y-%m-%d"),
            "predicted_price": float(next_pred_original)
        })

        # 更新序列
        current_sequence = np.append(current_sequence[0, 1:, 0], next_pred)
        current_sequence = current_sequence.reshape(1, lookback, 1)

    return predictions

# Prophet预测函数
def predict_with_prophet(model, future_dates):
    # 创建未来数据框
    future_df = pd.DataFrame({"ds": future_dates})

    # 预测
    forecast = model.predict(future_df)

    # 返回结果
    predictions = []
    for _, row in forecast.iterrows():
        predictions.append({
            "date": row['ds'].strftime("%Y-%m-%d"),
            "predicted_price": float(row['yhat'])
        })

    return predictions

# 计算评估指标
def calculate_metrics(df):
    # 简单计算统计指标
    return {
        "data_points": len(df),
        "mean_price": float(df['price'].mean()),
        "min_price": float(df['price'].min()),
        "max_price": float(df['price'].max()),
        "std_price": float(df['price'].std())
    }

# 将路由添加到主应用
app.include_router(prediction_router, tags=["prediction"])

class AIChatRequest(BaseModel):
    query: str
    city: Optional[str] = None
    area: Optional[str] = None
    # 可拓展更多上下文字段

@app.post("/ai/assistant")
def ai_assistant(
    req: AIChatRequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """
    AI助手 - 支持通用对话和房价智能分析
    """
    # 记录用户身份（可选）
    user_id = current_user["id"] if current_user else None

    # 如果提供城市/区域，尝试趋势分析，否则为通用对话
    if req.city:
        # 数据筛选
        area_df = df[(df['city'] == req.city)]
        if req.area:
            area_df = area_df[area_df['area'] == req.area]
        if area_df.empty:
            return {"error": f"未找到{req.city}{req.area or ''}的房价数据"}
        result = ai_service.analyze_housing_trend(req.city, req.area, area_df)
        return result
    else:
        # 通用AI对话
        ai_result = ai_service.chat_with_ai(prompt=req.query, system_prompt="你是专业的房地产智能助手，请用中文简明回答用户问题。")
        return ai_result
@app.get("/cities")
def get_cities():
    """获取所有城市列表"""
    cities = sorted(df['city'].unique().tolist())
    return {"cities": cities}

