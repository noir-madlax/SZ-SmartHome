#!/usr/bin/env python3
"""
创建讨论组风格的输出
模拟Facebook讨论组的目录结构，每个帖子一个文件夹
"""

import os
import json
import re
from datetime import datetime
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def sanitize_filename(text, max_length=50):
    """清理文件名，移除特殊字符"""
    if not text:
        return "untitled_post"
    
    # 移除或替换特殊字符
    text = re.sub(r'[<>:"/\\|?*]', '_', text)
    text = re.sub(r'\s+', '_', text)  # 空格替换为下划线
    text = re.sub(r'_+', '_', text)   # 多个下划线合并为一个
    text = text.strip('_')
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length]
    
    return text if text else "untitled_post"

def extract_post_title(post_text, max_length=50):
    """从帖子内容中提取标题"""
    if not post_text:
        return "Empty_Post"
    
    # 移除多余的空白字符
    text = ' '.join(post_text.split())
    
    # 如果文本很短，直接使用
    if len(text) <= max_length:
        return sanitize_filename(text, max_length)
    
    # 尝试找到第一个句子
    sentences = re.split(r'[.!?。！？]', text)
    if sentences and len(sentences[0].strip()) > 0:
        first_sentence = sentences[0].strip()
        if len(first_sentence) <= max_length:
            return sanitize_filename(first_sentence, max_length)
    
    # 否则取前50个字符
    return sanitize_filename(text[:max_length], max_length)

def create_discussion_structure(data, output_dir="output"):
    """创建讨论组风格的目录结构"""
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📁 创建输出目录: {output_dir}")
    print(f"📝 处理 {len(data)} 个帖子...")
    
    created_folders = []
    
    for i, post in enumerate(data, 1):
        try:
            # 提取帖子信息
            post_text = post.get('post_text', '')
            user_name = post.get('user_name', 'Unknown User')
            post_time = post.get('post_time', '')
            post_url = post.get('post_url', '')
            likes_count = post.get('likes_count', 0)
            comments_count = post.get('comments_count', 0)
            shares_count = post.get('shares_count', 0)
            attachments = post.get('attachments', [])
            
            # 生成帖子标题作为文件夹名
            post_title = extract_post_title(post_text)
            
            # 确保文件夹名唯一
            folder_name = f"{i:02d}_{post_title}"
            post_folder = os.path.join(output_dir, folder_name)
            
            # 创建帖子文件夹
            os.makedirs(post_folder, exist_ok=True)
            
            # 1. 帖子基本信息 (post_info.txt)
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
"""
            
            with open(os.path.join(post_folder, 'post_info.txt'), 'w', encoding='utf-8') as f:
                f.write(info_content)
            
            # 2. 帖子主要内容 (post_content.txt)
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
            
            # 3. 附件信息 (如果有附件)
            if attachments:
                attachments_content = f"""📎 附件信息
{'='*50}

共有 {len(attachments)} 个附件:

"""
                for j, attachment in enumerate(attachments, 1):
                    attachments_content += f"{j}. {attachment}\n"
                
                with open(os.path.join(post_folder, 'attachments.txt'), 'w', encoding='utf-8') as f:
                    f.write(attachments_content)
            
            # 4. 完整数据 (raw_data.json) - 用于备份
            with open(os.path.join(post_folder, 'raw_data.json'), 'w', encoding='utf-8') as f:
                json.dump(post, f, ensure_ascii=False, indent=2)
            
            created_folders.append(folder_name)
            print(f"  ✅ {i:02d}. {folder_name}")
            
        except Exception as e:
            print(f"  ❌ 处理第 {i} 个帖子时出错: {str(e)}")
            continue
    
    # 5. 创建索引文件
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
        user_name = post.get('user_name', 'Unknown')
        post_time = post.get('post_time', '')
        likes = post.get('likes_count', 0)
        comments = post.get('comments_count', 0)
        
        # 帖子预览（前50个字符）
        preview = post.get('post_text', '')[:50]
        if len(post.get('post_text', '')) > 50:
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
"""
    
    with open(os.path.join(output_dir, 'index.txt'), 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    # 同时创建README文件
    readme_content = f"""# Smart Home Facebook 群组讨论

这个目录包含从 Facebook Smart Home 群组爬取的讨论内容。

## 目录结构

每个帖子都有独立的文件夹，包含以下文件：
- `post_info.txt` - 帖子基本信息（作者、时间、互动数据）
- `post_content.txt` - 帖子主要内容
- `attachments.txt` - 附件信息（如果有）
- `raw_data.json` - 完整原始数据

## 使用方法

1. 查看 `index.txt` 了解所有帖子的概览
2. 进入感兴趣的帖子文件夹
3. 阅读相应的 txt 文件了解详细内容

## 统计信息

- 总帖子数: {len(folders)}
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 数据来源: Facebook Smart Home 群组
"""
    
    with open(os.path.join(output_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='创建讨论组风格的输出目录')  
    parser.add_argument('--file', '-f', required=True, help='JSON数据文件路径')
    parser.add_argument('--output', '-o', default='output', help='输出目录名称')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"❌ 文件不存在: {args.file}")
        return
    
    # 读取数据
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data:
            print("❌ 数据文件为空")
            return
        
        print(f"📖 读取数据: {len(data)} 条记录")
        
        # 创建目录结构
        create_discussion_structure(data, args.output)
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")

if __name__ == "__main__":
    main() 