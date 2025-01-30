import requests
from PyQt5.QtCore import QThread, pyqtSignal
import time
import qrcode
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage
import numpy as np
from config import get_header
from utils.log_manager import LogManager

log_manager = LogManager()

def get_qr_code():
    try:
        response = requests.get('https://passport.bilibili.com/x/passport-login/web/qrcode/generate', headers=get_header())
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                return data['data']['url'], data['data']['qrcode_key']
        else:
            log_manager.log("get_qr_code", response.text)
        print("二维码生成失败：", response.text)
    except Exception as e:
        print("获取二维码时发生错误：", str(e))
    return None, None


class QrCodeLoginThread(QThread):
    status_update = pyqtSignal(str)  # 用来更新状态的信号
    login_success = pyqtSignal(object)  # 登录成功时发射cookies信号

    def __init__(self, qrcode_key):
        super().__init__()
        self.qrcode_key = qrcode_key

    def run(self):
        """运行二维码轮询逻辑"""
        while True:
            response = requests.get(
                'https://passport.bilibili.com/x/passport-login/web/qrcode/poll',
                params={'qrcode_key': self.qrcode_key}, headers=get_header()
            )
            if response.status_code == 200:
                data = response.json()
                if data['data']['code'] == 0:
                    # 登录成功
                    self.status_update.emit("登录成功！")
                    # 在这里进行获取 b_3 和 b_4，并添加到 cookies 中
                    cookies = response.cookies

                    # 获取b_3和b_4并将其添加到cookies
                    self._add_additional_cookies(cookies)

                    # 发射更新后的cookies
                    self.login_success.emit(cookies)
                    break
                elif data['data']['code'] == 86038:
                    # 二维码已失效
                    self.status_update.emit("二维码已失效，请重新扫码")
                    break
                elif data['data']['code'] == 86090:
                    # 已扫码未确认
                    self.status_update.emit("已扫码，等待确认...")
                elif data['data']['code'] == 86101:
                    # 未扫码
                    self.status_update.emit("等待扫码...")

            time.sleep(2)  # 每隔2秒轮询一次

    def _add_additional_cookies(self, cookies):
        """发起请求获取b_3和b_4，并将其作为buvid3和buvid4添加到cookies中"""
        try:
            # 使用当前的cookies发起请求
            response = requests.get(
                'https://api.bilibili.com/x/frontend/finger/spi',
                headers=get_header(),
                cookies=cookies
            )

            if response.status_code == 200:
                data = response.json()
                if data['code'] == 0:
                    b_3 = data['data'].get('b_3')
                    b_4 = data['data'].get('b_4')

                    # 如果b_3和b_4存在，则添加到cookies
                    if b_3:
                        cookies.set('buvid3', b_3)
                    if b_4:
                        cookies.set('buvid4', b_4)

                    print(f"添加到Cookies: buvid3={b_3}, buvid4={b_4}")
        except Exception as e:
            log_manager.log("获取b_3和b_4失败", str(e))
            print("获取 b_3 和 b_4 时发生错误：", str(e))


def pil_image_to_qimage(img):
    """将PIL Image转换为QImage"""
    img = img.convert("RGBA")
    data = np.array(img)
    height, width, channels = data.shape
    return QImage(data.data, width, height, channels * width, QImage.Format_RGBA8888)


def show_qr_code_dialog(window, url, status_label):
    """生成并显示二维码，以及显示登录状态"""
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    if img:
        print("二维码生成成功")
    else:
        print("二维码生成失败")

    qim = pil_image_to_qimage(img)
    pixmap = QPixmap.fromImage(qim)

    # 创建对话框显示二维码
    dialog = QDialog(window)
    dialog.setWindowTitle("扫码登录")
    layout = QVBoxLayout()

    # 显示二维码
    label = QLabel()
    label.setPixmap(pixmap)
    layout.addWidget(label)

    # 显示状态标签
    layout.addWidget(status_label)
    
    dialog.setLayout(layout)
    dialog.show()

    # 刷新界面
    window.repaint() 

    return dialog
