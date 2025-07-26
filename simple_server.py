#!/usr/bin/env python3
"""
简化的知识库API服务器
"""

import asyncio
import json
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot.kb_loader import MogineKBLoader

class KnowledgeBaseHandler(BaseHTTPRequestHandler):
    """知识库API处理器"""
    
    def __init__(self, *args, kb_loader=None, **kwargs):
        self.kb_loader = kb_loader
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        
        # 设置CORS头
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if parsed_path.path == '/api/search':
            # 搜索知识库
            query_params = parse_qs(parsed_path.query, encoding='utf-8')
            query = query_params.get('q', [''])[0]
            top_k = int(query_params.get('top_k', ['3'])[0])
            
            print(f"收到搜索请求: {query}")
            print(f"查询参数: {query_params}")
            
            if query:
                results = self.kb_loader.search_knowledge(query, top_k)
                response = {
                    'success': True,
                    'query': query,
                    'results': results,
                    'total_found': len(results)
                }
            else:
                response = {
                    'success': False,
                    'error': 'Missing query parameter',
                    'results': []
                }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        elif parsed_path.path == '/api/company_info':
            # 获取公司信息
            company_info = self.kb_loader.get_company_info()
            assistant_info = self.kb_loader.get_assistant_info()
            
            response = {
                'success': True,
                'company_info': company_info,
                'assistant_info': assistant_info
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        else:
            # 404
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.address_string()}] {format % args}")

def create_handler(kb_loader):
    """创建处理器工厂函数"""
    def handler(*args, **kwargs):
        return KnowledgeBaseHandler(*args, kb_loader=kb_loader, **kwargs)
    return handler

def start_server():
    """启动服务器"""
    print("🚀 启动摩泛知识库API服务器...")
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 初始化知识库
    kb_loader = MogineKBLoader()
    
    # 从环境变量获取配置
    host = os.getenv("KB_SERVER_HOST", "localhost")
    port = int(os.getenv("KB_SERVER_PORT", "8739"))
    
    # 创建服务器
    server_address = (host if host != "localhost" else '', port)
    handler_class = create_handler(kb_loader)
    httpd = HTTPServer(server_address, handler_class)
    
    print(f"✅ 服务器启动成功！")
    print(f"📡 API地址: http://{host}:{port}")
    print(f"🔍 搜索接口: http://{host}:{port}/api/search?q=钱学森数字人")
    print(f"🏢 公司信息: http://{host}:{port}/api/company_info")
    print(f"⏹️  按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 服务器已停止")
        httpd.shutdown()

if __name__ == "__main__":
    start_server()