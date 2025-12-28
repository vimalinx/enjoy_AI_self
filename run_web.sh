#!/bin/bash
# 快速启动 Web 面板

WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORK_DIR"

HOST=${1:-"127.0.0.1"}
PORT=${2:-5000}

echo "================================"
echo "🌐 轮回系统 Web 面板"
echo "================================"
echo ""
echo "监听地址: http://$HOST:$PORT"
echo ""

if [ "$HOST" = "0.0.0.0" ]; then
    echo "提示: 0.0.0.0 允许外部访问"
    echo "局域网访问: http://$(hostname -I | awk '{print $1}'):$PORT"
    echo ""
fi

echo "按 Ctrl+C 停止"
echo ""

python3 web_dashboard.py --host "$HOST" --port "$PORT"
