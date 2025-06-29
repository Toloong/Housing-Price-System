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

# 导入用户管理相关模块
try:
    from backend.database import init_connection_pool, create_tables, UserManager, log_user_activity
    from backend.auth import (
        UserRegister, UserLogin, LoginResponse, UserResponse,
        validate_username, validate_password, get_current_user, get_optional_user
    )
except ImportError:
    # 备用导入方式
    from database import init_connection_pool, create_tables, UserManager, log_user_activity
    from auth import (
        UserRegister, UserLogin, LoginResponse, UserResponse,
        validate_username, validate_password, get_current_user, get_optional_user
    )

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
    print("正在初始化数据库连接...")
    if init_connection_pool():
        print("正在创建数据库表...")
        create_tables()
        print("数据库初始化完成")
    else:
        print("警告: 数据库连接失败，用户管理功能将不可用")

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

# AI 助手分析函数
def analyze_price_trend(city_data):
    """分析房价趋势"""
    try:
        if city_data.empty:
            return "暂无数据可供分析"
        
        # 按时间排序
        city_data = city_data.sort_values('date')
        recent_data = city_data.tail(6)  # 最近6个月
        
        if len(recent_data) < 2:
            return "数据不足，无法进行趋势分析"
        
        # 计算趋势
        price_change = float(recent_data['price'].iloc[-1] - recent_data['price'].iloc[0])
        price_change_pct = (price_change / float(recent_data['price'].iloc[0])) * 100
        
        trend_analysis = {
            "trend_direction": "上涨" if price_change > 0 else "下跌" if price_change < 0 else "平稳",
            "price_change": round(price_change, 2),
            "price_change_percentage": round(price_change_pct, 2),
            "current_price": round(float(recent_data['price'].iloc[-1]), 2),
            "average_price": round(float(recent_data['price'].mean()), 2),
            "volatility": round(float(recent_data['price'].std()), 2) if len(recent_data) > 1 else 0.0
        }
        
        return trend_analysis
    except Exception as e:
        return f"趋势分析出错: {str(e)}"

def generate_investment_advice(trend_analysis, city, area=None):
    """生成投资建议"""
    if isinstance(trend_analysis, str):
        return trend_analysis
    
    location = f"{city}市{area}区域" if area else f"{city}市"
    advice = []
    
    # 基于趋势的建议
    if trend_analysis["trend_direction"] == "上涨":
        if trend_analysis["price_change_percentage"] > 10:
            advice.append(f"⚠️ {location}房价涨幅较大（{trend_analysis['price_change_percentage']:.1f}%），建议谨慎入市")
        else:
            advice.append(f"📈 {location}房价稳步上涨，可考虑适时入手")
    elif trend_analysis["trend_direction"] == "下跌":
        if trend_analysis["price_change_percentage"] < -5:
            advice.append(f"📉 {location}房价下跌明显，可能是购买时机")
        else:
            advice.append(f"📊 {location}房价略有下调，建议观望")
    else:
        advice.append(f"📏 {location}房价相对稳定，适合长期投资")
    
    # 基于波动性的建议
    if trend_analysis["volatility"] > trend_analysis["average_price"] * 0.1:
        advice.append("⚡ 价格波动较大，投资需谨慎评估风险")
    else:
        advice.append("✅ 价格相对稳定，投资风险较低")
    
    return advice

def analyze_market_insights(city):
    """市场洞察分析"""
    try:
        city_data = df[df['city'] == city].copy()
        if city_data.empty:
            return "暂无该城市数据"
        
        insights = {}
        
        # 最新数据分析
        latest_date = city_data['date'].max()
        latest_data = city_data[city_data['date'] == latest_date]
        
        if not latest_data.empty:
            insights["最高价区域"] = latest_data.loc[latest_data['price'].idxmax(), 'area']
            insights["最低价区域"] = latest_data.loc[latest_data['price'].idxmin(), 'area']
            insights["平均房价"] = round(float(latest_data['price'].mean()), 2)
            insights["价格区间"] = f"{int(latest_data['price'].min())} - {int(latest_data['price'].max())}"
        
        # 时间趋势分析
        monthly_data = city_data.groupby(city_data['date'].dt.to_period('M'))['price'].mean()
        if len(monthly_data) >= 2:
            recent_trend = float(monthly_data.iloc[-1] - monthly_data.iloc[-2])
            insights["月度变化"] = f"{'上涨' if recent_trend > 0 else '下跌'} {abs(recent_trend):.0f}元/平米"
        
        return insights
    except Exception as e:
        return f"市场洞察分析出错: {str(e)}"

@app.post("/ai/analyze")
def ai_analyze(request: AIQueryRequest):
    """AI助手分析接口"""
    try:
        query = request.query.lower()
        city = request.city
        area = request.area
        
        response = {
            "query": request.query,
            "analysis": "",
            "insights": {},
            "recommendations": []
        }
        
        # 根据查询类型提供不同的分析
        if "趋势" in query or "走势" in query:
            if city and area:
                trend_data = df[(df['city'] == city) & (df['area'] == area)]
                trend_analysis = analyze_price_trend(trend_data)
                response["analysis"] = f"{city}{area}区域的房价趋势分析"
                response["insights"] = trend_analysis
                if isinstance(trend_analysis, dict):
                    response["recommendations"] = generate_investment_advice(trend_analysis, city, area)
            elif city:
                city_data = df[df['city'] == city]
                trend_analysis = analyze_price_trend(city_data)
                response["analysis"] = f"{city}市整体房价趋势分析"
                response["insights"] = trend_analysis
                if isinstance(trend_analysis, dict):
                    response["recommendations"] = generate_investment_advice(trend_analysis, city)
            else:
                response["analysis"] = "请指定要分析的城市或区域"
                
        elif "投资" in query or "建议" in query:
            if city:
                city_data = df[df['city'] == city]
                if area:
                    city_data = city_data[city_data['area'] == area]
                trend_analysis = analyze_price_trend(city_data)
                response["analysis"] = f"{city}{'的' + area + '区域' if area else ''}投资建议"
                response["recommendations"] = generate_investment_advice(trend_analysis, city, area)
            else:
                response["analysis"] = "请指定要投资的城市"
                
        elif "洞察" in query or "分析" in query or "市场" in query:
            if city:
                insights = analyze_market_insights(city)
                response["analysis"] = f"{city}市场洞察分析"
                response["insights"] = insights
            else:
                response["analysis"] = "请指定要分析的城市"
                
        elif "对比" in query or "比较" in query:
            response["analysis"] = "请使用城市对比功能进行详细比较"
            response["recommendations"] = ["建议前往'城市对比'页面获取详细的对比分析"]
            
        else:
            # 默认提供市场概览
            if city:
                insights = analyze_market_insights(city)
                response["analysis"] = f"{city}市场概览"
                response["insights"] = insights
                # 添加一些通用建议
                response["recommendations"] = [
                    "建议关注房价趋势变化",
                    "可以查看具体区域的详细分析",
                    "投资前请综合考虑多种因素"
                ]
            else:
                response["analysis"] = "我可以帮您分析房价趋势、提供投资建议、市场洞察等。请告诉我您想了解哪个城市的信息。"
                response["recommendations"] = [
                    "请选择具体城市进行分析",
                    "可以询问：房价趋势、投资建议、市场分析等"
                ]
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI分析失败: {str(e)}")

@app.get("/ai/suggestions")
def get_ai_suggestions(city: str):
    """获取AI建议的问题"""
    suggestions = [
        f"{city}的房价趋势如何？",
        f"{city}适合投资吗？",
        f"{city}的市场分析",
        f"{city}各区域房价对比",
        f"{city}未来房价预测"
    ]
    return {"suggestions": suggestions}

@app.get("/cities")
def get_cities():
    """获取所有可用的城市列表"""
    try:
        cities = sorted(df['city'].unique().tolist())
        return {"cities": cities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取城市列表失败: {str(e)}")


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
    return {
        "success": True,
        "user": current_user
    }

@app.get("/auth/users")
def get_all_users(current_user: dict = Depends(get_current_user)):
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
