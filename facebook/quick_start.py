#!/usr/bin/env python3
"""
快速启动脚本
一键下载、处理和导出Facebook群组数据
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("🚀 Facebook Smart Home 群组数据爬取项目")
    print("=" * 50)
    
    # 检查环境变量
    print("\n1. 检查配置...")
    
    # 检查.env文件
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if not os.path.exists(env_file):
        print("❌ 未找到.env文件，正在创建模板...")
        env_content = '''# Apify API Configuration
APIFY_API_TOKEN=your_apify_api_token_here

# Facebook Group Configuration
FACEBOOK_GROUP_URL=https://www.facebook.com/groups/2091834914421201/
FACEBOOK_GROUP_ID=2091834914421201

# Project Configuration
PROJECT_NAME=Smart Home Facebook Scraper
DATA_PATH=./facebook/data/'''
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print(f"✅ 已创建.env文件模板: {env_file}")
        print("⚠️  请编辑.env文件，添加你的APIFY_API_TOKEN")
        print("   你可以在Apify控制台的Account -> Settings -> API tokens中找到token")
        print()
        return
    
    print("✅ 找到.env配置文件")
    
    # 检查依赖
    try:
        import requests
        import pandas as pd
        from dotenv import load_dotenv
        print("✅ 依赖包检查完成")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r facebook/requirements.txt")
        return
    
    # 加载环境变量
    load_dotenv(env_file)
    api_token = os.getenv('APIFY_API_TOKEN', '')
    
    if not api_token or api_token == 'your_apify_api_token_here':
        print("❌ 请在.env文件中配置APIFY_API_TOKEN")
        return
    
    print("✅ API Token配置正确")
    
    # 导入项目模块
    try:
        from utils.apify_client import ApifyClient
        from utils.data_processor import DataProcessor
        from scripts.export_data import export_to_excel, export_summary_report
    except ImportError as e:
        print(f"❌ 导入项目模块失败: {e}")
        return
    
    print("\n2. 开始数据处理...")
    
    # 根据你提供的Run ID下载数据
    run_id = "GE9UnXsKVRMkLulNJ"  # 从截图中看到的你的运行ID
    
    print(f"📥 下载数据 (Run ID: {run_id})...")
    
    try:
        client = ApifyClient()
        
        # 下载数据
        filepath = client.save_run_data(run_id)
        print(f"✅ 数据下载完成: {filepath}")
        
        # 处理数据
        print("\n📊 处理数据...")
        processor = DataProcessor()
        data = processor.load_data(filepath)
        df = processor.process_posts(data)
        
        if df.empty:
            print("❌ 没有可处理的数据")
            return
        
        # 显示统计信息
        stats = processor.get_summary_stats(df)
        print(f"\n📈 数据统计:")
        print(f"  📝 总帖子数: {stats['total_posts']}")
        print(f"  👥 用户数: {stats['unique_users']}")
        print(f"  📅 时间范围: {stats['date_range']['start']} 到 {stats['date_range']['end']}")
        print(f"  👍 总点赞数: {stats['engagement_stats']['total_likes']}")
        print(f"  💬 总评论数: {stats['engagement_stats']['total_comments']}")
        print(f"  🔄 总分享数: {stats['engagement_stats']['total_shares']}")
        print(f"  🏆 平均互动分数: {stats['engagement_stats']['avg_engagement']:.2f}")
        
        # 保存处理后的数据
        print(f"\n💾 保存处理后的数据...")
        processed_filepath = processor.save_processed_data(df, format='json')
        
        # 导出报告
        print(f"\n📋 导出报告...")
        excel_filepath = export_to_excel(df)
        summary_filepath = export_summary_report(df)
        
        print(f"\n🎉 完成！文件已保存到:")
        print(f"  📄 原始数据: {filepath}")
        print(f"  🔄 处理数据: {processed_filepath}")
        print(f"  📊 Excel报告: {excel_filepath}")
        print(f"  📋 摘要报告: {summary_filepath}")
        
        print(f"\n📚 下次使用指令:")
        print(f"  下载最新数据: python scripts/download_data.py --latest")
        print(f"  处理数据: python scripts/process_data.py --latest")
        print(f"  导出报告: python scripts/export_data.py --latest")
        
    except Exception as e:
        print(f"❌ 处理过程中出错: {str(e)}")
        print(f"请检查:")
        print(f"  1. API Token是否正确")
        print(f"  2. 网络连接是否正常")
        print(f"  3. Apify服务是否可用")

if __name__ == "__main__":
    main() 