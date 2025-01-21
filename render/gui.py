from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget,
    QPushButton, QLabel, QLineEdit, QSpinBox, QTextEdit
)
from auth.login import on_scan_login_clicked, on_cookie_login_clicked
import sys

from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtCore import Qt

from render.accountTableRef import start_account_list_refresh

def create_gui():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("B站评论和粉丝采集工具")
    window.setGeometry(100, 100, 1000, 700)

    main_layout = QGridLayout()

    # 作品评论采集区域
    comment_group = QGroupBox("作品评论采集")
    comment_layout = QVBoxLayout()

    top_layout = QHBoxLayout()
    lbl_works = QLabel("作品地址：")
    input_works = QLineEdit()
    btn_collect_comments = QPushButton("开始采集")

    top_layout.addWidget(lbl_works)
    top_layout.addWidget(input_works)
    top_layout.addWidget(btn_collect_comments)

    # 评论区数据表格
    comment_table = QTableWidget()
    comment_table.setColumnCount(6)
    comment_table.setHorizontalHeaderLabels(["选择", "序号", "昵称", "uid", "评论内容", "结果"])
    comment_table.setColumnWidth(0, 30)
    comment_table.setColumnWidth(1, 50)
    comment_table.setColumnWidth(2, 150)
    comment_table.setColumnWidth(3, 150)
    comment_table.setColumnWidth(4, 400)
    comment_table.setColumnWidth(5, 100)

    btn_select_all_comments = QPushButton("全选")
    btn_clear_comments = QPushButton("清空列表")
    btn_export_comments = QPushButton("导出表格")
    lbl_current_execution = QLabel("当前执行序号：")
    input_execution_no = QLineEdit()

    comment_buttons_layout = QHBoxLayout()
    comment_buttons_layout.addWidget(btn_select_all_comments)
    comment_buttons_layout.addWidget(btn_clear_comments)
    comment_buttons_layout.addWidget(btn_export_comments)
    comment_buttons_layout.addWidget(lbl_current_execution)
    comment_buttons_layout.addWidget(input_execution_no)

    comment_layout.addLayout(top_layout)
    comment_layout.addWidget(comment_table)
    comment_layout.addLayout(comment_buttons_layout)
    comment_group.setLayout(comment_layout)

    # 账号管理区域
    account_group = QGroupBox("账号管理")
    account_layout = QVBoxLayout()

    # 账号列表表格
    lbl_account_list = QLabel("账号列表")
    account_table = QTableWidget()
    account_table.setColumnCount(5)
    account_table.setHorizontalHeaderLabels(["选择", "UID", "昵称", "登录状态", "执行状态"])
    account_table.setColumnWidth(0, 15)
    account_table.setColumnWidth(1, 100)
    account_table.setColumnWidth(2, 150)
    account_table.setColumnWidth(3, 80)
    account_table.setColumnWidth(4, 80)

    # 添加复选框和功能按钮
    account_buttons_layout = QHBoxLayout()
    btn_import_cookies = QPushButton("cookie登录")
    btn_scan_login = QPushButton("扫码登录")
    account_buttons_layout.addWidget(btn_import_cookies)
    account_buttons_layout.addWidget(btn_scan_login)

    account_layout.addWidget(lbl_account_list)
    account_layout.addWidget(account_table)
    account_layout.addLayout(account_buttons_layout)
    account_group.setLayout(account_layout)

    # 操作功能区
    action_group = QGroupBox("操作功能区")
    action_layout = QVBoxLayout()

    private_message_layout = QVBoxLayout()
    lbl_private_message = QLabel("私信内容：")
    text_private_message = QTextEdit()

    private_message_layout.addWidget(lbl_private_message)
    private_message_layout.addWidget(text_private_message)

    operation_buttons_layout = QHBoxLayout()
    btn_start_follow = QPushButton("开始关注")
    btn_start_message = QPushButton("开始私信")
    operation_buttons_layout.addWidget(btn_start_follow)
    operation_buttons_layout.addWidget(btn_start_message)

    operation_settings_layout = QHBoxLayout()
    lbl_delay = QLabel("私信/关注操作间隔(秒)：")
    spin_delay = QSpinBox()
    spin_delay.setRange(1, 60)
    spin_delay.setValue(6)
    lbl_operations_per_account = QLabel("账号私信/关注几次切换：")
    spin_operations_per_account = QSpinBox()
    spin_operations_per_account.setRange(1, 100)
    operation_settings_layout.addWidget(lbl_delay)
    operation_settings_layout.addWidget(spin_delay)
    operation_settings_layout.addWidget(lbl_operations_per_account)
    operation_settings_layout.addWidget(spin_operations_per_account)

    # 浏览器路径设置
    browser_path_layout = QHBoxLayout()
    lbl_browser_path = QLabel("浏览器路径：")
    input_browser_path = QLineEdit()
    btn_select_browser = QPushButton("选择路径")
    browser_path_layout.addWidget(lbl_browser_path)
    browser_path_layout.addWidget(input_browser_path)
    browser_path_layout.addWidget(btn_select_browser)

    action_layout.addLayout(private_message_layout)
    action_layout.addLayout(operation_buttons_layout)
    action_layout.addLayout(operation_settings_layout)
    action_layout.addLayout(browser_path_layout)

    action_group.setLayout(action_layout)

    # 添加到主布局
    main_layout.addWidget(comment_group, 0, 0, 1, 2)
    main_layout.addWidget(account_group, 1, 0)
    main_layout.addWidget(action_group, 1, 1)

    main_layout.setRowStretch(0, 1)
    main_layout.setRowStretch(1, 2)

    # 设置主窗口布局
    window.setLayout(main_layout)

    # 启动定时刷新账号列表
    start_account_list_refresh(account_table)

    # 扫码登录按钮的事件连接
    btn_scan_login.clicked.connect(lambda: on_scan_login_clicked(window))

    # cookie登录按钮的事件连接
    btn_import_cookies.clicked.connect(lambda: on_cookie_login_clicked(window))

    # 开始关注按钮的事件连接
    # btn_start_follow.clicked.connect(lambda: on_start_follow_clicked(account_table))

    window.show()
    sys.exit(app.exec_())


def get_selected_accounts(account_table):
    """获取选中的账号列表"""
    selected_accounts = []
    
    for row in range(account_table.rowCount()):
        checkbox_item = account_table.item(row, 0)  # 获取复选框所在的列（第0列）
        if checkbox_item.checkState() == Qt.Checked:  # 如果复选框被选中
            uid = account_table.item(row, 1).text()  # 获取 UID
            selected_accounts.append(uid)  # 将选中的 UID 加入列表
    
    return selected_accounts
