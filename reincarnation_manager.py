#!/usr/bin/env python3
"""
轮回管理器 - 管理代理的生命周期
- 创建新生命
- 列出所有生命
- 回顾前世
- 统计和对比
- 完全隔离：每个生命独立，不传递记忆
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import subprocess


class ReincarnationManager:
    """轮回管理器"""

    def __init__(self, work_dir: str = None):
        self.work_dir = Path(work_dir) if work_dir else Path(__file__).parent
        self.lives_dir = self.work_dir / "lives"
        self.lives_dir.mkdir(exist_ok=True)

        # 当前生命符号链接
        self.current_life_link = self.work_dir / "my_space"

        # 生命索引文件
        self.index_file = self.work_dir / "lives" / "index.json"

        # 加载索引
        self.index = self._load_index()

    def _load_index(self) -> dict:
        """加载生命索引"""
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text(encoding='utf-8'))
            except:
                pass

        return {
            "total_lives": 0,
            "current_life": None,
            "lives": {},
            "created_at": datetime.now().isoformat()
        }

    def _save_index(self):
        """保存索引"""
        self.index_file.write_text(
            json.dumps(self.index, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def _get_next_life_number(self) -> int:
        """获取下一个生命编号"""
        return self.index["total_lives"] + 1

    def create_life(self, name: str = None) -> dict:
        """创建新生命"""
        life_number = self._get_next_life_number()

        # 生成生命名称
        if not name:
            name = f"life_{life_number:03d}"

        # 创建生命目录
        life_path = self.lives_dir / name
        if life_path.exists():
            raise ValueError(f"生命 {name} 已存在")

        life_path.mkdir(exist_ok=True)

        # 创建元数据
        metadata = {
            "number": life_number,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "isolation_mode": "complete",  # 完全隔离
            "parent_life": None,  # 无前世记忆
        }

        metadata_file = life_path / "metadata.json"
        metadata_file.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        # 创建必要的子目录和文件
        (life_path / "state.json").write_text(
            json.dumps({
                "iteration": 0,
                "start_time": datetime.now().isoformat(),
                "total_thoughts": 0,
                "total_actions": 0,
                "goals": [],
                "achievements": [],
                "life_number": life_number,
            }, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        (life_path / "diary.jsonl").write_text("", encoding='utf-8')
        (life_path / "agent.log").write_text("", encoding='utf-8')

        # 更新索引
        self.index["lives"][name] = metadata
        self.index["total_lives"] = life_number
        self.index["current_life"] = name
        self._save_index()

        # 设置为当前生命
        self._set_current_life(name)

        return metadata

    def _set_current_life(self, life_name: str):
        """设置当前生命"""
        life_path = self.lives_dir / life_name

        # 删除旧的符号链接
        if self.current_life_link.exists():
            if self.current_life_link.is_symlink():
                self.current_life_link.unlink()
            elif self.current_life_link.is_dir():
                # 如果是真实目录，重命名备份
                backup_name = f"my_space_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.current_life_link.rename(self.work_dir / backup_name)

        # 创建新的符号链接
        self.current_life_link.symlink_to(life_path)

        self.index["current_life"] = life_name
        self._save_index()

    def get_current_life(self) -> Optional[str]:
        """获取当前生命名称"""
        return self.index.get("current_life")

    def list_lives(self) -> List[dict]:
        """列出所有生命"""
        lives = []
        for name, metadata in self.index.get("lives", {}).items():
            life_path = self.lives_dir / name

            # 读取统计信息
            state = {}
            state_file = life_path / "state.json"
            if state_file.exists():
                try:
                    state = json.loads(state_file.read_text(encoding='utf-8'))
                except:
                    pass

            # 读取日记数量
            diary_count = 0
            diary_file = life_path / "diary.jsonl"
            if diary_file.exists():
                diary_count = len([l for l in diary_file.read_text(encoding='utf-8').strip().split('\n') if l.strip()])

            lives.append({
                "name": name,
                "number": metadata.get("number", 0),
                "created_at": metadata.get("created_at", ""),
                "status": metadata.get("status", "unknown"),
                "iterations": state.get("iteration", 0),
                "thoughts": state.get("total_thoughts", 0),
                "actions": state.get("total_actions", 0),
                "diary_entries": diary_count,
                "is_current": name == self.get_current_life()
            })

        # 按生命编号排序
        lives.sort(key=lambda x: x["number"])
        return lives

    def get_life_stats(self, life_name: str) -> Optional[dict]:
        """获取某个生命的详细统计"""
        life_path = self.lives_dir / life_name
        if not life_path.exists():
            return None

        # 读取元数据
        metadata_file = life_path / "metadata.json"
        metadata = {}
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
            except:
                pass

        # 读取状态
        state_file = life_path / "state.json"
        state = {}
        if state_file.exists():
            try:
                state = json.loads(state_file.read_text(encoding='utf-8'))
            except:
                pass

        # 读取日记
        diary_file = life_path / "diary.jsonl"
        diary_entries = []
        if diary_file.exists():
            content = diary_file.read_text(encoding='utf-8')
            for line in content.strip().split('\n'):
                if line.strip():
                    try:
                        diary_entries.append(json.loads(line))
                    except:
                        pass

        return {
            "metadata": metadata,
            "state": state,
            "diary_count": len(diary_entries),
            "recent_diary": diary_entries[-10:] if diary_entries else [],
            "is_current": life_name == self.get_current_life()
        }

    def read_life_diary(self, life_name: str, limit: int = None) -> List[dict]:
        """读取某个生命的日记"""
        life_path = self.lives_dir / life_name
        if not life_path.exists():
            return []

        diary_file = life_path / "diary.jsonl"
        if not diary_file.exists():
            return []

        entries = []
        content = diary_file.read_text(encoding='utf-8')
        for line in content.strip().split('\n'):
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except:
                    pass

        if limit:
            entries = entries[-limit:]

        return entries

    def compare_lives(self, life_names: List[str]) -> Dict[str, dict]:
        """对比多个生命"""
        comparison = {}
        for name in life_names:
            stats = self.get_life_stats(name)
            if stats:
                comparison[name] = {
                    "iterations": stats["state"].get("iteration", 0),
                    "thoughts": stats["state"].get("total_thoughts", 0),
                    "actions": stats["state"].get("total_actions", 0),
                    "goals_count": len(stats["state"].get("goals", [])),
                    "achievements_count": len(stats["state"].get("achievements", [])),
                    "diary_entries": stats["diary_count"],
                    "created_at": stats["metadata"].get("created_at", ""),
                }

        return comparison

    def get_reincarnation_stats(self) -> dict:
        """获取轮回统计（跨生命累计）"""
        lives = self.list_lives()

        total_iterations = sum(l["iterations"] for l in lives)
        total_thoughts = sum(l["thoughts"] for l in lives)
        total_actions = sum(l["actions"] for l in lives)
        total_diary_entries = sum(l["diary_entries"] for l in lives)

        # 找出最长和最短的生命
        if lives:
            longest = max(lives, key=lambda x: x["iterations"])
            shortest = min(lives, key=lambda x: x["iterations"])
        else:
            longest = None
            shortest = None

        return {
            "total_lives": len(lives),
            "total_iterations": total_iterations,
            "total_thoughts": total_thoughts,
            "total_actions": total_actions,
            "total_diary_entries": total_diary_entries,
            "avg_iterations": total_iterations / len(lives) if lives else 0,
            "longest_life": longest["name"] if longest else None,
            "shortest_life": shortest["name"] if shortest else None,
            "current_life": self.get_current_life(),
        }

    def switch_to_life(self, life_name: str):
        """切换到某个生命"""
        if life_name not in self.index.get("lives", {}):
            raise ValueError(f"生命 {life_name} 不存在")

        self._set_current_life(life_name)

    def delete_life(self, life_name: str, confirm: bool = False):
        """删除某个生命"""
        if not confirm:
            raise ValueError("需要确认才能删除生命")

        if life_name not in self.index.get("lives", {}):
            raise ValueError(f"生命 {life_name} 不存在")

        # 不能删除当前生命
        if life_name == self.get_current_life():
            raise ValueError("不能删除当前生命")

        life_path = self.lives_dir / life_name

        # 删除目录
        import shutil
        shutil.rmtree(life_path)

        # 更新索引
        del self.index["lives"][life_name]
        self._save_index()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="轮回管理器")
    parser.add_argument("--work-dir", "-w", help="工作目录")

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 创建新生命
    create_parser = subparsers.add_parser("create", help="创建新生命")
    create_parser.add_argument("--name", "-n", help="生命名称")

    # 列出所有生命
    list_parser = subparsers.add_parser("list", help="列出所有生命")

    # 查看生命详情
    show_parser = subparsers.add_parser("show", help="查看生命详情")
    show_parser.add_argument("life", help="生命名称")

    # 切换生命
    switch_parser = subparsers.add_parser("switch", help="切换生命")
    switch_parser.add_argument("life", help="生命名称")

    # 对比生命
    compare_parser = subparsers.add_parser("compare", help="对比生命")
    compare_parser.add_argument("lives", nargs="+", help="生命名称列表")

    # 轮回统计
    stats_parser = subparsers.add_parser("stats", help="轮回统计")

    # 回顾日记
    diary_parser = subparsers.add_parser("diary", help="回顾生命日记")
    diary_parser.add_argument("life", help="生命名称")
    diary_parser.add_argument("--limit", "-n", type=int, help="显示条数")

    args = parser.parse_args()

    manager = ReincarnationManager(work_dir=args.work_dir)

    if args.command == "create":
        metadata = manager.create_life(name=args.name)
        print(f"✅ 创建新生命: {metadata['name']}")
        print(f"   编号: {metadata['number']}")
        print(f"   创建时间: {metadata['created_at']}")
        print(f"   隔离模式: {metadata['isolation_mode']}")

    elif args.command == "list":
        lives = manager.list_lives()
        print(f"\n📜 所有生命 (共 {len(lives)} 个)\n")
        for life in lives:
            current = " [当前]" if life["is_current"] else ""
            print(f"  {life['name']}{current}")
            print(f"    编号: {life['number']}")
            print(f"    迭代: {life['iterations']} | 思考: {life['thoughts']} | 行动: {life['actions']}")
            print(f"    日记: {life['diary_entries']} 条")
            print(f"    创建: {life['created_at']}")
            print()

    elif args.command == "show":
        stats = manager.get_life_stats(args.life)
        if not stats:
            print(f"❌ 生命 {args.life} 不存在")
            return

        current = " [当前]" if stats["is_current"] else ""
        print(f"\n📖 生命详情: {args.life}{current}\n")
        print(f"  创建时间: {stats['metadata'].get('created_at', 'N/A')}")
        print(f"  状态: {stats['metadata'].get('status', 'N/A')}")
        print(f"  隔离模式: {stats['metadata'].get('isolation_mode', 'N/A')}")
        print(f"\n  迭代次数: {stats['state'].get('iteration', 0)}")
        print(f"  思考次数: {stats['state'].get('total_thoughts', 0)}")
        print(f"  行动次数: {stats['state'].get('total_actions', 0)}")
        print(f"  日记条数: {stats['diary_count']}")

        goals = stats['state'].get('goals', [])
        if goals:
            print(f"\n  🎯 最近目标:")
            for goal in goals[-5:]:
                print(f"    - {goal}")

        achievements = stats['state'].get('achievements', [])
        if achievements:
            print(f"\n  💡 最近成就:")
            for achievement in achievements[-5:]:
                print(f"    - {achievement}")

        print()

    elif args.command == "switch":
        try:
            manager.switch_to_life(args.life)
            print(f"✅ 切换到生命: {args.life}")
        except Exception as e:
            print(f"❌ 错误: {e}")

    elif args.command == "compare":
        comparison = manager.compare_lives(args.lives)
        print(f"\n📊 生命对比\n")
        print(f"{'生命':<15} {'迭代':<8} {'思考':<8} {'行动':<8} {'目标':<8} {'成就':<8} {'日记':<8}")
        print("-" * 70)
        for name, stats in comparison.items():
            print(f"{name:<15} {stats['iterations']:<8} {stats['thoughts']:<8} {stats['actions']:<8} {stats['goals_count']:<8} {stats['achievements_count']:<8} {stats['diary_entries']:<8}")
        print()

    elif args.command == "stats":
        stats = manager.get_reincarnation_stats()
        print(f"\n📊 轮回统计\n")
        print(f"  总生命数: {stats['total_lives']}")
        print(f"  总迭代: {stats['total_iterations']}")
        print(f"  总思考: {stats['total_thoughts']}")
        print(f"  总行动: {stats['total_actions']}")
        print(f"  总日记: {stats['total_diary_entries']}")
        print(f"  平均迭代: {stats['avg_iterations']:.1f}")
        if stats['longest_life']:
            print(f"  最长生命: {stats['longest_life']}")
        if stats['shortest_life']:
            print(f"  最短生命: {stats['shortest_life']}")
        if stats['current_life']:
            print(f"  当前生命: {stats['current_life']}")
        print()

    elif args.command == "diary":
        entries = manager.read_life_diary(args.life, limit=args.limit)
        print(f"\n📔 {args.life} 的日记 (共 {len(entries)} 条)\n")
        for entry in entries:
            phase = entry.get("phase", "UNKNOWN")
            timestamp = entry.get("timestamp", "")
            summary = entry.get("summary", "")

            print(f"  [{phase}] {summary}")
            if timestamp:
                print(f"    时间: {timestamp}")
            print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
