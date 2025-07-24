#!/usr/bin/env python3
"""
最终版：自动下载并创建Facebook讨论组目录结构
- 汇总所有帖子到一个txt文件
- 在目录名前标识评论数量
- 输出到facebook/output目录
"""

import os
import json
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

def main():
    """主函数"""
    
    print("🚀 Facebook Smart Home 数据处理 (最终版)")
    print("=" * 50)
    
    # 加载环境变量
    load_dotenv()
    
    # 从环境变量获取API token
    api_token = os.getenv('apify_api') or os.getenv('APIFY_API_TOKEN')
    
    if not api_token:
        print("❌ 未找到API Token")
        print("请在.env文件中配置 apify_api 或 APIFY_API_TOKEN")
        return
    
    print("✅ 已从.env文件读取API配置")
    
    # 你的运行ID
    run_id = "GE9UnXsKVRMkLulNJ"
    print(f"📥 Run ID: {run_id}")
    
    # 下载数据
    print(f"\n📡 正在下载数据...")
    data = download_from_apify(run_id, api_token)
    
    if not data:
        return
    
    print(f"✅ 成功获取 {len(data)} 条帖子数据")
    
    # 创建讨论组结构
    print(f"\n📁 创建讨论组目录结构...")
    create_discussion_folders(data)

def download_from_apify(run_id, api_token):
    """从Apify下载数据"""
    
    base_url = "https://api.apify.com/v2"
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        data_url = f"{base_url}/actor-runs/{run_id}/dataset/items"
        response = requests.get(data_url, headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ API Token无效或已过期")
        elif e.response.status_code == 404:
            print("❌ 运行ID不存在或无权访问")
        else:
            print(f"❌ HTTP错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 下载失败: {str(e)}")
        return None

def sanitize_filename(text, max_length=50):
    """清理文件名"""
    if not text:
        return "untitled_post"
    
    text = re.sub(r'[<>:"/\\|?*]', '_', text)
    text = re.sub(r'\s+', '_', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    
    if len(text) > max_length:
        text = text[:max_length]
    
    return text if text else "untitled_post"

def extract_post_title(post_text, max_length=50):
    """提取帖子标题"""
    if not post_text:
        return "Empty_Post"
    
    text = ' '.join(post_text.split())
    
    if len(text) <= max_length:
        return sanitize_filename(text, max_length)
    
    sentences = re.split(r'[.!?。！？]', text)
    if sentences and len(sentences[0].strip()) > 0:
        first_sentence = sentences[0].strip()
        if len(first_sentence) <= max_length:
            return sanitize_filename(first_sentence, max_length)
    
    return sanitize_filename(text[:max_length], max_length)

def create_discussion_folders(data):
    """创建讨论组风格的文件夹结构"""
    
    # 创建facebook/output目录
    output_dir = "facebook/output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📂 输出目录: {output_dir}")
    print(f"📝 处理 {len(data)} 个帖子...")
    
    created_folders = []
    all_posts_content = []  # 用于汇总所有帖子内容
    
    for i, post in enumerate(data, 1):
        try:
            # 正确提取帖子信息
            post_text = post.get('text', '')
            user_info = post.get('user', {})
            user_name = user_info.get('name', 'Unknown User') if user_info else 'Unknown User'
            post_time = post.get('time', '')
            post_url = post.get('url', '')
            
            # 互动数据 - 根据实际数据结构调整
            likes_count = post.get('likes_count', 0) or post.get('topReactionsCount', 0)
            comments_count = post.get('comments_count', 0) or post.get('commentsCount', 0)
            shares_count = post.get('shares_count', 0) or post.get('sharesCount', 0)
            attachments = post.get('attachments', [])
            
            # 生成文件夹名 - 前面加上评论数量标识
            post_title = extract_post_title(post_text)
            folder_name = f"[{comments_count}评论]{i:02d}_{post_title}"
            post_folder = os.path.join(output_dir, folder_name)
            
            # 创建帖子文件夹
            os.makedirs(post_folder, exist_ok=True)
            
            # 准备帖子内容用于汇总文件
            post_summary = f"""
{'='*80}
📝 帖子 #{i:02d} - {comments_count} 条评论
{'='*80}

👤 作者: {user_name}
🕐 发布时间: {post_time}
🔗 帖子链接: {post_url}
📊 互动数据: 👍 {likes_count} 赞 · 💬 {comments_count} 评论 · 🔄 {shares_count} 分享
📎 附件数量: {len(attachments)}

💬 帖子内容:
{'-'*50}
{post_text if post_text else "[ 此帖子没有文字内容 ]"}
{'-'*50}

🆔 帖子ID: {post.get('id', '未知')}
🏷️ Legacy ID: {post.get('legacyId', '未知')}

"""
            
            # 如果有附件，添加附件信息
            if attachments:
                post_summary += "📎 附件信息:\n"
                for j, attachment in enumerate(attachments, 1):
                    if isinstance(attachment, dict):
                        if 'image' in attachment and 'uri' in attachment['image']:
                            post_summary += f"  {j}. 📷 图片: {attachment['image']['uri']}\n"
                            if 'width' in attachment['image'] and 'height' in attachment['image']:
                                post_summary += f"     📐 尺寸: {attachment['image']['width']}x{attachment['image']['height']}\n"
                            if 'ocrText' in attachment:
                                post_summary += f"     🔤 OCR文字: {attachment['ocrText'][:100]}...\n"
                        elif 'url' in attachment:
                            post_summary += f"  {j}. 🔗 链接: {attachment['url']}\n"
                post_summary += "\n"
            
            all_posts_content.append(post_summary)
            
            # 原始数据备份到各个文件夹
            with open(os.path.join(post_folder, 'raw_data.json'), 'w', encoding='utf-8') as f:
                json.dump(post, f, ensure_ascii=False, indent=2)
            
            created_folders.append(folder_name)
            print(f"  ✅ {i:02d}. {folder_name}")
            
        except Exception as e:
            print(f"  ❌ 处理第 {i} 个帖子时出错: {str(e)}")
            continue
    
    # 创建汇总的txt文件
    create_unified_posts_file(output_dir, all_posts_content, data)
    
    # 创建索引文件
    create_index_file(output_dir, created_folders, data)
    
    print(f"\n🎉 完成！")
    print(f"📁 输出目录: {output_dir}")
    print(f"📂 创建了 {len(created_folders)} 个帖子文件夹")
    print(f"📄 每个文件夹包含:")
    print(f"   - raw_data.json (完整原始数据)")
    print(f"📋 生成了汇总文件:")
    print(f"   - all_posts.txt (所有帖子内容汇总)")
    print(f"   - index.txt (帖子索引)")
    
    # 显示目录内容
    print(f"\n📋 生成的内容预览:")
    for folder in created_folders[:5]:  # 显示前5个
        print(f"  📁 {folder}/")
    if len(created_folders) > 5:
        print(f"  ... 还有 {len(created_folders) - 5} 个帖子文件夹")

def create_unified_posts_file(output_dir, all_posts_content, data):
    """创建汇总的帖子文件"""
    
    unified_content = f"""📚 Smart Home Facebook 群组 - 所有帖子汇总
{'='*90}

📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 总帖子数: {len(data)}
🔗 群组链接: https://www.facebook.com/groups/2091834914421201/

{'='*90}

📖 阅读说明:
- 每个帖子用分隔线分开
- 帖子按编号顺序排列
- 包含完整的帖子内容、作者信息、互动数据
- 附件信息（如有）会显示在帖子内容后

{'='*90}

"""
    
    # 添加所有帖子内容
    unified_content += "\n".join(all_posts_content)
    
    # 添加结尾统计
    total_likes = sum(post.get('topReactionsCount', 0) for post in data)
    total_comments = sum(post.get('commentsCount', 0) for post in data)
    total_shares = sum(post.get('sharesCount', 0) for post in data)
    
    unified_content += f"""
{'='*90}
📊 群组统计汇总
{'='*90}

📝 总帖子数: {len(data)}
👥 参与用户: {len(set(post.get('user', {}).get('name', 'Unknown') for post in data))} 人
👍 总点赞数: {total_likes}
💬 总评论数: {total_comments}
🔄 总分享数: {total_shares}

🏆 互动最高的帖子:
"""
    
    # 找出评论最多的帖子
    sorted_posts = sorted(enumerate(data, 1), key=lambda x: x[1].get('commentsCount', 0), reverse=True)
    for i, (post_num, post) in enumerate(sorted_posts[:3], 1):
        user_name = post.get('user', {}).get('name', 'Unknown') if post.get('user') else 'Unknown'
        comments = post.get('commentsCount', 0)
        preview = post.get('text', '')[:50]
        if len(post.get('text', '')) > 50:
            preview += "..."
        unified_content += f"  {i}. 帖子#{post_num:02d} - {user_name} ({comments}条评论)\n     {preview}\n"
    
    unified_content += f"\n📅 数据生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n"
    
    # 保存汇总文件
    unified_filepath = os.path.join(output_dir, 'all_posts.txt')
    with open(unified_filepath, 'w', encoding='utf-8') as f:
        f.write(unified_content)
    
    print(f"✅ 汇总文件已创建: {unified_filepath}")

def create_index_file(output_dir, folders, data):
    """创建索引文件"""
    
    index_content = f"""📚 Smart Home Facebook 群组讨论索引
{'='*60}

📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 总帖子数: {len(folders)}
🔗 群组链接: https://www.facebook.com/groups/2091834914421201/

{'='*60}

📂 帖子目录:

"""
    
    for i, (folder, post) in enumerate(zip(folders, data), 1):
        user_info = post.get('user', {})
        user_name = user_info.get('name', 'Unknown') if user_info else 'Unknown'
        post_time = post.get('time', '')
        likes = post.get('topReactionsCount', 0)
        comments = post.get('commentsCount', 0)
        shares = post.get('sharesCount', 0)
        
        preview = post.get('text', '')[:50]
        if len(post.get('text', '')) > 50:
            preview += "..."
        
        index_content += f"""{i:02d}. 📁 {folder}/
    👤 作者: {user_name}
    🕐 时间: {post_time}
    📊 互动: 👍 {likes} 赞 · 💬 {comments} 评论 · 🔄 {shares} 分享
    📝 预览: {preview}
    
"""
    
    index_content += f"""
{'='*60}

📖 文件说明:
1. all_posts.txt - 📄 所有帖子内容的完整汇总文件
2. 每个数字开头的文件夹代表一个帖子，包含原始数据
3. 文件夹名前的 [X评论] 表示该帖子的评论数量
4. 文件夹按帖子顺序编号，方便浏览

💡 推荐阅读方式：
   - 快速浏览：查看此 index.txt 文件
   - 完整阅读：打开 all_posts.txt 文件
   - 详细分析：进入具体帖子文件夹查看 raw_data.json

🌟 最受欢迎的帖子（按评论数排序）:
"""
    
    # 按评论数排序显示前5个
    sorted_posts_with_folders = sorted(
        zip(folders, data), 
        key=lambda x: x[1].get('commentsCount', 0), 
        reverse=True
    )
    
    for i, (folder, post) in enumerate(sorted_posts_with_folders[:5], 1):
        comments = post.get('commentsCount', 0)
        user_name = post.get('user', {}).get('name', 'Unknown') if post.get('user') else 'Unknown'
        preview = post.get('text', '')[:40]
        if len(post.get('text', '')) > 40:
            preview += "..."
        index_content += f"   {i}. {folder}/ - {user_name}\n      📝 {preview}\n"
    
    with open(os.path.join(output_dir, 'index.txt'), 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    # 创建README
    readme_content = f"""# Smart Home Facebook 群组讨论

这个目录包含从 Facebook Smart Home 群组爬取的讨论内容。

## 📄 主要文件

- **`all_posts.txt`** - 📚 所有帖子内容的完整汇总（推荐首先阅读）
- **`index.txt`** - 📋 帖子索引和导航信息
- **`README.md`** - 📖 本说明文件

## 🗂️ 目录结构

- 每个帖子都有独立的文件夹
- 文件夹名格式：`[X评论]序号_帖子标题`
- 每个帖子文件夹包含：`raw_data.json`（完整原始数据）

## 🔍 使用方法

1. **快速浏览**: 查看 `index.txt` 了解所有帖子概览
2. **完整阅读**: 打开 `all_posts.txt` 连续阅读所有内容
3. **深入分析**: 进入具体帖子文件夹查看原始数据

## 📊 统计信息

- 总帖子数: {len(folders)}
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 数据来源: Facebook Smart Home 群组
- 群组链接: https://www.facebook.com/groups/2091834914421201/

## 🎯 特色功能

- ✅ 所有帖子汇总在一个txt文件中，便于连续阅读
- ✅ 文件夹名显示评论数量，快速识别热门内容
- ✅ 完整保留原始数据，支持进一步分析
- ✅ 智能文件名清理，兼容各种操作系统

## 📈 热门内容

查看 `index.txt` 文件底部的"最受欢迎的帖子"部分，了解评论最多的讨论话题。
"""
    
    with open(os.path.join(output_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

if __name__ == "__main__":
    main() 