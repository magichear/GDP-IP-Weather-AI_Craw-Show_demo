import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class AskTheFriendlyAI:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.message_queue = queue.Queue()  # 消息队列
        self.response_ready = threading.Event()  # 信号：回复接收完成
        self.response_ready.set()  # 初始状态为允许发送消息
        self.executor = ThreadPoolExecutor(max_workers=2)  # 线程池，固定两个线程
        self.msg_cnt = 1  # 发送计数器，初始值为 1

    def start_browser(self):
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920,1080")
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_argument("--no-sandbox")
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
        time.sleep(3)

    def close_browser(self):
        if self.driver:
            self.driver.quit()

    def send_message(self):
        first_send = True  # 标记是否是第一次发送

        while True:
            # 等待回复接收完成
            self.response_ready.wait()

            # 从队列中获取消息
            input_text = self.message_queue.get()
            try:
                # 根据是否是第一次发送，选择不同的 XPath
                if first_send:
                    input_box_xpath = '//*[@id="app"]/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div[1]/p'
                    submit_button_xpath = '//*[@id="app"]/div/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div'
                    first_send = False  # 发送完成后切换到第二次发送的 XPath
                else:
                    input_box_xpath = '//*[@id="app"]/div/div/div[2]/div/div/div[1]/div[3]/div[2]/div[1]/div/div[1]/p'
                    submit_button_xpath = '//*[@id="app"]/div/div/div[2]/div/div/div[1]/div[3]/div[2]/div[2]/div[2]/div/div'

                input_box = self.driver.find_element(By.XPATH, input_box_xpath)
                input_box.send_keys(input_text)
                time.sleep(2)

                submit_button = self.driver.find_element(By.XPATH, submit_button_xpath)
                submit_button.click()

                # 发送后清除队列中的消息
                self.message_queue.task_done()

                # 设置信号为未完成状态，等待回复接收完成
                self.response_ready.clear()
            except Exception as e:
                print(f"[ERROR] 发送消息时发生错误: {e}")

    def receive_message(self, timeout=30):
        previous_text = ""
        start_time = time.time()

        while True:
            try:
                # 根据 msg_cnt 动态生成 XPath
                response_xpath = f'//*[@id="app"]/div/div/div[2]/div/div/div[1]/div[2]/div/div[{2 * self.msg_cnt}]/div/div[2]/div[1]/div[1]/div[2]/div'
                # print(f"[DEBUG] 当前 XPath: {response_xpath}")
                # //*[@id="app"]/div/div/div[2]/div/div/div[1]/div[2]/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div
                response_element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, response_xpath))
                )
                response_text = response_element.text

                # 如果有新内容，逐步输出到终端
                if response_text != previous_text:
                    new_text = response_text[len(previous_text) :]  # 获取新增的部分
                    print(new_text, end="", flush=True)  # 输出新增内容
                    previous_text = response_text  # 更新已输出的内容

                # 如果回复内容已完整加载，可以根据具体情况判断是否退出循环
                if "我已回复完毕" in response_text:
                    print("\n\n[INFO] 回复已完整加载。")
                    break

                time.sleep(0.5)  # 每隔 0.5 秒检查一次内容
            except Exception as e:
                print(f"\n\n[ERROR] 获取回复内容时发生错误: {e}")
                break

        # 设置信号为完成状态，允许发送下一条消息
        self.response_ready.set()

        # 接收完一条消息后，自增 msg_cnt
        self.msg_cnt += 1
        return previous_text

    def run(self, input_texts):
        """
        启动线程池并运行消息发送和接收逻辑
        :param input_texts: 待发送的消息列表
        """
        try:
            # 启动浏览器
            self.start_browser()

            # 启动发送消息线程
            self.executor.submit(self.send_message)

            # 将消息加入队列
            for text in input_texts:
                self.message_queue.put(text)

            # 启动接收消息线程
            self.executor.submit(self.receive_message)

            # 等待所有消息发送完成
            self.message_queue.join()
        finally:
            # 关闭线程池和浏览器
            self.executor.shutdown(wait=True)
            self.close_browser()


if __name__ == "__main__":
    input_texts = [
        "请你详细介绍一下统一牌绿茶（低糖）的成分和营养成分表。当你回复完毕后请严格回复“我已回复完毕”，之后你对我所有提问的回复都需要以“我已回复完毕”结尾",
        "低糖会比全糖更健康吗？",
        "请问今天的天气怎么样？",
    ]
    url = "https://kimi.moonshot.cn/chat/"

    browser = AskTheFriendlyAI(url)
    browser.run(input_texts)
