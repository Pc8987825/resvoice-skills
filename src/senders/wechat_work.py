"""
企业微信语音发送器
支持真正的语音消息（AMR 格式）
"""

from typing import Optional
from .base import BaseVoiceSender, VoiceSendResult
from ..wechat import WeChatWorkAPI, WeChatWorkConfig


class WeChatWorkSender(BaseVoiceSender):
    """
    企业微信语音发送器
    
    支持发送真正的语音消息（AMR 格式），在聊天中显示为可播放的语音
    """
    
    def __init__(
        self,
        corp_id: str,
        agent_id: int,
        secret: str,
        allow_fallback: bool = True
    ):
        super().__init__("wechat_work")
        self.config = WeChatWorkConfig(corp_id=corp_id, agent_id=agent_id, secret=secret)
        self.api = WeChatWorkAPI(self.config)
        self.allow_fallback = allow_fallback
    
    @property
    def supports_real_voice(self) -> bool:
        """企业微信支持真正的语音消息"""
        return True
    
    @property
    def supported_formats(self) -> list:
        """支持 AMR 和 MP3"""
        return ["amr", "mp3"]
    
    async def send_voice(
        self,
        text: str,
        user_id: str,
        voice: Optional[str] = None
    ) -> VoiceSendResult:
        """
        发送语音消息到企业微信
        
        流程：
        1. 生成 MP3 音频
        2. 转换为 AMR 格式
        3. 上传并发送语音消息
        4. 失败时回退到文件发送
        """
        from ..audio import AudioConverter
        
        try:
            # 1. 生成音频
            tts_result = await self._generate_audio(text, voice)
            mp3_path = tts_result["filepath"]
            
            # 2. 尝试转换为 AMR 并发送真正的语音
            try:
                converter = AudioConverter()
                amr_path = converter.mp3_to_amr(mp3_path)
                media_id = self.api.upload_media(amr_path, media_type="voice")
                self.api.send_voice_message(user_id, media_id)
                
                return VoiceSendResult(
                    success=True,
                    platform=self.platform_name,
                    is_real_voice=True,
                    format="amr",
                    filepath=amr_path,
                    message="已发送企业微信语音消息",
                    sent=True
                )
            
            except Exception as e:
                if not self.allow_fallback:
                    raise
                
                # 回退：发送 MP3 文件
                media_id = self.api.upload_media(mp3_path, media_type="file")
                return VoiceSendResult(
                    success=True,
                    platform=self.platform_name,
                    is_real_voice=False,
                    format="mp3",
                    filepath=mp3_path,
                    message=f"AMR 转换失败，已作为文件发送: {e}",
                    sent=True
                )
        
        except Exception as e:
            return VoiceSendResult(
                success=False,
                platform=self.platform_name,
                is_real_voice=False,
                format="",
                filepath="",
                message=f"发送失败: {e}",
                sent=False
            )
