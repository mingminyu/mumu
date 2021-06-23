# coding: utf-8
# ================================================
# Project: mumu
# File: /test_wwx.py
# Author: Mingmin Yu
# Email: yu_ming623@163.com
# Date: 2021/6/23 19:35
# Description:
# ================================================
import os
from mumu.conf import *
from mumu.robots import WorkWeChatRobot

# Test 1: Test for end text messages and at_all -> success
# content = """
#     Hi，我是机器人test
#     由郁明敏于2020年12月18日添加到群
#     """
# wwx = WorkWeChatRobot(key=WWX_CONF["key"], at_all=True)
# wwx.send_messages(content=content)

# Test 2: Test for mentioned_mobile_list -> success
# content = """
#     Hi，我是机器人test2
#     由郁明敏于2020年12月18日添加到群
#     """
# wwx = WorkWeChatRobot(key=WWX_CONF["key"], mentioned_mobile_list=WWX_CONF["at"])
# wwx.send_messages(content=content)

# Test 3: Test for markdown messages -> success
# content = '''实时新增用户反馈<font color=\"warning\">132例</font>，请相关同事注意。\n
#          > 类型:<font color=\"comment\">用户反馈</font>
#          > 普通用户反馈:<font color=\"comment\">117例</font>
#          > VIP用户反馈:<font color=\"comment\">15例</font>"
#
#          # h1
#          ## h2
#
#          <font color="info">绿色</font>
#          <font color="comment">灰色</font>
#          <font color="warning">橙红色</font>
#
#          `code`     **bold**
#
#          [click to browser](http://work.weixin.qq.com/api/doc)
#         '''
# wwx = WorkWeChatRobot(key=WWX_CONF["key"], at_all=True, mentioned_mobile_list=WWX_CONF["at"])
# wwx.send_messages_md(content=content)

# Test 4: Test for image -> success
# img = os.path.join(os.getcwd(), "zoro.jpg")
# wwx = WorkWeChatRobot(key=WWX_CONF["key"])
# wwx.send_image(image_path=img)

# Test 4: Test for news -> success
# content = [
#         {
#            "title": "中秋节礼品领取",
#            "description": "今年中秋节公司有豪礼相送",
#            "url": "www.qq.com",
#            "picurl": "https://img2.baidu.com/it/u=3566088443,3713209594&fm=26&fmt=auto&gp=0.jpg"
#         },
#         {
#            "title": "中秋节礼品领取2",
#            "description": "今年中秋节公司有豪礼相送",
#            "url": "www.qq.com",
#            "picurl": "https://img2.baidu.com/it/u=3566088443,3713209594&fm=26&fmt=auto&gp=0.jpg"
#         },
#     ]
# wwx = WorkWeChatRobot(key=WWX_CONF["key"])
# wwx.send_article(content=content)

# Test 5: Test for file ->
img = os.path.join(os.getcwd(), "zoro.jpg")
wwx = WorkWeChatRobot(key=WWX_CONF["key"])
wwx.send_file(file=img)
