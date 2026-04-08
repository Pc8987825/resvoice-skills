"""
通用工具函数
"""

import os
from pathlib import Path


def get_output_dir(output_dir: str = None) -> Path:
    """获取输出目录"""
    if output_dir:
        return Path(output_dir)
    env_dir = os.getenv("TTS_OUTPUT_DIR")
    if env_dir:
        return Path(env_dir)
    # 使用 src 目录的父目录下的 output
    return Path(__file__).parent.parent / "output"


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
