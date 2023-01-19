import requests as requests

from DuUtil import DuUtil
from syncSetter import makeNewSync


def main():
    ipt1 = ''
    while ipt1 != '0':
        print("请选择要执行的操作：\n\t[0] 退出\n\t[1] 设置同步目录\n\t[2] 同步所有目录")
        ipt1 = input()
        if ipt1 == '0':
            pass
        elif ipt1 == '1':
            makeNewSync(dupan)
            ipt1 = ''
        elif ipt1 == '2':
            print('敬请期待')
            ipt1 = ''
        else:
            ipt1 = ''


if __name__ == '__main__':
    try:
        dupan = DuUtil()
        # main()
        main()
    except requests.exceptions.ConnectionError:
        print("网络连接错误")
    finally:
        if dupan:
            dupan.close()
