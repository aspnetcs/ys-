"""
统一LLM接口层
支持多种模型提供商（OpenAI、Claude、通义千问、火山引擎等）
"""
import os
import json
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from config import config_manager, ModelConfig


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system, user, assistant
    content: str
    name: Optional[str] = None


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    provider: str
    total_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    finish_reason: Optional[str] = None


class BaseLLMProvider(ABC):
    """LLM提供商基类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model_name = config.model_name
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self.timeout = config.timeout
    
    @abstractmethod
    def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """发送聊天请求"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> ChatResponse:
        """文本生成"""
        pass
    
    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """获取文本embedding（可选实现）"""
        raise NotImplementedError("该提供商不支持embedding")


class ArkProvider(BaseLLMProvider):
    """火山引擎方舟大模型"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.api_base = config.api_base
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """发送聊天请求"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        data = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"API错误 (状态码 {response.status_code}): {response.text[:200]}")
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0]["message"]
                return ChatResponse(
                    content=message["content"],
                    model=result.get("model", self.model_name),
                    provider="ark",
                    total_tokens=result.get("usage", {}).get("total_tokens"),
                    prompt_tokens=result.get("usage", {}).get("prompt_tokens"),
                    completion_tokens=result.get("usage", {}).get("completion_tokens"),
                    finish_reason=result["choices"][0].get("finish_reason")
                )
            elif "error" in result:
                raise Exception(f"API错误: {result['error'].get('message', str(result['error']))}")
            else:
                raise Exception(f"响应格式异常: {response.text[:200]}")
        
        except requests.exceptions.Timeout:
            raise Exception("请求超时，请稍后重试")
        except requests.exceptions.ConnectionError:
            raise Exception("网络连接失败，请检查网络设置")
        except Exception as e:
            raise Exception(f"请求失败: {str(e)}")
    
    def generate(self, prompt: str, **kwargs) -> ChatResponse:
        """文本生成"""
        messages = [
            ChatMessage(role="user", content=prompt)
        ]
        return self.chat(messages, **kwargs)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT模型"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.api_base = config.api_base or "https://api.openai.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """发送聊天请求"""
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        data = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"API错误 (状态码 {response.status_code}): {response.text[:200]}")
            
            result = response.json()
            
            return ChatResponse(
                content=result["choices"][0]["message"]["content"],
                model=result.get("model", self.model_name),
                provider="openai",
                total_tokens=result.get("usage", {}).get("total_tokens"),
                prompt_tokens=result.get("usage", {}).get("prompt_tokens"),
                completion_tokens=result.get("usage", {}).get("completion_tokens"),
                finish_reason=result["choices"][0].get("finish_reason")
            )
        
        except Exception as e:
            raise Exception(f"OpenAI API调用失败: {str(e)}")
    
    def generate(self, prompt: str, **kwargs) -> ChatResponse:
        """文本生成"""
        messages = [
            ChatMessage(role="user", content=prompt)
        ]
        return self.chat(messages, **kwargs)
    
    def get_embedding(self, text: str, **kwargs) -> List[float]:
        """获取文本embedding"""
        data = {
            "model": kwargs.get("embedding_model", "text-embedding-ada-002"),
            "input": text
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/embeddings",
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Embedding API错误: {response.text[:200]}")
            
            result = response.json()
            return result["data"][0]["embedding"]
        except Exception as e:
            raise Exception(f"获取embedding失败: {str(e)}")


class QwenProvider(BaseLLMProvider):
    """通义千问 (阿里云)"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.api_base = config.api_base or "https://dashscope.aliyuncs.com/api/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """发送聊天请求"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        data = {
            "model": self.model_name,
            "input": {
                "messages": formatted_messages
            },
            "parameters": {
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }
        }
        
        if "top_p" in kwargs:
            data["parameters"]["top_p"] = kwargs["top_p"]
        
        try:
            response = requests.post(
                f"{self.api_base}/services/aigc/text-generation/generation",
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"API错误 (状态码 {response.status_code}): {response.text[:200]}")
            
            result = response.json()
            
            if "output" in result and "choices" in result["output"]:
                choice = result["output"]["choices"][0]
                return ChatResponse(
                    content=choice["message"]["content"],
                    model=result.get("model", self.model_name),
                    provider="qwen",
                    total_tokens=result.get("usage", {}).get("total_tokens"),
                    prompt_tokens=result.get("usage", {}).get("input_tokens"),
                    completion_tokens=result.get("usage", {}).get("output_tokens")
                )
            elif "error" in result:
                raise Exception(f"API错误: {result['error'].get('message', str(result['error']))}")
            else:
                raise Exception(f"响应格式异常: {response.text[:200]}")
        
        except Exception as e:
            raise Exception(f"通义千问API调用失败: {str(e)}")
    
    def generate(self, prompt: str, **kwargs) -> ChatResponse:
        """文本生成"""
        messages = [
            ChatMessage(role="user", content=prompt)
        ]
        return self.chat(messages, **kwargs)


class ZhipuProvider(BaseLLMProvider):
    """智谱AI (ChatGLM)"""
    
    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.api_key = config.api_key
        self.api_base = config.api_base or "https://open.bigmodel.cn/api/paas/v4"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def chat(self, messages: List[ChatMessage], **kwargs) -> ChatResponse:
        """发送聊天请求"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        data = {
            "model": self.model_name,
            "messages": formatted_messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
        }
        
        if "top_p" in kwargs:
            data["top_p"] = kwargs["top_p"]
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"API错误 (状态码 {response.status_code}): {response.text[:200]}")
            
            result = response.json()
            
            return ChatResponse(
                content=result["choices"][0]["message"]["content"],
                model=result.get("model", self.model_name),
                provider="zhipu",
                total_tokens=result.get("usage", {}).get("total_tokens"),
                prompt_tokens=result.get("usage", {}).get("prompt_tokens"),
                completion_tokens=result.get("usage", {}).get("completion_tokens"),
                finish_reason=result["choices"][0].get("finish_reason")
            )
        
        except Exception as e:
            raise Exception(f"智谱AI API调用失败: {str(e)}")
    
    def generate(self, prompt: str, **kwargs) -> ChatResponse:
        """文本生成"""
        messages = [
            ChatMessage(role="user", content=prompt)
        ]
        return self.chat(messages, **kwargs)


# ==================== LLM工厂类 ====================

class LLMFactory:
    """LLM工厂类，用于创建不同的LLM提供商实例"""
    
    _providers = {
        "ark": ArkProvider,
        "openai": OpenAIProvider,
        "qwen": QwenProvider,
        "zhipu": ZhipuProvider,
        "moonshot": OpenAIProvider,  # Moonshot兼容OpenAI API
    }
    
    @classmethod
    def create_provider(cls, provider_name: str = None) -> BaseLLMProvider:
        """创建LLM提供商实例"""
        config = config_manager.get_config(provider_name)
        
        if config.provider not in cls._providers:
            raise ValueError(f"不支持的模型提供商: {config.provider}")
        
        provider_class = cls._providers[config.provider]
        return provider_class(config)
    
    @classmethod
    def list_providers(cls) -> list:
        """列出所有支持的提供商"""
        return list(cls._providers.keys())


# 全局LLM实例（单例模式）
_llm_instance = None


def get_llm(provider: str = None) -> BaseLLMProvider:
    """获取LLM实例（全局单例）"""
    global _llm_instance
    
    if _llm_instance is None:
        _llm_instance = LLMFactory.create_provider(provider)
    
    return _llm_instance


def switch_llm(provider: str) -> BaseLLMProvider:
    """切换LLM提供商"""
    global _llm_instance
    
    _llm_instance = LLMFactory.create_provider(provider)
    return _llm_instance
