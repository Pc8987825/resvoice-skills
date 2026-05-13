"""
ResVoice.skills - 核心模块
"""

from .tts import TTSService, TTSEngine, text_to_speech_sync, text_to_speech_simple
from .audio import AudioConverter
from .wechat import WeChatWorkAPI, WeChatWorkConfig, WeChatWorkVoiceSender
from .utils import get_output_dir, format_file_size
from .environment import (
    check_environment,
    ensure_dependencies,
    check_deps,
    install_deps,
    EnvironmentCheckResult,
    SkillError,
    ErrorType,
)

__all__ = [
    "TTSService",
    "TTSEngine",
    "text_to_speech_sync",
    "text_to_speech_simple",
    "AudioConverter",
    "WeChatWorkAPI",
    "WeChatWorkConfig",
    "WeChatWorkVoiceSender",
    "get_output_dir",
    "format_file_size",
    # 环境检测
    "check_environment",
    "ensure_dependencies",
    "check_deps",
    "install_deps",
    "EnvironmentCheckResult",
    "SkillError",
    "ErrorType",
]
