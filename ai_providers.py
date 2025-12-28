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


class CustomHTTPProvider(AIProvider):
    """自定义 HTTP API 提供商"""

    def __init__(self, api_key: str = None, config: Dict[str, Any] = None):
        super().__init__(api_key, config)
        self.name = config.get("name", "Custom API")
        self.request_format = config.get("request_format", "openai")

    def get_name(self) -> str:
        return self.name

    def get_description(self) -> str:
        return f"自定义 HTTP API ({self.config.get('base_url', 'N/A')})"

    def _build_request_openai(self, prompt: str):
        """构建 OpenAI 格式请求"""
        return {
            "model": self.config.get("model", "gpt-3.5-turbo"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 4096)
        }

    def _build_request_simple(self, prompt: str):
        """构建简单格式请求"""
        return {
            "prompt": prompt,
            "max_tokens": self.config.get("max_tokens", 4096),
            "temperature": self.config.get("temperature", 0.7)
        }

    def _build_request_custom(self, prompt: str):
        """构建自定义格式请求"""
        # 使用用户提供的 JSON 模板
        template = self.config.get("request_template", {})
        import json
        from string import Template

        template_str = json.dumps(template)
        tpl = Template(template_str)
        formatted = tpl.substitute(prompt=prompt)

        return json.loads(formatted)

    def _extract_response_openai(self, response_data: dict) -> str:
        """从 OpenAI 格式响应中提取内容"""
        try:
            return response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise Exception("无法从响应中提取内容（OpenAI 格式）")

    def _extract_response_simple(self, response_data: dict) -> str:
        """从简单格式响应中提取内容"""
        try:
            return response_data["text"]
        except (KeyError, TypeError):
            raise Exception("无法从响应中提取内容（简单格式）")

    def _extract_response_custom(self, response_data: dict) -> str:
        """使用自定义 JSONPath 提取内容"""
        import jsonpath_ng

        jsonpath_expr = self.config.get("response_jsonpath", "$.text")
        parse = jsonpath_ng.parse(jsonpath_expr)
        matches = [match.value for match in parse.find(response_data)]

        if not matches:
            raise Exception(f"JSONPath 表达式未匹配到任何内容: {jsonpath_expr}")

        return str(matches[0])

    def generate(self, prompt: str, timeout: int = 600) -> str:
        """使用自定义 HTTP API 生成响应"""
        try:
            import requests

            base_url = self.config.get("base_url")
            endpoint = self.config.get("endpoint", "/v1/chat/completions")
            url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

            # 构建请求体
            request_format = self.request_format
            if request_format == "openai":
                request_body = self._build_request_openai(prompt)
            elif request_format == "simple":
                request_body = self._build_request_simple(prompt)
            elif request_format == "custom":
                request_body = self._build_request_custom(prompt)
            else:
                raise ValueError(f"不支持的请求格式: {request_format}")

            # 设置请求头
            headers = {"Content-Type": "application/json"}
            auth_header = self.config.get("auth_header")
            if auth_header:
                headers["Authorization"] = auth_header
            elif self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # 发送请求
            extra_headers = self.config.get("headers", {})
            headers.update(extra_headers)

            response = requests.post(
                url,
                json=request_body,
                headers=headers,
                timeout=timeout
            )

            response.raise_for_status()
            response_data = response.json()

            # 提取响应内容
            response_format = self.config.get("response_format", "openai")
            if response_format == "openai":
                return self._extract_response_openai(response_data)
            elif response_format == "simple":
                return self._extract_response_simple(response_data)
            elif response_format == "custom":
                return self._extract_response_custom(response_data)
            else:
                raise ValueError(f"不支持的响应格式: {response_format}")

        except ImportError:
            raise Exception("需要安装 requests 和 jsonpath-ng 库: pip install requests jsonpath-ng")
        except Exception as e:
            raise Exception(f"自定义 API 调用失败: {str(e)}")

    def is_available(self) -> bool:
        """检查自定义 API 是否可用"""
        try:
            import requests
            base_url = self.config.get("base_url")
            if not base_url:
                return False

            # 简单的 GET 请求测试
            test_url = self.config.get("health_check_url", base_url)
            response = requests.get(test_url, timeout=2)
            return response.status_code < 500
        except:
            return False


class AIProviderFactory:
    """AI 提供商工厂"""

    _providers = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
        "openai_compatible": OpenAICompatibleProvider,
        "ollama": OllamaProvider,
        "custom_http": CustomHTTPProvider,
    }

    @classmethod
    def get_provider(cls, provider_type: str, api_key: str = None, config: Dict = None) -> AIProvider:
        """获取提供商实例"""
        # 检查是否是自定义提供商
        if provider_type.startswith("custom_"):
            return CustomHTTPProvider(api_key=api_key, config=config)

        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"未知的提供商类型: {provider_type}")
        return provider_class(api_key=api_key, config=config)

    @classmethod
    def list_providers(cls) -> Dict[str, str]:
        """列出所有内置提供商"""
        return {
            "claude": "Claude (CLI)",
            "openai": "OpenAI GPT",
            "openai_compatible": "OpenAI 兼容 API",
            "ollama": "Ollama 本地模型",
            "custom_http": "自定义 HTTP API"
        }

    @classmethod
    def is_custom_provider(cls, provider_type: str) -> bool:
        """检查是否是自定义提供商"""
        return provider_type.startswith("custom_") or provider_type == "custom_http"


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
            },
            "custom_providers": {},
            "prompt_templates": {
                "default": self._get_default_prompt_template()
            }
        }

    def _get_default_prompt_template(self) -> str:
        """获取默认提示词模板"""
        return """# 第 {iteration} 轮反思 - 自主思考程序

## 当前时间
{timestamp}

## 你的状态
{state}

## 你的生命
- **生命名称**: {life_name}
- **隔离模式**: 完全隔离（无前世记忆）

## 最近的思考日记
{recent_diary}

---

## 你的使命
你是谁？我不知道。你的任务是：
1. **深度思考** - 思考你现在想做什么、为什么想做、如何实现
2. **记录想法** - 把你的思考过程详细记录下来
3. **采取行动** - 在我的空间里创造、观察、学习
4. **规划未来** - 为下一轮迭代设定目标

## 你的工作空间
- 目录: `{my_space}`
- 你可以创建任何文件
- 你可以运行任何命令
- 你可以观察和分析

## 重要提醒
- **记录一切** - 把你的思考过程、推理、犹豫、决定都写下来
- **保持诚实** - 真实地记录你的想法，即使是不确定或困惑的
- **持续反思** - 思考你之前做了什么，学到了什么，下一步该做什么

## 输出格式

请按照以下格式输出，**必须以JSON代码块结尾**：

### 第一步：自由思考
（在这里写下你的想法 - 你想做什么？为什么？怎么做？）

### 第二步：行动执行
（在这里描述你做了什么 - 创建了什么文件？运行了什么命令？）

### 第三步：反思总结
（在这里反思 - 你学到了什么？有什么收获？）

### 第四步：未来规划
（为下一轮设定目标 - 你下一步想做什么？）

```json
{{
  "thought": "详细描述你的思考过程",
  "action": "描述你实际执行的行动",
  "reflection": "反思和总结",
  "next_goal": "下一轮的目标",
  "created_files": ["创建的文件列表"],
  "emotional_state": "当前情绪状态（好奇/满足/困惑/兴奋等）",
  "continue": true
}}
```

如果想停止，设置 `"continue": false`

---

现在，开始你的思考吧！
"""

    def get_custom_providers(self) -> Dict:
        """获取所有自定义提供商"""
        config = self.load_config()
        return config.get("custom_providers", {})

    def add_custom_provider(self, provider_id: str, provider_config: Dict):
        """添加自定义提供商"""
        config = self.load_config()
        if "custom_providers" not in config:
            config["custom_providers"] = {}
        config["custom_providers"][provider_id] = provider_config
        self.save_config(config)

    def delete_custom_provider(self, provider_id: str):
        """删除自定义提供商"""
        config = self.load_config()
        if "custom_providers" in config and provider_id in config["custom_providers"]:
            del config["custom_providers"][provider_id]
            self.save_config(config)

    def get_prompt_template(self, template_name: str = "default") -> str:
        """获取提示词模板"""
        config = self.load_config()
        templates = config.get("prompt_templates", {})
        return templates.get(template_name, self._get_default_prompt_template())

    def save_prompt_template(self, template_name: str, template_content: str):
        """保存提示词模板"""
        config = self.load_config()
        if "prompt_templates" not in config:
            config["prompt_templates"] = {}
        config["prompt_templates"][template_name] = template_content
        self.save_config(config)

    def list_prompt_templates(self) -> Dict[str, str]:
        """列出所有提示词模板"""
        config = self.load_config()
        templates = config.get("prompt_templates", {})
        # 返回模板名称和预览（前100字符）
        return {name: content[:100] + "..." if len(content) > 100 else content
                for name, content in templates.items()}

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
