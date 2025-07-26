import httpx
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
import random

class ExternalAgent:
    """外部Agent - 处理需要实时信息或外部服务的查询"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def query(self, query_text: str) -> Dict[str, Any]:
        """查询外部Agent"""
        try:
            # 根据查询类型路由到不同的处理方法
            if "天气" in query_text or "weather" in query_text.lower():
                return await self._get_weather_info(query_text)
            elif "时间" in query_text or "time" in query_text.lower():
                return await self._get_time_info(query_text)
            elif "计算" in query_text or "算" in query_text:
                return await self._calculate(query_text)
            elif "新闻" in query_text or "news" in query_text.lower():
                return await self._get_news_info(query_text)
            else:
                return await self._general_external_query(query_text)
                
        except Exception as e:
            print(f"外部Agent查询错误: {e}")
            return {
                "success": False,
                "query": query_text,
                "error": str(e),
                "data": None
            }
    
    async def _get_weather_info(self, query: str) -> Dict[str, Any]:
        """获取天气信息 (模拟实现)"""
        # 这里应该调用真实的天气API，比如OpenWeatherMap
        # 为了演示，我们返回模拟数据
        await asyncio.sleep(0.5)  # 模拟API调用延迟
        
        weather_data = {
            "city": "北京",
            "temperature": random.randint(15, 30),
            "condition": random.choice(["晴朗", "多云", "小雨", "阴天"]),
            "humidity": random.randint(40, 80),
            "wind_speed": random.randint(5, 20)
        }
        
        return {
            "success": True,
            "query": query,
            "data": weather_data,
            "source": "天气API"
        }
    
    async def _get_time_info(self, query: str) -> Dict[str, Any]:
        """获取时间信息"""
        current_time = datetime.now()
        
        time_data = {
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "day_of_week": current_time.strftime("%A"),
            "timezone": "Asia/Shanghai"
        }
        
        return {
            "success": True,
            "query": query,
            "data": time_data,
            "source": "系统时间"
        }
    
    async def _calculate(self, query: str) -> Dict[str, Any]:
        """执行计算任务"""
        try:
            # 简单的数学表达式计算
            # 注意：在生产环境中应该使用更安全的计算方法
            import re
            
            # 提取数学表达式
            math_pattern = r'[\d+\-*/().\s]+'
            matches = re.findall(math_pattern, query)
            
            if matches:
                expression = ''.join(matches).strip()
                # 安全计算（仅允许基本数学运算）
                allowed_chars = set('0123456789+-*/(). ')
                if all(c in allowed_chars for c in expression):
                    result = eval(expression)
                    return {
                        "success": True,
                        "query": query,
                        "data": {
                            "expression": expression,
                            "result": result
                        },
                        "source": "计算器"
                    }
            
            return {
                "success": False,
                "query": query,
                "error": "无法识别数学表达式",
                "data": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "error": f"计算错误: {str(e)}",
                "data": None
            }
    
    async def _get_news_info(self, query: str) -> Dict[str, Any]:
        """获取新闻信息 (模拟实现)"""
        await asyncio.sleep(0.3)  # 模拟API调用延迟
        
        # 模拟新闻数据
        news_data = {
            "headlines": [
                "科技公司发布新AI产品",
                "经济数据显示增长趋势",
                "环保政策获得积极响应"
            ],
            "source": "新闻API",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "query": query,
            "data": news_data,
            "source": "新闻API"
        }
    
    async def _general_external_query(self, query: str) -> Dict[str, Any]:
        """通用外部查询处理"""
        # 这里可以集成更多外部服务
        # 比如搜索引擎API、专业数据库等
        
        await asyncio.sleep(0.2)  # 模拟处理时间
        
        return {
            "success": True,
            "query": query,
            "data": {
                "message": "这是一个需要外部服务处理的查询",
                "suggestions": [
                    "建议查询更具体的信息",
                    "可以尝试重新表述问题",
                    "或者联系相关专业人员"
                ]
            },
            "source": "通用外部服务"
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()