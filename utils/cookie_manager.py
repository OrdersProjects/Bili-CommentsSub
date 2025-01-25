import os

# 创建保存 cookies 的文件夹
COOKIE_DIR = 'cookies'

# 确保 cookies 文件夹存在
if not os.path.exists(COOKIE_DIR):
    os.makedirs(COOKIE_DIR)

def save_cookies(cookies, dede_user_id):
    """保存 cookies 到对应文件，覆盖已存在的文件"""
    cookie_file_path = os.path.join(COOKIE_DIR, f"{dede_user_id}.txt")

    # 直接覆盖原文件
    with open(cookie_file_path, 'w') as f:
        # 保存 cookies 为文本格式
        for name, value in cookies.items():
            cookie_str = f"{name}={value}"
            f.write(cookie_str + "\n")


def get_all_cookies():
    """获取 cookies 文件夹下所有的文件名列表"""
    # 获取文件夹中的所有文件名
    files = os.listdir(COOKIE_DIR)
    return [file.split('.')[0] for file in files if file.endswith('.txt')]  # 返回文件名（去掉扩展名）即 UID 列表


def load_cookies(dede_user_id):
    """根据DedeUserID加载对应的cookie文件"""
    cookie_file_path = os.path.join(COOKIE_DIR, f"{dede_user_id}.txt")
    cookies = {}

    if os.path.exists(cookie_file_path):
        with open(cookie_file_path, 'r') as f:
            for line in f:
                name, value = line.strip().split('=', 1)
                cookies[name] = value
    return cookies


def delete_cookie(dede_user_id):
    """
    删除指定用户的 cookie 文件。
    """
    cookie_file_path = os.path.join(COOKIE_DIR, f"{dede_user_id}.txt")
    if os.path.exists(cookie_file_path):
        os.remove(cookie_file_path)
        print(f"Cookie 文件已删除: {cookie_file_path}")
    else:
        print(f"未找到 Cookie 文件: {cookie_file_path}")
    

def check_cookie_exists(dede_user_id):
    """检查是否已存在该用户的 cookie"""
    cookie_file_path = os.path.join(COOKIE_DIR, f"{dede_user_id}.txt")
    return os.path.exists(cookie_file_path)
