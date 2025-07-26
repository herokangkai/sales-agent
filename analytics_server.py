#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
查询分析API服务器
提供查询日志的分析和统计功能
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sqlite3

# 导入查询日志记录器
from chatbot.query_logger import QueryLogger

class AnalyticsHandler(BaseHTTPRequestHandler):
    """分析API处理器"""
    
    def __init__(self, *args, **kwargs):
        self.query_logger = QueryLogger()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # 设置CORS头
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if path == '/api/analytics/queries':
                # 获取查询记录
                self._handle_get_queries(query_params)
            elif path == '/api/analytics/statistics':
                # 获取统计信息
                self._handle_get_statistics(query_params)
            elif path == '/api/analytics/intent-distribution':
                # 获取意图分布
                self._handle_get_intent_distribution(query_params)
            elif path == '/api/analytics/query-trend':
                # 获取查询趋势
                self._handle_get_query_trend(query_params)
            elif path == '/api/analytics/export':
                # 导出数据
                self._handle_export_data(query_params)
            elif path == '/api/analytics/health':
                # 健康检查
                self._send_json_response({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
            else:
                self._send_error_response(404, 'API endpoint not found')
                
        except Exception as e:
            print(f"Error handling GET request: {e}")
            self._send_error_response(500, str(e))
    
    def do_POST(self):
        """处理POST请求"""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # 设置CORS头
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if path == '/api/analytics/cleanup':
                # 清理旧数据
                self._handle_cleanup_data(post_data)
            else:
                self._send_error_response(404, 'API endpoint not found')
                
        except Exception as e:
            print(f"Error handling POST request: {e}")
            self._send_error_response(500, str(e))
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _handle_get_queries(self, query_params):
        """处理获取查询记录请求"""
        limit = int(query_params.get('limit', [100])[0])
        offset = int(query_params.get('offset', [0])[0])
        user_id = query_params.get('user_id', [None])[0]
        intent_category = query_params.get('intent_category', [None])[0]
        start_date = query_params.get('start_date', [None])[0]
        end_date = query_params.get('end_date', [None])[0]
        
        queries = self.query_logger.get_queries(
            limit=limit,
            offset=offset,
            user_id=user_id,
            intent_category=intent_category,
            start_date=start_date,
            end_date=end_date
        )
        
        self._send_json_response({
            'queries': queries,
            'total': len(queries),
            'limit': limit,
            'offset': offset
        })
    
    def _handle_get_statistics(self, query_params):
        """处理获取统计信息请求"""
        days = int(query_params.get('days', [30])[0])
        statistics = self.query_logger.get_intent_statistics(days)
        self._send_json_response(statistics)
    
    def _handle_get_intent_distribution(self, query_params):
        """处理获取意图分布请求"""
        days = int(query_params.get('days', [30])[0])
        statistics = self.query_logger.get_intent_statistics(days)
        self._send_json_response({
            'intent_distribution': statistics['intent_distribution'],
            'period_days': days
        })
    
    def _handle_get_query_trend(self, query_params):
        """处理获取查询趋势请求"""
        days = int(query_params.get('days', [30])[0])
        statistics = self.query_logger.get_intent_statistics(days)
        self._send_json_response({
            'query_trend': statistics['query_trend'],
            'period_days': days
        })
    
    def _handle_export_data(self, query_params):
        """处理导出数据请求"""
        format_type = query_params.get('format', ['json'])[0]
        
        # 生成临时文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"query_export_{timestamp}.{format_type}"
        filepath = f"data/exports/{filename}"
        
        # 确保导出目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 导出数据
        self.query_logger.export_data(filepath, format_type)
        
        self._send_json_response({
            'message': 'Data exported successfully',
            'filename': filename,
            'filepath': filepath,
            'format': format_type
        })
    
    def _handle_cleanup_data(self, post_data):
        """处理清理数据请求"""
        try:
            data = json.loads(post_data) if post_data else {}
            days = data.get('days', 90)
            
            deleted_count = self.query_logger.cleanup_old_data(days)
            
            self._send_json_response({
                'message': f'Cleaned up data older than {days} days',
                'deleted_records': deleted_count
            })
        except json.JSONDecodeError:
            self._send_error_response(400, 'Invalid JSON data')
    
    def _send_json_response(self, data):
        """发送JSON响应"""
        response = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        self.wfile.write(response.encode('utf-8'))
    
    def _send_error_response(self, status_code, message):
        """发送错误响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            'error': message,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        }
        
        response = json.dumps(error_response, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))

def main():
    """启动分析服务器"""
    # 从环境变量获取配置
    host = os.getenv('ANALYTICS_SERVER_HOST', '127.0.0.1')
    port = int(os.getenv('ANALYTICS_SERVER_PORT', 8742))
    
    # 确保数据目录存在
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/exports', exist_ok=True)
    
    print(f"🔍 启动查询分析服务器...")
    print(f"📊 服务地址: http://{host}:{port}")
    print(f"📋 API文档:")
    print(f"   GET  /api/analytics/queries - 获取查询记录")
    print(f"   GET  /api/analytics/statistics - 获取统计信息")
    print(f"   GET  /api/analytics/intent-distribution - 获取意图分布")
    print(f"   GET  /api/analytics/query-trend - 获取查询趋势")
    print(f"   GET  /api/analytics/export - 导出数据")
    print(f"   POST /api/analytics/cleanup - 清理旧数据")
    print(f"   GET  /api/analytics/health - 健康检查")
    print("")
    
    try:
        server = HTTPServer((host, port), AnalyticsHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")

if __name__ == '__main__':
    main()