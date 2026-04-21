# 颍上小智 - 项目结构

## 目录结构

```
yingxiao-ai/
├── backend/                    # 后端服务
│   ├── api/                   # 核心API服务（正在使用）
│   │   ├── ys_api_server.py   # 主API服务 - 豆包/Ark大模型
│   │   ├── guanbao_api.py     # 管鲍之交对话API
│   │   ├── doubao_chat.py     # 豆包对话封装
│   │   └── llm_provider.py    # LLM provider封装
│   │
│   ├── data/                  # 数据文件
│   │   ├── 颍上景区介绍.txt   # 景区基础信息
│   │   └── 颍上知识库.md      # 知识库文档
│   │
│   ├── scripts/               # 数据处理脚本
│   │   ├── crawl_ys_tourism_optimized.py  # 颍上旅游数据爬虫
│   │   ├── prepare_data.py    # 数据预处理
│   │   ├── enhance_local_data.py  # 本地数据增强
│   │   └── reformat_chunks.py # 数据格式转换
│   │
│   ├── docs/                  # 文档和网页
│   │   ├── 多API接入说明.md   # API接入指南
│   │   ├── 管仲小之青提示词优化.txt  # 提示词优化记录
│   │   ├── 颍上小智.html      # 网页版（基础版）
│   │   └── 颍上小智_API版.html  # 网页版（API版）
│   │
│   ├── legacy/                # 旧版本/废弃文件（仅供参考）
│   │   ├── ask_ys.py         # 旧版问答程序
│   │   ├── ask_ys_file_based.py  # 基于文件的旧版
│   │   ├── ys_api.py         # 旧API
│   │   ├── app_gradio.py     # Gradio旧版本
│   │   ├── build_vector_db.py  # 向量数据库构建（旧）
│   │   └── rebuild_vector_db_fixed.py  # 向量数据库重建（旧）
│   │
│   ├── .env.template          # 环境变量模板
│   ├── requirements.txt       # Python依赖
│   ├── natapp.ini            # 内网穿透配置
│   └── 启动API服务.bat       # 启动脚本
│
├── frontend/                   # 微信小程序前端
│   ├── pages/                 # 页面目录
│   │   ├── index/            # 首页
│   │   ├── chat/             # AI聊天页面
│   │   ├── guide/            # 智慧导览
│   │   ├── audio/            # 语音导览
│   │   ├── ticket/           # 门票预订
│   │   ├── transport/        # 交通出行
│   │   ├── profile/          # 个人中心
│   │   ├── heritage/         # 颍上非遗
│   │   ├── feedback/         # 意见反馈
│   │   ├── feedback-list/    # 反馈管理
│   │   └── mine/             # 我的（备用）
│   │
│   ├── static/               # 静态资源
│   │   ├── scenic/           # 景区图片
│   │   └── logo.png          # Logo
│   │
│   ├── uniCloud-aliyun/      # 云数据库
│   ├── uni_modules/          # uni-app模块
│   │
│   ├── app.js                # 应用入口
│   ├── app.json              # 应用配置
│   ├── app.wxss              # 全局样式
│   └── pages.json            # 页面配置
│
├── 修复总结.md                # 项目修复记录
└── 项目问题检查报告.md         # 问题报告
```

## 各模块说明

### Backend - 后端服务

#### api/ - 核心API（正在使用）
| 文件 | 说明 | 端口 |
|------|------|------|
| ys_api_server.py | 主API服务，豆包/Ark大模型集成，支持图片分析 | 5000 |
| guanbao_api.py | 管鲍之交数字孪生对话API | 5001 |
| doubao_chat.py | 豆包对话封装 | - |
| llm_provider.py | LLM统一接口封装 | - |

#### data/ - 业务数据
- 颍上景区介绍.txt - 景区基本信息
- 颍上知识库.md - 知识库文档

#### scripts/ - 数据处理
- crawl_ys_tourism_optimized.py - 爬取颍上旅游数据
- prepare_data.py - 数据预处理
- enhance_local_data.py - 数据增强
- reformat_chunks.py - 格式转换

#### docs/ - 文档
- 多API接入说明.md - API接入指南
- 管仲小之青提示词优化.txt - 提示词记录
- 颍上小智.html - 网页版演示
- 颍上小智_API版.html - API版演示

#### legacy/ - 旧版本（不建议使用）
旧版本的代码，仅供参考。

### Frontend - 微信小程序

| 页面 | 功能 |
|------|------|
| index | 首页 - 景区轮播、功能入口 |
| chat | AI聊天 - 管仲小之青智能问答，支持图片 |
| guide | 智慧导览 - 景区地图、路线推荐 |
| audio | 语音导览 |
| ticket | 门票预订 |
| transport | 交通出行 |
| profile | 个人中心 - 收藏、订单、反馈等 |
| heritage | 颍上非遗 - 国家级/省级/市级非遗列表 |
| feedback | 意见反馈 - 景区建议、小程序建议、其他 |
| feedback-list | 反馈管理 - 查看用户提交的反馶 |

## 启动方式

### 后端API服务
```bash
cd backend
pip install -r requirements.txt
python api/ys_api_server.py
# 服务地址: http://localhost:5000
```

### 前端（微信开发者工具）
导入 `frontend` 文件夹到微信开发者工具即可。

## 环境变量

参考 `.env.template` 配置：
- ARK_API_KEY - 豆包API密钥
- ARK_API_URL - API地址
- ARK_MODEL_ID - 模型ID
- API_ACCESS_KEY - 小程序访问密钥