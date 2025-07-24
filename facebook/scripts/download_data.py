#!/usr/bin/env python3
"""
Facebook群组数据下载脚本
从Apify下载Smart Home群组的爬虫数据
"""

import os
import sys
import argparse
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.apify_client import ApifyClient
from config.settings import FACEBOOK_GROUPS_SCRAPER_ACTOR_ID

def download_run_data(run_id: str):
    """下载指定运行的数据"""
    client = ApifyClient()
    
    try:
        # 获取运行信息
        print(f"获取运行信息: {run_id}")
        run_info = client.get_run_info(run_id)
        print(f"运行状态: {run_info['data']['status']}")
        print(f"开始时间: {run_info['data']['startedAt']}")
        print(f"结束时间: {run_info['data'].get('finishedAt', 'N/A')}")
        
        # 下载数据
        print("\n开始下载数据...")
        filepath = client.save_run_data(run_id)
        
        print(f"\n✅ 数据下载完成!")
        print(f"文件路径: {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")
        return None

def download_latest_data():
    """下载最新的成功运行数据"""
    client = ApifyClient()
    
    try:
        print("查找最新的成功运行...")
        latest_run = client.get_latest_successful_run(FACEBOOK_GROUPS_SCRAPER_ACTOR_ID)
        
        if not latest_run:
            print("❌ 没有找到成功的运行记录")
            return None
        
        run_id = latest_run['id']
        print(f"找到最新运行: {run_id}")
        
        return download_run_data(run_id)
        
    except Exception as e:
        print(f"❌ 获取最新运行失败: {str(e)}")
        return None

def list_recent_runs():
    """列出最近的运行记录"""
    client = ApifyClient()
    
    try:
        print("获取最近的运行记录...")
        runs = client.get_actor_runs(FACEBOOK_GROUPS_SCRAPER_ACTOR_ID, limit=10)
        
        print("\n最近的运行记录:")
        print("-" * 80)
        print(f"{'序号':<4} {'运行ID':<20} {'状态':<12} {'开始时间':<20} {'结果数量':<10}")
        print("-" * 80)
        
        for i, run in enumerate(runs, 1):
            run_id = run['id']
            status = run['status']
            started_at = run['startedAt'][:19] if run['startedAt'] else 'N/A'
            
            # 尝试获取结果数量
            try:
                if status == 'SUCCEEDED':
                    data = client.download_run_data(run_id)
                    item_count = len(data) if isinstance(data, list) else 'N/A'
                else:
                    item_count = 'N/A'
            except:
                item_count = 'N/A'
            
            print(f"{i:<4} {run_id:<20} {status:<12} {started_at:<20} {item_count:<10}")
        
        return runs
        
    except Exception as e:
        print(f"❌ 获取运行记录失败: {str(e)}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Facebook群组数据下载工具')
    parser.add_argument('--run-id', '-r', help='指定要下载的运行ID')
    parser.add_argument('--latest', '-l', action='store_true', help='下载最新的成功运行数据')
    parser.add_argument('--list', '-ls', action='store_true', help='列出最近的运行记录')
    
    args = parser.parse_args()
    
    if args.list:
        list_recent_runs()
    elif args.run_id:
        download_run_data(args.run_id)
    elif args.latest:
        download_latest_data()
    else:
        print("请指定操作选项:")
        print("  --run-id <ID>  下载指定运行的数据")
        print("  --latest       下载最新成功运行的数据")
        print("  --list         列出最近的运行记录")
        print("\n示例:")
        print("  python download_data.py --run-id GE9UnXsKVRMkLulNJ")
        print("  python download_data.py --latest")
        print("  python download_data.py --list")

if __name__ == "__main__":
    main() 