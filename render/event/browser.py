from PyQt5.QtWidgets import (
    QMessageBox, QFileDialog
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from utils.config_manager import save_browser_path_to_config
from utils.cookie_manager import load_cookies

def open_browser_with_cookie(browser_path, uid):
    """
    启动浏览器，并使用指定的浏览器路径和 cookies 打开页面
    """
    if not browser_path:
        QMessageBox.warning(None, "警告", "浏览器路径不能为空！")
        return
    if not uid:
        QMessageBox.warning(None, "警告", "UID 不能为空！")
        return

    try:
        # 加载 Cookie
        cookies = load_cookies(uid)

        # 设置浏览器路径
        url = f"https://space.bilibili.com/{uid}"

        # 配置 Chrome 启动选项
        if "chrome.exe" in browser_path.lower():
            options = Options()
        elif "msedge.exe" in browser_path.lower():
            options = EdgeOptions()
        
        options.binary_location = browser_path  # 指定 Chrome 浏览器路径
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # 启动浏览器
        if "chrome.exe" in browser_path.lower():
            driver = webdriver.Chrome(options=options)
        elif "msedge.exe" in browser_path.lower():
            driver = webdriver.Edge(options=options)

        # 打开目标页面，确保加载了正确的域名
        driver.get(url)

        # 设置 cookies，确保已经加载页面后再设置
        for cookie in [{
            'name': 'DedeUserID',
            'value': cookies.get('DedeUserID'),
            'domain': '.bilibili.com'
        }, {
            'name': 'DedeUserID__ckMd5',
            'value': cookies.get('DedeUserID__ckMd5'),
            'domain': '.bilibili.com'
        }, {
            'name': 'SESSDATA',
            'value': cookies.get('SESSDATA'),
            'domain': '.bilibili.com'
        }, {
            'name': 'bili_jct',
            'value': cookies.get('bili_jct'),
            'domain': '.bilibili.com'
        }, {
            'name': 'sid',
            'value': cookies.get('sid'),
            'domain': '.bilibili.com'
        }]:
            driver.add_cookie(cookie)

        # 刷新页面以便 cookies 生效
        driver.refresh()

    except FileNotFoundError as e:
        QMessageBox.critical(None, "错误", f"Cookie 文件加载失败：{e}")
    except Exception as e:
        QMessageBox.critical(None, "错误", f"打开浏览器失败：{e}")

def select_browser_path(input_browser_path, window):
    file_path, _ = QFileDialog.getOpenFileName(window, "选择浏览器路径", "", "Executable Files (*.exe)")
    if file_path:
        input_browser_path.setText(file_path)
        save_browser_path_to_config(file_path)
