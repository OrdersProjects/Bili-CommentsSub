from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QTableWidget,
    QPushButton, QLabel, QLineEdit, QSpinBox, QTextEdit
)
import sys
from PyQt5.QtCore import Qt
from auth.login import on_cookie_login_clicked, on_scan_login_clicked
from render.event.accountTable import show_context_menu, start_account_list_refresh
from render.event.browser import select_browser_path
from render.event.videoComment import (
    on_clear_comments_clicked, on_clear_followed_comments_clicked, on_clear_sent_messages_clicked, on_collect_comments_clicked, on_export_comments_clicked,
    on_select_all_comments_clicked, on_deselect_all_comments_clicked,
    on_select_male_comments_clicked, on_select_female_comments_clicked
)
from render.event.followAccount import on_follow_account_clicked
from render.event.sendMsg import on_send_msg_clicked
from render.event.fans import on_collect_fans_clicked
from utils.config_manager import load_browser_path_from_config


def create_gui():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("B站评论和粉丝采集工具")
    window.setGeometry(100, 100, 1500, 700)

    # 主布局
    main_layout = QGridLayout()

    # 左侧：作品评论采集/粉丝列表采集区域
    comment_group = QGroupBox("作品评论采集/粉丝列表采集")
    comment_layout = QVBoxLayout()

    # 顶部采集输入框和按钮
    lbl_works = QLabel("作品地址：")
    input_works = QLineEdit()
    btn_collect_comments = QPushButton("开始采集")

    lbl_fans = QLabel("目标用户UID")
    input_fans = QLineEdit()
    btn_collect_fans = QPushButton("开始采集")

    works_layout = QHBoxLayout()
    works_layout.addWidget(lbl_works)
    works_layout.addWidget(input_works)
    works_layout.addWidget(btn_collect_comments)

    fans_layout = QHBoxLayout()
    fans_layout.addWidget(lbl_fans)
    fans_layout.addWidget(input_fans)
    fans_layout.addWidget(btn_collect_fans)

    # 评论区数据表格
    comment_table = QTableWidget()
    comment_table.setColumnCount(6)
    comment_table.setHorizontalHeaderLabels(["选择", "昵称", "UID", "性别", "关注结果", "私信结果"])
    comment_table.setColumnWidth(0, 40)
    comment_table.setColumnWidth(1, 190)
    comment_table.setColumnWidth(2, 190)
    comment_table.setColumnWidth(3, 50)
    comment_table.setColumnWidth(4, 90)
    comment_table.setColumnWidth(5, 90)

    # 表格操作按钮（6 个按钮分三排两列）
    btn_select_all_comments = QPushButton("全选")
    btn_deselect_all_comments = QPushButton("取消全选")
    btn_select_male_comments = QPushButton("只选男性")
    btn_select_female_comments = QPushButton("只选女性")
    btn_clear_comments = QPushButton("清空列表")
    btn_export_comments = QPushButton("导出表格")
    btn_clear_followed = QPushButton("清除已关注")
    btn_clear_sent_msgs = QPushButton("清除已私信")

    button_grid_layout = QGridLayout()
    button_grid_layout.addWidget(btn_select_all_comments, 0, 0)
    button_grid_layout.addWidget(btn_deselect_all_comments, 0, 1)
    button_grid_layout.addWidget(btn_select_male_comments, 1, 0)
    button_grid_layout.addWidget(btn_select_female_comments, 1, 1)
    button_grid_layout.addWidget(btn_clear_comments, 2, 0)
    button_grid_layout.addWidget(btn_export_comments, 2, 1)
    button_grid_layout.addWidget(btn_clear_followed, 3, 0)
    button_grid_layout.addWidget(btn_clear_sent_msgs, 3, 1)

    comment_layout.addLayout(works_layout)
    comment_layout.addLayout(fans_layout)
    comment_layout.addWidget(comment_table)
    comment_layout.addLayout(button_grid_layout)
    comment_group.setLayout(comment_layout)

    # 右上角：账号管理区域
    account_group = QGroupBox("账号管理")
    account_layout = QVBoxLayout()
    lbl_account_list = QLabel("账号列表")
    account_table = QTableWidget()
    account_table.setColumnCount(5)
    account_table.setHorizontalHeaderLabels(["选择", "UID", "昵称", "登录状态", "执行状态"])
    account_table.setColumnWidth(0, 35)
    account_table.setColumnWidth(1, 100)
    account_table.setColumnWidth(2, 150)
    account_table.setColumnWidth(3, 80)
    account_table.setColumnWidth(4, 80)

    btn_import_cookies = QPushButton("cookie登录")
    btn_scan_login = QPushButton("扫码登录")
    account_buttons_layout = QHBoxLayout()
    account_buttons_layout.addWidget(btn_import_cookies)
    account_buttons_layout.addWidget(btn_scan_login)

    account_layout.addWidget(lbl_account_list)
    account_layout.addWidget(account_table)
    account_layout.addLayout(account_buttons_layout)
    account_group.setLayout(account_layout)

    # 右下角：操作功能区
    action_group = QGroupBox("操作功能区")
    action_layout = QVBoxLayout()

    lbl_private_message = QLabel("私信内容：")
    text_private_message = QTextEdit()
    action_layout.addWidget(lbl_private_message)
    action_layout.addWidget(text_private_message)

    operation_buttons_layout = QHBoxLayout()
    btn_start_follow = QPushButton("开始关注")
    btn_start_message = QPushButton("开始私信")
    operation_buttons_layout.addWidget(btn_start_follow)
    operation_buttons_layout.addWidget(btn_start_message)

    lbl_delay = QLabel("操作间隔(秒)：")
    spin_delay = QSpinBox()
    spin_delay.setRange(1, 60)
    spin_delay.setValue(6)
    lbl_operations_per_account = QLabel("每账号操作次数：")
    spin_operations_per_account = QSpinBox()
    spin_operations_per_account.setRange(1, 100)

    operation_settings_layout = QHBoxLayout()
    operation_settings_layout.addWidget(lbl_delay)
    operation_settings_layout.addWidget(spin_delay)
    operation_settings_layout.addWidget(lbl_operations_per_account)
    operation_settings_layout.addWidget(spin_operations_per_account)

    lbl_browser_path = QLabel("浏览器路径：")
    input_browser_path = QLineEdit()
    btn_select_browser = QPushButton("选择路径")
    browser_path_layout = QHBoxLayout()
    browser_path_layout.addWidget(lbl_browser_path)
    browser_path_layout.addWidget(input_browser_path)
    browser_path_layout.addWidget(btn_select_browser)

    action_layout.addLayout(operation_buttons_layout)
    action_layout.addLayout(operation_settings_layout)
    action_layout.addLayout(browser_path_layout)
    action_group.setLayout(action_layout)

    # 添加到主布局
    main_layout.addWidget(comment_group, 0, 0, 2, 1)  # 左侧占两行
    main_layout.addWidget(account_group, 0, 1)         # 右上角
    main_layout.addWidget(action_group, 1, 1)         # 右下角

    window.setLayout(main_layout)

    input_browser_path.setText(load_browser_path_from_config())

     # 启动定时刷新账号列表
    start_account_list_refresh(account_table)
    account_table.setContextMenuPolicy(Qt.CustomContextMenu)
    account_table.customContextMenuRequested.connect(lambda position: show_context_menu(account_table, input_browser_path, position))

    btn_select_browser.clicked.connect(lambda: select_browser_path(input_browser_path, window))

    # 扫码登录按钮的事件连接
    btn_scan_login.clicked.connect(lambda: on_scan_login_clicked(window, account_table))

    # cookie登录按钮的事件连接
    btn_import_cookies.clicked.connect(lambda: on_cookie_login_clicked(window, account_table))

    # 评论区开始采集按钮的事件连接
    btn_collect_comments.clicked.connect(lambda: on_collect_comments_clicked(input_works.text(), comment_table, account_table))

    # 粉丝列表开始采集按钮的事件连接
    btn_collect_fans.clicked.connect(lambda: on_collect_fans_clicked(input_fans.text(), comment_table, account_table))

    # 采集区全选/清空/导出按钮的事件连接
    btn_select_all_comments.clicked.connect(lambda: on_select_all_comments_clicked(comment_table))
    btn_clear_comments.clicked.connect(lambda: on_clear_comments_clicked(comment_table))
    btn_export_comments.clicked.connect(lambda: on_export_comments_clicked(comment_table))

    # 采集区取消全选按钮的事件连接
    btn_deselect_all_comments.clicked.connect(lambda: on_deselect_all_comments_clicked(comment_table))

    # 采集区只选男性按钮的事件连接
    btn_select_male_comments.clicked.connect(lambda: on_select_male_comments_clicked(comment_table))

     # 采集区只选女性按钮的事件连接
    btn_select_female_comments.clicked.connect(lambda: on_select_female_comments_clicked(comment_table))

    # 清除已关注按钮的事件连接
    btn_clear_followed.clicked.connect(lambda: on_clear_followed_comments_clicked(comment_table))

    # 清除已私信按钮的事件连接
    btn_clear_sent_msgs.clicked.connect(lambda: on_clear_sent_messages_clicked(comment_table))

    # 开始关注的事件连接
    btn_start_follow.clicked.connect(lambda: on_follow_account_clicked(account_table,comment_table,spin_delay.value(),spin_operations_per_account.value(),window))
    # 开始私信的事件连接
    btn_start_message.clicked.connect(lambda: on_send_msg_clicked(account_table,comment_table,text_private_message.toPlainText(),spin_delay.value(),spin_operations_per_account.value(),window))

    window.show()
    app.exec_()


if __name__ == "__main__":
    create_gui()
