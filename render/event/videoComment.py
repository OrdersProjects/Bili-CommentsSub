import re
from PyQt5.QtWidgets import (
    QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt

from render.event.accountTable import get_selected_accounts
from utils.cookie_manager import load_cookies
from utils.getVideoInfo import calculate_total_pages, get_comments, get_video_comment_count


def on_collect_comments_clicked(input_url, comment_table, account_table):
    """采集按钮点击事件"""
    video_id = extract_video_id(input_url)

    if not video_id:
        print("无法提取视频 ID，请检查链接格式")
        return

    print(f"提取到的视频 ID：{video_id}")
    
    # 获取选中的账号
    selected_accounts = get_selected_accounts(account_table)
    if not selected_accounts:
        QMessageBox.warning(None, "警告", "请先选择要操作的账号")
        return

    all_comments = []
    failed_accounts = []

    # 循环遍历选中的账号，获取评论
    for uid in selected_accounts:
        cookies = load_cookies(uid)
        
        if not cookies:
            print(f"无法加载 {uid} 的 cookie")
            failed_accounts.append(uid)
            continue

        # 获取视频的评论总数
        comment_count = get_video_comment_count(video_id, cookies)
        if comment_count == 0:
            failed_accounts.append(uid)
            continue

        # 根据评论总数计算总页数
        total_pages = calculate_total_pages(comment_count)

        # 获取评论数据
        comments = get_comments(video_id, total_pages, cookies)
        if not comments:
            failed_accounts.append(uid)
            continue

        all_comments.extend(comments)

    if failed_accounts:
        QMessageBox.warning(None, "警告", f"无法获取以下账号的评论数据：{', '.join(failed_accounts)}")

    # 更新表格
    comment_table.setRowCount(len(all_comments))
    for row, (index, uname, uid, sex) in enumerate(all_comments):
        # 创建复选框并添加到表格的第一列
        checkbox_item = QTableWidgetItem()
        checkbox_item.setCheckState(Qt.Unchecked)  # 默认不选中
        comment_table.setItem(row, 0, checkbox_item)  # 第 0 列为复选框

        comment_table.setItem(row, 1, QTableWidgetItem(uname))  # 昵称
        comment_table.setItem(row, 2, QTableWidgetItem(uid))  # UID
        comment_table.setItem(row, 3, QTableWidgetItem(sex))  # 性别

def extract_video_id(url):
    """提取 BV 号或 AV 号"""
    bv_pattern = re.compile(r'BV([a-zA-Z0-9]+)')
    av_pattern = re.compile(r'av(\d+)')

    bv_match = bv_pattern.search(url)
    av_match = av_pattern.search(url)

    if bv_match:
        return 'BV' + bv_match.group(1)
    elif av_match:
        return 'av' + av_match.group(1)
    else:
        return None
