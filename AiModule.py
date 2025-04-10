from jsonIO import jsonIO
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from Config import Config


class AskTheFriendlyAI:
    def __init__(self, url, output_file="output.json"):
        """
        初始化浏览器自动化类
        :param url: 要打开的网页 URL
        :param output_file: 输出 JSON 文件路径
        """
        self.url = url
        self.driver = None
        self.msg_cnt = 1  # 发送计数器，初始值为 1
        self.output_file = output_file  # 输出 JSON 文件路径
        self.json_handler = jsonIO()  # JSON 读写工具类

    def start_browser(self):
        """
        启动浏览器
        """
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_argument("--no-sandbox")
        # edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--disable-extensions")
        edge_options.add_argument("--disable-infobars")
        edge_options.add_argument("--ignore-certificate-errors")
        edge_options.add_argument("--allow-insecure-localhost")
        edge_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.driver = webdriver.Edge(options=edge_options)
        self.driver.get(self.url)
        time.sleep(10)
        self.send_message("", True)
        time.sleep(10)
        self.receive_message()

    def close_browser(self):
        """
        关闭浏览器
        """
        if self.driver:
            self.driver.quit()

    def send_message(self, input_text, first_send=False):
        """
        发送消息
        :param input_text: 要发送的消息内容
        :param first_send: 是否是第一次发送
        """
        try:
            # 根据是否是第一次发送，选择不同的 XPath
            if first_send:
                input_box_xpath = Config.get("INPUT_XPATH_KIMI_FIRST")
                submit_button_xpath = Config.get("SUBMIT_BUTTON_XPATH_KIMI_FIRST")
                input_text = Config.get("START_PROMPT") + input_text
            else:
                input_box_xpath = Config.get("INPUT_XPATH_KIMI")
                submit_button_xpath = Config.get("SUBMIT_BUTTON_XPATH_KIMI")

            # 定位输入框
            input_box = self.driver.find_element(By.XPATH, input_box_xpath)
            input_box.send_keys(input_text)

            print(f"[DEBUG] 输入框已定位: {input_box_xpath}")

            # 定位提交按钮并点击
            submit_button = self.driver.find_element(By.XPATH, submit_button_xpath)
            submit_button.click()
            print(f"[DEBUG] 提交按钮已定位: {submit_button_xpath}")

            print(f"[INFO] 消息已发送: {input_text}")
        except Exception as e:
            print(f"[ERROR] 发送消息时发生错误: {e}")

    def receive_message(self, timeout=30):
        """
        接收网页返回的消息并写入 JSON 文件
        :param timeout: 最大等待时间（秒）
        """
        previous_text = ""
        new_text_list = []  # 用于存储新增的文本内容
        full_html = ""  # 用于存储完整的 HTML 源码
        # 根据 msg_cnt 动态生成 XPath
        response_xpath = Config.getResponseXpath(self.msg_cnt)
        print(f"[DEBUG] 当前 XPath: {response_xpath}")
        time.sleep(2)
        while True:
            try:
                response_element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, response_xpath))
                )

                # 获取元素的文本内容
                response_text = response_element.text

                # 如果有新内容，逐步存储到 new_text_list 列表
                if response_text != previous_text:
                    new_text = response_text[len(previous_text) :]  # 获取新增的部分
                    new_text_list.append(new_text)  # 存储新增的文本内容
                    previous_text = response_text  # 更新已输出的内容
                    print(f"[DEBUG] 成功获取新内容: {new_text}")

                # 如果回复内容已完整加载，可以根据具体情况判断是否退出循环
                if "回复完毕" in response_text:
                    print("\n\n[INFO] 回复已完整加载。")
                    # 获取完整的 HTML 源码
                    full_html = response_element.get_attribute("outerHTML")
                    break

                time.sleep(0.5)  # 每隔 0.5 秒检查一次内容
            except Exception as e:
                print(f"\n\n[ERROR] 获取回复内容时发生错误: {e}")
                break
        self.msg_cnt += 1
        # 将新数据写入 JSON 文件
        if new_text_list:
            return self.write_to_json(self.msg_cnt, new_text_list, full_html)

    def write_to_json(self, msg_cnt, new_text_list, full_html):
        """
        将新增内容写入 JSON 文件
        :param msg_cnt: 当前发送次数
        :param new_text_list: 新增的文本内容列表
        :param full_html: 完整的 HTML 源码
        """
        # 检查并删除包含指定内容的 <span> 标签
        if full_html:
            soup = BeautifulSoup(full_html, "html.parser")

            # 删除包含指定 xmlns 属性的 <span> 标签
            for span in soup.find_all("span"):
                if 'xmlns="http://www.w3.org/2000/svg"' in str(
                    span
                ) or 'xmlns:xlink="http://www.w3.org/1999/xlink"' in str(span):
                    span.decompose()  # 删除整个 <span> 标签及其内容

            # 删除最后的“我已回复完毕”内容
            last_node = soup.find("div", class_="paragraph last-node")
            if last_node and "回复完毕" in last_node.text:
                last_node.decompose()  # 删除整个 <div> 标签及其内容

            full_html = str(soup)  # 更新 HTML 源码

        # 加载旧数据
        old_data = self.json_handler.jsonIO(
            mode=self.json_handler.LDJSON, inputfile=self.output_file
        )
        if old_data is None:
            old_data = {}

        # 更新数据
        old_data[str(msg_cnt)] = {
            "text_list": old_data.get(str(msg_cnt), {}).get("text_list", [])
            + new_text_list,
            "full_html": full_html,
        }
        print(f"[DEBUG] 更新后的数据: {old_data}")
        # 写入文件
        try:
            self.json_handler.jsonIO(
                mode=self.json_handler.STJSON,
                output_file=self.output_file,
                outdata=old_data,
            )
        except Exception as e:
            print(f"[ERROR] 写入 JSON 文件时发生错误: {e}")

        return full_html

    def run(self, input_texts):
        """
        顺序执行消息发送和接收
        :param input_texts: 待发送的消息列表
        这里对字符串迭代，当然每次只发送一个字符，卡了我一整个下午，无语了家人们
        """
        try:
            # 启动浏览器
            self.start_browser()
            # 发送消息
            self.send_message(input_texts)
            # 接收消息
            self.receive_message()
            time.sleep(1)

        finally:
            # 关闭浏览器
            self.close_browser()

    def format_input_data(self, input_data):
        """
        将输入数据结构转换为单行字符串格式。
        :param input_data: 包含国家列表、起始年份和结束年份的字典
        :return: 格式化后的单行字符串
        """
        try:
            # 提取数据
            countries = ",".join(
                input_data.get("countries", [])
            )  # 将国家列表用逗号连接
            start_year = input_data.get("start_year", "")
            end_year = input_data.get("end_year", "")

            # 格式化为指定的单行字符串
            formatted_string = f"countries:{countries};Year:{start_year}-{end_year}."
            return formatted_string
        except Exception as e:
            raise ValueError(f"格式化输入数据时发生错误: {e}")


if __name__ == "__main__":
    # 示例用法
    url = Config.get("KIMI_URL")
    ai_module = AskTheFriendlyAI(url)
    input_texts = {
        "countries": ["Advanced economies", "United Kingdom", "United States", "China"],
        "start_year": 1980,
        "end_year": 2022,
    }
    ai_module.run(ai_module.format_input_data(input_texts))

    # countries:Advanced economies,United Kingdom,United States,China;1980-2022.
