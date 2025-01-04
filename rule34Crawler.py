import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from uitls.FileUtils import replace_illegal_chars
from uitls.FileUtils import redlines

from uitls.Log import set_console_log
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# video_url example: https://rule34video.com/videos/3138647/genshin-girls-music-part-2/
def download_rule34video(video_url, local_video_path):
    legal_filename = None
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # 后台初始化一个 Chrome 浏览器实例
    driver = webdriver.Chrome(options=chrome_options)
    # 打开某个网页
    driver.get(video_url)
    # 等待页面加载完全
    button_continue = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//*[@name="continue"]')))
    button_continue.click()

    labels = driver.find_elements(By.CLASS_NAME, 'label')
    for label in labels:
        if label.text == 'Download:':
            first_href = label.parent.find_element(By.CLASS_NAME, 'tag_item')
            video_download_href = first_href.get_property('href')
            # 获取页面的用户代理
            user_agent = driver.execute_script('return navigator.userAgent')
            headers = {'User-Agent': user_agent}
            # 获取页面的cookie
            cookies_list = driver.get_cookies()
            cookies_dict = {}
            for cookie in cookies_list:
                cookies_dict[cookie['name']] = cookie['value']
            # 下载文件
            response = requests.get(video_download_href, headers=headers, cookies=cookies_dict)
            today_path = local_video_path + '/' + datetime.now().strftime('%Y-%m-%d')
            # 使用os模块的makedirs函数创建文件夹
            os.makedirs(today_path, exist_ok=True)
            legal_filename = replace_illegal_chars(driver.title + '.mp4')
            chunk_size = 102400  # 每个块的大小
            with open(f"{today_path}/{legal_filename}", "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    # 写入每个块的内容
                    f.write(chunk)

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
        with open(ok_url_file, 'a') as f:
            # 写入url+换行符
            f.write(f'{video_url}\n')
            if legal_filename:
                f.write(f'{legal_filename}\n')


ok_urls = None
retry_urls = None
failed_urls = None


def parse_rule34video_links(rule34_root, local_video_path):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    headers = {'User-Agent': user_agent}
    response = requests.get(rule34_root, headers=headers)
    global ok_urls
    global retry_urls
    global failed_urls
    ok_urls = redlines(ok_url_file)
    retry_urls = redlines(retry_url_file)
    failed_urls = redlines(failed_url_file)
    soup = BeautifulSoup(response.text, 'html.parser')

    # get video page url
    elements = soup.find_all('a', class_="th js-open-popup")

    with ThreadPoolExecutor(max_workers=5) as executor:
        if retry_urls:
            for retry_url in retry_urls:
                executor.submit(download_rule34video_with_retry, retry_url, local_video_path)
        for element in elements:
            video_page_url = element.get('href')
            if ok_urls and video_page_url not in ok_urls:
                executor.submit(download_rule34video_with_retry, video_page_url, local_video_path)


def main():
    set_console_log()
    parse_rule34video_links('https://rule34video.com/', r'D:\P\Video\Rule34')


if __name__ == "__main__":
    main()
