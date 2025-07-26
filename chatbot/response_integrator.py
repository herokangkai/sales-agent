import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional
from .intent_analyzer import IntentResult
from .doubao_client import DoubaoClient

class ResponseIntegrator:
    """响应整合器 - 将多源信息整合并流式输出"""
    
    def __init__(self):
        self.doubao_client = DoubaoClient()
    
    async def integrate_and_stream(
        self,
        original_question: str,
        intent_result: IntentResult,
        knowledge_result: Optional[Dict[str, Any]] = None,
        agent_result: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """整合多源信息并流式输出响应"""
        
        # 构建上下文信息
        context_info = self._build_context(
            original_question, intent_result, knowledge_result, agent_result
        )
        
        # 构建系统提示
        system_prompt = """你是一个智能助手，需要基于提供的信息来回答用户问题。

请遵循以下原则：
1. 优先使用提供的知识库信息和外部Agent数据
2. 如果信息不完整，请诚实说明
3. 保持回答的准确性和相关性
4. 用自然、友好的语调回答
5. 适当引用信息来源

请基于以下信息回答用户问题："""

        try:
            # 使用豆包流式API生成回答
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context_info}
            ]
            
            # 流式输出响应
            async for chunk in self.doubao_client.chat_completion_stream(
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            ):
                yield chunk
                    
        except Exception as e:
            # 如果豆包API失败，使用备用方案
            print(f"豆包API错误: {e}")
            async for chunk in self._fallback_response(
                original_question, knowledge_result, agent_result
            ):
                yield chunk
    
    def _build_context(
        self,
        question: str,
        intent_result: IntentResult,
        knowledge_result: Optional[Dict[str, Any]],
        agent_result: Optional[Dict[str, Any]]
    ) -> str:
        """构建上下文信息"""
        
        context_parts = [f"用户问题: {question}"]
        context_parts.append(f"意图分析: {intent_result.summary}")
        
        # 添加知识库信息
        if knowledge_result and knowledge_result.get('success'):
            context_parts.append("\\n知识库信息:")
            for i, result in enumerate(knowledge_result.get('results', []), 1):
                context_parts.append(f"{i}. {result['content']}")
                if result.get('metadata'):
                    context_parts.append(f"   来源: {result['metadata']}")
        
        # 添加外部Agent信息
        if agent_result and agent_result.get('success'):
            context_parts.append("\\n外部服务信息:")
            data = agent_result.get('data', {})
            source = agent_result.get('source', '外部服务')
            
            if isinstance(data, dict):
                for key, value in data.items():
                    context_parts.append(f"- {key}: {value}")
            else:
                context_parts.append(f"- {data}")
            
            context_parts.append(f"信息来源: {source}")
        
        return "\\n".join(context_parts)
    
    async def _fallback_response(
        self,
        question: str,
        knowledge_result: Optional[Dict[str, Any]],
        agent_result: Optional[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """备用响应方案（当OpenAI API不可用时）"""
        
        response_parts = []
        
        # 基础回答
        response_parts.append("根据您的问题，我为您整理了以下信息：\\n\\n")
        
        # 知识库信息
        if knowledge_result and knowledge_result.get('success'):
            response_parts.append("📚 知识库信息：\\n")
            for i, result in enumerate(knowledge_result.get('results', []), 1):
                response_parts.append(f"{i}. {result['content']}\\n")
        
        # 外部服务信息
        if agent_result and agent_result.get('success'):
            response_parts.append("\\n🔍 实时信息：\\n")
            data = agent_result.get('data', {})
            
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        response_parts.append(f"• {key}:\\n")
                        for item in value:
                            response_parts.append(f"  - {item}\\n")
                    else:
                        response_parts.append(f"• {key}: {value}\\n")
            else:
                response_parts.append(f"• {data}\\n")
        
        # 如果没有找到相关信息
        if not (knowledge_result and knowledge_result.get('success')) and not (agent_result and agent_result.get('success')):
            response_parts.append("抱歉，我没有找到与您问题直接相关的信息。")
            response_parts.append("建议您：\\n")
            response_parts.append("1. 尝试重新表述问题\\n")
            response_parts.append("2. 提供更多具体细节\\n")
            response_parts.append("3. 或者咨询相关专业人员\\n")
        
        # 模拟流式输出
        full_response = "".join(response_parts)
        words = full_response.split()
        
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")
            await asyncio.sleep(0.05)  # 模拟打字效果