"""
企业微信 API 语音发送模块
"""

import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


WECHAT_ERROR_CODES = {
    60020: "IP 未在白名单，需添加服务器 IP 到企业微信后台",
    40014: "access_token 无效或过期",
    40001: "secret 错误",
    40004: "无效的媒体文件类型",
    40006: "文件太大（语音最大 2MB）",
    40013: "无效的 CorpID",
    60003: "不合法的 UserID",
}


@dataclass
class WeChatWorkConfig:
    """企业微信配置"""
    corp_id: str
    agent_id: int
    secret: str


class WeChatWorkAPI:
    """企业微信 API 客户端"""
    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"
    
    def __init__(self, config: WeChatWorkConfig):
        self.config = config
        self._token: Optional[str] = None
        self._token_expire: float = 0
        self.session = requests.Session()
    
    def _get_token(self) -> str:
        """获取 access_token"""
        if self._token and time.time() < self._token_expire:
            return self._token
        
        url = f"{self.BASE_URL}/gettoken"
        params = {"corpid": self.config.corp_id, "corpsecret": self.config.secret}
        
        response = self.session.get(url, params=params, timeout=30)
        result = response.json()
        
        if result.get("errcode") != 0:
            errcode = result.get("errcode")
            suggestion = WECHAT_ERROR_CODES.get(errcode, "未知错误")
            raise RuntimeError(f"获取 token 失败 [{errcode}]: {result.get('errmsg')}\n建议: {suggestion}")
        
        self._token = result["access_token"]
        self._token_expire = time.time() + result.get("expires_in", 7200) - 300
        return self._token
    
    def upload_media(self, file_path: str, media_type: str = "voice") -> str:
        """上传媒体文件"""
        token = self._get_token()
        url = f"{self.BASE_URL}/media/upload"
        params = {"access_token": token, "type": media_type}
        
        # 检查文件大小（语音最大 2MB）
        file_size = Path(file_path).stat().st_size
        if media_type == "voice" and file_size > 2 * 1024 * 1024:
            raise RuntimeError(f"语音文件过大 ({file_size / 1024 / 1024:.1f}MB)，超过 2MB 限制")
        
        with open(file_path, "rb") as f:
            files = {"media": (Path(file_path).name, f)}
            response = self.session.post(url, params=params, files=files, timeout=60)
        
        result = response.json()
        if result.get("errcode") != 0:
            raise RuntimeError(f"上传失败: {result.get('errmsg')}")
        
        return result["media_id"]
    
    def send_voice_message(self, user_id: str, media_id: str) -> dict:
        """发送语音消息"""
        token = self._get_token()
        url = f"{self.BASE_URL}/message/send"
        params = {"access_token": token}
        
        data = {
            "touser": user_id,
            "msgtype": "voice",
            "agentid": self.config.agent_id,
            "voice": {"media_id": media_id},
            "safe": 0
        }
        
        response = self.session.post(url, params=params, json=data, timeout=30)
        result = response.json()
        
        if result.get("errcode") != 0:
            errcode = result.get("errcode")
            suggestion = WECHAT_ERROR_CODES.get(errcode, "")
            raise RuntimeError(f"发送失败 [{errcode}]: {result.get('errmsg')}\n{suggestion}")
        
        return result
    
    def send_text_message(self, user_id: str, content: str) -> dict:
        """发送文本消息"""
        token = self._get_token()
        url = f"{self.BASE_URL}/message/send"
        params = {"access_token": token}
        
        data = {
            "touser": user_id,
            "msgtype": "text",
            "agentid": self.config.agent_id,
            "text": {"content": content},
            "safe": 0
        }
        
        response = self.session.post(url, params=params, json=data, timeout=30)
        result = response.json()
        
        if result.get("errcode") != 0:
            raise RuntimeError(f"发送失败: {result.get('errmsg')}")
        
        return result


class WeChatWorkVoiceSender:
    """企业微信语音发送器"""
    
    def __init__(self, corp_id: str, agent_id: int, secret: str, allow_fallback: bool = False):
        self.config = WeChatWorkConfig(corp_id=corp_id, agent_id=agent_id, secret=secret)
        self.api = WeChatWorkAPI(self.config)
        self.allow_fallback = allow_fallback
    
    async def text_to_voice_and_send(self, text: str, user_id: str, voice: str = None) -> dict:
        """文字转语音并发送"""
        from .tts import TTSService
        from .audio import AudioConverter
        
        # 1. 生成语音
        tts = TTSService()
        tts_result = await tts.text_to_speech(text, voice=voice)
        mp3_path = tts_result["filepath"]
        
        # 2. 尝试发送语音
        try:
            converter = AudioConverter()
            amr_path = converter.mp3_to_amr(mp3_path)
            media_id = self.api.upload_media(amr_path, media_type="voice")
            send_result = self.api.send_voice_message(user_id, media_id)
            
            return {
                "success": True,
                "type": "voice",
                "filepath": mp3_path,
                "send_result": send_result
            }
        
        except Exception as voice_error:
            if not self.allow_fallback:
                raise RuntimeError(
                    f"语音发送失败: {voice_error}\n"
                    "建议: 设置 allow_fallback=True 以发送 MP3 文件"
                )
            
            # 降级为 MP3 文件
            try:
                media_id = self.api.upload_media(mp3_path, media_type="file")
                return {
                    "success": True,
                    "type": "file",
                    "fallback": True,
                    "filepath": mp3_path
                }
            except Exception as file_error:
                # 最后尝试文本
                self.api.send_text_message(user_id, f"[语音发送失败]\n{text[:500]}")
                return {
                    "success": True,
                    "type": "text",
                    "fallback": True
                }
