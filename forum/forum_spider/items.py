import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
import re


def clean_text(text):
    """清理文本，去除多余空白字符"""
    if text:
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 去除多余空白
        text = ' '.join(text.split())
        return text.strip()
    return text


def extract_numbers(text):
    """从文本中提取数字"""
    if text is None:
        return 0
    # 如果已经是数字，直接返回
    if isinstance(text, (int, float)):
        return int(text)
    # 如果是字符串，提取数字
    if isinstance(text, str):
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0
    return 0


class PostItem(scrapy.Item):
    """帖子信息"""
    # 帖子基本信息
    post_id = scrapy.Field()  # 帖子ID
    title = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )  # 帖子标题
    author = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )  # 作者
    post_time = scrapy.Field(
        output_processor=TakeFirst()
    )  # 发帖时间
    post_url = scrapy.Field(
        output_processor=TakeFirst()
    )  # 帖子链接
    
    # 帖子统计信息
    view_count = scrapy.Field(
        input_processor=MapCompose(extract_numbers),
        output_processor=TakeFirst()
    )  # 浏览数
    reply_count = scrapy.Field(
        input_processor=MapCompose(extract_numbers),
        output_processor=TakeFirst()
    )  # 回复数
    
    # 帖子内容
    content = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )  # 帖子内容
    
    # 爬取信息
    page_num = scrapy.Field()  # 来源页码
    crawl_time = scrapy.Field()  # 爬取时间


class ReplyItem(scrapy.Item):
    """回复信息"""
    # 回复基本信息
    post_id = scrapy.Field()  # 所属帖子ID
    reply_id = scrapy.Field()  # 回复ID
    floor_num = scrapy.Field(
        input_processor=MapCompose(extract_numbers),
        output_processor=TakeFirst()
    )  # 楼层号
    
    # 回复者信息
    author = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )  # 回复者
    reply_time = scrapy.Field(
        output_processor=TakeFirst()
    )  # 回复时间
    
    # 回复内容
    content = scrapy.Field(
        input_processor=MapCompose(clean_text),
        output_processor=TakeFirst()
    )  # 回复内容
    
    # 爬取信息
    crawl_time = scrapy.Field()  # 爬取时间 