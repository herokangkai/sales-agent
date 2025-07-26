#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户查询日志记录器
用于存储用户查询数据，方便后期意图分析
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
from pathlib import Path

class QueryLogger:
    """用户查询日志记录器"""
    
    def __init__(self, db_path: str = "data/query_logs.db"):
        """
        初始化查询日志记录器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        
        # 确保数据目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 初始化数据库
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建用户查询表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_queries (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    session_id TEXT,
                    query_text TEXT NOT NULL,
                    query_length INTEGER,
                    intent_category TEXT,
                    intent_confidence REAL,
                    response_type TEXT,
                    response_sources TEXT,
                    processing_time REAL,
                    user_agent TEXT,
                    ip_address TEXT,
                    metadata TEXT
                )
            ''')
            
            # 创建意图分析表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS intent_analysis (
                    id TEXT PRIMARY KEY,
                    query_id TEXT,
                    intent_type TEXT,
                    confidence_score REAL,
                    keywords TEXT,
                    entities TEXT,
                    sentiment TEXT,
                    complexity_level TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (query_id) REFERENCES user_queries (id)
                )
            ''')
            
            # 创建查询统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_statistics (
                    date TEXT PRIMARY KEY,
                    total_queries INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    avg_query_length REAL DEFAULT 0,
                    top_intents TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON user_queries(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON user_queries(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_intent_category ON user_queries(intent_category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON query_statistics(date)')
            
            conn.commit()
    
    def log_query(self, 
                  query_text: str,
                  user_id: str = None,
                  session_id: str = None,
                  intent_category: str = None,
                  intent_confidence: float = None,
                  response_type: str = None,
                  response_sources: List[str] = None,
                  processing_time: float = None,
                  user_agent: str = None,
                  ip_address: str = None,
                  metadata: Dict[str, Any] = None) -> str:
        """
        记录用户查询
        
        Args:
            query_text: 查询文本
            user_id: 用户ID
            session_id: 会话ID
            intent_category: 意图分类
            intent_confidence: 意图置信度
            response_type: 响应类型
            response_sources: 响应来源列表
            processing_time: 处理时间（秒）
            user_agent: 用户代理
            ip_address: IP地址
            metadata: 额外元数据
            
        Returns:
            查询记录ID
        """
        query_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_queries (
                    id, user_id, session_id, query_text, query_length,
                    intent_category, intent_confidence, response_type,
                    response_sources, processing_time, user_agent,
                    ip_address, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                query_id,
                user_id,
                session_id,
                query_text,
                len(query_text),
                intent_category,
                intent_confidence,
                response_type,
                json.dumps(response_sources) if response_sources else None,
                processing_time,
                user_agent,
                ip_address,
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
        
        # 更新统计信息
        self._update_statistics()
        
        return query_id
    
    def log_intent_analysis(self,
                           query_id: str,
                           intent_type: str,
                           confidence_score: float,
                           keywords: List[str] = None,
                           entities: List[str] = None,
                           sentiment: str = None,
                           complexity_level: str = None):
        """
        记录意图分析结果
        
        Args:
            query_id: 查询ID
            intent_type: 意图类型
            confidence_score: 置信度分数
            keywords: 关键词列表
            entities: 实体列表
            sentiment: 情感分析结果
            complexity_level: 复杂度级别
        """
        analysis_id = str(uuid.uuid4())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO intent_analysis (
                    id, query_id, intent_type, confidence_score,
                    keywords, entities, sentiment, complexity_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_id,
                query_id,
                intent_type,
                confidence_score,
                json.dumps(keywords) if keywords else None,
                json.dumps(entities) if entities else None,
                sentiment,
                complexity_level
            ))
            
            conn.commit()
    
    def get_queries(self, 
                   limit: int = 100,
                   offset: int = 0,
                   user_id: str = None,
                   intent_category: str = None,
                   start_date: str = None,
                   end_date: str = None) -> List[Dict]:
        """
        获取查询记录
        
        Args:
            limit: 限制数量
            offset: 偏移量
            user_id: 用户ID过滤
            intent_category: 意图分类过滤
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            查询记录列表
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM user_queries WHERE 1=1"
            params = []
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
            
            if intent_category:
                query += " AND intent_category = ?"
                params.append(intent_category)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_intent_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        获取意图统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            统计信息字典
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取意图分布
            cursor.execute('''
                SELECT intent_category, COUNT(*) as count
                FROM user_queries 
                WHERE timestamp >= datetime('now', '-{} days')
                AND intent_category IS NOT NULL
                GROUP BY intent_category
                ORDER BY count DESC
            '''.format(days))
            
            intent_distribution = dict(cursor.fetchall())
            
            # 获取查询趋势
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM user_queries 
                WHERE timestamp >= datetime('now', '-{} days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            '''.format(days))
            
            query_trend = dict(cursor.fetchall())
            
            # 获取平均查询长度
            cursor.execute('''
                SELECT AVG(query_length) as avg_length
                FROM user_queries 
                WHERE timestamp >= datetime('now', '-{} days')
            '''.format(days))
            
            avg_length = cursor.fetchone()[0] or 0
            
            # 获取总查询数
            cursor.execute('''
                SELECT COUNT(*) as total
                FROM user_queries 
                WHERE timestamp >= datetime('now', '-{} days')
            '''.format(days))
            
            total_queries = cursor.fetchone()[0]
            
            return {
                'intent_distribution': intent_distribution,
                'query_trend': query_trend,
                'avg_query_length': round(avg_length, 2),
                'total_queries': total_queries,
                'period_days': days
            }
    
    def _update_statistics(self):
        """更新每日统计信息"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 获取今日统计
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_queries,
                    COUNT(DISTINCT user_id) as unique_users,
                    AVG(query_length) as avg_length
                FROM user_queries 
                WHERE DATE(timestamp) = ?
            ''', (today,))
            
            stats = cursor.fetchone()
            
            # 获取今日热门意图
            cursor.execute('''
                SELECT intent_category, COUNT(*) as count
                FROM user_queries 
                WHERE DATE(timestamp) = ? AND intent_category IS NOT NULL
                GROUP BY intent_category
                ORDER BY count DESC
                LIMIT 5
            ''', (today,))
            
            top_intents = dict(cursor.fetchall())
            
            # 更新或插入统计记录
            cursor.execute('''
                INSERT OR REPLACE INTO query_statistics (
                    date, total_queries, unique_users, avg_query_length, top_intents
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                today,
                stats[0],
                stats[1],
                stats[2] or 0,
                json.dumps(top_intents)
            ))
            
            conn.commit()
    
    def export_data(self, output_file: str, format: str = 'json'):
        """
        导出数据
        
        Args:
            output_file: 输出文件路径
            format: 导出格式 ('json' 或 'csv')
        """
        queries = self.get_queries(limit=10000)
        
        if format.lower() == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(queries, f, ensure_ascii=False, indent=2, default=str)
        elif format.lower() == 'csv':
            import csv
            if queries:
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=queries[0].keys())
                    writer.writeheader()
                    writer.writerows(queries)
    
    def cleanup_old_data(self, days: int = 90):
        """
        清理旧数据
        
        Args:
            days: 保留天数
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM user_queries 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
            cursor.execute('''
                DELETE FROM intent_analysis 
                WHERE created_at < datetime('now', '-{} days')
            '''.format(days))
            
            cursor.execute('''
                DELETE FROM query_statistics 
                WHERE date < date('now', '-{} days')
            '''.format(days))
            
            conn.commit()
            
            return cursor.rowcount