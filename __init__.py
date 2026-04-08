"""
ResVoice (回应之声) - AI 语音合成与发送 Skill

零配置开箱即用，内置 Edge TTS，无需 OpenAI/ElevenLabs API

快速开始:
    from skills.ResVoice import send_voice_message
    result = await send_voice_message("你好梦哥")

版本: 0.1.5-beta
作者: 远梦
"""

__version__ = "0.1.5-beta"
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
        "channels": ["wechat_work"],
        "formats": ["mp3", "amr"]
    }
}

# 从 src 导入核心功能
from .src.tts import TTSService, TTSEngine, text_to_speech_sync, text_to_speech_simple
from .src.audio import AudioConverter
from .src.wechat import WeChatWorkAPI, WeChatWorkConfig, WeChatWorkVoiceSender


async def send_voice_message(
    text: str,
    to_user: str = None,
    voice: str = "zh-CN-XiaoxiaoNeural",
    engine=None,
    send_to_wechat: bool = False,
    corp_id: str = None,
    agent_id: int = None,
    secret: str = None,
) -> dict:
    """
    生成语音并发送（OpenClaw 专用便捷函数）
    
    Args:
        text: 要转换的文字
        to_user: 企业微信用户ID
        voice: 音色，默认晓晓女声
        engine: TTS 引擎
        send_to_wechat: 是否发送到企业微信
        corp_id, agent_id, secret: 企业微信配置
    
    Returns:
        {"success": True, "filepath": "...", "engine": "edge", "sent": bool}
    """
    tts = TTSService()
    tts_result = await tts.text_to_speech(text=text, voice=voice, engine=engine)
    
    result = {
        "success": True,
        "filepath": tts_result["filepath"],
        "engine": tts_result["engine"],
        "voice": tts_result.get("voice", voice),
        "sent": False
    }
    
    if send_to_wechat and to_user:
        if not all([corp_id, agent_id, secret]):
            raise ValueError("发送到企业微信需要提供 corp_id, agent_id, secret")
        
        sender = WeChatWorkVoiceSender(corp_id, agent_id, secret, allow_fallback=True)
        send_result = await sender.text_to_voice_and_send(text, to_user, voice)
        result["sent"] = True
        result["send_result"] = send_result
    
    return result


def send_voice_message_sync(text: str, **kwargs) -> dict:
    """send_voice_message 的同步版本"""
    import asyncio
    return asyncio.run(send_voice_message(text, **kwargs))


__all__ = [
    # 核心类
    "TTSService", "TTSEngine",
    "AudioConverter",
    "WeChatWorkAPI", "WeChatWorkConfig", "WeChatWorkVoiceSender",
    # 便捷函数
    "send_voice_message", "send_voice_message_sync",
    "text_to_speech_sync", "text_to_speech_simple",
    # 能力声明
    "OPENCLAW_CAPABILITIES",
]
