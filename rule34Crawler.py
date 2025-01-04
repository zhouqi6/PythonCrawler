import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from Parsers.parse_rule34_video_links import parse_rule34_video_page_links
from uitls.FileUtils import replace_illegal_chars
from uitls.FileUtils import redlines

from uitls.Log import set_loggers
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 根据正则表达式筛选tag_item中的视频链接
# tag_item示例：<a class="tag_item" href="https://rule34video.com/get_file/47/" data-attach-session="PHPSESSID">MP4 1080p</a>
def get_video_download_url_from_tag_item(tag_item):
    href = tag_item.get_property('href')
    if href is not None and href.startswith('https://rule34video.com/get_file'):
        return href
    else:
        return None


# video_url example: https://rule34video.com/videos/3138647/genshin-girls-music-part-2/
def download_rule34video(video_url, local_video_path):
    legal_filename = None
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # 后台初始化一个 Chrome 浏览器实例
    driver = webdriver.Chrome(options=chrome_options)
    # 打开某个网页
    driver.get(video_url)
    # 等待页面加载完全后，获取继续按钮（确认满18）
    button_continue = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@name="continue"]')))
    button_continue.click()

    download_div_label = 'Download'
    # 找到所有的tag_item
    tag_items = driver.find_elements(By.CLASS_NAME, 'tag_item')
    found_download_label = False
    for tag_item in tag_items:
        video_download_url = get_video_download_url_from_tag_item(tag_item)
        if video_download_url is not None:
            # 获取页面的用户代理
            user_agent = driver.execute_script('return navigator.userAgent')
            headers = {'User-Agent': user_agent}
            # 获取页面的cookie
            cookies_list = driver.get_cookies()
            cookies_dict = {}
            for cookie in cookies_list:
                cookies_dict[cookie['name']] = cookie['value']
            # 下载文件
            response = requests.get(video_download_url, headers=headers, cookies=cookies_dict)
            today_path = local_video_path + '/' + datetime.now().strftime('%Y-%m-%d')
            # 使用os模块的makedirs函数创建文件夹
            os.makedirs(today_path, exist_ok=True)
            legal_filename = replace_illegal_chars(driver.title + '.mp4')
            chunk_size = 102400  # 每个块的大小
            with open(f"{today_path}/{legal_filename}", "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    # 写入每个块的内容
                    f.write(chunk)
            found_download_label = True
            # 当前第一个是最高清晰度，只下载第一个，后续是否需要优化逻辑
            break

    if not found_download_label:
        raise ValueError(f'video download url not found in url:{video_url}')

    # 关闭浏览器实例
    driver.quit()
    return legal_filename


ok_url_file = 'ok urls.txt'
failed_url_file = 'failed urls.txt'
retry_url_file = 'retry urls.txt'


def download_rule34video_with_retry(video_url, local_video_path):
    need_retry = True
    retry_time = 0
    max_retry_limit = 5
    legal_filename = None
    while need_retry and retry_time < max_retry_limit:
        try:
            need_retry = False
            legal_filename = download_rule34video(video_url, local_video_path)
        except Exception as e:
            retry_time += 1
            need_retry = True
            logging.warning(f'download_rule34video failed, retry time:{retry_time}')
            logging.warning(e)

    if need_retry:
        with open(failed_url_file, 'a') as f:
            # 写入url+换行符
            f.write(f'{video_url}\n')
            if legal_filename:
                f.write(f'{legal_filename}\n')
    else:
        # 先不记录成功结果，调试中
        with open(ok_url_file, 'a') as f:
            # 写入url+换行符
            f.write(f'{video_url}\n')
            if legal_filename:
                f.write(f'{legal_filename}\n')


ok_urls = None
retry_urls = None
failed_urls = None


# 解析所有rule34_url中的视频页面的链接，并且下载他们的视频（跳过成功的项），重试下载失败的链接
def try_download_video_links(rule34_root, local_video_path):
    parsed_video_links = parse_rule34_video_page_links(rule34_root)
    global ok_urls
    global retry_urls
    global failed_urls
    ok_urls = redlines(ok_url_file)
    retry_urls = redlines(retry_url_file)
    failed_urls = redlines(failed_url_file)

    with ThreadPoolExecutor(max_workers=32) as executor:
        if retry_urls:
            for retry_url in retry_urls:
                executor.submit(download_rule34video_with_retry, retry_url, local_video_path)
        for video_page_url in parsed_video_links:
            if video_page_url not in ok_urls:
                executor.submit(download_rule34video_with_retry, video_page_url, local_video_path)


def main():
    set_loggers()
    try_download_video_links('https://rule34video.com/', r'D:\P\Video\Rule34')


if __name__ == "__main__":
    main()
