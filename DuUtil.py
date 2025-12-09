import base64
import json
import re
import urllib
from time import sleep

# import qrcode_terminal
from loguru import logger
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver import Safari
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from request import Request
from util import getConfig


class DuUtil:
    _config = None
    _cookie = None
    _header = None
    _driver = None
    _bdstoken = None
    _request = None

    def __init__(self):
        logger.info("初始化DuUtil...")
        print("\n正在初始化...")
        self._config = getConfig()
        self._setDriver()
        self._setHeader()
        self._request = Request("https://pan.baidu.com", self._header)
        logger.info("DuUtil初始化成功")
        print("初始化成功")

    def _setDriver(self):
        """
        设置浏览器

        主要用于获取登录token和bdstoken
        :return:
        """
        # self._bdstoken = "71bd27e587f4adee527c306035028bd4"
        # driver_options = ChromeOptions()
        # if not self._config['showWebDriver']:
        #     logger.info("已配置不显示浏览器")
        #     driver_options.add_argument("--headless")
        #     driver_options.add_argument('--no-sandbox')
        #     driver_options.add_argument('--disable-gpu')
        #     driver_options.add_argument('--disable-dev-shm-usage')
        #     driver_options.add_argument('--incognito')
        #     driver_options.add_argument('--blink-settings=imagesEnabled=false')
        # self._driver = Chrome(
        #     self._config['ChromedriverPath'] if self._config['ChromedriverPath'] is not None else "chromedriver",
        #     options=driver_options)
        # self._driver.get("https://pan.baidu.com")
        # with open("./temp/cookie.json", "r", encoding="utf8") as f:
        #     self._cookie = json.load(f)
        # return
        driver_options = ChromeOptions()
        if not self._config['showWebDriver']:
            logger.info("已配置不显示浏览器")
            driver_options.add_argument("--headless")
            driver_options.add_argument('--no-sandbox')
            driver_options.add_argument('--disable-gpu')
            driver_options.add_argument('--disable-dev-shm-usage')
            driver_options.add_argument('--incognito')
            driver_options.add_argument('--blink-settings=imagesEnabled=false')
        # 添加SSL/证书相关选项，解决新版Chrome的兼容性问题
        driver_options.add_argument('--ignore-certificate-errors')
        driver_options.add_argument('--ignore-ssl-errors=yes')
        driver_options.add_argument('--allow-running-insecure-content')
        
        # 使用webdriver-manager自动管理ChromeDriver版本
        chrome_path = self._config.get('ChromedriverPath')
        if chrome_path:
            service = Service(executable_path=chrome_path)
        else:
            service = Service(ChromeDriverManager().install())
        
        self._driver = Chrome(service=service, options=driver_options)
        self._driver.get("https://pan.baidu.com")
        try:
            f = None
            with open("./temp/cookie.json", "r", encoding="utf8") as f:
                self._cookie = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
            try:
                self._getCookie()
            except AssertionError:
                logger.warning("登录失败，重试次数过多")
                print("登录失败，重试次数过多")
        else:
            WebDriverWait(self._driver, 5, 0.5).until(expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, ".u-button.bd-login-button__wrapper.u-button--primary")))
            for c in self._cookie:
                self._driver.add_cookie(c)

            self._driver.get("https://pan.baidu.com")
            logger.info("自动登录成功")
            print("自动登录成功")
            # TODO: token失效时的处理，目前还未测试出token失效时间，待补充
        finally:
            if f:
                f.close()
            if self._cookie is not None:
                source = self._driver.page_source
                self._bdstoken = re.findall(r'bdstoken":"(.*?)"', source)[0]
                logger.debug("bdstoken获取成功：{}".format(self._bdstoken))

    def _getCookie(self):
        """
        获取cookie
        :return:
        """
        logger.info("开始使用浏览器登录")
        # 等待未登录时的登录按钮加载出来
        WebDriverWait(self._driver, 5, 0.5).until(expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, ".u-button.bd-login-button__wrapper.u-button--primary")))
        # 点击"去登录"按钮
        btn_qudenglu = self._driver.find_element(By.CSS_SELECTOR,
                                                 ".u-button.bd-login-button__wrapper.u-button--primary")
        btn_qudenglu.click()
        logger.debug("点击 .u-button.bd-login-button__wrapper.u-button--primary 标签")
        # 等待"扫码登录"按钮出现并点击
        WebDriverWait(self._driver, 5, 0.5).until(
            expected_conditions.presence_of_element_located((By.ID, "TANGRAM__PSP_11__changeQrCodeItem")))
        btn_saomadenglu = self._driver.find_element(By.ID, "TANGRAM__PSP_11__changeQrCodeItem")
        btn_saomadenglu.click()
        logger.debug("点击 #TANGRAM__PSP_11__changeQrCodeItem 按钮")
        # 等待登录二维码出现
        WebDriverWait(self._driver, 5, 0.5).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, "tang-pass-qrcode-img")))
        # TODO：等待两秒让他加载出来二维码，此处可以优化判断链接是否是加载中
        sleep(2)
        login_qrcode_url = self._driver.find_element(By.CLASS_NAME, "tang-pass-qrcode-img")
        logger.debug("获取登录二维码，二维码链接: {}".format(login_qrcode_url))
        # 保存图片
        login_qrcode_url.screenshot(self._config['qrCodeImagePath'])
        print("请扫描二维码登录，如果无法扫描请扫描程序目录下" + self._config['qrCodeImagePath'])
        print("登录成功后请按下回车键")
        # 在控制台打印二维码，同时保存图片到本地
        # qrcode_terminal.draw(zxingParseQRCode(login_qrcode_url.get_attribute("src")))
        terminal_input = None
        relogin = 1
        while terminal_input is None and relogin < 6:
            terminal_input = input()
            # 尝试查找用户名的标签，如果找到就继续执行，否则重新按下键盘
            try:
                self._driver.find_element(By.CSS_SELECTOR,
                                          ".wp-s-header-user__body-username.inline-block-v-middle.text-ellip")
            except NoSuchElementException:
                terminal_input = None
                relogin += 1
                logger.warning("登录未成功，请重新按下回车键，失败次数：{}".format(relogin))
                print("登录未成功，请重新按下回车键")
        assert relogin < 6
        ck = self._driver.get_cookies()

        self._cookie = ck

        logger.info("登录成功，cookie存储在 ./temp/cookie.json")
        self._driver.get("https://pan.baidu.com")
        with open("./temp/cookie.json", "w") as f:
            json.dump(ck, f, ensure_ascii=False, indent=2)
            f.close()

    def _setHeader(self):
        """
        设置请求头
        :return:
        """
        if self._cookie is None:
            self._getCookie()
        self._header = {
            "Cookie": "",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
        }
        for c in self._cookie:
            self._header["Cookie"] += (c["name"] + "=" + c["value"] + ";")

        logger.debug("请求头Cookie: {}".format(self._header['Cookie']))

    def getFileList(self, path="/", isdir=False, page=1, num=100, order="time"):
        """
        获取网盘文件目录

        :param path: 目录路径
        :param isdir: 只列出文件夹
        :param page: 页码
        :param num: 一页的数量
        :param order: 排序方式
        :return:
        """
        res = self._request.get(url="/api/list", params={
            "channel": "chunlei",
            "clienttype": 0,
            "web": 1,
            "app_id": 250528,
            "order": order,
            "desc": 1,
            "dir": path,
            "page": page,
            "num": num,
            "folder": isdir + 0
        })
        try:
            return res['list']
        except KeyError:
            logger.debug(res)
            return []

    def removeFile(self, path: list):
        """
        移除指定目录下的文件/文件夹
        删除需要时间，最长可能需要10s

        :param path: 包括文件夹和文件，每一项都是文件夹或者文件的路径，如：['/test/1.txt', '/test/2.txt', '/test/3.txt']
        :return: True/False
        """
        res = self._request.post(url="/api/filemanager", params={
            "async": 2,
            "onnest": 'fail',
            "web": 1,
            "app_id": 250528,
            "opera": 'delete',
            "newVerify": 1,
            "clienttype": 0,
            "bdstoken": self._bdstoken,
        },data={
            "filelist": json.dumps(path)
        })
        res = json.loads(res)

        if res['errno'] == 0:
            verifyRes = None
            retry = 0
            while verifyRes is None or verifyRes['status'] not in ['success', 'failed'] or retry < 10:
                verifyRes = self._request.get(url="/share/taskquery", params={
                    "taskid": res['taskid'],
                    "web": 1,
                    "app_id": 250528,
                    "clienttype": 0,
                })
                retry += 1
                sleep(1)
            return verifyRes['status'] == 'success'
        else:
            logger.warning("删除文件失败：{}".format(res))
            return False

    def getGroupList(self, page=0, num=20):
        """
        获取群组列表
        :param page: 第几页
        :param num: 一页多少条
        :return:[{
                    "gid": "593261968581215430",
                    "gnum": "983965159",
                    "name": "迟**vQ、WhB****226、175*****759、11****旺的家、155*****518",
                    "gdesc": "",
                    "announce": "",
                    "type": "1",
                    "status": "1",
                    "ctime": 1610274959,
                    "name_flag": "0",
                    "vip": "0",
                    "spam_count": null,
                    "invite_status": "0",
                    "search_status": 1,
                    "banpost_status": "0",
                    "photoinfo": [{
                        "uk": 2956775652,
                        "uname": "迟**vQ",
                        "photo": "https://dss0.bdstatic.com/7Ls0a8Sm1A5BphGlnYG/sys/portrait/item/netdisk.1.e1f087ba.jQ-2zO1sOrsp77mez_x6Ug.jpg"
                      }],
                    "gtype": 1,
                    "group_status": 1,
                    "uname": "迟**vQ",
                    "uk": 2956775652,
                    "avatar_url": "https://dss0.bdstatic.com/7Ls0a8Sm1A5BphGlnYG/sys/portrait/item/netdisk.1.e1f087ba.jQ-2zO1sOrsp77mez_x6Ug.jpg",
                    "group_remark": ""
                }]
        """
        groups_list_res = self._request.get(url="/mbox/group/list", params={
            "web": 1,
            "start": page,
            "limit": num,
            "type": 0,
            "clienttype": 0
        })
        try:
            return groups_list_res["records"]
        except KeyError:
            logger.debug(groups_list_res)
            return []

    def getGroupRoot(self, group_id):
        """
        获取群文件根目录

        :param group_id: 群组gid
        :return:
        """
        listshare_res = None
        try:
            listshare_res = self._request.get(url="/mbox/group/listshare", params={
                "web": 1,
                "type": 2,
                "gid": group_id,
                "limit": 50,
                "desc": 1,
                "app-id": 250528,
                "clienttype": 0
            })
            return listshare_res['records']['msg_list']
        except KeyError:
            logger.debug(listshare_res.text)
            return []

    def getGroupDir(self, group_uk, msg_id, fs_id, group_id, page=1, num=50):
        """
        获取群文件列表（不是根目录的）

        :param group_uk:
        :param msg_id:
        :param fs_id:
        :param group_id:
        :param page: 页码
        :param num: 一页的数量
        :return:[{
            "category": 6,
            "fs_id": 142717881277597,
            "isdir": 1,
            "local_ctime": 1597286720,
            "local_mtime": 1597286720,
            "path": "/2024公共课【持续更新中】/重要：课程都是自动更新，跟文件夹日期无关，切记",
            "server_ctime": 1597286720,
            "server_filename": "重要：课程都是自动更新，跟文件夹日期无关，切记",
            "server_mtime": 1672747196,
            "size": 0
        }]
        """
        res = self._request.post(url="/mbox/msg/shareinfo", params={
            "from_uk": group_uk,
            "msg_id": msg_id,
            "type": 2,
            "num": num,
            "page": page,
            "fs_id": fs_id,
            "gid": group_id,
            "limit": 50,
            "desc": 1,
            "clienttype": 0,
            "app_id": 250528,
            "web": 1
        })
        try:
            return res['records']
        except KeyError:
            logger.debug(res)
            return []

    def saveDir(self, from_uk, msg_id, path, fs_id, gid):
        logid = ""
        for c in self._cookie:
            if c['name'] == 'BAIDUID':
                logid = base64.b64encode(c['value'].encode('utf-8')).decode('utf-8')

        payload = 'from_uk=' + str(from_uk) \
                  + '&msg_id=' + str(msg_id) \
                  + '&path=' + urllib.parse.quote(path).replace('/', '%2F') \
                  + '&ondup=newcopy&async=1&' \
                  + 'fs_ids=%5B' + str(fs_id) + '%5D&type=2&' \
                  + 'gid=' + str(gid)

        logger.debug("logid: {}".format(logid))
        transfer_res = self._request.post(
            url="/mbox/msg/transfer?channel=chunlei&clienttype=0&web=1&app_id=250528&logId=" + logid + "&bdstoken=" + self._bdstoken + "&clienttype=0&app_id=250528&web=1",
            data=payload)
        if transfer_res['errno'] == 0:
            logger.info("保存文件成功: 文件已保存到 {}".format(path))
            print("保存成功")
            return True
        else:
            logger.warning("文件保存失败：{}".format(transfer_res))
            print("保存失败")
            return False

    def close(self):
        logger.info("DuUtil关闭")
        logger.debug("一共发送了{}次请求", self._request.get_num())
        if self._driver:
            self._driver.close()
