from typing import Dict, Any
from pydantic import BaseModel
import json
import time
from .doubao_client import DoubaoClient
from .query_logger import QueryLogger

class IntentResult(BaseModel):
    """意图分析结果"""
    summary: str  # 意图摘要
    needs_knowledge_base: bool  # 是否需要查询知识库
    needs_external_agent: bool  # 是否需要调用外部Agent
    knowledge_query: str = ""  # 知识库查询语句
    agent_query: str = ""  # Agent查询语句
    confidence: float = 0.0  # 置信度

class IntentAnalyzer:
    """意图分析器 - 负责拆解用户问题"""
    
    def __init__(self):
        self.doubao_client = DoubaoClient()
        self.query_logger = QueryLogger()
        
    async def analyze_intent(self, user_message: str, user_id: str = None, session_id: str = None) -> IntentResult:
        """分析用户意图并拆解查询需求"""
        start_time = time.time()
        
        system_prompt = """你是一个意图分析专家。分析用户问题，判断需要哪些信息源来回答：

1. 本地知识库：适合回答已知的事实性信息、文档内容、历史记录等
2. 外部Agent：适合需要实时信息、计算、API调用、外部服务等

请以JSON格式返回分析结果：
{
    "summary": "意图摘要",
    "needs_knowledge_base": true/false,
    "needs_external_agent": true/false,
    "knowledge_query": "如果需要知识库，这里是查询语句",
    "agent_query": "如果需要外部Agent，这里是查询语句",
    "confidence": 0.95
}

示例：
用户问："今天天气怎么样？"
返回：{
    "summary": "查询当前天气信息",
    "needs_knowledge_base": false,
    "needs_external_agent": true,
    "knowledge_query": "",
    "agent_query": "获取今天的天气信息",
    "confidence": 0.9
}

用户问："什么是机器学习？"
返回：{
    "summary": "解释机器学习概念",
    "needs_knowledge_base": true,
    "needs_external_agent": false,
    "knowledge_query": "机器学习定义和基本概念",
    "agent_query": "",
    "confidence": 0.95
}"""

        try:
            # 使用豆包API进行意图分析
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = await self.doubao_client.chat_completion(
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response["choices"][0]["message"]["content"].strip()
            
            # 解析JSON结果
            try:
                result_data = json.loads(result_text)
                result = IntentResult(**result_data)
                
                # 记录查询日志
                processing_time = time.time() - start_time
                query_id = self.query_logger.log_query(
                    query_text=user_message,
                    user_id=user_id,
                    session_id=session_id,
                    intent_category=result.summary,
                    intent_confidence=result.confidence,
                    response_type="intent_analysis",
                    processing_time=processing_time,
                    metadata={
                        "needs_knowledge_base": result.needs_knowledge_base,
                        "needs_external_agent": result.needs_external_agent,
                        "knowledge_query": result.knowledge_query,
                        "agent_query": result.agent_query
                    }
                )
                
                # 记录详细的意图分析
                self.query_logger.log_intent_analysis(
                    query_id=query_id,
                    intent_type=result.summary,
                    confidence_score=result.confidence,
                    keywords=self._extract_keywords(user_message),
                    entities=self._extract_entities(user_message),
                    sentiment=self._analyze_sentiment(user_message),
                    complexity_level=self._assess_complexity(user_message)
                )
                
                return result
            except json.JSONDecodeError:
                # 如果JSON解析失败，返回默认结果
                result = IntentResult(
                    summary="通用问题处理",
                    needs_knowledge_base=True,
                    needs_external_agent=True,
                    knowledge_query=user_message,
                    agent_query=user_message,
                    confidence=0.5
                )
                
                # 记录失败的查询
                processing_time = time.time() - start_time
                self.query_logger.log_query(
                    query_text=user_message,
                    user_id=user_id,
                    session_id=session_id,
                    intent_category="parsing_failed",
                    intent_confidence=0.5,
                    response_type="intent_analysis_failed",
                    processing_time=processing_time,
                    metadata={"error": "JSON parsing failed"}
                )
                
                return result
                
        except Exception as e:
            print(f"意图分析错误: {e}")
            # 返回保守的默认结果
            result = IntentResult(
                summary="问题分析",
                needs_knowledge_base=True,
                needs_external_agent=False,
                knowledge_query=user_message,
                agent_query="",
                confidence=0.3
            )
            
            # 记录错误的查询
            processing_time = time.time() - start_time
            self.query_logger.log_query(
                query_text=user_message,
                user_id=user_id,
                session_id=session_id,
                intent_category="analysis_error",
                intent_confidence=0.3,
                response_type="intent_analysis_error",
                processing_time=processing_time,
                metadata={"error": str(e)}
            )
            
            return result
    
    def _extract_keywords(self, text: str) -> list:
        """提取关键词（简单实现）"""
        # 这里可以使用更复杂的NLP库，现在先用简单的分词
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        # 过滤常见停用词
        stop_words = {'的', '是', '在', '有', '和', '与', '或', '但', '然而', '因为', '所以', '如果', '那么', '这', '那', '什么', '怎么', '为什么', '哪里', '谁', 'when', 'what', 'where', 'who', 'why', 'how', 'the', 'is', 'are', 'and', 'or', 'but', 'if', 'then'}
        keywords = [word for word in words if word not in stop_words and len(word) > 1]
        return keywords[:10]  # 返回前10个关键词
    
    def _extract_entities(self, text: str) -> list:
        """提取实体（简单实现）"""
        # 这里可以使用NER模型，现在先用简单的正则匹配
        import re
        entities = []
        
        # 匹配日期
        date_pattern = r'\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日]?'
        dates = re.findall(date_pattern, text)
        entities.extend([{'type': 'date', 'value': date} for date in dates])
        
        # 匹配数字
        number_pattern = r'\d+\.?\d*'
        numbers = re.findall(number_pattern, text)
        entities.extend([{'type': 'number', 'value': num} for num in numbers[:5]])
        
        return entities
    
    def _analyze_sentiment(self, text: str) -> str:
        """分析情感（简单实现）"""
        # 简单的情感分析，基于关键词
        positive_words = ['好', '棒', '优秀', '满意', '喜欢', '赞', '不错', 'good', 'great', 'excellent', 'like', 'love']
        negative_words = ['坏', '差', '糟糕', '不满', '讨厌', '烂', '问题', 'bad', 'terrible', 'hate', 'problem', 'issue']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _assess_complexity(self, text: str) -> str:
        """评估查询复杂度"""
        length = len(text)
        word_count = len(text.split())
        
        # 检查是否包含复杂的逻辑词
        complex_indicators = ['如果', '但是', '然而', '因为', '所以', '不仅', '而且', 'if', 'but', 'however', 'because', 'therefore']
        has_complex_logic = any(indicator in text.lower() for indicator in complex_indicators)
        
        if length > 100 or word_count > 20 or has_complex_logic:
            return 'high'
        elif length > 50 or word_count > 10:
            return 'medium'
        else:
            return 'low'