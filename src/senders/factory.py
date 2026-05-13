"""
发送器工厂模块

提供统一的方式创建不同平台的发送器
"""

from enum import Enum
from typing import Optional, Callable


class SenderType(Enum):
    """发送器类型"""
    WECHAT_WORK = "wechat_work"           # 企业微信
    PERSONAL_WECHAT = "personal_wechat"   # 个人微信
    # 未来可扩展：
    # DINGTALK = "dingtalk"               # 钉钉
    # FEISHU = "feishu"                   # 飞书


def create_sender(
    sender_type: SenderType,
    # 企业微信参数
    corp_id: Optional[str] = None,
    agent_id: Optional[int] = None,
    secret: Optional[str] = None,
    # 个人微信参数
    send_func: Optional[Callable[[str, str], bool]] = None,
    # 通用参数
    allow_fallback: bool = True
):
    """
    创建对应平台的发送器
    
    Args:
        sender_type: 发送器类型（SenderType 枚举）
        
        # 企业微信参数
        corp_id: 企业微信 CorpID
        agent_id: 企业微信 AgentID
        secret: 企业微信 Secret
        
        # 个人微信参数
        send_func: 发送函数，接收 (filepath, user_id) 参数
        
        # 通用参数
        allow_fallback: 是否允许回退（企业微信专用）
    
    Returns:
        BaseVoiceSender 子类的实例
    
    Examples:
        # 创建企业微信发送器
        sender = create_sender(
            SenderType.WECHAT_WORK,
            corp_id="ww...",
            agent_id=1000002,
            secret="..."
        )
        
        # 创建个人微信发送器
        sender = create_sender(
            SenderType.PERSONAL_WECHAT,
            send_func=your_send_function
        )
    """
    if sender_type == SenderType.WECHAT_WORK:
        from .wechat_work import WeChatWorkSender
        
        if not all([corp_id, agent_id, secret]):
            raise ValueError("企业微信发送器需要提供 corp_id, agent_id, secret")
        
        return WeChatWorkSender(
            corp_id=corp_id,
            agent_id=agent_id,
            secret=secret,
            allow_fallback=allow_fallback
        )
    
    elif sender_type == SenderType.PERSONAL_WECHAT:
        from .personal_wechat import PersonalWeChatSender
        
        return PersonalWeChatSender(send_func=send_func)
    
    else:
        raise ValueError(f"不支持的发送器类型: {sender_type}")


def get_sender_info(sender_type: SenderType) -> dict:
    """
    获取发送器信息
    
    Args:
        sender_type: 发送器类型
    
    Returns:
        包含发送器详细信息的字典
    """
    info_map = {
        SenderType.WECHAT_WORK: {
            "name": "企业微信",
            "supports_real_voice": True,
            "formats": ["amr", "mp3"],
            "description": "支持真正的语音消息（AMR格式）",
            "requires": ["corp_id", "agent_id", "secret"]
        },
        SenderType.PERSONAL_WECHAT: {
            "name": "个人微信",
            "supports_real_voice": False,
            "formats": ["mp3"],
            "description": "只能发送MP3文件作为语音替代",
            "requires": ["send_func（可选）"]
        }
    }
    
    return info_map.get(sender_type, {"error": "未知类型"})


def list_supported_platforms() -> list:
    """
    列出所有支持的平台
    
    Returns:
        平台信息列表
    """
    return [
        {
            "type": SenderType.WECHAT_WORK.value,
            **get_sender_info(SenderType.WECHAT_WORK)
        },
        {
            "type": SenderType.PERSONAL_WECHAT.value,
            **get_sender_info(SenderType.PERSONAL_WECHAT)
        }
    ]
