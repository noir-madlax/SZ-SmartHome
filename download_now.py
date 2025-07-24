#!/usr/bin/env python3
"""
直接下载Apify数据的脚本
"""

import os
import json
import requests
from datetime import datetime

def download_data():
    """下载数据"""
    
    # 你的运行ID
    run_id = "GE9UnXsKVRMkLulNJ"
    
    print("🚀 Facebook Smart Home 数据下载")
    print("=" * 40)
    print(f"📥 Run ID: {run_id}")
    
    # 输入API Token
    print("\n请输入你的Apify API Token:")
    print("(在Apify控制台 Account -> Settings -> API tokens 中获取)")
    api_token = input("Token: ").strip()
    
    if not api_token:
        print("❌ 需要提供API Token")
        return None
    
    # 创建目录
    os.makedirs("data/raw", exist_ok=True)
    
    # API请求
    base_url = "https://api.apify.com/v2"
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"\n📡 连接Apify API...")
        
        # 获取运行数据
        data_url = f"{base_url}/actor-runs/{run_id}/dataset/items"
        response = requests.get(data_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ 成功获取 {len(data)} 条记录")
        
        # 保存数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"facebook_posts_{run_id}_{timestamp}.json"
        filepath = os.path.join("data/raw", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存: {filepath}")
        return filepath
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ API Token无效或已过期")
        elif e.response.status_code == 404:
            print("❌ 运行ID不存在或无权访问")
        else:
            print(f"❌ HTTP错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")
        return None

if __name__ == "__main__":
    download_data() 