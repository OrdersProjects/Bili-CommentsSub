def get_header(space=False):
    """返回一个带有固定 User-Agent 的请求头，Referer 根据传入的参数决定"""

    # 固定 User-Agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"

    # 根据传入的 is_bilibili_com 参数设置 Referer
    referer = 'https://space.bilibili.com/' if space else 'https://www.bilibili.com/'

    return {
        'User-Agent': user_agent,
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'referer': referer
    }
