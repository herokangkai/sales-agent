import os
from typing import Dict, Any

class Config:
    """配置管理"""
    
    # 豆包API配置
    DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
    DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    DOUBAO_MODEL = os.getenv("DOUBAO_MODEL", "doubao-1-5-thinking-vision-pro-250428")
    
    # 知识库配置
    KNOWLEDGE_DB_PATH = os.getenv("KNOWLEDGE_DB_PATH", "./knowledge_db")
    
    # 服务器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # 外部服务配置
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
    
    # 流式输出配置
    STREAM_DELAY = float(os.getenv("STREAM_DELAY", 0.05))  # 流式输出延迟
    MAX_RESPONSE_LENGTH = int(os.getenv("MAX_RESPONSE_LENGTH", 2000))
    
    @classmethod
    def get_doubao_config(cls) -> Dict[str, Any]:
        """获取豆包API配置"""
        return {
            "api_key": cls.DOUBAO_API_KEY,
            "base_url": cls.DOUBAO_BASE_URL,
            "model": cls.DOUBAO_MODEL
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置是否完整"""
        required_configs = [
            cls.DOUBAO_API_KEY
        ]
        
        missing_configs = [
            config for config in required_configs 
            if not config
        ]
        
        if missing_configs:
            print("警告: 以下配置缺失:")
            print("- DOUBAO_API_KEY: 请设置有效的豆包API密钥")
            return False
        
        return True