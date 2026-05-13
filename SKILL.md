# ResVoice.skills (应声)

## 一句话描述

**当用户需要语音回复时，调用本 Skill 生成语音并自动发送到微信。**

---

## 什么时候调用？

用户说这些时立即调用：
- "发语音给我"
- "用语音回复"
- "语音说一遍"

---

## 核心接口（OpenClaw 自动适配）

```python
from skills.ResVoice import send_voice_message

# 最简单的方式：自动检测 OpenClaw 环境
result = await send_voice_message("你好，世界！")

# OpenClaw 会自动：
# 1. 检测当前是微信个人号还是企业微信
# 2. 生成语音文件
# 3. 自动发送到当前聊天窗口
```

### 返回值

```python
{
    "success": True,
    "filepath": "/path/to/audio.mp3",
    "platform": "openclaw_weixin",  # 自动检测的平台
    "is_real_voice": False,          # 个人微信为 MP3 文件
    "sent": True                     # 是否成功发送
}
```

---

## OpenClaw 环境自动检测

本 Skill 会自动读取 OpenClaw 注入的元数据：

```json
{
  "channel": "openclaw-weixin",      // 微信个人号
  "chat_id": "xxx@im.wechat",        // 用户ID
  "account_id": "xxx-im-bot"         // 机器人账号
}
```

**自动适配逻辑：**

| 渠道 | 检测标识 | 发送方式 |
|------|----------|----------|
| 微信个人号 | `channel: "openclaw-weixin"` | MP3 文件 |
| 企业微信 | `channel: "wechat-work"` | AMR 语音 |

**Agent 无需手动配置，一行代码搞定：**

```python
# 自动检测平台，自动发送
result = await send_voice_message("你好")
```

---

## ⚠️ 重要：不要传 channel 参数

```python
# ❌ 错误：加了 channel 会失败
message(action="send", media="/path/to/file.mp3", channel="openclaw-weixin")
# 结果: "Unknown channel" 或 "Channel is required"

# ✅ 正确：不加 channel，让 OpenClaw 自动使用当前会话的 channel
message(action="send", media="/path/to/file.mp3")
# 结果: 成功发送！
```

**原因**：OpenClaw 会自动从当前会话上下文获取 channel，显式传入反而会覆盖导致失败。

---

## 手动指定平台（可选）

如果需要手动控制：

```python
# 发送到企业微信
result = await send_voice_message(
    text="你好",
    platform="wechat_work",
    corp_id="...",
    agent_id=...,
    secret="..."
)

# 发送到个人微信（手动指定）
result = await send_voice_message(
    text="你好",
    platform="personal_wechat",
    send_func=your_func
)
```

---

## 环境检查

```python
from skills.ResVoice import check_setup, auto_setup

# 检查环境
status = check_setup()
if not status["ready"]:
    auto_setup()  # 自动修复
```

---

## 能力声明

```yaml
skill: ResVoice
version: 0.3.0-beta

capabilities:
  tts:
    provider: edge_tts
    engines: [edge, gtts, pyttsx3]
    voices: [zh-CN-XiaoxiaoNeural, zh-CN-YunxiNeural, ...]
    offline_fallback: true
    
  voice_send:
    platforms:
      - openclaw_weixin    # 个人微信（自动检测）
      - wechat_work        # 企业微信
    formats: [mp3, amr]
    
  openclaw_integration:
    auto_detect: true                    # 自动检测环境
    meta_source: OPENCLAW_META           # 读取元数据
    send_method: message(action="send")  # 使用 OpenClaw 工具
```

---

## 依赖

- Python 3.9+
- ffmpeg（系统依赖）

自动安装：`auto_setup()`

---

## 更新日志

### 0.3.0-beta
- **新增**: OpenClaw 自动适配，无需手动配置
- **新增**: 自动检测微信个人号/企业微信
- **优化**: `send_voice_message()` 支持 platform=None 自动检测

### 0.2.0-beta
- 重构：专注 Agent 调用
- 新增：环境检测与自动修复

### 0.1.0-beta
- 初始版本
