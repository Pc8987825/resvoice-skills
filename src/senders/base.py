"""
语音发送器抽象基类
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class VoiceSendResult:
    """语音发送结果"""
    success: bool
    platform: str                          # 平台名称
    is_real_voice: bool                    # 是否是真正的语音消息
    format: str                            # 音频格式: mp3, amr, etc.
    filepath: str                          # 本地文件路径
    message: Optional[str] = None          # 发送结果说明
    sent: bool = False                     # 是否成功发送到平台
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "success": self.success,
            "platform": self.platform,
            "is_real_voice": self.is_real_voice,
            "format": self.format,
            "filepath": self.filepath,
            "message": self.message,
            "sent": self.sent,
        }


class BaseVoiceSender(ABC):
    """
    语音发送器抽象基类
    
    所有平台的发送器都应继承此类，实现统一接口
    """
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
    
    @property
    @abstractmethod
    def supports_real_voice(self) -> bool:
        """
        是否支持真正的语音消息（而非文件形式）
        
        Returns:
            True: 支持 AMR 等真正的语音消息格式
            False: 只能以文件形式发送（如 MP3）
        """
        pass
    
    @property
    @abstractmethod
    def supported_formats(self) -> list:
        """
        支持的音频格式列表
        
        Returns:
            如 ["mp3", "amr"] 或 ["mp3"]
        """
        pass
    
    @abstractmethod
    async def send_voice(
        self, 
        text: str, 
        user_id: str,
        voice: Optional[str] = None
    ) -> VoiceSendResult:
        """
        发送语音消息
        
        Args:
            text: 要转换的文字
            user_id: 目标用户ID
            voice: 音色选择（可选）
        
        Returns:
            VoiceSendResult 发送结果
        """
        pass
    
    async def _generate_audio(self, text: str, voice: Optional[str] = None) -> dict:
        """
        生成音频文件（内部方法）
        
        Args:
            text: 要转换的文字
            voice: 音色选择
        
        Returns:
            TTS 生成结果字典
        """
        from ..tts import TTSService
        
        tts = TTSService()
        return await tts.text_to_speech(text=text, voice=voice)
