from PyQt5.QtWidgets import (
    QTableWidgetItem, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt

from render.event.accountTable import get_selected_accounts
from utils.cookie_manager import load_cookies
from utils.getUserInfo import get_gender
from config import get_header
from auth.bili_ticket import get_bili_ticket
import requests
import json

def on_collect_fans_clicked(input_uid, comment_table, account_table):
    """粉丝采集按钮点击事件"""
    uid = input_uid
    if not uid:
        QMessageBox.warning(None, "警告", "请输入要爬取的用户UID")
        return
    # 获取选中的账号
    selected_accounts = get_selected_accounts(account_table)
    if not selected_accounts:
        QMessageBox.warning(None, "警告", "请先选择要操作的账号")
        return
    # 爬取粉丝列表
    url = f"https://api.bilibili.com/x/relation/followers"
    # 获取第一个用来爬取的cookie，若该cookie失效，则尝试下一个直到成功爬取到列表
    for account in selected_accounts:
        cookies = load_cookies(account)
        if not cookies:
            continue
        bili_ticket = get_bili_ticket(cookies.get("bili_jct"))
        cookie_dict = {
            "DedeUserID": cookies.get("DedeUserID"),
            "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
            "SESSDATA": cookies.get("SESSDATA"),
            "bili_jct": cookies.get("bili_jct"),
            "sid": cookies.get("sid"),
            "bili_ticket": bili_ticket
        }
        params = {
            "vmid": uid,
            "pn": 1,  # 页码，从1开始
            "ps": 50  # 每页数量
        }
        while True:
            try:
                response = requests.get(url, params=params, cookies=cookie_dict, headers=get_header())
                response.raise_for_status()  # 检查请求是否成功
                data = response.json()  # 尝试解析JSON
                if data["code"] == 0:
                    # 遍历粉丝列表
                    for item in data["data"]["list"]:
                        # 获取粉丝信息
                        mid = item.get("mid")
                        uname = item.get("uname")
                        sex = get_gender(mid)
                        # 将粉丝信息添加到表格中
                        row = comment_table.rowCount()
                        comment_table.insertRow(row)
                        checkbox_item = QTableWidgetItem()
                        checkbox_item.setCheckState(Qt.Unchecked)  # 默认不选中
                        comment_table.setItem(row, 0, checkbox_item)  # 第 0 列为复选框
                        comment_table.setItem(row, 1, QTableWidgetItem(uname))
                        comment_table.setItem(row, 2, QTableWidgetItem(str(mid)))
                        comment_table.setItem(row, 3, QTableWidgetItem(sex))
                    # 检查是否还有下一页数据
                    if len(data["data"]["list"]) < params["ps"]:
                        break  # 没有更多数据，退出循环
                    else:
                        params["pn"] += 1  # 增加页码
                else:
                    QMessageBox.warning(None, "错误", f"请求失败，错误代码: {data['code']}")
                    break
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(None, "错误", f"请求失败: {e}")
                print(e)
                break
            # 修复缩进问题
            except json.JSONDecodeError as e:
                QMessageBox.warning(None, "错误", f"解析JSON失败: {e}")
                break
