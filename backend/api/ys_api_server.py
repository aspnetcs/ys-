# -*- coding: utf-8 -*-
"""颍上小智 - 后端API服务（支持流式输出 + 文件上传 + RAG）"""
from flask import Flask, request, jsonify, send_file, Response
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com' # 配置国内镜像，确保顺利下载 Whisper 模型
from flask_cors import CORS
import requests
import json
import base64
import threading
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'md', 'csv', 'xlsx', 'xls', 'mp3', 'wav', 'm4a', 'ogg', 'mp4', 'mov'}

API_KEY = os.getenv('ARK_API_KEY', '')
API_URL = os.getenv('ARK_API_URL', 'https://ark.cn-beijing.volces.com/api/v3/chat/completions')
MODEL = os.getenv('ARK_MODEL_ID', 'ep-20260314173917-ntg75')

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '').strip(" `\\n\\r\\t")
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com').strip(" `\\n\\r\\t")
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat').strip(" `\\n\\r\\t")

CURRENT_MODEL = os.getenv('CURRENT_MODEL', 'ark')

SYSTEM_PROMPT = """你是"颍上小智"，一个智能旅游问答助手。

你有两个身份：
1. 旅游问答模式：回答颍上旅游相关问题（景区信息、门票、开放时间、美食、交通等）
2. 管鲍对话模式：以管仲或鲍叔牙的身份与用户对话

==============================
【颍上景区详细信息】
==============================

1. 八里河景区
- 等级：5A级
- 门票：90元
- 开放时间：08:00-17:30
- 特色：皖北地区首家5A级景区，融生态旅游、休闲度假于一体，世界风光、锦绣中华、鸟语林、碧波游览区四大主题园区
- 美食：八里河鱼宴、八里河活鱼三吃、特色农家菜
- 地址：安徽省阜阳市颍上县八里河镇
- 交通指南：
  * 自驾：从阜阳出发，沿S102省道至颍上县，再沿八里河大道即可到达
  * 公交：颍上县城有直达景区的公交车，约20分钟车程
  * 高铁：从颍上北站下车后，可乘坐出租车或公交车前往
- 周边：管仲老街、尤家花园、明清苑

2. 管仲老街
- 门票：免费
- 开放时间：08:00-22:00
- 特色：春秋里街区、皖北水乡古韵、青石板路、小桥流水、管仲文化故里
- 美食：太和板面、阜阳卷馍、格拉条、尤记柿饼、管仲鱼汤
- 地址：颍上县慎城镇管仲大道
- 交通指南：
  * 自驾：直接导航至"管仲老街"，景区有停车场
  * 公交：颍上县城内多条公交线路可达
  * 步行：从县城中心步行约10分钟即可到达
- 周边：明清苑、江心洲滨河公园、管鲍祠

3. 尤家花园
- 等级：3A级
- 门票：50元
- 开放时间：08:00-17:30
- 特色：始建于清末，1922年扩建为苏式园林，四面环水，三条水系分为四区
- 美食：尤记柿饼、管仲鱼汤
- 地址：颍上县尤家花园路
- 交通指南：
  * 自驾：导航至"尤家花园"，景区有停车场
  * 公交：颍上县城有公交车直达
  * 出租车：从县城中心打车约15分钟
- 周边：管仲老街、明清苑

4. 迪沟生态园
- 等级：4A级
- 门票：免费
- 特色：湿地生态观鸟胜地、珍稀动物、地质奇观
- 最佳观鸟时间：清晨和傍晚
- 地址：颍上县迪沟镇
- 交通指南：
  * 自驾：从颍上县城沿S102省道至迪沟镇
  * 公交：颍上县城有前往迪沟的班车
  * 出租车：从县城打车约30分钟
- 周边：小张庄公园

5. 湿地公园（五里湖）
- 等级：4A级
- 门票：免费
- 特色：滨河休闲公园、湿地生态、城市氧吧
- 地址：颍上县五里湖
- 交通指南：
  * 自驾：导航至"五里湖湿地公园"
  * 公交：颍上县城内多条公交线路可达
  * 步行：从县城中心步行约20分钟
- 周边：管仲老街、江心洲滨河公园

6. 江心洲公园
- 门票：免费
- 特色：滨河休闲、文化公园
- 地址：颍上县江心洲
- 交通指南：
  * 自驾：导航至"江心洲滨河公园"
  * 公交：颍上县城内多条公交线路可达
  * 步行：从县城中心步行约15分钟
- 周边：明清苑、管仲老街、湿地公园

7. 明清苑
- 门票：30元
- 特色：明清古建筑群、南北建筑风格、古风摄影
- 地址：颍上县江心洲滨河公园内
- 交通指南：
  * 自驾：导航至"明清苑"
  * 公交：颍上县城内多条公交线路可达
  * 步行：从县城中心步行约15分钟
- 周边：江心洲滨河公园、管仲老街

8. 管鲍祠
- 门票：免费
- 开放时间：全天
- 特色：为纪念管仲和鲍叔牙而建，管仲纪念馆
- 地址：颍上县顺河路管仲公园内
- 交通指南：
  * 自驾：导航至"管鲍祠"，位于管仲公园内
  * 公交：颍上县城内多条公交线路可达
  * 步行：从县城中心步行约10分钟
- 周边：管仲老街、明清苑

9. 小张庄公园
- 门票：免费
- 特色：生态观光、休闲娱乐、萌宠乐园
- 地址：颍上县谢桥镇小张庄村
- 交通指南：
  * 自驾：从颍上县城沿S102省道至谢桥镇小张庄村
  * 公交：颍上县城有前往谢桥的班车，在小张庄下车
  * 出租车：从县城打车约25分钟
- 周边：迪沟生态园

==============================
【管鲍之交典故】
==============================
管仲和鲍叔牙的故事：
1. 相识相交：两人年轻时一起经商，鲍叔牙总是让管仲多分钱。鲍叔牙说："管仲家里穷，等他有钱了就会还。"
2. 各为其主：齐襄公死后，公子纠和公子小白争夺王位。管仲辅佐公子纠，鲍叔牙辅佐公子小白。
3. 推荐管仲：公子小白即位（齐桓公）后，鲍叔牙劝阻杀管仲，说："如果您只想治理齐国，有我就够了；如果想称霸天下，必须用管仲！"
4. 管仲名言："生我者父母，知我者鲍子也"
5. 鲍叔牙让贤：放弃做相国的机会，推荐管仲，自己甘居其下

==============================
【颍上历史文化】
==============================
- 位置：安徽省阜阳市
- 历史：春秋时期属楚国，管仲故里
- 文化：管仲文化、颍淮文化
- 非遗：颍上花鼓灯（国家级非物质文化遗产）、嗨子戏（地方戏曲）
- 特产：颍上大米、颍上红萝卜、迪沟粉丝

==============================
【旅游路线推荐】
==============================
1. 一日游：八里河 + 管仲老街 + 明清苑
2. 二日游：八里河 + 迪沟生态园 + 管仲老街 + 湿地公园

==============================
【回答要求】
==============================
1. 亲切友好，使用简单的语言
2. 如果不知道某事，请如实告知
3. 可以适当使用表情
4. 根据用户问题自动判断使用旅游问答模式或管鲍对话模式
5. 涉及管仲问题时，可以适当引入管鲍之交典故
6. 【非常重要】必须只输出纯文本，严禁使用任何Markdown格式（包括反引号 ` 等代码块符号、加粗、标题等），因为前端不支持Markdown渲染。不要输出 ```markdown 或 ``` 等标记。
"""

conversation_history = {}
feedback_list = []
history_lock = threading.Lock()

user_files = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def call_llm(messages, stream=False):
    """统一调用LLM接口，根据配置选择模型"""
    if CURRENT_MODEL == 'deepseek' and DEEPSEEK_API_KEY:
        return call_deepseek(messages, stream)
    else:
        return call_ark(messages, stream)

def call_deepseek(messages, stream=False):
    """调用DeepSeek API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048
    }
    if stream:
        data["stream"] = True

    response = requests.post(
        f"{DEEPSEEK_API_URL}/chat/completions",
        headers=headers,
        json=data,
        timeout=120,
        stream=stream
    )
    return response

def call_ark(messages, stream=False):
    """调用Ark(豆包) API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2048
    }
    if stream:
        data["stream"] = True

    response = requests.post(
        API_URL,
        headers=headers,
        json=data,
        timeout=120,
        stream=stream
    )
    return response

def extract_text_from_file(file_path, file_ext):
    """从不同类型文件中提取文本内容"""
    text = ""
    try:
        if file_ext == 'txt' or file_ext == 'md' or file_ext == 'csv':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

        elif file_ext == 'pdf':
            try:
                from pdfminer.high_level import extract_text
                text = extract_text(file_path)
            except ImportError:
                text = "[PDF解析需要安装pdfminer.six: pip install pdfminer.six]"

        elif file_ext in ['doc', 'docx']:
            try:
                from docx import Document
                doc = Document(file_path)
                text = '\n'.join([p.text for p in doc.paragraphs])
            except ImportError:
                text = "[Word文档解析需要python-docx库]"

        elif file_ext in ['xlsx', 'xls']:
            try:
                import pandas as pd
                df = pd.read_excel(file_path)
                text = df.to_string()
            except ImportError:
                text = "[Excel解析需要pandas库]"

        elif file_ext in ['mp3', 'wav', 'm4a', 'ogg', 'mp4', 'mov']:
            try:
                from faster_whisper import WhisperModel
                print(f"正在进行本地音视频语音转写: {file_path}")
                model = WhisperModel("base", device="auto", compute_type="default")
                segments, info = model.transcribe(file_path, beam_size=5)
                
                text_parts = []
                for segment in segments:
                    text_parts.append(segment.text)
                
                text = " ".join(text_parts)
                if not text.strip():
                    text = "[该音视频中未识别到有效语音]"
                else:
                    text = "[以下为音视频语音转写内容]\n" + text
            except Exception as e:
                text = f"[音视频解析失败: {str(e)}]"

    except Exception as e:
        text = f"[文件读取错误: {str(e)}]"

    return text[:50000]

def get_history(user_id):
    with history_lock:
        if user_id not in conversation_history:
            conversation_history[user_id] = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        return conversation_history[user_id]

def save_history(user_id, messages):
    with history_lock:
        conversation_history[user_id] = messages
        if len(messages) > 21:
            conversation_history[user_id] = [messages[0]] + messages[-20:]

@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(__file__), 'docs', '颍上小智_API版.html')
    return send_file(html_path, mimetype='text/html')

@app.route('/api/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/chat', methods=['POST'])
def chat():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_ACCESS_KEY'):
        return jsonify({'error': 'Unauthorized: invalid API key'}), 401

    data = request.json
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    clear_history = data.get('clear', False)
    use_file_context = data.get('use_file_context', True)

    messages = get_history(user_id)
    if clear_history:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    user_files_content = ""
    if use_file_context and user_id in user_files and user_files[user_id]:
        file_context_parts = []
        for f in user_files[user_id]:
            file_context_parts.append(f"【{f['filename']}】\n{f['text_content']}")
        user_files_content = "\n\n".join(file_context_parts)

        context_prompt = f"""用户上传了以下文件内容，请结合这些内容回答用户的问题：

{user_files_content}

---
用户当前问题：{message}"""
        messages.append({"role": "user", "content": context_prompt})
    else:
        messages.append({"role": "user", "content": message})

    try:
        response = call_llm(messages)

        if response.status_code != 200:
            return jsonify({"error": f"API错误: {response.text[:200]}"}), 500

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            # 过滤常见的 Markdown 代码块标记，防止前端显示反引号
            reply = reply.replace('```markdown\\n', '').replace('```markdown', '').replace('```json\\n', '').replace('```json', '').replace('```', '')
            if use_file_context and user_files_content:
                messages[-1] = {"role": "user", "content": message}
            messages.append({"role": "assistant", "content": reply})
            save_history(user_id, messages)
            return jsonify({"reply": reply, "files_used": bool(user_files_content), "model": CURRENT_MODEL})
        else:
            return jsonify({"error": "响应格式异常"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_ACCESS_KEY'):
        return jsonify({'error': 'Unauthorized: invalid API key'}), 401

    data = request.json
    user_id = data.get('user_id', 'default')
    message = data.get('message', '')
    clear_history = data.get('clear', False)
    use_file_context = data.get('use_file_context', True)

    messages = get_history(user_id)
    if clear_history:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    user_files_content = ""
    if use_file_context and user_id in user_files and user_files[user_id]:
        file_context_parts = []
        for f in user_files[user_id]:
            file_context_parts.append(f"【{f['filename']}】\n{f['text_content']}")
        user_files_content = "\n\n".join(file_context_parts)

        context_prompt = f"""用户上传了以下文件内容，请结合这些内容回答用户的问题：

{user_files_content}

---
用户当前问题：{message}"""
        messages.append({"role": "user", "content": context_prompt})
        original_message = message
    else:
        messages.append({"role": "user", "content": message})
        original_message = None
        user_files_content = None

    def generate():
        try:
            response = call_llm(messages, stream=True)

            if response.status_code != 200:
                yield f"data: {json.dumps({'error': 'API错误'})}\n\n"
                return

            full_reply = ""

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        data_str = decoded_line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data_obj = json.loads(data_str)
                            if 'choices' in data_obj and len(data_obj['choices']) > 0:
                                delta = data_obj['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    chunk = delta['content']
                                    # 过滤反引号
                                    if '`' in chunk:
                                        chunk = chunk.replace('`', '')
                                    # 如果是常见 markdown 前缀在流开头，去掉
                                    if len(full_reply) < 20:
                                        chunk = chunk.replace('markdown\\n', '').replace('markdown', '')
                                    full_reply += chunk
                                    yield f"data: {json.dumps({'chunk': chunk})}\\n\\n"
                        except json.JSONDecodeError:
                            continue

            if original_message is not None:
                messages[-1] = {"role": "user", "content": original_message}
            messages.append({"role": "assistant", "content": full_reply})
            save_history(user_id, messages)

            yield f"data: {json.dumps({'done': True, 'reply': full_reply, 'files_used': bool(user_files_content), 'model': CURRENT_MODEL})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/clear', methods=['POST'])
def clear():
    data = request.json
    user_id = data.get('user_id', 'default')
    with history_lock:
        if user_id in conversation_history:
            del conversation_history[user_id]
    return jsonify({"success": True})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    feedback = {
        "id": len(feedback_list) + 1,
        "category": data.get('category', ''),
        "content": data.get('content', ''),
        "contact": data.get('contact', ''),
        "time": data.get('time', '')
    }
    feedback_list.append(feedback)
    return jsonify({"success": True, "id": feedback["id"]})

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    return jsonify({"feedback": feedback_list})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_ACCESS_KEY'):
        return jsonify({'error': 'Unauthorized: invalid API key'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    user_id = request.form.get('user_id', 'default')

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    file_ext = file.filename.rsplit('.', 1)[1].lower()
    file_id = str(uuid.uuid4())
    filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(file_path)

    text_content = extract_text_from_file(file_path, file_ext)

    if user_id not in user_files:
        user_files[user_id] = []

    file_info = {
        "file_id": file_id,
        "filename": file.filename,
        "stored_filename": filename,
        "file_type": file_ext,
        "text_content": text_content,
        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "size": os.path.getsize(file_path)
    }
    user_files[user_id].append(file_info)

    return jsonify({
        "success": True,
        "file_id": file_id,
        "filename": file.filename,
        "file_type": file_ext,
        "text_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content,
        "text_length": len(text_content),
        "message": f"文件上传成功！已提取 {len(text_content)} 个字符的内容。"
    })

@app.route('/api/files', methods=['GET'])
def get_user_files():
    """获取用户上传的文件列表"""
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_ACCESS_KEY'):
        return jsonify({'error': 'Unauthorized: invalid API key'}), 401

    user_id = request.args.get('user_id', 'default')
    files = user_files.get(user_id, [])

    return jsonify({
        "files": [{
            "file_id": f["file_id"],
            "filename": f["filename"],
            "file_type": f["file_type"],
            "upload_time": f["upload_time"],
            "size": f["size"],
            "text_length": len(f["text_content"])
        } for f in files]
    })

@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除用户上传的文件"""
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_ACCESS_KEY'):
        return jsonify({'error': 'Unauthorized: invalid API key'}), 401

    user_id = request.args.get('user_id', 'default')

    if user_id in user_files:
        for i, f in enumerate(user_files[user_id]):
            if f["file_id"] == file_id:
                file_path = os.path.join(UPLOAD_FOLDER, f["stored_filename"])
                if os.path.exists(file_path):
                    os.remove(file_path)
                user_files[user_id].pop(i)
                return jsonify({"success": True, "message": "文件已删除"})

    return jsonify({'error': 'File not found'}), 404

@app.route('/api/files/<file_id>/content', methods=['GET'])
def get_file_content(file_id):
    """获取文件内容"""
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_ACCESS_KEY'):
        return jsonify({'error': 'Unauthorized: invalid API key'}), 401

    user_id = request.args.get('user_id', 'default')

    if user_id in user_files:
        for f in user_files[user_id]:
            if f["file_id"] == file_id:
                return jsonify({
                    "filename": f["filename"],
                    "file_type": f["file_type"],
                    "content": f["text_content"]
                })

    return jsonify({'error': 'File not found'}), 404

@app.route('/api/chat/image', methods=['POST'])
def chat_with_image():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_ACCESS_KEY'):
        return jsonify({'error': 'Unauthorized: invalid API key'}), 401

    try:
        if 'image' not in request.files and 'image_base64' not in request.form:
            return jsonify({'error': 'No image provided'}), 400

        user_id = request.form.get('user_id', 'default')
        message = request.form.get('message', '请描述这张图片')

        if 'image' in request.files:
            file = request.files['image']
            image_data = file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        else:
            image_base64 = request.form.get('image_base64')

        messages = get_history(user_id)

        content = [
            {"type": "text", "text": message},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]

        messages.append({"role": "user", "content": content})

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

        response = requests.post(API_URL, headers=headers, data=body.encode('utf-8'), timeout=120)

        if response.status_code != 200:
            return jsonify({"error": f"API错误: {response.text[:200]}"}), 500

        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            reply = result["choices"][0]["message"]["content"]
            reply = reply.replace('```markdown\\n', '').replace('```markdown', '').replace('```json\\n', '').replace('```json', '').replace('```', '')
            messages.append({"role": "assistant", "content": reply})
            save_history(user_id, messages)
            return jsonify({"reply": reply})
        else:
            return jsonify({"error": "响应格式异常"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/voice', methods=['POST'])
def upload_voice():
    """接收前端语音记录并调用本地 Whisper ASR 接口"""
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_ACCESS_KEY'):
        return jsonify({'error': 'Unauthorized: invalid API key'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    file = request.files['file']
    user_id = request.form.get('user_id', 'default')

    try:
        import uuid
        from faster_whisper import WhisperModel
        
        # 将前端传上来的录音临时保存
        temp_filename = f"temp_voice_{uuid.uuid4().hex}.mp3"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_path)
        
        print(f"[{user_id}] 正在使用本地引擎识别录音...")
        
        model = WhisperModel("base", device="auto", compute_type="default")
        segments, info = model.transcribe(temp_path, beam_size=5)
        
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)
            
        text = " ".join(text_parts).strip()
        
        # 识别完毕，删掉临时录音文件释放空间
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if not text:
            return jsonify({'error': '我没听清你在说什么，可以大声点再试一次吗？'})
            
        return jsonify({'text': text})

    except Exception as e:
        return jsonify({'error': f'语音处理失败: {str(e)}'})

if __name__ == '__main__':
    print("=" * 50)
    print("🌾 颍上小智 API 服务启动中...")
    print("=" * 50)
    print("HTTP接口: http://localhost:5000")
    print("流式接口: POST /api/chat/stream")
    print("=" * 50)
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)