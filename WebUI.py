import gradio as gr
import matplotlib
import matplotlib.pyplot as plt
from Config import Config

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

        # 将 server 的 logger 传递给 AiModule
        self.ai_module = AskTheFriendlyAI(url=Config.get("KIMI_URL"))
        self.ai_module.start_browser()  # 启动浏览器

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
