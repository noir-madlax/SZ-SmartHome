import scrapy
from itemloaders.processors import TakeFirst, MapCompose
import re


def clean_text(text):
	if text is None:
		return text
	text = re.sub(r'<[^>]+>', '', text)
	text = ' '.join(text.split())
	return text.strip()


class TopicItem(scrapy.Item):
	post_id = scrapy.Field()
	title = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
	author = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
	post_time = scrapy.Field(output_processor=TakeFirst())
	post_url = scrapy.Field(output_processor=TakeFirst())
	view_count = scrapy.Field(output_processor=TakeFirst())
	reply_count = scrapy.Field(output_processor=TakeFirst())
	content = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
	crawl_time = scrapy.Field()


class ReplyItem(scrapy.Item):
	post_id = scrapy.Field()
	reply_id = scrapy.Field()
	floor_num = scrapy.Field(output_processor=TakeFirst())
	author = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
	reply_time = scrapy.Field(output_processor=TakeFirst())
	content = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
	crawl_time = scrapy.Field()


class LatestTopicItem(scrapy.Item):
	post_id = scrapy.Field()
	title = scrapy.Field()
	post_url = scrapy.Field()
	reply_count = scrapy.Field()
	view_count = scrapy.Field()
	category_id = scrapy.Field()
	created_at = scrapy.Field()
	last_posted_at = scrapy.Field()
	crawl_time = scrapy.Field()
