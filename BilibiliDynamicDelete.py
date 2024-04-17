# https://github.com/sakurasvip2023/Bilibili-Dynamic-Delete
import json
import requests
import time

# 全局变量
COOKIE_STRING = ""  # 你的 cookie 字符串

QuantityToBeDeleted = 100  # 需要删除的动态数量

def get_cookies(COOKIE_STRING):
    """解析 cookie 字符串，返回 cookies 字典"""
    cookies = {}
    for cookie in COOKIE_STRING.split('; '):
        if '=' in cookie:
            key, value = cookie.split('=', 1)
            cookies[key.strip()] = value.strip()
    return cookies

def get_csrf_and_uid(cookies):
    """从 cookies 中获取 CSRF 和 UID"""
    csrf = cookies.get('bili_jct')
    uid = cookies.get('DedeUserID')
    return csrf, uid

def get_headers(uid):
    """构造请求头"""
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "content-type": "application/json;charset=UTF-8",
        "cookie": COOKIE_STRING,
        "origin": "https://space.bilibili.com",
        "referer": f"https://space.bilibili.com/{uid}/dynamic",
        "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }
    return headers

def fetch_dynamic_data(headers, uid,cookies):
    """获取动态数据"""
    url = f'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?offset=&host_mid={uid}&timezone_offset=-480'
    response = requests.get(url, headers=headers, cookies=cookies)
    return response

def delete_dynamic(comment_id_str, csrf, cookies,headers):
    """删除动态"""
    data = {"dyn_id_str": comment_id_str}
    url = f"https://api.bilibili.com/x/dynamic/feed/operate/remove?platform=web&csrf={csrf}"
    response = requests.post(url, headers=headers, data=json.dumps(data), cookies=cookies)
    return response

def main():
    # 解析 cookies
    cookies = get_cookies(COOKIE_STRING)
    if not cookies:
        print("无法解析 cookie 字符串。请检查 COOKIE 是否正确。")
        return

    # 获取 CSRF 和 UID
    csrf, uid = get_csrf_and_uid(cookies)

    # 构造请求头
    headers = get_headers(uid)

    # 初始化已删除动态计数器
    DeleteQuantity = 0

    index = 0  # 初始偏移量

    # 循环直到达到删除数量上限
    while DeleteQuantity < QuantityToBeDeleted:
        # 获取动态数据
        response = fetch_dynamic_data(headers, uid,cookies)

        # 检查响应状态码
        if response.status_code != 200:
            print(f"请求失败，状态码为 {response.status_code}")
            break

        try:
            data = response.json()
        except json.decoder.JSONDecodeError as e:
            print("响应内容无法解析为 JSON 格式")
            print(e)
            break
        print(data)
        # 检查返回的数据是否正常
        if data.get("code") != 0:
            print("获取动态失败")
            break

        # 提取动态数据并逐条删除
        items = data["data"]["items"]
        for item in items:
            comment_id_str = item["basic"]["comment_id_str"]
            response = delete_dynamic(comment_id_str, csrf, cookies,headers)
            print(f"正在删除第 {DeleteQuantity + 1} 条动态:{response.text} ")
            DeleteQuantity += 1
            if DeleteQuantity >= QuantityToBeDeleted:
                break

        # 更新偏移量
        index += len(items)

        # 添加延迟，防止请求过于频繁
        time.sleep(1)

if __name__ == "__main__":
    main()
