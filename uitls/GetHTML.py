import logging
import requests

from uitls.proxy import get_proxy


def download_page(url):
    try:
        response = requests.get(url, proxies=get_proxy())
        if response.status_code < 300:
            logging.debug("get page from:" + url + " succeeded with http code:" + str(response.status_code))
            return response.text
        else:
            logging.error("get page from:" + url + " failed with http code:" + str(response.status_code))
            logging.error(f"failed request headers: {response['headers']}")
            logging.error(f"failed request body: {response['text']}")
            return None
    except requests.exceptions.RequestException as e:
        # 处理请求异常
        logging.error(f"请求出现异常：{e}")
    except Exception as e:
        # 处理其他异常
        logging.error(f"发生未知异常：{e}")
