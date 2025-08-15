import scrapy
from urllib.parse import urljoin
from itemloaders import ItemLoader
from discourse_spider.items import LatestTopicItem


class LatestTopicsSpider(scrapy.Spider):
	name = 'latest_topics'
	allowed_domains = ['community.home-assistant.io']
	custom_settings = {
		'FORUM_NAME': 'Home Assistant Community'
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.base = 'https://community.home-assistant.io'
		self.limit = int(kwargs.get('limit', 200))
		self.collected = 0

	def start_requests(self):
		url = urljoin(self.base, '/latest.json')
		yield scrapy.Request(url=url, callback=self.parse_page, meta={'page': 0})

	def parse_page(self, response):
		data = response.json()
		topic_list = data.get('topic_list', {})
		topics = topic_list.get('topics', []) or []
		for t in topics:
			if self.collected >= self.limit:
				return
			post_id = t.get('id')
			slug = t.get('slug')
			title = t.get('title')
			posts_count = t.get('posts_count')
			views = t.get('views')
			category_id = t.get('category_id')
			created_at = t.get('created_at')
			last_posted_at = t.get('last_posted_at')
			post_url = urljoin(self.base, f"/t/{slug}/{post_id}")

			ldr = ItemLoader(item=LatestTopicItem())
			ldr.add_value('post_id', str(post_id))
			ldr.add_value('title', title)
			ldr.add_value('post_url', post_url)
			ldr.add_value('reply_count', max(0, int(posts_count) - 1) if posts_count else 0)
			ldr.add_value('view_count', views or 0)
			ldr.add_value('category_id', category_id)
			ldr.add_value('created_at', created_at)
			ldr.add_value('last_posted_at', last_posted_at)
			yield ldr.load_item()
			self.collected += 1

		if self.collected < self.limit:
			next_page = response.meta['page'] + 1
			next_url = urljoin(self.base, f"/latest.json?page={next_page}")
			yield scrapy.Request(url=next_url, callback=self.parse_page, meta={'page': next_page})
