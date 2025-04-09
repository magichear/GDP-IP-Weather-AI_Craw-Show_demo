import asyncio
from Server import Server
from WebUI import WebUI


class Main:
    def __init__(self):
        self.server = Server()
        self.web_ui = WebUI(self.server)

    async def run(self):
        """
        前后端异步启动
        """
        asyncio.create_task(self.server.start_async())
        await asyncio.to_thread(self.web_ui.launch)


if __name__ == "__main__":
    main = Main()
    asyncio.run(main.run())
