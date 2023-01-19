import json
import os

import zxing as zxing
import requests as requests


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
        with open(getConfig()['qrCodeImagePath'], "wb") as f:
            f.write(requests.get(url=filePath).content)
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
