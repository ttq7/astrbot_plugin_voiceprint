import asyncio
import aiohttp
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig


@register(
    "lolicon_plugin",
    author="Your Name",
    description="高性能随机色图插件（支持并发重试/连接池复用）",
    version="2.0.0",
    repo_url="https://your-repo-url.com"
)
class LoliconPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self._validate_config()  # 初始化时校验配置合法性
        self._session = None  # 全局连接池（复用TCP连接）

    def _validate_config(self):
        """校验配置参数合法性"""
        # r18参数校验（0/1/2）
        r18 = self.config.get("r18", 0)
        if r18 not in {0, 1, 2}:
            raise ValueError("r18必须为0（非R18）、1（R18）或2（混合）")

        # num参数校验（1-20）
        num = self.config.get("num", 1)
        if not 1 <= num <= 20:
            raise ValueError("num必须在1到20之间")

        # 重试次数校验（1-5）
        max_retries = self.config.get("max_retries", 3)
        if not 1 <= max_retries <= 5:
            raise ValueError("max_retries必须在1到5之间")

    async def _create_session(self):
        """创建带连接池的aiohttp会话（复用TCP连接）"""
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(
                limit_per_host=10,  # 每个主机的最大连接数
                ttl_dns_cache=300   # DNS缓存5分钟（减少DNS查询开销）
            ),
            timeout=aiohttp.ClientTimeout(total=10)  # 全局请求超时10秒
        )

    async def _single_request(self, session: aiohttp.ClientSession, params: dict):
        """单个API请求的异步协程（核心逻辑）"""
        try:
            async with session.get(
                "https://api.lolicon.app/setu/v2",
                params=params,
                headers={"User-Agent": "AstrBot-Lolicon-Plugin/2.0.0"}
            ) as response:
                # 校验HTTP状态码
                if response.status != 200:
                    raise Exception(f"HTTP状态码错误：{response.status}")
                
                # 异步解析JSON（自动处理gzip压缩）
                result = await response.json()
                
                # 校验API业务错误
                if result["error"]:
                    raise Exception(f"API错误：{result['error']}")
                
                return result["data"]  # 返回图片数据列表

        except Exception as e:
            logger.debug(f"单次请求失败：{str(e)}")
            return None

    @filter.command("lolicon")
    async def cmd_get_setu(self, event: AstrMessageEvent):
        """处理 /lolicon 指令的高性能异步方法"""
        # 从配置获取参数（带默认值）
        r18 = self.config.get("r18", 0)
        num = self.config.get("num", 1)
        tag = self.config.get("tag", [])
        max_retries = self.config.get("max_retries", 3)
        retry_delay = self.config.get("retry_delay", 2)  # 初始重试间隔（秒）

        # 构造请求参数（过滤空值）
        params = {
            "r18": r18,
            "num": num,
            "tag": tag if tag else None
        }
        params = {k: v for k, v in params.items() if v is not None}

        # 创建连接池（复用TCP连接）
        async with await self._create_session() as session:
            # 并发发起所有重试请求（最多max_retries个）
            tasks = [
                asyncio.create_task(
                    self._single_request(session, params)
                ) for _ in range(max_retries)
            ]

            # 优化点：等待第一个成功的请求（快速失败）
            done, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED
            )

            # 取消未完成的请求（释放资源）
            for task in pending:
                task.cancel()

            # 处理完成的任务（取第一个成功结果）
            for task in done:
                try:
                    images = task.result()
                    if images:
                        # 异步返回图片（按获取顺序发送）
                        for setu in images:
                            img_url = setu["urls"].get("original")
                            if img_url:
                                yield event.image_result(img_url)
                        return  # 成功后立即退出

                except Exception as e:
                    logger.warning(f"重试任务异常：{str(e)}")

        # 所有重试均失败
        yield event.plain_result(
            f"❌ 已尝试 {max_retries} 次，均未成功获取色图。"
            "请检查网络或稍后再试。"
        )

    async def terminate(self):
        """插件卸载时关闭连接池"""
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("Lolicon插件已安全退出")