from typing import List, Dict, Any, Optional
import os
import asyncio
from .kb_loader import MogineKBLoader

class KnowledgeBase:
    """本地知识库 - 使用摩泛科技知识库"""
    
    def __init__(self):
        # 初始化摩泛科技知识库加载器
        self.kb_loader = MogineKBLoader()
        self.company_info = self.kb_loader.get_company_info()
        self.assistant_info = self.kb_loader.get_assistant_info()
    
    async def query(self, query_text: str, top_k: int = 3) -> Dict[str, Any]:
        """查询知识库"""
        try:
            # 在异步环境中运行知识库搜索
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None, 
                lambda: self.kb_loader.search_knowledge(query_text, top_k)
            )
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_result = {
                    "content": result.get('content', ''),
                    "title": result.get('title', ''),
                    "type": result.get('type', ''),
                    "source": result.get('source', ''),
                    "relevance_score": result.get('relevance_score', 0.0)
                }
                
                # 添加解决方案信息（如果有）
                if result.get('solution'):
                    formatted_result["solution"] = result.get('solution')
                
                # 添加URL信息（如果是外部链接）
                if result.get('url'):
                    formatted_result["url"] = result.get('url')
                
                # 添加媒体文件信息
                if result.get('media_files'):
                    formatted_result["media_files"] = result.get('media_files')
                
                formatted_results.append(formatted_result)
            
            return {
                "success": True,
                "query": query_text,
                "results": formatted_results,
                "total_found": len(formatted_results),
                "company_info": self.company_info,
                "assistant_info": self.assistant_info
            }
            
        except Exception as e:
            print(f"知识库查询错误: {e}")
            return {
                "success": False,
                "query": query_text,
                "error": str(e),
                "results": [],
                "company_info": self.company_info,
                "assistant_info": self.assistant_info
            }
    
    def add_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None):
        """添加文档到知识库"""
        try:
            self.collection.add(
                documents=[content],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
            return True
        except Exception as e:
            print(f"添加文档错误: {e}")
            return False
    
    def update_document(self, doc_id: str, content: str, metadata: Dict[str, Any] = None):
        """更新知识库中的文档"""
        try:
            self.collection.update(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata or {}]
            )
            return True
        except Exception as e:
            print(f"更新文档错误: {e}")
            return False
    
    def delete_document(self, doc_id: str):
        """从知识库删除文档"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"删除文档错误: {e}")
            return False