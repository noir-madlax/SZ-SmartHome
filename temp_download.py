#!/usr/bin/env python3
"""
临时下载脚本
直接下载Apify数据，不依赖.env配置
"""

import os
import json
import requests
from datetime import datetime

def download_apify_data(run_id, api_token):
    """直接下载Apify数据"""
    
    # 创建data/raw目录
    raw_dir = "data/raw"
    os.makedirs(raw_dir, exist_ok=True)
    
    # API配置
    base_url = "https://api.apify.com/v2"
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # 获取运行信息
        print(f"获取运行信息: {run_id}")
        run_url = f"{base_url}/actor-runs/{run_id}"
        response = requests.get(run_url, headers=headers)
        response.raise_for_status()
        run_info = response.json()
        
        print(f"运行状态: {run_info['data']['status']}")
        
        # 下载数据
        print("下载数据...")
        data_url = f"{base_url}/actor-runs/{run_id}/dataset/items"
        response = requests.get(data_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"获取到 {len(data)} 条记录")
        
        # 保存数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"facebook_posts_{run_id}_{timestamp}.json"
        filepath = os.path.join(raw_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filepath}")
        return filepath, data
        
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return None, None

# 主函数
if __name__ == "__main__":
    # 从用户输入获取API token
    print("请输入你的Apify API Token:")
    print("(可以在Apify控制台的Account -> Settings -> API tokens中找到)")
    api_token = input("API Token: ").strip()
    
    if not api_token:
        print("❌ 请提供API Token")
        exit(1)
    
    # 你的运行ID
    run_id = "GE9UnXsKVRMkLulNJ"
    
    filepath, data = download_apify_data(run_id, api_token)
    
    if data:
        print(f"\n✅ 成功下载 {len(data)} 条Facebook帖子数据")
        print(f"文件保存在: {filepath}")
    else:
        print("❌ 下载失败") 