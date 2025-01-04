import requests
from bs4 import BeautifulSoup


# 解析所有rule34_url中的视频页面的链接
def parse_rule34_video_page_links(rule34_url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    headers = {'User-Agent': user_agent}
    response = requests.get(rule34_url, headers=headers)
    parsed_video_links = []
    soup = BeautifulSoup(response.text, 'html.parser')

    # get video page url
    elements = soup.find_all('a', class_="th js-open-popup")

    for element in elements:
        video_page_url = element.get('href')
        parsed_video_links.append(video_page_url)
    return parsed_video_links
