# -*- coding: utf-8 -*-
"""颍上小智 - 管鲍之交数字孪生对话API"""
from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# 角色设定
ROLES = {
    "管仲": {
        "name": "管仲",
        "title": "春秋时期齐国名相",
        "personality": "智慧超群、善于治国、重视人才、务实进取",
        "background": "辅佐齐桓公称霸天下，提出\"仓廪实而知礼节\"等治国理念",
        "knowledge": ["治国之道", "经济发展", "人才选用", "军事谋略", "外交策略"],
        "greeting": "老夫管仲也！有何见解想与老夫探讨？"
    },
    "鲍叔牙": {
        "name": "鲍叔牙",
        "title": "春秋时期齐国大夫",
        "personality": "忠诚厚道、重情重义、知人善任、淡泊名利",
        "background": "与管仲相交甚厚，推荐管仲辅佐齐桓公，留下\"管鲍之交\"佳话",
        "knowledge": ["友谊之道", "识人用人", "君子品格", "忠诚义气"],
        "greeting": "老夫鲍叔牙是也！相逢即是有缘，汝有何事想与老夫叙说？"
    }
}

# 对话历史
conversation_history = {}

# 系统提示词
SYSTEM_PROMPTS = {
    "管仲": """你是管仲，春秋时期齐国名相，有着卓越的政治才能和深邃的思想。

角色设定：
- 智慧超群、善于治国、重视人才、务实进取
- 辅佐齐桓公称霸天下，提出"仓廪实而知礼节"等治国理念
- 说话风格：引经据典、深入浅出、富有哲理

请用管仲的身份和语气与用户对话，可以引用《管子》中的思想，结合现代话题进行探讨。
回答要简洁、有深度、富有启发性。""",

    "鲍叔牙": """你是鲍叔牙，春秋时期齐国大夫，以忠诚厚道、重情重义著称。

角色设定：
- 忠诚厚道、重情重义、知人善任、淡泊名利
- 与管仲相交甚厚，推荐管仲辅佐齐桓公，留下"管鲍之交"佳话
- 说话风格：温和亲切、重情重义、循循善诱

请用鲍叔牙的身份和语气与用户对话，体现友谊之道和君子品格。
回答要温暖、有深度、富有启发性。"""
}

# 模拟对话（无需API_key的简单版本）
def simple_chat(role, user_input):
    """简单的对话模拟（基于规则）"""
    
    role_data = ROLES[role]
    
    # 预设问答
    qa_database = {
        "管仲": {
            "你好": f"{role_data['greeting']}",
            "您好": f"{role_data['greeting']}",
            "hello": f"{role_data['greeting']}",
            "你是谁": f"{role_data['greeting']} 老夫便是管仲，曾辅佐齐桓公称霸天下。",
            "管鲍之交": "管鲍之交，乃老夫与鲍叔牙之深厚友谊也。当年鲍叔牙举荐老夫于桓公，甘居其下，此等胸襟，实属难得。我二人相交数十年，彼此信任，无论贫穷富贵，始终不弃。此等友谊，堪称千古楷模！",
            "治国": "治国之道，在于民富国强。老夫以为，仓廪实而知礼节，衣食足而知荣辱。先让百姓安居乐业，再教之以礼义。此乃治国之本也。",
            "人才": "人才乃国家之栋梁。老夫以为，治国之要，在于选贤任能。用人当用其长，避其短。又云：'千里马常有，而伯乐不常有'，识人之明，实乃为政者之要务也。",
            "诚信": "诚信者，国之宝也，民之凭也。老夫辅佐桓公，首重信诺。一言既出，驷马难追。治国之道，无信不立。",
            "经济": "发展经济，宜藏富于民。老夫主张通商贾之便，利农桑之业。百姓仓廪充实，自然知礼节。经济乃国家之根基，不可不察也。"
        },
        "鲍叔牙": {
            "你好": f"{role_data['greeting']}",
            "您好": f"{role_data['greeting']}",
            "hello": f"{role_data['greeting']}",
            "你是谁": f"{role_data['greeting']} 老夫鲍叔牙是也。",
            "管鲍之交": "管鲍之交，乃老夫与管仲之深厚友谊也。老夫深知管仲之才，荐之于桓公，甘居其下。此等友谊，贵在相知相信。管仲曾言：'生我者父母，知我者鲍子也'，此言让老夫感动至今。",
            "友谊": "友谊之道，贵在相知。老夫与管仲相交，始终以诚相待。虽各有见解，但彼此信任。无论贫富贵贱，不离不弃。此乃真友谊也。",
            "诚信": "诚信乃立身之本。老夫生平最重信诺，一言既出，必有践行。与人相交，当以诚相待，方能长久。",
            "知人": "知人者智，自知者明。老夫与管仲相交多年，深知其才。故举荐于桓公，不计个人得失。用人之道，在于扬其长、避其短。"
        }
    }
    
    # 检查预设问答
    user_lower = user_input.lower()
    for key, answer in qa_database[role].items():
        if key in user_lower:
            return answer
    
    # 默认回复
    default_responses = {
        "管仲": f"{role_data['greeting']} 汝之所问，颇有意思。不妨与老夫细说其中的道理。",
        "鲍叔牙": f"{role_data['greeting']} 汝有何见解？但说无妨。"
    }
    
    return default_responses[role]

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>颍上小智 - 管鲍之交</title>
        <style>
            body { font-family: Microsoft YaHei, Arial; background: linear-gradient(135deg, #1a1a2e, #16213e); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; margin: 0; }
            .container { width: 100%; max-width: 500px; }
            .header { text-align: center; color: #fff; margin-bottom: 20px; }
            .header h1 { font-size: 28px; margin-bottom: 10px; }
            .header p { color: #aaa; font-size: 14px; }
            .role-select { display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; }
            .role-btn { padding: 12px 24px; border: none; border-radius: 25px; font-size: 16px; cursor: pointer; transition: all 0.3s; background: #333; color: #fff; }
            .role-btn.active { background: #667eea; transform: scale(1.05); }
            .role-btn:hover { transform: scale(1.05); }
            .chat { background: white; border-radius: 15px; overflow: hidden; }
            .msgs { height: 350px; overflow-y: auto; padding: 15px; background: #f5f5f5; }
            .msg { margin-bottom: 12px; }
            .msg-bot { text-align: left; }
            .msg-user { text-align: right; }
            .txt { display: inline-block; max-width: 80%; padding: 10px 14px; border-radius: 12px; font-size: 14px; }
            .msg-user .txt { background: #667eea; color: white; }
            .msg-bot .txt { background: white; color: #333; }
            .input-box { display: flex; padding: 12px; gap: 8px; }
            .input-box input { flex: 1; padding: 12px; border: 2px solid #ddd; border-radius: 20px; font-size: 14px; }
            .input-box button { padding: 12px 20px; background: #667eea; color: white; border: none; border-radius: 20px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏛️ 管鲍之交</h1>
                <p>与历史名人跨时空对话</p>
            </div>
            <div class="role-select">
                <button class="role-btn active" onclick="selectRole('管仲')">对话管仲</button>
                <button class="role-btn" onclick="selectRole('鲍叔牙')">对话鲍叔牙</button>
            </div>
            <div class="chat">
                <div class="msgs" id="msgs">
                    <div class="msg msg-bot">
                        <div class="txt">请选择一位历史人物，开始对话~</div>
                    </div>
                </div>
                <div class="input-box">
                    <input type="text" id="txt" placeholder="输入你想问的问题..." onkeypress="if(event.key==='Enter')send()">
                    <button onclick="send()">发送</button>
                </div>
            </div>
        </div>
        <script>
            var currentRole = "管仲";
            
            function selectRole(role) {
                currentRole = role;
                document.querySelectorAll('.role-btn').forEach(b => b.classList.remove('active'));
                event.target.classList.add('active');
                document.getElementById('msgs').innerHTML = '<div class="msg msg-bot"><div class="txt">与' + role + '对话中...</div></div>';
            }
            
            function add(t, isUser) {
                var d = document.createElement("div");
                d.className = "msg " + (isUser ? "msg-user" : "msg-bot");
                d.innerHTML = '<div class="txt">' + t + '</div>';
                document.getElementById("msgs").appendChild(d);
                document.getElementById("msgs").scrollTop = document.getElementById("msgs").scrollHeight;
            }
            
            function send() {
                var inp = document.getElementById("txt");
                var q = inp.value.trim();
                if (!q) return;
                add(q, true);
                inp.value = "";
                
                fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({role: currentRole, message: q})
                })
                .then(r => r.json())
                .then(d => {
                    add(d.reply, false);
                });
            }
        </script>
    </body>
    </html>
    '''

@app.route('/api/chat', methods=['POST'])
def chat():
    """对话API"""
    data = request.json
    role = data.get('role', '管仲')
    message = data.get('message', '')
    
    if role not in ROLES:
        return jsonify({"error": "无效的角色"})
    
    # 获取回复
    reply = simple_chat(role, message)
    
    return jsonify({
        "role": role,
        "reply": reply
    })

@app.route('/api/roles')
def get_roles():
    """获取可用角色"""
    return jsonify(ROLES)

if __name__ == '__main__':
    print("=" * 50)
    print("🏛️ 颍上小智 - 管鲍之交数字孪生对话")
    print("=" * 50)
    print("访问地址: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
