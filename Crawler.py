"""
对每个链接：

定位到每个页面下的这些XPATH(变化之处在tr的数字上，每页可能有多个)
/html/body/div[3]/div[7]/table/tbody/tr[1]/td[1]/div
/html/body/div[3]/div[7]/table/tbody/tr[2]/td[1]/div

例如：
//*[@id="chk_513"]
/html/body/div[3]/div[7]/table/tbody/tr[1]/td[1]/div/label


//*[@id="chk_514"]
/html/body/div[3]/div[7]/table/tbody/tr[2]/td[1]/div/label


可以增加初始化功能，允许在程序运行后首先初始化映射表

主要难点在一开始的数据获取途径分析上，本来没发现规律，还以为是动态生成的得上edgeDriver+selenium，
然后发现连参数都是静态的（没有动态key），这就好办了

至于展示媒介，初步计划使用WebUI+Cloudflare转发
"""

import requests
from lxml import html
from jsonIO import jsonIO
from Config import Config


class Crawler:
    def __init__(self, urls=None):
        self.urls = urls
        self.json_handler = jsonIO()
        self.final_data = {}

    def prepareDB(self):
        xpath_input = Config.get("INPUT_XPATH")
        xpath_label = Config.get("LABEL_XPATH")

        for url in self.urls:
            try:
                # 检查是否为地区
                is_aggregated = url.startswith("AA_")
                if is_aggregated:
                    url = url[3:]

                response = requests.get(url)
                response.raise_for_status()
                tree = html.fromstring(response.content)

                inputs = tree.xpath(xpath_input)
                labels = tree.xpath(xpath_label)

                # 前三个 input 无效
                inputs = inputs[3:]
                labels = labels[: len(inputs)]

                for input_elem, label_elem in zip(inputs, labels):
                    input_id = input_elem.get("id").replace(
                        "chk_", ""
                    )  # 去掉 chk_ 前缀
                    if is_aggregated:
                        input_id = f"{Config.get('CODE_PREFIX')}{input_id}"  # 地区的查询与国家不一样，这里加上前缀 ** 来标注
                    label_text = label_elem.text_content().strip()
                    self.final_data[label_text] = input_id

            except Exception as e:
                print(f"Error processing {url}: {e}")

        # 按 Label 的自然顺序排序
        self.final_data = dict(sorted(self.final_data.items()))

        # 保存为 JSON 文件
        self.json_handler.jsonIO(
            mode=self.json_handler.STJSON,
            output_file=Config.get("MAP_PATH"),
            outdata=self.final_data,
            sort_mode=self.json_handler.SORTBYKEY,
        )

    def fetch_GDP_Data(self, url, years, count=1):
        """
        获取指定页面下表格中指定范围列的数据

        :param url: 页面 URL
        :param years: 总年数，用于计算需要获取的列范围
        :param count: 数据组数，默认为 1；当 count > 1 时，处理多组数据
        :return: 包含表格中指定范围列数据的字典（键为国家名称，值为 GDP 数据列表）
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            tree = html.fromstring(response.content)

            # 初始化结果字典
            result = {}

            # 循环处理每组数据
            for group_index in range(1, count + 1):
                # 构造每组数据的 XPath
                group_xpath = Config.geGroupXpath(group_index, count)

                # 获取国家名称
                country_name_xpath = f"{group_xpath}/td[2]"
                country_name_data = tree.xpath(country_name_xpath)
                if not country_name_data:
                    print(f"[Warning] No country name found for group {group_index}.")
                    continue
                country_name = country_name_data[0].text_content().strip()

                # 获取 GDP 数据
                gdp_data = []
                td_start = Config.get("TABLE_START_INDEX")
                for td_index in range(td_start, years + td_start + 1):
                    xpath_td = f"{group_xpath}/td[{td_index}]"
                    td_data = tree.xpath(xpath_td)
                    if td_data:
                        value = td_data[0].text_content().strip()
                        # 将 "n/a" 替换为 0，并转换为 float
                        gdp_data.append(0.0 if value.lower() == "n/a" else float(value))
                    else:
                        gdp_data.append(0.0)  # 如果没有数据，填充为 0

                # 将结果存入字典
                result[country_name] = gdp_data

            return result

        except Exception as e:
            print(f"Error fetching table data from {url}: {e}")
            return {}


if __name__ == "__main__":
    urls = [
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=995&sg=All-countries/Advanced-economies/Euro-area",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=119&sg=All-countries/Advanced-economies/Major-advanced-economies-(G7)",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2505&sg=All-countries/Emerging-market-and-developing-economies/Emerging-and-developing-Asia",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2903&sg=All-countries/Emerging-market-and-developing-economies/Emerging-and-developing-Europe",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=205&sg=All-countries/Emerging-market-and-developing-economies/Latin-America-and-the-Caribbean",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2400&sg=All-countries/Emerging-market-and-developing-economies/Middle-East-and-Central-Asia",
        "https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2603&sg=All-countries/Emerging-market-and-developing-economies/Sub-Saharan-Africa",
        "AA_https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-aggr-data",
    ]

    crawler = Crawler(urls)
    crawler.prepareDB()
