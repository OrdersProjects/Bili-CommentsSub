import requests
from config import get_header
from utils.log_manager import LogManager
log_manager = LogManager()

def get_username(cookies):
    """通过 cookie 请求获取该账号的昵称"""
    cookie_dict = {
        "buvid3": cookies.get("buvid3"),
        "buvid4": cookies.get("buvid4"),
        "DedeUserID": cookies.get("DedeUserID"),
        "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
        "SESSDATA": cookies.get("SESSDATA"),
        "bili_jct": cookies.get("bili_jct"),
        "sid": cookies.get("sid"),
    }

    try:
        response = requests.get("https://api.bilibili.com/x/web-interface/nav", cookies=cookie_dict, headers=get_header())
        result = response.json()
        if result["code"] == 0:
            uname = result["data"]["uname"]
            return uname, True  # 返回昵称和登录状态
        else:
            log_manager.log("get_username", response.text)
            return None, False  # 登录失败
    except Exception as e:
        print(f"请求错误：{e}")
        return None, False  # 请求失败


#通过UID获取用户性别
def get_gender(uid):
    """通过 UID 请求获取该账号的性别"""
    try:
        response = requests.get(f"https://api.bilibili.com/x/web-interface/card?mid={uid}", headers=get_header())
        result = response.json()
        if result["code"] == 0:
            gender = result["data"]["card"]["sex"]
            return gender
        else:
            log_manager.log("get_gender", response.text)
            return "失败"
    except Exception as e:
        print(f"请求错误：{e}")
        return "失败"