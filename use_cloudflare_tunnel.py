# Ubuntu 安装cloudflare
# !wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
# !sudo dpkg -i cloudflared-linux-amd64.deb

# Windows11 手动下载安装 cloudflare
# 浏览器打开 https://github.com/cloudflare/cloudflared/releases/download/2024.9.1/cloudflared-windows-amd64.msi

import subprocess
import threading
import time
import socket
import urllib.request
import os
import argparse


def iframe_thread(port):
    while True:
        time.sleep(0.5)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("127.0.0.1", port))
        if result == 0:
            break
        sock.close()
    print(
        "\nxxxxxx finished loading, trying to launch cloudflared (if it gets stuck here cloudflared is having issues)\n"
    )

    p = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://127.0.0.1:{}".format(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    for line in p.stderr:
        l = line.decode()
        if "trycloudflare.com " in l:
            print("This is the URL to access xxxxxx:", l[l.find("http") :], end="")
        # print(l, end='')


threading.Thread(target=iframe_thread, daemon=True, args=(7860,)).start()

os.system("python Main.py")
