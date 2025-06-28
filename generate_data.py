#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
房价数据生成脚本
生成包含广州、深圳、北京、上海、杭州、重庆6个城市的房价模拟数据
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_housing_data():
    """生成房价模拟数据"""
    
    # 城市配置 - 每个城市的区域和基础房价
    cities_config = {
        "北京": {
            "areas": ["东城区", "西城区", "朝阳区", "海淀区", "丰台区", "石景山区"],
            "base_prices": [115000, 135000, 88000, 105000, 75000, 68000]
        },
        "上海": {
            "areas": ["黄浦区", "徐汇区", "静安区", "浦东新区", "虹口区", "杨浦区"],
            "base_prices": [110000, 95000, 105000, 85000, 78000, 82000]
        },
        "深圳": {
            "areas": ["福田区", "南山区", "龙华区", "宝安区", "龙岗区", "罗湖区"],
            "base_prices": [92000, 98000, 73000, 78000, 65000, 75000]
        },
        "广州": {
            "areas": ["天河区", "越秀区", "荔湾区", "海珠区", "白云区", "番禺区"],
            "base_prices": [85000, 78000, 72000, 75000, 55000, 48000]
        },
        "杭州": {
            "areas": ["西湖区", "上城区", "拱墅区", "余杭区", "萧山区", "滨江区"],
            "base_prices": [75000, 68000, 58000, 52000, 48000, 88000]
        },
        "重庆": {
            "areas": ["渝中区", "江北区", "南岸区", "九龙坡区", "沙坪坝区", "渝北区"],
            "base_prices": [35000, 32000, 28000, 25000, 22000, 30000]
        }
    }
    
    # 生成时间序列 - 从2023年1月到2025年6月
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 6, 1)
    
    # 生成月度时间点
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        # 下个月的第一天
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    print(f"生成时间范围: {start_date.strftime('%Y-%m')} 到 {end_date.strftime('%Y-%m')}")
    print(f"时间点数量: {len(dates)}")
    
    # 生成数据
    data = []
    
    for i, date in enumerate(dates):
        for city, config in cities_config.items():
            areas = config["areas"]
            base_prices = config["base_prices"]
            
            for j, (area, base_price) in enumerate(zip(areas, base_prices)):
                # 计算房价趋势
                # 整体趋势：缓慢上涨 + 季节性波动 + 随机波动
                
                # 1. 时间趋势 (每月增长0.2%-0.8%)
                time_trend = 1 + (i * random.uniform(0.002, 0.008))
                
                # 2. 季节性波动 (春秋季较高，冬夏季较低)
                month = date.month
                if month in [3, 4, 5, 9, 10, 11]:  # 春秋季
                    seasonal_factor = random.uniform(1.02, 1.08)
                elif month in [1, 2, 7, 8]:  # 冬夏季
                    seasonal_factor = random.uniform(0.95, 1.02)
                else:  # 其他月份
                    seasonal_factor = random.uniform(0.98, 1.05)
                
                # 3. 城市特殊因素
                city_factors = {
                    "北京": random.uniform(0.98, 1.05),
                    "上海": random.uniform(0.97, 1.04),
                    "深圳": random.uniform(1.00, 1.08),  # 深圳波动较大
                    "广州": random.uniform(0.95, 1.03),
                    "杭州": random.uniform(0.96, 1.06),
                    "重庆": random.uniform(0.92, 1.04)
                }
                
                # 4. 区域因素
                area_premium = {
                    "核心区": random.uniform(1.05, 1.15),
                    "次核心区": random.uniform(1.00, 1.08),
                    "一般区": random.uniform(0.90, 1.02)
                }
                
                # 判断区域类型
                core_areas = ["东城区", "西城区", "黄浦区", "静安区", "福田区", "南山区", 
                             "天河区", "越秀区", "西湖区", "上城区", "渝中区"]
                if area in core_areas:
                    area_factor = area_premium["核心区"]
                elif j < 3:  # 前3个区域视为次核心
                    area_factor = area_premium["次核心区"]
                else:
                    area_factor = area_premium["一般区"]
                
                # 5. 随机波动 (-5% 到 +5%)
                random_factor = random.uniform(0.95, 1.05)
                
                # 计算最终价格
                final_price = (base_price * time_trend * seasonal_factor * 
                             city_factors[city] * area_factor * random_factor)
                
                # 取整到最近的10
                final_price = round(final_price / 10) * 10
                
                data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'city': city,
                    'area': area,
                    'price': int(final_price)
                })
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    print(f"生成数据总数: {len(df)}")
    print(f"城市数量: {df['city'].nunique()}")
    print(f"每个城市的区域数: {df.groupby('city')['area'].nunique().to_dict()}")
    print(f"时间跨度: {df['date'].min()} 到 {df['date'].max()}")
    
    return df

def main():
    """主函数"""
    print("开始生成房价数据...")
    
    # 生成数据
    df = generate_housing_data()
    
    # 保存到CSV文件
    output_file = "/home/rcore/桌面/Housing_Price_Analysis_System/house_price_analyizing/data/housing_data.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n数据已保存到: {output_file}")
    print(f"数据行数: {len(df)}")
    
    # 显示数据概览
    print("\n数据概览:")
    print(df.head(10))
    
    print("\n各城市数据统计:")
    city_stats = df.groupby('city').agg({
        'price': ['count', 'mean', 'min', 'max'],
        'area': 'nunique'
    }).round(2)
    city_stats.columns = ['记录数', '平均价格', '最低价格', '最高价格', '区域数']
    print(city_stats)
    
    print("\n✅ 数据生成完成！")

if __name__ == "__main__":
    main()
