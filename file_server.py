#!/usr/bin/env python3
"""
简单的文件服务器，用于提供媒体文件
"""

import os
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import unquote
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class MediaFileHandler(SimpleHTTPRequestHandler):
    """媒体文件处理器"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)
    
    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[文件服务器] {format % args}")

def start_file_server():
    """启动文件服务器"""
    print("🗂️  启动媒体文件服务器...")
    
    # 从环境变量获取配置
    host = os.getenv("FILE_SERVER_HOST", "localhost")
    port = int(os.getenv("FILE_SERVER_PORT", "8740"))
    
    # 创建服务器
    server_address = (host if host != "localhost" else '', port)
    httpd = HTTPServer(server_address, MediaFileHandler)
    
    print(f"✅ 文件服务器启动成功！")
    print(f"📁 服务目录: {os.getcwd()}")
    print(f"🌐 访问地址: http://{host}:{port}")
    print(f"🖼️  图片示例: http://{host}:{port}/kb/assets/cases/case4_great_person_digital_human.png")
    print(f"🎥 视频示例: http://{host}:{port}/kb/assets/products_tech/mohuman_ai_agent_realistic.mp4")
    print(f"⏹️  按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n🛑 文件服务器已停止")
        httpd.shutdown()

if __name__ == "__main__":
    start_file_server()