"""
Apify客户端工具类
用于与Apify API交互，下载和管理爬虫数据
"""

import os
import json
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import APIFY_API_TOKEN, RAW_DATA_DIR

class ApifyClient:
    """Apify API客户端"""
    
    def __init__(self, api_token: str = None):
        self.api_token = api_token or APIFY_API_TOKEN
        self.base_url = "https://api.apify.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_run_info(self, run_id: str) -> Dict[str, Any]:
        """获取运行信息"""
        url = f"{self.base_url}/actor-runs/{run_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def download_run_data(self, run_id: str, format: str = 'json') -> List[Dict[str, Any]]:
        """下载运行数据"""
        url = f"{self.base_url}/actor-runs/{run_id}/dataset/items"
        params = {'format': format}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        if format == 'json':
            return response.json()
        else:
            return response.text
    
    def save_run_data(self, run_id: str, filename: str = None) -> str:
        """保存运行数据到本地文件"""
        data = self.download_run_data(run_id)
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"facebook_posts_{run_id}_{timestamp}.json"
        
        filepath = os.path.join(RAW_DATA_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到: {filepath}")
        print(f"共保存 {len(data)} 条记录")
        
        return filepath
    
    def get_actor_runs(self, actor_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取Actor的运行历史"""
        url = f"{self.base_url}/acts/{actor_id}/runs"
        params = {'limit': limit}
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        
        return response.json().get('data', {}).get('items', [])
    
    def get_latest_successful_run(self, actor_id: str) -> Optional[Dict[str, Any]]:
        """获取最新的成功运行"""
        runs = self.get_actor_runs(actor_id)
        
        for run in runs:
            if run.get('status') == 'SUCCEEDED':
                return run
        
        return None 