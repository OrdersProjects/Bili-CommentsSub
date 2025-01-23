def get_all_uids(comment_table):
    """获取采集列表里的所有 uid"""
    uids = []
    for row in range(comment_table.rowCount()):
        uid_item = comment_table.item(row, 2)  # 获取 UID 所在列（第 2 列）
        if uid_item:
            uids.append(uid_item.text())  # 获取 UID
    return uids


def set_follow_status(comment_table, uids):
    """根据传入的 uid 列表设置关注状态为已关注"""
    for row in range(comment_table.rowCount()):
        uid_item = comment_table.item(row, 2)  # 获取 UID 所在列（第 2 列）
        if uid_item and uid_item.text() in uids:
            follow_result_item = comment_table.item(row, 4)  # 获取关注结果列（第 4 列）
            if follow_result_item:
                follow_result_item.setText("已关注")  # 设置关注状态为 "已关注"


def set_message_status(comment_table, uids):
    """根据传入的 uid 列表设置私信状态为已私信"""
    for row in range(comment_table.rowCount()):
        uid_item = comment_table.item(row, 2)  # 获取 UID 所在列（第 2 列）
        if uid_item and uid_item.text() in uids:
            message_result_item = comment_table.item(row, 5)  # 获取私信结果列（第 5 列）
            if message_result_item:
                message_result_item.setText("已私信")  # 设置私信状态为 "已私信"