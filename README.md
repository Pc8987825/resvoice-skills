<h1 align="center">ResVoice.skills (应声)</h1>

> 让 Agent 开口说话

## 核心价值

**零配置，开箱即用。**

Agent 发现用户需要语音时，自动调用本 Skill 生成并发送语音。

```python
from skills.ResVoice import send_voice_message

# Agent 调用
result = await send_voice_message("你好，我是你的 AI 助手")
```

## 特性

| 特性 | 说明 |
|------|------|
| **零配置** | 内置 Edge TTS，无需 API 配置 |
| **自修复** | 缺失依赖自动安装 |
| **结构化错误** | Agent 能判断修复或提示用户 |
| **多引擎** | Edge → gTTS → pyttsx3 自动回退 |
| **双平台** | 企业微信（AMR）/ 个人微信（MP3）|

## 快速开始

```python
from skills.ResVoice import send_voice_message, check_setup

# 可选：环境检查
if not check_setup()["ready"]:
    from skills.ResVoice import auto_setup
    auto_setup()  # 自动安装依赖

# 生成语音
result = await send_voice_message("你好，世界")
print(result["filepath"])  # 语音文件路径
```

## 发送到微信

```python
# 企业微信（真正语音）
result = await send_voice_message(
    text="会议提醒",
    to_user="UserID",
    platform="wechat_work",
    corp_id="ww...",
    agent_id=1000002,
    secret="..."
)

# 个人微信（MP3文件）
result = await send_voice_message(
    text="你好",
    to_user="filehelper",
    platform="personal_wechat",
    send_func=your_send_function
)
```

## 返回值

```python
{
    "success": True,
    "filepath": "/path/to/audio.mp3",
    "is_real_voice": False,  # 个人微信为 MP3 文件
    "sent": True
}

# 错误时
{
    "success": False,
    "error_type": "MISSING_DEPENDENCY",
    "message": "缺少 edge-tts",
    "fix_command": "pip install edge-tts",
    "auto_fixable": True
}
```

## 安装

```bash
pip install -r requirements.txt
```

**系统依赖**: ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt-get install ffmpeg

# Windows
winget install Gyan.FFmpeg
```

## 文件结构

```
ResVoice/
├── src/
│   ├── senders/        # 多平台发送器
│   ├── environment.py  # 环境检测与自修复
│   ├── tts.py         # TTS 核心（多引擎）
│   └── ...
├── __init__.py        # 核心接口
├── SKILL.md           # Agent 调用文档
└── requirements.txt
```

## 核心设计

**"import 即用，出错能修"**

- ✅ 自动检测并安装缺失依赖
- ✅ 结构化错误，Agent 能处理
- ✅ 多引擎自动回退，保证可用
- ✅ 企业微信 + 个人微信双支持

## License

MIT
