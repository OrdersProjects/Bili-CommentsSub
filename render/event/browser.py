
import subprocess
from PyQt5.QtWidgets import (
    QMessageBox, QFileDialog
)

from utils.config_manager import save_browser_path_to_config

def open_browser_with_cookie(browser_path, uid):
    """
    使用指定浏览器路径打开 B 站用户主页，并附带指定账号的 cookie。
    """
    if not browser_path:
        QMessageBox.warning(None, "警告", "浏览器路径不能为空！")
        return
    if not uid:
        QMessageBox.warning(None, "警告", "UID 不能为空！")
        return

    try:
        url = f"https://space.bilibili.com/{uid}"
        # 使用 subprocess 调用浏览器
        subprocess.Popen([browser_path, url])
    except Exception as e:
        QMessageBox.critical(None, "错误", f"打开浏览器失败：{e}")


def select_browser_path(input_browser_path, window):
    file_path, _ = QFileDialog.getOpenFileName(window, "选择浏览器路径", "", "Executable Files (*.exe)")
    if file_path:
        input_browser_path.setText(file_path)
        save_browser_path_to_config(file_path)