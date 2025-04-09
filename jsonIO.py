import json


class jsonIO:

    def __init__(self, LDJSON=1, STJSON=2, SORTBYLEN=3, SORTBYKEY=4):
        self.LDJSON = LDJSON  # 加载
        self.STJSON = STJSON  # 存储
        self.SORTBYLEN = SORTBYLEN  # 按值长排序
        self.SORTBYKEY = SORTBYKEY  # 按键排序

    def jsonIO(
        self, mode=0, inputfile=None, output_file=None, outdata=None, sort_mode=None
    ):
        """
        通用 JSON 读写方法
        :param mode       : 操作模式
        :param inputfile  : 输入文件路径
        :param output_file: 输出文件路径
        :param outdata    : 要存储的数据
        :param sort_mode  : 排序模式
        :return: 加载模式返回数据，存储模式无返回值
        """
        if mode == self.LDJSON:
            try:
                with open(inputfile, "r", encoding="utf-8") as file:
                    data = json.load(file)
                return data
            except FileNotFoundError:
                print(f"[ERROR]  File '{inputfile}' not found.")
                return None
            except json.JSONDecodeError:
                print(f"[ERROR]  Failed to decode JSON from '{inputfile}'.")
                return None
            except Exception as e:
                print(f"[ERROR]  {e}")
                return None

        elif mode == self.STJSON:
            if sort_mode == self.SORTBYLEN:
                # 按值长度排序
                sorted_data = {
                    k: v
                    for k, v in sorted(outdata.items(), key=lambda item: len(item[1]))
                }
            elif sort_mode == self.SORTBYKEY:
                # 按键排序
                sorted_data = {
                    k: v for k, v in sorted(outdata.items(), key=lambda item: item[0])
                }
            else:
                # 不排序
                sorted_data = outdata

            try:
                with open(output_file, "w", encoding="utf-8") as file:
                    json.dump(sorted_data, file, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"[ERROR]  {e}")

        else:
            print("[ERROR]  Invalid mode specified.")
