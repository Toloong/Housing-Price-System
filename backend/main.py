from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta
import datetime
import os

app = FastAPI(title="房价分析系统后端API")

# 允许跨域，便于前端本地开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
