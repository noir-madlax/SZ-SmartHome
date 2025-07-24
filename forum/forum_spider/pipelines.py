import json
import csv
import os
import logging
from datetime import datetime
from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter
import re

logger = logging.getLogger(__name__)


def clean_filename(filename):
    """清理文件名，移除非法字符"""
    # 移除或替换Windows/Linux文件名中的非法字符
    illegal_chars = ['<', '>', '"', '/', '\\', '|', '?', '*', ':']
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    # 限制长度
    if len(filename) > 100:
        filename = filename[:100]
    return filename.strip()


class TxtWriterPipeline:
    """TXT格式输出Pipeline - 按论坛结构组织，帖子和回复合并到一个文件"""
    
    def __init__(self):
        self.forum_name = "HomeAssistant综合讨论区"
        self.base_output_dir = None
        self.processed_posts = set()  # 跟踪已处理的帖子

    def open_spider(self, spider):
        # 创建基础输出目录结构
        custom_settings = spider.crawler.settings.get('CUSTOM_SETTINGS', {})
        base_dir = custom_settings.get('OUTPUT_DIR', 'output')
        
        self.base_output_dir = os.path.join(base_dir, self.forum_name)
        if not os.path.exists(self.base_output_dir):
            os.makedirs(self.base_output_dir)
            
        # 获取已存在的帖子目录，用于跳过
        existing_dirs = [d for d in os.listdir(self.base_output_dir) 
                        if os.path.isdir(os.path.join(self.base_output_dir, d))]
        
        spider.existing_post_ids = set()
        for dir_name in existing_dirs:
            if '_' in dir_name:
                post_id = dir_name.split('_')[0]
                spider.existing_post_ids.add(post_id)
                logger.info(f"Found existing post directory: {dir_name} (ID: {post_id})")
        
        logger.info(f"TXT output directory initialized: {self.base_output_dir}")
        logger.info(f"Found {len(spider.existing_post_ids)} existing posts to skip")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if item.__class__.__name__ == 'PostItem':
            self._save_post_as_txt(adapter)
        elif item.__class__.__name__ == 'ReplyItem':
            self._append_reply_to_txt(adapter)
            
        return item

    def _save_post_as_txt(self, adapter):
        """保存帖子为TXT文件（初始化文件）"""
        try:
            post_id = adapter.get('post_id', [''])[0] if isinstance(adapter.get('post_id'), list) else adapter.get('post_id', '')
            title = adapter.get('title', '未知标题')
            
            # 检查是否已处理过
            if post_id in self.processed_posts:
                return
            
            # 创建帖子目录
            clean_title = clean_filename(title)
            post_dir_name = f"{post_id}_{clean_title}"
            post_dir = os.path.join(self.base_output_dir, post_dir_name)
            
            if not os.path.exists(post_dir):
                os.makedirs(post_dir)
            
            # 创建合并的内容文件
            content_file = os.path.join(post_dir, "完整内容.txt")
            with open(content_file, 'w', encoding='utf-8') as f:
                # 写入帖子头部信息
                f.write("=" * 60 + "\n")
                f.write(f"帖子标题: {title}\n")
                f.write(f"帖子ID: {post_id}\n")
                f.write(f"作者: {adapter.get('author', '未知')}\n")
                f.write(f"发帖时间: {adapter.get('post_time', '未知')}\n")
                f.write(f"帖子链接: {adapter.get('post_url', '')}\n")
                f.write(f"浏览数: {adapter.get('view_count', 0)}\n")
                f.write(f"回复数: {adapter.get('reply_count', 0)}\n")
                f.write(f"爬取时间: {adapter.get('crawl_time', '')}\n")
                f.write("=" * 60 + "\n\n")
                
                # 写入帖子内容
                f.write("【楼主帖子内容】\n")
                f.write("-" * 30 + "\n")
                content = adapter.get('content', '暂无内容')
                if content and content.strip():
                    f.write(f"{content}\n")
                else:
                    f.write("暂无内容\n")
                f.write("\n" + "=" * 60 + "\n")
                f.write("【回复内容】\n")
                f.write("=" * 60 + "\n")
                
            self.processed_posts.add(post_id)
            logger.info(f"Post initialized: {content_file}")
            
        except Exception as e:
            logger.error(f"Error saving post as TXT: {e}")

    def _append_reply_to_txt(self, adapter):
        """追加回复到TXT文件"""
        try:
            post_id = adapter.get('post_id', [''])[0] if isinstance(adapter.get('post_id'), list) else adapter.get('post_id', '')
            
            # 找到对应的帖子目录
            post_dirs = [d for d in os.listdir(self.base_output_dir) 
                        if os.path.isdir(os.path.join(self.base_output_dir, d)) and d.startswith(f"{post_id}_")]
            
            if not post_dirs:
                logger.warning(f"No post directory found for post_id: {post_id}")
                return
                
            post_dir = os.path.join(self.base_output_dir, post_dirs[0])
            content_file = os.path.join(post_dir, "完整内容.txt")
            
            # 追加回复内容
            with open(content_file, 'a', encoding='utf-8') as f:
                f.write(f"\n【{adapter.get('floor_num', 0)}楼】 - {adapter.get('author', '未知用户')}\n")
                f.write(f"回复时间: {adapter.get('reply_time', '未知')}\n")
                f.write("-" * 40 + "\n")
                f.write(f"{adapter.get('content', '暂无内容')}\n")
                f.write("-" * 40 + "\n")
                
            logger.info(f"Reply appended to: {content_file} (Floor: {adapter.get('floor_num')})")
            
        except Exception as e:
            logger.error(f"Error appending reply to TXT: {e}")

    def close_spider(self, spider):
        logger.info(f"TXT files saved in forum structure under: {self.base_output_dir}")
        logger.info(f"Total posts processed in this session: {len(self.processed_posts)}")


class ValidationPipeline:
    """数据验证Pipeline"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # 验证必填字段
        if item.__class__.__name__ == 'PostItem':
            required_fields = ['title', 'author', 'post_url']
        elif item.__class__.__name__ == 'ReplyItem':
            required_fields = ['post_id', 'author', 'content']
        else:
            required_fields = []
            
        for field in required_fields:
            if not adapter.get(field):
                raise DropItem(f"Missing required field: {field} in {item}")
        
        # 添加爬取时间
        adapter['crawl_time'] = datetime.now().isoformat()
        
        logger.info(f"Item validated: {item.__class__.__name__}")
        return item


class DuplicatesPipeline:
    """去重Pipeline"""
    
    def __init__(self):
        self.seen_posts = set()
        self.seen_replies = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if item.__class__.__name__ == 'PostItem':
            post_id = adapter.get('post_id')
            post_id_str = post_id[0] if isinstance(post_id, list) else post_id
            if post_id_str in self.seen_posts:
                raise DropItem(f"Duplicate post found: {post_id_str}")
            else:
                self.seen_posts.add(post_id_str)
                
        elif item.__class__.__name__ == 'ReplyItem':
            post_id = adapter.get('post_id')
            post_id_str = post_id[0] if isinstance(post_id, list) else post_id
            reply_key = f"{post_id_str}_{adapter.get('floor_num')}"
            if reply_key in self.seen_replies:
                raise DropItem(f"Duplicate reply found: {reply_key}")
            else:
                self.seen_replies.add(reply_key)
        
        return item


class JsonWriterPipeline:
    """JSON输出Pipeline"""
    
    def __init__(self):
        self.posts_file = None
        self.replies_file = None
        self.posts_data = []
        self.replies_data = []

    def open_spider(self, spider):
        # 创建输出目录
        output_dir = spider.settings.get('CUSTOM_SETTINGS', {}).get('OUTPUT_DIR', 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 初始化文件
        self.posts_file = open(f'{output_dir}/posts.json', 'w', encoding='utf-8')
        self.replies_file = open(f'{output_dir}/replies.json', 'w', encoding='utf-8')
        
        logger.info("JSON files initialized")

    def close_spider(self, spider):
        # 写入数据
        if self.posts_data:
            json.dump(self.posts_data, self.posts_file, ensure_ascii=False, indent=2)
        if self.replies_data:
            json.dump(self.replies_data, self.replies_file, ensure_ascii=False, indent=2)
            
        # 关闭文件
        self.posts_file.close()
        self.replies_file.close()
        
        logger.info(f"Saved {len(self.posts_data)} posts and {len(self.replies_data)} replies to JSON files")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if item.__class__.__name__ == 'PostItem':
            self.posts_data.append(dict(adapter))
        elif item.__class__.__name__ == 'ReplyItem':
            self.replies_data.append(dict(adapter))
            
        return item


class CsvWriterPipeline:
    """CSV输出Pipeline"""
    
    def __init__(self):
        self.posts_file = None
        self.replies_file = None
        self.posts_writer = None
        self.replies_writer = None
        self.posts_written = False
        self.replies_written = False

    def open_spider(self, spider):
        output_dir = spider.settings.get('CUSTOM_SETTINGS', {}).get('OUTPUT_DIR', 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 打开CSV文件
        self.posts_file = open(f'{output_dir}/posts.csv', 'w', newline='', encoding='utf-8')
        self.replies_file = open(f'{output_dir}/replies.csv', 'w', newline='', encoding='utf-8')
        
        logger.info("CSV files initialized")

    def close_spider(self, spider):
        self.posts_file.close()
        self.replies_file.close()
        logger.info("CSV files closed")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if item.__class__.__name__ == 'PostItem':
            if not self.posts_written:
                self.posts_writer = csv.DictWriter(self.posts_file, fieldnames=adapter.field_names())
                self.posts_writer.writeheader()
                self.posts_written = True
            self.posts_writer.writerow(dict(adapter))
            
        elif item.__class__.__name__ == 'ReplyItem':
            if not self.replies_written:
                self.replies_writer = csv.DictWriter(self.replies_file, fieldnames=adapter.field_names())
                self.replies_writer.writeheader()
                self.replies_written = True
            self.replies_writer.writerow(dict(adapter))
            
        return item


class StatisticsPipeline:
    """统计Pipeline"""
    
    def __init__(self):
        self.posts_count = 0
        self.replies_count = 0
        self.start_time = None

    def open_spider(self, spider):
        self.start_time = datetime.now()
        logger.info("Statistics pipeline started")

    def close_spider(self, spider):
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        stats_info = {
            'total_posts': self.posts_count,
            'total_replies': self.replies_count,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'avg_posts_per_minute': self.posts_count / (duration.total_seconds() / 60) if duration.total_seconds() > 0 else 0,
            'avg_replies_per_minute': self.replies_count / (duration.total_seconds() / 60) if duration.total_seconds() > 0 else 0,
        }
        
        # 保存统计信息
        output_dir = spider.settings.get('CUSTOM_SETTINGS', {}).get('OUTPUT_DIR', 'output')
        with open(f'{output_dir}/statistics.json', 'w', encoding='utf-8') as f:
            json.dump(stats_info, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Crawling completed! Posts: {self.posts_count}, Replies: {self.replies_count}, Duration: {duration}")

    def process_item(self, item, spider):
        if item.__class__.__name__ == 'PostItem':
            self.posts_count += 1
        elif item.__class__.__name__ == 'ReplyItem':
            self.replies_count += 1
            
        return item


class FilterPipeline:
    """内容过滤Pipeline"""
    
    def __init__(self):
        # 可以添加需要过滤的关键词
        self.blocked_keywords = [
            # '广告', '推广', '代理'  # 示例关键词
        ]

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        content = adapter.get('content', '')
        title = adapter.get('title', '')
        
        # 检查是否包含屏蔽关键词
        for keyword in self.blocked_keywords:
            if keyword in content or keyword in title:
                raise DropItem(f"Item contains blocked keyword: {keyword}")
                
        # 过滤空内容
        if not content or len(content.strip()) < 10:
            raise DropItem("Item content too short or empty")
            
        return item 