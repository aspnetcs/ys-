# -*- coding: utf-8 -*-
"""颍上小智 - 后端API服务"""
from flask import Flask, request, jsonify, send_file
import os
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

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

conversation_history = {}

@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(__file__), '颍上小智_API版.html')
    return send_file(html_path, mimetype='text/html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    clear_history = data.get('clear', False)

    if clear_history or user_id not in conversation_history:
        conversation_history[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    messages = conversation_history[user_id]
    messages.append({"role": "user", "content": message})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    body = json.dumps({
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048
    }, ensure_ascii=False)

    try:
        response = requests.post(API_URL, headers=headers, data=body.encode('utf-8'), timeout=60)

        if response.status_code != 200:
            return jsonify({"error": f"API错误: {response.text[:200]}"}), 500

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": reply})

            if len(messages) > 21:
                messages = [messages[0]] + messages[-20:]

            conversation_history[user_id] = messages

            return jsonify({"reply": reply})
        else:
            return jsonify({"error": "响应格式异常"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear():
    data = request.json
    user_id = data.get('user_id', 'default')
    if user_id in conversation_history:
        del conversation_history[user_id]
    return jsonify({"success": True})

if __name__ == '__main__':
    print("=" * 50)
    print("🌾 颍上小智 API 服务启动中...")
    print("=" * 50)
    print("请在浏览器打开: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
