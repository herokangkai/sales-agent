import xml.etree.ElementTree as ET
import os
from typing import Dict, List, Any, Optional
import re

class MogineKBLoader:
    """摩泛科技知识库加载器"""
    
    def __init__(self, kb_path: str = "kb/mogine_unified_kb_fixed.xml"):
        self.kb_path = kb_path
        self.knowledge_data = {}
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """加载XML知识库"""
        try:
            if not os.path.exists(self.kb_path):
                print(f"知识库文件不存在: {self.kb_path}")
                return
            
            tree = ET.parse(self.kb_path)
            root = tree.getroot()
            
            # 解析公司基本信息
            self._parse_metadata(root)
            
            # 解析内容结构
            self._parse_content_structure(root)
            
            # 解析外部链接
            self._parse_external_links(root)
            
            print(f"✅ 成功加载知识库，共 {len(self.knowledge_data)} 个条目")
            
        except Exception as e:
            print(f"❌ 加载知识库失败: {e}")
    
    def _parse_metadata(self, root):
        """解析元数据信息"""
        metadata = root.find('metadata')
        if metadata is not None:
            company = metadata.find('company')
            if company is not None:
                self.knowledge_data['company_info'] = {
                    'name_cn': self._get_text(company, 'name_cn', '摩泛科技'),
                    'name_en': self._get_text(company, 'name_en', 'Mogine'),
                    'full_name_cn': self._get_text(company, 'full_name_cn'),
                    'full_name_en': self._get_text(company, 'full_name_en'),
                    'website': self._get_text(company, 'website'),
                    'description': '高保真AI空间计算数字孪生专家'
                }
            
            assistant = metadata.find('assistant')
            if assistant is not None:
                self.knowledge_data['assistant_info'] = {
                    'name': self._get_text(assistant, 'n', '小摩'),
                    'full_name': self._get_text(assistant, 'full_name', '摩泛AI小助手')
                }
    
    def _parse_content_structure(self, root):
        """解析内容结构"""
        content_structure = root.find('content_structure')
        if content_structure is not None:
            for section in content_structure.findall('section'):
                section_id = section.get('id')
                section_title = section.get('title')
                
                section_data = {
                    'title': section_title,
                    'title_en': section.get('title_en', ''),
                    'subsections': []
                }
                
                for subsection in section.findall('subsection'):
                    subsection_data = self._parse_subsection(subsection)
                    section_data['subsections'].append(subsection_data)
                
                self.knowledge_data[section_id] = section_data
    
    def _parse_subsection(self, subsection):
        """解析子章节"""
        subsection_data = {
            'id': subsection.get('id'),
            'title': subsection.get('title'),
            'level': subsection.get('level'),
            'page': subsection.get('page'),
            'content': [],
            'images': [],
            'solution': []
        }
        
        # 解析文本内容
        content = subsection.find('content')
        if content is not None:
            for text_elem in content.findall('text'):
                text_content = text_elem.text
                if text_content:
                    subsection_data['content'].append(text_content.strip())
        
        # 解析解决方案
        solution = subsection.find('solution')
        if solution is not None:
            for text_elem in solution.findall('text'):
                text_content = text_elem.text
                if text_content:
                    subsection_data['solution'].append(text_content.strip())
        
        # 解析图片信息
        images = subsection.find('images')
        if images is not None:
            for image in images.findall('image'):
                image_data = {
                    'path': image.get('path'),
                    'caption': image.get('caption')
                }
                subsection_data['images'].append(image_data)
        
        return subsection_data
    
    def _parse_external_links(self, root):
        """解析外部链接"""
        external_links = root.find('external_links')
        if external_links is not None:
            links_data = []
            for link in external_links.findall('link'):
                link_data = {
                    'id': link.get('id'),
                    'title': self._get_text(link, 'title'),
                    'url': self._get_text(link, 'url'),
                    'description': self._get_text(link, 'description'),
                    'keywords': []
                }
                
                keywords = link.find('keywords')
                if keywords is not None:
                    for keyword in keywords.findall('keyword'):
                        if keyword.text:
                            link_data['keywords'].append(keyword.text.strip())
                
                links_data.append(link_data)
            
            self.knowledge_data['external_links'] = links_data
    
    def _get_text(self, parent, tag, default=''):
        """安全获取XML元素文本"""
        element = parent.find(tag)
        return element.text.strip() if element is not None and element.text else default
    
    def search_knowledge(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """搜索知识库"""
        query_lower = query.lower()
        results = []
        
        # 搜索公司信息
        if any(keyword in query_lower for keyword in ['公司', '摩泛', 'mogine', '介绍', '关于', '什么']):
            company_info = self.knowledge_data.get('company_info', {})
            if company_info:
                results.append({
                    'type': 'company_info',
                    'title': '公司信息',
                    'content': f"{company_info.get('full_name_cn', '')} ({company_info.get('name_en', '')}) - {company_info.get('description', '')}",
                    'relevance_score': 0.9,
                    'source': '公司基本信息'
                })
        
        # 搜索具体内容 - 改进搜索逻辑
        for section_id, section_data in self.knowledge_data.items():
            if section_id in ['company_info', 'assistant_info', 'external_links']:
                continue
            
            section_title = section_data.get('title', '')
            
            # 遍历所有子章节
            for subsection in section_data.get('subsections', []):
                subsection_title = subsection.get('title', '')
                content_text = ' '.join(subsection.get('content', []))
                solution_text = ' '.join(subsection.get('solution', []))
                full_text = f"{subsection_title} {content_text} {solution_text}"
                
                # 计算相关性
                relevance = self._calculate_relevance(query_lower, full_text.lower())
                
                # 特定关键词匹配加分
                keyword_bonus = 0
                if '数字孪生' in query_lower and '数字孪生' in full_text.lower():
                    keyword_bonus += 0.3
                if 'mohuman' in query_lower.replace(' ', '') and 'mohuman' in full_text.lower():
                    keyword_bonus += 0.3
                if 'mobox' in query_lower.replace(' ', '') and 'mobox' in full_text.lower():
                    keyword_bonus += 0.3
                if '钱学森' in query_lower and '钱学森' in full_text.lower():
                    keyword_bonus += 0.4
                if 'usd' in query_lower and 'usd' in full_text.lower():
                    keyword_bonus += 0.3
                if '3d' in query_lower and '3d' in full_text.lower():
                    keyword_bonus += 0.2
                if '协作' in query_lower and '协作' in full_text.lower():
                    keyword_bonus += 0.2
                
                final_relevance = relevance + keyword_bonus
                
                if final_relevance > 0.15 and (content_text or solution_text):
                    # 获取相关的图片和视频
                    media_files = []
                    for image in subsection.get('images', []):
                        media_files.append({
                            'type': 'image' if not image.get('path', '').endswith('.mp4') else 'video',
                            'path': image.get('path', ''),
                            'caption': image.get('caption', ''),
                            'full_path': f"/Users/kangkai/Desktop/AI Projects/academic_agent/sales-agent/kb/{image.get('path', '')}"
                        })
                    
                    results.append({
                        'type': 'content',
                        'title': subsection_title,
                        'content': content_text,
                        'solution': solution_text,
                        'media_files': media_files,
                        'relevance_score': final_relevance,
                        'source': f"{section_title} - {subsection_title}"
                    })
        
        # 搜索外部链接
        external_links = self.knowledge_data.get('external_links', [])
        for link in external_links:
            link_text = f"{link.get('title', '')} {link.get('description', '')} {' '.join(link.get('keywords', []))}"
            relevance = self._calculate_relevance(query_lower, link_text.lower())
            if relevance > 0.2:
                results.append({
                    'type': 'external_link',
                    'title': link.get('title', ''),
                    'content': link.get('description', ''),
                    'url': link.get('url', ''),
                    'relevance_score': relevance,
                    'source': '外部链接'
                })
        
        # 按相关性排序并返回前top_k个结果
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:top_k]
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """简单的文本相似度计算"""
        words1 = set(re.findall(r'\w+', text1))
        words2 = set(re.findall(r'\w+', text2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_relevance(self, query: str, text: str) -> float:
        """计算查询与文本的相关性"""
        if not query or not text:
            return 0.0
        
        # 中文分词简化处理
        query_chars = set(query.replace(' ', ''))
        text_chars = set(text.replace(' ', ''))
        
        # 字符级匹配
        char_matches = query_chars.intersection(text_chars)
        char_coverage = len(char_matches) / len(query_chars) if query_chars else 0
        
        # 词级匹配
        query_words = set(re.findall(r'\w+', query))
        text_words = set(re.findall(r'\w+', text))
        word_matches = query_words.intersection(text_words)
        word_coverage = len(word_matches) / len(query_words) if query_words else 0
        
        # 子串匹配
        substring_score = 0
        for i in range(2, min(len(query) + 1, 6)):  # 检查2-5字符的子串
            for j in range(len(query) - i + 1):
                substring = query[j:j+i]
                if substring in text:
                    substring_score += len(substring) / len(query)
        
        # 综合评分
        final_score = (char_coverage * 0.3 + word_coverage * 0.4 + substring_score * 0.3)
        
        # 考虑文本长度的影响
        length_factor = min(1.0, len(text) / 50)
        
        return final_score * 0.9 + length_factor * 0.1
    
    def get_company_info(self) -> Dict[str, Any]:
        """获取公司基本信息"""
        return self.knowledge_data.get('company_info', {})
    
    def get_assistant_info(self) -> Dict[str, Any]:
        """获取助手信息"""
        return self.knowledge_data.get('assistant_info', {})
    
    def get_all_sections(self) -> List[str]:
        """获取所有章节标题"""
        sections = []
        for section_id, section_data in self.knowledge_data.items():
            if section_id not in ['company_info', 'assistant_info', 'external_links']:
                sections.append(section_data.get('title', section_id))
        return sections