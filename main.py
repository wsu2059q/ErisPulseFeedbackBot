# ErisPulse 主程序文件 - 反馈系统
# 本文件由 SDK 自动创建，您可随意修改
import asyncio
from ErisPulse import sdk
from bot import FeedbackBot
from builder import FeedbackBuilder
from commands import FeedbackCommands


async def main():
    try:
        # 初始化反馈机器人
        bot = FeedbackBot(sdk)
        builder = FeedbackBuilder(bot)
        commands = FeedbackCommands(bot, builder)
        
        # 注册所有命令
        await commands.register_commands()
        
        # 运行 SDK
        await sdk.run(keep_running=True)
    except Exception as e:
        sdk.logger.error(e)
    except KeyboardInterrupt:
        sdk.logger.info("正在停止程序")
    finally:
        await sdk.uninit()


if __name__ == "__main__":
    asyncio.run(main())