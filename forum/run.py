#!/usr/bin/env python3
"""
论坛爬虫运行脚本
Usage: python run.py [options]
"""

import os
import sys
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='运行论坛数据爬虫')
    parser.add_argument('--url', type=str, 
                       help='爬取单个帖子URL（如果提供，将只爬取这个帖子）')
    parser.add_argument('--pages', type=int, default=1, 
                       help='要爬取的页数 (默认: 1, 仅在非单URL模式下有效)')
    parser.add_argument('--posts', type=int, default=10,
                       help='每页最大帖子数 (默认: 10)')
    parser.add_argument('--replies', type=int, default=20,
                       help='每个帖子最大回复数 (默认: 20)')
    parser.add_argument('--output', type=str, default='output',
                       help='输出目录 (默认: output)')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='请求延迟秒数 (默认: 2.0)')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    parser.add_argument('--no-cache', action='store_true',
                       help='禁用HTTP缓存')
    
    args = parser.parse_args()
    
    # 获取项目设置
    settings = get_project_settings()
    
    # 应用命令行参数
    settings.set('CUSTOM_SETTINGS', {
        **settings.get('CUSTOM_SETTINGS', {}),
        'MAX_PAGES': args.pages,
        'MAX_POSTS_PER_PAGE': args.posts,
        'MAX_REPLIES_PER_POST': args.replies,
        'OUTPUT_DIR': args.output,
    })
    
    settings.set('DOWNLOAD_DELAY', args.delay)
    
    if args.debug:
        settings.set('LOG_LEVEL', 'DEBUG')
        
    if args.no_cache:
        settings.set('HTTPCACHE_ENABLED', False)
    
    # 创建输出目录
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        print(f"创建输出目录: {args.output}")
    
    # 根据模式显示不同的配置信息
    if args.url:
        print(f"""
开始运行论坛爬虫（单帖模式）...
配置参数:
- 目标帖子: {args.url}
- 每帖回复数: {args.replies}
- 输出目录: {args.output}
- 输出格式: TXT文件 (论坛目录结构)
- 请求延迟: {args.delay}秒
- 调试模式: {'开启' if args.debug else '关闭'}
- HTTP缓存: {'禁用' if args.no_cache else '启用'}
        """)
    else:
        print(f"""
开始运行论坛爬虫（板块模式）...
配置参数:
- 爬取页数: {args.pages}
- 每页帖子数: {args.posts}
- 每帖回复数: {args.replies}
- 输出目录: {args.output}
- 输出格式: TXT文件 (论坛目录结构)
- 请求延迟: {args.delay}秒
- 调试模式: {'开启' if args.debug else '关闭'}
- HTTP缓存: {'禁用' if args.no_cache else '启用'}
        """)
    
    # 启动爬虫，传递URL参数
    process = CrawlerProcess(settings)
    spider_kwargs = {}
    if args.url:
        spider_kwargs['url'] = args.url
        
    process.crawl('hassbian', **spider_kwargs)
    process.start()


if __name__ == '__main__':
    main() 