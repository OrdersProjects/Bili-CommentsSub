import re
import requests
from PyQt5.QtWidgets import QDialog, QLabel, QTextEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from utils.cookie_manager import COOKIE_DIR, check_cookie_exists
from config import get_header
from utils.log_manager import LogManager
log_manager = LogManager()

def extract_cookies(cookie_str):
    """
    从用户提供的 cookie 字符串中提取所需的 cookies
    """
    cookie_dict = {}

    # 使用正则提取所需的 cookie 项
    cookies_to_extract = ['buvid3', 'buvid4', 'DedeUserID', 'DedeUserID__ckMd5', 'SESSDATA', 'bili_jct', 'sid']
    for cookie_name in cookies_to_extract:
        match = re.search(f"{cookie_name}=([^;]+)", cookie_str)
        if match:
            cookie_dict[cookie_name] = match.group(1)
    
    return cookie_dict


def validate_cookies(cookies):
    """
    验证 cookies 是否有效
    通过请求 Bilibili 的接口来验证 cookies 是否有效
    """
    cookies_dict = {
        "buvid3": cookies.get("buvid3"),
        "buvid4": cookies.get("buvid4"),
        "DedeUserID": cookies.get("DedeUserID"),
        "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
        "SESSDATA": cookies.get("SESSDATA"),
        "bili_jct": cookies.get("bili_jct"),
        "sid": cookies.get("sid"),
    }

    try:
        response = requests.get("https://api.bilibili.com/x/web-interface/nav", headers=get_header(), cookies=cookies_dict)
        result = response.json()
        if result["code"] == 0:
            return True  # 有效
        else:
            log_manager.log("validate_cookies", response.text)
            return False  # 无效
    except Exception as e:
        print(f"验证 cookies 时出错：{e}")
        return False  # 无效


# 处理 cookie 登录的线程
class CookieLoginThread(QThread):
    login_success = pyqtSignal(dict)  # 登录成功时发射 cookies 信号
    status_update = pyqtSignal(str)  # 更新状态的信号

    def __init__(self, cookie_str):
        super().__init__()
        self.cookie_str = cookie_str

    def run(self):
        # 提取 cookies
        cookies = extract_cookies(self.cookie_str)

        if not cookies:
            self.status_update.emit("无法从输入的 cookie 字符串中提取到有效的信息")
            return

        # 验证 cookies 是否有效
        if not validate_cookies(cookies):
            self.status_update.emit("无效的 Cookie，请检查您的 Cookie 是否有效")
            return

        # 登录成功，发出信号
        self.login_success.emit(cookies)


class CookieLoginDialog(QDialog):
    def __init__(self, window):
        super().__init__(window)
        self.setWindowTitle("通过 Cookie 登录")

        # 布局
        layout = QVBoxLayout()

        self.info_label = QLabel("请输入浏览器中提取的 Cookie 内容：")
        self.cookie_input = QTextEdit(self)
        self.cookie_input.setPlaceholderText("粘贴您的 cookie 字符串到此...")

        self.ok_button = QPushButton("确定", self)
        self.ok_button.clicked.connect(self.on_ok_clicked)

        layout.addWidget(self.info_label)
        layout.addWidget(self.cookie_input)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

        self.thread = None  # 存储线程引用，避免被销毁
        self.cookies = None  # 用于存储cookies

    def on_ok_clicked(self):
        cookie_str = self.cookie_input.toPlainText().strip()
        if not cookie_str:
            QMessageBox.warning(self, "警告", "请输入有效的 cookie 字符串")
            return
        
        # 创建并启动 Cookie 登录线程
        self.thread = CookieLoginThread(cookie_str)
        self.thread.status_update.connect(self.update_status)  # 更新状态
        self.thread.login_success.connect(self.accept_login_success)  # 登录成功后触发信号
        self.thread.start()  # 启动线程

    def update_status(self, status):
        """更新状态标签"""
        self.info_label.setText(status)

    def accept_login_success(self, cookies):
        """接受登录成功信号，返回 cookies"""
        self.cookies = cookies  # 将 cookies 保存到 dialog 中
        self.accept()  # 关闭对话框

    def closeEvent(self, event):
        """重写关闭事件，确保线程在对话框关闭时结束"""
        if self.thread and self.thread.isRunning():
            self.thread.terminate()  # 强制终止线程
            self.thread.wait()  # 等待线程终止

        event.accept()  # 正常关闭对话框
