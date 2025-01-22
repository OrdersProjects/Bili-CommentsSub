import requests
from config import get_header

def get_username(cookies):
    """通过 cookie 请求获取该账号的昵称"""
    cookie_dict = {
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
            return None, False  # 登录失败
    except Exception as e:
        print(f"请求错误：{e}")
        return None, False  # 请求失败
