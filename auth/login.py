from PyQt5.QtWidgets import QLabel, QMessageBox
from auth.cookie_login import CookieLoginDialog
from render.event.accountTable import start_account_list_refresh
from utils.cookie_manager import check_cookie_exists, save_cookies
from auth.qrcode_login import QrCodeLoginThread, get_qr_code, show_qr_code_dialog


def handle_login_success(cookies, dialog, window, account_table):
    """处理登录成功后的操作"""
    print("登录成功, cookie:" + str(cookies))  # 打印 cookies 字典

    dede_user_id = cookies.get('DedeUserID')
    if check_cookie_exists(dede_user_id):
        # 在保存 cookies 前弹出确认框
        reply = QMessageBox.question(window, '确认覆盖', 
                                     f"用户 {dede_user_id} 已存在，是否覆盖？", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            save_cookies(cookies, dede_user_id)
            QMessageBox.information(window, "登录成功", f"登录成功 | UID:{dede_user_id}")
        else:
            print("用户取消了覆盖操作")
    else:
        save_cookies(cookies, dede_user_id)
        QMessageBox.information(window, "登录成功", f"登录成功 | UID:{dede_user_id}")

    # 关闭对话框
    start_account_list_refresh(account_table)
    dialog.accept()


def on_scan_login_clicked(window, account_table):
    url, qrcode_key = get_qr_code()
    if url and qrcode_key:
        print("二维码获取成功")  # 打印日志
        status_label = QLabel("扫码登录状态：")
        dialog = show_qr_code_dialog(window, url, status_label)

        # 创建并启动二维码轮询线程
        thread = QrCodeLoginThread(qrcode_key)
        thread.status_update.connect(status_label.setText)  # 更新状态
        thread.login_success.connect(lambda cookies: handle_login_success(cookies, dialog, window, account_table))
        thread.start()  # 启动线程

        dialog.exec_()  # 继续执行对话框
    else:
        QMessageBox.warning(window, "二维码获取失败", "获取二维码失败，请重试")
        print("二维码获取失败")  # 打印日志


def on_cookie_login_clicked(window, account_table):
    """通过cookie登录"""
    dialog = CookieLoginDialog(window)
    if dialog.exec_():  # 如果登录成功
        handle_login_success(dialog.cookies, dialog, window, account_table)
