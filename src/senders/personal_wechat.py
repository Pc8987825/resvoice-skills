"""
个人微信语音发送器

注意：个人微信没有官方 API，只能通过第三方库（如 itchat、wxpy）发送文件
MP3 文件会以"文件"形式发送，而非真正的语音消息
"""

import os
from typing import Optional, Callable
from .base import BaseVoiceSender, VoiceSendResult


class PersonalWeChatSender(BaseVoiceSender):
    """
    个人微信语音发送器
    
    由于个人微信限制，只能发送 MP3 文件作为"语音"的替代形式
    接收方需要点击文件才能播放
    
    使用方式：
        # 方式 1：提供发送函数
        sender = PersonalWeChatSender(send_func=your_send_function)
        
        # 方式 2：仅生成文件，自行发送
        sender = PersonalWeChatSender()
        result = await sender.send_voice("你好", "filehelper")
        # 然后使用你自己的方式发送 result.filepath
    """
    
    def __init__(
        self,
        send_func: Optional[Callable[[str, str], bool]] = None,
        output_dir: Optional[str] = None
    ):
        """
        初始化个人微信发送器
        
        Args:
            send_func: 可选的发送函数，接收 (filepath, user_id) 参数
                      如果提供，会自动调用此函数发送文件
            output_dir: 音频文件输出目录
        """
        super().__init__("personal_wechat")
        self.send_func = send_func
        self.output_dir = output_dir
    
    @property
    def supports_real_voice(self) -> bool:
        """个人微信不支持真正的语音消息，只能发文件"""
        return False
    
    @property
    def supported_formats(self) -> list:
        """只支持 MP3 格式"""
        return ["mp3"]
    
    async def send_voice(
        self,
        text: str,
        user_id: str,
        voice: Optional[str] = None
    ) -> VoiceSendResult:
        """
        生成语音文件并发送（或返回文件路径）
        
        对于个人微信：
        - 生成 MP3 文件
        - 如果提供了 send_func，自动调用发送
        - 否则只返回文件路径，由调用方自行发送
        
        Args:
            text: 要转换的文字
            user_id: 目标用户ID（如 filehelper、好友昵称等）
            voice: 音色选择
        
        Returns:
            VoiceSendResult，其中 is_real_voice=False 表示这是文件形式的"语音"
        """
        try:
            # 1. 生成 MP3 音频
            tts_result = await self._generate_audio(text, voice)
            mp3_path = tts_result["filepath"]
            
            # 2. 如果提供了发送函数，自动发送
            sent = False
            send_message = "MP3 文件已生成"
            
            if self.send_func:
                try:
                    send_success = self.send_func(mp3_path, user_id)
                    if send_success:
                        sent = True
                        send_message = "MP3 语音文件已发送（以文件形式）"
                    else:
                        send_message = "发送函数返回失败，请手动发送文件"
                except Exception as e:
                    send_message = f"发送失败: {e}，请手动发送文件"
            else:
                send_message = "未提供发送函数，请使用文件路径自行发送"
            
            return VoiceSendResult(
                success=True,
                platform=self.platform_name,
                is_real_voice=False,  # 明确标记这不是真正的语音
                format="mp3",
                filepath=mp3_path,
                message=send_message,
                sent=sent
            )
        
        except Exception as e:
            return VoiceSendResult(
                success=False,
                platform=self.platform_name,
                is_real_voice=False,
                format="",
                filepath="",
                message=f"生成失败: {e}",
                sent=False
            )
    
    def set_send_func(self, send_func: Callable[[str, str], bool]):
        """
        动态设置发送函数
        
        Args:
            send_func: 发送函数，接收 (filepath, user_id) 参数，返回是否成功
        """
        self.send_func = send_func


# 预置的发送函数示例（供参考）
def create_itchat_sender():
    """
    创建基于 itchat 的发送函数
    
    使用示例：
        import itchat
        itchat.auto_login()
        
        sender = PersonalWeChatSender(
            send_func=create_itchat_sender()
        )
    """
    try:
        import itchat
        
        def send_file(filepath: str, user_id: str) -> bool:
            """使用 itchat 发送文件"""
            try:
                itchat.send_file(filepath, toUserName=user_id)
                return True
            except Exception as e:
                print(f"itchat 发送失败: {e}")
                return False
        
        return send_file
    except ImportError:
        print("未安装 itchat，请运行: pip install itchat")
        return None


def create_wxpy_sender(bot):
    """
    创建基于 wxpy 的发送函数
    
    使用示例：
        from wxpy import Bot
        bot = Bot()
        
        sender = PersonalWeChatSender(
            send_func=create_wxpy_sender(bot)
        )
    """
    try:
        from wxpy import Bot
        
        def send_file(filepath: str, user_id: str) -> bool:
            """使用 wxpy 发送文件"""
            try:
                friend = bot.friends().search(user_id)[0]
                friend.send_file(filepath)
                return True
            except Exception as e:
                print(f"wxpy 发送失败: {e}")
                return False
        
        return send_file
    except ImportError:
        print("未安装 wxpy，请运行: pip install wxpy")
        return None
