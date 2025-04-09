class Config:
    BASEURL = (
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?"
    )
    SUFFIX = "ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1"

    MAP_PATH = "countryMap.json"

    INPUT_XPATH = "//input[@id]"
    LABEL_XPATH = "//label"

    CODE_PREFIX = "**"  # 自定义的前缀标识符，用于地区的查询与国家不一样
    TABLE_START_INDEX = 7  # 表格数据起始列索引

    @classmethod
    def get(cls, key):
        return getattr(cls, key, None)

    @staticmethod
    def geTableDataXpath(td_index):
        return f"/html/body/div[3]/div[5]/div/div[2]/table[1]/tbody/tr/td[{td_index}]"
