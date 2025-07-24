"""
数据处理工具类
用于处理和分析Facebook群组数据
"""

import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import re
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import PROCESSED_DATA_DIR, EXPORTS_DIR

class DataProcessor:
    """Facebook数据处理器"""
    
    def __init__(self):
        self.data = None
        self.processed_data = None
    
    def load_data(self, filepath: str) -> List[Dict[str, Any]]:
        """加载JSON数据"""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        return self.data
    
    def process_posts(self, data: List[Dict[str, Any]] = None) -> pd.DataFrame:
        """处理帖子数据"""
        if data is None:
            data = self.data
        
        if not data:
            return pd.DataFrame()
        
        processed_posts = []
        
        for item in data:
            # 提取帖子信息
            post_info = {
                'post_id': item.get('post_id', ''),
                'group_url': item.get('group_url', ''),
                'post_url': item.get('post_url', ''),
                'post_text': item.get('post_text', ''),
                'user_name': item.get('user_name', ''),
                'user_url': item.get('user_url', ''),
                'post_time': item.get('post_time', ''),
                'likes_count': item.get('likes_count', 0),
                'comments_count': item.get('comments_count', 0),
                'shares_count': item.get('shares_count', 0),
                'post_type': item.get('post_type', ''),
                'attachments': item.get('attachments', []),
                'hashtags': self.extract_hashtags(item.get('post_text', '')),
                'mentions': self.extract_mentions(item.get('post_text', '')),
                'text_length': len(item.get('post_text', '')),
                'has_image': bool(item.get('attachments', [])),
                'engagement_score': self.calculate_engagement(item)
            }
            
            processed_posts.append(post_info)
        
        df = pd.DataFrame(processed_posts)
        
        # 数据类型转换
        if not df.empty:
            df['post_time'] = pd.to_datetime(df['post_time'], errors='coerce')
            df['likes_count'] = pd.to_numeric(df['likes_count'], errors='coerce').fillna(0)
            df['comments_count'] = pd.to_numeric(df['comments_count'], errors='coerce').fillna(0)
            df['shares_count'] = pd.to_numeric(df['shares_count'], errors='coerce').fillna(0)
        
        self.processed_data = df
        return df
    
    def extract_hashtags(self, text: str) -> List[str]:
        """提取话题标签"""
        if not text:
            return []
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def extract_mentions(self, text: str) -> List[str]:
        """提取@提及"""
        if not text:
            return []
        mentions = re.findall(r'@\w+', text)
        return mentions
    
    def calculate_engagement(self, item: Dict[str, Any]) -> float:
        """计算互动分数"""
        likes = int(item.get('likes_count', 0))
        comments = int(item.get('comments_count', 0))
        shares = int(item.get('shares_count', 0))
        
        # 简单的互动分数计算 (可以根据需要调整权重)
        engagement = likes * 1 + comments * 2 + shares * 3
        return engagement
    
    def get_summary_stats(self, df: pd.DataFrame = None) -> Dict[str, Any]:
        """获取数据摘要统计"""
        if df is None:
            df = self.processed_data
        
        if df.empty:
            return {}
        
        stats = {
            'total_posts': len(df),
            'unique_users': df['user_name'].nunique(),
            'date_range': {
                'start': df['post_time'].min().strftime('%Y-%m-%d') if df['post_time'].min() else None,
                'end': df['post_time'].max().strftime('%Y-%m-%d') if df['post_time'].max() else None
            },
            'engagement_stats': {
                'total_likes': int(df['likes_count'].sum()),
                'total_comments': int(df['comments_count'].sum()),
                'total_shares': int(df['shares_count'].sum()),
                'avg_engagement': float(df['engagement_score'].mean())
            },
            'content_stats': {
                'avg_text_length': float(df['text_length'].mean()),
                'posts_with_images': int(df['has_image'].sum()),
                'posts_with_hashtags': int(df['hashtags'].apply(len).gt(0).sum())
            }
        }
        
        return stats
    
    def save_processed_data(self, df: pd.DataFrame, format: str = 'json', filename: str = None):
        """保存处理后的数据"""
        if df.empty:
            print("没有数据可保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == 'json':
            if not filename:
                filename = f"processed_posts_{timestamp}.json"
            filepath = os.path.join(PROCESSED_DATA_DIR, filename)
            df.to_json(filepath, orient='records', force_ascii=False, indent=2)
        
        elif format == 'csv':
            if not filename:
                filename = f"processed_posts_{timestamp}.csv"
            filepath = os.path.join(PROCESSED_DATA_DIR, filename)
            df.to_csv(filepath, index=False, encoding='utf-8')
        
        elif format == 'xlsx':
            if not filename:
                filename = f"processed_posts_{timestamp}.xlsx"
            filepath = os.path.join(PROCESSED_DATA_DIR, filename)
            df.to_excel(filepath, index=False)
        
        print(f"处理后的数据已保存到: {filepath}")
        return filepath 