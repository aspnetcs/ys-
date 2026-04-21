# 多API模型接入指南

本文档介绍如何使用统一LLM接口接入不同的模型API。

## 📋 目录

1. [架构概述](#架构概述)
2. [快速开始](#快速开始)
3. [支持的模型提供商](#支持的模型提供商)
4. [如何切换模型](#如何切换模型)
5. [代码示例](#代码示例)
6. [故障排除](#故障排除)

---

## 一、架构概述

### 设计目标

- ✅ **统一接口**：所有模型使用相同的调用方式
- ✅ **易于扩展**：新增模型只需添加适配器
- ✅ **灵活切换**：运行时动态切换不同模型
- ✅ **配置驱动**：通过环境变量管理API密钥
- ✅ **向后兼容**：无缝替换现有硬编码实现

### 核心组件

```
config.py           # 配置文件，管理所有模型配置
llm_provider.py     # 统一LLM接口和适配器
.env                # 环境变量文件（存储API密钥）
```

---

## 二、快速开始

### 步骤1：安装依赖

```bash
cd d:/yingxiao-ai/backend

# 安装必要依赖
pip install python-dotenv requests

# 可选：安装OpenAI SDK（如果使用OpenAI模型）
pip install openai
```

### 步骤2：配置环境变量

```bash
# 复制模板文件
cp .env.template .env

# 编辑 .env 文件，填写你的API密钥
# 保留你需要的模型配置，删除或注释掉不需要的
```

### 步骤3：测试配置

```bash
# 运行演示程序
python llm_demo.py

# 或者直接测试API服务
python ys_api_server_new.py
```

---

## 三、支持的模型提供商

### 已支持的模型

| 提供商 | 环境变量 | 模型示例 | 特点 |
|--------|----------|----------|------|
| **火山引擎方舟** | `ARK_API_KEY` | `ep-20260314173917-ntg75` | 当前使用，中文优化 |
| **OpenAI** | `OPENAI_API_KEY` | `gpt-4-turbo-preview` | 性能强大，支持多语言 |
| **通义千问** | `DASHSCOPE_API_KEY` | `qwen-max` | 阿里，中文优秀 |
| **智谱AI** | `ZHIPU_API_KEY` | `glm-4` | 清华，中文优秀 |
| **Moonshot** | `MOONSHOT_API_KEY` | `moonshot-v1-8k` | Kimi，长文本 |
| **Claude** | `ANTHROPIC_API_KEY` | `claude-3-opus` | Anthropic，安全性高 |

### 如何获取API密钥

#### 1. 火山引擎方舟
- 访问：[https://console.volcengine.com/ark](https://console.volcengine.com/ark)
- 注册账号 → API密钥管理 → 创建密钥

#### 2. OpenAI
- 访问：[https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- 需要有国际信用卡

#### 3. 通义千问
- 访问：[https://dashscope.console.aliyun.com/](https://dashscope.console.aliyun.com/)
- 支付宝实名认证 → 创建API密钥
- **新用户有免费额度**

#### 4. 智谱AI
- 访问：[https://open.bigmodel.cn/](https://open.bigmodel.cn/)
- 注册 → API密钥管理
- **新用户有免费额度**

#### 5. Moonshot (Kimi)
- 访问：[https://platform.moonshot.cn/](https://platform.moonshot.cn/)
- 注册 → API密钥管理

---

## 四、如何切换模型

### 方法1：修改默认配置（推荐）

在 `.env` 文件中设置：

```env
# 设置默认使用的模型提供商
DEFAULT_LLM_PROVIDER=openai  # 可选: ark, openai, qwen, zhipu, moonshot, claude
```

### 方法2：运行时动态切换

```python
from llm_provider import switch_llm, ChatMessage

# 切换到OpenAI
llm = switch_llm("openai")

# 切换到通义千问
llm = switch_llm("qwen")

# 使用新模型
messages = [ChatMessage(role="user", content="你好")]
response = llm.chat(messages)
```

### 方法3：API请求时指定

```javascript
// 前端请求时指定使用的模型
fetch('/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: 'user123',
    message: '你好',
    model: 'qwen'  // 指定使用通义千问
  })
})
```

---

## 五、代码示例

### 示例1：基本聊天

```python
from llm_provider import get_llm, ChatMessage

# 获取LLM实例
llm = get_llm()

# 准备消息
messages = [
    ChatMessage(role="system", content="你是一个助手"),
    ChatMessage(role="user", content="你好！")
]

# 发送请求
response = llm.chat(messages)

print(f"回复: {response.content}")
print(f"使用模型: {response.model}")
print(f"Token使用: {response.total_tokens}")
```

### 示例2：在RAG中使用

```python
from llm_provider import get_llm, ChatMessage

def rag_query(query, retrieved_docs):
    llm = get_llm()
    
    # 构建RAG prompt
    context = "\n".join(retrieved_docs)
    prompt = f"""基于以下信息回答问题：

信息：
{context}

问题：{query}

回答："""
    
    messages = [
        ChatMessage(role="user", content=prompt)
    ]
    
    response = llm.chat(messages)
    return response.content
```

### 示例3：修改现有代码

**改造前（ys_api_server.py）：**

```python
# 硬编码API密钥和URL
API_KEY = "aea0249a-f824-4caa-8dc1-6ea8e8e96dbd"
API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

# 直接调用requests
response = requests.post(API_URL, headers=headers, json=data)
result = response.json()
reply = result["choices"][0]["message"]["content"]
```

**改造后（使用统一接口）：**

```python
from llm_provider import get_llm, ChatMessage

# 无需硬编码，自动从环境变量读取
llm = get_llm()

# 统一的调用方式
messages = [
    ChatMessage(role="system", content=SYSTEM_PROMPT),
    ChatMessage(role="user", content=message)
]

response = llm.chat(messages)
reply = response.content
```

---

## 六、故障排除

### 问题1：API密钥无效

**错误信息**：
```
错误: API密钥未配置
```

**解决方案**：
1. 检查 `.env` 文件是否存在
2. 检查API密钥是否正确填写
3. 检查密钥是否有额度

### 问题2：网络连接失败

**错误信息**：
```
错误: 网络连接失败，请检查网络设置
```

**解决方案**：
1. 检查网络连接
2. 检查API地址是否正确
3. 检查是否需要代理（某些地区访问境外API需要）

### 问题3：模型不支持

**错误信息**：
```
错误: 不支持的模型提供商: xxx
```

**解决方案**：
1. 检查拼写是否正确（ark/openai/qwen/zhipu/moonshot/claude）
2. 在 `config.py` 中添加新模型的支持

### 问题4：响应格式异常

**错误信息**：
```
错误: 响应格式异常
```

**解决方案**：
1. 检查模型是否正常工作
2. 查看原始响应内容排查问题
3. 某些模型可能有特殊的响应格式，需要修改适配器

---

## 七、高级功能

### 添加新的模型提供商

假设要添加新的模型提供商 `custom_ai`：

1. **在 `config.py` 中添加配置：**

```python
CUSTOM_AI_CONFIG = ModelConfig(
    provider="custom_ai",
    model_name=os.getenv("CUSTOM_AI_MODEL", "custom-model"),
    api_key=os.getenv("CUSTOM_AI_API_KEY"),
    api_base=os.getenv("CUSTOM_AI_API_BASE", "https://api.custom.ai/v1"),
    temperature=0.7,
    max_tokens=2048
)

# 在LLMConfigManager的__init__中添加
self.configs["custom_ai"] = CUSTOM_AI_CONFIG
```

2. **在 `llm_provider.py` 中实现适配器：**

```python
class CustomAIProvider(BaseLLMProvider):
    def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        # 实现API调用逻辑
        pass
    
    def generate(self, prompt: str, **kwargs) -> ChatResponse:
        # 实现生成逻辑
        pass

# 在LLMFactory._providers中添加
_providers = {
    # ... 其他提供商
    "custom_ai": CustomAIProvider,
}
```

3. **在 `.env` 中添加配置：**

```env
CUSTOM_AI_API_KEY=your_key_here
CUSTOM_AI_MODEL=custom-model
```

### 实现流式输出

流式输出需要修改适配器以支持流式API：

```python
class ArkProvider(BaseLLMProvider):
    def chat_stream(self, messages: List[ChatMessage], **kwargs):
        """流式输出"""
        # 设置 stream=True
        data["stream"] = True
        
        response = requests.post(
            url,
            headers=self.headers,
            json=data,
            stream=True  # 重要：启用流式
        )
        
        for line in response.iter_lines():
            if line:
                yield line.decode('utf-8')
```

### 成本监控

可以在 `ChatResponse` 中记录token使用量：

```python
class CostTracker:
    # 各模型的单价（美元/1K tokens）
    PRICES = {
        "ark": {"input": 0.001, "output": 0.002},
        "openai-gpt4": {"input": 0.03, "output": 0.06},
        "qwen": {"input": 0.0008, "output": 0.002},
    }
    
    @classmethod
    def calculate_cost(cls, provider, tokens):
        prices = cls.PRICES.get(provider, {})
        return (
            tokens.get("prompt", 0) / 1000 * prices.get("input", 0) +
            tokens.get("completion", 0) / 1000 * prices.get("output", 0)
        )
```

---

## 八、最佳实践

### 1. 生产环境配置

```python
# 设置环境变量
export FLASK_DEBUG=False
export DEFAULT_LLM_PROVIDER=ark
export ARK_API_KEY=your_production_key
```

### 2. 错误处理和降级

```python
def chat_with_fallback(message):
    """主模型失败时自动降级到备用模型"""
    providers = ['ark', 'qwen', 'zhipu']  # 优先级顺序
    
    for provider in providers:
        try:
            llm = get_llm(provider)
            response = llm.generate(message)
            return response.content
        except Exception as e:
            print(f"{provider} 失败: {e}")
            continue
    
    return "抱歉，所有模型都无法响应，请稍后重试"
```

### 3. 缓存优化

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_llm_query(prompt, provider):
    """缓存LLM查询结果"""
    llm = get_llm(provider)
    response = llm.generate(prompt)
    return response.content
```

### 4. 并发控制

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=5)

def async_chat(messages, provider):
    """异步调用LLM"""
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(executor, lambda: get_llm(provider).chat(messages))
```

---

## 九、总结

### 优势

✅ **统一管理**：所有API密钥在 `.env` 中集中管理  
✅ **灵活切换**：一行代码切换不同模型  
✅ **易于扩展**：新增模型只需实现适配器  
✅ **类型安全**：使用dataclass和类型注解  
✅ **错误处理**：统一的异常处理机制  

### 下一步

1. ✅ 复制 `.env.template` 到 `.env`
2. ✅ 填写你的API密钥
3. ✅ 运行 `python llm_demo.py` 测试
4. ✅ 修改现有代码使用新接口
5. ✅ 根据需要添加更多模型支持

---

**文档版本**: 1.0  
**最后更新**: 2026年3月19日  
**维护者**: 颍上小智开发团队
