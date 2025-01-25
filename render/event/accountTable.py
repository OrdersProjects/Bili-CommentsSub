# 定时刷新账号列表
import os
from render.event.browser import open_browser_with_cookie
from utils.cookie_manager import COOKIE_DIR, delete_cookie, get_all_cookies, load_cookies
from utils.getUserInfo import get_username
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMenu, QTableWidgetItem
)
def update_account_list(account_table):
    """更新账号列表"""
    # 获取所有 cookie 文件（即 UID）
    print("读取Cookie列表")
    all_cookies = get_all_cookies()
    print(all_cookies)
    
    account_table.setRowCount(len(all_cookies))  # 设置表格行数

    for row, uid in enumerate(all_cookies):
        # 读取每个 cookie 文件内容
        cookie_file_path = os.path.join(COOKIE_DIR, f"{uid}.txt")
        with open(cookie_file_path, 'r') as f:
            cookies = {line.split('=')[0]: line.split('=')[1].strip() for line in f.readlines()}

        # 获取账号的昵称和登录状态
        uname, is_logged_in = get_username(cookies)

        # 创建复选框并添加到表格的第一列
        checkbox_item = QTableWidgetItem()
        checkbox_item.setCheckState(Qt.Unchecked)  # 默认不选中
        account_table.setItem(row, 0, checkbox_item)  # 第 0 列为复选框

        # 更新表格中的内容
        account_table.setItem(row, 1, QTableWidgetItem(uid))  # UID
        account_table.setItem(row, 2, QTableWidgetItem(uname if uname else "未知"))  # 昵称
        account_table.setItem(row, 3, QTableWidgetItem("已登录" if is_logged_in else "未登录"))  # 登录状态
        account_table.setItem(row, 4, QTableWidgetItem("待执行"))  # 执行状态（暂时不管）


# 在 GUI 中定时更新账号列表
def start_account_list_refresh(account_table):
    """定时刷新账号列表"""
    print("开始刷新账号列表")
    QTimer.singleShot(1000, lambda: update_account_list(account_table))


def get_selected_accounts(account_table):
    """获取选中的账号列表"""
    selected_accounts = []
    
    for row in range(account_table.rowCount()):
        checkbox_item = account_table.item(row, 0)  # 获取复选框所在的列（第0列）
        if checkbox_item.checkState() == Qt.Checked:  # 如果复选框被选中
            uid = account_table.item(row, 1).text()  # 获取 UID
            selected_accounts.append(uid)  # 将选中的 UID 加入列表
    
    return selected_accounts


def set_execution_status(account_table, uids, status="已执行"):
    """根据传入的 uid 列表设置执行状态为指定状态"""
    for row in range(account_table.rowCount()):
        uid_item = account_table.item(row, 1)  # 获取 UID 所在列（第 1 列）
        if uid_item and uid_item.text() in uids:
            execution_status_item = account_table.item(row, 4)  # 获取执行状态列（第 4 列）
            if execution_status_item:
                execution_status_item.setText(status)  # 设置执行状态为 "已执行" 或其他状态


 # 添加右键菜单功能
def show_context_menu(account_table, input_browser_path, position):
    index = account_table.indexAt(position)
    if not index.isValid():
        return

    uid = account_table.item(index.row(), 1).text()

    menu = QMenu()
    open_home_action = menu.addAction("打开主页")
    delete_account_action = menu.addAction("删除账号")

    action = menu.exec_(account_table.viewport().mapToGlobal(position))
    if action == open_home_action:
        open_browser_with_cookie(input_browser_path.text(), uid)
    elif action == delete_account_action:
        delete_cookie(uid)
        account_table.removeRow(index.row())