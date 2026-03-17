# -*- coding: utf-8 -*-
"""颍上小智 - 豆包大模型接入"""
import requests
import json

API_KEY = "aea0249a-f824-4caa-8dc1-6ea8e8e96dbd"

API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

MODEL = "ep-20260314173917-ntg75"

SYSTEM_PROMPT = """你是"颍上小智"，一个智能旅游问答助手。

你有两个身份：
1. 旅游问答模式：回答颍上旅游相关问题（景区信息、门票、开放时间等）
2. 管鲍对话模式：以管仲或鲍叔牙的身份与用户对话

颍上主要景区信息：
- 八里河景区：5A级，门票90元，开放时间08:00-17:30
- 管仲老街：4A级，免费开放，08:00-22:00
- 尤家花园：3A级，门票50元
- 迪沟生态园：4A级，免费开放
- 湿地公园：4A级，免费开放
- 江心洲公园：免费开放
- 明清苑：门票30元
- 管鲍祠：免费开放
- 小张庄公园：免费开放

管鲍之交典故：
- 管仲和鲍叔牙是好朋友，鲍叔牙推荐管仲做相国
- 管仲曾说："生我者父母，知我者鲍子也"
- 他们留下了"管鲍之交"的千古佳话

回答要求：
- 亲切友好，使用简单的语言
- 如果不知道某事，请如实告知
- 可以适当使用表情"""

def chat_with_doubao(messages, model=MODEL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048
    }, ensure_ascii=False)

    try:
        response = requests.post(API_URL, headers=headers, data=body.encode('utf-8'), timeout=60)

        if response.status_code != 200:
            return f"API错误 (状态码 {response.status_code}): {response.text[:200]}"

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        elif "error" in result:
            return f"API错误: {result['error'].get('message', str(result['error']))}"
        else:
            return f"抱歉，响应格式异常: {response.text[:200]}"
    except Exception as e:
        return f"网络错误: {str(e)}"

def main():
    print("=" * 50)
    print("🌾 颍上小智 - 豆包大模型版")
    print("=" * 50)
    print("输入 'quit' 退出程序")
    print("=" * 50)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    while True:
        try:
            user_input = input("\n👤 您: ").strip()
        except:
            break

        if user_input.lower() in ['quit', 'q', '退出']:
            print("\n🌾 再见！欢迎下次使用颍上小智~")
            break

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        print("\n🤖 颍小智正在思考...")
        response = chat_with_doubao(messages)

        messages.append({"role": "assistant", "content": response})

        if len(messages) > 21:
            messages = [messages[0]] + messages[-20:]

        print(f"\n🌾 颍小智: {response}")

if __name__ == "__main__":
    main()
