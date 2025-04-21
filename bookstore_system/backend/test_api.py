import urllib.request
import urllib.error
import json
import ssl

def test_api_endpoints():
    """测试API端点是否可访问 (使用urllib标准库)"""
    # 测试基本的API路由
    base_url = "http://127.0.0.1:5000"
    
    endpoints = [
        "/api",                # API根路径
        "/api/auth/login",     # 登录端点 
    ]
    
    results = []
    # 创建上下文，忽略SSL证书验证（仅用于开发测试）
    context = ssl._create_unverified_context()
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            # 发送GET请求
            response = urllib.request.urlopen(url, context=context)
            status = response.status
            
            # 尝试为登录端点获取CORS头信息
            cors_headers = None
            if endpoint == "/api/auth/login":
                try:
                    # 创建一个OPTIONS请求来检查CORS
                    req = urllib.request.Request(url, method="OPTIONS")
                    options_resp = urllib.request.urlopen(req, context=context)
                    cors_headers = options_resp.headers.get('Access-Control-Allow-Origin')
                except Exception as e:
                    print(f"无法检查CORS头: {str(e)}")
                    
            results.append({
                "endpoint": endpoint,
                "status": status,
                "success": status != 404,
                "cors": cors_headers
            })
            print(f"端点 {endpoint}: 状态码 {status}")
            
        except urllib.error.HTTPError as e:
            print(f"端点 {endpoint}: HTTP错误 - {e.code} {e.reason}")
            results.append({
                "endpoint": endpoint,
                "status": e.code,
                "success": e.code != 404,  # 我们只关心它是否存在，404表示不存在
                "error": e.reason
            })
        except Exception as e:
            print(f"端点 {endpoint}: 错误 - {str(e)}")
            results.append({
                "endpoint": endpoint,
                "status": "错误",
                "error": str(e)
            })
    
    return results

if __name__ == "__main__":
    print("测试API端点...")
    results = test_api_endpoints()
    
    # 打印总结
    print("\n测试结果摘要:")
    for result in results:
        status = "✓" if result.get("success") else "✗"
        print(f"{status} {result['endpoint']} - 状态码: {result['status']}")
    
    # 检查CORS设置
    cors_tests = [r for r in results if r.get("cors") is not None]
    if cors_tests:
        print("\nCORS 配置:")
        for test in cors_tests:
            print(f"端点 {test['endpoint']}: {test.get('cors', '未配置')}")
    
    print("\n注意: 如果需要更强大的HTTP测试功能，建议安装requests库:")
    print("  pip install requests")
