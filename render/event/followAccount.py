from concurrent.futures import ThreadPoolExecutor
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

from utils.log_manager import LogManager
log_manager = LogManager()


executor = ThreadPoolExecutor(max_workers=4)

# 开始关注按钮事件
def on_follow_account_clicked(account_table, comment_table, spin_operations_per_account, spin_delay, window):
    """Start following accounts without blocking the GUI"""
    selected_accounts = get_selected_accounts(account_table)
    if not selected_accounts:
        QMessageBox.warning(window, "警告", "请先选择账号！")
        return

    # Get selected uids from the comment table
    uids = []
    for row in range(comment_table.rowCount()):
        if comment_table.item(row, 0).checkState() == Qt.Checked:
            uids.append(comment_table.item(row, 2).text())

    follow_limit = int(spin_operations_per_account)
    delay_seconds = int(spin_delay)

    # Use ThreadPoolExecutor to execute the task asynchronously
    executor.submit(follow_accounts_task, selected_accounts, uids, follow_limit, delay_seconds, account_table, comment_table, window, executor)

def follow_accounts_task(selected_accounts, uids, follow_limit, delay_seconds, account_table, comment_table, window, executor):
    """Task to perform the following operation in a background thread"""
    processed_uids = set()
    while len(processed_uids) < len(uids):
        for account in selected_accounts:
            cookies = load_cookies(account)
            follow_count = 0

            for uid in uids:
                if uid in processed_uids:
                    continue

                # Perform the follow operation
                result = follow_account(uid, cookies)
                follow_count += 1
                processed_uids.add(uid)

                # Update the follow status in the comment table
                if result == 0:
                    set_follow_status(comment_table, uid, "已关注")
                else:
                    set_follow_status(comment_table, uid, "关注失败")

                comment_table.viewport().update()
                # Switch accounts if the follow limit is reached
                if follow_count >= follow_limit:
                    break

                time.sleep(delay_seconds)

            if len(processed_uids) >= len(uids):
                break

        # Update account execution status in the table
        for account in selected_accounts:
            set_execution_status(account_table, account, "已执行")

    # Inform the user that the process is finished (optional)
    executor.close()


# 关注账号
#传入cookies和被关注用户ID
def follow_account(fid, cookies):
    """关注账号"""
    url = f"https://api.bilibili.com/x/relation/modify?x-bili-device-req-json=%7B%27platform%27%3A+%27web%27%7D"
    bili_ticket = get_bili_ticket(cookies.get("bili_jct"))
    cookie_dict = {
        "buvid3": cookies.get("buvid3"),
        "buvid4": cookies.get("buvid4"),
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
    log_manager.log(f"关注账户{fid}", f"{data['message']},code:{data['code']}")
    if data["code"] == 0:
        return data["code"]
    else:
        log_manager.log("follow_account", response.text)
    return data["code"]  # 0为成功
