import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import os

# 设置页面配置
st.set_page_config(page_title="房价分析系统", page_icon="🏠", layout="wide")

# --- 加载本地 CSS 文件 ---
def load_css(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    try:
        with open(file_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS文件未找到: {file_path}")

# 调用函数加载CSS
load_css("style.css")

# --- 页面主标题 ---
st.markdown("<p class='main-title'>房价分析系统</p>", unsafe_allow_html=True)


# --- 后端 URL ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- 数据加载 --- 
@st.cache_data # 使用缓存来避免重复加载数据
def load_all_cities():
    """从后端加载所有可用的城市列表，这里用固定的列表模拟"""
    # 在真实的系统中，这里可以是一个API调用
    # 为了简单起见，我们直接从已知的数据中获取
    # 注意：这个模拟列表应该与你的 housing_data.csv 保持一致
    try:
        # 尝试从一个（可能不存在的）API端点获取城市列表
        # response = requests.get("http://127.0.0.1:8000/cities")
        # response.raise_for_status()
        # return response.json()["cities"]
        # 目前，我们硬编码这个列表
        return ["北京", "上海", "深圳"]
    except requests.exceptions.RequestException:
        return ["北京", "上海", "深圳"] # 如果API失败，返回一个默认列表

@st.cache_data
def load_areas_for_city(city):
    """为指定城市加载区域列表"""
    try:
        res = requests.get(f"{BACKEND_URL}/areas", params={"city": city})
        if res.status_code == 200:
            return res.json().get("areas", [])
    except requests.exceptions.RequestException:
        return [] # 如果API失败，返回空列表

# --- 页面选择 --- 
page = option_menu(
    menu_title=None,  # 标题已在页面顶部单独显示
    options=["主页", "房价查询", "趋势分析", "城市对比", "数据洞察"],
    icons=['house', 'search', 'graph-up', 'distribute-horizontal', 'clipboard-data'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# --- 主页 ---
if page == "主页":
    st.title("欢迎 🏠")
    st.markdown("""
    这是一个交互式Web应用，旨在帮助您分析和可视化不同城市的房价数据。

    **主要功能:**
    - **房价查询**: 搜索特定城市的最新房价，并以图表形式展示各区域的价格分布。
    - **趋势分析**: 查看特定城市特定区域的房价随时间变化的走势。
    - **城市对比**: 直观地比较两个城市最近半年的平均房价趋势。
    - **数据洞察**: 对单个城市的房价数据进行深入的统计分析，发现数据背后的故事。

    请通过上方的导航栏选择您感兴趣的功能。
    """)

    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            st.success(f"后端服务连接成功: {response.json().get('message')}")
        else:
            st.error("后端服务连接失败，请确保后端服务已启动。")
    except requests.exceptions.ConnectionError:
        st.error("无法连接到后端服务，请检查后端地址和网络连接。")

# --- 房价查询页面 ---
if page == "房价查询":
    st.header("按城市搜索房价")
    cities = load_all_cities()
    city = st.selectbox("请选择城市", cities, index=0)
    st.button("搜索") # 保留按钮用于手动刷新

    # 切换城市后自动查询
    if city:
        try:
            res = requests.get(f"{BACKEND_URL}/search", params={"city": city})
            if res.status_code == 200:
                data = res.json().get("data", [])
                if data:
                    df = pd.DataFrame(data)
                    st.write(f"**{city}** 的房价数据：")
                    st.dataframe(df)

                    st.subheader("各区域房价对比柱状图")
                    fig = px.bar(df, x="area", y="price", title=f"{city}各区域房价对比",
                                 labels={"area": "区域", "price": "价格"})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("未找到该城市的房价数据。")
            else:
                st.error(f"获取数据失败，状态码: {res.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("无法连接到后端服务。")
    else:
        st.warning("请选择一个城市。")

# --- 趋势分析页面 ---
if page == "趋势分析":
    st.header("分析房价走势")
    cities = load_all_cities()
    col1, col2 = st.columns(2)
    with col1:
        trend_city = st.selectbox("请选择城市", cities, index=1, key="trend_city_select")
    with col2:
        areas = load_areas_for_city(trend_city)
        default_area = "黄浦区" if trend_city == "上海" else ("海淀区" if trend_city == "北京" else "南山区")
        
        if areas:
            try:
                default_index = areas.index(default_area)
            except ValueError:
                default_index = 0
            trend_area = st.selectbox("请选择区域", areas, index=default_index, key=f"trend_area_select_{trend_city}")
        else:
            trend_area = st.text_input("请输入区域", default_area, key=f"trend_area_input_{trend_city}")

    st.button("分析走势") # 保留按钮用于手动刷新

    if trend_city and trend_area:
        try:
            res = requests.get(f"{BACKEND_URL}/trend", params={"city": trend_city, "area": trend_area})
            if res.status_code == 200:
                trend_data = res.json().get("trend", [])
                if trend_data:
                    df_trend = pd.DataFrame(trend_data)
                    df_trend['date'] = pd.to_datetime(df_trend['date'])
                    df_trend = df_trend.sort_values('date')

                    st.subheader(f"{trend_city} - {trend_area} 房价走势")
                    fig = px.line(df_trend, x='date', y='price', title="房价走势分析", markers=True,
                                  labels={"date": "日期", "price": "价格"})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("未找到该区域的房价趋势数据。")
            else:
                st.error(f"获取数据失败，状态码: {res.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("无法连接到后端服务。")
    else:
        st.warning("请输入城市和区域。")

# --- 城市对比页面 ---
if page == "城市对比":
    st.header("对比不同城市近6个月房价走势")
    cities = load_all_cities()
    col1, col2 = st.columns(2)
    with col1:
        city1 = st.selectbox("选择城市1", cities, index=0, key="compare_city1_select")
    with col2:
        city2 = st.selectbox("选择城市2", cities, index=1, key="compare_city2_select")

    st.button("开始对比") # 保留按钮用于手动刷新

    if city1 and city2:
        try:
            res = requests.get(f"{BACKEND_URL}/compare", params={"city1": city1, "city2": city2})
            if res.status_code == 200:
                comp_data = res.json()
                trend_data = comp_data.get("trend_data", {})

                if trend_data:
                    st.subheader(f"{city1} vs {city2} 近6个月房价走势对比")
                    
                    all_trends = []
                    for city, trend in trend_data.items():
                        if trend:
                            df = pd.DataFrame(trend)
                            df['城市'] = city
                            all_trends.append(df)
                    
                    if all_trends:
                        df_combined = pd.concat(all_trends, ignore_index=True)
                        df_combined['date'] = pd.to_datetime(df_combined['date']).dt.strftime('%Y-%m')

                        fig = px.bar(df_combined, x='date', y='price', color='城市',
                                     barmode='group',
                                     title=f'{city1} vs {city2} 近6个月房价对比',
                                     labels={'date': '月份', 'price': '价格(元)', '城市': '城市'})
                        st.plotly_chart(fig, use_container_width=True)

                        st.subheader("详细数据")
                        st.write(f"**{city1}** 的详细数据:")
                        st.dataframe(pd.DataFrame(trend_data.get(city1, [])))
                        st.write(f"**{city2}** 的详细数据:")
                        st.dataframe(pd.DataFrame(trend_data.get(city2, [])))
                    else:
                        st.warning("未找到足够的趋势数据进行对比。")
                else:
                    st.warning("未返回有效的对比数据。")
            else:
                st.error(f"获取数据失败，状态码: {res.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("无法连接到后端服务。")
    else:
        st.warning("请输入两个需要对比的城市。")

# --- 数据洞察页面 ---
if page == "数据洞察":
    st.title("城市房价数据洞察")
    st.write("根据最新的房价数据，对单个城市的房价分布进行统计分析，提供更深入的洞察。")

    # 从缓存中加载城市列表
    cities = load_all_cities()
    selected_city_stats = st.selectbox("选择一个城市进行分析", options=cities, key="stats_city_select")

    st.button("获取统计数据", key="get_stats_button") # 保留按钮用于手动刷新

    if selected_city_stats:
        try:
            # 调用后端的 /stats 接口
            response = requests.get(f"{BACKEND_URL}/stats?city={selected_city_stats}")
            response.raise_for_status()  # 如果请求失败则抛出异常
            stats_data = response.json()

            if stats_data and "stats" in stats_data and stats_data["stats"]:
                st.subheader(f"🏙️ {selected_city_stats} 最新房价统计分析")
                stats = stats_data['stats']
                
                # 使用两列布局来展示数据
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(label="平均价格 (元/平米)", value=f"{stats.get('mean', 0):,.2f}")
                    st.metric(label="价格中位数 (元/平米)", value=f"{stats.get('50%', 0):,.2f}")
                    st.metric(label="最高价 (元/平米)", value=f"{stats.get('max', 0):,.0f}")
                    st.metric(label="最低价 (元/平米)", value=f"{stats.get('min', 0):,.0f}")

                with col2:
                    st.metric(label="价格标准差", value=f"{stats.get('std', 0):,.2f}")
                    st.metric(label="价格极差", value=f"{stats.get('range', 0):,.0f}")
                    st.metric(label="价格方差", value=f"{stats.get('variance', 0):,.2f}")
                    st.metric(label="变异系数", value=f"{stats.get('coefficient_of_variation', 0):,.2f}")

                st.info("**指标解读:**\n" 
                        "- **标准差**: 数值越大，说明房价波动范围越广，区域间差异越大。\n"
                        "- **极差**: 最高价与最低价的差距，直观反映价格跨度。\n"
                        "- **变异系数**: 一个相对指标，值越大表示数据越离散，房价水平越不均衡。")

            elif "message" in stats_data:
                st.warning(stats_data["message"])
            else:
                st.error("未能获取有效的统计数据。")

        except requests.exceptions.RequestException as e:
            st.error(f"请求后端服务失败，请确保后端正在运行。错误信息: {e}")
        except Exception as e:
            st.error(f"处理数据时发生未知错误: {e}")
