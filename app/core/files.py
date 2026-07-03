# Day08 — 文件工具（PDF 上传配套）
#
# 功能：目录创建、文件大小人类可读格式化
# 逻辑：
#   format_file_size — 字节 → "8MB" / "512KB" / "100B"
#   ensure_dir       — 若目录不存在则创建（如 uploads/）

from pathlib import Path


def format_file_size(size_bytes: int) -> str:
    mb = 1024 * 1024
    kb = 1024
    if size_bytes >= mb:
        return f"{round(size_bytes / mb)}MB"
    if size_bytes >= kb:
        return f"{round(size_bytes / kb)}KB"
    return f"{size_bytes}B"


def ensure_dir(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
