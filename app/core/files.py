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
