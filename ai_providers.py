#!/usr/bin/env python3
"""
AI 提供商抽象层
支持多个 AI 服务：Anthropic Claude、OpenAI GPT、本地模型等
"""

import os
import json
import subprocess
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path


class AIProvider(ABC):
    """AI 提供商基类"""

    def __init__(self, api_key: str = None, config: Dict[str, Any] = None):
        self.api_key = api_key
        self.config = config or {}

    @abstractmethod
    def get_name(self) -> str:
        """获取提供商名称"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """获取提供商描述"""
        pass

    @abstractmethod
    def generate(self, prompt: str, timeout: int = 600) -> str:
        """生成响应"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查是否可用"""
        pass


class ClaudeProvider(AIProvider):
    """Anthropic Claude 提供商（使用 Claude CLI）"""

    def get_name(self) -> str:
        return "Claude (CLI)"

    def get_description(self) -> str:
        return "使用 Claude CLI 工具调用 Anthropic Claude API"

    def generate(self, prompt: str, timeout: int = 600) -> str:
        """使用 Claude CLI 生成响应"""
        try:
            result = subprocess.run(
                ["claude", "--permission-mode", "bypassPermissions"],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            raise Exception("Claude API 调用超时")
        except Exception as e:
            raise Exception(f"Claude API 调用失败: {str(e)}")

    def is_available(self) -> bool:
        """检查 Claude CLI 是否可用"""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False


class OpenAIProvider(AIProvider):
    """OpenAI GPT 提供商"""

    def get_name(self) -> str:
        return "OpenAI GPT"

    def get_description(self) -> str:
        return "使用 OpenAI API (GPT-4, GPT-3.5 等)"

    def generate(self, prompt: str, timeout: int = 600) -> str:
        """使用 OpenAI API 生成响应"""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            model = self.config.get("model", "gpt-4")
            temperature = self.config.get("temperature", 0.7)
            max_tokens = self.config.get("max_tokens", 4096)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            return response.choices[0].message.content

        except ImportError:
            raise Exception("需要安装 openai 库: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI API 调用失败: {str(e)}")

    def is_available(self) -> bool:
        """检查 OpenAI API 是否可用"""
        if not self.api_key:
            return False
        try:
            from openai import OpenAI
            return True
        except:
            return False


class OpenAICompatibleProvider(AIProvider):
    """OpenAI 兼容 API 提供商（如本地模型、第三方API）"""

    def get_name(self) -> str:
        return self.config.get("name", "OpenAI Compatible")

    def get_description(self) -> str:
        base_url = self.config.get("base_url", "N/A")
        return f"OpenAI 兼容 API ({base_url})"

    def generate(self, prompt: str, timeout: int = 600) -> str:
        """使用 OpenAI 兼容 API 生成响应"""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.api_key or "dummy",
                base_url=self.config.get("base_url")
            )

            model = self.config.get("model", "gpt-3.5-turbo")
            temperature = self.config.get("temperature", 0.7)
            max_tokens = self.config.get("max_tokens", 4096)

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            return response.choices[0].message.content

        except ImportError:
            raise Exception("需要安装 openai 库: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI 兼容 API 调用失败: {str(e)}")

    def is_available(self) -> bool:
        """检查是否可用"""
        base_url = self.config.get("base_url")
        if not base_url:
            return False
        try:
            from openai import OpenAI
            return True
        except:
            return False


class OllamaProvider(AIProvider):
    """Ollama 本地模型提供商"""

    def get_name(self) -> str:
        return "Ollama (Local)"

    def get_description(self) -> str:
        return "使用 Ollama 运行本地模型"

    def generate(self, prompt: str, timeout: int = 600) -> str:
        """使用 Ollama 生成响应"""
        try:
            import requests

            base_url = self.config.get("base_url", "http://localhost:11434")
            model = self.config.get("model", "llama2")

            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=timeout
            )

            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

        except ImportError:
            raise Exception("需要安装 requests 库: pip install requests")
        except Exception as e:
            raise Exception(f"Ollama API 调用失败: {str(e)}")

    def is_available(self) -> bool:
        """检查 Ollama 是否可用"""
        try:
            import requests
            base_url = self.config.get("base_url", "http://localhost:11434")
            response = requests.get(f"{base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False


class AIProviderFactory:
    """AI 提供商工厂"""

    _providers = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "openai_compatible": OpenAICompatibleProvider,
        "ollama": OllamaProvider,
    }

    @classmethod
    def get_provider(cls, provider_type: str, api_key: str = None, config: Dict = None) -> AIProvider:
        """获取提供商实例"""
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"未知的提供商类型: {provider_type}")
        return provider_class(api_key=api_key, config=config)

    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        """列出所有提供商"""
        return {
            "claude": "Claude (CLI)",
            "openai": "OpenAI GPT",
            "openai_compatible": "OpenAI 兼容 API",
            "ollama": "Ollama 本地模型"
        }


class APIKeyManager:
    """API 密钥管理器"""

    def __init__(self, work_dir: str = None):
        self.work_dir = Path(work_dir) if work_dir else Path(__file__).parent
        self.config_file = self.work_dir / "ai_config.json"

    def load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text(encoding='utf-8'))
            except:
                pass
        return {
            "default_provider": "claude",
            "providers": {
                "claude": {"enabled": True},
                "openai": {"enabled": False, "api_key": "", "model": "gpt-4"},
                "openai_compatible": {"enabled": False, "api_key": "", "base_url": "", "model": "gpt-3.5-turbo"},
                "ollama": {"enabled": False, "base_url": "http://localhost:11434", "model": "llama2"}
            }
        }

    def save_config(self, config: Dict):
        """保存配置"""
        self.config_file.write_text(
            json.dumps(config, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def get_provider_config(self, provider_type: str) -> Dict:
        """获取特定提供商的配置"""
        config = self.load_config()
        return config.get("providers", {}).get(provider_type, {})

    def update_provider_config(self, provider_type: str, provider_config: Dict):
        """更新提供商配置"""
        config = self.load_config()
        if "providers" not in config:
            config["providers"] = {}
        config["providers"][provider_type] = provider_config
        self.save_config(config)

    def set_default_provider(self, provider_type: str):
        """设置默认提供商"""
        config = self.load_config()
        config["default_provider"] = provider_type
        self.save_config(config)

    def get_default_provider(self) -> str:
        """获取默认提供商"""
        config = self.load_config()
        return config.get("default_provider", "claude")

    def get_enabled_providers(self) -> list:
        """获取已启用的提供商列表"""
        config = self.load_config()
        enabled = []
        for provider_type, provider_config in config.get("providers", {}).items():
            if provider_config.get("enabled", False) or provider_type == "claude":
                enabled.append(provider_type)
        return enabled


def main():
    import argparse

    factory = AIProviderFactory()

    parser = argparse.ArgumentParser(description="AI 提供商管理")
    parser.add_argument("--list", "-l", action="store_true", help="列出所有提供商")
    parser.add_argument("--test", "-t", help="测试提供商")

    args = parser.parse_args()

    if args.list:
        print("可用的 AI 提供商:")
        for key, name in factory.list_providers().items():
            print(f"  - {key}: {name}")

    elif args.test:
        provider = factory.get_provider(args.test)
        print(f"测试提供商: {provider.get_name()}")
        print(f"描述: {provider.get_description()}")
        print(f"可用: {provider.is_available()}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
