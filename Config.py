class Config:
    PREPARE_URLS = [
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=995&sg=All-countries/Advanced-economies/Euro-area",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=119&sg=All-countries/Advanced-economies/Major-advanced-economies-(G7)",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2505&sg=All-countries/Emerging-market-and-developing-economies/Emerging-and-developing-Asia",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2903&sg=All-countries/Emerging-market-and-developing-economies/Emerging-and-developing-Europe",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=205&sg=All-countries/Emerging-market-and-developing-economies/Latin-America-and-the-Caribbean",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2400&sg=All-countries/Emerging-market-and-developing-economies/Middle-East-and-Central-Asia",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2603&sg=All-countries/Emerging-market-and-developing-economies/Sub-Saharan-Africa",
        "AA_https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-aggr-data",
    ]
    BASEURL = (
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?"
    )
    SUFFIX = "ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1"

    MAP_PATH = "countryMap.json"

    INPUT_XPATH = "//input[@id]"
    LABEL_XPATH = "//label"

    CODE_PREFIX = "**"  # 自定义的前缀标识符，用于地区的查询与国家不一样
    TABLE_START_INDEX = 7  # 表格数据起始列索引

    MAX_RETRIES = 5
    TIMEOUT = 30

    WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
    IPADDRESS_API_URL = "http://ip-api.com/json/"

    #################################SERVER#####################################
    LOG_FILE = "server.log"  # 日志文件路径
    BATCH_SIZE = 20  # 批量查询的大小
    START_YEAR = 1980  # 查询的起始年份
    END_YEAR = 2029  # 查询的结束年份
    CACHE_PATH = "data_cache.json"  # 缓存数据的文件路径
    MAX_WORKERS = 5  # 线程池的最大工作线程数

    #################################WebUI#####################################
    INPUT_XPATH_KIMI_FIRST = (
        '//*[@id="app"]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[1]/p'
    )
    # //*[@id="app"]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[1]/p
    INPUT_XPATH_KIMI = (
        '//*[@id="app"]/div/div/div[2]/div/div/div[1]/div[3]/div[2]/div[1]/div/div[1]/p'
    )
    # //*[@id="app"]/div/div/div[2]/div/div/div[1]/div[3]/div[2]/div[1]/div/div[1]/p
    SUBMIT_BUTTON_XPATH_KIMI_FIRST = (
        '//*[@id="app"]/div/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div'
    )
    SUBMIT_BUTTON_XPATH_KIMI = '//*[@id="app"]/div/div/div[2]/div/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div'
    KIMI_URL = "https://kimi.moonshot.cn/chat/"
    START_PROMPT = "接下来请简要分析给定国家在指定年份内的GDP变化及可能影响因素(countries:China;Year:1980-2022.)。回复完毕后请严格回复“回复完毕”"

    @classmethod
    def get(cls, key):
        return getattr(cls, key, None)

    @staticmethod
    def geGroupXpath(td_index, count):
        if count == 1:
            return f"/html/body/div[3]/div[5]/div/div[2]/table[1]/tbody/tr"
        return f"/html/body/div[3]/div[5]/div/div[2]/table[1]/tbody/tr[{td_index}]"

    @staticmethod
    def getResponseXpath(msg_cnt):
        return f'//*[@id="app"]/div/div/div[2]/div/div/div[1]/div[2]/div/div[{2 * msg_cnt}]/div/div[2]/div[1]/div[1]/div[2]/div'
