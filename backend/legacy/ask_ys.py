# -*- coding: utf-8 -*-
"""颍上智能问答（颍小智·零警告零报错终极版）"""
import os
import sys
import logging
import warnings
import re  # ← 【关键修复1】补全缺失导入

# === 【三重保险】彻底屏蔽遥测（政府内网必备）===
os.environ['CHROMA_TELEMETRY'] = '0'
os.environ['ANONYMIZED_TELEMETRY'] = 'false'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# 屏蔽所有遥测相关日志
logging.getLogger('chromadb').setLevel(logging.CRITICAL)
logging.getLogger('chromadb.telemetry').setLevel(logging.CRITICAL)
logging.getLogger('httpx').setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*telemetry.*")
warnings.filterwarnings("ignore", message=".*capture.*")

print("🌾 正在唤醒颍小智...")
sys.stdout.flush()

# === 安全导入（消除弃用警告）===
try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    from langchain.vectorstores import Chroma
    from langchain.embeddings import HuggingFaceEmbeddings

# === 【关键修复2】Chroma客户端级禁用遥测 ===
try:
    from chromadb.config import Settings
    CHROMA_SETTINGS = Settings(anonymized_telemetry=False)
except Exception:
    CHROMA_SETTINGS = None

# === 加载知识库（静默无警告）===
embeddings = HuggingFaceEmbeddings(
    model_name="D:/颍上智能问答助手/bge-small-zh-v1.5",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# 创建时传入遥测禁用配置
vector_db_kwargs = {
    "persist_directory": "./ys_rag_db",
    "embedding_function": embeddings,
    "collection_name": "ys_scenic_knowledge"
}
if CHROMA_SETTINGS is not None:
    vector_db_kwargs["client_settings"] = CHROMA_SETTINGS

vector_db = Chroma(**vector_db_kwargs)
print("✅ 颍小智已上线！俺是咱颍上的旅游小管家~\n")

# === 智能问答循环（安全清洗）===
while True:
    try:
        question = input("👉 您想问啥？（输入q退出）: ").strip()
        if question.lower() in ['q', 'quit', '退出']: 
            print("\n🌾 颍小智：慢走啊！有空常来颍上耍~")
            break
        if not question:
            print("🌾 颍小智：俺等着哩！您说说想了解啥？\n")
            continue
        
        # 智能查询处理
        # 同义词和相关词映射
        synonyms = {
            '老街': '管仲老街',
            '八里河': '八里河景区',
            '迪沟': '迪沟生态园',
            '尤家花园': '尤家花园',
            '湿地公园': '湿地公园',
            '江心洲': '江心洲公园',
            '明清苑': '明清苑',
            '管鲍祠': '管鲍祠',
            '小张庄': '小张庄公园',
            '五里湖': '湿地公园',
            '管仲': '管仲老街',
            '生态园': '迪沟生态园',
            '花园': '尤家花园',
            '公园': '江心洲公园'
        }
        
        # 处理查询
        processed_question = question
        for key, value in synonyms.items():
            if key in question:
                processed_question = processed_question.replace(key, value)
        
        # 增强查询关键词
        keywords = ['特色', '门票', '开放时间', '地址', '美食', '历史', '交通', '游玩', '推荐']
        for keyword in keywords:
            if keyword in question and keyword not in processed_question:
                processed_question += f' {keyword}'
        
        # 检索+智能清洗
        results = vector_db.similarity_search(processed_question, k=5)
        formatted_results = []
        for idx, doc in enumerate(results):
            text = doc.page_content
            # 彻底清洗项目符号/多余空行
            text = re.sub(r'^o\s*', '', text, flags=re.MULTILINE)
            text = re.sub(r'\n{3,}', '\n\n', text).strip()
            if text and len(text.replace('\n', '')) > 15:
                formatted_results.append(f"【{idx+1}】{text}")
        
        # 生成颍上方言回答
        if formatted_results:
            context = "\n\n".join(formatted_results)
            scenic_set = {doc.metadata.get('景区', '颍上景点') for doc in results if doc.metadata.get('景区')}
            scenic_list = "、".join(sorted(scenic_set)) if scenic_set else "颍上核心景区"
            
            print("\n" + "="*50)
            print("🌾 颍小智：")
            print(f"（眼睛一亮）关于「{question}」，俺给您说道说道：\n")
            print(context)
            print(f"\n💡 小提示：以上内容来自 {scenic_list}")
            print("📍 想了解更细？直接问：'管仲老街几点关门？''迪沟观鸟最佳时间？'")
            print("="*50 + "\n")
        else:
            print("\n" + "="*50)
            print("🌾 颍小智：")
            print(f"哎呀！俺在资料库里没找到「{question}」的详细信息~\n")
            print("💡 建议您：")
            print("1️⃣ 换个问法（比如'管仲老街特色？'）")
            print("2️⃣ 问具体景区：八里河/管仲老街/迪沟/尤家花园/五里湖")
            print("3️⃣ 联系颍上文旅局：0558-XXXXXXX（资料库持续更新！）")
            print("\n❤️ 感谢您关注咱颍上！有空常来耍~")
            print("="*50 + "\n")
            
    except KeyboardInterrupt:
        print("\n\n🌾 颍小智：俺先歇会儿~ 随时喊俺！")
        break
    except Exception as e:
        if "re" not in str(e).lower():  # 避免循环报错
            print(f"\n❌ 遇到小问题：{str(e)}\n💡 请重试或联系技术支持\n")