#!/usr/bin/env python3
"""
简化版聊天机器人 - 直接测试豆包API
"""

import asyncio
import httpx
import json
import os
from typing import AsyncGenerator
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class SimpleDoubaoClient:
    """简化的豆包API客户端"""
    
    def __init__(self):
        self.api_key = os.getenv("DOUBAO_API_KEY", "")
        self.base_url = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.model = os.getenv("DOUBAO_MODEL", "doubao-1-5-thinking-vision-pro-250428")
        
        if not self.api_key:
            raise ValueError("请设置DOUBAO_API_KEY环境变量")
    
    async def chat_simple(self, message: str) -> str:
        """简单聊天接口"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
            except Exception as e:
                return f"API调用错误: {str(e)}"
    
    async def chat_stream(self, message: str) -> AsyncGenerator[str, None]:
        """流式聊天接口"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                async with client.stream(
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
                yield f"流式API调用错误: {str(e)}"

async def test_basic_chat():
    """测试基础聊天功能"""
    print("🧪 测试基础聊天功能...")
    
    client = SimpleDoubaoClient()
    
    test_messages = [
        "你好，请简单介绍一下自己",
        "什么是人工智能？",
        "用一句话解释机器学习"
    ]
    
    for msg in test_messages:
        print(f"\n用户: {msg}")
        try:
            response = await client.chat_simple(msg)
            print(f"助手: {response}")
        except Exception as e:
            print(f"错误: {e}")

async def test_stream_chat():
    """测试流式聊天功能"""
    print("\n\n🧪 测试流式聊天功能...")
    
    client = SimpleDoubaoClient()
    
    message = "请用100字左右介绍Python编程语言的特点"
    print(f"\n用户: {message}")
    print("助手: ", end="", flush=True)
    
    try:
        async for chunk in client.chat_stream(message):
            print(chunk, end="", flush=True)
        print()  # 换行
    except Exception as e:
        print(f"\n流式聊天错误: {e}")

async def interactive_chat():
    """交互式聊天"""
    print("\n\n💬 进入交互式聊天模式 (输入 'quit' 退出)")
    
    client = SimpleDoubaoClient()
    
    while True:
        try:
            user_input = input("\n你: ").strip()
            if user_input.lower() in ['quit', 'exit', '退出']:
                print("再见！")
                break
            
            if not user_input:
                continue
            
            print("助手: ", end="", flush=True)
            async for chunk in client.chat_stream(user_input):
                print(chunk, end="", flush=True)
            print()  # 换行
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n聊天错误: {e}")

async def main():
    """主函数"""
    print("🚀 豆包API简化测试程序")
    print("=" * 50)
    
    # 测试基础功能
    await test_basic_chat()
    
    # 测试流式功能
    await test_stream_chat()
    
    # 交互式聊天
    await interactive_chat()

if __name__ == "__main__":
    asyncio.run(main())