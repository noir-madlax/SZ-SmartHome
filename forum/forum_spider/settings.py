# Scrapy settings for forum_spider project

BOT_NAME = 'forum_spider'

SPIDER_MODULES = ['forum_spider.spiders']
NEWSPIDER_MODULE = 'forum_spider.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# 并发设置
CONCURRENT_REQUESTS = 8  # 减少并发请求数，避免给服务器造成压力
CONCURRENT_REQUESTS_PER_DOMAIN = 2  # 每个域名并发数
CONCURRENT_REQUESTS_PER_IP = 1

# 下载延迟设置 (单位：秒)
DOWNLOAD_DELAY = 2  # 2秒延迟，模拟人类行为
RANDOMIZE_DOWNLOAD_DELAY = 0.5  # 随机延迟 (0.5 * to 1.5 * DOWNLOAD_DELAY)

# AutoThrottle 自动调节
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = True  # 启用调试信息

# User-Agent 设置
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# 请求头设置
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 中间件设置
SPIDER_MIDDLEWARES = {
    'forum_spider.middlewares.ForumSpiderMiddleware': 543,
}

DOWNLOADER_MIDDLEWARES = {
    'forum_spider.middlewares.RotateUserAgentMiddleware': 400,  # 轮换User-Agent
    'forum_spider.middlewares.ProxyMiddleware': 410,  # 代理中间件（可选）
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,  # 禁用默认UA中间件
}

# Pipeline 设置
ITEM_PIPELINES = {
    'forum_spider.pipelines.ValidationPipeline': 300,  # 数据验证
    'forum_spider.pipelines.DuplicatesPipeline': 350,  # 去重处理
    'forum_spider.pipelines.TxtWriterPipeline': 400,   # TXT输出（主要）
    'forum_spider.pipelines.JsonWriterPipeline': 450,  # JSON输出（备份）
    # 'forum_spider.pipelines.CsvWriterPipeline': 500, # CSV输出（禁用）
}

# 缓存设置（开发时建议开启，生产环境可关闭）
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600  # 1小时缓存
HTTPCACHE_DIR = 'httpcache'

# 日志设置
LOG_LEVEL = 'INFO'
LOG_FILE = 'scrapy.log'

# 请求重试设置
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# 下载超时设置
DOWNLOAD_TIMEOUT = 30

# 自定义设置
CUSTOM_SETTINGS = {
    # 论坛爬取专用设置
    'MAX_PAGES': 1,  # 最大爬取页数（1页通常包含10+个帖子）
    'MAX_POSTS_PER_PAGE': 10,  # 每页最大爬取帖子数
    'MAX_REPLIES_PER_POST': 20,  # 每个帖子最大爬取回复数
    'FORUM_BASE_URL': 'https://bbs.hassbian.com',
    'FORUM_LIST_URL': 'https://bbs.hassbian.com/forum-38-{}.html',  # 论坛列表页URL模板
    
    # 输出文件设置
    'OUTPUT_DIR': 'output',
    'JSON_FILE': 'forum_data.json',
    'CSV_FILE': 'forum_data.csv',
}

# Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# 扩展设置
EXTENSIONS = {
    'scrapy.extensions.telnet.TelnetConsole': None,
    'scrapy.extensions.corestats.CoreStats': 300,  # 核心统计
    'scrapy.extensions.memusage.MemoryUsage': 200,  # 内存使用监控
}

# 内存使用限制 (MB)
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_WARNING_MB = 1024

# Feed 导出设置
FEEDS = {
    'output/posts.json': {
        'format': 'json',
        'encoding': 'utf8',
        'indent': 2,
        'item_classes': ['forum_spider.items.PostItem'],
    },
    'output/replies.json': {
        'format': 'json', 
        'encoding': 'utf8',
        'indent': 2,
        'item_classes': ['forum_spider.items.ReplyItem'],
    },
    'output/forum_data.csv': {
        'format': 'csv',
        'encoding': 'utf8',
    }
} 