#!/usr/bin/env python3
"""
爬虫测试脚本
用于测试爬虫的基本功能和CSS选择器
"""

import requests
from bs4 import BeautifulSoup
import time
import sys


def test_connection():
    """测试网站连接"""
    print("🔍 测试网站连接...")
    
    url = "https://bbs.hassbian.com/forum-38-1.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"✅ 连接成功! 状态码: {response.status_code}")
        print(f"   响应长度: {len(response.text)} 字符")
        return response
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None


def test_selectors(response):
    """测试CSS选择器"""
    print("\n🔍 测试CSS选择器...")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 测试帖子链接选择器
    selectors_to_test = [
        ('tbody[id^="normalthread_"] th.new a', '帖子链接选择器1'),
        ('th.common a[href*="thread-"]', '帖子链接选择器2'), 
        ('a[href*="thread-"]', '帖子链接选择器3（通用）'),
    ]
    
    for selector, desc in selectors_to_test:
        try:
            elements = soup.select(selector)
            hrefs = [elem.get('href') for elem in elements if elem.get('href')]
            print(f"   {desc}: 找到 {len(hrefs)} 个链接")
            if hrefs:
                print(f"      示例: {hrefs[0]}")
        except Exception as e:
            print(f"   {desc}: 错误 - {e}")


def test_post_page():
    """测试帖子详情页"""
    print("\n🔍 测试帖子详情页...")
    
    # 先获取论坛列表页
    list_url = "https://bbs.hassbian.com/forum-38-1.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        list_response = requests.get(list_url, headers=headers, timeout=10)
        soup = BeautifulSoup(list_response.text, 'html.parser')
        
        # 查找第一个帖子链接
        post_links = []
        for selector in ['tbody[id^="normalthread_"] th.new a', 'a[href*="thread-"]']:
            elements = soup.select(selector)
            post_links = [elem.get('href') for elem in elements if elem.get('href') and 'thread-' in elem.get('href')]
            if post_links:
                break
        
        if not post_links:
            print("❌ 未找到帖子链接")
            return
            
        # 获取第一个帖子的详情
        post_url = post_links[0]
        if not post_url.startswith('http'):
            post_url = 'https://bbs.hassbian.com/' + post_url.lstrip('./')
            
        print(f"   测试帖子: {post_url}")
        
        post_response = requests.get(post_url, headers=headers, timeout=10)
        post_soup = BeautifulSoup(post_response.text, 'html.parser')
        
        # 测试帖子信息提取
        title_selectors = ['#thread_subject', 'h1', '.maintitle']
        for selector in title_selectors:
            title_elem = post_soup.select_one(selector)
            if title_elem:
                print(f"✅ 标题选择器 '{selector}': {title_elem.get_text().strip()[:50]}...")
                break
        else:
            print("❌ 未找到标题")
            
        # 测试作者信息
        author_selectors = ['.authi a', '.postauthor a', '[id^="postauthor"] a']
        for selector in author_selectors:
            author_elem = post_soup.select_one(selector)
            if author_elem:
                print(f"✅ 作者选择器 '{selector}': {author_elem.get_text().strip()}")
                break
        else:
            print("❌ 未找到作者")
            
        # 测试内容
        content_selectors = ['.postcontent .postmessage', '.t_msgfont', '[id^="postmessage_"]']
        for selector in content_selectors:
            content_elem = post_soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text().strip()
                print(f"✅ 内容选择器 '{selector}': {content[:100]}...")
                break
        else:
            print("❌ 未找到内容")
            
    except Exception as e:
        print(f"❌ 测试帖子详情页失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("📋 论坛爬虫测试工具")
    print("=" * 60)
    
    # 测试网站连接
    response = test_connection()
    if not response:
        print("\n❌ 网站连接失败，请检查网络或网站状态")
        sys.exit(1)
    
    # 测试选择器
    test_selectors(response)
    
    # 延迟一下，避免请求过快
    print("\n⏳ 等待2秒...")
    time.sleep(2)
    
    # 测试帖子页面
    test_post_page()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成!")
    print("💡 如果所有测试都通过，可以运行以下命令开始爬取:")
    print("   python run.py --pages 2 --replies 10 --debug")
    print("=" * 60)


if __name__ == '__main__':
    main() 