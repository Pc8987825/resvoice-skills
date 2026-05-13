# ResVoice.skills (应声)

## 一句话描述

**当用户需要语音回复时，调用本 Skill 生成语音。**

---

## 什么时候调用？

用户说这些时立即调用：
- "发语音给我"
- "用语音回复"
- "语音说一遍"

---

## 核心接口

```python
from skills.ResVoice import send_voice_message

# 生成语音
result = await send_voice_message("你好")

# 发送到企业微信
result = await send_voice_message(
    text="你好",
    to_user="UserID",
    platform="wechat_work",
    corp_id="...",
    agent_id=...,
    secret="..."
)

# 发送到个人微信（MP3文件）
result = await send_voice_message(
    text="你好",
    to_user="好友",
    platform="personal_wechat",
    send_func=your_func
)
```

---

## 返回值

```python
{
    "success": True,
    "filepath": "/path/to/audio.mp3",
    "platform": "wechat_work",      # wechat_work / personal_wechat
    "is_real_voice": True,          # True=AMR语音, False=MP3文件
    "format": "amr",                # amr / mp3
    "sent": True                    # 是否成功发送
}

# 错误时
{
    "success": False,
    "error_type": "MISSING_DEPENDENCY",  # 错误类型
    "message": "缺少依赖",
    "fix_command": "pip install ...",     # 修复命令
    "auto_fixable": True                  # 能否自动修复
}
```

---

## 环境检查（可选）

```python
from skills.ResVoice import check_setup, auto_setup

# 检查
status = check_setup()
if not status["ready"] and status["auto_fixable"]:
    auto_setup()  # 自动修复
```

---

## 能力声明

```yaml
skill: ResVoice
version: 0.2.0-beta

capabilities:
  tts:
    provider: edge_tts
    engines: [edge, gtts, pyttsx3]  # 自动回退
    voices:
      - zh-CN-XiaoxiaoNeural  # 女声（默认）
      - zh-CN-YunxiNeural     # 男声
    offline_fallback: true
    
  voice_send:
    platforms:
      - wechat_work     # 真正语音（AMR）
      - personal_wechat # MP3文件
```

---

## 依赖

- Python 3.9+
- ffmpeg（系统依赖）

自动安装：`auto_setup()`

---

## 更新日志

### 0.2.0-beta
- 重构：专注 Agent 调用，删除 CLI
- 保留：自动依赖安装、结构化错误、多引擎回退

### 0.1.0-beta
- 初始版本
