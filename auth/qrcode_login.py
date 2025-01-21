import requests
from PyQt5.QtCore import QThread, pyqtSignal
import time
import qrcode
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QImage, QPixmap
import numpy as np

from config import get_header

def get_qr_code():
    try:
        response = requests.get('https://passport.bilibili.com/x/passport-login/web/qrcode/generate', headers=get_header())
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                return data['data']['url'], data['data']['qrcode_key']
        print("二维码生成失败：", response.text)
    except Exception as e:
        print("获取二维码时发生错误：", str(e))
    return None, None


# 创建一个线程执行二维码轮询任务
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
                    self.login_success.emit(response.cookies)
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