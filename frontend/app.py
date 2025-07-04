import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import os
import pandas as pd
import json
from datetime import datetime

# 设置页面配置
st.set_page_config(page_title="房价分析系统", page_icon="🏠", layout="wide")

# ================ 用户认证相关函数 ================

def init_session_state():
    """初始化会话状态"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'auth_token' not in st.session_state:
        st.session_state.auth_token = None
    if 'user_mode' not in st.session_state:
        st.session_state.user_mode = None  # 'logged_in', 'guest', None
    if 'show_main_app' not in st.session_state:
        st.session_state.show_main_app = False

def login_user(username, password):
    """用户登录"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", json={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                # 获取完整的用户信息（包括管理员标识）
                try:
                    me_response = requests.get(f"{BACKEND_URL}/auth/me", headers={"Authorization": f"Bearer {data['token']}"})
                    if me_response.status_code == 200:
                        me_data = me_response.json()
                        if me_data.get("success"):
                            user_login_success(me_data["user"], data["token"])
                        else:
                            user_login_success(data["user"], data["token"])
                    else:
                        user_login_success(data["user"], data["token"])
                except:
                    user_login_success(data["user"], data["token"])
                
                return True, "登录成功！"
            else:
                return False, data.get("message", "登录失败")
        else:
            error_data = response.json()
            return False, error_data.get("detail", "登录失败")
    except Exception as e:
        return False, f"登录出错: {str(e)}"

def register_user(username, email, password, full_name=None):
    """用户注册"""
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", json={
            "username": username,
            "email": email,
            "password": password,
            "full_name": full_name
        })
        
        if response.status_code == 200:
            data = response.json()
            return data["success"], data.get("message", "注册成功")
        else:
            error_data = response.json()
            return False, error_data.get("detail", "注册失败")
    except Exception as e:
        return False, f"注册出错: {str(e)}"

def logout_user():
    """用户登出"""
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.session_state.auth_token = None
    st.session_state.user_mode = None
    st.session_state.show_main_app = False

def guest_login():
    """游客登录"""
    st.session_state.logged_in = False
    st.session_state.user_info = None
    st.session_state.auth_token = None
    st.session_state.user_mode = "guest"
    st.session_state.show_main_app = True

def user_login_success(user_data, token):
    """用户登录成功处理"""
    st.session_state.logged_in = True
    st.session_state.user_info = user_data
    st.session_state.auth_token = token
    st.session_state.user_mode = "logged_in"
    st.session_state.show_main_app = True

def get_auth_headers():
    """获取认证请求头"""
    if st.session_state.auth_token:
        return {"Authorization": f"Bearer {st.session_state.auth_token}"}
    return {}

def check_login_status():
    """检查登录状态"""
    if st.session_state.logged_in and st.session_state.auth_token:
        try:
            response = requests.get(f"{BACKEND_URL}/auth/me", headers=get_auth_headers())
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # 更新用户信息，包括管理员标识
                    st.session_state.user_info = data["user"]
                    return True
            # Token无效，清除登录状态
            logout_user()
            return False
        except:
            return False
    return False

# --- 后端 URL ---
BACKEND_URL = "http://127.0.0.1:8000"

# 初始化会话状态
init_session_state()

# --- 加载本地 CSS 文件 ---
def load_css(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    try:
        # 获取文件修改时间作为版本号，实现缓存破坏
        import time
        file_mtime = os.path.getmtime(file_path)
        version = str(int(file_mtime))
        
        with open(file_path, encoding='utf-8') as f:
            css_content = f.read()
            # 添加版本注释来确保CSS更新
            css_with_version = f"/* CSS Version: {version} */\n{css_content}"
            st.markdown(f'<style>{css_with_version}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS文件未找到: {file_path}")
    except Exception as e:
        st.error(f"加载CSS文件失败: {str(e)}")

# 调用函数加载CSS
load_css("style.css")

def render_basic_stats(stats: dict):
    """将基础统计数据友好地用中文格式化输出"""
    if not stats:
        st.info("暂无基础统计信息")
        return

    # 字段名映射
    field_map = {
        "current_price": "当前价格",
        "average_price": "平均价格",
        "price_change": "价格变化",
        "price_change_percentage": "价格变化幅度",
        "sample_count": "统计月数",
        "price_range": "价格区间"
    }
    # 展示主统计
    st.markdown("#### 📊 基础统计信息")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(field_map["current_price"], f'{int(stats.get("current_price", 0)):,} 元/㎡')
        st.metric(field_map["average_price"], f'{int(stats.get("average_price", 0)):,} 元/㎡')
    with col2:
        st.metric(field_map["price_change"], f'{stats.get("price_change", 0):,.0f} 元')
        st.metric(field_map["price_change_percentage"], f'{stats.get("price_change_percentage", 0):.2f} %')
    with col3:
        st.metric(field_map["sample_count"], f'{stats.get("sample_count", 0)} 个月')
        pr = stats.get("price_range", {})
        st.metric(field_map["price_range"], f'{int(pr.get("min",0)):,} ~ {int(pr.get("max",0)):,} 元/㎡')


# 添加页面刷新按钮到侧边栏（用于开发调试）
with st.sidebar:
    if st.button("🔄 刷新页面缓存", help="如果页面显示异常，点击此按钮清除缓存"):
        st.cache_data.clear()
        st.rerun()

# --- 页面主标题 ---
st.markdown("<p class='main-title'>房价分析系统</p>", unsafe_allow_html=True)


# --- 后端 URL ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- 数据加载 --- 
@st.cache_data(ttl=300)  # 5分钟缓存，避免缓存过久导致的问题
def load_all_cities():
    """从后端加载所有可用的城市列表"""
    try:
        # 尝试从后端API获取城市列表
        response = requests.get(f"{BACKEND_URL}/cities", timeout=5)
        if response.status_code == 200:
            return response.json().get("cities", [])
        else:
            # API失败时返回默认列表
            return ["北京", "上海", "深圳", "广州", "杭州", "重庆"]
    except requests.exceptions.RequestException:
        # 如果API失败，返回默认列表
        return ["北京", "上海", "深圳", "广州", "杭州", "重庆"]

@st.cache_data(ttl=300)  # 5分钟缓存
def load_areas_for_city(city):
    """为指定城市加载区域列表"""
    try:
        res = requests.get(f"{BACKEND_URL}/areas", params={"city": city}, timeout=5)
        if res.status_code == 200:
            return res.json().get("areas", [])
    except requests.exceptions.RequestException:
        return []  # 如果API失败，返回空列表

# --- 页面状态管理 ---
def initialize_page_state():
    """初始化页面状态，防止状态混乱"""
    if 'page_initialized' not in st.session_state:
        st.session_state.page_initialized = True
        # 清除可能的旧状态
        for key in list(st.session_state.keys()):
            if key.startswith('temp_'):
                del st.session_state[key]

# --- 检查用户是否为管理员的函数 ---
def is_current_user_admin():
    """检查当前用户是否为管理员"""
    if st.session_state.user_info:
        return st.session_state.user_info.get("is_admin", False)
    return False

# 初始化页面状态
initialize_page_state()

# --- 登录页面组件 ---
def show_login_page():
    """显示登录页面"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>🏠 房价分析系统</h1>
        <p style="font-size: 1.2rem; color: #666;">专业的房价数据分析平台</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建三列布局
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # 选择登录方式
        login_tab, register_tab, guest_tab = st.tabs(["🔑 登录", "📝 注册", "👤 游客模式"])
        
        with login_tab:
            show_login_form()
            
        with register_tab:
            show_register_form()
            
        with guest_tab:
            show_guest_login()

def show_login_form():
    """显示登录表单"""
    st.markdown("### 用户登录")
    
    with st.form("login_form"):
        username = st.text_input("用户名或邮箱", placeholder="请输入用户名或邮箱")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        
        login_button = st.form_submit_button("🔑 登录", use_container_width=True)
        
        if login_button:
            if username and password:
                with st.spinner("正在登录..."):
                    success, message = login_user(username, password)
                    if success:
                        st.success("登录成功！正在跳转...")
                        st.rerun()
                    else:
                        st.error(f"登录失败：{message}")
            else:
                st.warning("请填写完整的登录信息")
    
    st.markdown("---")
    st.info("💡 测试账户：admin / 123456")

def show_register_form():
    """显示注册表单"""
    st.markdown("### 用户注册")
    
    with st.form("register_form"):
        username = st.text_input("用户名", placeholder="3-20位字母、数字、下划线")
        email = st.text_input("邮箱", placeholder="请输入有效邮箱地址")
        full_name = st.text_input("姓名", placeholder="请输入真实姓名（可选）")
        password = st.text_input("密码", type="password", placeholder="至少6位字符")
        confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
        
        register_button = st.form_submit_button("📝 注册", use_container_width=True)
        
        if register_button:
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("两次输入的密码不一致")
                else:
                    with st.spinner("正在注册..."):
                        success, message = register_user(username, email, password, full_name)
                        if success:
                            st.success(f"注册成功！{message}")
                            st.info("请切换到登录标签页进行登录")
                        else:
                            st.error(f"注册失败：{message}")
            else:
                st.warning("请填写完整的注册信息")

def show_guest_login():
    """显示游客登录"""
    st.markdown("### 游客模式")
    st.markdown("""
    作为游客，您可以：
    - ✅ 查看房价数据
    - ✅ 分析房价趋势  
    - ✅ 对比不同城市
    - ✅ 使用AI助手
    - ❌ 无法使用用户管理功能
    - ❌ 无法保存个人偏好
    """)
    
    if st.button("👤 以游客身份进入", use_container_width=True, type="primary"):
        guest_login()
        st.success("欢迎使用游客模式！")
        st.rerun()
    
    st.markdown("---")
    st.info("💡 游客模式下可以体验大部分功能，如需完整功能请注册登录")

# 初始化页面状态
initialize_page_state()

# === 主应用流程控制 ===
if not st.session_state.show_main_app:
    # 显示登录页面
    show_login_page()
    st.stop()

# --- 页面选择 --- 
# 检查用户模式
if st.session_state.user_mode == "logged_in":
    # 已登录用户的导航栏
    col1, col2 = st.columns([4, 1])
    with col1:
        # 根据用户权限决定导航选项
        if is_current_user_admin():
            # 管理员可以看到用户管理
            nav_options = ["主页", "房价查询", "趋势分析", "城市对比", "数据洞察", "AI助手", "用户管理", "房价预测"]
            nav_icons = ['house', 'search', 'graph-up', 'distribute-horizontal', 'clipboard-data', 'robot', 'people', 'graph-up-arrow']
        else:
            # 普通用户看不到用户管理
            nav_options = ["主页", "房价查询", "趋势分析", "城市对比", "数据洞察", "AI助手", "房价预测"]
            nav_icons = ['house', 'search', 'graph-up', 'distribute-horizontal', 'clipboard-data', 'robot', 'graph-up-arrow']
        
        page = option_menu(
            menu_title=None,
            options=nav_options,
            icons=nav_icons,
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
        )
    with col2:
        # 用户信息和登出按钮
        if st.session_state.user_info:
            st.write(f"👤 {st.session_state.user_info.get('username', '用户')}")
        if st.button("登出", type="secondary"):
            logout_user()
            st.rerun()

elif st.session_state.user_mode == "guest":
    # 游客模式的导航栏 - 绝对不包含用户管理功能
    col1, col2 = st.columns([4, 1])
    with col1:
        # 游客只能看到基础功能，严格禁止用户管理
        nav_options = ["主页", "房价查询", "趋势分析", "城市对比", "数据洞察", "AI助手", "房价预测"]
        nav_icons = ['house', 'search', 'graph-up', 'distribute-horizontal', 'clipboard-data', 'robot', 'graph-up-arrow']
        
        page = option_menu(
            menu_title=None,
            options=nav_options,
            icons=nav_icons,
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
        )
    with col2:
        st.write("👤 游客模式")
        if st.button("登录", type="primary"):
            logout_user()  # 清除游客状态
            st.rerun()

else:
    # 未知状态，返回登录页面
    st.session_state.show_main_app = False
    st.rerun()

# --- 页面内容展示 ---
initialize_page_state()
if hasattr(st.session_state, 'show_auth') and st.session_state.show_auth:
    if st.session_state.auth_mode == "登录":
        page = "登录"
    else:
        page = "注册"

# --- 主页 ---
if page == "主页":
    # 显示当前用户状态
    if st.session_state.user_mode == "logged_in":
        user_name = st.session_state.user_info.get('username', '用户') if st.session_state.user_info else '用户'
        is_admin = is_current_user_admin()
        admin_status = "管理员" if is_admin else "普通用户"
        st.success(f"👤 当前登录用户：{user_name} ({admin_status})")
    elif st.session_state.user_mode == "guest":
        st.info("👤 当前为游客模式 - 功能受限")
    
    st.title("欢迎 🏠")
    st.markdown("""
    这是一个交互式Web应用，旨在帮助您分析和可视化不同城市的房价数据。

    **主要功能:**
    - **房价查询**: 搜索特定城市的最新房价，并以图表形式展示各区域的价格分布。
    - **趋势分析**: 查看特定城市特定区域的房价随时间变化的走势。
    - **城市对比**: 直观地比较两个城市最近半年的平均房价趋势。
    - **数据洞察**: 对单个城市的房价数据进行深入的统计分析，发现数据背后的故事。
    - **AI助手**: 智能分析房价数据，提供投资建议和市场洞察。

    请通过上方的导航栏选择您感兴趣的功能。
    """)
    
    # 权限说明
    if st.session_state.user_mode == "guest":
        st.warning("""
        **游客模式限制：**
        - ❌ 无法访问用户管理功能
        - ❌ 无法保存个人偏好设置
        - ✅ 可以使用所有数据分析功能
        """)
    elif st.session_state.user_mode == "logged_in" and not is_current_user_admin():
        st.info("""
        **普通用户权限：**
        - ❌ 无法访问用户管理功能
        - ✅ 可以保存个人偏好
        - ✅ 可以使用所有数据分析功能
        """)
    elif st.session_state.user_mode == "logged_in" and is_current_user_admin():
        st.success("""
        **管理员权限：**
        - ✅ 可以访问用户管理功能
        - ✅ 可以查看所有用户信息
        - ✅ 享有完整系统权限
        """)

    # 系统状态检查
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 系统状态")
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=5)
            if response.status_code == 200:
                st.success(f"✅ 后端服务正常: {response.json().get('message')}")
                
                # 检查数据完整性
                cities = load_all_cities()
                st.info(f"📊 已加载 {len(cities)} 个城市数据")
                
            else:
                st.error("❌ 后端服务异常，请检查服务状态")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ 无法连接后端服务: {str(e)}")
    
    with col2:
        st.subheader("� 系统说明")
        st.markdown("""
        **✅ 可用功能:**
        - 房价查询、趋势分析
        - 城市对比、数据洞察  
        - AI智能助手
        
        **⚠️ 用户管理状态:**
        """)
        
        # 检查用户管理功能状态
        try:
            # 尝试访问基础API来检查后端状态
            test_response = requests.get(f"{BACKEND_URL}/", timeout=3)
            if test_response.status_code == 200:
                st.info("✅ 后端服务正常，用户管理功能可用")
            else:
                st.warning("⚠️ 后端服务异常")
        except:
            st.warning("❌ 无法连接到后端服务，用户管理功能暂不可用")
            
        st.markdown("""
        **📋 使用提示:**
        - 所有核心分析功能无需登录即可使用
        - 如需使用用户管理功能，请配置PostgreSQL数据库
        
        **如果遇到页面显示问题：**
        1. 点击左侧 "🔄 刷新页面缓存" 按钮
        2. 使用 Ctrl+Shift+R 强制刷新浏览器
        3. 清除浏览器缓存后重新打开页面
        """)
        
        if st.button("🧹 清除所有缓存", help="清除应用程序缓存，解决数据显示问题"):
            st.cache_data.clear()
            st.success("✅ 缓存已清除，页面将自动刷新")
            st.rerun()

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
                    st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})
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
    
    # 添加分析模式选择
    analysis_mode = st.radio(
        "选择分析模式",
        ["单个区域分析", "城市全景分析"],
        horizontal=True,
        help="单个区域分析：查看特定区域的详细趋势；城市全景分析：对比该城市所有区域的趋势"
    )
    
    if analysis_mode == "单个区域分析":
        # 原有的单个区域分析功能
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

        if trend_city and trend_area:
            try:
                res = requests.get(f"{BACKEND_URL}/trend", params={"city": trend_city, "area": trend_area}, timeout=10)
                if res.status_code == 200:
                    trend_data = res.json().get("trend", [])
                    if trend_data:
                        df_trend = pd.DataFrame(trend_data)
                        df_trend['date'] = pd.to_datetime(df_trend['date'])
                        df_trend = df_trend.sort_values('date')

                        st.subheader(f"📈 {trend_city} - {trend_area} 房价走势")
                        fig = px.line(df_trend, x='date', y='price', title=f"{trend_city} {trend_area} 房价走势分析", 
                                      markers=True, labels={"date": "日期", "price": "价格 (元/平米)"})
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})

                        # 显示趋势统计信息
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("当前价格", f"{trend_data[-1]['price']:,.0f} 元/平米")
                        with col2:
                            price_change = trend_data[-1]['price'] - trend_data[0]['price']
                            st.metric("总变化", f"{price_change:+,.0f} 元/平米", f"{price_change/trend_data[0]['price']*100:+.1f}%")
                        with col3:
                            prices = [d['price'] for d in trend_data]
                            st.metric("最高价格", f"{max(prices):,.0f} 元/平米")
                        with col4:
                            st.metric("最低价格", f"{min(prices):,.0f} 元/平米")
                    else:
                        st.warning("未找到该区域的房价趋势数据。")
                else:
                    st.error(f"获取数据失败，状态码: {res.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"请求失败: {str(e)}")
        else:
            st.warning("请选择城市和区域。")
    
    else:  # 城市全景分析
        trend_city = st.selectbox("请选择城市", cities, index=1, key="city_overview_select")
        
        if trend_city:
            try:
                # 获取城市所有区域的趋势数据
                res = requests.get(f"{BACKEND_URL}/city_all_trends", params={"city": trend_city}, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    areas = data.get("areas", [])
                    trends = data.get("trends", {})
                    
                    if trends:
                        st.subheader(f"🏙️ {trend_city}市所有区域房价趋势对比")
                        
                        # 准备绘图数据
                        all_data = []
                        for area, trend_data in trends.items():
                            for point in trend_data:
                                all_data.append({
                                    'date': point['date'],
                                    'price': point['price'],
                                    'area': area
                                })
                        
                        if all_data:
                            df_all = pd.DataFrame(all_data)
                            df_all['date'] = pd.to_datetime(df_all['date'])
                            df_all = df_all.sort_values(['area', 'date'])
                            
                            # 创建多线趋势图
                            fig = px.line(df_all, x='date', y='price', color='area',
                                         title=f"{trend_city}市各区域房价走势对比",
                                         labels={"date": "日期", "price": "价格 (元/平米)", "area": "区域"},
                                         markers=True)
                            fig.update_layout(height=600, legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.01))
                            st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})

                            # 显示各区域统计对比
                            st.subheader("📊 各区域统计对比")
                            
                            # 计算统计数据
                            stats_data = []
                            for area in areas:
                                area_data = df_all[df_all['area'] == area]
                                if not area_data.empty:
                                    latest_price = area_data['price'].iloc[-1]
                                    earliest_price = area_data['price'].iloc[0]
                                    max_price = area_data['price'].max()
                                    min_price = area_data['price'].min()
                                    avg_price = area_data['price'].mean()
                                    price_change = latest_price - earliest_price
                                    change_pct = (price_change / earliest_price) * 100
                                    
                                    stats_data.append({
                                        '区域': area,
                                        '当前价格': f"{latest_price:,.0f}",
                                        '均价': f"{avg_price:,.0f}",
                                        '最高价': f"{max_price:,.0f}",
                                        '最低价': f"{min_price:,.0f}",
                                        '总变化': f"{price_change:+,.0f}",
                                        '变化率': f"{change_pct:+.1f}%"
                                    })
                            
                            if stats_data:
                                stats_df = pd.DataFrame(stats_data)
                                st.dataframe(stats_df, use_container_width=True)
                                
                                # 区域排名
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.subheader("🏆 当前房价排名")
                                    price_ranking = sorted(stats_data, key=lambda x: float(x['当前价格'].replace(',', '')), reverse=True)
                                    for i, area_stat in enumerate(price_ranking[:3], 1):
                                        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                                        st.write(f"{emoji} {area_stat['区域']}: {area_stat['当前价格']} 元/平米")
                                
                                with col2:
                                    st.subheader("📈 涨幅排名")
                                    change_ranking = sorted(stats_data, key=lambda x: float(x['变化率'].replace('%', '').replace('+', '')), reverse=True)
                                    for i, area_stat in enumerate(change_ranking[:3], 1):
                                        emoji = "🚀" if i == 1 else "📈" if i == 2 else "⬆️"
                                        st.write(f"{emoji} {area_stat['区域']}: {area_stat['变化率']}")
                        else:
                            st.warning("暂无趋势数据可显示。")
                    else:
                        st.warning(f"未找到 {trend_city} 的趋势数据。")
                else:
                    st.error(f"获取城市趋势数据失败，状态码: {res.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"请求失败: {str(e)}")
        else:
            st.info("请选择要分析的城市。")

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
                        st.plotly_chart(fig, use_container_width=True, config={"staticPlot": True})

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

# --- AI助手页面 ---
if page == "AI助手":
    st.header("🤖 AI助手 - 智能房价分析与对话")

    # 聊天历史（可选，session_state存储）
    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    # 选项：智能分析 or 通用对话
    mode = st.radio("请选择AI助手模式", ["房价智能分析", "自由对话"], horizontal=True)

    if mode == "房价智能分析":
        # 选择城市/区域
        cities = load_all_cities()
        city = st.selectbox("请选择城市", cities, key="ai_city")
        areas = load_areas_for_city(city) if city else []
        area = st.selectbox("请选择区域（可选）", [""] + areas, key="ai_area")
        if st.button("让AI分析房价趋势", use_container_width=True):
            with st.spinner("AI正在分析..."):
                payload = {
                    "query": "请分析该地区的房价趋势",
                    "city": city,
                    "area": area if area else None
                }
                try:
                    res = requests.post(f"{BACKEND_URL}/ai/assistant", json=payload, headers=get_auth_headers())
                    result = res.json()
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        # 展示AI回复
                        st.markdown("##### AI分析结果：")
                        if "error" in result:
                            st.error(result["error"])
                        elif "text" in result:
                            st.markdown(result["text"])
                        else:
                            st.warning("AI未返回有效内容")
                        # 展示基础统计（可选）
                        if "basic_stats" in result:
                            render_basic_stats(result["basic_stats"])
                        # 聊天历史
                        st.session_state.ai_chat_history.append({
                            "role": "user", "content": f"[{city} {area}] 房价趋势分析"
                        })
                        st.session_state.ai_chat_history.append({
                            "role": "ai", "content": result["text"]
                        })
                except Exception as e:
                    st.error(f"AI分析失败: {str(e)}")
    else:
        # 自由对话
        user_input = st.text_area("输入你的问题（如：介绍北京房价走势、未来房价趋势等）", key="ai_input")
        if st.button("发送", use_container_width=True):
            if user_input.strip():
                with st.spinner("AI正在思考..."):
                    payload = {"query": user_input}
                    try:
                        res = requests.post(f"{BACKEND_URL}/ai/assistant", json=payload, headers=get_auth_headers())
                        result = res.json()
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.markdown("##### AI回复：")
                            st.markdown(result["text"])
                            # 聊天历史
                            st.session_state.ai_chat_history.append({"role": "user", "content": user_input})
                            st.session_state.ai_chat_history.append({"role": "ai", "content": result["text"]})
                    except Exception as e:
                        st.error(f"AI对话失败: {str(e)}")
            else:
                st.warning("请输入你的问题")

    # 展示聊天历史
    if st.session_state.ai_chat_history:
        st.markdown("---")
        st.markdown("#### 聊天记录")
        for msg in st.session_state.ai_chat_history[-10:]:
            role = "👤" if msg["role"] == "user" else "🤖"
            st.markdown(f"{role} {msg['content']}", unsafe_allow_html=True)
        if st.button("清空聊天记录"):
            st.session_state.ai_chat_history = []


# --- 登录页面 ---
elif page == "登录":
    # 添加返回按钮
    if st.button("← 返回主页"):
        st.session_state.show_auth = False
        st.rerun()
    
    st.title("🔐 用户登录")
    
    with st.form("login_form"):
        st.markdown("### 请输入登录信息")
        username = st.text_input("用户名/邮箱", placeholder="请输入用户名或邮箱")
        password = st.text_input("密码", type="password", placeholder="请输入密码")
        
        submit_button = st.form_submit_button("登录", type="primary")
        
        if submit_button:
            if username and password:
                success, message = login_user(username, password)
                if success:
                    st.success(message)
                    st.session_state.show_auth = False  # 登录成功后隐藏认证界面
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("请填写所有字段")
    
    st.markdown("---")
    st.info("没有账号？请点击右上角的'注册'选项")

# --- 注册页面 ---
elif page == "注册":
    # 添加返回按钮
    if st.button("← 返回主页"):
        st.session_state.show_auth = False
        st.rerun()
    
    st.title("📝 用户注册")
    
    with st.form("register_form"):
        st.markdown("### 创建新账号")
        username = st.text_input("用户名", placeholder="3-20位字母、数字、下划线", help="用户名长度3-20位，只能包含字母、数字、下划线")
        email = st.text_input("邮箱", placeholder="请输入有效邮箱地址")
        full_name = st.text_input("姓名", placeholder="请输入真实姓名（可选）")
        password = st.text_input("密码", type="password", placeholder="密码长度至少6位", help="密码长度至少6位")
        confirm_password = st.text_input("确认密码", type="password", placeholder="请再次输入密码")
        
        submit_button = st.form_submit_button("注册", type="primary")
        
        if submit_button:
            if username and email and password and confirm_password:
                if password != confirm_password:
                    st.error("两次输入的密码不一致")
                elif len(password) < 6:
                    st.error("密码长度至少6位")
                else:
                    success, message = register_user(username, email, password, full_name if full_name else None)
                    if success:
                        st.success(message)
                        st.info("注册成功！您可以返回主页或切换到登录")
                        st.session_state.show_auth = False  # 注册成功后隐藏认证界面
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.warning("请填写所有必填字段（姓名可选）")
    
    st.markdown("---")
    st.info("已有账号？请选择右上角的'登录'选项")

# --- 用户管理页面 ---
elif page == "用户管理":
    # 多重安全检查：绝对禁止游客模式访问用户管理
    if st.session_state.user_mode == "guest":
        st.error("🚫 严重错误：游客模式禁止访问用户管理功能")
        st.warning("⚠️ 检测到非法访问尝试，请通过正当渠道登录")
        st.info("💡 如需使用此功能，请先注册并登录")
        
        # 提供返回主页的选项
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏠 返回主页", type="primary"):
                # 强制跳转到主页
                st.session_state.show_main_app = True
                st.rerun()
        with col2:
            if st.button("🔑 前往登录", type="secondary"):
                logout_user()  # 清除游客状态，返回登录页面
                st.rerun()
        st.stop()
    
    # 检查是否已登录
    if not st.session_state.logged_in:
        st.error("❌ 未登录用户无法访问用户管理功能")
        st.info("💡 请先登录以访问此功能")
        if st.button("前往登录"):
            logout_user()
            st.rerun()
        st.stop()
    
    # 检查管理员权限
    if not is_current_user_admin():
        st.error("❌ 权限不足：只有管理员才能访问用户管理功能")
        st.info("💡 当前用户无管理员权限")
        st.warning("如果您是管理员，请确保您的姓名设置为'管理员'")
        st.stop()
    
    st.title("👥 用户管理")
    st.success("✅ 管理员权限验证通过")
    
    # 用户信息卡片
    if st.session_state.user_info:
        user = st.session_state.user_info
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("个人信息")
            with st.container():
                st.markdown(f"""
                **用户ID**: {user.get('id')}  
                **用户名**: {user.get('username')}  
                **邮箱**: {user.get('email')}  
                **姓名**: {user.get('full_name', '未设置')}  
                **创建时间**: {user.get('created_at', '未知')}  
                **最后登录**: {user.get('last_login', '未知')}
                """)
        
        with col2:
            st.subheader("账户操作")
            if st.button("🔄 刷新信息", type="secondary"):
                # 重新获取用户信息
                try:
                    response = requests.get(f"{BACKEND_URL}/auth/me", headers=get_auth_headers())
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.user_info = data["user"]
                        st.success("信息已更新")
                        st.rerun()
                    else:
                        st.error("获取用户信息失败")
                except Exception as e:
                    st.error(f"刷新失败: {str(e)}")
            
            if st.button("🚪 登出", type="primary"):
                logout_user()
                st.success("已登出")
                st.rerun()
    
    st.markdown("---")
    
    # 用户列表（管理员功能）
    st.subheader("📋 用户列表")
    
    if st.button("🔄 刷新用户列表"):
        try:
            response = requests.get(f"{BACKEND_URL}/auth/users", headers=get_auth_headers())
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    users_data = data["users"]
                    
                    if users_data:
                        # 转换为DataFrame并显示
                        df_users = pd.DataFrame(users_data)
                        
                        # 格式化时间列
                        if 'created_at' in df_users.columns:
                            df_users['created_at'] = pd.to_datetime(df_users['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                        if 'last_login' in df_users.columns:
                            df_users['last_login'] = pd.to_datetime(df_users['last_login'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')
                        
                        # 重命名列
                        column_mapping = {
                            'id': 'ID',
                            'username': '用户名',
                            'email': '邮箱',
                            'full_name': '姓名',
                            'created_at': '创建时间',
                            'last_login': '最后登录',
                            'is_active': '状态'
                        }
                        df_display = df_users.rename(columns=column_mapping)
                        
                        # 状态格式化
                        if '状态' in df_display.columns:
                            df_display['状态'] = df_display['状态'].map({True: '✅ 活跃', False: '❌ 禁用'})
                        
                        st.dataframe(df_display, use_container_width=True)
                        
                        # 统计信息
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("总用户数", len(users_data))
                        with col2:
                            active_users = sum(1 for user in users_data if user.get('is_active', False))
                            st.metric("活跃用户", active_users)
                        with col3:
                            recent_users = sum(1 for user in users_data if user.get('last_login'))
                            st.metric("有登录记录", recent_users)
                    else:
                        st.info("暂无用户数据")
                else:
                    st.error(data.get("message", "获取用户列表失败"))
            elif response.status_code == 403:
                st.error("❌ 权限不足：您没有管理员权限，无法查看用户列表")
            else:
                error_data = response.json() if response.content else {}
                st.error(f"服务器错误 ({response.status_code}): {error_data.get('detail', '未知错误')}")
        except Exception as e:
            st.error(f"获取用户列表失败: {str(e)}")
    
    # 使用说明
    with st.expander("📚 用户管理说明"):
        st.markdown("""
        **个人信息**：
        - 查看和管理您的账户信息
        - 刷新最新的登录状态
        
        **用户列表**：
        - 查看系统中所有注册用户
        - 查看用户活跃状态和登录记录
        - 提供用户统计信息
        
        **安全提示**：
        - 定期更换密码保护账户安全
        - 不要在公共电脑上保持长期登录
        - 发现异常登录请及时联系管理员
        """)
# --- 房价预测页面 ---
if page == "房价预测":
    st.title("🔮 房价深度学习预测")
    st.markdown("""
    使用深度学习模型预测未来房价走势。选择城市、区域和预测模型，
    系统将基于历史数据训练模型并给出预测结果。
    """)

    # 选择城市和区域
    col1, col2 = st.columns(2)
    with col1:
        cities = load_all_cities()
        selected_city = st.selectbox("选择城市", cities, index=0)

    with col2:
        areas = load_areas_for_city(selected_city)
        if areas:
            selected_area = st.selectbox("选择区域", areas, index=0)
        else:
            selected_area = st.text_input("输入区域名称", "")

    # 模型选择
    st.subheader("模型选择与参数")

    col1, col2 = st.columns(2)
    with col1:
        model_type = st.radio(
            "选择预测模型",
            ["DNN (全连接神经网络)", "LSTM (长短期记忆网络)", "Prophet (时序预测)"],
            help="不同模型适用于不同类型的数据和预测任务"
        )

    with col2:
        periods = st.slider(
            "预测未来月数",
            min_value=1,
            max_value=24,
            value=6,
            help="预测未来几个月的房价走势"
        )

    # 开始预测
    if st.button("开始预测", type="primary"):
        if not selected_city or not selected_area:
            st.error("请选择城市和区域")
        else:
            with st.spinner("正在训练模型并生成预测..."):
                try:
                    # 准备请求数据
                    model_name = model_type.split(" ")[0]  # 提取模型名称

                    request_data = {
                        "city": selected_city,
                        "area": selected_area,
                        "model_type": model_name,
                        "periods": periods
                    }

                    # 发送请求
                    response = requests.post(
                        f"{BACKEND_URL}/predict",
                        json=request_data,
                        headers=get_auth_headers()
                    )

                    if response.status_code == 200:
                        result = response.json()

                        if result["success"]:
                            st.success("✅ 预测完成")

                            # 显示预测结果
                            predictions = result["predictions"]
                            metrics = result["metrics"]

                            # 显示统计指标
                            st.subheader("数据统计")
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                st.metric("历史数据点数", metrics["data_points"])
                            with col2:
                                st.metric("平均价格", f"{metrics['mean_price']:,.0f}")
                            with col3:
                                st.metric("最高价格", f"{metrics['max_price']:,.0f}")
                            with col4:
                                st.metric("最低价格", f"{metrics['min_price']:,.0f}")

                            # 创建预测数据框
                            df_pred = pd.DataFrame(predictions)
                            df_pred["date"] = pd.to_datetime(df_pred["date"])

                            # 获取历史数据用于绘图
                            hist_response = requests.get(
                                f"{BACKEND_URL}/trend",
                                params={"city": selected_city, "area": selected_area}
                            )

                            if hist_response.status_code == 200:
                                hist_data = hist_response.json().get("trend", [])
                                df_hist = pd.DataFrame(hist_data)
                                df_hist["date"] = pd.to_datetime(df_hist["date"])

                                # 绘制预测图
                                st.subheader("预测结果可视化")

                                fig = px.line()

                                # 添加历史数据
                                fig.add_scatter(
                                    x=df_hist["date"],
                                    y=df_hist["price"],
                                    name="历史数据",
                                    line=dict(color="blue")
                                )

                                # 添加预测数据
                                fig.add_scatter(
                                    x=df_pred["date"],
                                    y=df_pred["predicted_price"],
                                    name="预测数据",
                                    line=dict(color="red", dash="dash")
                                )

                                fig.update_layout(
                                    title=f"{selected_city} {selected_area} 房价预测 (未来{periods}个月)",
                                    xaxis_title="日期",
                                    yaxis_title="房价 (元/平方米)",
                                    height=500
                                )

                                st.plotly_chart(fig, use_container_width=True)

                                # 显示预测数据表格
                                st.subheader("预测详细数据")

                                # 格式化日期和价格
                                df_display = df_pred.copy()
                                df_display["date"] = df_display["date"].dt.strftime("%Y-%m-%d")
                                df_display["predicted_price"] = df_display["predicted_price"].round(2)
                                df_display.columns = ["日期", "预测价格 (元/平方米)"]

                                st.dataframe(df_display, use_container_width=True)

                                # 提供下载链接
                                csv = df_pred.to_csv(index=False)
                                st.download_button(
                                    "📥 下载预测数据 (CSV)",
                                    data=csv,
                                    file_name=f"{selected_city}_{selected_area}_prediction.csv",
                                    mime="text/csv"
                                )

                                # 分析预测趋势
                                first_price = df_pred["predicted_price"].iloc[0]
                                last_price = df_pred["predicted_price"].iloc[-1]
                                change = last_price - first_price
                                change_pct = (change / first_price) * 100

                                trend_direction = "上涨" if change > 0 else "下跌" if change < 0 else "保持稳定"
                                trend_icon = "📈" if change > 0 else "📉" if change < 0 else "📊"

                                st.subheader("预测趋势分析")
                                st.info(
                                    f"{trend_icon} 未来{periods}个月内，{selected_city}{selected_area}的房价预计将{trend_direction} {abs(change_pct):.2f}%，从 {first_price:.2f} 变化到 {last_price:.2f} 元/平方米。")

                            else:
                                st.error("获取历史数据失败，无法生成对比图")

                        else:
                            st.error(f"预测失败: {result.get('message', '未知错误')}")

                    else:
                        st.error(f"请求失败，状态码: {response.status_code}")

                except Exception as e:
                    st.error(f"预测过程中发生错误: {str(e)}")

    # 模型说明
    with st.expander("深度学习模型说明"):
        st.markdown("""
        ### 模型类型介绍

        #### DNN (全连接神经网络)
        - **特点**: 结构简单，适合一般回归问题
        - **优势**: 训练速度快，易于实现
        - **适用场景**: 特征较少，关系相对简单的数据

        #### LSTM (长短期记忆网络)
        - **特点**: 专门设计用于处理时序数据
        - **优势**: 能捕捉长期依赖关系，保留历史信息
        - **适用场景**: 房价走势等时间序列预测

        #### Prophet (Facebook时序预测模型)
        - **特点**: 专为时间序列数据设计的预测工具
        - **优势**: 自动处理季节性、节假日效应等
        - **适用场景**: 有明显季节性波动的房价数据

        ### 注意事项
        - 预测准确性依赖于历史数据的质量和数量
        - 预测时间越长，不确定性越大
        - 建议同时比较多个模型的预测结果
        - 深度学习预测仅供参考，实际房价受多种因素影响
        """)

# 在导航栏中添加"房价预测"选项
if st.session_state.user_mode == "logged_in":
    nav_options = ["主页", "房价查询", "趋势分析", "城市对比", "数据洞察", "AI助手", "房价预测"]
    nav_icons = ['house', 'search', 'graph-up', 'distribute-horizontal', 'clipboard-data', 'robot', 'graph-up-arrow']
else:
    nav_options = ["主页", "房价查询", "趋势分析", "城市对比", "数据洞察", "AI助手", "房价预测"]
    nav_icons = ['house', 'search', 'graph-up', 'distribute-horizontal', 'clipboard-data', 'robot', 'graph-up-arrow']
