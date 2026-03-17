# -*- coding: utf-8 -*-
"""重新格式化 processed_chunks 目录下的文件"""
import os
import re

print("="*60)
print("📋 重新格式化 processed_chunks 文件")
print("="*60)

# 定义景区名称映射
SCENIC_NAME_MAP = {
    "管鲍祠": "管鲍祠",
    "小张庄公园": "小张庄公园",
    "明清苑": "明清苑",
    "颍上八里河景区": "八里河景区",
    "颍上尤家花园": "尤家花园",
    "颍上江心洲公园": "江心洲公园",
    "颍上湿地公园": "湿地公园",
    "颍上管仲老街": "管仲老街",
    "颍上迪沟生态园": "迪沟生态园"
}

def extract_scenic_name(filename):
    """从文件名中提取景区名称"""
    # 移除文件扩展名
    name = os.path.splitext(filename)[0]
    # 查找映射
    for key, value in SCENIC_NAME_MAP.items():
        if key in name:
            return value
    return name

def reformat_content(content, scenic_name):
    """重新格式化文件内容"""
    # 构建新内容
    new_content = []
    new_content.append(f"【📍 景区】{scenic_name}")
    new_content.append("【📌 简介】")
    new_content.append(content)
    return '\n\n'.join(new_content)

def main():
    """主函数"""
    chunks_dir = "processed_chunks"
    
    # 检查目录是否存在
    if not os.path.exists(chunks_dir):
        print(f"❌ 目录 {chunks_dir} 不存在！")
        return
    
    # 获取目录下的所有文件
    files = [f for f in os.listdir(chunks_dir) if f.endswith('.txt')]
    
    if not files:
        print("❌ 目录中没有 .txt 文件！")
        return
    
    print(f"✅ 找到 {len(files)} 个文件")
    
    # 处理每个文件
    for filename in files:
        # 跳过 chunk_0.txt，因为它可能是预览文件
        if filename == "chunk_0.txt":
            print(f"⏭️  跳过 {filename}")
            continue
        
        filepath = os.path.join(chunks_dir, filename)
        
        # 读取文件内容
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except Exception as e:
            print(f"❌ 读取 {filename} 失败: {str(e)}")
            continue
        
        # 提取景区名称
        scenic_name = extract_scenic_name(filename)
        
        # 重新格式化内容
        new_content = reformat_content(content, scenic_name)
        
        # 新文件名
        new_filename = f"processed_chunk.{scenic_name}.txt"
        new_filepath = os.path.join(chunks_dir, new_filename)
        
        # 保存新文件
        try:
            with open(new_filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ 处理完成: {filename} → {new_filename}")
        except Exception as e:
            print(f"❌ 保存 {new_filename} 失败: {str(e)}")
            continue
        
        # 删除旧文件
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"⚠️  删除旧文件 {filename} 失败: {str(e)}")
    
    print("\n✨ 所有文件处理完成！")
    print("📁 新文件格式: processed_chunk.景区.txt")
    print("📝 新内容格式: 【📍 景区】景区名称\n【📌 简介】内容")

if __name__ == "__main__":
    main()
