# -*- coding: utf-8 -*-
"""重新构建向量数据库（修复版）"""
import os
import re
import glob
import sys

# 禁用遥测和SSL验证
os.environ['CHROMA_TELEMETRY'] = '0'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

print("="*60)
print("🔄 重新构建颍上向量数据库（修复版）")
print("="*60)

# 模型路径
MODEL_PATH = "D:/颍上智能问答助手/bge-small-zh-v1.5"

# 检查模型是否存在
if not os.path.exists(MODEL_PATH):
    print("❌ 模型路径不存在！")
    print(f"请确保模型已下载到: {MODEL_PATH}")
    sys.exit(1)

# 读取processed_chunks目录下所有txt文件
chunks = []
txt_files = glob.glob("processed_chunks/*.txt")
print(f"\n🔍 扫描到 {len(txt_files)} 个知识文件：")
for filepath in txt_files:
    print(f"   ✓ {os.path.basename(filepath)}")

# 加载并处理知识片段
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
    
    # 提取景区名称
    scenic = "颍上景点"
    
    # 从新格式中提取景区名称
    match = re.search(r"【📍\s*景区】\s*([^\n]+)", content)
    if match:
        scenic = match.group(1).strip()
    # 从文件名中提取
    elif "八里河" in filename:
        scenic = "八里河景区"
    elif "管仲老街" in filename:
        scenic = "管仲老街"
    elif "迪沟" in filename:
        scenic = "迪沟生态园"
    elif "尤家花园" in filename:
        scenic = "尤家花园"
    elif "江心洲" in filename:
        scenic = "江心洲公园"
    elif "湿地" in filename:
        scenic = "湿地公园"
    elif "明清苑" in filename:
        scenic = "明清苑"
    elif "管鲍祠" in filename:
        scenic = "管鲍祠"
    elif "小张庄" in filename:
        scenic = "小张庄公园"
    
    # 清理内容
    content = content.replace("【📍 景区】" + scenic, "")
    content = content.replace("【📌 简介】", "")
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = content.strip()
    
    # 过滤短内容
    clean_text = content.replace("\n", "").replace(" ", "")
    if len(clean_text) < 20:
        print(f"   ⚠️ 跳过短内容: {filename}")
        continue
    
    # 添加到chunks
    chunks.append({
        "content": content,
        "metadata": {
            "景区": scenic,
            "来源": filename,
            "ID": valid_count
        }
    })
    valid_count += 1
    print(f"   ✅ 处理完成: {filename} → {scenic}")

print(f"\n✅ 共处理 {len(chunks)} 个有效知识片段")

# 生成向量
print("\n⛏️  正在生成向量...")
try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
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
print("💾 保存向量库...")

# 清空旧的向量库
if os.path.exists("./ys_rag_db"):
    import shutil
    shutil.rmtree("./ys_rag_db")

vector_db = Chroma.from_documents(
    documents,
    embeddings,
    persist_directory="./ys_rag_db",
    collection_name="ys_scenic_knowledge"
)
vector_db.persist()

# 生成报告
print("\n" + "="*60)
print("🌟 向量数据库构建成功！")
print(f"   • 有效知识片段: {len(chunks)} 个")
print(f"   • 覆盖景区: {len(set([c['metadata']['景区'] for c in chunks]))} 个")
print(f"   • 存储路径: {os.path.abspath('./ys_rag_db')}")
print("\n📊 景区分布:")
for scenic in sorted(set([c['metadata']['景区'] for c in chunks])):
    count = sum(1 for c in chunks if c['metadata']['景区'] == scenic)
    print(f"   • {scenic}: {count} 个片段")
print("="*60)

print("\n💡 现在可以运行 `python ask_ys.py` 测试智能问答了！")
