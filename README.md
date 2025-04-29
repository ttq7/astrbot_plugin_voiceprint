
# AstrBot 活字印刷语音插件 (astrbot_plugin_voiceprint)

## 插件简介
**活字印刷语音插件** 是一款基于 **AstrBot** 的文本转语音插件，通过将输入文本转换为拼音，并拼接预存的拼音音频文件（`.wav`）生成语音消息。支持在 QQ、微信等消息平台发送语音，自动清理临时文件，实现轻量化的语音合成功能。


## 核心功能
1. **文本转语音**：将用户输入的中文文本转换为拼音，拼接对应音频文件生成语音。  
2. **自动清理**：发送语音后自动删除临时生成的拼接文件（`combined.wav`）。  
3. **多平台支持**：兼容 AstrBot 支持的消息平台（如 QQ、微信、Telegram 等）。  
4. **灵活扩展**：用户可自定义拼音音频库，扩展支持更多词汇。


## 安装步骤

### 1. 克隆插件仓库
```bash
git clone https://github.com/ttq7/astrbot_plugin_voiceprint.git
```


### 2. 安装依赖
在插件目录中创建 `requirements.txt` 并添加依赖：  
```txt
pydub==0.25.1       # 音频处理库
pypinyin==0.32.1    # 拼音转换库
```  
安装依赖：  
```bash
pip install -r data/plugins/astrbot_plugin_voiceprint/requirements.txt
```


## 使用说明

### 指令格式
```
/活字印刷 [需要转换为语音的文本]
```

### 示例
- 输入：`/活字印刷 你好，世界！`  
- 插件会将文本转换为拼音 `ni hao shi jie`，查找 `sources/` 中的 `ni.wav`、`hao.wav`、`shi.wav`、`jie.wav`，拼接生成语音并发送。

### 注意事项
- 输入文本支持中文、英文和空格，特殊符号会被忽略。  
- 音频文件需为 **WAV 格式**，编码建议为 PCM 格式（16 位，单声道，44100Hz）。  
- 若某拼音对应的音频文件缺失，插件会跳过该拼音并记录警告日志。


## 配置要求
| 依赖项         | 版本要求       | 说明                     |
|----------------|----------------|--------------------------|
| AstrBot        | ≥ 3.4.21       | 核心框架                 |
| Python         | ≥ 3.8          | 运行环境                 |
| pydub          | ≥ 0.25.1       | 音频处理（需 FFmpeg 支持）|
| pypinyin       | ≥ 0.32.1       | 拼音转换                 |

### 环境依赖（可选）
- **FFmpeg**：用于处理音频格式转换（若需支持非 WAV 格式的输入文件，需自行安装并配置环境变量）。


### 2. 错误处理
- 插件会记录音频文件缺失或加载失败的日志（位于 AstrBot 日志目录），可通过 `logger` 查看详细信息：  
  ```python
  from astrbot.api import logger
  logger.error("音频文件加载失败：xxx.wav")
  ```


## 更新日志
### v1.0.0（初始版本）
- 实现基础文本转语音功能，支持拼音拼接和语音发送。  
- 新增临时文件自动删除机制，避免磁盘空间占用。  
- 支持多平台消息发送（依赖 AstrBot 平台适配器）。


## 贡献与反馈
- **问题反馈**：在 [GitHub Issues](https://github.com/ttq7/astrbot_plugin_voiceprint/issues) 提交 bug 或建议。  
- **代码贡献**：提交 PR 前请确保代码符合 PEP8 规范，并添加必要注释。  
- **交流群**：欢迎加入 AstrBot 开发者群（群号：975206796）讨论插件开发。



