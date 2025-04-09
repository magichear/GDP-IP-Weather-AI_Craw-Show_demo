import asyncio
from Server import Server
from WebUI import WebUI


class Main:
    def __init__(self):
        self.server = Server()
        self.web_ui = WebUI(self.server)
        self.is_running = True  # 用于标记是否继续运行

    async def run(self):
        """
        前后端异步启动
        """
        try:
            server_task = asyncio.create_task(self.server.start_async())
            web_ui_task = asyncio.to_thread(self.web_ui.launch)

            # 等待任务完成
            await asyncio.gather(server_task, web_ui_task)
        except Exception as e:
            self.server.logger.exception(f"运行过程中发生错误：{e}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """
        强制关闭所有服务
        """
        if self.is_running:
            self.is_running = False
            self.server.logger.info("检测到中断信号，正在关闭服务...")
            self.server.stop()  # 停止后端服务
            self.server.logger.info("服务已关闭。")

            # 取消所有未完成的任务
            pending = asyncio.all_tasks()
            for task in pending:
                if task is not asyncio.current_task():
                    task.cancel()
            self.server.logger.info("所有异步任务已取消。")

            # 等待所有任务完成
            await asyncio.gather(*pending, return_exceptions=True)


"""
程序中断后终端一直处于阻塞状态，多进程与多线程也无法处理（强制终止可能导致资源泄露）

于是决定写一个bat文件来自动启动，中断并关闭终端后windows自动终止程序
"""
if __name__ == "__main__":
    main = Main()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main.run())
    except KeyboardInterrupt:
        loop.run_until_complete(main.shutdown())
    finally:
        # 确保事件循环已关闭
        loop.close()
