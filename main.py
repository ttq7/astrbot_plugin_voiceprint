from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Star, register
from astrbot.api import logger
import json
from pydub import AudioSegment
import os
from pypinyin import pinyin, Style

@register(
    "astrbot_plugin_voiceprint",
    "hello七七",
    "活字印刷语音插件",
    "1.0.0",
    "https://github.com/ttq7/astrbot_plugin_voiceprint"
)
class PrintingPressPlugin(Star):
    def __init__(self, context):
        super().__init__(context)
        self.plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.source_folder = os.path.join(self.plugin_dir, "sources")
        os.makedirs(self.source_folder, exist_ok=True)
        self.output_path = os.path.join(self.plugin_dir, "combined.wav")  

    @filter.command("活字印刷")
    async def cmd_printing_press(self, event: AstrMessageEvent):
        cmd_name = "活字印刷"
        input_text = event.message_str.strip()
        if input_text.startswith(cmd_name):
            params = input_text[len(cmd_name):].strip()
            if not params:
                yield event.plain_result("请输入需要转换为语音的内容~")
                return
            input_text = params
        else:
            yield event.plain_result("指令格式应为：/活字印刷 [需要转换的文本]")
            return

        combined_wav = await self.concatenate_wav(input_text)
        if combined_wav:
            from astrbot.api.message_components import Record
            yield event.chain_result([Record(file=combined_wav)])  
            self.delete_temp_file()
        else:
            yield event.plain_result("生成语音失败，请检查音频文件是否齐全")

    async def concatenate_wav(self, input_text):
        combined = AudioSegment.empty()
        pinyin_list = pinyin(input_text, style=Style.NORMAL)
        for py in pinyin_list:
            pinyin_str = py[0]
            wav_path = os.path.join(self.source_folder, f"{pinyin_str}.wav")
            if os.path.exists(wav_path):
                try:
                    audio = AudioSegment.from_wav(wav_path)
                    combined += audio
                except Exception as e:
                    logger.error(f"加载 {wav_path} 失败: {str(e)}")
            else:
                logger.warning(f"未找到音频文件: {wav_path}")

        if len(combined) > 0:
            self.output_path = os.path.join(self.plugin_dir, "combined.wav")
            combined.export(self.output_path, format="wav")
            return self.output_path
        return None

    def delete_temp_file(self):
        try:
            if os.path.exists(self.output_path):
                os.remove(self.output_path)
                logger.info(f"成功删除临时文件: {self.output_path}")
            else:
                logger.warning(f"临时文件不存在，无需删除: {self.output_path}")
        except Exception as e:
            logger.error(f"删除临时文件失败: {str(e)}")