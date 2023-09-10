from bs4 import BeautifulSoup as bs

#
# def download_brob_url(html):
#     soup = bs(html, 'html.parser')
#     # 查找包含Blob URL的标签，例如<a>标签
#     a_tags = soup.find_all('a')
#
#     # 遍历<a>标签，查找Blob URL并下载文件
#     for a_tag in a_tags:
#         href = a_tag.get('href')
#         if href.startswith('blob:'):
#             # 构建Blob URL的完整路径
#             blob_url = url + href
#             # 发送HTTP请求，获取Blob文件内容
#             blob_response = requests.get(blob_url)
#             # 将Blob文件保存到本地
#             with open('file.txt', 'wb') as f:
#                 f.write(blob_response.content)
