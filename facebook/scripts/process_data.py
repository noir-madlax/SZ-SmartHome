#!/usr/bin/env python3
"""
Facebook群组数据处理脚本
处理和分析下载的Smart Home群组数据
"""

import os
import sys
import argparse
import json
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processor import DataProcessor
from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR

def process_file(filepath: str, output_format: str = 'json'):
    """处理指定文件"""
    processor = DataProcessor()
    
    try:
        print(f"加载数据文件: {filepath}")
        data = processor.load_data(filepath)
        print(f"原始数据记录数: {len(data)}")
        
        print("\n处理帖子数据...")
        df = processor.process_posts(data)
        
        if df.empty:
            print("❌ 没有可处理的数据")
            return None
        
        print(f"处理后记录数: {len(df)}")
        
        # 获取统计信息
        stats = processor.get_summary_stats(df)
        print("\n📊 数据统计:")
        print(f"  总帖子数: {stats['total_posts']}")
        print(f"  用户数: {stats['unique_users']}")
        print(f"  时间范围: {stats['date_range']['start']} 到 {stats['date_range']['end']}")
        print(f"  总点赞数: {stats['engagement_stats']['total_likes']}")
        print(f"  总评论数: {stats['engagement_stats']['total_comments']}")
        print(f"  总分享数: {stats['engagement_stats']['total_shares']}")
        print(f"  平均互动分数: {stats['engagement_stats']['avg_engagement']:.2f}")
        print(f"  包含图片的帖子: {stats['content_stats']['posts_with_images']}")
        print(f"  包含话题标签的帖子: {stats['content_stats']['posts_with_hashtags']}")
        
        # 保存处理后的数据
        print(f"\n保存处理后的数据 (格式: {output_format})...")
        output_filepath = processor.save_processed_data(df, format=output_format)
        
        # 保存统计信息
        stats_filename = f"stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        stats_filepath = os.path.join(PROCESSED_DATA_DIR, stats_filename)
        with open(stats_filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        print(f"统计信息已保存到: {stats_filepath}")
        
        print(f"\n✅ 数据处理完成!")
        return output_filepath
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        return None

def list_raw_files():
    """列出原始数据文件"""
    if not os.path.exists(RAW_DATA_DIR):
        print("❌ 原始数据目录不存在")
        return []
    
    files = [f for f in os.listdir(RAW_DATA_DIR) if f.endswith('.json')]
    
    if not files:
        print("❌ 没有找到原始数据文件")
        return []
    
    print("原始数据文件:")
    print("-" * 60)
    for i, filename in enumerate(files, 1):
        filepath = os.path.join(RAW_DATA_DIR, filename)
        size = os.path.getsize(filepath)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        print(f"{i:2d}. {filename:<30} ({size:,} bytes, {mtime.strftime('%Y-%m-%d %H:%M')})")
    
    return files

def process_latest_file(output_format: str = 'json'):
    """处理最新的原始数据文件"""
    files = list_raw_files()
    if not files:
        return None
    
    # 按修改时间排序，获取最新文件
    files_with_time = []
    for filename in files:
        filepath = os.path.join(RAW_DATA_DIR, filename)
        mtime = os.path.getmtime(filepath)
        files_with_time.append((filename, mtime))
    
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    latest_file = files_with_time[0][0]
    
    print(f"\n处理最新文件: {latest_file}")
    latest_filepath = os.path.join(RAW_DATA_DIR, latest_file)
    
    return process_file(latest_filepath, output_format)

def analyze_trends(filepath: str):
    """分析趋势数据"""
    processor = DataProcessor()
    
    try:
        data = processor.load_data(filepath)
        df = processor.process_posts(data)
        
        if df.empty:
            print("❌ 没有数据可分析")
            return
        
        print("\n📈 趋势分析:")
        
        # 按日期分组分析
        if 'post_time' in df.columns and not df['post_time'].isnull().all():
            df['date'] = df['post_time'].dt.date
            daily_stats = df.groupby('date').agg({
                'post_id': 'count',
                'likes_count': 'sum',
                'comments_count': 'sum',
                'engagement_score': 'mean'
            }).rename(columns={'post_id': 'posts_count'})
            
            print("\n每日统计 (最近10天):")
            print("-" * 70)
            print(f"{'日期':<12} {'帖子数':<8} {'点赞数':<8} {'评论数':<8} {'平均互动':<10}")
            print("-" * 70)
            
            for date, row in daily_stats.tail(10).iterrows():
                print(f"{date} {int(row['posts_count']):>6} {int(row['likes_count']):>7} {int(row['comments_count']):>7} {row['engagement_score']:>9.1f}")
        
        # 用户活跃度分析
        user_stats = df.groupby('user_name').agg({
            'post_id': 'count',
            'likes_count': 'sum',
            'engagement_score': 'mean'
        }).rename(columns={'post_id': 'posts_count'}).sort_values('posts_count', ascending=False)
        
        print(f"\n最活跃用户 (Top 10):")
        print("-" * 60)
        print(f"{'用户名':<20} {'帖子数':<8} {'总点赞':<8} {'平均互动':<10}")
        print("-" * 60)
        
        for user, row in user_stats.head(10).iterrows():
            print(f"{user[:18]:<20} {int(row['posts_count']):>6} {int(row['likes_count']):>7} {row['engagement_score']:>9.1f}")
        
        # 话题标签分析
        if 'hashtags' in df.columns:
            all_hashtags = []
            for hashtags in df['hashtags']:
                if isinstance(hashtags, list):
                    all_hashtags.extend(hashtags)
            
            if all_hashtags:
                from collections import Counter
                hashtag_counts = Counter(all_hashtags)
                
                print(f"\n热门话题标签 (Top 10):")
                print("-" * 30)
                for hashtag, count in hashtag_counts.most_common(10):
                    print(f"{hashtag:<20} {count:>6}")
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Facebook群组数据处理工具')
    parser.add_argument('--file', '-f', help='指定要处理的原始数据文件路径')
    parser.add_argument('--latest', '-l', action='store_true', help='处理最新的原始数据文件')
    parser.add_argument('--list', '-ls', action='store_true', help='列出原始数据文件')
    parser.add_argument('--format', '-fmt', choices=['json', 'csv', 'xlsx'], default='json', help='输出格式')
    parser.add_argument('--analyze', '-a', help='分析指定文件的趋势数据')
    
    args = parser.parse_args()
    
    if args.list:
        list_raw_files()
    elif args.file:
        if os.path.exists(args.file):
            process_file(args.file, args.format)
        else:
            print(f"❌ 文件不存在: {args.file}")
    elif args.latest:
        process_latest_file(args.format)
    elif args.analyze:
        if os.path.exists(args.analyze):
            analyze_trends(args.analyze)
        else:
            print(f"❌ 文件不存在: {args.analyze}")
    else:
        print("请指定操作选项:")
        print("  --file <path>     处理指定的原始数据文件")
        print("  --latest          处理最新的原始数据文件")
        print("  --list            列出原始数据文件")
        print("  --format <fmt>    指定输出格式 (json/csv/xlsx)")
        print("  --analyze <path>  分析指定文件的趋势数据")
        print("\n示例:")
        print("  python process_data.py --latest --format csv")
        print("  python process_data.py --file data/raw/facebook_posts_xxx.json")
        print("  python process_data.py --analyze data/raw/facebook_posts_xxx.json")

if __name__ == "__main__":
    main() 