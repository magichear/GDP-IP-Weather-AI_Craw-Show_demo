"""
对于下面的每个链接：

https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=995&sg=All-countries/Advanced-economies/Euro-area
https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=119&sg=All-countries/Advanced-economies/Major-advanced-economies-(G7)
https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2505&sg=All-countries/Emerging-market-and-developing-economies/Emerging-and-developing-Asia
https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2903&sg=All-countries/Emerging-market-and-developing-economies/Emerging-and-developing-Europe
https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=205&sg=All-countries/Emerging-market-and-developing-economies/Latin-America-and-the-Caribbean
https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2400&sg=All-countries/Emerging-market-and-developing-economies/Middle-East-and-Central-Asia
https://www.imf.org/en/Publications/WEO/weo-database/2024/October/select-countries?grp=2603&sg=All-countries/Emerging-market-and-developing-economies/Sub-Saharan-Africa

定位到每个页面下的这些XPATH(变化之处在tr的数字上，每页可能有多个)
/html/body/div[3]/div[7]/table/tbody/tr[1]/td[1]/div
/html/body/div[3]/div[7]/table/tbody/tr[2]/td[1]/div

//*[@id="chk_513"]
/html/body/div[3]/div[7]/table/tbody/tr[1]/td[1]/div/label


//*[@id="chk_514"]
/html/body/div[3]/div[7]/table/tbody/tr[2]/td[1]/div/label
"""

import requests
from lxml import html
import json

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


FILE_PATH = "countryMap.json"

# XPATH 模板
xpath_input = "//input[@id]"
xpath_label = "//label"

final_data = {}

for url in urls:
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

        # 前三个input无效
        inputs = inputs[3:]
        labels = labels[: len(inputs)]

        for input_elem, label_elem in zip(inputs, labels):
            input_id = input_elem.get("id").replace("chk_", "")  # 去掉 chk_ 前缀
            if is_aggregated:
                input_id = (
                    f"**{input_id}"  # 地区的查询与国家不一样，这里加上前缀 **来标注
                )
            label_text = label_elem.text_content().strip()
            final_data[label_text] = input_id

    except Exception as e:
        print(f"Error processing {url}: {e}")

# 按 Label 的自然顺序排序
final_data = dict(sorted(final_data.items()))


with open(FILE_PATH, "w", encoding="utf-8") as json_file:
    json.dump(final_data, json_file, ensure_ascii=False, indent=4)
