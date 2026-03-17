# -*- coding: utf-8 -*-
"""颍上向量库构建（全景区覆盖版）"""
import os
import re
import glob
import sys

# === 【关键修复】禁用所有遥测+SSL验证（政府内网必备）===
os.environ['CHROMA_TELEMETRY'] = '0'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

print("="*50)
print("🌾 颍上智能问答助手 · 向量库构建（全景区覆盖版）")
print(f"🌐 当前HF镜像源: {os.environ['HF_ENDPOINT']}")
print("="*50)

# === 关键修复：预下载模型到本地缓存 ===
MODEL_PATH = "D:/颍上智能问答助手/bge-small-zh-v1.5"
if not os.path.exists(MODEL_PATH):
    print("\n⚠️  检测到首次运行，正在下载中文嵌入模型（使用清华镜像）...")
    print("   (此过程约3-5分钟，下载后永久缓存)")
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="BAAI/bge-small-zh-v1.5",
            local_dir=MODEL_PATH,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print("✅ 模型下载成功！路径: " + MODEL_PATH)
    except Exception as e:
        print(f"❌ 模型下载失败: {str(e)}")
        print("💡 手动下载方案（推荐）:")
        print("   1. 在有网络的电脑访问: https://hf-mirror.com/BAAI/bge-small-zh-v1.5")
        print("   2. 下载所有文件 → 复制到 D:/颍上智能问答助手/bge-small-zh-v1.5")
        print("   3. 重新运行本脚本")
        sys.exit(1)

# === 读取processed_chunks目录下所有txt文件 ===
chunks = []
txt_files = glob.glob("processed_chunks/*.txt")
print(f"\n🔍 扫描到 {len(txt_files)} 个知识文件：")
for filepath in txt_files:
    print(f"   ✓ {os.path.basename(filepath)}")

# === 加载并过滤知识片段（优化版）===
print("\n📚 正在解析知识内容...")
valid_count = 0
for filepath in txt_files:
    filename = os.path.basename(filepath)
    
    # 读取内容
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️  读取失败 {filename}: {str(e)}")
        continue
    
    # 跳过明显无效内容
    if "langchain==" in content or "unstructured==" in content:
        print(f"   ⚠️ 跳过无效文件: {filename} (含依赖标记)")
        continue
    
    # 提取景区名称（支持两种格式）
    scenic = "颍上景点"
    
    # 格式1：新标准格式【📍 景区】管仲老街
    match = re.search(r"【📍\s*景区】\s*([^\n]+)", content)
    if match:
        scenic = match.group(1).strip()
        # 清理内容：移除标记行
        content = re.sub(r"【📍\s*景区】[^\n]*\n?", "", content, 1)
    # 格式2：旧格式中的景区名
    elif "八里河" in filename or "八里河" in content:
        scenic = "八里河风景区（5A级湿地）"
    elif "老街" in filename or "管仲" in content.lower():
        scenic = "管仲老街"
    elif "迪沟" in filename or "迪沟" in content.lower():
        scenic = "迪沟生态园"
    elif "尤家" in filename or "尤家" in content.lower():
        scenic = "尤家花园"
    elif "五里湖" in filename or "五里湖" in content.lower():
        scenic = "五里湖湿地公园"
    
    # 提取真实内容（移除标记行）
    for marker in ["【📌 简介】", "【🎫 实用信息】", "【💡 小贴士】", "="*40]:
        content = content.replace(marker, "").strip()
    
    # 清理内容：移除多余空行和项目符号
    content = re.sub(r'\no\s*', '\n', content)  # 移除行首"o "
    content = re.sub(r'\n{3,}', '\n\n', content)  # 合并多余空行
    content = content.strip()
    
    # 严格但合理的长度过滤
    clean_text = content.replace("\n", "").replace(" ", "")
    if len(clean_text) < 30:  # 保留短但有效的内容（如开放时间）
        print(f"   ⚠️ 跳过短内容: {filename} (有效字符: {len(clean_text)})")
        continue
    
    # 创建文档对象
    chunks.append({
        "content": content,
        "metadata": {
            "景区": scenic,
            "来源": filename,
            "ID": valid_count
        }
    })
    valid_count += 1
    print(f"   ✅ 有效内容: {filename} → {scenic} ({len(content)}字)")

print(f"\n✅ 有效知识片段: {len(chunks)} 个（覆盖 {len(set([c['metadata']['景区'] for c in chunks]))} 个景区）")

# === 生成向量（使用本地模型）===
print("\n⛏️  正在生成中文向量（使用本地BGE模型）...")
try:
    # 优先使用新模块（消除弃用警告）
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    # 兼容旧环境
    from langchain.vectorstores import Chroma
    from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

# 转换为Document对象
documents = [
    Document(
        page_content=item["content"],
        metadata=item["metadata"]
    ) for item in chunks
]

# 初始化嵌入模型
embeddings = HuggingFaceEmbeddings(
    model_name=MODEL_PATH,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# 保存向量库
print("💾 保存至颍上专属知识库...")
vector_db = Chroma.from_documents(
    documents,
    embeddings,
    persist_directory="./ys_rag_db",
    collection_name="ys_scenic_knowledge"
)
vector_db.persist()

# === 生成知识库报告 ===
print("\n" + "="*50)
print("🌟 颍上向量知识库构建成功！")
print(f"   • 有效知识片段: {len(chunks)} 个")
print(f"   • 覆盖景区数量: {len(set([c['metadata']['景区'] for c in chunks]))} 个")
print(f"   • 模型路径: {MODEL_PATH}")
print(f"   • 存储路径: {os.path.abspath('./ys_rag_db')}")
print("\n📊 景区分布详情:")
for scenic in sorted(set([c['metadata']['景区'] for c in chunks])):
    count = sum(1 for c in chunks if c['metadata']['景区'] == scenic)
    print(f"   • {scenic}: {count} 个片段")
print("="*50)

print("\n💡 下一步：")
print("   1. 运行 `python ask_ys.py` 立即体验全景区问答")
print("   2. 回复'生成二维码'，获取手机扫码对话方案")
print("   3. 补充更多景区资料 → 重新运行本脚本扩容知识库")