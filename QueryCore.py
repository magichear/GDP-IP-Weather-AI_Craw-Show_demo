"""
https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?c=122,124,960,423,939,172,132,134,174,178,136,941,946,137,181,138,182,936,961,184,&s=NGDPD,&sy=1990&ey=2022&ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1

https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?c=156,132,134,136,158,112,111,&s=NGDPD,&sy=1990&ey=2022&ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1

https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?a=1&c=001,110,163,119,123,998,510,200,505,903,205,400,603,&s=NGDPD,&sy=1990&ey=2022&ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1

https://www.imf.org/en/Publications/WEO/weo-database/2024/October/weo-report?c=513,514,516,522,924,819,534,536,826,544,548,556,867,868,948,518,836,558,565,853,566,862,813,524,578,537,866,869,846,582,&s=NGDPD,&sy=1990&ey=2022&ssm=0&scsm=1&scc=1&ssd=1&ssc=0&sic=0&sort=country&ds=.&br=1
"""

import matplotlib.pyplot as plt
from jsonIO import jsonIO
from Config import Config
from Crawler import Crawler


class QueryCore:
    def __init__(self, dbPath=Config.get("MAP_PATH")):
        self.baseURL = Config.get("BASEURL")
        self.suffix = Config.get("SUFFIX")
        self.json_handler = jsonIO()
        self.crawler = Crawler()
        self.countryCode = ""
        self.dbPath = dbPath
        self.url = ""
        self.data = self.json_handler.jsonIO(
            mode=self.json_handler.LDJSON, inputfile=self.dbPath
        )

    def query(self, startYear, endYear, countryNames):
        """
        根据传入的 countryNames 列表查找对应的 countryCode，并生成查询 URL。
        :param startYear   : 开始年份
        :param endYear     : 结束年份
        :param countryNames: 国家名称列表
        """
        data = {}

        # 获取两类国家编码
        codes_with_prefix, codes_without_prefix = self.__getCode(countryNames)

        # 检查是否有带前缀的编码
        if codes_with_prefix:
            url = f"{self.baseURL}{codes_with_prefix}&s=NGDPD,&sy={startYear}&ey={endYear}&{self.suffix}"
            GDP_with_prefix = self.crawler.fetch_GDP_Data(
                url, endYear - startYear, len(codes_with_prefix.split(","))
            )
            for countryName, gdp in GDP_with_prefix.items():
                data[countryName] = gdp

        # 检查是否有不带前缀的编码
        if codes_without_prefix:
            url = f"{self.baseURL}{codes_without_prefix}&s=NGDPD,&sy={startYear}&ey={endYear}&{self.suffix}"
            GDP_without_prefix = self.crawler.fetch_GDP_Data(
                url, endYear - startYear, len(codes_without_prefix.split(","))
            )
            for countryName, gdp in GDP_without_prefix.items():
                data[countryName] = gdp

        # 绘制所有数据
        # print(f"Data: {data}")
        # self.plot(startYear, endYear, data)
        return data

    def __getCode(self, countryNames):
        """
        根据传入的国家名称列表返回两类国家代码字符串。
        :param countryNames: 国家名称列表
        :return: 两类国家代码字符串（带前缀和不带前缀），以逗号分隔
        """
        codes_with_prefix = []
        codes_without_prefix = []

        for countryName in countryNames:
            countryCode = self.data.get(countryName)
            if not countryCode:
                print(f"Error: Country '{countryName}' not found in the data.")
                continue

            # 检查是否具有地区前缀
            if countryCode.startswith(Config.get("CODE_PREFIX")):
                codes_with_prefix.append(countryCode[2:] + ",")
            else:
                codes_without_prefix.append(countryCode + ",")

        # 将两类编码以逗号分隔
        return (
            f"a=1&c={''.join(codes_with_prefix)}" if codes_with_prefix else "",
            f"c={''.join(codes_without_prefix)}" if codes_without_prefix else "",
        )

    def plot(self, start, end, data):
        """
        :param start: 开始年份
        :param end  : 结束年份
        :param data : 数据字典，键为国家名称，值为其对应年份内的GDP数据列表
        :return     : 返回绘制的 Figure 对象
        """
        try:

            def find_extrema(data):
                """
                找到数据中的极大值和最大值，并统一标注为 "max"。
                :param data: 输入数据列表
                :return: 包含极大值和最大值的索引及类型的列表
                """
                extrema_indices = []

                # 极大值
                for i in range(1, len(data) - 1):
                    if data[i] > data[i - 1] and data[i] > data[i + 1]:
                        extrema_indices.append((i, "max"))

                # 最大值，可能有多个
                max_value = max(data)
                max_indices = [i for i, value in enumerate(data) if value == max_value]
                for idx in max_indices:
                    if (idx, "max") not in extrema_indices:
                        extrema_indices.append((idx, "max"))

                return extrema_indices

            years = list(range(start, end + 1))
            fig, ax = plt.subplots(figsize=(12, 6))

            max_gdp = 0

            for country, gdp_data in data.items():
                if len(gdp_data) != len(years):
                    print(f"[Error] {country} 的数据长度与年份范围不匹配。")
                    print(gdp_data)
                    return None  # 返回 None 表示绘图失败
                max_gdp = max(max_gdp, max(gdp_data))
                ax.plot(years, gdp_data, marker="o", linestyle="-", label=country)

                # 在极大值处标注
                extrema = find_extrema(gdp_data)
                for index, extrema_type in extrema:
                    if extrema_type == "max":
                        ax.text(
                            years[index],
                            gdp_data[index],
                            f"{gdp_data[index]:.2f}",
                            color="red",
                            fontsize=10,
                            ha="center",
                        )

            ax.set_title(f"GDP Trend from {start} to {end}", fontsize=14)
            ax.set_xlabel("Year", fontsize=12)
            ax.set_ylabel("GDP (USD, in billions)", fontsize=12)
            ax.set_xticks(years)
            ax.tick_params(axis="x", rotation=45)
            ax.set_ylim(0, max_gdp * 1.1)
            ax.legend()
            plt.tight_layout()

            return fig

        except Exception as e:
            print(f"Error while plotting comparison chart: {e}")
            return None


def testPlot():
    # 假设 data 是一个包含国家 GDP 数据的字典
    data = {
        "USA": [5000, 5200, 5400, 5300, 5500, 5400, 5600],
        "China": [3000, 3200, 3100, 3300, 3200, 3400, 3300],
    }

    query_core = QueryCore()
    fig = query_core.plot(1980, 1986, data)

    if fig:
        # fig.savefig("gdp_trend.png")
        plt.show()
    else:
        print("绘图失败")


if __name__ == "__main__":
    country_list = ["Palau", "Finland", "Belgium"]
    start_year = 1990
    end_year = 2022
    query = QueryCore()
    query.query(start_year, end_year, country_list)
