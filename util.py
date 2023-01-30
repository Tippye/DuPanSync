import json
import os
import re

import zxing as zxing
import requests as requests
import smtplib
from email.mime.text import MIMEText

from loguru import logger


def email_push(send_email, send_pwd, receive_email, title, text,
               text_type="html", smtp_address="smtp.qq.com", smtp_port=465):
    """
    邮箱推送

    :param send_email: 发送邮箱的邮箱地址
                       默认为：qq 邮箱，其他邮箱请修改 stmp 地址和端口
    :param send_pwd: 发送邮箱的邮箱授权码
    :param receive_email: 接收信息的邮箱地址（随意是什么邮箱）
                          如果是多个请列表传入 ["第一个", "第二个"]
    :param title: 邮箱标题
    :param text: 需要发送的消息
    :param text_type: 纯文本："plain"，默认为发送 html："html"
    :param smtp_address: stmp 服务地址
    :param smtp_port: stmp 服务端口
    :return:
    """
    msg = MIMEText(text, text_type, "utf-8")
    msg["From"] = send_email
    msg["Subject"] = title
    try:
        with smtplib.SMTP_SSL(smtp_address, smtp_port) as server:
            server.login(send_email, send_pwd)
            server.sendmail(send_email, receive_email, msg.as_string())
            return True
    except Exception as e:
        print(e)
        return False


def server_push(send_key, title, content):
    """
    Server酱推送服务

    :param send_key: 官网获取 send_key，用来发送消息
    :param title: 发送消息的标题
    :param content: 发送文本
    :return:
    """
    send_url = f"https://sctapi.ftqq.com/{send_key}.send"
    params = {"text": title, "desp": content}
    try:
        res = requests.post(send_url, data=params).json()
        """
        {'message': '[AUTH]用户不存在或者权限不足', 'code': 40001, 'info': '用户不存在或者权限不足', 'args': [None]}
        {'code': 0, 'message': '', 'data': {'pushid': '851777', 'readkey': 'SCTHPzE9Yvar1eA', 'error': 'SUCCESS', 'errno': 0}}
        """
        if not res["code"]:
            return {"status": 1, "msg": "Server酱推送服务成功"}
        else:
            return {"status": 0, "errmsg": f"Server酱推送服务失败，{res['message']}"}
    except Exception as e:
        return {"status": 0, "errmsg": f"Server酱推送服务失败，{e}"}


def wechat_enterprise_push(corp_id, corp_secret, agent_id, to_user, msg):
    """
    企业微信推送
    https://work.weixin.qq.com/

    :param corp_id: 企业 ID
    :param corp_secret: 自建应用 Secret
    :param agent_id: 应用 ID
    :param to_user: 接收者用户，多用户用|分割，所有用户填写 @all
    :param msg: 推送消息
    :return:
    """
    # 获取 access_token
    get_access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
    values = {
        'corpid': corp_id,
        'corpsecret': corp_secret,
    }
    try:
        res = requests.post(get_access_token_url, params=values).json()
        if not res['errcode']:
            access_token = res["access_token"]
        elif res['errcode'] == 40001:
            return {"status": 0, "errmsg": "不合法的 secret 参数，https://open.work.weixin.qq.com/devtool/query?e=40001"}
        elif res['errcode'] == 40013:
            return {"status": 0, "errmsg": "不合法的 CorpID，https://open.work.weixin.qq.com/devtool/query?e=40013"}
        else:
            return {"status": 0, "errmsg": res['errmsg']}
    except Exception as e:
        return {"status": 0, "errmsg": f"获取企业微信 access_token 失败，{e}"}

    # 推送消息
    send_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
    post_data = {
        "touser": to_user,
        "msgtype": "text",
        "agentid": agent_id,
        "text": {
            "content": msg
        },
        "safe": "0"
    }
    try:
        res = requests.post(send_url, data=json.dumps(post_data)).json()
        if not res['errcode']:
            return {"status": 1, "msg": "企业微信推送服务成功"}
        elif res['errcode'] == 40056:
            return {"status": 0, "errmsg": "不合法的 agentid，https://open.work.weixin.qq.com/devtool/query?e=40056"}
        elif res['reecode'] == 81013:
            return {"status": 0,
                    "errmsg": "UserID、部门 ID、标签 ID 全部非法或无权限，https://open.work.weixin.qq.com/devtool/query?e=81013"}
    except Exception as e:
        return {"status": 0, "errmsg": f"企业微信推送服务失败，{e}"}


def qmsg_push(key, qq_num, msg, send_type="send"):
    """
    Qmsg酱
    https://qmsg.zendee.cn/index.html

    :param key: qmsg酱的key，官网获取
    :param qq_num: qq号或qq群组号，要与 send_type 对应
    :param msg: 发送消息
    :param send_type: 发送模式，"send"为发送给个人，"group"为发送给群组
    :return:
    """
    post_data = {
        "msg": msg,
        "qq": qq_num
    }
    try:
        res = requests.post(f"https://qmsg.zendee.cn/{send_type}/{key}", data=post_data).json()
        """
        {"success":true,"reason":"操作成功","code":0,"info":{}}
        {"success":false,"reason":"消息内容不能为空","code":500,"info":{}}
        """
        if res['success']:
            return {"status": 1, "msg": "Qmsg酱推送服务成功"}
        return {"status": 0, "errmsg": f"Qmsg酱推送服务失败，{res['reason']}"}
    except Exception as e:
        return {"status": 0, "errmsg": f"Qmsg酱推送服务失败，{e}"}


class Notices:
    success = None
    fail = None
    success_num = None
    config = None
    subscription = None

    def __init__(self):
        self.success = []
        self.fail = []
        self.success_num = 0
        self.config = getConfig()['notice']
        try:
            with open("./temp/sub.json", 'r') as f:
                self.subscription = json.load(f)
        finally:
            if f:
                f.close()

    def addSuccess(self, item):
        self.success.append(item)
        self.success_num += 1
        print("{} 自动同步完成".format(item['save_path'] + '/' + item['server_filename']))

    def addFail(self, item):
        self.fail.append(item)
        print("{} 保存失败".format(item['path']))

    def send(self):
        if len(self.success) < 1 and len(self.fail) < 1:
            logger.info("没有同步文件")
            return
        self._email_push()
        if self.config['email']['enable']:
            logger.info("使用email方式发送通知，通知邮箱：{}".format(self.config['email']['receive_email']))
        else:
            logger.debug(self.config['email'])

    def send_sub(self):
        if self.subscription is None:
            logger.info("没有订阅用户")
            return

        for sub in self.subscription:
            sub_send_list = []
            for p in sub['path']:
                for s in self.success:
                    if len(re.findall('^' + p, s['path'])) > 0:
                        sub_send_list.append(s)
                        break

            if len(sub_send_list) > 0:
                if sub['notice']['email']['enable']:
                    self._email_push(success=sub_send_list, recive=sub['notice']['email']['receive_email'])
                if sub['notice']['request']['enable']:
                    requests.request(method=sub['notice']['request']['method'], url=sub['notice']['request']['url'])
                    self._request_push(sub['notice']['request']['url'], sub['notice']['request']['method'],
                                       sub['notice']['request']['header'])

    def _request_push(self, url, method="GET", header=None, success=None, fail=None):
        if success is None and fail is None:
            success = self.success
            fail = self.fail
        if header is None:
            header = {}
        data = {
            "success": success,
            "fail": fail
        }
        if method == "GET":
            requests.request(method="GET", url=url, params=data, headers=header)
            logger.info("GET请求已发送，url={}".format(url))
        elif method == "POST":
            requests.request(method="POST", url=url, data=data, headers=header)
            logger.info("POST请求已发送，url={}".format(url))

    def _email_push(self, success=None, fail=None, recive=None):
        if not self.config['email']['enable']:
            logger.info("未配置email通知方式")
            return
        if success is None and fail is None:
            success = self.success
            fail = self.fail
        if recive is None:
            recive = self.config['email']['receive_email']
        mail_msg_list = ["""<style type="text/css">
                #customers
                  {
                  font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
                  width:100%;
                  border-collapse:collapse;
                  }

                #customers td, #customers th
                  {
                  font-size:1em;
                  border:1px solid #98bf21;
                  padding:3px 7px 2px 7px;
                  }

                #customers th
                  {
                  font-size:1.1em;
                  text-align:left;
                  padding-top:5px;
                  padding-bottom:4px;
                  background-color:#A7C942;
                  color:#ffffff;
                  }

                #customers tr.alt td
                  {
                  color:#000000;
                  background-color:#EAF2D3;
                  }
                
                #customers tr.fail td
                  {
                  color:#000000;
                  background-color:#FFC6D3;
                  }
                  
                #customers tr.fail.alt td
                  {
                  background-color:#FEA1BF;
                  }
                  
              
                </style>""", f"""<span style="font-family: 'Microsoft YaHei UI',serif; color: lightskyblue;text-align: center;" >
        >>>>更新信息数据表格<<<</span> <table id="customers"> <tr> <th>文件名</th> <th>群文件路径</th> <th>保存路径</th> </tr>"""]
        if success is not None:
            for index, item in enumerate(success):
                try:
                    if index % 2:
                        mail_msg_list.append(f"""<tr>
                                            <td>{item['path'].split('/')[-1]}</td>
                                            <td>{item['path']}</td>
                                            <td>{item['save_path']}</td>
                                            </tr>""")
                    else:
                        mail_msg_list.append(f"""<tr class="alt">
                                            <td>{item['path'].split('/')[-1]}</td>
                                            <td>{item['path']}</td>
                                            <td>{item['save_path']}</td>
                                            </tr>""")
                except BaseException as e:
                    logger.error(e)
                    logger.info(success)

        if fail is not None:
            for index, item in enumerate(fail):
                try:
                    if index % 2:
                        mail_msg_list.append(f"""<tr class="fail">
                                            <td>{item['path'].split('/')[-1]}</td>
                                            <td>{item['path']}</td>
                                            <td>{item['save_path']}</td>
                                            </tr>""")
                    else:
                        mail_msg_list.append(f"""<tr class="fail alt">
                                            <td>{item['path'].split('/')[-1]}</td>
                                            <td>{item['path']}</td>
                                            <td>{item['save_path']}</td>
                                            </tr>""")
                except BaseException as e:
                    logger.error(e)
                    logger.info(fail)
        mail_msg_list.append(
            f"""</table><h4><center> >>>>  <a href="https://gitee.com/tippy_q/du-pan-sync">DuPanSync</a> <<<<</center></h4>""")
        return email_push(send_email=self.config['email']['send_email'], send_pwd=self.config['email']['send_pwd'],
                          receive_email=recive, title="百度网盘同步更新",
                          text="".join(mail_msg_list), smtp_port=self.config['email']['smtp_port'],
                          smtp_address=self.config['email']['smtp_address'])


def zxingParseQRCode(filePath):
    """
    控制台打印二维码

    :param filePath: 图片地址，可以是url
    :return:
    """
    reader = zxing.BarCodeReader()
    if os.path.isfile(filePath):
        barcode = reader.decode(filePath)
    else:
        save_path = getConfig()['qrCodeImagePath']
        with open(save_path, "wb") as f:
            f.write(requests.get(url=filePath).content)
            logger.info("二维码图片已保存到 {}".format(save_path))
        barcode = reader.decode("./temp/login.png")

    return barcode.parsed


def getConfig():
    """
    获取配置文件的信息

    :return:
    """
    try:
        with open('./config.json', 'r', encoding='utf8') as f:
            return json.load(f)
    except:
        return {}
    finally:
        if f:
            f.close()
