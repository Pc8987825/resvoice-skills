"""
音频转换模块
"""

import os
import subprocess
from pathlib import Path
from typing import Optional


class AudioConverter:
    """音频格式转换器"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """检查 ffmpeg 是否可用"""
        try:
            subprocess.run([self.ffmpeg_path, "-version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "ffmpeg 未安装或未找到\n"
                "安装命令:\n"
                "  Ubuntu/Debian: sudo apt-get install ffmpeg\n"
                "  macOS: brew install ffmpeg\n"
                "  Windows: 下载 https://www.gyan.dev/ffmpeg/builds/"
            )
    
    def check_amr_support(self) -> bool:
        """检查是否支持 AMR 编码"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-encoders"],
                capture_output=True,
                text=True
            )
            return "amr_nb" in result.stdout or "libopencore_amrnb" in result.stdout
        except Exception:
            return False
    
    def mp3_to_amr(self, mp3_path: str, amr_path: Optional[str] = None) -> str:
        """MP3 转 AMR"""
        if not self.check_amr_support():
            raise RuntimeError(
                "ffmpeg 缺少 AMR 编码器\n"
                "安装命令: sudo apt-get install ffmpeg libavcodec-extra"
            )
        
        mp3_file = Path(mp3_path)
        if not mp3_file.exists():
            raise FileNotFoundError(f"MP3 文件不存在: {mp3_path}")
        
        if amr_path is None:
            amr_path = str(mp3_file.with_suffix(".amr"))
        
        cmd = [
            self.ffmpeg_path,
            "-i", str(mp3_path),
            "-ar", "8000",
            "-ac", "1",
            "-c:a", "libopencore_amrnb",
            "-y",
            str(amr_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"AMR 转换失败: {result.stderr}")
        
        return amr_path
    
    def get_audio_info(self, file_path: str) -> dict:
        """获取音频文件信息"""
        cmd = [
            self.ffmpeg_path,
            "-i", file_path,
            "-hide_banner"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        info = {"path": file_path}
        
        # 解析时长
        for line in result.stderr.split('\n'):
            if 'Duration' in line:
                parts = line.split(',')
                for part in parts:
                    if 'Duration' in part:
                        duration_str = part.split(':')[1].strip()
                        info['duration'] = duration_str
                    if 'bitrate' in part:
                        info['bitrate'] = part.strip()
                break
        
        # 文件大小
        file_size = Path(file_path).stat().st_size
        info['size'] = file_size
        info['size_human'] = self._format_size(file_size)
        
        return info
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} GB"
