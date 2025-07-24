# Facebook Smart Home 群组数据爬取项目

这个项目用于从Facebook Smart Home群组爬取和分析数据，使用Apify平台进行数据采集。

## 项目结构

```
/facebook/
├── config/
│   └── settings.py          # 项目配置
├── data/
│   ├── raw/                 # 原始数据存储
│   ├── processed/           # 处理后的数据
│   └── exports/             # 导出的报告
├── scripts/
│   ├── download_data.py     # 数据下载脚本
│   ├── process_data.py      # 数据处理脚本
│   └── export_data.py       # 数据导出脚本
├── utils/
│   ├── apify_client.py      # Apify API客户端
│   └── data_processor.py    # 数据处理工具
├── requirements.txt         # 项目依赖
└── README.md               # 项目说明
```

## 安装和配置

### 1. 安装依赖

```bash
cd facebook
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件，添加你的Apify API token:

```env
APIFY_API_TOKEN=your_apify_api_token_here
FACEBOOK_GROUP_URL=https://www.facebook.com/groups/2091834914421201/
FACEBOOK_GROUP_ID=2091834914421201
```

## 使用方法

### 1. 下载数据

从Apify下载爬取的数据到本地：

```bash
# 下载指定运行ID的数据
python scripts/download_data.py --run-id GE9UnXsKVRMkLulNJ

# 下载最新成功运行的数据
python scripts/download_data.py --latest

# 列出最近的运行记录
python scripts/download_data.py --list
```

### 2. 处理数据

处理下载的原始数据，提取有用信息：

```bash
# 处理最新的原始数据文件
python scripts/process_data.py --latest

# 处理指定文件
python scripts/process_data.py --file data/raw/facebook_posts_xxx.json

# 指定输出格式
python scripts/process_data.py --latest --format csv

# 分析数据趋势
python scripts/process_data.py --analyze data/raw/facebook_posts_xxx.json

# 列出原始数据文件
python scripts/process_data.py --list
```

### 3. 导出报告

将处理后的数据导出为报告格式：

```bash
# 导出最新处理的数据为Excel报告
python scripts/export_data.py --latest --format excel

# 导出摘要报告
python scripts/export_data.py --latest --format summary

# 导出完整报告 (Excel + 摘要)
python scripts/export_data.py --latest --format both

# 指定输出文件名
python scripts/export_data.py --latest --output my_report

# 列出可导出的文件
python scripts/export_data.py --list
```

## 数据结构

### 原始数据字段
- `post_id`: 帖子ID
- `group_url`: 群组URL
- `post_url`: 帖子URL
- `post_text`: 帖子内容
- `user_name`: 用户名
- `user_url`: 用户链接
- `post_time`: 发布时间
- `likes_count`: 点赞数
- `comments_count`: 评论数
- `shares_count`: 分享数
- `attachments`: 附件信息

### 处理后的数据字段
在原始数据基础上添加：
- `hashtags`: 提取的话题标签
- `mentions`: 提取的@提及
- `text_length`: 文本长度
- `has_image`: 是否包含图片
- `engagement_score`: 互动分数

## 数据分析功能

### 统计分析
- 总帖子数和用户数
- 时间范围分析
- 互动数据统计（点赞、评论、分享）
- 内容特征分析

### 趋势分析
- 每日发帖趋势
- 用户活跃度排名
- 热门话题标签
- 高互动内容识别

### 导出格式
- **Excel报告**: 包含多个工作表的详细数据
- **摘要报告**: JSON格式的关键指标摘要
- **CSV格式**: 便于进一步分析的数据表

## 目标群组信息

- **群组名称**: Smart Home (推测)
- **群组ID**: 2091834914421201
- **群组URL**: https://www.facebook.com/groups/2091834914421201/
- **类型**: 公开群组
- **主题**: 智能家居相关讨论

## 注意事项

1. **API限制**: 请遵守Apify的API使用限制
2. **数据隐私**: 确保遵守Facebook的数据使用政策
3. **存储空间**: 定期清理不需要的原始数据文件
4. **更新频率**: 建议定期运行爬虫获取最新数据

## 故障排除

### 常见问题

1. **API Token错误**
   - 检查 `.env` 文件中的 `APIFY_API_TOKEN` 是否正确
   - 验证token是否有效且未过期

2. **没有数据**
   - 确认Apify上的爬虫运行成功
   - 检查运行ID是否正确

3. **处理失败**
   - 检查原始数据文件格式是否正确
   - 确认所有依赖包已安装

## 扩展功能

可以考虑添加的功能：
- 情感分析
- 关键词提取
- 用户网络分析
- 定时自动爬取
- 数据可视化图表
- 邮件报告推送

## 支持

如有问题，请检查：
1. 环境变量配置
2. 依赖包安装
3. Apify服务状态
4. 网络连接 