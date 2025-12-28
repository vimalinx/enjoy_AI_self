#!/usr/bin/env python3
"""
观察者程序 - 实时监控反思型代理的日记
- 实时读取并输出日记
- 美化显示思考过程
- 追踪代理状态
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional


class Observer:
    """观察者 - 实时监控代理的思考"""

    # 颜色代码
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
    }

    # 阶段图标和颜色
    PHASE_STYLES = {
        "SYSTEM_START": {"icon": "🚀", "color": "green"},
        "ITERATION_START": {"icon": "📍", "color": "blue"},
        "PROMPT_GENERATED": {"icon": "📝", "color": "cyan"},
        "THINKING": {"icon": "🤔", "color": "magenta"},
        "ACTION": {"icon": "⚡", "color": "yellow"},
        "REFLECTION": {"icon": "💡", "color": "green"},
        "NEXT_GOAL": {"icon": "🎯", "color": "blue"},
        "RESPONSE_RECEIVED": {"icon": "📨", "color": "cyan"},
        "ITERATION_END": {"icon": "✅", "color": "green"},
        "ERROR": {"icon": "❌", "color": "red"},
        "SYSTEM_STOP": {"icon": "👋", "color": "yellow"},
    }

    def __init__(self, work_dir: str = None, life_name: str = None):
        self.work_dir = Path(work_dir) if work_dir else Path(__file__).parent
        self.my_space = self.work_dir / "my_space"

        # 如果指定了生命名称，直接使用 lives 目录下的生命
        if life_name:
            self.life_dir = self.work_dir / "lives" / life_name
            if not self.life_dir.exists():
                raise ValueError(f"生命 {life_name} 不存在")
        else:
            # 使用当前生命（my_space 符号链接）
            self.life_dir = self.my_space

        self.diary_file = self.life_dir / "diary.jsonl"
        self.state_file = self.life_dir / "state.json"

        self.last_position = 0
        self.last_iteration = -1

        # 获取生命名称
        self.life_name = life_name
        if self.my_space.is_symlink() and not life_name:
            self.life_name = Path(os.path.realpath(self.my_space)).name

    def colorize(self, text: str, color: str) -> str:
        """给文本添加颜色"""
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"

    def bold(self, text: str) -> str:
        """粗体文本"""
        return f"{self.COLORS['bold']}{text}{self.COLORS['reset']}"

    def dim(self, text: str) -> str:
        """暗色文本"""
        return f"{self.COLORS['dim']}{text}{self.COLORS['reset']}"

    def get_state(self) -> Optional[dict]:
        """读取当前状态"""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding='utf-8'))
            except:
                pass
        return None

    def format_timestamp(self, timestamp: str) -> str:
        """格式化时间戳"""
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%H:%M:%S")
        except:
            return timestamp

    def display_entry(self, entry: dict):
        """显示一条日记条目"""
        phase = entry.get("phase", "UNKNOWN")
        timestamp = entry.get("timestamp", "")
        iteration = entry.get("iteration", 0)

        # 获取阶段样式
        style = self.PHASE_STYLES.get(phase, {"icon": "📌", "color": "white"})
        icon = style["icon"]
        color = style["color"]

        # 打印时间戳和阶段
        time_str = self.format_timestamp(timestamp) if timestamp else "--:--:--"
        header = f"{icon} {self.colorize(phase, color)} #{iteration}"
        time_display = self.dim(f"[{time_str}]")

        print(f"  {header} {time_display}")

        # 根据阶段显示不同内容
        if phase == "THINKING":
            thought = entry.get("thought", "")
            if thought:
                print(f"    {self.dim('思考:')} {thought}")

        elif phase == "ACTION":
            action = entry.get("action", "")
            files = entry.get("created_files", [])
            if action:
                print(f"    {self.dim('行动:')} {action}")
            if files:
                print(f"    {self.dim('文件:')} {', '.join(files)}")

        elif phase == "REFLECTION":
            reflection = entry.get("reflection", "")
            emotion = entry.get("emotional_state", "")
            if reflection:
                print(f"    {self.dim('反思:')} {reflection}")
            if emotion:
                emoji = self._get_emotion_emoji(emotion)
                print(f"    {self.dim('心情:')} {emoji} {emotion}")

        elif phase == "NEXT_GOAL":
            goal = entry.get("next_goal", "")
            if goal:
                print(f"    {self.dim('目标:')} {self.colorize(goal, 'blue')}")

        elif phase == "ERROR":
            summary = entry.get("summary", "")
            if summary:
                print(f"    {self.colorize(summary, 'red')}")

        elif phase == "ITERATION_END":
            will_continue = entry.get("will_continue", True)
            status = self.colorize("继续", "green") if will_continue else self.colorize("停止", "red")
            print(f"    {self.dim('状态:')} {status}")

        print()

    def _get_emotion_emoji(self, emotion: str) -> str:
        """获取情绪表情"""
        emotion_map = {
            "好奇": "🔍",
            "兴奋": "🎉",
            "满足": "😊",
            "困惑": "😕",
            "思考": "🤔",
            "专注": "🎯",
            "平静": "😌",
            "期待": "✨",
        }
        return emotion_map.get(emotion, "💭")

    def display_status(self):
        """显示当前状态"""
        state = self.get_state()
        if not state:
            return

        iteration = state.get("iteration", 0)
        thoughts = state.get("total_thoughts", 0)
        actions = state.get("total_actions", 0)

        print()
        print(self.bold("=" * 60))
        if self.life_name:
            print(self.bold(f"📊 代理状态 - {self.life_name} - 第 {iteration} 轮"))
        else:
            print(self.bold(f"📊 代理状态 - 第 {iteration} 轮"))
        print(self.bold("=" * 60))
        print(f"  迭代次数: {self.colorize(str(iteration), 'cyan')}")
        print(f"  思考次数: {self.colorize(str(thoughts), 'magenta')}")
        print(f"  行动次数: {self.colorize(str(actions), 'yellow')}")
        print()

        # 显示最近的思考
        last_thought = state.get("last_thought", "")
        if last_thought:
            print(self.bold("💭 最近思考:"))
            print(f"  {self.dim(last_thought)}")
            print()

        # 显示最近目标
        goals = state.get("goals", [])
        if goals:
            print(self.bold("🎯 当前目标:"))
            for i, goal in enumerate(goals[-3:], 1):
                print(f"  {i}. {self.colorize(goal, 'blue')}")
            print()

    def read_new_entries(self) -> list:
        """读取新的日记条目"""
        if not self.diary_file.exists():
            return []

        try:
            with open(self.diary_file, 'r', encoding='utf-8') as f:
                # 跳到上次读取的位置
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()

            entries = []
            for line in new_lines:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except:
                        pass

            return entries
        except:
            return []

    def watch(self, interval: float = 0.5):
        """监视模式 - 实时显示新条目"""
        print(self.bold("👁️  观察者启动"))
        if self.life_name:
            print(self.dim(f"生命: {self.life_name}"))
        print(self.dim(f"监控文件: {self.diary_file.relative_to(self.work_dir)}"))
        print(self.dim(f"等待数据..."))
        print()

        try:
            while True:
                # 读取新条目
                new_entries = self.read_new_entries()

                # 显示新条目
                for entry in new_entries:
                    phase = entry.get("phase", "")

                    # 在每次迭代开始时更新状态
                    if phase == "ITERATION_START":
                        iteration = entry.get("iteration", 0)
                        if iteration != self.last_iteration:
                            self.last_iteration = iteration
                            self.display_status()

                    # 显示条目
                    self.display_entry(entry)

                # 检查停止条件
                state = self.get_state()
                if state:
                    # 检查是否有系统停止的标志
                    pass

                time.sleep(interval)

        except KeyboardInterrupt:
            print()
            print(self.bold("👋 观察者退出"))
            print(self.dim("监控结束"))

    def replay(self, limit: int = None):
        """回放模式 - 显示所有历史条目"""
        print(self.bold("📜 日记回放"))
        print(self.dim(f"读取文件: {self.diary_file.relative_to(self.work_dir)}"))
        print()

        if not self.diary_file.exists():
            print(self.dim("（日记文件不存在）"))
            return

        try:
            with open(self.diary_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            entries = []
            for line in lines:
                if line.strip():
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except:
                        pass

            if limit:
                entries = entries[-limit:]

            print(self.dim(f"总共 {len(entries)} 条记录"))
            print()

            for entry in entries:
                self.display_entry(entry)

        except Exception as e:
            print(f"读取错误: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="观察者 - 实时监控反思型代理")
    parser.add_argument("--work-dir", "-w", help="工作目录")
    parser.add_argument("--life", "-l", help="观察特定生命")
    parser.add_argument("--replay", "-r", action="store_true", help="回放模式")
    parser.add_argument("--limit", "-n", type=int, help="回放条数限制")
    parser.add_argument("--interval", "-i", type=float, default=0.5, help="监控间隔（秒）")

    args = parser.parse_args()

    observer = Observer(work_dir=args.work_dir, life_name=args.life)

    if args.replay:
        observer.replay(limit=args.limit)
    else:
        observer.watch(interval=args.interval)


if __name__ == "__main__":
    main()
