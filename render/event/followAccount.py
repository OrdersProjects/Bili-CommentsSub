from PyQt5.QtWidgets import (
    QMessageBox
)
from PyQt5.QtCore import Qt
from render.event.accountTable import (
    get_selected_accounts, set_execution_status
)
from utils.cookie_manager import load_cookies
from render.event.commentTable import set_follow_status
from config import get_header
from auth.bili_ticket import get_bili_ticket
import requests
import time


# 开始关注按钮事件
def on_follow_account_clicked(account_table, comment_table, spin_operations_per_account, spin_delay, window):
    """开始关注按钮事件"""
    # 获取选中的登录账号
    selected_accounts = get_selected_accounts(account_table)
    if not selected_accounts:
        QMessageBox.warning(window, "警告", "请先选择账号！")
        return
    # 获取选择的评论账号uid
    uids = []
    for row in range(comment_table.rowCount()):
        # 检查第一列的复选框是否被选中
        if comment_table.item(row, 0).checkState() == Qt.Checked:
            # 获取第三列的UID
            uids.append(comment_table.item(row, 2).text())
    # 获取关注次数切换的数值
    follow_limit = int(spin_operations_per_account)
    # 获取私信/关注操作间隔的数值
    delay_seconds = int(spin_delay)
    # 遍历选中的登录账号
    for account in selected_accounts:
        cookies = load_cookies(account)
        follow_count = 0
        # 遍历评论账号uid
        for uid in uids:
            # 执行关注操作
            result = follow_account(uid, cookies)
            follow_count += 1
            # 检查是否需要切换账号
            if follow_count >= follow_limit:
                break
            time.sleep(delay_seconds)
            # 更新关注状态
            if result == 0:
                set_follow_status(comment_table, uid, "已关注")
            else:
                set_follow_status(comment_table, uid, "关注失败")

        # 更新账号执行状态
        set_execution_status(account_table, account, "已执行")


# 关注账号
#传入cookies和被关注用户ID
def follow_account(fid, cookies):
    """关注账号"""
    url = f"https://api.bilibili.com/x/relation/modify?x-bili-device-req-json=%7B%27platform%27%3A+%27web%27%7D"
    bili_ticket = get_bili_ticket(cookies.get("bili_jct"))
    cookie_dict = {
        "SESSDATA": cookies.get("SESSDATA"),
        "bili_jct": cookies.get("bili_jct"),  # CSRF Token即为bili_jct
        "sid": cookies.get("sid"),
        "DedeUserID": cookies.get("DedeUserID"),
        "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
        "bili_ticket": bili_ticket
    }
    # post参数
    payload = f"csrf={cookies.get('bili_jct')}&act=1&re_src=14&fid={fid}"
    response = requests.post(url, cookies=cookie_dict, headers=get_header(), data=payload)
    data = response.json()
    print(f"关注账户{fid}: {data['message']},code:{data['code']}")
    return data["code"]  # 0为成功
