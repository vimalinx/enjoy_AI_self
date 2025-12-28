# Web 面板使用指南

## 概述

轮回系统提供了一个现代化的 Web 面板，让你可以通过浏览器直观地管理和查看所有生命。

## 启动方式

### 方式 1：使用主脚本

```bash
./run_reflective.sh web [host] [port]
```

### 方式 2：使用专用脚本（推荐）

```bash
./run_web.sh [host] [port]
```

### 示例

```bash
# 默认配置（localhost:5000）
./run_web.sh

# 允许外部访问（局域网内其他设备可访问）
./run_web.sh 0.0.0.0 5000

# 自定义端口
./run_web.sh 127.0.0.1 8080
```

## 功能说明

### 1. 生命列表页面

这是默认页面，展示所有生命的卡片式视图。

**功能：**
- 📊 **统计卡片**：顶部显示总生命数、总迭代次数等
- 🎴 **生命卡片**：每个生命显示：
  - 生命名称和编号
  - 当前生命标识（蓝色边框 + "当前" 徽章）
  - 迭代、思考、行动次数
  - 日记条数
  - 创建时间
- ➕ **创建生命**：点击按钮创建新生命
- 🔄 **刷新**：重新加载所有数据

**交互：**
- 点击任意生命卡片打开详情模态框

### 2. 轮回统计页面

显示跨所有生命的累计统计。

**统计指标：**
- 总生命数
- 总迭代次数
- 总思考次数
- 总行动次数
- 总日记条数
- 平均迭代次数
- 最长生命
- 最短生命
- 当前生命

### 3. 生命对比页面

对比多个生命的差异。

**使用步骤：**
1. 勾选要对比的生命（至少 2 个）
2. 点击"对比选中生命"按钮
3. 查看对比结果表格

**对比指标：**
- 迭代次数
- 思考次数
- 行动次数
- 目标数量
- 成就数量
- 日记条数

### 4. 生命详情模态框

点击生命卡片后打开，显示完整的生命信息。

**显示内容：**
- **基本信息**：编号、创建时间、状态、隔离模式
- **统计数据**：迭代、思考、行动、日记数
- **最近目标**：最多显示 5 个
- **最近成就**：最多显示 5 个
- **最近日记**：点击"加载日记"按钮查看

**操作按钮：**
- 📝 **加载日记**：查看最近 20 条日记
- 🔄 **切换到此生命**：将当前生命切换为选中的生命
- ❌ **关闭**：关闭模态框

## 日记展示

日记条目包含：
- **阶段徽章**：彩色标签显示阶段（思考、行动、反思等）
- **摘要**：简短描述
- **时间戳**：精确时间
- **详细信息**（展开显示）：
  - 思考内容
  - 执行的行动
  - 反思总结
  - 下一步目标

## 阶段颜色说明

| 阶段 | 颜色 | 说明 |
|------|------|------|
| THINKING | 蓝色 | 思考阶段 |
| ACTION | 橙色 | 行动阶段 |
| REFLECTION | 绿色 | 反思阶段 |
| ERROR | 红色 | 错误 |
| ITERATION_START | 紫色 | 迭代开始 |
| ITERATION_END | 青色 | 迭代结束 |

## API 端点

Web 面板使用以下 RESTful API：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/lives` | GET | 获取所有生命 |
| `/api/lives/<name>` | GET | 获取生命详情 |
| `/api/lives/<name>/diary` | GET | 获取生命日记 |
| `/api/lives/<name>/state` | GET | 获取生命状态 |
| `/api/lives/create` | POST | 创建新生命 |
| `/api/lives/<name>/switch` | POST | 切换生命 |
| `/api/stats` | GET | 轮回统计 |
| `/api/compare` | POST | 对比生命 |

## 响应式设计

Web 面板完全响应式，支持：
- 💻 桌面浏览器（最佳体验）
- 📱 平板设备
- 📲 手机设备

移动端会自动调整为单列布局。

## 浏览器兼容性

支持所有现代浏览器：
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## 安全建议

1. **本地使用**：默认 `127.0.0.1` 仅允许本机访问
2. **局域网访问**：使用 `0.0.0.0` 时注意网络安全
3. **生产环境**：建议配置反向代理（如 Nginx）并启用 HTTPS

## 故障排除

### 端口被占用

```
Error: [Errno 98] Address already in use
```

**解决方案**：使用其他端口
```bash
./run_web.sh 127.0.0.1 8080
```

### Flask 未安装

```
ModuleNotFoundError: No module named 'flask'
```

**解决方案**：安装 Flask
```bash
pip3 install flask
```

### 无法访问面板

检查防火墙设置：
```bash
# Linux (ufw)
sudo ufw allow 5000

# Linux (firewalld)
sudo firewall-cmd --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

## 高级用法

### 后台运行

```bash
nohup ./run_web.sh 0.0.0.0 5000 > web.log 2>&1 &
```

### 开机自启动（systemd）

创建服务文件 `/etc/systemd/system/reincarnation-web.service`：

```ini
[Unit]
Description=Reincarnation System Web Dashboard
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/enjoy_your_self
ExecStart=/usr/bin/python3 /path/to/enjoy_your_self/web_dashboard.py --host 0.0.0.0 --port 5000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable reincarnation-web
sudo systemctl start reincarnation-web
```

## 开发模式

启动调试模式（自动重载）：
```bash
python3 web_dashboard.py --debug
```

## 实时更新

当前版本需要手动刷新数据。未来版本可能添加：
- WebSocket 实时推送
- 自动轮询更新
- 代理运行时实时流式显示

---

享受可视化的轮回管理体验！ 🎉
