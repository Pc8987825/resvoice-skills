"""
多引擎 TTS 服务
支持 Edge TTS(默认)、gTTS、pyttsx3 三种引擎，自动回退
"""

import os
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum


class TTSEngine(Enum):
    """TTS 引擎类型"""
    EDGE = "edge"
    GTTS = "gtts"
    PYTTSX3 = "pyttsx3"


class TTSService:
    """多引擎文字转语音服务"""
    
    DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
    
    EDGE_VOICES = {
        "zh-CN-XiaoxiaoNeural": "中文-女声（晓晓）",
        "zh-CN-XiaoyiNeural": "中文-女声（晓伊）",
        "zh-CN-YunjianNeural": "中文-男声（云健）",
        "zh-CN-YunxiNeural": "中文-男声（云希）",
        "zh-CN-YunxiaNeural": "中文-男声（云夏）",
        "zh-CN-YunyangNeural": "中文-男声（云扬）",
        "en-US-AriaNeural": "英文-女声（Aria）",
        "en-US-GuyNeural": "英文-男声（Guy）",
    }
    
    def __init__(
        self, 
        output_dir: Optional[str] = None,
        default_engine: TTSEngine = TTSEngine.EDGE,
        auto_fallback: bool = True
    ):
        from .utils import get_output_dir
        self.output_dir = get_output_dir(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.default_engine = default_engine
        self.auto_fallback = auto_fallback
    
    async def text_to_speech(
        self, 
        text: str, 
        voice: Optional[str] = None,
        engine: Optional[TTSEngine] = None,
        rate: str = "+0%",
        volume: str = "+0%",
        pitch: str = "+0Hz",
        **kwargs
    ) -> dict:
        """将文字转换为语音"""
        if not text or not text.strip():
            raise ValueError("文本内容不能为空")
        
        use_engine = engine or self.default_engine
        engines_to_try = [use_engine]
        
        if self.auto_fallback and use_engine in [TTSEngine.EDGE, TTSEngine.GTTS]:
            if TTSEngine.GTTS not in engines_to_try:
                engines_to_try.append(TTSEngine.GTTS)
            if TTSEngine.PYTTSX3 not in engines_to_try:
                engines_to_try.append(TTSEngine.PYTTSX3)
        
        last_error = None
        for try_engine in engines_to_try:
            try:
                if try_engine == TTSEngine.EDGE:
                    return await self._use_edge_tts(text, voice, rate, volume, pitch)
                elif try_engine == TTSEngine.GTTS:
                    return await self._use_gtts(text)
                elif try_engine == TTSEngine.PYTTSX3:
                    return await self._use_pyttsx3(text)
            except Exception as e:
                last_error = e
                print(f"⚠️ {try_engine.value} 引擎失败: {e}")
                continue
        
        raise RuntimeError(f"所有 TTS 引擎均失败，最后错误: {last_error}")
    
    async def _use_edge_tts(self, text: str, voice: Optional[str], rate: str, volume: str, pitch: str) -> dict:
        """使用 Edge TTS"""
        import edge_tts
        
        voice = voice or self.DEFAULT_VOICE
        file_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_edge_{timestamp}_{file_id}.mp3"
        filepath = self.output_dir / filename
        
        communicate = edge_tts.Communicate(
            text=text, voice=voice, rate=rate, volume=volume, pitch=pitch
        )
        await communicate.save(str(filepath))
        
        return self._build_result(filepath, filename, text, voice, TTSEngine.EDGE)
    
    async def _use_gtts(self, text: str) -> dict:
        """使用 gTTS"""
        from gtts import gTTS
        
        file_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_gtts_{timestamp}_{file_id}.mp3"
        filepath = self.output_dir / filename
        
        tts = gTTS(text=text, lang='zh-cn', slow=False)
        tts.save(str(filepath))
        
        return self._build_result(filepath, filename, text, "gtts-zh", TTSEngine.GTTS)
    
    def _is_headless_server(self) -> bool:
        """检测是否为无音频设备的服务器环境"""
        import platform
        if os.getenv("HEADLESS") == "1":
            return True
        if os.getenv("DISPLAY") is None and platform.system() != "Windows":
            return True
        if platform.system() == "Linux" and not os.path.exists("/dev/audio"):
            if not os.path.exists("/dev/snd"):
                return True
        return False
    
    async def _use_pyttsx3(self, text: str) -> dict:
        """使用 pyttsx3（本地离线）"""
        import pyttsx3
        
        if self._is_headless_server():
            raise RuntimeError(
                "pyttsx3 在无音频设备的服务器环境无法运行\n"
                "建议: 1) 设置环境变量 HEADLESS=1 跳过 pyttsx3\n"
                "      2) 使用 Edge TTS 或 gTTS 引擎"
            )
        
        file_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_local_{timestamp}_{file_id}.mp3"
        filepath = self.output_dir / filename
        
        def run_pyttsx3():
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.save_to_file(text, str(filepath))
            engine.runAndWait()
        
        loop = asyncio.get_event_loop()
        await asyncio.wait_for(
            loop.run_in_executor(None, run_pyttsx3),
            timeout=10.0
        )
        
        return self._build_result(filepath, filename, text, "local", TTSEngine.PYTTSX3)
    
    def _build_result(self, filepath: Path, filename: str, text: str, voice: str, engine: TTSEngine) -> dict:
        """构建返回结果"""
        from .utils import format_file_size
        file_size = filepath.stat().st_size
        
        return {
            "success": True,
            "filename": filename,
            "filepath": str(filepath),
            "file_size": file_size,
            "file_size_human": format_file_size(file_size),
            "voice": voice,
            "voice_name": self.EDGE_VOICES.get(voice, voice),
            "engine": engine.value,
            "text_length": len(text),
            "text_preview": text[:50] + "..." if len(text) > 50 else text,
            "created_at": datetime.now().isoformat()
        }
    
    async def list_voices(self, language: Optional[str] = "zh-CN") -> list:
        """获取可用的语音列表"""
        try:
            from edge_tts import VoicesManager
            voices_manager = await VoicesManager.create()
            voices = voices_manager.voices
            
            if language:
                voices = [v for v in voices if v["Locale"].startswith(language)]
            
            return [
                {
                    "name": v["ShortName"],
                    "locale": v["Locale"],
                    "gender": v["Gender"],
                    "friendly_name": v.get("FriendlyName", v["ShortName"]),
                    "engine": "edge"
                }
                for v in voices
            ]
        except Exception:
            return [
                {"name": "local-male", "locale": "zh-CN", "gender": "Male", "engine": "pyttsx3"},
                {"name": "local-female", "locale": "zh-CN", "gender": "Female", "engine": "pyttsx3"},
                {"name": "gtts-zh", "locale": "zh-CN", "gender": "Female", "engine": "gtts"},
            ]


def text_to_speech_sync(
    text: str, 
    voice: Optional[str] = None,
    engine: Optional[str] = None,
    output_dir: Optional[str] = None
) -> dict:
    """同步方式调用文字转语音"""
    service = TTSService(output_dir)
    engine_enum = TTSEngine(engine) if engine else TTSEngine.EDGE
    return asyncio.run(service.text_to_speech(text, voice, engine_enum))


def text_to_speech_simple(text: str, output_path: Optional[str] = None) -> str:
    """最简单的文字转语音，返回文件路径"""
    service = TTSService()
    result = asyncio.run(service.text_to_speech(text))
    return result["filepath"]
