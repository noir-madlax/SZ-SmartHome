import scrapy
import re
from urllib.parse import urljoin, urlparse, parse_qs
from forum_spider.items import PostItem, ReplyItem
from itemloaders import ItemLoader
import logging

logger = logging.getLogger(__name__)


class HassbianSpider(scrapy.Spider):
    name = 'hassbian'
    allowed_domains = ['bbs.hassbian.com']
    
    def __init__(self, *args, **kwargs):
        super(HassbianSpider, self).__init__(*args, **kwargs)
        
        # 从命令行参数获取单个帖子URL
        self.single_url = kwargs.get('url', None)
        
        # 设置默认值，这些将在from_crawler中被覆盖
        self.max_pages = 1
        self.max_posts_per_page = 10
        self.max_replies = 20
        self.base_url = 'https://bbs.hassbian.com'
        self.list_url_template = 'https://bbs.hassbian.com/forum-38-{}.html'
        
        # 初始化已存在帖子ID集合（将在Pipeline中设置）
        self.existing_post_ids = set()
        self.found_posts_count = 0  # 跟踪找到的新帖子数量
        
        logger.info(f"Spider initialized with single_url: {self.single_url}")

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """从crawler创建spider实例"""
        spider = super(HassbianSpider, cls).from_crawler(crawler, *args, **kwargs)
        
        # 从设置中获取配置
        custom_settings = crawler.settings.get('CUSTOM_SETTINGS', {})
        spider.max_pages = custom_settings.get('MAX_PAGES', 1)
        spider.max_posts_per_page = custom_settings.get('MAX_POSTS_PER_PAGE', 10)
        spider.max_replies = custom_settings.get('MAX_REPLIES_PER_POST', 20)
        spider.base_url = custom_settings.get('FORUM_BASE_URL', 'https://bbs.hassbian.com')
        spider.list_url_template = custom_settings.get('FORUM_LIST_URL', 'https://bbs.hassbian.com/forum-38-{}.html')
        
        logger.info(f"Spider configured: max_pages={spider.max_pages}, max_posts_per_page={spider.max_posts_per_page}, max_replies={spider.max_replies}")
        if spider.single_url:
            logger.info(f"Single URL mode: {spider.single_url}")
            
        return spider

    def start_requests(self):
        """生成初始请求"""
        # 如果提供了单个URL，只爬取这个帖子
        if self.single_url:
            yield scrapy.Request(
                url=self.single_url,
                callback=self.parse_post_detail,
                meta={'page_num': 1},
                dont_filter=False
            )
        else:
            # 默认模式：从第1页开始爬取论坛列表页
            url = self.list_url_template.format(1)
            yield scrapy.Request(
                url=url,
                callback=self.parse_forum_list,
                meta={'page_num': 1},
                dont_filter=False
            )

    def parse_forum_list(self, response):
        """解析论坛列表页"""
        page_num = response.meta['page_num']
        logger.info(f"Parsing forum list page {page_num}: {response.url}")
        logger.info(f"Current found posts: {self.found_posts_count}, target: {self.max_posts_per_page}")
        
        # 如果已经找到足够的帖子，停止处理
        if self.found_posts_count >= self.max_posts_per_page:
            logger.info(f"Already found {self.found_posts_count} posts, stopping")
            return
        
        # 提取帖子链接，使用更精确的选择器
        post_links = []
        
        # 尝试多种选择器来获取帖子链接，从严格到宽松
        selectors = [
            'tbody[id^="normalthread_"] th.new a[href*="thread-"]::attr(href)',
            'tbody[id^="normalthread_"] th.common a[href*="thread-"]::attr(href)',
            'th.new a[href*="thread-"]::attr(href)',
            'th.common a[href*="thread-"]::attr(href)',
            'tbody[id^="normalthread_"] a[href*="thread-"]::attr(href)',
            'a[href*="thread-"][href*=".html"]::attr(href)'
        ]
        
        for selector in selectors:
            post_links = response.css(selector).getall()
            if post_links:
                logger.info(f"Using selector: {selector}")
                break
        
        # 提取帖子ID并过滤，优先选择第一页的帖子
        new_posts = []
        seen_posts = set()
        
        for link in post_links:
            if not link or 'thread-' not in link:
                continue
            
            # 优先选择主题帖（-1-1.html结尾）
            is_main_thread = link.endswith('-1-1.html')
            
            # 提取帖子ID
            post_id = self.extract_post_id(urljoin(self.base_url, link))
            if not post_id:
                continue
                
            # 跳过已存在的帖子
            if post_id in self.existing_post_ids:
                logger.info(f"Skipping existing post: {post_id}")
                continue
                
            # 跳过重复的帖子（优先保留主题帖）
            if post_id in seen_posts:
                # 如果当前是主题帖，替换之前的
                if is_main_thread:
                    # 移除之前的版本
                    new_posts = [(pid, plink) for pid, plink in new_posts if pid != post_id]
                    new_posts.append((post_id, link))
                continue
                
            seen_posts.add(post_id)
            new_posts.append((post_id, link))
            
            # 如果找到足够的新帖子，停止
            if len(new_posts) >= (self.max_posts_per_page - self.found_posts_count):
                break
        
        # 按链接类型排序，主题帖优先
        new_posts.sort(key=lambda x: (not x[1].endswith('-1-1.html'), x[0]))
        
        logger.info(f"Found {len(new_posts)} new posts on page {page_num} (skipped {len(self.existing_post_ids)} existing)")
        
        # 处理新帖子
        for i, (post_id, link) in enumerate(new_posts, 1):
            full_url = urljoin(self.base_url, link)
            logger.info(f"Processing new post {self.found_posts_count + i}/{self.max_posts_per_page}: {post_id} - {full_url}")
            
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_post_detail,
                meta={'page_num': page_num, 'post_index': self.found_posts_count + i, 'post_id': post_id},
                dont_filter=False
            )
        
        # 更新计数
        self.found_posts_count += len(new_posts)
        
        # 如果还需要更多帖子并且当前页有帖子，继续下一页
        if self.found_posts_count < self.max_posts_per_page and len(post_links) > 0 and page_num < 10:
            next_page = page_num + 1
            next_url = self.list_url_template.format(next_page)
            logger.info(f"Need more posts ({self.found_posts_count}/{self.max_posts_per_page}), going to page {next_page}")
            
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_forum_list,
                meta={'page_num': next_page},
                dont_filter=False
            )
        else:
            logger.info(f"Finished collecting posts: {self.found_posts_count}/{self.max_posts_per_page}")

    def parse_post_detail(self, response):
        """解析帖子详情页"""
        logger.info(f"Parsing post detail: {response.url}")
        
        # 提取帖子ID
        post_id = self.extract_post_id(response.url)
        if not post_id:
            logger.warning(f"Could not extract post ID from URL: {response.url}")
            return
        
        # 提取帖子基本信息
        post_item = self.extract_post_info(response, post_id)
        if post_item:
            post_item['page_num'] = response.meta['page_num']
            yield post_item
        
        # 提取回复信息（前20楼）
        replies = self.extract_replies(response, post_id)
        for reply in replies[:self.max_replies]:
            yield reply
        
        # 如果有下一页回复，继续爬取
        next_page_links = response.css('a.nxt::attr(href)').getall()
        if next_page_links and len(replies) >= self.max_replies:
            next_url = urljoin(self.base_url, next_page_links[0])
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_post_replies,
                meta={
                    'post_id': post_id,
                    'current_replies': len(replies),
                    'page_num': response.meta['page_num']
                }
            )

    def parse_post_replies(self, response):
        """解析帖子回复页（第2页及以后）"""
        post_id = response.meta['post_id']
        current_replies = response.meta['current_replies']
        
        logger.info(f"Parsing replies page for post {post_id}: {response.url}")
        
        replies = self.extract_replies(response, post_id, start_floor=current_replies + 1)
        
        for reply in replies:
            if current_replies < self.max_replies:
                yield reply
                current_replies += 1
            else:
                break

    def extract_post_id(self, url):
        """从URL中提取帖子ID"""
        # 匹配 thread-数字-数字-数字.html 格式 
        match = re.search(r'thread-(\d+)-\d+-\d+\.html', url)
        if match:
            return match.group(1)
        # 如果上面不匹配，尝试简单的thread-数字格式
        match = re.search(r'thread-(\d+)', url)
        if match:
            return match.group(1)
        return None

    def extract_post_info(self, response, post_id):
        """提取帖子信息"""
        try:
            loader = ItemLoader(item=PostItem(), response=response)
            
            # 基本信息
            loader.add_value('post_id', post_id)
            loader.add_value('post_url', response.url)
            
            # 标题 - 尝试多种选择器
            title_selectors = [
                '#thread_subject::text',
                'h1::text',
                '.maintitle::text',
                'span[id^="thread_subject"]::text',
                '.threadtitle a::text'
            ]
            
            title = None
            for selector in title_selectors:
                title = response.css(selector).get()
                if title:
                    break
            
            if title:
                loader.add_value('title', title.strip())
            else:
                # 从URL中提取标题作为后备
                logger.warning(f"Could not extract title for post {post_id}")
                loader.add_value('title', f'未知标题_{post_id}')
            
            # 作者信息 - 尝试多种选择器
            author_selectors = [
                '.authi a::text',
                '.postauthor a::text',
                '[id^="postauthor"] a::text',
                '.username a::text',
                'td.postauthor .username::text'
            ]
            
            author = None
            for selector in author_selectors:
                author = response.css(selector).get()
                if author:
                    break
            
            if author:
                loader.add_value('author', author.strip())
            
            # 发帖时间 - 尝试多种选择器和格式
            time_selectors = [
                '.authi em::text',
                '.postinfo em::text',
                'em[id^="authorposton"]::text',
                '.postdate::text'
            ]
            
            post_time = None
            for selector in time_selectors:
                post_time = response.css(selector).get()
                if post_time:
                    break
            
            # 如果没找到，尝试从页面文本中提取
            if not post_time:
                post_time = response.css('.postinfo::text').re_first(r'发表于\s*([^|]+)')
            
            if post_time:
                loader.add_value('post_time', post_time.strip())
            
            # 帖子内容 - 尝试多种选择器
            content_selectors = [
                '[id^="postmessage_"]:first-child',  # 第一个帖子内容
                '.postcontent .postmessage:first-child',
                '.t_msgfont:first-child',
                '.postbody .postmessage:first-child',
                '[id^="post_"] .postmessage:first-child',
                'td[id^="postmessage_"]:first-child'
            ]
            
            content = None
            for selector in content_selectors:
                content_elems = response.css(selector)
                if content_elems:
                    # 获取第一个元素的所有文本内容
                    content_texts = content_elems[0].css('::text').getall()
                    if content_texts:
                        content = ' '.join([text.strip() for text in content_texts if text.strip()])
                        break
            
            # 如果还是没有内容，尝试更宽泛的选择器
            if not content or len(content.strip()) < 10:
                broader_selectors = [
                    '[id^="postmessage_"]',
                    '.postmessage',
                    '.t_msgfont'
                ]
                
                for selector in broader_selectors:
                    content_elems = response.css(selector)
                    if content_elems:
                        # 获取第一个有实际内容的元素
                        for elem in content_elems:
                            text_content = ' '.join(elem.css('::text').getall()).strip()
                            if text_content and len(text_content) > 10:
                                content = text_content
                                break
                        if content:
                            break
            
            if content and content.strip():
                loader.add_value('content', content.strip())
            else:
                loader.add_value('content', '暂无内容')
                logger.warning(f"Could not extract content for post {post_id}")
            
            # 统计信息 - 尝试多种格式
            stats_text = ' '.join(response.css('.postinfo::text').getall())
            
            # 查看数
            view_patterns = [r'查看[：:]\s*(\d+)', r'浏览[：:]\s*(\d+)', r'(\d+)\s*次查看']
            view_count = None
            for pattern in view_patterns:
                view_match = re.search(pattern, stats_text)
                if view_match:
                    view_count = view_match.group(1)
                    break
            
            if view_count:
                loader.add_value('view_count', int(view_count))
            
            # 回复数
            reply_patterns = [r'回复[：:]\s*(\d+)', r'(\d+)\s*个回复', r'回帖\s*(\d+)']
            reply_count = None
            for pattern in reply_patterns:
                reply_match = re.search(pattern, stats_text)
                if reply_match:
                    reply_count = reply_match.group(1)
                    break
            
            if reply_count:
                loader.add_value('reply_count', int(reply_count))
            
            return loader.load_item()
            
        except Exception as e:
            logger.error(f"Error extracting post info for {post_id}: {e}")
            return None

    def extract_replies(self, response, post_id, start_floor=1):
        """提取回复信息"""
        replies = []
        
        # 查找回复元素
        reply_selectors = [
            '[id^="post_"]',
            '.postinfo',
            'table[id^="pid"]'
        ]
        
        reply_elements = []
        for selector in reply_selectors:
            reply_elements = response.css(selector)
            if reply_elements:
                break
        
        if not reply_elements:
            logger.warning(f"No reply elements found for post {post_id}")
            return replies
        
        floor_num = start_floor
        
        for elem in reply_elements:
            try:
                # 跳过楼主的帖子（通常是第一个元素）
                if floor_num == 1 and start_floor == 1:
                    floor_num += 1
                    continue
                
                loader = ItemLoader(item=ReplyItem(), selector=elem)
                
                loader.add_value('post_id', post_id)
                loader.add_value('floor_num', floor_num)
                
                # 回复者
                author = elem.css('.postauthor a::text').get() or \
                        elem.css('.authi a::text').get() or \
                        elem.css('[id^="postauthor"] a::text').get()
                if author:
                    loader.add_value('author', author.strip())
                
                # 回复时间
                reply_time = elem.css('.authi em::text').get() or \
                           elem.css('.postinfo::text').re_first(r'(\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2})')
                if reply_time:
                    loader.add_value('reply_time', reply_time.strip())
                
                # 回复内容
                content_selectors = [
                    '.postcontent .postmessage',
                    '.t_msgfont', 
                    '[id^="postmessage_"]',
                    '.postbody .postmessage'
                ]
                
                content = None
                for selector in content_selectors:
                    content_elem = elem.css(selector)
                    if content_elem:
                        content = ' '.join(content_elem.css('::text').getall())
                        break
                
                if content and content.strip():
                    loader.add_value('content', content)
                    
                    # 提取回复ID
                    reply_id = elem.css('::attr(id)').get()
                    if reply_id:
                        loader.add_value('reply_id', reply_id)
                    
                    reply_item = loader.load_item()
                    replies.append(reply_item)
                    
                floor_num += 1
                if len(replies) >= self.max_replies:
                    break
                    
            except Exception as e:
                logger.error(f"Error extracting reply {floor_num}: {e}")
                continue
        
        logger.info(f"Extracted {len(replies)} replies for post {post_id}")
        return replies

    def parse(self, response):
        """默认解析方法（如果直接访问帖子URL）"""
        if 'forum-' in response.url:
            return self.parse_forum_list(response)
        elif 'thread-' in response.url:
            return self.parse_post_detail(response)
        else:
            logger.warning(f"Unknown URL format: {response.url}") 