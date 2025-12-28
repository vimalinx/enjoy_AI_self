#!/bin/bash
# 反思型自主代理系统启动脚本

WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORK_DIR"

echo "================================"
echo "反思型自主代理系统"
echo "================================"
echo ""
echo "工作目录: $WORK_DIR"
echo ""

# 创建必要的目录
mkdir -p my_space lives

# PID 文件
AGENT_PID_FILE="$WORK_DIR/.agent.pid"
OBSERVER_PID_FILE="$WORK_DIR/.observer.pid"

# 停止已运行的进程
stop() {
    if [ -f "$AGENT_PID_FILE" ]; then
        AGENT_PID=$(cat "$AGENT_PID_FILE")
        if ps -p "$AGENT_PID" > /dev/null 2>&1; then
            echo "停止代理进程 (PID: $AGENT_PID)..."
            kill "$AGENT_PID"
        fi
        rm -f "$AGENT_PID_FILE"
    fi

    if [ -f "$OBSERVER_PID_FILE" ]; then
        OBSERVER_PID=$(cat "$OBSERVER_PID_FILE")
        if ps -p "$OBSERVER_PID" > /dev/null 2>&1; then
            echo "停止观察者进程 (PID: $OBSERVER_PID)..."
            kill "$OBSERVER_PID"
        fi
        rm -f "$OBSERVER_PID_FILE"
    fi

    echo "所有进程已停止"
}

# 捕获退出信号
trap stop EXIT INT TERM

# 检查参数
MODE=${1:-"run"}

if [ "$MODE" = "stop" ]; then
    stop
    trap - EXIT INT TERM
    exit 0
fi

if [ "$MODE" = "watch" ]; then
    echo "仅启动观察者..."
    python3 observer.py
    exit 0
fi

if [ "$MODE" = "replay" ]; then
    echo "回放日记..."
    python3 observer.py --replay --limit "${2:-50}"
    exit 0
fi

# 轮回管理命令
if [ "$MODE" = "reincarnate" ]; then
    echo "轮回：创建新生命..."
    python3 reincarnation_manager.py create ${2:+--name "$2"}
    exit 0
fi

if [ "$MODE" = "lives" ]; then
    python3 reincarnation_manager.py list
    exit 0
fi

if [ "$MODE" = "show-life" ]; then
    python3 reincarnation_manager.py show "${2:-life_001}"
    exit 0
fi

if [ "$MODE" = "switch-life" ]; then
    python3 reincarnation_manager.py switch "${2:-life_001}"
    exit 0
fi

if [ "$MODE" = "compare" ]; then
    shift
    python3 reincarnation_manager.py compare "$@"
    exit 0
fi

if [ "$MODE" = "stats" ]; then
    python3 reincarnation_manager.py stats
    exit 0
fi

if [ "$MODE" = "life-diary" ]; then
    python3 reincarnation_manager.py diary "${2:-life_001}" ${3:+--limit "$3"}
    exit 0
fi

# Web 面板命令
if [ "$MODE" = "web" ]; then
    echo "启动 Web 面板..."
    python3 web_dashboard.py ${2:+--host "$2"} ${3:+--port "$3"}
    exit 0
fi

# 检查是否已经在运行
if [ -f "$AGENT_PID_FILE" ] || [ -f "$OBSERVER_PID_FILE" ]; then
    echo "⚠️  系统已在运行"
    echo ""
    echo "控制命令:"
    echo "  - 停止系统: $0 stop"
    echo "  - 仅查看日记: $0 replay [数量]"
    echo "  - 仅启动观察者: $0 watch"
    echo ""
    echo "轮回命令:"
    echo "  - 创建新生命: $0 reincarnate [名称]"
    echo "  - 列出所有生命: $0 lives"
    echo "  - 查看生命详情: $0 show-life [生命名]"
    echo "  - 切换生命: $0 switch-life [生命名]"
    echo "  - 对比生命: $0 compare 生命1 生命2 ..."
    echo "  - 轮回统计: $0 stats"
    echo "  - 查看生命日记: $0 life-diary [生命名] [数量]"
    echo ""
    echo "Web 面板:"
    echo "  - 启动 Web 面板: $0 web [host] [port]"
    exit 1
fi

# 启动代理
echo "启动代理..."
python3 reflective_agent.py ${MAX_ITERATIONS:+"--max-iterations $MAX_ITERATIONS"} > my_space/agent.log 2>&1 &
AGENT_PID=$!
echo "$AGENT_PID" > "$AGENT_PID_FILE"
echo "代理 PID: $AGENT_PID"

# 等待一下确保代理启动
sleep 1

# 检查代理是否运行
if ! ps -p "$AGENT_PID" > /dev/null 2>&1; then
    echo "❌ 代理启动失败"
    rm -f "$AGENT_PID_FILE"
    cat my_space/agent.log
    exit 1
fi

# 启动观察者
echo "启动观察者..."
python3 observer.py &
OBSERVER_PID=$!
echo "$OBSERVER_PID" > "$OBSERVER_PID_FILE"
echo "观察者 PID: $OBSERVER_PID"

echo ""
echo "✅ 系统启动成功"
echo ""
echo "数据文件（位于 my_space/）:"
echo "  - 代理日志: agent.log"
echo "  - 日记文件: diary.jsonl"
echo "  - 状态文件: state.json"
echo ""
echo "控制命令:"
echo "  - 停止系统: $0 stop"
echo "  - 仅查看日记: $0 replay [数量]"
echo "  - 仅启动观察者: $0 watch"
echo ""
echo "轮回命令:"
echo "  - 创建新生命: $0 reincarnate [名称]"
echo "  - 列出所有生命: $0 lives"
echo "  - 查看生命详情: $0 show-life [生命名]"
echo "  - 切换生命: $0 switch-life [生命名]"
echo "  - 对比生命: $0 compare 生命1 生命2 ..."
echo "  - 轮回统计: $0 stats"
echo "  - 查看生命日记: $0 life-diary [生命名] [数量]"
echo ""
echo "Web 面板:"
echo "  - 启动面板: $0 web [host] [port]"
echo "    示例: $0 web 0.0.0.0 5000"
echo ""
echo "按 Ctrl+C 停止"
echo ""

# 等待任意一个进程结束
wait
