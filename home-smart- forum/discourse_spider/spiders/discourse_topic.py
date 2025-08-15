import scrapy
import re
from urllib.parse import urljoin, urlparse
from itemloaders import ItemLoader
from discourse_spider.items import TopicItem, ReplyItem


class DiscourseTopicSpider(scrapy.Spider):
	name = 'discourse_topic'
	allowed_domains = ['community.home-assistant.io']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.single_url = kwargs.get('url')
		self.max_replies = 100
		self.forum_name = 'Home Assistant Community'

	@classmethod
	def from_crawler(cls, crawler, *args, **kwargs):
		spider = super().from_crawler(crawler, *args, **kwargs)
		custom = crawler.settings.get('CUSTOM_SETTINGS', {})
		spider.max_replies = int(custom.get('MAX_REPLIES_PER_POST', 100))
		spider.forum_name = custom.get('FORUM_NAME', 'Home Assistant Community')
		return spider

	@staticmethod
	def _normalize_topic_base(url: str) -> str:
		# Ensure URL like https://domain/t/slug/id (strip trailing page or post number segment)
		m = re.search(r'(https?://[^/]+/t/[^/]+/\d+)', url)
		return m.group(1) if m else url

	def start_requests(self):
		if not self.single_url:
			self.logger.error('No --url provided for Discourse spider')
			return
		base = self._normalize_topic_base(self.single_url)
		first_json = base + '.json'
		yield scrapy.Request(url=first_json, callback=self.parse_topic_json, meta={'base': base, 'page': 0, 'emitted_first': False, 'replies_count': 0})

	def parse_topic_json(self, response):
		base = response.meta['base']
		page = response.meta['page']
		emitted_first = response.meta.get('emitted_first', False)
		replies_count = response.meta.get('replies_count', 0)

		data = response.json()
		# Basic topic info
		slug = data.get('slug')
		topic_id = data.get('id')
		title = data.get('title')
		post_stream = data.get('post_stream', {})
		posts = post_stream.get('posts', []) or []

		for post in posts:
			post_number = post.get('post_number')
			author = post.get('username') or (post.get('name') or '')
			created_at = post.get('created_at')
			# content is in 'cooked' (HTML); we can keep text-only by stripping tags later in pipeline; store raw text now
			cooked = post.get('cooked') or ''
			plain = ' '.join(re.sub(r'<[^>]+>', ' ', cooked).split())

			if post_number == 1 and not emitted_first:
				loader = ItemLoader(item=TopicItem())
				loader.add_value('post_id', str(topic_id))
				loader.add_value('post_url', base)
				if title:
					loader.add_value('title', title)
				if author:
					loader.add_value('author', author)
				if created_at:
					loader.add_value('post_time', created_at)
				loader.add_value('content', plain if plain else 'No content')
				yield loader.load_item()
				emitted_first = True
				continue

			if post_number and post_number != 1:
				ldr = ItemLoader(item=ReplyItem(), selector=None)
				ldr.add_value('post_id', str(topic_id))
				ldr.add_value('floor_num', int(post_number))
				if author:
					ldr.add_value('author', author)
				if created_at:
					ldr.add_value('reply_time', created_at)
				ldr.add_value('content', plain if plain else 'No content')
				reply_id = post.get('id')
				if reply_id:
					ldr.add_value('reply_id', f'post_{reply_id}')
				yield ldr.load_item()
				replies_count += 1
				if replies_count >= self.max_replies:
					return

		# Next page
		next_page = page + 1
		next_url = f"{base}.json?page={next_page}"
		# Heuristic: if this page returned zero new posts (or only first page already emitted and empty), stop
		if posts:
			yield scrapy.Request(url=next_url, callback=self.parse_topic_json, meta={'base': base, 'page': next_page, 'emitted_first': emitted_first, 'replies_count': replies_count})
