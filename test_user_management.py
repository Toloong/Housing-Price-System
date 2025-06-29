#!/usr/bin/env python3
"""
用户管理功能测试脚本
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_user_registration():
    """测试用户注册"""
    print("=== 测试用户注册 ===")
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "full_name": "测试用户"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"注册测试失败: {e}")
        return False

def test_user_login():
    """测试用户登录"""
    print("\n=== 测试用户登录 ===")
    
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {result}")
        
        if response.status_code == 200 and result.get("success"):
            return result.get("token")
        return None
    except Exception as e:
        print(f"登录测试失败: {e}")
        return None

def test_protected_endpoint(token):
    """测试受保护的端点"""
    print("\n=== 测试受保护端点 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 测试获取用户信息
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"获取用户信息 - 状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        # 测试获取用户列表
        response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
        print(f"获取用户列表 - 状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        
        return True
    except Exception as e:
        print(f"受保护端点测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试基础API端点 ===")
    
    endpoints = [
        "/",
        "/cities",
        "/search?city=北京",
        "/areas?city=北京"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"{endpoint} - 状态码: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ 成功")
            else:
                print(f"  ❌ 失败: {response.text}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")

def main():
    """主测试函数"""
    print("房价分析系统用户管理功能测试")
    print("=" * 50)
    
    # 测试基础API
    test_api_endpoints()
    
    # 测试用户注册
    if test_user_registration():
        print("✅ 用户注册测试通过")
        
        # 测试用户登录
        token = test_user_login()
        if token:
            print("✅ 用户登录测试通过")
            
            # 测试受保护端点
            if test_protected_endpoint(token):
                print("✅ 受保护端点测试通过")
            else:
                print("❌ 受保护端点测试失败")
        else:
            print("❌ 用户登录测试失败")
    else:
        print("❌ 用户注册测试失败")
    
    print("\n" + "=" * 50)
    print("测试完成！")

if __name__ == "__main__":
    main()
