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

    @classmethod
    def get(cls, key):
        return getattr(cls, key, None)

    @staticmethod
    def geGroupXpath(td_index, count):
        if count == 1:
            return f"/html/body/div[3]/div[5]/div/div[2]/table[1]/tbody/tr"
        return f"/html/body/div[3]/div[5]/div/div[2]/table[1]/tbody/tr[{td_index}]"
