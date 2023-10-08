import requests
import selenium.common.exceptions

from DuUtil import DuUtil
from sync import syncAllDir
from syncSetter import makeNewSync, printSyncList
from loguru import logger


def main(dp):
    ipt1 = ''
    while ipt1 != '0':
        print("请选择要执行的操作：\n\t[0] 退出\n\t[1] 设置同步目录\n\t[2] 同步所有目录\n\t[3] 查看同步列表")
        ipt1 = input()
        try:
            if ipt1 != '0':
                if ipt1 == '1':
                    makeNewSync(dp)
                elif ipt1 == '2':
                    syncAllDir(dp)
                elif ipt1 == '3':
                    printSyncList()

                ipt1 = ''
            else:
                dp.close()
        except AssertionError as e:
            logger.warning(e)

def shellSync():
    """
    此方法用于直接从命令行执行同步命令，方便自己设定定时任务
    启动命令    python -c "from main import shellSync;shellSync()"

    :return:
    """
    logger.add('./logs/runlog_{time}.log', rotation="50 MB", encoding='utf-8', retention="3 days",
               level="INFO")
    logger.info("开始执行同步程序")

    dp = None
    try:
        dp = DuUtil()
        syncAllDir(dp)
    except requests.exceptions.ConnectionError as e:
        logger.error("网络连接错误：{}".format(e))
        print("网络连接错误")
    except AssertionError as e:
        logger.warning("程序中断：{}".format(e))
    except selenium.common.exceptions.SessionNotCreatedException as e:
        if e.msg.find("This version of ChromeDriver only supports Chrome version"):
            logger.error("ChromeDriver版本错误，请检查ChromeDriver版本是否正确")
            print("ChromeDriver版本错误，请检查ChromeDriver版本是否正确")
    finally:
        if dp:
            dp.close()


if __name__ == '__main__':
    logger.remove()
    logger.add('./logs/runlog_{time}.log', rotation="50 MB", encoding='utf-8', retention="3 days")
    logger.info("开始执行主程序")

    dupan = None
    try:
        dupan = DuUtil()
        main(dupan)
    except requests.exceptions.ConnectionError as e:
        logger.error("网络连接错误：{}".format(e))
        print("网络连接错误")
    except AssertionError as e:
        logger.warning("程序中断：{}".format(e))
    except selenium.common.exceptions.SessionNotCreatedException as e:
        if e.msg.find("This version of ChromeDriver only supports Chrome version"):
            logger.error("ChromeDriver版本错误，请检查ChromeDriver版本是否正确")
            print("ChromeDriver版本错误，请检查ChromeDriver版本是否正确")
    finally:
        if dupan:
            dupan.close()
