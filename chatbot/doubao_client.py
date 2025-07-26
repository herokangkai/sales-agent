import httpx
import json
import asyncio
from typing import Dict, Any, List, AsyncGenerator
from config import Config

class DoubaoClient:
    """豆包API客户端"""
    
    def __init__(self):
        self.config = Config.get_doubao_config()
        self.base_url = self.config["base_url"]
        self.api_key = self.config["api_key"]
        self.model = self.config["model"]
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def chat_completion(
        self, 
        messages: List[Dict[str, Any]], 
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """调用豆包聊天完成API"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            if stream:
                return await self._stream_request(headers, payload)
            else:
                response = await self.client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            print(f"豆包API调用错误: {e}")
            raise e
    
    async def _stream_request(self, headers: Dict[str, str], payload: Dict[str, Any]):
        """处理流式请求"""
        async with self.client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # 移除 "data: " 前缀
                    if data == "[DONE]":
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue
    
    async def chat_completion_stream(
        self, 
        messages: List[Dict[str, Any]], 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 移除 "data: " 前缀
                        if data.strip() == "[DONE]":
                            break
                        if data.strip():
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            print(f"豆包流式API调用错误: {e}")
            yield f"API调用错误: {str(e)}"
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()