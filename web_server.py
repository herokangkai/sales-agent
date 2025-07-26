#!/usr/bin/env python3
"""
Web服务器 - 提供HTML文件和处理API代理
"""

import os
import json
import asyncio
import httpx
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class WebHandler(SimpleHTTPRequestHandler):
    """Web请求处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/llm/doubao':
            self.handle_doubao_proxy()
        elif parsed_path.path == '/api/llm/dashscope':
            self.handle_dashscope_proxy()
        else:
            super().do_POST()
    
    def handle_doubao_proxy(self):
        """处理豆包API代理"""
        try:
            content_length = self.headers.get('Content-Length')
            if content_length is not None:
                content_length = int(content_length)
            else:
                content_length = 0
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # 异步调用豆包API
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.call_doubao_api(request_data))
            loop.close()
            
            if request_data.get('stream', False):
                # 流式响应
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                
                # 转发流式数据
                for chunk in response:
                    self.wfile.write(chunk.encode('utf-8'))
                    self.wfile.flush()
            else:
                # 普通响应
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
        except Exception as e:
            # 返回JSON格式的错误响应
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "error": {
                    "message": f"API proxy error: {str(e)}",
                    "type": "proxy_error",
                    "code": 500
                }
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def handle_dashscope_proxy(self):
        """处理DashScope API代理"""
        try:
            content_length = self.headers.get('Content-Length')
            if content_length is not None:
                content_length = int(content_length)
            else:
                content_length = 0
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # 异步调用DashScope API
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.call_dashscope_api(request_data))
            loop.close()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            # 返回JSON格式的错误响应
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "error": {
                    "message": f"DashScope proxy error: {str(e)}",
                    "type": "proxy_error", 
                    "code": 500
                }
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    async def call_doubao_api(self, request_data):
        """调用豆包API"""
        api_key = os.getenv("DOUBAO_API_KEY")
        base_url = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            if request_data.get('stream', False):
                # 流式请求
                async with client.stream(
                    "POST",
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=request_data
                ) as response:
                    response.raise_for_status()
                    
                    chunks = []
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunks.append(line + "\n\n")
                    
                    return chunks
            else:
                # 普通请求
                response = await client.post(
                    f"{base_url}/chat/completions",
                    headers=headers,
                    json=request_data
                )
                response.raise_for_status()
                return response.json()
    
    async def call_dashscope_api(self, request_data):
        """调用DashScope API"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        app_id = os.getenv("DASHSCOPE_APP_ID")
        base_url = f"https://dashscope.aliyuncs.com/api/v1/apps/{app_id}/completion"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(base_url, headers=headers, json=request_data)
            response.raise_for_status()
            return response.json()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[Web服务器] {format % args}")

def start_web_server():
    """启动Web服务器"""
    print("🌐 启动Web服务器...")
    
    # 从环境变量获取配置
    host = os.getenv("MAIN_SERVER_HOST", "localhost")
    port = int(os.getenv("MAIN_SERVER_PORT", "8741"))
    
    # 创建服务器
    server_address = (host if host != "localhost" else '', port)
    httpd = HTTPServer(server_address, WebHandler)
    
    print(f"✅ Web服务器启动成功！")
    print(f"🌐 访问地址: http://{host}:{port}")
    print(f"📄 聊天界面: http://{host}:{port}/real_llm_chat.html")
    print(f"🔧 API代理: http://{host}:{port}/api/llm/")
    print(f"⏹️  按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 Web服务器已停止")
        httpd.shutdown()

if __name__ == "__main__":
    start_web_server()