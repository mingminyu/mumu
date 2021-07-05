# coding: utf-8
# ================================================
# Project: mumu
# File: robots/_workwx.py
# Author: Mingmin Yu
# Email: yu_ming623@163.com
# Date: 2021/6/23 17:43
# Description:
# ================================================
import requests
import json
import logging
import base64
import hashlib
from mumu.utils import str_to_list


prefix_api = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=%s"
upload_api = "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=%s&type=file"
# multipart/form-data;
headers = {
    "Content-Type": "application/json;text/plain;charset=UTF-8",
    "Accept": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/79.0.3945.79 Safari/537.36 "
    }


def send_messages(key=None, content=None, at_all=False, mentioned_mobile_list=None):
    """Send messages in text format.

    :param key:str, private key for Work WeChat robot
    :param content: str, text messages will be sent.
    :param at_all: bool, default False, robot will @all when set `True`
    :param mentioned_mobile_list: use mobile list to remind some members.
    :return: bool
        True for success, False for fail.
    """
    web_hook = prefix_api % key
    preload = {
        "msgtype": "text",
        "text": {
            "mentioned_mobile_list": str_to_list(mentioned_mobile_list) if not at_all else ["@all"],
            "content": content
            }
        }
    print(preload)
    res = requests.post(web_hook, json=preload, headers=headers, verify=False)

    if json.loads(res.text)["errmsg"] == "ok":
        logging.info("successful")
        return True
    else:
        logging.info("failed")
        return False


def send_messages_md(key=None, content=None):
    """Send messages in markdown format.

    :param key: str, private key for Work WeChat robot
    :param content: str, markdown messages will be sent.
    :return: bool
        True for success, False for fail.
    """
    web_hook = prefix_api % key
    preload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
            }
        }

    res = requests.post(web_hook, json=preload, headers=headers, verify=False)

    if json.loads(res.text)["errmsg"] == "ok":
        logging.info("successful")
        return True
    else:
        logging.info("failed")


def send_image(key=None, image=None):
    """Send an image

    :param key: str, key for Work WeChat robot
    :param image: str, absolute path of an image
    :return: bool
        True for success, False for fail.
    """
    with open(image, "rb") as img:
        base64_ = str(base64.b64encode(img.read()), encoding='utf-8')

    with open(image, "rb") as img:
        md = hashlib.md5()
        md.update(img.read())
        md5_ = md.hexdigest()

    web_hook = prefix_api % key
    preload = {
        "msgtype": "image",
        "image": {
            "base64": base64_,
            "md5": md5_,
            }
        }

    headers = {"Content-Type": "application/json"}

    res = requests.post(web_hook, json=preload, headers=headers, verify=False)

    if json.loads(res.text)["errmsg"] == "ok":
        logging.info("successful")
        return True
    else:
        logging.info("failed")
        return False


def send_images(key=None, images=None):
    """Send images

    :param key: str
    :param images: list, absolute path of images
    :return: bool
        True for success, False for fail.
    """
    for img in images:
        send_image(key=key, image=img)


def send_news(key=None, articles=None):
    """Send news with links

    :param key: str, key for Work WeChat robot
    :param articles: list, a list contains json articles
    :return: bool
        True for success, False for fail.
    """
    web_hook = prefix_api % key
    preload = {
        "msgtype": "news",
        "news": {
            "articles": articles
        }
    }

    res = requests.post(web_hook, json=preload, headers=headers, verify=False)

    if json.loads(res.text)["errmsg"] == "ok":
        logging.info("successful")
        return True
    else:
        logging.info("failed")
        return False


def send_file(key=None, file=None):
    """Send a file

    :param key: str, key for Work WeChat robot
    :param file: str, file absolute path
    :return: bool
        True for success, False for fail.
    """
    web_hook = prefix_api % key
    media_id = _upload_file(key=key, file=file)
    preload = {
        "msgtype": "file",
        "file": {
            "media_id": media_id
            }
        }
    res = requests.post(web_hook, json=preload)

    if json.loads(res.text)["errmsg"] == "ok":
        logging.info("successful")
        return True
    else:
        logging.info("failed")
        return False


def _upload_file(key=None, file=None):
    """Upload

    :param key: str, key for Work WeChat robot
    :param file: str, file absolute path
    :return: str,
        return media id of the file when upload successfully.
    """
    upload_hook = upload_api % key

    with open(file, "rb") as fp:
        data = {"file": fp}
        res = requests.post(upload_hook, files=data)
        media_id = res.json()["media_id"]

        return media_id
