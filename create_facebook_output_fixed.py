#!/usr/bin/env python3
"""
修正版：自动下载并创建Facebook讨论组目录结构
正确处理实际的数据结构
"""

import os
import json
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

def main():
    """主函数"""
    
    print("🚀 Facebook Smart Home 数据处理 (修正版)")
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
    
    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📂 输出目录: {output_dir}")
    print(f"📝 处理 {len(data)} 个帖子...")
    
    created_folders = []
    
    for i, post in enumerate(data, 1):
        try:
            # 正确提取帖子信息 - 修正字段名
            post_text = post.get('text', '')  # 修正：使用 'text' 而不是 'post_text'
            user_info = post.get('user', {})
            user_name = user_info.get('name', 'Unknown User') if user_info else 'Unknown User'  # 修正：从user对象中获取name
            post_time = post.get('time', '')  # 修正：使用 'time' 而不是 'post_time'
            post_url = post.get('url', '')  # 修正：使用 'url'
            
            # 互动数据 - 根据实际数据结构调整
            likes_count = post.get('likes_count', 0) or post.get('topReactionsCount', 0)
            comments_count = post.get('comments_count', 0) or post.get('commentsCount', 0)
            shares_count = post.get('shares_count', 0) or post.get('sharesCount', 0)
            attachments = post.get('attachments', [])
            
            # 生成文件夹名
            post_title = extract_post_title(post_text)
            folder_name = f"{i:02d}_{post_title}"
            post_folder = os.path.join(output_dir, folder_name)
            
            # 创建帖子文件夹
            os.makedirs(post_folder, exist_ok=True)
            
            # 1. 帖子基本信息
            info_content = f"""📋 帖子信息
{'='*50}

👤 作者: {user_name}
🕐 发布时间: {post_time}
🔗 帖子链接: {post_url}

📊 互动数据:
  👍 点赞: {likes_count}
  💬 评论: {comments_count}
  🔄 分享: {shares_count}

📎 附件数量: {len(attachments)}

🆔 帖子ID: {post.get('id', '未知')}
🏷️ Legacy ID: {post.get('legacyId', '未知')}
"""
            
            with open(os.path.join(post_folder, 'post_info.txt'), 'w', encoding='utf-8') as f:
                f.write(info_content)
            
            # 2. 帖子主要内容
            content_header = f"""💬 帖子内容
{'='*50}

作者: {user_name}
时间: {post_time}

{'='*50}

"""
            
            content_body = post_text if post_text else "[ 此帖子没有文字内容 ]"
            
            content_footer = f"""

{'='*50}
📊 {likes_count} 个赞 · {comments_count} 条评论 · {shares_count} 次分享
"""
            
            full_content = content_header + content_body + content_footer
            
            with open(os.path.join(post_folder, 'post_content.txt'), 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            # 3. 附件信息 - 更好的格式化
            if attachments:
                attachments_content = f"""📎 附件信息
{'='*50}

共有 {len(attachments)} 个附件:

"""
                for j, attachment in enumerate(attachments, 1):
                    if isinstance(attachment, dict):
                        if 'image' in attachment and 'uri' in attachment['image']:
                            # 图片附件
                            attachments_content += f"{j}. 📷 图片:\n"
                            attachments_content += f"   🔗 链接: {attachment['image']['uri']}\n"
                            if 'width' in attachment['image'] and 'height' in attachment['image']:
                                attachments_content += f"   📐 尺寸: {attachment['image']['width']}x{attachment['image']['height']}\n"
                            if 'ocrText' in attachment:
                                attachments_content += f"   🔤 OCR文字: {attachment['ocrText']}\n"
                        elif 'url' in attachment:
                            # 其他链接附件
                            attachments_content += f"{j}. 🔗 链接: {attachment['url']}\n"
                        else:
                            # 原始数据
                            attachments_content += f"{j}. 📄 附件数据: {attachment}\n"
                    else:
                        attachments_content += f"{j}. {attachment}\n"
                    attachments_content += "\n"
                
                with open(os.path.join(post_folder, 'attachments.txt'), 'w', encoding='utf-8') as f:
                    f.write(attachments_content)
            
            # 4. 原始数据备份
            with open(os.path.join(post_folder, 'raw_data.json'), 'w', encoding='utf-8') as f:
                json.dump(post, f, ensure_ascii=False, indent=2)
            
            created_folders.append(folder_name)
            print(f"  ✅ {i:02d}. {folder_name}")
            
        except Exception as e:
            print(f"  ❌ 处理第 {i} 个帖子时出错: {str(e)}")
            continue
    
    # 创建索引文件
    create_index_file(output_dir, created_folders, data)
    
    print(f"\n🎉 完成！")
    print(f"📁 输出目录: {output_dir}")
    print(f"📂 创建了 {len(created_folders)} 个帖子文件夹")
    print(f"📄 每个文件夹包含:")
    print(f"   - post_info.txt (帖子基本信息)")
    print(f"   - post_content.txt (帖子主要内容)")
    print(f"   - attachments.txt (附件信息，如果有)")
    print(f"   - raw_data.json (完整原始数据)")
    print(f"📋 生成了索引文件: index.txt")
    
    # 显示目录内容
    print(f"\n📋 生成的内容预览:")
    for folder in created_folders[:5]:  # 显示前5个
        print(f"  📁 {folder}/")
    if len(created_folders) > 5:
        print(f"  ... 还有 {len(created_folders) - 5} 个帖子文件夹")

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
        
        preview = post.get('text', '')[:50]
        if len(post.get('text', '')) > 50:
            preview += "..."
        
        index_content += f"""{i:02d}. 📁 {folder}/
    👤 作者: {user_name}
    🕐 时间: {post_time}
    👍 {likes} 赞 💬 {comments} 评论
    📝 预览: {preview}
    
"""
    
    index_content += f"""
{'='*60}

🔍 使用说明:
1. 每个数字开头的文件夹代表一个帖子
2. 进入文件夹查看该帖子的详细内容
3. post_content.txt 包含帖子的主要内容
4. post_info.txt 包含帖子的基本信息和互动数据
5. attachments.txt 包含附件信息（如果有）

💡 提示: 文件夹按帖子顺序编号，方便浏览

🌟 推荐阅读顺序：
   查看 index.txt → 选择感兴趣的帖子 → 进入文件夹 → 阅读 post_content.txt
"""
    
    with open(os.path.join(output_dir, 'index.txt'), 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    # 创建README
    readme_content = f"""# Smart Home Facebook 群组讨论

这个目录包含从 Facebook Smart Home 群组爬取的讨论内容。

## 🗂️ 目录结构

每个帖子都有独立的文件夹，包含以下文件：
- `post_info.txt` - 📋 帖子基本信息（作者、时间、互动数据）
- `post_content.txt` - 💬 帖子主要内容  
- `attachments.txt` - 📎 附件信息（如果有）
- `raw_data.json` - 🗃️ 完整原始数据

## 🔍 使用方法

1. 查看 `index.txt` 了解所有帖子的概览
2. 进入感兴趣的帖子文件夹
3. 阅读相应的 txt 文件了解详细内容

## 📊 统计信息

- 总帖子数: {len(folders)}
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 数据来源: Facebook Smart Home 群组
- 群组链接: https://www.facebook.com/groups/2091834914421201/

## 🎯 快速导航

推荐从 `index.txt` 开始浏览，它包含所有帖子的预览信息。
"""
    
    with open(os.path.join(output_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

if __name__ == "__main__":
    main() 