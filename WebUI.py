import gradio as gr
import matplotlib
import matplotlib.pyplot as plt
from Config import Config
import threading

matplotlib.use("Agg")  # 使用非交互式后端以避免图形显示问题（很奇怪，昨天不加也能跑）
from AiModule import AskTheFriendlyAI


class WebUI:
    def __init__(self, server):
        """
        初始化 WebUI 类。
        :param server: Server 类的实例
        """
        self.server = server

        self.countryNames = []  # 初始化为空列表
        self.is_ready = False
        self.interface = self.create_interface()  # 创建界面

        self.ai_module = AskTheFriendlyAI(url=Config.get("KIMI_URL"))
        self.browser_thread = threading.Thread(
            target=self.ai_module.start_browser, daemon=True
        )
        self.browser_thread.start()

    def create_interface(self):
        """
        创建 Gradio 界面。
        """

        def query_gdp_trend(selected_countries, start_year, end_year):
            """
            查询 GDP 趋势图。
            :param selected_countries: 用户选择的国家名称列表
            :param start_year: 用户选择的起始年份
            :param end_year: 用户选择的结束年份
            :return: GDP 趋势图
            """
            if not self.server.is_ready:
                # 记录日志
                self.server.logger.warning("后端未准备就绪，无法查询 GDP 趋势图。")
                # 返回一个空图形，并在图形上显示提示信息
                fig, ax = plt.subplots()
                ax.text(
                    0.5,
                    0.5,
                    "后端正在初始化，请稍后再试。",
                    fontsize=12,
                    ha="center",
                    va="center",
                )
                ax.axis("off")
                return fig

            try:
                # 调用服务器的 getGDPTrend 方法，传递国家列表和年份范围
                self.server.logger.info(
                    f"查询 GDP 趋势图，国家：{selected_countries}，年份范围：{start_year}-{end_year}"
                )
                fig = self.server.getGDPTrend(
                    selected_countries, int(start_year), int(end_year)
                )

                if fig is None:
                    # 如果返回值为 None，记录日志并生成一个空图形
                    self.server.logger.error(
                        f"未能生成 GDP 趋势图，国家：{selected_countries}，年份范围：{start_year}-{end_year}"
                    )
                    fig, ax = plt.subplots()
                    ax.text(
                        0.5,
                        0.5,
                        "未能生成 GDP 趋势图，请检查输入的国家名称或年份范围。",
                        fontsize=12,
                        ha="center",
                        va="center",
                    )
                    ax.axis("off")
                    return fig

                return fig  # 返回图形
            except Exception as e:
                # 捕获异常并记录日志
                self.server.logger.exception(f"查询 GDP 趋势图时发生错误：{e}")
                # 返回一个空图形，显示错误信息
                fig, ax = plt.subplots()
                ax.text(
                    0.5, 0.5, f"查询失败：{e}", fontsize=12, ha="center", va="center"
                )
                ax.axis("off")
                return fig

        # 这一部分其实改成进程间通信会比较好一点，可以实现流式输出，并且还可以弄一个任务队列/拒绝服务策略
        # 另一种改法是在receive_message中每接收到新数据就存一次（这部分的流式输出已经实现过了）
        #        之后在gradio这里就循环查询有没有新数据，有就更新（还可以设一个信号量来标识是否需要更新）
        # 但是这两种改法都需要修改大段代码，鉴于这只是个小作业，卷到这个程度感觉已经可以了
        def query_ai_analysis(selected_countries, start_year, end_year):
            """
            查询 AI 分析结果。
            :param selected_countries: 用户选择的国家名称列表
            :param start_year: 用户选择的起始年份
            :param end_year: 用户选择的结束年份
            :return: AI 分析结果
            """
            try:
                # 调用服务器的 getRawGDPData 方法，传递国家列表和年份范围
                self.server.logger.info(
                    f"查询 AI 分析，国家：{selected_countries}，年份范围：{start_year}-{end_year}"
                )
                raw_data = {}
                raw_data["countries"] = selected_countries
                raw_data["start_year"] = start_year
                raw_data["end_year"] = end_year
                query_data = self.ai_module.format_input_data(
                    raw_data
                )  # 格式化输入数据
                self.server.logger.info(f"[DEBUG]: {query_data}")
                self.ai_module.send_message((query_data))
                ai_response = self.ai_module.receive_message()

                return ai_response  # 返回 AI 的回复
            except Exception as e:
                # 捕获异常并记录日志
                self.server.logger.exception(f"查询 AI 分析时发生错误：{e}")
                return f"查询失败：{e}"

        def update_country_names():
            """
            更新国家名称列表。
            """
            if self.server.is_ready and not self.is_ready:
                self.is_ready = True
                self.server.logger.info("更新国家名称列表。")
                self.countryNames = self.server.getNames()
            return gr.update(choices=self.countryNames)

        def update_end_year_options(start_year):
            """
            根据起始年份动态更新终止年份选项。
            :param start_year: 用户选择的起始年份
            :return: 更新后的终止年份选项
            """
            if start_year:
                start_year = int(start_year)
                return gr.update(
                    choices=list(range(start_year, Config.get("END_YEAR") + 1))
                )
            return gr.update()

        def get_client_ip_info(request=None):
            # 这一部分想做成获取用户IP的，但暂时不好实现，先空着
            if request:
                client_ip = request.headers.get("X-Forwarded-For", request.client.host)
                client_ip = client_ip.split(",")[0].strip()
            else:
                client_ip = None
            info = self.server.getWeatherInfo(client_ip)
            if info:
                return (
                    f"服务器位置 | {info['ip_res']}\n"
                    f" | 温度: {info['temperature']} ℃\n"
                    f"海拔: {info['elevation']} m\n"
                    f"时区: {info['timezone']}\n"
                    f"风速: {info['windspeed']} km/h"
                )
            else:
                return "无法获取信息"

        # 创建 Gradio 界面
        with gr.Blocks(
            css="""
            #submit_button {
                background-color: #f68b08;
                color: black;
                font-weight: bold;
            }
        """
        ) as demo:
            client_ip_info_box = gr.Markdown(
                label="服务器信息", value="正在获取服务器信息..."
            )
            demo.load(
                lambda: get_client_ip_info(),
                inputs=None,
                outputs=client_ip_info_box,
            )
            gr.Markdown("# GDP 趋势查询系统")
            with gr.Row():
                country_selector = gr.Dropdown(
                    label="选择国家（支持多选）",
                    choices=self.countryNames,  # 初始为空列表
                    multiselect=True,
                )
            with gr.Row():
                start_year_selector = gr.Dropdown(
                    label="选择起始年份",
                    choices=list(
                        range(Config.get("START_YEAR"), Config.get("END_YEAR") + 1)
                    ),
                )
                end_year_selector = gr.Dropdown(
                    label="选择结束年份",
                    choices=list(
                        range(Config.get("START_YEAR"), Config.get("END_YEAR") + 1)
                    ),
                )
            with gr.Row():
                submit_button = gr.Button("查询", elem_id="submit_button")
            output = gr.Plot(label="GDP 趋势图")
            message_box = gr.Markdown(
                label="解析：", value="请点击查询按钮并等待获取解析结果"
            )

            # 绑定按钮点击事件
            submit_button.click(
                query_gdp_trend,
                inputs=[country_selector, start_year_selector, end_year_selector],
                outputs=output,  # 仅更新图形
            )
            submit_button.click(
                query_ai_analysis,
                inputs=[country_selector, start_year_selector, end_year_selector],
                outputs=message_box,  # 仅更新“解析”文本框
            )

            # 动态更新终止年份选项
            start_year_selector.change(
                update_end_year_options,
                inputs=start_year_selector,
                outputs=end_year_selector,
            )

            # 动态更新国家名称列表
            demo.load(update_country_names, inputs=None, outputs=country_selector)

        return demo

    def launch(self):
        """
        启动 Gradio 界面。
        """
        self.server.logger.info("启动 Gradio 界面。")
        self.interface.launch()
