from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import (
    QMessageBox
)
from PyQt5.QtCore import QMetaType
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
    is_running = False
    executor = None

    @staticmethod
    def create_executor():
        """创建一个新的ThreadPoolExecutor实例"""
        FollowAccountManager.executor = ThreadPoolExecutor(max_workers=4)

    @staticmethod
    def create_cookie_dict(cookies, bili_ticket):
        """创建统一的cookie字典"""
        #先检测cookies中是否有x-bili-gaia-vtoken，如果有添加
        if "x-bili-gaia-vtoken" not in cookies:
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
        else:
            base_cookies = {
                "buvid3": cookies.get("buvid3"),
                "buvid4": cookies.get("buvid4"),
                "SESSDATA": cookies.get("SESSDATA"),
                "bili_jct": cookies.get("bili_jct"),
                "sid": cookies.get("sid"),
                "DedeUserID": cookies.get("DedeUserID"),
                "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
                "bili_ticket": bili_ticket,
                "x-bili-gaia-vtoken": cookies.get("x-bili-gaia-vtoken")
            }
        return base_cookies

    @staticmethod
    def handle_follow_result(result, comment_table, uid, cookies):
        """处理关注结果"""
        if result["code"] == 0:
            set_follow_status(comment_table, uid, "已关注")
        elif isinstance(result, dict):
            if result["code"] == -352:
                v_voucher = result["data"]["v_voucher"]
                gaia_token_result = get_gaia_vtoken(v_voucher, cookies.get("bili_jct"),
                    "https://api.bilibili.com/x/relation/modify?x-bili-device-req-json=%7B%27platform%27%3A+%27web%27%7D")
                if gaia_token_result.get("code") != 0:
                    set_follow_status(comment_table, uid, "风控验证失败")
                    return True
                gaia_token = gaia_token_result["data"]["grisk_id"]
                #写入到当前的cookie中并保存,路径./cookies/{uid}.txt
                # 新增写入cookie文件逻辑
                account_uid = cookies.get("DedeUserID")
                file_path = f"./cookies/{account_uid}.txt"
                try:
                    # 读取现有内容并更新
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = [line for line in f if not line.startswith('x-bili-gaia-vtoken=')]
                    
                    # 添加新token行
                    lines.append(f"x-bili-gaia-vtoken={gaia_token}\n")
                    
                    # 写回文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                except Exception as e:
                    log_manager.log("handle_follow_result", f"写入cookie文件失败: {str(e)}")
                
                result = follow_account(uid, cookies)
                if result["code"] == 0:
                    set_follow_status(comment_table, uid, "已关注")
                else:
                    set_follow_status(comment_table, uid, "风控流程验证失败，尝试重复关注失败")
            elif result["code"]== 22014:
                set_follow_status(comment_table, uid, "已关注")
            else:
                set_follow_status(comment_table, uid, "关注失败")
        return True


# 开始关注按钮事件
def on_follow_account_clicked(account_table, comment_table, spin_operations_per_account, spin_delay, btn, window):
    """Start following accounts without blocking the GUI"""
    
    # 如果线程已经在运行，则停止线程并修改按钮文本
    if FollowAccountManager.is_running:
        FollowAccountManager.executor.shutdown(wait=False)  # 关闭线程池，所有未完成的任务将被取消
        FollowAccountManager.is_running = False
        btn.setText("开始关注")  # 恢复按钮文本为"开始关注"
        return
    
    # 否则，开始关注流程
    FollowAccountManager.is_running = True
    FollowAccountManager.create_executor()
    btn.setText("停止关注")  # 改变按钮文本为"停止关注"
    
    selected_accounts = get_selected_accounts(account_table)
    if not selected_accounts:
        QMessageBox.warning(window, "警告", "请先选择账号！")
        FollowAccountManager.is_running = False
        btn.setText("开始关注")
        return

    # 获取选中的uids
    uids = []
    for row in range(comment_table.rowCount()):
        if comment_table.item(row, 0).checkState() == Qt.Checked:
            uids.append(comment_table.item(row, 2).text())

    follow_limit = int(spin_operations_per_account)
    delay_seconds = int(spin_delay)

    # 使用ThreadPoolExecutor执行任务
    FollowAccountManager.executor.submit(follow_accounts_task, selected_accounts, uids, follow_limit, delay_seconds, account_table, comment_table, btn)

def follow_accounts_task(selected_accounts, uids, follow_limit, delay_seconds, account_table, comment_table, btn):
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

                    if FollowAccountManager.is_running is False:
                        break

                    try:
                        result = follow_account(uid, cookies)
                        follow_count += 1
                        processed_uids.add(uid)
                        
                        FollowAccountManager.handle_follow_result(result, comment_table, uid, cookies)
                        
                        if follow_count >= follow_limit:
                            break

                        time.sleep(delay_seconds)
                        comment_table.viewport().update()
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
        FollowAccountManager.is_running = False  # 完成任务后重置状态
        btn.setText("开始关注")  # 恢复按钮文本为"开始关注"


# 关注账号
#传入cookies和被关注用户ID    gaia_vtoken
def follow_account(fid, cookies):
    """关注账号"""
    cookie_dict = FollowAccountManager.create_cookie_dict(cookies, get_bili_ticket(cookies.get("bili_jct")))
    #检测cookies中是否有x-bili-gaia-vtoken，如果有添加到api中
    if cookie_dict.get("x-bili-gaia-vtoken") is None:
        url = f"https://api.bilibili.com/x/relation/modify?x-bili-device-req-json=%7B%27platform%27%3A+%27web%27%7D"
    else:
        url = f"https://api.bilibili.com/x/relation/modify?x-bili-device-req-json=%7B%27platform%27%3A+%27web%27%7D&gaia_vtoken={cookie_dict['x-bili-gaia-vtoken']}"
    bili_ticket = get_bili_ticket(cookies.get("bili_jct"))
    # post参数
    payload = f"csrf={cookies.get('bili_jct')}&act=1&re_src=14&fid={fid}"
    response = requests.post(url, cookies=cookie_dict, headers=get_header(), data=payload)
    data = response.json()
    print(f"关注账户{fid}: {data['message']},code:{data['code']}")
    log_manager.log(f"关注账户{fid}", f"{data['message']},code:{data['code']}")
    return data
