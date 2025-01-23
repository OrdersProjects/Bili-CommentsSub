import re
import requests

from config import get_header

def get_comments(video_id, page, cookies):

    all_comments = []
    seen_uids = set()

    for page in range(1, page + 1):
        cookie_dict = {
            "DedeUserID": cookies.get("DedeUserID"),
            "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
            "SESSDATA": cookies.get("SESSDATA"),
            "bili_jct": cookies.get("bili_jct"),
            "sid": cookies.get("sid"),
        }

        oid = video_id

        # 调用评论区 API 获取当前页评论数据
        url = f"https://api.bilibili.com/x/v2/reply?oid={oid}&type=1&ps=20&pn={page}&sort=0"
        response = requests.get(url, cookies=cookie_dict, headers=get_header())
        data = response.json()

        if data['code'] != 0 or 'data' not in data:
            break

        replies = data['data'].get('replies', [])

        for idx, reply in enumerate(replies):
            mid = reply['member']['mid']  # 用户 UID
            uname = reply['member']['uname']  # 用户昵称
            sex = reply['member']['sex']  # 性别
            print(f"{mid}: {uname} ({sex})")

            # 如果该用户的 UID 已经在 seen_uids 中，则跳过
            if mid in seen_uids:
                continue

            seen_uids.add(mid)

            all_comments.append((idx + 1, uname, mid, sex))  # 添加到评论列表

    return all_comments


def get_video_comment_count(video_id, cookies):
    """获取视频的评论总数"""
    cookie_dict = {
        "DedeUserID": cookies.get("DedeUserID"),
        "DedeUserID__ckMd5": cookies.get("DedeUserID__ckMd5"),
        "SESSDATA": cookies.get("SESSDATA"),
        "bili_jct": cookies.get("bili_jct"),
        "sid": cookies.get("sid"),
    }


    oid = video_id

    # 调用评论区 API 获取评论总数
    url = f"https://api.bilibili.com/x/v2/reply/count?oid={oid}&type=1"
    print(url)
    response = requests.get(url, cookies=cookie_dict, headers=get_header())
    data = response.json()

    if data['code'] != 0 or 'data' not in data:
        return 0

    # 获取评论总数
    all_count = data['data'].get('count', 0)
    print(f"数量: {data['data'].get('count', 0)}")
    return all_count


def calculate_total_pages(comment_count):
    """根据评论总数计算需要多少页"""
    return (comment_count // 20) + (1 if comment_count % 20 != 0 else 0)



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
