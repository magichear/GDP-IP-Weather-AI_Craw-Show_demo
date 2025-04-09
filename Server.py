import os
import logging
import asyncio
import threading
from Config import Config
from Crawler import Crawler
from QueryCore import QueryCore
from concurrent.futures import ThreadPoolExecutor, as_completed


class Server:
    def __init__(self):
        """
        初始化 Server 类，完成数据库准备和数据缓存。
        """
        self.crawler = Crawler(Config.get("PREPARE_URLS"))
        self.query_core = QueryCore()
        self.cache_path = Config.get("CACHE_PATH")
        self.start_year = Config.get("START_YEAR")
        self.end_year = Config.get("END_YEAR")
        self.data_cache = {}
        self.is_ready = False  # 初始化标志
        self.lock = threading.Lock()  # 虽然所有国家的名字不同，但还是加个锁

        # 初始化日志配置
        log_file = Config.get("LOG_FILE")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, mode="a", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("Server")

    def start(self, useNew=False):
        """
        启动服务器，完成初始化和数据缓存。
        """
        self.logger.info("[Server] Starting server...")
        self.logger.info("[Server] Preparing database...")
        if useNew:
            self.crawler.prepareDB()
        self.logger.info("[Server] Loading country map...")
        country_map = self.query_core.data
        if not country_map:
            self.logger.error("[Error] Failed to load country map. Exiting...")
            return

        self.logger.info(
            "[Server] Querying data for all countries and regions using threads..."
        )
        if useNew:
            self.queryAll(country_map)

        self.logger.info("[Server] Saving cached data...")
        if useNew:
            self.saveCache()
        else:
            self.loadCache()
        self.logger.info("[Server] Server started successfully.")

    def queryAll(self, country_map):
        """
        使用线程池查询所有国家和地区的 GDP 数据。
        :param country_map: 国家和地区映射表
        """
        country_names = list(country_map.keys())

        # 分批查询，避免 URL 过长被ban掉
        batch_size = Config.get("BATCH_SIZE")
        batches = [
            country_names[i : i + batch_size]
            for i in range(0, len(country_names), batch_size)
        ]

        # 线程池， 有with语句自动关闭
        with ThreadPoolExecutor(max_workers=Config.get("MAX_WORKERS")) as executor:
            future_to_batch = {
                executor.submit(self.__query, batch): batch for batch in batches
            }

            for future in as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    future.result()  # 等待线程完成
                except Exception as e:
                    self.logger.error(f"[Error] Failed to query batch {batch}: {e}")

    def __query(self, batch):
        """
        查询一批国家的 GDP 数据，并直接更新 self.data_cache。
        :param batch: 国家名称列表
        """
        self.logger.info(f"[Server] Querying batch: {batch}")
        data = self.query_core.query(self.start_year, self.end_year, batch)

        # 使用锁保护对 self.data_cache 的修改
        with self.lock:
            for country in batch:
                if country in data:
                    self.data_cache[country] = data[country]

    def saveCache(self):
        """
        缓存数据
        """
        self.query_core.json_handler.jsonIO(
            mode=self.query_core.json_handler.STJSON,
            output_file=self.cache_path,
            outdata=self.data_cache,
            sort_mode=self.query_core.json_handler.SORTBYKEY,
        )
        self.logger.info(f"[Server] Cache saved to {self.cache_path}.")

    def loadCache(self):
        """
        加载缓存数据
        """
        if os.path.exists(self.cache_path):
            self.logger.info("[Server] Loading cached data...")
            self.data_cache = self.query_core.json_handler.jsonIO(
                mode=self.query_core.json_handler.LDJSON, inputfile=self.cache_path
            )
        else:
            self.logger.warning("[Server] No cache file found. Starting fresh.")

    def getGDPTrend(self, country_names, start, end):
        """
        :param country_names: 国家名称列表
        :param start: 起始年份
        :param end: 结束年份
        :return: GDP 趋势图
        """
        # 从配置中获取起止年份
        config_start_year = Config.get("START_YEAR")
        config_end_year = Config.get("END_YEAR")

        # 确保 start 和 end 在配置范围内
        start = max(start, config_start_year)
        end = min(end, config_end_year)

        if start > end:
            self.logger.error(f"[Error] Invalid year range: start={start}, end={end}")
            return None

        data = {}
        for country_name in country_names:
            if country_name in self.data_cache:
                # 对数据进行切片
                country_data = self.data_cache[country_name]
                if isinstance(country_data, list):
                    # 如果是列表，根据年份范围切片
                    start_index = start - config_start_year
                    end_index = end - config_start_year + 1
                    sliced_data = country_data[start_index:end_index]
                    data[country_name] = sliced_data
                else:
                    self.logger.error(
                        f"[Error] Unexpected data format for country '{country_name}'."
                    )
                    continue
            else:
                self.logger.error(
                    f"[Error] Country '{country_name}' not found in cache."
                )
                continue

        return self.query_core.plot(start=start, end=end, data=data)

    def __input(self):
        """
        获取用户输入的国家名称。
        :return: 用户输入的国家名称列表
        """
        user_input = input(
            "请输入要查询的国家名称（多个国家用分号分隔），使用 'quit' 退出："
        ).strip()
        if user_input.lower() == "quit":
            return None
        return [name.strip() for name in user_input.split(";")]

    def getNames(self):
        return list(self.query_core.data.keys())

    def run(self):
        """
        启动服务器并进入查询循环。
        """
        self.start()  # 启动服务器

        while True:
            country_names = self.__input()
            if country_names is None:  # 用户输入 'quit' 时退出
                self.logger.info("[Server] Exiting...")
                break

            # 获取并展示 GDP 趋势图
            fig = self.getGDPTrend(country_names, self.start_year, self.end_year)
            if fig:
                fig.show()  # 显示图像
            else:
                self.logger.error("[Error] Failed to generate GDP trend plot.")

    async def start_async(self):
        """
        异步启动服务器
        """
        await asyncio.to_thread(self.start)  # 异步运行原有的 start 方法
        self.is_ready = True  # 初始化完成后设置标志位

    def stop(self):
        """
        停止后端服务。
        """
        self.logger.info("[Server] Stopping server...")


if __name__ == "__main__":
    server = Server()
    server.run()
