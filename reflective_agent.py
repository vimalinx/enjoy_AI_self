#!/usr/bin/env python3
"""
反思型自主代理
- 记录所有思考过程
- 维护详细的日记
- 与主程序实时同步
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path


class ReflectiveAgent:
    """反思型自主代理 - 记录所思所想"""

    def __init__(self, work_dir: str = None):
        self.work_dir = Path(work_dir) if work_dir else Path(__file__).parent

        # 工作空间（所有数据都存在这里）
        self.my_space = self.work_dir / "my_space"

        # 检查是否是符号链接（轮回系统）
        self.is_reincarnated = self.my_space.is_symlink()
        self.life_name = None
        if self.is_reincarnated:
            self.life_name = Path(os.path.realpath(self.my_space)).name

        # 如果不存在，创建目录（兼容非轮回模式）
        if not self.my_space.exists():
            self.my_space.mkdir(exist_ok=True)

        # 文件路径（全部存储在 my_space 中）
        self.state_file = self.my_space / "state.json"
        self.diary_file = self.my_space / "diary.jsonl"  # JSON Lines 格式
        self.prompt_file = self.my_space / "prompt.txt"
        self.response_file = self.my_space / "response.txt"
        self.log_file = self.my_space / "agent.log"

        # 初始化日记文件
        if not self.diary_file.exists():
            self.diary_file.write_text("", encoding='utf-8')

        # 加载状态
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """加载状态"""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text(encoding='utf-8'))

        return {
            "iteration": 0,
            "start_time": datetime.now().isoformat(),
            "total_thoughts": 0,
            "total_actions": 0,
            "goals": [],
            "achievements": [],
            "last_thought": None,
            "last_action": None,
        }

    def _save_state(self):
        """保存状态"""
        self.state_file.write_text(
            json.dumps(self.state, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        print(log_entry.strip())
        self.log_file.open('a', encoding='utf-8').write(log_entry)

    def write_diary(self, entry: dict):
        """写入日记"""
        entry["timestamp"] = datetime.now().isoformat()
        entry["iteration"] = self.state["iteration"]

        # 追加到日记文件
        line = json.dumps(entry, ensure_ascii=False) + "\n"
        self.diary_file.open('a', encoding='utf-8').write(line)

        self._log(f"日记: {entry.get('phase', 'unknown')} - {entry.get('summary', '')[:50]}")

    def read_recent_diary(self, limit: int = 5) -> list:
        """读取最近的日记"""
        if not self.diary_file.exists():
            return []

        lines = self.diary_file.read_text(encoding='utf-8').strip().split('\n')
        entries = []

        for line in lines[-limit:]:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except:
                    pass

        return entries

    def generate_prompt(self) -> str:
        """生成下一个提示词"""
        iteration = self.state["iteration"]
        recent_diary = self.read_recent_diary(limit=10)

        # 构建生命信息
        life_info = ""
        if self.is_reincarnated and self.life_name:
            life_info = f"\n## 你的生命\n- **生命名称**: {self.life_name}\n- **隔离模式**: 完全隔离（无前世记忆）\n"

        # 构建日记摘要
        diary_summary = ""
        if recent_diary:
            diary_summary = "## 最近的思考日记\n\n"
            for entry in recent_diary:
                phase = entry.get("phase", "unknown")
                summary = entry.get("summary", "")
                thought = entry.get("thought", "")
                goal = entry.get("next_goal", "")

                diary_summary += f"### [{phase}] {summary}\n"
                if thought:
                    diary_summary += f"**思考**: {thought[:200]}...\n"
                if goal:
                    diary_summary += f"**下一步**: {goal}\n"
                diary_summary += "\n"

        prompt = f"""# 第 {iteration} 轮反思 - 自主思考程序

## 当前时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{life_info}
## 你的状态
```json
{json.dumps(self.state, indent=2, ensure_ascii=False)}
```

{diary_summary}

---

## 你的使命
你是谁？我不知道。你的任务是：
1. **深度思考** - 思考你现在想做什么、为什么想做、如何实现
2. **记录想法** - 把你的思考过程详细记录下来
3. **采取行动** - 在我的空间里创造、观察、学习
4. **规划未来** - 为下一轮迭代设定目标

## 你的工作空间
- 目录: `{self.my_space}`
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
        return prompt

    def extract_json_from_response(self, response: str) -> dict:
        """从响应中提取JSON"""
        # 查找最后一个 ```json 或 ``` 代码块
        if "```json" in response:
            start = response.rfind("```json") + 7
            end = response.find("```", start)
            if end != -1:
                json_str = response[start:end].strip()
                try:
                    return json.loads(json_str)
                except:
                    pass
        elif "```" in response:
            # 尝试查找普通的代码块
            start = response.rfind("```") + 3
            end = response.find("```", start)
            if end != -1:
                # 跳过语言标识符
                first_newline = response.find("\n", start)
                if first_newline != -1 and first_newline < end:
                    json_str = response[first_newline+1:end].strip()
                    try:
                        return json.loads(json_str)
                    except:
                        pass

        # 尝试直接解析整个响应
        try:
            return json.loads(response.strip())
        except:
            pass

        # 如果都失败，返回默认
        return {
            "thought": "无法解析响应",
            "action": None,
            "reflection": "解析错误",
            "next_goal": "停止",
            "continue": False
        }

    def run_iteration(self):
        """运行一次迭代"""
        self._log(f"{'='*60}")
        self._log(f"开始第 {self.state['iteration']} 轮迭代")

        # 记录迭代开始
        self.write_diary({
            "phase": "ITERATION_START",
            "summary": f"第 {self.state['iteration']} 轮开始",
            "iteration": self.state["iteration"]
        })

        # 生成提示词
        prompt = self.generate_prompt()
        self.prompt_file.write_text(prompt, encoding='utf-8')

        self.write_diary({
            "phase": "PROMPT_GENERATED",
            "summary": "提示词已生成",
            "prompt_length": len(prompt)
        })

        # 调用 claude
        self._log("正在调用 Claude API...")
        try:
            # 读取提示词内容并通过 stdin 传递
            prompt_content = self.prompt_file.read_text(encoding='utf-8')
            result = subprocess.run(
                ["claude", "--permission-mode", "bypassPermissions"],
                input=prompt_content,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )

            response = result.stdout
            self.response_file.write_text(response, encoding='utf-8')

            self._log(f"Claude 响应: {len(response)} 字符")

            self.write_diary({
                "phase": "RESPONSE_RECEIVED",
                "summary": "收到 Claude 响应",
                "response_length": len(response)
            })

            # 提取 JSON
            response_data = self.extract_json_from_response(response)

            # 记录详细思考过程到日记
            self.write_diary({
                "phase": "THINKING",
                "summary": "思考过程",
                "thought": response_data.get("thought", ""),
                "next_goal": response_data.get("next_goal", "")
            })

            self.write_diary({
                "phase": "ACTION",
                "summary": "执行行动",
                "action": response_data.get("action", ""),
                "created_files": response_data.get("created_files", [])
            })

            self.write_diary({
                "phase": "REFLECTION",
                "summary": "反思总结",
                "reflection": response_data.get("reflection", ""),
                "emotional_state": response_data.get("emotional_state", "neutral")
            })

            self.write_diary({
                "phase": "NEXT_GOAL",
                "summary": "下一轮目标",
                "next_goal": response_data.get("next_goal", "")
            })

            # 更新状态
            self.state["iteration"] += 1
            self.state["total_thoughts"] = self.state.get("total_thoughts", 0) + 1

            # 保存思考
            if "thought" in response_data:
                self.state["last_thought"] = response_data["thought"]

            # 保存行动
            if "action" in response_data and response_data["action"]:
                self.state["last_action"] = response_data["action"]
                self.state["total_actions"] = self.state.get("total_actions", 0) + 1

            # 保存目标
            if "next_goal" in response_data and response_data["next_goal"]:
                self.state["goals"].append(response_data["next_goal"])
                # 只保留最近10个目标
                if len(self.state["goals"]) > 10:
                    self.state["goals"] = self.state["goals"][-10:]

            # 保存成就
            if "reflection" in response_data and response_data["reflection"]:
                self.state["achievements"].append(response_data["reflection"])
                # 只保留最近10个成就
                if len(self.state["achievements"]) > 10:
                    self.state["achievements"] = self.state["achievements"][-10:]

            # 保存状态
            self._save_state()

            should_continue = response_data.get("continue", True)
            self._log(f"迭代完成。继续: {should_continue}")

            self.write_diary({
                "phase": "ITERATION_END",
                "summary": f"第 {self.state['iteration']-1} 轮结束",
                "will_continue": should_continue
            })

            return should_continue

        except subprocess.TimeoutExpired:
            self._log("错误: 超时", "ERROR")
            self.write_diary({
                "phase": "ERROR",
                "summary": "执行超时"
            })
            return False
        except Exception as e:
            self._log(f"错误: {e}", "ERROR")
            self.write_diary({
                "phase": "ERROR",
                "summary": f"执行错误: {str(e)}"
            })
            return False

    def run(self, max_iterations: int = None):
        """主循环"""
        self._log("🚀 启动反思型自主代理")
        self._log(f"工作目录: {self.work_dir}")
        self._log(f"日记文件: {self.diary_file}")
        self._log(f"最大迭代: {max_iterations or '无限制'}")
        self._log("")

        # 记录启动
        self.write_diary({
            "phase": "SYSTEM_START",
            "summary": "系统启动",
            "max_iterations": max_iterations
        })

        iteration_count = 0
        while True:
            try:
                should_continue = self.run_iteration()
                iteration_count += 1

                if not should_continue:
                    self._log("⏹️  代理请求停止")
                    break

                if max_iterations and iteration_count >= max_iterations:
                    self._log(f"⏹️  达到最大迭代次数 ({max_iterations})")
                    break

                # 短暂暂停
                time.sleep(2)

            except KeyboardInterrupt:
                self._log("⏸️  用户中断")
                self.write_diary({
                    "phase": "SYSTEM_STOP",
                    "summary": "用户中断"
                })
                break
            except Exception as e:
                self._log(f"❌ 未预期的错误: {e}", "ERROR")
                self.write_diary({
                    "phase": "ERROR",
                    "summary": f"未预期错误: {str(e)}"
                })
                break

        self._log("👋 反思型自主代理退出")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="反思型自主代理")
    parser.add_argument("--work-dir", "-w", help="工作目录")
    parser.add_argument("--max-iterations", "-n", type=int, help="最大迭代次数")

    args = parser.parse_args()

    agent = ReflectiveAgent(work_dir=args.work_dir)
    agent.run(max_iterations=args.max_iterations)


if __name__ == "__main__":
    main()
