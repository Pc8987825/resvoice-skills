"""
平台检测与自动适配模块

自动检测 OpenClaw 环境，提供对应的发送函数
"""

import os
import json
from typing import Dict, Callable, Optional, Any
from dataclasses import dataclass


@dataclass
class PlatformInfo:
    """平台信息"""
    platform: str                    # "openclaw_weixin" / "wechat_work" / "unknown"
    channel: str                     # 原始 channel 标识
    chat_id: str                     # 用户ID
    account_id: str                  # 机器人账号
    can_send_real_voice: bool        # 是否能发真正语音
    send_func: Optional[Callable]    # 发送函数（已配置好）
    meta: Dict[str, Any]             # 完整元数据


def detect_openclaw_meta() -> Optional[Dict]:
    """
    检测 OpenClaw 元数据
    
    从环境变量 OPENCLAW_META 或标准输入读取
    
    Returns:
        元数据字典，或 None（非 OpenClaw 环境）
    """
    # 方式 1：环境变量
    meta_env = os.getenv("OPENCLAW_META")
    if meta_env:
        try:
            return json.loads(meta_env)
        except json.JSONDecodeError:
            pass
    
    # 方式 2：文件（OpenClaw 可能写入临时文件）
    meta_file = os.getenv("OPENCLAW_META_FILE")
    if meta_file and os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
    return None


def create_openclaw_sender(meta: Dict) -> Callable[[str, str], bool]:
    """
    创建 OpenClaw 发送函数
    
    Args:
        meta: OpenClaw 元数据
    
    Returns:
        发送函数：send_func(filepath, user_id) -> bool
    """
    chat_id = meta.get("chat_id", "")
    channel = meta.get("channel", "")
    
    def send_file(filepath: str, user_id: str = None) -> bool:
        """
        发送文件到微信
        
        使用 OpenClaw 的 message 工具
        """
        try:
            # 尝试导入 OpenClaw 的工具
            # 方式 1：直接调用 OpenClaw 的 message 函数
            try:
                from openclaw.tools import message
                
                result = message(
                    action="send",
                    media=filepath,
                    # 可选参数
                    channel=channel,
                    target=user_id or chat_id
                )
                
                # 检查结果
                if isinstance(result, dict):
                    return result.get("status") == "sent" or result.get("success", False)
                return True
                
            except ImportError:
                pass
            
            # 方式 2：通过 subprocess 调用 OpenClaw CLI
            import subprocess
            import json
            
            cmd = {
                "tool": "message",
                "params": {
                    "action": "send",
                    "media": filepath,
                    "channel": channel,
                    "target": user_id or chat_id
                }
            }
            
            result = subprocess.run(
                ["openclaw", "tool", "invoke"],
                input=json.dumps(cmd),
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"OpenClaw 发送失败: {e}")
            return False
    
    return send_file


def detect_platform() -> PlatformInfo:
    """
    自动检测平台并返回配置信息
    
    Returns:
        PlatformInfo 包含平台类型和配置好的发送函数
    
    使用示例：
        info = detect_platform()
        
        # 直接调用，无需手动配置
        result = await send_voice_message(
            "你好",
            platform=info.platform,
            send_func=info.send_func
        )
    """
    # 检测 OpenClaw 环境
    meta = detect_openclaw_meta()
    
    if meta:
        channel = meta.get("channel", "")
        chat_id = meta.get("chat_id", "")
        account_id = meta.get("account_id", "")
        
        # 判断平台类型
        if channel == "openclaw-weixin" or "@im.wechat" in chat_id:
            # 个人微信 - 只能发 MP3 文件
            return PlatformInfo(
                platform="openclaw_weixin",
                channel=channel,
                chat_id=chat_id,
                account_id=account_id,
                can_send_real_voice=False,
                send_func=create_openclaw_sender(meta),
                meta=meta
            )
        
        elif channel == "wechat-work":
            # 企业微信 - 可以发真正语音
            return PlatformInfo(
                platform="wechat_work",
                channel=channel,
                chat_id=chat_id,
                account_id=account_id,
                can_send_real_voice=True,
                send_func=create_openclaw_sender(meta),
                meta=meta
            )
        
        else:
            # 其他 OpenClaw 渠道
            return PlatformInfo(
                platform="openclaw_other",
                channel=channel,
                chat_id=chat_id,
                account_id=account_id,
                can_send_real_voice=False,
                send_func=create_openclaw_sender(meta),
                meta=meta
            )
    
    # 非 OpenClaw 环境
    return PlatformInfo(
        platform="unknown",
        channel="unknown",
        chat_id="",
        account_id="",
        can_send_real_voice=False,
        send_func=None,
        meta={}
    )


def is_openclaw_environment() -> bool:
    """检查是否在 OpenClaw 环境中"""
    return detect_openclaw_meta() is not None


# 便捷函数：一键发送（自动检测平台）
async def send_voice_auto(text: str, voice: str = None, **kwargs) -> dict:
    """
    自动检测平台并发送语音
    
    这是最简单的使用方式，无需手动配置平台参数
    
    Args:
        text: 要转换的文字
        voice: 音色选择
        **kwargs: 其他参数（如 rate, volume 等）
    
    Returns:
        发送结果字典
    
    使用示例：
        from skills.ResVoice import send_voice_auto
        
        # 一行代码搞定，自动检测 OpenClaw 环境
        result = await send_voice_auto("你好，世界！")
    """
    from .senders import create_sender, SenderType
    from .tts import TTSService
    
    # 检测平台
    info = detect_platform()
    
    if info.platform == "unknown":
        # 非 OpenClaw 环境，只生成文件
        tts = TTSService()
        result = await tts.text_to_speech(text=text, voice=voice, **kwargs)
        return {
            "success": True,
            "filepath": result["filepath"],
            "platform": "unknown",
            "is_real_voice": False,
            "sent": False,
            "note": "非 OpenClaw 环境，仅生成文件"
        }
    
    # OpenClaw 环境
    if info.platform == "openclaw_weixin":
        # 个人微信 - 使用 PersonalWeChatSender
        sender = create_sender(
            SenderType.PERSONAL_WECHAT,
            send_func=info.send_func
        )
    elif info.platform == "wechat_work":
        # 企业微信 - 需要 corp_id 等参数
        # 尝试从环境变量获取
        corp_id = os.getenv("WECHAT_WORK_CORP_ID")
        agent_id = os.getenv("WECHAT_WORK_AGENT_ID")
        secret = os.getenv("WECHAT_WORK_SECRET")
        
        if all([corp_id, agent_id, secret]):
            sender = create_sender(
                SenderType.WECHAT_WORK,
                corp_id=corp_id,
                agent_id=int(agent_id),
                secret=secret
            )
        else:
            # 没有企业微信配置，降级为文件发送
            sender = create_sender(
                SenderType.PERSONAL_WECHAT,
                send_func=info.send_func
            )
    else:
        # 其他渠道，使用文件发送
        sender = create_sender(
            SenderType.PERSONAL_WECHAT,
            send_func=info.send_func
        )
    
    # 发送语音
    result = await sender.send_voice(
        text=text,
        user_id=info.chat_id,
        voice=voice
    )
    
    return result.to_dict()