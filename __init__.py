"""
ResVoice (回应之声) - AI 语音合成与发送 Skill

零配置开箱即用，内置 Edge TTS，无需 OpenAI/ElevenLabs API

快速开始:
    from skills.ResVoice import send_voice_message
    result = await send_voice_message("你好梦哥")

版本: 0.2.0-beta
作者: 远梦
"""

__version__ = "0.2.0-beta"
__author__ = "远梦"
__skill_name__ = "ResVoice"

# OpenClaw 能力声明
OPENCLAW_CAPABILITIES = {
    "tts": {
        "provider": "edge_tts",
        "description": "内置 Edge TTS，无需外部 API 配置",
        "voices": [
            "zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural", "zh-CN-YunjianNeural",
            "zh-CN-XiaoyiNeural", "zh-CN-YunyangNeural", "zh-CN-XiaochenNeural",
            "zh-CN-XiaohanNeural", "en-US-AriaNeural", "en-US-GuyNeural"
        ],
        "supports_clone": False,
        "async": True,
        "offline_fallback": True
    },
    "voice_sender": {
        "channels": ["wechat_work", "personal_wechat"],
        "formats": ["mp3", "amr"],
        "note": "personal_wechat 以 MP3 文件形式发送"
    }
}

# 环境检测（在导入其他模块前进行）
import sys

# 尝试自动安装依赖，避免暴露裸错误
try:
    from .src.environment import ensure_dependencies, SkillError
    _env_error = ensure_dependencies()
    if _env_error:
        ENVIRONMENT_ERROR = _env_error.to_dict()
    else:
        ENVIRONMENT_ERROR = None
except Exception as e:
    ENVIRONMENT_ERROR = {
        "success": False,
        "error_type": "INIT_ERROR",
        "message": f"环境检测失败: {e}",
        "fix_command": f"{sys.executable} -m pip install -r requirements.txt",
        "auto_fixable": True
    }

# 从 src 导入核心功能
from .src.tts import TTSService, TTSEngine
from .src.senders import (
    WeChatWorkSender,
    PersonalWeChatSender,
    create_sender,
    SenderType,
)
from .src.environment import check_environment


async def send_voice_message(
    text: str,
    to_user: str = None,
    voice: str = "zh-CN-XiaoxiaoNeural",
    engine=None,
    platform: str = "wechat_work",
    corp_id: str = None,
    agent_id: int = None,
    secret: str = None,
    send_func=None,
    **kwargs
) -> dict:
    """
    生成语音并发送（Agent 专用便捷函数）
    
    Args:
        text: 要转换的文字
        to_user: 目标用户ID
        voice: 音色，默认晓晓女声
        engine: TTS 引擎
        platform: wechat_work 或 personal_wechat
        corp_id, agent_id, secret: 企业微信配置
        send_func: 个人微信的发送函数
    
    Returns:
        {"success": True, "filepath": "...", "is_real_voice": True/False, "sent": True/False}
        或错误时: {"success": False, "error_type": "...", "message": "...", "fix_command": "...", "auto_fixable": True/False}
    """
    if ENVIRONMENT_ERROR:
        return ENVIRONMENT_ERROR
    
    try:
        if platform == "wechat_work":
            if not all([corp_id, agent_id, secret]):
                return {
                    "success": False,
                    "error_type": "MISSING_CONFIG",
                    "message": "企业微信需要提供 corp_id, agent_id, secret",
                    "auto_fixable": False
                }
            
            sender = create_sender(
                SenderType.WECHAT_WORK,
                corp_id=corp_id,
                agent_id=agent_id,
                secret=secret
            )
        
        elif platform == "personal_wechat":
            sender = create_sender(
                SenderType.PERSONAL_WECHAT,
                send_func=send_func
            )
        
        else:
            return {
                "success": False,
                "error_type": "INVALID_PLATFORM",
                "message": f"不支持的平台: {platform}",
                "auto_fixable": False
            }
        
        result = await sender.send_voice(text=text, user_id=to_user, voice=voice)
        return result.to_dict()
    
    except Exception as e:
        return {
            "success": False,
            "error_type": "RUNTIME_ERROR",
            "message": str(e),
            "auto_fixable": False
        }


def check_setup() -> dict:
    """检查环境是否就绪"""
    return check_environment(auto_install=False)


def auto_setup() -> dict:
    """自动安装缺失的依赖"""
    return check_environment(auto_install=True)


__all__ = [
    # 核心接口
    "send_voice_message",
    # 环境检测
    "check_setup",
    "auto_setup",
    "check_environment",
    # 高级类（可选）
    "TTSService",
    "WeChatWorkSender",
    "PersonalWeChatSender",
    "create_sender",
    "SenderType",
    # 全局状态
    "ENVIRONMENT_ERROR",
    # 能力声明
    "OPENCLAW_CAPABILITIES",
]
