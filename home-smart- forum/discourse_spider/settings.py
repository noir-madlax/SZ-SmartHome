BOT_NAME = 'discourse_spider'

SPIDER_MODULES = ['discourse_spider.spiders']
NEWSPIDER_MODULE = 'discourse_spider.spiders'

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_REQUESTS_PER_IP = 1

DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

DEFAULT_REQUEST_HEADERS = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
	'Accept-Encoding': 'gzip, deflate, br',
	'Connection': 'keep-alive',
	'Upgrade-Insecure-Requests': '1',
}

DOWNLOADER_MIDDLEWARES = {
	'discourse_spider.middlewares.RotateUserAgentMiddleware': 400,
	'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

ITEM_PIPELINES = {
	'discourse_spider.pipelines.ValidationPipeline': 300,
	'discourse_spider.pipelines.TxtWriterPipeline': 400,
	'discourse_spider.pipelines.JsonWriterPipeline': 450,
}

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'

LOG_LEVEL = 'INFO'
LOG_FILE = 'scrapy.log'

RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

DOWNLOAD_TIMEOUT = 30

CUSTOM_SETTINGS = {
	'FORUM_NAME': 'Home Assistant Community',
	'OUTPUT_DIR': 'output',
	'MAX_REPLIES_PER_POST': 100,
}

TELNETCONSOLE_ENABLED = False
