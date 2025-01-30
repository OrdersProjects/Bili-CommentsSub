import random
import string
import requests
import time
from config import get_header
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from render.event.accountTable import get_selected_accounts, set_execution_status
from render.event.commentTable import set_message_status
from utils.cookie_manager import load_cookies
from auth.bili_ticket import get_bili_ticket
import json

from utils.log_manager import LogManager
log_manager = LogManager()

def generate_deviceid():
    deviceid = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    return ''.join(random.choice(string.hexdigits) if c == 'x' else random.choice('89ab') if c == 'y' else c for c in deviceid)

def send_msg(sender_uid, receiver_uid, cookies, message):
    """发送私信"""
    url = "https://api.vc.bilibili.com/web_im/v1/web_im/send_msg"
    deviceid = generate_deviceid()
    bili_ticket = get_bili_ticket(cookies.get("bili_jct"))
    cookie_dict = {
        "buvid3": cookies.get("buvid3"),
        "buvid4": cookies.get("buvid4"),
        "SESSDATA": cookies.get("SESSDATA"),
        "bili_jct": cookies.get("bili_jct"),
        "sid": cookies.get("sid"),
        "DedeUserID": cookies.get("DedeUserID"),
        "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
        "bili_ticket": bili_ticket,
    }
    # body参数(application/x-www-form-urlencoded)
    # 将 message 转换为 JSON 字符串
    message_json = json.dumps({"content": message})
    payload = f"msg[sender_uid]={sender_uid}&msg[receiver_id]={receiver_uid}&msg[receiver_type]=1&msg[msg_type]=1&msg[content]={message_json}&msg[dev_id]={deviceid}&csrf={cookies.get('bili_jct')}&msg[timestamp]={int(time.time())}"
    #print(payload)
    response = requests.post(url, cookies=cookie_dict, headers=get_header(), data=payload)
    data = response.json()
    print(f"发送私信{receiver_uid}: 内容为{message}, {data['message']}, code:{data['code']}")
    if data["code"] == 0:
        return data["code"]
    else:
        log_manager.log("send_msg", response.text)
    return data["code"]  # 返回0表示成功

def on_send_msg_clicked(account_table, comment_table, message, spin_delay, spin_operations_per_account, window):
    """开始私信按钮事件"""
    if not message:
        QMessageBox.warning(window, "警告", "请输入私信内容！")
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
    # 获取私信次数切换的数值
    msg_limit = int(spin_operations_per_account)
    # 获取私信/关注操作间隔的数值
    delay_seconds = int(spin_delay)
     # 遍历选中的登录账号
    for account in selected_accounts:
        cookies = load_cookies(account)
        msg_count = 0
        # 遍历评论账号uid
        for uid in uids:
            # 执行关注操作
            result = send_msg(cookies.get("DedeUserID"),uid, cookies, message)
            msg_count += 1
            # 检查是否需要切换账号
            if msg_count >= msg_limit and len(selected_accounts) > 1:
                break
            time.sleep(delay_seconds)
            # 更新关注状态
            if result == 0:
                set_message_status(comment_table, uid, "已私信")
            else:
                set_message_status(comment_table, uid, "私信失败")

        # 更新账号执行状态
        print(f"账号{account}执行完毕")
        set_execution_status(account_table, account, "已执行")
