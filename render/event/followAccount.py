from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import (
    QMessageBox
)
from PyQt5.QtCore import Qt
from render.event.accountTable import (
    get_selected_accounts, set_execution_status
)
from managers.cookie_manager import load_cookies
from render.event.commentTable import set_follow_status
from managers.header_manager import get_header
from auth.bili_ticket import get_bili_ticket
import requests
import time

from managers.log_manager import LogManager
from utils.fuck_v_voucher import get_gaia_vtoken
log_manager = LogManager()


class FollowAccountManager:
    executor = ThreadPoolExecutor(max_workers=4)

    @staticmethod
    def create_cookie_dict(cookies, bili_ticket, gaia_token=None):
        """创建统一的cookie字典"""
        base_cookies = {
            "buvid3": cookies.get("buvid3"),
            "buvid4": cookies.get("buvid4"),
            "SESSDATA": cookies.get("SESSDATA"),
            "bili_jct": cookies.get("bili_jct"),
            "sid": cookies.get("sid"),
            "DedeUserID": cookies.get("DedeUserID"),
            "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
            "bili_ticket": bili_ticket
        }
        if gaia_token:
            base_cookies["x-bili-gaia-vtoken"] = gaia_token
        return base_cookies

    @staticmethod
    def handle_follow_result(result, comment_table, uid, cookies):
        """处理关注结果"""
        if result == 0:
            set_follow_status(comment_table, uid, "已关注")
        elif isinstance(result, dict):
            if result.get("code") == -352:
                v_voucher = result["data"]["v_voucher"]
                gaia_token = get_gaia_vtoken(v_voucher, cookies.get("bili_jct"), 
                    "https://api.bilibili.com/x/relation/modify?x-bili-device-req-json=%7B%27platform%27%3A+%27web%27%7D")
                result = follow_account(uid, cookies, gaia_token, if_captcha=True)
                if result == 0:
                    set_follow_status(comment_table, uid, "已关注")
                else:
                    set_follow_status(comment_table, uid, "风控流程验证失败，尝试重复关注失败")
            elif result.get("code") == 22014:
                set_follow_status(comment_table, uid, "已关注")
            else:
                set_follow_status(comment_table, uid, "关注失败")
        return True


# 开始关注按钮事件
def on_follow_account_clicked(account_table, comment_table, spin_operations_per_account, spin_delay, window):
    """Start following accounts without blocking the GUI"""
    executor = ThreadPoolExecutor(max_workers=4)
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
    try:
        while len(processed_uids) < len(uids):
            for account in selected_accounts:
                cookies = load_cookies(account)
                if not cookies:
                    continue
                
                follow_count = 0

                for uid in uids:
                    if uid in processed_uids:
                        continue

                    try:
                        result = follow_account(uid, cookies)
                        follow_count += 1
                        processed_uids.add(uid)
                        
                        FollowAccountManager.handle_follow_result(result, comment_table, uid, cookies)
                        
                        if follow_count >= follow_limit:
                            break

                        time.sleep(delay_seconds)

                    except Exception as e:
                        log_manager.log("follow_accounts_task", f"Error processing uid {uid}: {str(e)}")
                        set_follow_status(comment_table, uid, "处理异常")

                if len(processed_uids) >= len(uids):
                    break

            # 批量更新账号状态
            for account in selected_accounts:
                set_execution_status(account_table, account, "已执行")

    finally:
        # 仅在需要时更新UI
        comment_table.viewport().update()


# 关注账号
#传入cookies和被关注用户ID    gaia_vtoken
def follow_account(fid, cookies,gaia_token=None,if_captcha=False):
    """关注账号"""
    if if_captcha == False:
        url = f"https://api.bilibili.com/x/relation/modify?x-bili-device-req-json=%7B%27platform%27%3A+%27web%27%7D"
    else:
        url = f"https://api.bilibili.com/x/relation/modify?x-bili-device-req-json=%7B%27platform%27%3A+%27web%27%7D&gaia_vtoken={gaia_token}"
    bili_ticket = get_bili_ticket(cookies.get("bili_jct"))
    if if_captcha == False:
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
    else:
        cookie_dict = {
            "buvid3": cookies.get("buvid3"),
            "buvid4": cookies.get("buvid4"),
            "SESSDATA": cookies.get("SESSDATA"),
            "bili_jct": cookies.get("bili_jct"),  # CSRF Token即为bili_jct
            "sid": cookies.get("sid"),
            "DedeUserID": cookies.get("DedeUserID"),
            "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
            "bili_ticket": bili_ticket,
            "x-bili-gaia-vtoken": gaia_token,
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
        return data # 0为成功
