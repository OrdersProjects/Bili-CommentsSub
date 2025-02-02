import re
import csv
from PyQt5.QtWidgets import (
    QTableWidgetItem, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt

from render.event.accountTable import get_selected_accounts
from utils.cookie_manager import load_cookies
from utils.getVideoInfo import calculate_total_pages, extract_video_id, get_comments, get_video_comment_count


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
    added_uids = set()  # 记录已经添加到表格中的 uid

    # 循环遍历选中的账号，获取评论
    for uid in selected_accounts:
        cookies = load_cookies(uid)

        if not cookies:
            print(f"无法加载 {uid} 的 cookie")
            failed_accounts.append(uid)
            continue  # 切换到下一个账号

        try:
            # 获取视频的评论总数
            comment_count = get_video_comment_count(video_id, cookies)
            if comment_count == 0:
                print(f"{uid} 无法获取评论总数")
                failed_accounts.append(uid)
                continue  # 切换到下一个账号

            # 根据评论总数计算总页数
            total_pages = calculate_total_pages(comment_count)

            # 获取评论数据
            comments = get_comments(video_id, total_pages, cookies)
            if not comments:
                print(f"{uid} 无法获取评论数据")
                failed_accounts.append(uid)
                continue  # 切换到下一个账号

            # 过滤已添加的 uid，避免重复
            new_comments = []
            for comment in comments:
                if comment[2] not in added_uids:  # comment[2] 是 uid
                    new_comments.append(comment)
                    added_uids.add(comment[2])

            all_comments.extend(new_comments)

        except Exception as e:
            print(f"{uid} 获取评论数据时发生异常：{e}")
            failed_accounts.append(uid)
            continue  # 切换到下一个账号

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


def on_select_all_comments_clicked(comment_table):
    """全选按钮点击事件"""
    for row in range(comment_table.rowCount()):
        checkbox_item = comment_table.item(row, 0)  # 获取复选框所在的列（第0列）
        checkbox_item.setCheckState(Qt.Checked)  # 设置为选中状态


def on_clear_comments_clicked(comment_table):
    """清空列表按钮点击事件"""
    comment_table.setRowCount(0)  # 清空表格中的所有行


def on_export_comments_clicked(comment_table):
    """导出表格按钮点击事件"""
    # 获取表格的数据
    rows = []
    for row in range(comment_table.rowCount()):
        row_data = []
        for col in range(comment_table.columnCount()):
            item = comment_table.item(row, col)
            if item is not None:
                row_data.append(item.text())
            else:
                row_data.append("")  # 如果单元格为空，加入空字符串
        rows.append(row_data)
    
    # 保存为 CSV 文件
    filename, _ = QFileDialog.getSaveFileName(None, "保存为 CSV", "", "CSV Files (*.csv)")
    if filename:
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(rows)  # 写入表格数据

#取消全选按钮点击事件
def on_deselect_all_comments_clicked(comment_table):
    """
    取消全选评论区数据表格中的所有行
    :param comment_table: 评论区数据表格
    """
    for row in range(comment_table.rowCount()):
        comment_table.item(row, 0).setCheckState(Qt.Unchecked)

# 只选择男性
def on_select_male_comments_clicked(comment_table):
    """
    只选择评论区数据表格中的男性行
    :param comment_table: 评论区数据表格
    """
    for row in range(comment_table.rowCount()):
        gender_item = comment_table.item(row, 3)
        if gender_item and gender_item.text() == "男":
            comment_table.item(row, 0).setCheckState(Qt.Checked)
        else:
            comment_table.item(row, 0).setCheckState(Qt.Unchecked)

#只选择女性
def on_select_female_comments_clicked(comment_table):
    """
    只选择评论区数据表格中的女性行
    :param comment_table: 评论区数据表格
    """
    for row in range(comment_table.rowCount()):
        gender_item = comment_table.item(row, 3)
        if gender_item and gender_item.text() == "女":
            comment_table.item(row, 0).setCheckState(Qt.Checked)
        else:
            comment_table.item(row, 0).setCheckState(Qt.Unchecked)


def on_clear_followed_comments_clicked(comment_table):
    """清除已关注的评论区数据"""
    rows_to_remove = []
    
    for row in range(comment_table.rowCount()):
        follow_status_item = comment_table.item(row, 4)  # 获取关注状态（第五列）
        if follow_status_item and follow_status_item.text() == "已关注":
            rows_to_remove.append(row)  # 记录要删除的行
    
    # 删除记录的行，从最后一行开始删除，避免删除时改变了行的索引
    for row in reversed(rows_to_remove):
        comment_table.removeRow(row)


def on_clear_sent_messages_clicked(comment_table):
    """清除已私信的评论区数据"""
    rows_to_remove = []
    
    for row in range(comment_table.rowCount()):
        msg_status_item = comment_table.item(row, 5)  # 获取私信状态（第六列）
        if msg_status_item and msg_status_item.text() == "已私信":
            rows_to_remove.append(row)  # 记录要删除的行
    
    # 删除记录的行，从最后一行开始删除，避免删除时改变了行的索引
    for row in reversed(rows_to_remove):
        comment_table.removeRow(row)
