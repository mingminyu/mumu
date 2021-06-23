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


class WorkWeChatRobot(object):
    def __init__(self, key=None, mentioned_mobile_list=None, at_all=False):
        """

        :param key:
        :param msgtype: text / markdown
        :param mentioned_list: list
        :param mentioned_mobile_list: list
        """
        prefix_api = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="
        upload_api = "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=%s&type=file"
        self.web_hook = prefix_api + key
        self.upload_hook = upload_api % key
        self.mentioned_mobile_list = mentioned_mobile_list
        self.at_all = at_all
        self.headers = {
            "Content-Type": "multipart/form-data;text/plain;application/json;charset=UTF-8",
            "Accept": "application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/79.0.3945.79 Safari/537.36 "
            }

    def _preload(self, msgtype=None, content=None, base64_=None, md5_=None, media_id=None):
        """preload send messages context"""
        preload = {"msgtype": msgtype}

        if msgtype == "text":
            preload[msgtype] = {
                "mentioned_mobile_list": str_to_list(self.mentioned_mobile_list) if not self.at_all else ["@all"],
                "content": content
                }
        elif msgtype == "markdown":
            preload[msgtype] = {
                "content": content
                }
        elif msgtype == "image":
            preload[msgtype] = {
                "base64": base64_,
                "md5": md5_
                }
        elif msgtype == "news":
            preload[msgtype] = {
                "articles": content
                }
        elif msgtype == "file":
            preload[msgtype] = {
                "media_id": media_id
                }
        else:
            preload = {}

        return preload

    def send_messages(self, content=None):
        preload = self._preload(msgtype="text", content=content)
        res = requests.post(self.web_hook, json=preload, headers=self.headers, verify=False)

        if json.loads(res.text)["errmsg"] == "ok":
            logging.info("successful")
        else:
            logging.info("failed")

    def send_messages_md(self, content=None):
        """

        :param content:
        :return:
        """
        preload = self._preload(msgtype="markdown", content=content)
        res = requests.post(self.web_hook, json=preload, headers=self.headers, verify=False)

        if json.loads(res.text)["errmsg"] == "ok":
            logging.info("successful")
        else:
            logging.info("failed")

    def send_image(self, image_path=None):
        """Send an image

        :param image_path: str, absolute path of an image
        :return:
        """
        with open(image_path, "rb") as img:
            base64_ = base64.b64encode(img.read())

        with open(image_path, "rb") as img:
            md = hashlib.md5()
            md.update(img.read())
            md5_ = md.hexdigest()

        preload = self._preload(msgtype="image", base64_=base64_, md5_=md5_)
        res = requests.post(self.web_hook, json=preload, headers=self.headers, verify=False)

        if json.loads(res.text)["errmsg"] == "ok":
            logging.info("successful")
        else:
            logging.info("failed")

    def send_images(self, images_path=None):
        """

        :param images_path: list, absolute path of images
        :return:
        """
        for img in images_path:
            self.send_image(img)

    def send_article(self, content=None):
        preload = self._preload(msgtype="news", content=content)
        res = requests.post(self.web_hook, json=preload, headers=self.headers, verify=False)

        if json.loads(res.text)["errmsg"] == "ok":
            logging.info("successful")
        else:
            logging.info("failed")

    def send_file(self, file):
        media_id = self._upload_file(file)
        preload = self._preload(msgtype="file", media_id=media_id)
        res = requests.post(self.web_hook, json=preload)

        if json.loads(res.text)["errmsg"] == "ok":
            logging.info("successful")
        else:
            logging.info("failed")

    def _upload_file(self, file):
        with open(file, "rb") as f:
            data = {"file": f}
            res = requests.post(self.upload_hook, files=data)
            media_id = res.json()["media_id"]

            return media_id


prefix_api = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=%s"
upload_api = "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=%s&type=file"
headers = {
    "Content-Type": "multipart/form-data;text/plain;application/json;charset=UTF-8",
    "Accept": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/79.0.3945.79 Safari/537.36 "
    }


def send_messages(key=None, content=None, at_all=False, mentioned_mobile_list=None):
    web_hook = prefix_api % key
    preload = {
        "msgtype": "text",
        "text": {
            "mentioned_mobile_list": str_to_list(mentioned_mobile_list) if not at_all else ["@all"],
            "content": content
            }
        }
    res = requests.post(web_hook, json=preload, headers=headers, verify=False)

    if json.loads(res.text)["errmsg"] == "ok":
        logging.info("successful")
    else:
        logging.info("failed")


def send_messages_md(key=None, content=None):
    """

    :param key:
    :param content:
    :return:
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
    else:
        logging.info("failed")


def send_image(key=None, image=None):
    """Send an image

    :param key: str,
    :param image: str, absolute path of an image
    :return:
    """
    with open(image, "rb") as img:
        base64_ = base64.b64encode(img.read())

    with open(image, "rb") as img:
        md = hashlib.md5()
        md.update(img.read())
        md5_ = md.hexdigest()

    web_hook = prefix_api % key
    preload = {
        "msgtype": "image",
        "image": {
            "base64": base64_,
            "md5": md5_
            }
        }

    res = requests.post(web_hook, json=preload, headers=headers, verify=False)

    if json.loads(res.text)["errmsg"] == "ok":
        logging.info("successful")
    else:
        logging.info("failed")


def send_images(key=None, images=None):
    """Send images

    :param key: str
    :param images: list, absolute path of images
    :return:
    """
    for img in images:
        send_image(key=key, image=img)


def send_news(key=None, articles=None):
    web_hook = prefix_api % key
    preload = {
        "msgtype": "news",
        "news": {
            "artcles": articles
        }
    }

    res = requests.post(web_hook, json=preload, headers=headers, verify=False)

    if json.loads(res.text)["errmsg"] == "ok":
        logging.info("successful")
    else:
        logging.info("failed")


def send_file(key=None, file=None):
    web_hook = prefix_api % key
    media_id = _upload_file(key=key, file=file)
    preload = {
        "msgtype": "file",
        "news": {
            "media_id": media_id
            }
        }
    res = requests.post(web_hook, json=preload)

    if json.loads(res.text)["errmsg"] == "ok":
        logging.info("successful")
    else:
        logging.info("failed")


def _upload_file(key=None, file=None):
    upload_hook = upload_api % key

    with open(file, "rb") as fp:
        data = {"file": fp}
        res = requests.post(upload_hook, files=data)
        media_id = res.json()["media_id"]

        return media_id
