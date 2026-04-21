# 颍上小智 - 云服务器部署指南

## 部署步骤

### 1. 上传代码到云服务器

将 `backend/api/` 目录下的文件上传到云服务器，例如：

```bash
scp -r backend/api/* root@你的服务器IP:/opt/yingxiao-ai/
```

或者使用 FileZilla 等工具上传。

### 2. 安装依赖

SSH连接到服务器后，执行：

```bash
cd /opt/yingxiao-ai
pip install flask flask-cors requests python-dotenv
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
nano .env
```

添加以下内容：

```
ARK_API_KEY=你的豆包API密钥
ARK_API_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions
ARK_MODEL_ID=你的模型ID
API_ACCESS_KEY=15556556443
FLASK_DEBUG=false
```

### 4. 启动服务

```bash
cd /opt/yingxiao-ai
nohup python ys_api_server.py > api.log 2>&1 &
```

### 5. 验证服务

```bash
curl http://localhost:5000/api/chat/stream
```

### 6. 使用 PM2 管理服务（推荐）

```bash
npm install -g pm2
pm2 start ys_api_server.py --name yingxiao-api
pm2 save
pm2 startup
```

常用命令：
- `pm2 status` - 查看状态
- `pm2 logs yingxiao-api` - 查看日志
- `pm2 restart yingxiao-api` - 重启服务

## 目录结构（云服务器）

```
/opt/yingxiao-ai/
├── api/
│   ├── ys_api_server.py    # 主API服务
│   ├── guanbao_api.py      # 管鲍API
│   ├── doubao_chat.py      # 豆包封装
│   └── llm_provider.py     # LLM封装
├── docs/
│   ├── 颍上小智.html
│   └── 颍上小智_API版.html
├── .env                    # 环境变量（需要手动创建）
└── requirements.txt        # Python依赖
```

## 更新代码

如果代码有更新，重复步骤1-2，然后重启服务：

```bash
pm2 restart yingxiao-api
```

## 防火墙配置

确保云服务器的安全组开放了5000端口：

```bash
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
```