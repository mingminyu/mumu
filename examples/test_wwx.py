# # coding: utf-8
# # ================================================
# # Project: mumu
# # File: examples/test_wwx.py
# # Author: Mingmin Yu
# # Email: yu_ming623@163.com
# # Date: 2021/6/23 19:35
# # Description:
# # ================================================
import os
import textwrap
from mumu.conf import read_config
from mumu.robots import (wwx_send_messages,
                         wwx_send_messages_md,
                         wwx_send_file,
                         wwx_send_news,
                         wwx_send_image,
                         wwx_send_images)


config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "project.cfg")
PROJECT_CONF, DB_CONF, HDFS_CONF, EMAIL_CONF, WWX_CONF = read_config(cfg_file=config_file)

# Test 1: Test for end text messages and at_all -> success
content = """
    Hi，我是机器人test
    于2020年12月18日添加到群
    """
wwx_send_messages(key=WWX_CONF["key"], at_all=True, content=content)

# Test 2: Test for mentioned_mobile_list -> success
content = """
    Hi，我是机器人test2
    于2020年12月18日添加到群
    """
wwx_send_messages(key=WWX_CONF["key"], content=content, mentioned_mobile_list=WWX_CONF["at"])


# Test 3: Test for markdown messages -> success
content = '''
     实时新增用户反馈<font color=\"warning\">132例</font>，请相关同事注意。\n
     > 类型:<font color=\"comment\">用户反馈</font>
     > 普通用户反馈:<font color=\"comment\">117例</font>
     > VIP用户反馈:<font color=\"comment\">15例</font>"

     # h1
     ## h2

     <font color="info">绿色</font>
     <font color="comment">灰色</font>
     <font color="warning">橙红色</font>

     `code`     **bold**

     [click to browser](http://work.weixin.qq.com/api/doc)
    '''
wwx_send_messages_md(key=WWX_CONF["key"], content=textwrap.dedent(content))

# Test 4: Test for image -> success
img = os.path.join(os.getcwd(), "test.png")
wwx_send_image(key=WWX_CONF["key"], image=img)

# Test 4: Test for news -> success
articles = [
        {
           "title": "中秋节礼品领取",
           "description": "今年中秋节公司有豪礼相送",
           "url": "www.qq.com",
           "picurl": "https://img2.baidu.com/it/u=3566088443,3713209594&fm=26&fmt=auto&gp=0.jpg"
        },
        {
           "title": "中秋节礼品领取2",
           "description": "今年中秋节公司有豪礼相送",
           "url": "www.qq.com",
           "picurl": "https://img2.baidu.com/it/u=3566088443,3713209594&fm=26&fmt=auto&gp=0.jpg"
        },
    ]
wwx_send_news(key=WWX_CONF["key"], articles=articles)

# Test 5: Test for file -> success
fn = os.path.join(os.getcwd(), "zoro.jpg")
wwx_send_file(key=WWX_CONF["key"], file=fn)
