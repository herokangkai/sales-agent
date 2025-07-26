import asyncio
import json
import time
import uuid
from typing import AsyncGenerator, Dict, List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai
from chatbot.intent_analyzer import IntentAnalyzer
from chatbot.knowledge_base import KnowledgeBase
from chatbot.external_agent import ExternalAgent
from chatbot.response_integrator import ResponseIntegrator
from chatbot.query_logger import QueryLogger

app = FastAPI(title="智能聊天机器人")

# 初始化组件
intent_analyzer = IntentAnalyzer()
knowledge_base = KnowledgeBase()
external_agent = ExternalAgent()
response_integrator = ResponseIntegrator()
query_logger = QueryLogger()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    user_id: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """返回聊天界面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>智能聊天机器人</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .chat-container { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .chat-header { background: #007bff; color: white; padding: 20px; text-align: center; }
            .chat-messages { height: 400px; overflow-y: auto; padding: 20px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background: #e3f2fd; margin-left: 20%; }
            .bot-message { background: #f5f5f5; margin-right: 20%; }
            .input-area { padding: 20px; border-top: 1px solid #eee; display: flex; }
            .input-area input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-right: 10px; }
            .input-area button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .typing { color: #666; font-style: italic; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>智能聊天机器人</h1>
                <p>支持本地知识库查询和外部Agent调用</p>
            </div>
            <div class="chat-messages" id="messages"></div>
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="输入您的问题..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">发送</button>
            </div>
        </div>

        <script>
            function addMessage(content, isUser = false) {
                const messages = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                messageDiv.innerHTML = content;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;

                addMessage(message, true);
                input.value = '';

                const botMessageDiv = document.createElement('div');
                botMessageDiv.className = 'message bot-message';
                document.getElementById('messages').appendChild(botMessageDiv);

                try {
                    const response = await fetch('/chat/stream', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message: message })
                    });

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let content = '';

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value);
                        const lines = chunk.split('\\n');
                        
                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                const data = line.slice(6);
                                if (data === '[DONE]') return;
                                
                                try {
                                    const parsed = JSON.parse(data);
                                    content += parsed.content;
                                    botMessageDiv.innerHTML = content.replace(/\\n/g, '<br>');
                                    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
                                } catch (e) {}
                            }
                        }
                    }
                } catch (error) {
                    botMessageDiv.innerHTML = '抱歉，发生了错误，请稍后重试。';
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, client_request: Request):
    """流式聊天接口"""
    # 生成用户ID（如果没有提供）
    user_id = request.user_id or str(uuid.uuid4())
    session_id = request.session_id or "default"
    
    # 获取客户端信息
    user_agent = client_request.headers.get("user-agent", "")
    client_ip = client_request.client.host if client_request.client else ""
    
    start_time = time.time()
    response_sources = []
    
    async def generate_response():
        try:
            # 1. 意图分析和拆解
            yield f"data: {json.dumps({'content': '正在分析您的问题...\\n'})}\n\n"
            
            intent_result = await intent_analyzer.analyze_intent(
                request.message, 
                user_id=user_id, 
                session_id=session_id
            )
            
            yield f"data: {json.dumps({'content': f'意图识别完成: {intent_result.summary}\\n\\n'})}\n\n"
            
            # 2. 并行查询本地知识库和外部Agent
            yield f"data: {json.dumps({'content': '正在查询相关信息...\\n'})}\n\n"
            
            tasks = []
            if intent_result.needs_knowledge_base:
                tasks.append(knowledge_base.query(intent_result.knowledge_query))
                response_sources.append("knowledge_base")
            if intent_result.needs_external_agent:
                tasks.append(external_agent.query(intent_result.agent_query))
                response_sources.append("external_agent")
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 3. 整合结果并流式输出
            yield f"data: {json.dumps({'content': '正在整理答案...\\n\\n'})}\n\n"
            
            knowledge_result = results[0] if intent_result.needs_knowledge_base else None
            agent_result = results[1] if intent_result.needs_external_agent else (results[0] if not intent_result.needs_knowledge_base else None)
            
            # 流式生成最终回答
            async for chunk in response_integrator.integrate_and_stream(
                original_question=request.message,
                intent_result=intent_result,
                knowledge_result=knowledge_result,
                agent_result=agent_result
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # 记录完整的对话日志
            processing_time = time.time() - start_time
            query_logger.log_query(
                query_text=request.message,
                user_id=user_id,
                session_id=session_id,
                intent_category=intent_result.summary,
                intent_confidence=intent_result.confidence,
                response_type="chat_completion",
                response_sources=response_sources,
                processing_time=processing_time,
                user_agent=user_agent,
                ip_address=client_ip,
                metadata={
                    "needs_knowledge_base": intent_result.needs_knowledge_base,
                    "needs_external_agent": intent_result.needs_external_agent,
                    "knowledge_query": intent_result.knowledge_query,
                    "agent_query": intent_result.agent_query,
                    "has_knowledge_result": knowledge_result is not None,
                    "has_agent_result": agent_result is not None
                }
            )
                
        except Exception as e:
            # 记录错误日志
            processing_time = time.time() - start_time
            query_logger.log_query(
                query_text=request.message,
                user_id=user_id,
                session_id=session_id,
                intent_category="error",
                intent_confidence=0.0,
                response_type="chat_error",
                response_sources=[],
                processing_time=processing_time,
                user_agent=user_agent,
                ip_address=client_ip,
                metadata={"error": str(e)}
            )
            yield f"data: {json.dumps({'content': f'抱歉，处理过程中出现错误: {str(e)}'})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate_response(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)