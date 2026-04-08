# ResVoice.skills (回应之声)

## 🎯 核心优势：零配置 TTS

**ResVoice 自带完整 TTS 能力，无需配置 OpenAI/ElevenLabs API！**

```python
from skills.ResVoice import send_voice_message

# 零配置，开箱即用
result = await send_voice_message("你好梦哥")
print(f"语音文件: {result['filepath']}")
```

## 前置检查（安装前必须）

运行以下命令，确认输出包含 `amr_nb`：

```bash
ffmpeg -encoders | grep amr
```

- ✅ 看到 `libopencore_amrnb` → 可以继续安装
- ❌ 无输出 → 先执行下方「安装系统依赖」

## 基本信息

| 项目 | 内容 |
|------|------|
| **名称** | ResVoice.skills |
| **版本** | 0.1.5-beta |
| **作者** | 远梦 |
| **描述** | 让 AI 开口说话，支持文字转语音并发送微信语音消息 |
| **分类** | 语音/通讯 |

## OpenClaw 能力声明

```yaml
capabilities:
  tts:
    provider: edge_tts
    description: "内置 Edge TTS，无需外部 API 配置"
    voices:
      - zh-CN-XiaoxiaoNeural
      - zh-CN-YunxiNeural
      - zh-CN-YunjianNeural
      - zh-CN-XiaoyiNeural
      - zh-CN-YunyangNeural
      - zh-CN-XiaochenNeural
      - zh-CN-XiaohanNeural
      - en-US-AriaNeural
      - en-US-GuyNeural
    supports_clone: false
    async: true
    offline_fallback: true
  voice_sender:
    channels:
      - wechat_work
    formats:
      - mp3
      - amr
  audio_processing:
    conversion:
      - mp3_to_amr
    requires_ffmpeg: true
```

## 功能特性

- 🎙️ **零配置 TTS** - 内置 Edge TTS，无需 OpenAI/ElevenLabs API
- 🔄 **音频转换** - 自动处理 MP3 → AMR 微信语音格式
- 💬 **微信发送** - 企业微信语音消息发送
- 🎭 **多音色支持** - 男声、女声、中英文等多种语音选项
- 📦 **离线可用** - pyttsx3 引擎无需网络
- 🚀 **OpenClaw 集成** - 专用 `send_voice_message()` 函数

## 安装

### 1. 安装系统依赖（必需！）

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg libavcodec-extra
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
1. 下载 https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z
2. 解压到 `C:\ffmpeg`
3. 添加到 PATH

### 2. 验证安装

```bash
ffmpeg -encoders | grep amr
# 必须看到 libopencore_amrnb，否则无法发语音！
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 基础用法 - 文字转语音

```python
from skills.ResVoice import TTSService
import asyncio

async def main():
    tts = TTSService()
    
    # 自动选择最佳引擎（Edge → gTTS → pyttsx3）
    result = await tts.text_to_speech("你好，我在")
    print(f"语音文件: {result['filepath']}")
    print(f"使用引擎: {result['engine']}")

asyncio.run(main())
```

### 指定引擎

```python
from skills.ResVoice import TTSService, TTSEngine

# 使用本地离线引擎（无需网络）
tts = TTSService()
result = await tts.text_to_speech(
    text="离线测试",
    engine=TTSEngine.PYTTSX3
)

# 使用 Google TTS
result = await tts.text_to_speech(
    text="Google语音",
    engine=TTSEngine.GTTS
)
```

### 同步调用（非异步代码）

```python
from skills.ResVoice import text_to_speech_sync

# 同步方式调用
result = text_to_speech_sync("同步测试文本")
print(result['filepath'])
```

### OpenClaw 专用：生成并发送语音

```python
from skills.ResVoice import send_voice_message

# 仅生成语音（零配置）
result = await send_voice_message("你好梦哥")
print(f"语音文件: {result['filepath']}")

# 生成并发送到企业微信
result = await send_voice_message(
    "你好梦哥",
    to_user="UserID",
    send_to_wechat=True,
    corp_id="ww...",
    agent_id=1000002,
    secret="..."
)
```

### 发送微信语音

```python
from skills.ResVoice import WeChatWorkVoiceSender

async def send_voice():
    sender = WeChatWorkVoiceSender(
        corp_id="wwxxxxxxxxxxxxxxxx",
        agent_id=1000002,
        secret="your_secret_here"
    )
    
    # 文字 → 语音 → 微信
    result = await sender.text_to_voice_and_send(
        text="这是 AI 的语音回复",
        user_id="UserID"
    )
    print("发送成功！")
```

## 配置说明

### 环境变量

```bash
# 企业微信配置（可选，也可代码中传入）
WECHAT_CORP_ID=wwxxxxxxxxxxxxxxxx
WECHAT_AGENT_ID=1000002
WECHAT_SECRET=your_secret_here
```

### 初始化参数

```python
from skills.ResVoice import TTSService, TTSEngine

# 完整配置
tts = TTSService(
    output_dir="/path/to/output",      # 输出目录
    default_engine=TTSEngine.EDGE,      # 默认引擎
    auto_fallback=True                   # 网络失败自动回退
)
```

## API 参考

### TTSService

#### `text_to_speech(text, voice=None, engine=None, ...)`

文字转语音

| 参数 | 类型 | 说明 |
|------|------|------|
| text | str | 要转换的文字（必填） |
| voice | str | 语音类型，仅 Edge 有效 |
| engine | TTSEngine | 指定引擎 |
| rate | str | 语速，如 "+10%" |
| volume | str | 音量，如 "+10%" |
| pitch | str | 音调，如 "+10Hz" |

**返回值:**
```python
{
    "success": True,
    "filepath": "/path/to/audio.mp3",
    "engine": "edge",
    "voice": "zh-CN-XiaoxiaoNeural",
    "file_size_human": "12.5 KB"
}
```

### 引擎类型

| 引擎 | 说明 | 网络需求 | 质量 |
|------|------|----------|------|
| `TTSEngine.EDGE` | Edge TTS（默认） | 需要 | ⭐⭐⭐ |
| `TTSEngine.GTTS` | Google TTS | 需要 | ⭐⭐ |
| `TTSEngine.PYTTSX3` | 本地合成 | 不需要 | ⭐ |

### 便捷函数

- `send_voice_message(text, ...)` - OpenClaw 专用，生成并发送
- `send_voice_message_sync(text, ...)` - 同步版本
- `text_to_speech_sync(text, ...)` - 同步调用
- `text_to_speech_simple(text)` - 最简单调用，返回路径

## 注意事项

1. **网络问题**: Edge TTS 在国内可能不稳定，已配置自动回退到 gTTS 或 pyttsx3
2. **ffmpeg**: 必须安装，用于音频格式转换
3. **企业微信**: 需要企业微信管理员权限获取 corp_id/agent_id/secret
4. **离线使用**: 设置 `engine=TTSEngine.PYTTSX3` 可完全离线使用

## 故障排除

### "No audio was received" 错误
- Edge TTS 网络不稳定
- 已自动回退到其他引擎，无需处理

### "ffmpeg not found" 错误
- 未安装 ffmpeg
- 参考安装章节安装

### 企业微信发送失败
- 检查 corp_id/agent_id/secret 是否正确
- 确认应用有发送消息权限
- 确认接收用户在企业微信中

## 更新日志

### 0.1.5-beta
- 新增: OPENCLAW_CAPABILITIES 能力声明
- 新增: send_voice_message() OpenClaw 专用便捷函数
- 优化: 声明自带 TTS 能力，零配置开箱即用
- 重构: 目录结构优化，代码更清晰

### 0.1.0-beta
- 初始版本
- 多引擎 TTS 支持
- 企业微信语音发送
- 自动引擎回退

## 许可证

MIT License
