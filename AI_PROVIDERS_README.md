# AI 提供商配置指南

轮回系统支持多个 AI 提供商，可以在 Web 面板中轻松配置和切换。

## 支持的 AI 提供商

### 1. Claude (CLI) - 默认

使用 Anthropic 官方的 Claude CLI 工具。

**优点：**
- 无需 API 密钥配置
- 官方支持，稳定可靠
- 支持所有 Claude 模型

**使用前准备：**
```bash
# 安装 Claude CLI
npm install -g @anthropic-ai/claude-code

# 登录
claude login
```

**配置：**
- 无需额外配置，安装后即可使用

---

### 2. OpenAI GPT

使用 OpenAI 官方 API。

**支持模型：**
- GPT-4
- GPT-4 Turbo
- GPT-3.5 Turbo

**配置步骤：**

1. **获取 API 密钥**
   - 访问：https://platform.openai.com/api-keys
   - 创建新的 API 密钥

2. **安装依赖**
   ```bash
   pip install openai
   ```

3. **在 Web 面板配置**
   - 打开"AI 配置"标签页
   - 找到"OpenAI GPT"卡片
   - 在配置框中输入：
     ```
     API_KEY=sk-xxxxxxxxxxxxxxxxxx
     MODEL=gpt-4
     ```

   或者使用命令行：
   ```bash
   python3 ai_providers.py --test openai
   ```

**高级配置：**
```
API_KEY=sk-xxxxxxxxxxxxxxxxxx
MODEL=gpt-4
TEMPERATURE=0.7
MAX_TOKENS=4096
```

---

### 3. OpenAI 兼容 API

使用任何兼容 OpenAI API 格式的服务。

**适用场景：**
- Azure OpenAI
- 本地部署的模型（如 vLLM、Text Generation WebUI）
- 第三方 API 服务

**配置示例：**

Azure OpenAI:
```
API_KEY=xxxxxxxxxxxxxxxxxx
BASE_URL=https://your-resource.openai.azure.com
MODEL=gpt-4
```

本地 vLLM:
```
API_KEY=dummy
BASE_URL=http://localhost:8000/v1
MODEL=meta-llama/Llama-2-70b-chat-hf
```

---

### 4. Ollama (本地模型)

使用 Ollama 运行本地开源模型。

**优点：**
- 完全本地运行，无需联网
- 支持多种开源模型
- 隐私安全

**安装 Ollama：**

macOS/Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

Windows:
- 下载：https://ollama.ai/download

**拉取模型：**
```bash
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

**配置：**
```
BASE_URL=http://localhost:11434
MODEL=llama2
```

**启动 Ollama：**
```bash
ollama serve
```

---

## Web 面板配置

### 1. 启动 Web 面板

```bash
./run_web.sh
```

### 2. 打开 AI 配置页面

在浏览器中访问 http://localhost:5000，点击"AI 配置"标签页。

### 3. 配置提供商

每个提供商卡片包含：

#### 启用/禁用
- 勾选"启用此提供商"来激活该提供商

#### API 密钥 / 配置
- 输入配置信息（格式：`KEY=VALUE`）
- 不同配置项换行分隔

#### 测试按钮
- 点击"🧪 测试"检查连接状态
- 显示提供商名称、描述和可用状态

#### 设为默认
- 点击"⭐ 设为默认"设置该提供商为默认选项
- 代理启动时会使用默认提供商

### 4. 保存配置

配置完成后，点击页面顶部的"💾 保存配置"按钮。

---

## 命令行使用

### 使用指定 AI 提供商启动代理

```bash
# 使用 Claude (默认)
./run_reflective.sh

# 使用 OpenAI
python3 reflective_agent.py --ai openai

# 使用 Ollama
python3 reflective_agent.py --ai ollama

# 使用 OpenAI 兼容 API
python3 reflective_agent.py --ai openai_compatible
```

### 测试提供商

```bash
python3 ai_providers.py --test openai
python3 ai_providers.py --test ollama
```

### 列出所有提供商

```bash
python3 ai_providers.py --list
```

---

## 配置文件格式

AI 配置存储在 `ai_config.json`（已加入 .gitignore）：

```json
{
  "default_provider": "claude",
  "providers": {
    "claude": {
      "enabled": true
    },
    "openai": {
      "enabled": true,
      "api_key": "sk-xxxxxxxxxxxxxxxxxx",
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 4096
    },
    "ollama": {
      "enabled": true,
      "base_url": "http://localhost:11434",
      "model": "llama2"
    },
    "openai_compatible": {
      "enabled": false,
      "api_key": "",
      "base_url": "",
      "model": "gpt-3.5-turbo"
    }
  }
}
```

---

## 添加新的 AI 提供商

### 1. 创建提供商类

在 `ai_providers.py` 中添加新的提供商类：

```python
class MyCustomProvider(AIProvider):
    def get_name(self) -> str:
        return "My Custom AI"

    def get_description(self) -> str:
        return "自定义 AI 提供商"

    def generate(self, prompt: str, timeout: int = 600) -> str:
        # 实现 API 调用逻辑
        pass

    def is_available(self) -> bool:
        # 检查可用性
        pass
```

### 2. 注册提供商

在 `AIProviderFactory._providers` 中添加：

```python
_providers = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "my_custom": MyCustomProvider,  # 新增
}
```

### 3. 更新配置模板

在 `APIKeyManager.__init__` 的默认配置中添加：

```python
"my_custom": {
    "enabled": False,
    "api_key": "",
    "model": "custom-model"
}
```

---

## 性能对比

| 提供商 | 响应速度 | 质量 | 成本 | 离线使用 |
|--------|---------|------|------|---------|
| Claude CLI | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 按使用计费 | ❌ |
| OpenAI GPT | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 按使用计费 | ❌ |
| OpenAI 兼容 | ⭐⭐⭐ | ⭐⭐⭐ | 取决于部署 | ✅ |
| Ollama | ⭐⭐ | ⭐⭐⭐ | 免费 | ✅ |

---

## 常见问题

### Q: 如何切换 AI 提供商？

A: 在 Web 面板的"AI 配置"标签页中，点击提供商卡片上的"⭐ 设为默认"按钮，然后保存配置。

### Q: API 密钥存储在哪里？

A: 存储在 `ai_config.json` 文件中（已加入 .gitignore，不会被提交到 Git）。

### Q: 可以同时使用多个提供商吗？

A: 当前版本一次只能使用一个提供商。但你可以随时切换不同提供商来对比效果。

### Q: 本地模型需要什么配置？

A: 推荐 16GB+ 内存的机器。使用 Ollama 或 vLLM 部署。

### Q: 如何查看代理使用的提供商？

A: 代理启动时会在日志中显示使用的提供商。你也可以查看生命目录中的 `diary.jsonl` 文件。

---

## 安全建议

1. **不要分享 API 密钥**
   - `ai_config.json` 已加入 .gitignore
   - 不要将密钥提交到版本控制系统

2. **使用环境变量（可选）**
   ```bash
   export OPENAI_API_KEY="sk-xxxxxxxx"
   export ANTHROPIC_API_KEY="sk-ant-xxxxxxxx"
   ```

3. **定期轮换密钥**
   - 定期更换 API 密钥
   - 监控 API 使用量

4. **限制 API 权限**
   - 只授予必要的权限
   - 设置使用限额

---

享受多 AI 提供商的灵活性！🚀
