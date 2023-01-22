import requests as requests

from DuUtil import DuUtil
from sync import syncAllDir
from syncSetter import makeNewSync, printSyncList


def main():
    ipt1 = ''
    while ipt1 != '0':
        print("请选择要执行的操作：\n\t[0] 退出\n\t[1] 设置同步目录\n\t[2] 同步所有目录\n\t[3] 查看同步列表")
        ipt1 = input()
        if ipt1 != '0':
            if ipt1 == '1':
                makeNewSync(dupan)
            elif ipt1 == '2':
                syncAllDir(dupan)
            elif ipt1 == '3':
                printSyncList()

            ipt1 = ''


def shellSync():
    """
    此方法用于直接从命令行执行同步命令，方便自己设定定时任务
    启动命令    python -c "from main import shellSync;shellSync()"

    :return:
    """
    try:
        dupan = DuUtil()
        syncAllDir(dupan)
    except requests.exceptions.ConnectionError:
        print("网络连接错误")
    finally:
        if dupan:
            dupan.close()


if __name__ == '__main__':
    try:
        dupan = DuUtil()
        main()
    except requests.exceptions.ConnectionError:
        print("网络连接错误")
    finally:
        if dupan:
            dupan.close()
