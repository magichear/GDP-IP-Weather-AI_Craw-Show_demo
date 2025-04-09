import gradio as gr
import matplotlib.pyplot as plt


class WebUI:
    def __init__(self, server, countryNames=None):
        """
        初始化 WebUI 类。
        :param server: Server 类的实例
        """
        self.server = server
        self.interface = self.create_interface()
        self.countryNames = countryNames
        self.is_ready = False

    def create_interface(self):
        """
        创建 Gradio 界面。
        """

        def query_gdp_trend(country_names):
            """
            查询 GDP 趋势图。
            :param country_names: 用户输入的国家名称（分号分隔）
            :return: GDP 趋势图或提示信息
            """
            if not self.server.is_ready:
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
            if not self.is_ready:  # 第一次运行加载国家名称列表
                self.is_ready = True
                self.countryNames = self.server.getNames()
            country_list = [name.strip() for name in country_names.split(";")]
            try:
                fig = self.server.getGDPTrend(
                    country_list, self.server.start_year, self.server.end_year
                )
                if fig is None:
                    # 如果返回值为 None，生成一个空图形并显示错误信息
                    fig, ax = plt.subplots()
                    ax.text(
                        0.5,
                        0.5,
                        "未能生成 GDP 趋势图，请检查输入的国家名称。",
                        fontsize=12,
                        ha="center",
                        va="center",
                    )
                    ax.axis("off")
                return fig
            except Exception as e:
                # 捕获异常并返回一个空图形，显示错误信息
                fig, ax = plt.subplots()
                ax.text(
                    0.5, 0.5, f"查询失败：{e}", fontsize=12, ha="center", va="center"
                )
                ax.axis("off")
                return fig

        # 创建 Gradio 界面
        with gr.Blocks() as demo:
            gr.Markdown("# GDP 趋势查询系统")
            with gr.Row():
                country_input = gr.Textbox(label="输入国家名称（多个国家用分号分隔）")
                submit_button = gr.Button("提交")
            output = gr.Plot(label="GDP 趋势图")

            # 绑定按钮点击事件
            submit_button.click(query_gdp_trend, inputs=country_input, outputs=output)

        return demo

    def launch(self):
        """
        启动 Gradio 界面。
        """
        self.interface.launch()
