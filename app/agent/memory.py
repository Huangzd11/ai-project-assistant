# Day17 — Agent 会话记忆（Short / Long Memory）
#
# 功能：按 session_id 持久化对话历史与关键事实
# 逻辑：JSON 落盘 data/conversations/{session_id}.json

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import MEMORY_MAX_TURNS
from app.core.logger import logger


# @brief: 规范化 session_id，防止路径穿越
# @param: session_id: 原始会话 ID
# @return: 安全文件名
def _safe_session_id(session_id: str) -> str:
    safe = re.sub(r"[^\w\-]", "_", session_id.strip())
    if not safe:
        raise ValueError("session_id 无效")
    return safe[:64]

# 单个会话的 Short Memory（messages）与 Long Memory（facts）
class ConversationMemory:

    # @brief: 初始化会话记忆
    # @param: session_id: 会话 ID
    # @param: memory_dir: 记忆目录
    def __init__(self, session_id: str, memory_dir: str | Path):
        self.session_id = _safe_session_id(session_id)
        self.path = Path(memory_dir) / f"{self.session_id}.json"
        self.messages: list[dict] = []
        self.facts: list[str] = []
        self._load()

    # @brief: 加载会话记忆
    # @return: None
    def _load(self) -> None:
        if not self.path.is_file():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.messages = data.get("messages", [])
            self.facts = data.get("facts", [])
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("memory load failed  session=%s  error=%s", self.session_id, exc)
            self.messages = []
            self.facts = []

    # @brief: 保存会话记忆
    # @return: None
    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "session_id": self.session_id,
            "messages": self.messages,
            "facts": self.facts,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # @brief: 追加一条对话消息（Short Memory）
    # @param: role: user / assistant
    # @param: content: 消息内容
    def append(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})
        max_msgs = MEMORY_MAX_TURNS * 2
        if len(self.messages) > max_msgs:
            self.messages = self.messages[-max_msgs:]
        self._save()

    # @brief: 获取历史消息列表
    # @return: messages 副本
    def get_messages(self) -> list[dict]:
        return list(self.messages)

    # @brief: 写入 Long Memory 事实
    # @param: fact: 关键事实文本
    def add_fact(self, fact: str) -> None:
        fact = fact.strip()
        if fact and fact not in self.facts:
            self.facts.append(fact)
            self._save()

    # @brief: 读取 Long Memory 事实列表
    # @return: facts 副本
    def get_facts(self) -> list[str]:
        return list(self.facts)

    # @brief: 清空当前会话记忆
    def clear(self) -> None:
        self.messages = []
        self.facts = []
        self._save()


_store: dict[str, ConversationMemory] = {}

# @brief: 获取或创建会话记忆实例
# @param: session_id: 会话 ID
# @return: ConversationMemory
def get_memory(session_id: str) -> ConversationMemory:
    from app.core.config import MEMORY_DIR

    safe_id = _safe_session_id(session_id)
    if safe_id not in _store:
        _store[safe_id] = ConversationMemory(safe_id, MEMORY_DIR)
    return _store[safe_id]


# @brief: 从用户消息提取简单事实写入 Long Memory（规则版）
# @param: memory: 会话记忆
# @param: user_message: 用户消息
def maybe_extract_facts(memory: ConversationMemory, user_message: str) -> None:
    match = re.search(r"我是(.+?)[。．.!！?？\s]*$", user_message.strip())
    if match:
        memory.add_fact(f"用户是{match.group(1).strip()}")


# @brief: 将 Long Memory facts 拼入 system prompt
# @param: base_prompt: 基础 system prompt
# @param: facts: 事实列表
# @return: 增强后的 system prompt
def build_system_with_facts(base_prompt: str, facts: list[str]) -> str:
    if not facts:
        return base_prompt
    lines = "\n".join(f"- {fact}" for fact in facts)
    return f"{base_prompt}\n\n已知用户信息：\n{lines}"
