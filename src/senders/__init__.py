"""
语音发送器模块

提供统一接口，支持多平台语音发送
"""

from .base import BaseVoiceSender, VoiceSendResult
from .wechat_work import WeChatWorkSender
from .personal_wechat import PersonalWeChatSender
from .factory import create_sender, SenderType

__all__ = [
    "BaseVoiceSender",
    "VoiceSendResult",
    "WeChatWorkSender",
    "PersonalWeChatSender",
    "create_sender",
    "SenderType",
]
