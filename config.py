import random

def get_header():
    """返回一个带有随机 User-Agent 的请求头"""
    
    # 随机选择操作系统
    os_list = [
        'Windows NT 10.0; Win64; x64',
        'Windows NT 6.1; WOW64',
        'Macintosh; Intel Mac OS X 10_15_7',
        'X11; Linux x86_64',
        'Android 10; Mobile; rv:91.0',
    ]
    os = random.choice(os_list)

    # 随机选择浏览器及版本号
    browsers = [
        ('Chrome', random.randint(85, 91)),
        ('Firefox', random.randint(85, 92)),
        ('Safari', random.randint(13, 15)),
        ('Edge', random.randint(91, 95)),
    ]
    browser, version = random.choice(browsers)

    # 生成随机的 User-Agent
    user_agent = f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}/{version}.0 Safari/537.36"

    return {
        'User-Agent': user_agent,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
