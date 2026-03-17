# -*- coding: utf-8 -*-
"""颍上智能问答 · 网页版（颍小智方言版）"""
import os
import sys
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
os.environ['CURL_CA_BUNDLE'] = ''

import gradio as gr
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# === 加载颍上知识库 ===
print("🌾 正在唤醒颍小智...")
embeddings = HuggingFaceEmbeddings(
    model_name="D:/颍上智能问答助手/bge-small-zh-v1.5",
    model_kwargs={'device': 'cpu'}
)
vector_db = Chroma(
    persist_directory="./ys_rag_db",
    embedding_function=embeddings,
    collection_name="ys_scenic_knowledge"
)
print("✅ 颍小智已上线！")

# === 颍上方言问答函数 ===
def ask_yingshang(question):
    if not question.strip():
        return "🌾 颍小智：您还没提问呢~ 俺等着给您介绍咱颍上的好地方哩！"
    
    # 检索知识库
    results = vector_db.similarity_search(question, k=3)
    
    # 生成颍上方言回答
    if results:
        context = "\n\n".join([f"【{i+1}】{doc.page_content}" for i, doc in enumerate(results)])
        scenic_list = "、".join(set([doc.metadata.get('景区', '颍上景点') for doc in results]))
        
        response = f"""🌾 **颍小智（颍上旅游小管家）**：
俺刚翻了翻咱颍上的资料库，关于「{question}」，有这些信息：

{context}

💡 **小智贴心提示**：
- 以上内容来自：{scenic_list}
- 想了解更详细？直接问“八里河门票多少”“管仲老街开放时间”~
- 资料库持续更新中，有啥建议随时提！

📍 **颍上欢迎您**：八里河湿地观鸟、管仲老街品茶、迪沟生态园漫步... 俺们颍上，处处是风景！"""
        return response
    else:
        return f"""🌾 **颍小智**：
哎呀！俺在颍上资料库里没找到「{question}」的详细信息~ 

💡 **建议您**：
1️⃣ 换个问法试试（比如“八里河有啥好玩的”）
2️⃣ 问具体景区（八里河/管仲老街/迪沟/尤家花园）
3️⃣ 联系颍上文旅局：0558-XXXXXXX（资料库会持续更新！）

❤️ 感谢您关注咱颍上！有空常来耍~"""

# === 构建Gradio界面 ===
with gr.Blocks(title="🌾 颍上智能问答助手", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🌾 颍上智能问答助手（颍小智）
    ### 👋 俺是颍上旅游小管家！专为您解答八里河、管仲老街、迪沟等景区问题~
    *资料库更新至2024年 | 由颍上县文旅局技术支持*
    """)
    
    chatbot = gr.Chatbot(
        value=[("🌾 颍小智", "您好！俺是颍上旅游小管家颍小智~ 有啥想了解的？比如：\n• 八里河景区特色？\n• 管仲老街开放时间？\n• 迪沟生态园怎么玩？")],
        height=400,
        label="💬 与颍小智对话"
    )
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="👉 输入您的问题（例如：八里河门票多少钱？）",
            label="您的问题",
            scale=4
        )
        clear = gr.ClearButton([msg, chatbot], value="🧹 清空对话")
    
    gr.Markdown("""
    ---
    **📌 使用提示**：
    - 问具体景区：`八里河` `管仲老街` `迪沟` `尤家花园`
    - 问实用信息：`门票` `开放时间` `交通` `特色`
    - 颍上方言彩蛋：输入“俺想...”触发亲切回复！
    
    **💡 温馨提示**：当前知识库含9个核心片段，覆盖颍上主要景区。资料持续扩充中！
    """)
    
    # 交互逻辑
    def respond(message, chat_history):
        bot_message = ask_yingshang(message)
        chat_history.append((message, bot_message))
        return "", chat_history
    
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    gr.Examples(
        examples=[
            ["八里河景区有啥特色？"],
            ["管仲老街几点开门？"],
            ["迪沟生态园适合带孩子去吗？"],
            ["颍上哪里看荷花最好？"]
        ],
        inputs=msg,
        label="✨ 点击示例问题快速体验"
    )

# 启动服务
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 颍小智网页服务启动中...")
    print("📱 手机访问：确保电脑和手机在同一WiFi，浏览器输入：http://<电脑IP>:7860")
    print("   （查看电脑IP：cmd输入 ipconfig → 找IPv4地址）")
    print("💻 本机访问：http://127.0.0.1:7860")
    print("="*50 + "\n")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)