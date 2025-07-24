import random
import logging
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

logger = logging.getLogger(__name__)


class ForumSpiderMiddleware:
    """Spider中间件"""
    
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RotateUserAgentMiddleware:
    """User-Agent轮换中间件"""
    
    def __init__(self):
        self.user_agent_list = [
            # Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/120.0',
            
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        ]

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = ua
        return None


class ProxyMiddleware:
    """代理中间件（可选使用）"""
    
    def __init__(self):
        # 代理列表（需要自己添加有效代理）
        self.proxy_list = [
            # 'http://proxy1:port',
            # 'http://proxy2:port',
            # 添加更多代理...
        ]
        self.proxy_index = 0

    def process_request(self, request, spider):
        if self.proxy_list:
            proxy = self.proxy_list[self.proxy_index]
            self.proxy_index = (self.proxy_index + 1) % len(self.proxy_list)
            request.meta['proxy'] = proxy
            logger.info(f'Using proxy: {proxy}')
        return None


class CustomRetryMiddleware(RetryMiddleware):
    """自定义重试中间件"""
    
    def __init__(self, settings):
        super().__init__(settings)
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
            
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
            
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) and not request.meta.get('dont_retry', False):
            return self._retry(request, exception, spider)

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1
        
        if retries <= self.max_retry_times:
            logger.warning(f"Retrying {request.url} (failed {retries} times): {reason}")
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            
            # 增加重试延迟
            if retries > 1:
                delay = min(2 ** retries, 60)  # 指数退避，最大60秒
                retryreq.meta['download_delay'] = delay
                
            return retryreq
        else:
            logger.error(f"Gave up retrying {request.url} (failed {retries} times): {reason}")


class ResponseValidationMiddleware:
    """响应验证中间件"""
    
    def process_response(self, request, response, spider):
        # 检查响应是否有效
        if response.status == 200:
            # 检查是否被反爬虫拦截
            if '访问被拒绝' in response.text or '验证码' in response.text or len(response.text) < 100:
                logger.warning(f"Possible anti-spider detected for {request.url}")
                # 可以选择重试或跳过
                request.meta['retry_times'] = request.meta.get('retry_times', 0) + 1
                return request
                
        return response 