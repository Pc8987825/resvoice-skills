"""
ResVoice (回应之声) - AI 语音合成与发送 Skill

零配置开箱即用，内置 Edge TTS，无需 OpenAI/ElevenLabs API

快速开始:
    from skills.ResVoice import send_voice_auto
    result = await send_voice_auto("你好梦哥")

版本: 0.3.0-beta
作者: 远梦
"""

__version__ = "0.3.0-beta"
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
        "channels": ["openclaw_weixin", "wechat_work"],
        "formats": ["mp3", "amr"],
        "note": "自动检测 OpenClaw 环境，选择最优发送方式"
    },
    "openclaw_auto_detect": True
}

# 环境检测
import sys

try:
    from .src.environment import ensure_dependencies, SkillError
    _env_error = ensure_dependencies()
    ENVIRONMENT_ERROR = _env_error.to_dict() if _env_error else None
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
from .src.platform import (
    detect_platform,
    is_openclaw_environment,
    PlatformInfo,
    send_voice_auto,
)


async def send_voice_message(
    text: str,
    to_user: str = None,
    voice: str = "zh-CN-XiaoxiaoNeural",
    engine=None,
    platform: str = None,
    corp_id: str = None,
    agent_id: int = None,
    secret: str = None,
    send_func=None,
    **kwargs
) -> dict:
    """
    生成语音并发送（Agent 专用便捷函数）
    
    核心特点：
    - platform=None 时自动检测 OpenClaw 环境
    - 自动选择最优发送方式
    - 无需手动配置 send_func
    
    Args:
        text: 要转换的文字
        to_user: 目标用户ID（自动从 OpenClaw 获取）
        voice: 音色，默认晓晓女声
        platform: 平台类型，None=自动检测
        corp_id, agent_id, secret: 企业微信配置
        send_func: 发送函数（自动配置）
    
    Returns:
        发送结果字典
    """
    if ENVIRONMENT_ERROR:
        return ENVIRONMENT_ERROR
    
    # 自动检测平台
    if platform is None:
        info = detect_platform()
        
        if info.platform == "unknown":
            # 非 OpenClaw 环境，只生成文件
            tts = TTSService()
            result = await tts.text_to_speech(text=text, voice=voice)
            return {
                "success": True,
                "filepath": result["filepath"],
                "platform": "unknown",
                "is_real_voice": False,
                "sent": False,
                "note": "非 OpenClaw 环境，仅生成文件"
            }
        
        # OpenClaw 环境，使用自动配置的发送函数
        platform = info.platform
        send_func = info.send_func
        to_user = to_user or info.chat_id
    
    try:
        if platform == "wechat_work":
            # 企业微信
            if not all([corp_id, agent_id, secret]):
                return {
                    "success": False,
                    "error_type": "MISSING_CONFIG",
                    "message": "企业微信需要提供 corp_id, agent_id, secret",
                    "fix_command": "设置环境变量 WECHAT_WORK_CORP_ID, WECHAT_WORK_AGENT_ID, WECHAT_WORK_SECRET",
                    "auto_fixable": False
                }
            
            sender = create_sender(
                SenderType.WECHAT_WORK,
                corp_id=corp_id,
                agent_id=agent_id,
                secret=secret
            )
        
        elif platform in ["personal_wechat", "openclaw_weixin", "openclaw_other"]:
            # 个人微信或其他渠道，使用 OpenClaw 的发送函数
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
    # 核心接口（推荐）
    "send_voice_message",      # 自动检测 OpenClaw
    "send_voice_auto",         # 同上，语义更明确
    # 环境检测
    "check_setup",
    "auto_setup",
    "check_environment",
    # 平台检测
    "detect_platform",
    "is_openclaw_environment",
    "PlatformInfo",
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
