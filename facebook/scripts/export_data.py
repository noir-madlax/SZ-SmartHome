#!/usr/bin/env python3
"""
Facebook群组数据导出脚本
将处理过的数据导出为不同格式，用于报告和分析
"""

import os
import sys
import argparse
import json
import pandas as pd
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import PROCESSED_DATA_DIR, EXPORTS_DIR

def export_to_excel(df: pd.DataFrame, filename: str = None) -> str:
    """导出到Excel文件，包含多个工作表"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"smart_home_facebook_report_{timestamp}.xlsx"
    
    filepath = os.path.join(EXPORTS_DIR, filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # 主数据表
        df.to_excel(writer, sheet_name='Posts', index=False)
        
        # 用户统计表
        user_stats = df.groupby('user_name').agg({
            'post_id': 'count',
            'likes_count': 'sum',
            'comments_count': 'sum',
            'shares_count': 'sum',
            'engagement_score': 'mean',
            'text_length': 'mean'
        }).rename(columns={
            'post_id': 'posts_count',
            'likes_count': 'total_likes',
            'comments_count': 'total_comments',  
            'shares_count': 'total_shares',
            'engagement_score': 'avg_engagement',
            'text_length': 'avg_text_length'
        }).sort_values('posts_count', ascending=False)
        
        user_stats.to_excel(writer, sheet_name='User Stats')
        
        # 日期统计表
        if 'post_time' in df.columns and not df['post_time'].isnull().all():
            df['date'] = df['post_time'].dt.date
            daily_stats = df.groupby('date').agg({
                'post_id': 'count',
                'likes_count': 'sum',
                'comments_count': 'sum',
                'shares_count': 'sum',
                'engagement_score': 'mean'
            }).rename(columns={
                'post_id': 'posts_count',
                'likes_count': 'total_likes',
                'comments_count': 'total_comments',
                'shares_count': 'total_shares',
                'engagement_score': 'avg_engagement'
            })
            
            daily_stats.to_excel(writer, sheet_name='Daily Stats')
        
        # 话题标签统计
        if 'hashtags' in df.columns:
            all_hashtags = []
            for hashtags in df['hashtags']:
                if isinstance(hashtags, list):
                    all_hashtags.extend(hashtags)
            
            if all_hashtags:
                from collections import Counter
                hashtag_counts = Counter(all_hashtags)
                hashtag_df = pd.DataFrame(hashtag_counts.most_common(), 
                                        columns=['Hashtag', 'Count'])
                hashtag_df.to_excel(writer, sheet_name='Hashtags', index=False)
    
    print(f"Excel报告已导出到: {filepath}")
    return filepath

def export_summary_report(df: pd.DataFrame, filename: str = None) -> str:
    """导出摘要报告 (JSON格式)"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"smart_home_summary_{timestamp}.json"
    
    filepath = os.path.join(EXPORTS_DIR, filename)
    
    # 基础统计
    summary = {
        'report_generated': datetime.now().isoformat(),
        'data_source': 'Facebook Smart Home Group',
        'group_id': '2091834914421201',
        'total_posts': len(df),
        'unique_users': df['user_name'].nunique() if 'user_name' in df.columns else 0,
        'date_range': {
            'start': df['post_time'].min().isoformat() if 'post_time' in df.columns and not df['post_time'].isnull().all() else None,
            'end': df['post_time'].max().isoformat() if 'post_time' in df.columns and not df['post_time'].isnull().all() else None
        },
        'engagement_overview': {
            'total_likes': int(df['likes_count'].sum()) if 'likes_count' in df.columns else 0,
            'total_comments': int(df['comments_count'].sum()) if 'comments_count' in df.columns else 0,
            'total_shares': int(df['shares_count'].sum()) if 'shares_count' in df.columns else 0,
            'average_engagement': float(df['engagement_score'].mean()) if 'engagement_score' in df.columns else 0
        },
        'content_analysis': {
            'average_text_length': float(df['text_length'].mean()) if 'text_length' in df.columns else 0,
            'posts_with_images': int(df['has_image'].sum()) if 'has_image' in df.columns else 0,
            'posts_with_hashtags': int(df['hashtags'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False).sum()) if 'hashtags' in df.columns else 0
        }
    }
    
    # Top用户
    if 'user_name' in df.columns:
        top_users = df.groupby('user_name').agg({
            'post_id': 'count',
            'engagement_score': 'mean'
        }).rename(columns={
            'post_id': 'posts_count',
            'engagement_score': 'avg_engagement'
        }).sort_values('posts_count', ascending=False).head(10)
        
        summary['top_users'] = [
            {
                'username': user,
                'posts_count': int(stats['posts_count']),
                'avg_engagement': float(stats['avg_engagement'])
            }
            for user, stats in top_users.iterrows()
        ]
    
    # 热门话题标签
    if 'hashtags' in df.columns:
        all_hashtags = []
        for hashtags in df['hashtags']:
            if isinstance(hashtags, list):
                all_hashtags.extend(hashtags)
        
        if all_hashtags:
            from collections import Counter
            hashtag_counts = Counter(all_hashtags)
            summary['top_hashtags'] = [
                {'hashtag': tag, 'count': count}
                for tag, count in hashtag_counts.most_common(20)
            ]
    
    # 高互动帖子
    if 'engagement_score' in df.columns:
        top_posts = df.nlargest(10, 'engagement_score')[
            ['post_url', 'post_text', 'user_name', 'engagement_score', 'likes_count', 'comments_count']
        ].to_dict('records')
        
        summary['top_engaging_posts'] = [
            {
                'url': post.get('post_url', ''),
                'text': post.get('post_text', '')[:200] + '...' if len(post.get('post_text', '')) > 200 else post.get('post_text', ''),
                'user': post.get('user_name', ''),
                'engagement_score': float(post.get('engagement_score', 0)),
                'likes': int(post.get('likes_count', 0)),
                'comments': int(post.get('comments_count', 0))
            }
            for post in top_posts
        ]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"摘要报告已导出到: {filepath}")
    return filepath

def list_processed_files():
    """列出处理过的数据文件"""
    if not os.path.exists(PROCESSED_DATA_DIR):
        print("❌ 处理数据目录不存在")
        return []
    
    files = []
    for f in os.listdir(PROCESSED_DATA_DIR):
        if f.endswith(('.json', '.csv', '.xlsx')):
            files.append(f)
    
    if not files:
        print("❌ 没有找到处理过的数据文件")
        return []
    
    print("处理过的数据文件:")
    print("-" * 60)
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(PROCESSED_DATA_DIR, filename)
        size = os.path.getsize(filepath)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        print(f"{i:2d}. {filename:<40} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
    
    return files

def load_processed_data(filepath: str) -> pd.DataFrame:
    """加载处理过的数据"""
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.json':
        return pd.read_json(filepath)
    elif ext == '.csv':
        return pd.read_csv(filepath)
    elif ext == '.xlsx':
        return pd.read_excel(filepath)
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

def main():
    parser = argparse.ArgumentParser(description='Facebook群组数据导出工具')
    parser.add_argument('--file', '-f', help='指定要导出的处理数据文件路径')
    parser.add_argument('--latest', '-l', action='store_true', help='导出最新的处理数据文件')
    parser.add_argument('--list', '-ls', action='store_true', help='列出处理过的数据文件')
    parser.add_argument('--format', '-fmt', choices=['excel', 'summary', 'both'], default='both', help='导出格式')
    parser.add_argument('--output', '-o', help='输出文件名')
    
    args = parser.parse_args()
    
    if args.list:
        list_processed_files()
        return
    
    # 确定要处理的文件
    if args.file:
        if not os.path.exists(args.file):
            print(f"❌ 文件不存在: {args.file}")
            return
        filepath = args.file
    elif args.latest:
        files = list_processed_files()
        if not files:
            return
        
        # 找到最新的文件
        files_with_time = []
        for filename in files:
            file_path = os.path.join(PROCESSED_DATA_DIR, filename)
            mtime = os.path.getmtime(file_path)
            files_with_time.append((filename, mtime))
        
        files_with_time.sort(key=lambda x: x[1], reverse=True)
        latest_file = files_with_time[0][0]
        filepath = os.path.join(PROCESSED_DATA_DIR, latest_file)
        print(f"使用最新文件: {latest_file}")
    else:
        print("请指定要导出的文件 (--file 或 --latest)")
        return
    
    try:
        # 加载数据
        df = load_processed_data(filepath)
        print(f"加载数据: {len(df)} 条记录")
        
        # 导出
        if args.format in ['excel', 'both']:
            excel_file = f"{args.output}.xlsx" if args.output else None
            export_to_excel(df, excel_file)
        
        if args.format in ['summary', 'both']:
            summary_file = f"{args.output}_summary.json" if args.output else None
            export_summary_report(df, summary_file)
        
        print("\n✅ 导出完成!")
        
    except Exception as e:
        print(f"❌ 导出失败: {str(e)}")

if __name__ == "__main__":
    main() 