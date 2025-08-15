import os
import json
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


def clean_filename(filename: str) -> str:
	for ch in ['<','>','"','/','\\','|','?','*',':']:
		filename = filename.replace(ch, '_')
	return filename.strip()[:120]


class ValidationPipeline:
	def process_item(self, item, spider):
		adapter = ItemAdapter(item)
		cls = item.__class__.__name__
		if cls == 'TopicItem':
			for f in ['title', 'post_url']:
				if not adapter.get(f):
					raise DropItem(f"Missing field {f}")
		elif cls == 'ReplyItem':
			for f in ['post_id', 'content']:
				if not adapter.get(f):
					raise DropItem(f"Missing field {f}")
		elif cls == 'LatestTopicItem':
			for f in ['title', 'post_url']:
				if not adapter.get(f):
					raise DropItem(f"Missing field {f}")
		adapter['crawl_time'] = datetime.now().isoformat()
		return item


class JsonWriterPipeline:
	def __init__(self):
		self.posts = []
		self.replies = []
		self.latest = []
		self.posts_file = None
		self.replies_file = None
		self.latest_file = None

	def open_spider(self, spider):
		out_dir = spider.settings.get('CUSTOM_SETTINGS', {}).get('OUTPUT_DIR', 'output')
		os.makedirs(out_dir, exist_ok=True)
		self.posts_file = open(os.path.join(out_dir, 'posts.json'), 'w', encoding='utf-8')
		self.replies_file = open(os.path.join(out_dir, 'replies.json'), 'w', encoding='utf-8')
		self.latest_file = open(os.path.join(out_dir, 'latest_topics.json'), 'w', encoding='utf-8')

	def close_spider(self, spider):
		json.dump(self.posts, self.posts_file, ensure_ascii=False, indent=2)
		json.dump(self.replies, self.replies_file, ensure_ascii=False, indent=2)
		json.dump(self.latest, self.latest_file, ensure_ascii=False, indent=2)
		self.posts_file.close()
		self.replies_file.close()
		self.latest_file.close()

	def process_item(self, item, spider):
		adapter = ItemAdapter(item)
		cls = item.__class__.__name__
		if cls == 'TopicItem':
			self.posts.append(dict(adapter))
		elif cls == 'ReplyItem':
			self.replies.append(dict(adapter))
		elif cls == 'LatestTopicItem':
			self.latest.append(dict(adapter))
		return item


class TxtWriterPipeline:
	def __init__(self):
		self.base = None
		self.forum_name = None
		self.inited = set()

	def open_spider(self, spider):
		custom = spider.settings.get('CUSTOM_SETTINGS', {})
		self.forum_name = custom.get('FORUM_NAME', 'Home Assistant Community')
		out_dir = custom.get('OUTPUT_DIR', 'output')
		self.base = os.path.join(out_dir, self.forum_name)
		os.makedirs(self.base, exist_ok=True)

	def process_item(self, item, spider):
		adapter = ItemAdapter(item)
		if item.__class__.__name__ == 'TopicItem':
			post_id = adapter.get('post_id') or 'unknown'
			title = clean_filename(adapter.get('title', 'unknown'))
			dir_name = f"{post_id}_{title}"
			post_dir = os.path.join(self.base, dir_name)
			os.makedirs(post_dir, exist_ok=True)
			file_path = os.path.join(post_dir, '完整内容.txt')
			if file_path in self.inited:
				return item
			with open(file_path, 'w', encoding='utf-8') as f:
				f.write("="*60 + "\n")
				f.write(f"帖子标题: {adapter.get('title','')}\n")
				f.write(f"帖子ID: {post_id}\n")
				f.write(f"作者: {adapter.get('author','')}\n")
				f.write(f"发帖时间: {adapter.get('post_time','')}\n")
				f.write(f"帖子链接: {adapter.get('post_url','')}\n")
				f.write(f"浏览数: {adapter.get('view_count',0)}\n")
				f.write(f"回复数: {adapter.get('reply_count',0)}\n")
				f.write(f"爬取时间: {adapter.get('crawl_time','')}\n")
				f.write("="*60 + "\n\n")
				f.write("【楼主帖子内容】\n")
				f.write("-"*30 + "\n")
				f.write(f"{adapter.get('content','暂无内容')}\n")
				f.write("\n" + "="*60 + "\n")
				f.write("【回复内容】\n")
				f.write("="*60 + "\n")
			self.inited.add(file_path)
		elif item.__class__.__name__ == 'ReplyItem':
			post_id = adapter.get('post_id') or 'unknown'
			# find directory by prefix
			for d in os.listdir(self.base):
				if d.startswith(f"{post_id}_"):
					file_path = os.path.join(self.base, d, '完整内容.txt')
					with open(file_path, 'a', encoding='utf-8') as f:
						f.write(f"\n【{adapter.get('floor_num',0)}楼】 - {adapter.get('author','未知用户')}\n")
						f.write(f"回复时间: {adapter.get('reply_time','未知')}\n")
						f.write("-"*40 + "\n")
						f.write(f"{adapter.get('content','暂无内容')}\n")
						f.write("-"*40 + "\n")
					break
		return item
