# -*- coding: utf-8 -*-
"""颍上风景区预处理（零依赖·纯Python版）"""
import os
import glob

print("="*50)
print("🌾 颍上智能问答助手 · 文档预处理")
print("📍 当前目录:", os.getcwd())
print("="*50)

# 景区关键词映射（自动识别）
SCENIC_KEYWORDS = {
    "八里河": "八里河风景区（5A级湿地）",
    "管仲": "管仲老街（明清文化街区）",
    "迪沟": "迪沟生态园（湿地公园）",
    "尤家花园": "尤家花园（江南园林）",
    "小张庄": "小张庄（全国生态典范）",
    "淮罗": "淮罗村（淮河风情）"
}

# 收集所有文本文件（跳过PDF/Word，专注已转换的txt/md）
text_files = glob.glob("*.txt") + glob.glob("*.md")
if not text_files:
    print("❌ 未找到 .txt 或 .md 文件！")
    print("💡 请将PDF/Word用WPS另存为【纯文本(.txt)】或【Markdown(.md)】")
    print("   操作：WPS打开文档 → 另存为 → 选择'文本文档(.txt)' → 保存到本文件夹")
    exit(1)

print(f"\n✅ 找到 {len(text_files)} 个文本文件：")
for f in text_files:
    print(f"   • {f}")

# 处理每个文件
all_chunks = []
for filepath in text_files:
    try:
        # 尝试多种编码（避免乱码）
        for enc in ['utf-8', 'gbk', 'gb2312']:
            try:
                with open(filepath, 'r', encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        else:
            print(f"⚠️  跳过无法解码的文件: {filepath}")
            continue
        
        # 按语义切分（保留完整段落）
        paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 30]
        
        # 为每个段落打标签
        for para in paragraphs:
            # 识别景区
            scenic = "颍上其他景点"
            for kw, name in SCENIC_KEYWORDS.items():
                if kw in filepath or kw in para:
                    scenic = name
                    break
            
            all_chunks.append({
                "content": para,
                "metadata": {
                    "景区": scenic,
                    "来源文件": os.path.basename(filepath),
                    "字符数": len(para)
                }
            })
    except Exception as e:
        print(f"❌ 处理 {filepath} 时出错: {str(e)}")

# 保存结果
os.makedirs("processed_chunks", exist_ok=True)
for i, chunk in enumerate(all_chunks[:10]):  # 保存前10个预览
    with open(f"processed_chunks/chunk_{i}.txt", "w", encoding="utf-8") as f:
        f.write(f"【📍 景区】{chunk['metadata']['景区']}\n")
        f.write(f"【📄 来源】{chunk['metadata']['来源文件']}\n")
        f.write(f"【📏 长度】{chunk['metadata']['字符数']} 字符\n")
        f.write("\n" + "="*40 + "\n\n")
        f.write(chunk["content"])
    
    # 控制台预览
    if i < 3:
        print(f"\n【预览 chunk_{i}】")
        print(f"📍 {chunk['metadata']['景区']} | {chunk['metadata']['来源文件']}")
        print(f"📝 {chunk['content'][:100]}...")

print("\n" + "="*50)
print(f"✨ 预处理成功！共生成 {len(all_chunks)} 个知识片段")
print(f"📁 已保存至: {os.path.abspath('processed_chunks')}")
print("🔍 请立即打开 processed_chunks/chunk_0.txt 检查内容")
print("="*50)
print("\n💡 下一步：")
print("   1. 确认 chunk_0.txt 内容正常（颍上景区介绍文字）")
print("   2. 回复'预处理成功'，我将提供【向量库构建命令】")
print("   3. 3分钟内让颍上知识库'活'起来！")