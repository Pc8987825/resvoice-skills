# ResVoice.skills (回应之声)

> 让 AI 开口说话，让思念有处回应

一个为 OpenClaw 打造的文字转语音 Skill，让 AI 不再只输出文字，而是可以 "开口说话"。

## 🎯 核心优势：零配置开箱即用

**与其他 TTS Skill 不同，ResVoice 自带完整 TTS 引擎，无需配置 OpenAI/ElevenLabs API！**

```python
from skills.ResVoice import send_voice_message

# 零配置，直接生成语音
result = await send_voice_message("你好梦哥")
print(f"语音文件: {result['filepath']}")
```

| 特性 | ResVoice.skills | 其他 TTS Skill |
|------|-------------|----------------|
| **API 配置** | ❌ 不需要 | ✅ 需要 OpenAI/ElevenLabs |
| **网络依赖** | Edge TTS（微软服务） | 依赖外部 API |
| **离线可用** | ✅ pyttsx3 回退 | ❌ 不可用 |
| **成本** | 免费 | 按量付费 |

## ⚠️ 前置要求：ffmpeg + AMR 编码器

**必须安装 ffmpeg 且支持 AMR 编码器，否则无法发送语音消息！**

### 快速检查（先运行这个！）

```bash
ffmpeg -encoders | grep amr
```

- ✅ **如果看到 `libopencore_amrnb`** → 可以继续安装
- ❌ **如果无输出** → [点击看安装指南](#1-安装-ffmpeg必需)

## ⚠️ 重要限制说明

**个人微信 vs 企业微信**：
- ❌ **个人微信**：无法直接发送语音消息，只能发送 MP3 文件（微信会显示为文件而非语音）
- ✅ **企业微信**：可以发送真正的语音消息（AMR 格式），在聊天中显示为可播放的语音

**网络依赖**：
- Edge TTS 需要微软服务网络可用，国内可能不稳定
- 已配置自动回退：Edge → gTTS → pyttsx3（本地离线）

## 创作初衷

**实用层面**：完善本地部署 AI 的语音能力，实现 AI 回复 → 语音合成 → 微信语音发送的完整链路。不方便看屏幕时，也能用耳朵接收 AI 消息。

**情感层面**：通过历史对话、语音数据，让 AI 学习并复刻熟悉的人声，做一个 "应声虫" 般的存在。清醒知道这只是机器学习，但可以再次听到思念之人的声音，获得情感上的慰藉与陪伴。

## 功能

- 🎙️ **多引擎 TTS** - Edge TTS(默认)、gTTS、pyttsx3，自动回退
- 🔄 **音频转换** - 自动处理 MP3 → AMR 微信语音格式
- 💬 **微信发送** - 企业微信语音消息发送（个人微信仅支持 MP3 文件）
- 🎭 **多音色支持** - 男声、女声、中英文等多种语音选项
- 📴 **离线可用** - pyttsx3 引擎无需网络

## 安装

```bash
pip install -r requirements.txt
```

**系统依赖**：需要安装 [ffmpeg](https://ffmpeg.org/download.html)

### 各平台 ffmpeg 安装指南

#### 🪟 Windows

**方式 1：使用 winget（推荐）**
```powershell
winget install Gyan.FFmpeg
```

**方式 2：手动安装**
1. 下载：https://ffmpeg.org/download.html#build-windows
2. 解压到 `C:\ffmpeg`
3. 添加环境变量：将 `C:\ffmpeg\bin` 添加到 PATH
4. 重启终端，验证：`ffmpeg -version`

#### 🍎 macOS

**方式 1：使用 Homebrew（推荐）**
```bash
brew install ffmpeg
```

**方式 2：手动安装**
1. 下载：https://ffmpeg.org/download.html#build-mac
2. 解压并移动到 `/usr/local/bin`
3. 验证：`ffmpeg -version`

#### 🐧 Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install ffmpeg
ffmpeg -version
```

#### 🐧 Linux (CentOS/RHEL)

```bash
sudo yum install ffmpeg
# 或
sudo dnf install ffmpeg
```

#### 🐧 Linux (Alpine - Docker 常用)

```bash
apk add ffmpeg
```

### 服务器部署建议

由于本 Skill 依赖 ffmpeg，建议在服务器上使用 Docker 部署，确保环境一致性：

```dockerfile
FROM python:3.11-slim

# 安装 ffmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制 Skill 代码
COPY . /app/skills/ResVoice

WORKDIR /app
```

或者在 docker-compose 中：

```yaml
services:
  openclaw:
    image: your-openclaw-image
    volumes:
      - ./skills/ResVoice:/app/skills/ResVoice
    # ffmpeg 需要在镜像中预装
```

**注意**：Skill 会尝试自动检测和安装 ffmpeg（仅限 Linux），但预装更可靠。

## 快速使用

### 1. 文字转语音

```python
from skills.ResVoice import TTSService
import asyncio

async def main():
    tts = TTSService()
    result = await tts.text_to_speech(
        text="你好，世界！",
        voice="zh-CN-XiaoxiaoNeural"  # 中文女声
    )
    print(f"生成成功: {result['filepath']}")

asyncio.run(main())
```

### 2. 发送企业微信语音

```python
from skills.ResVoice import WeChatWorkVoiceSender
import asyncio

async def main():
    sender = WeChatWorkVoiceSender(
        corp_id="wwexxxxxxxxxxxxxxxx",
        agent_id=1000002,
        secret="your_secret_here"
    )
    
    result = await sender.text_to_voice_and_send(
        text="你好，这是语音消息！",
        user_id="UserID"
    )
    print("发送成功！")

asyncio.run(main())
```

### 3. 仅发送文本消息

```python
from skills.ResVoice import WeChatWorkAPI, WeChatWorkConfig

config = WeChatWorkConfig(
    corp_id="your_corp_id",
    agent_id=1000002,
    secret="your_secret"
)

api = WeChatWorkAPI(config)
api.send_text_message("UserID", "Hello from OpenClaw!")
```

## API 参考

### TTSService

```python
async def text_to_speech(
    text: str,           # 要转换的文字
    voice: str = None,   # 语音类型，默认中文女声
    rate: str = "+0%",   # 语速
    volume: str = "+0%", # 音量
    pitch: str = "+0Hz"  # 音调
) -> dict
```

**支持的语音**：
- `zh-CN-XiaoxiaoNeural` - 中文女声（晓晓）
- `zh-CN-YunxiNeural` - 中文男声（云希）
- `en-US-AriaNeural` - 英文女声
- 更多见 `tts.py` 中的 `EDGE_VOICES`

### WeChatWorkVoiceSender

```python
async def text_to_voice_and_send(
    text: str,           # 要转换的文字
    user_id: str,        # 企业微信用户 ID
    voice: str = None    # 语音类型
) -> dict
```

### AudioConverter

```python
converter = AudioConverter()

# MP3 转 AMR
amr_path = converter.mp3_to_amr("input.mp3")

# 获取音频信息
info = converter.get_audio_info("audio.mp3")
```

## 企业微信配置指南

### 1. 获取配置参数

登录 [企业微信管理后台](https://work.weixin.qq.com) 获取以下参数：

| 参数 | 获取位置 | 说明 |
|------|----------|------|
| **CorpID** | 我的企业 → 企业ID | 以 `ww` 开头的字符串 |
| **AgentID** | 应用管理 → 应用 → AgentId | 数字，如 `1000002` |
| **Secret** | 应用管理 → 应用 → Secret | 点击「查看」获取 |
| **UserID** | 通讯录 → 成员详情 → 账号 | 如 `ZhangSan` |

### 2. 配置 IP 白名单（重要！）

**错误码 60020 = IP 未授权**

解决步骤：
1. 登录 https://work.weixin.qq.com
2. 进入「管理工具」→「通讯录同步」→「企业可信IP」
3. 添加服务器公网 IP（如 `xxx.xxx.xxx.xxx`）
4. 等待 5-10 分钟生效

### 3. 检查 ffmpeg AMR 支持

发送企业微信语音需要 ffmpeg 支持 AMR 编码：

```bash
# 检查 AMR 支持
ffmpeg -encoders | grep amr

# 如果有输出，说明支持
# 如果无输出，需要安装静态 ffmpeg 或 AMR 库
```

**安装方案：**

**方案 A - 使用静态 ffmpeg（推荐，5分钟）**
```bash
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf ffmpeg-release-amd64-static.tar.xz
sudo cp ffmpeg-*-static/ffmpeg /usr/local/bin/ffmpeg-amr
export FFMPEG_PATH=/usr/local/bin/ffmpeg-amr
```

**方案 B - 安装 AMR 库**
```bash
sudo apt-get install libopencore-amrnb-dev
# 注意：某些系统源不包含此包
```

### 4. 快速测试

```python
from skills.ResVoice import WeChatWorkVoiceSender
import asyncio

async def test():
    sender = WeChatWorkVoiceSender(
        corp_id='你的CorpID',
        agent_id=你的AgentID,
        secret='你的Secret'
    )
    await sender.text_to_voice_and_send(
        text='测试消息',
        user_id='你的UserID'
    )

asyncio.run(test())
```

## 快速诊断

如果无法发送语音，按以下步骤排查：

### 步骤 1：检查 ffmpeg AMR 支持
```python
from skills.ResVoice import AudioConverter
c = AudioConverter()
print('AMR支持:', c.check_amr_support())
```

### 步骤 2：检查企业微信配置
```python
from skills.ResVoice import WeChatWorkVoiceSender
sender = WeChatWorkVoiceSender(
    corp_id='...', 
    agent_id=..., 
    secret='...'
)
# 配置有问题会立即提示
```

## 文件结构

```
ResVoice/
├── src/                # 核心代码
│   ├── __init__.py
│   ├── tts.py          # TTS 核心
│   ├── audio.py        # 音频转换
│   ├── wechat.py       # 企业微信 API
│   └── utils.py        # 通用工具
├── __init__.py         # Skill 入口
├── requirements.txt    # 依赖
├── SKILL.md            # OpenClaw 规范文档
└── README.md           # 本文档
```

## 依赖

- Python 3.9+
- edge-tts
- gTTS
- pyttsx3
- requests
- ffmpeg（系统依赖）

## License

MIT
