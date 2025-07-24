# 论坛数据爬虫

基于Scrapy框架的论坛数据爬取工具，用于爬取HassBian论坛的帖子和回复数据。

## 功能特点

- 🚀 **高效爬取**: 基于Scrapy的异步爬虫框架
- 🛡️ **反爬虫策略**: 包含User-Agent轮换、请求延迟、重试机制
- 📊 **数据结构化**: 自动提取帖子标题、作者、内容、回复等信息
- 💾 **多格式输出**: 支持JSON、CSV格式输出
- 📈 **统计信息**: 提供爬取统计和性能监控
- 🎛️ **灵活配置**: 可自定义爬取页数、回复数等参数

## 项目结构

```
forum/
├── scrapy.cfg                 # Scrapy配置文件
├── requirements.txt           # 依赖包列表
├── run.py                    # 运行脚本
├── README.md                 # 项目说明
└── forum_spider/             # 主项目目录
    ├── __init__.py
    ├── items.py              # 数据模型定义
    ├── middlewares.py        # 中间件
    ├── pipelines.py          # 数据处理管道
    ├── settings.py           # 项目设置
    └── spiders/              # 爬虫目录
        ├── __init__.py
        └── hassbian_spider.py # 主爬虫
```

## 安装使用

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行爬虫

#### 方式一：使用便捷脚本（推荐）

```bash
# 使用默认设置运行
python run.py

# 自定义参数运行
python run.py --pages 3 --replies 15 --delay 1.5

# 启用调试模式
python run.py --debug

# 查看所有可用参数
python run.py --help
```

#### 方式二：使用Scrapy命令

```bash
# 基本运行
scrapy crawl hassbian

# 自定义输出
scrapy crawl hassbian -s FEED_URI=custom_output.json

# 设置日志级别
scrapy crawl hassbian -L INFO
```

## 配置参数

可以在 `forum_spider/settings.py` 中修改以下关键参数：

```python
CUSTOM_SETTINGS = {
    'MAX_PAGES': 5,                    # 最大爬取页数
    'MAX_REPLIES_PER_POST': 20,        # 每个帖子最大回复数
    'OUTPUT_DIR': 'output',            # 输出目录
}

DOWNLOAD_DELAY = 2                     # 请求延迟（秒）
CONCURRENT_REQUESTS = 8                # 并发请求数
AUTOTHROTTLE_ENABLED = True            # 自动限速
```

## 输出文件

爬虫运行后会在 `output/` 目录下生成以下文件：

- `posts.json` - 帖子数据（JSON格式）
- `replies.json` - 回复数据（JSON格式）
- `posts.csv` - 帖子数据（CSV格式）
- `replies.csv` - 回复数据（CSV格式）
- `statistics.json` - 爬取统计信息
- `scrapy.log` - 运行日志

## 数据字段说明

### 帖子数据 (PostItem)
- `post_id`: 帖子ID
- `title`: 帖子标题
- `author`: 作者
- `post_time`: 发帖时间
- `post_url`: 帖子链接
- `view_count`: 浏览数
- `reply_count`: 回复数
- `content`: 帖子内容
- `page_num`: 来源页码
- `crawl_time`: 爬取时间

### 回复数据 (ReplyItem)
- `post_id`: 所属帖子ID
- `reply_id`: 回复ID
- `floor_num`: 楼层号
- `author`: 回复者
- `reply_time`: 回复时间
- `content`: 回复内容
- `crawl_time`: 爬取时间

## 反爬虫特性

项目内置了多种反爬虫机制：

1. **User-Agent轮换**: 随机使用不同浏览器的User-Agent
2. **请求延迟**: 可配置的请求间隔时间
3. **自动限速**: 根据服务器响应动态调整请求频率
4. **重试机制**: 自动重试失败的请求
5. **响应验证**: 检测和处理反爬虫页面

## 注意事项

1. **遵守robots.txt**: 虽然项目中设置了 `ROBOTSTXT_OBEY = False`，但建议在实际使用时考虑网站的robots.txt规则

2. **合理使用**: 
   - 不要设置过高的并发数
   - 保持合理的请求延迟
   - 避免对服务器造成过大压力

3. **法律合规**: 
   - 仅用于学习和研究目的
   - 遵守相关法律法规
   - 尊重网站服务条款

4. **数据处理**: 
   - 爬取的数据可能包含HTML标签，已在Pipeline中进行清理
   - 建议对爬取的数据进行进一步的验证和清洗

## 故障排除

### 常见问题

1. **无法获取数据**
   - 检查网络连接
   - 确认目标网站是否可访问
   - 查看日志文件中的错误信息

2. **爬取速度过慢**
   - 适当减少 `DOWNLOAD_DELAY` 值
   - 增加 `CONCURRENT_REQUESTS` 值
   - 关闭HTTP缓存 (`--no-cache`)

3. **被反爬虫拦截**
   - 增加请求延迟
   - 添加代理服务器
   - 检查User-Agent设置

### 调试技巧

```bash
# 启用详细日志
python run.py --debug

# 使用Scrapy shell调试
scrapy shell "https://bbs.hassbian.com/forum-38-1.html"

# 检查特定选择器
response.css('tbody[id^="normalthread_"] th.new a::attr(href)').getall()
```

## 扩展功能

可以根据需要扩展以下功能：

1. **数据库存储**: 在Pipeline中添加数据库写入功能
2. **邮件通知**: 爬取完成后发送邮件通知
3. **定时任务**: 结合crontab实现定时爬取
4. **数据分析**: 添加数据统计和分析功能
5. **Web界面**: 开发Web管理界面

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和网站服务条款。 