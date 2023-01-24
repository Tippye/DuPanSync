import json
import urllib

from loguru import logger

from DuUtil import DuUtil

SyncPath = "./temp/sync.json"


def getSyncData():
    """
    读取自动同步列表文件

    :return:
    """
    try:
        with open(SyncPath, 'r') as f:
            return json.load(f)
    except FileNotFoundError as e:
        d = []
        if setSyncData(d):
            return d
        return False
    finally:
        f.close()


def setSyncData(data):
    """
    设置自动同步文件

    :param data:覆盖原文件的内容
    :return:
    """
    try:
        with open(SyncPath, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except BaseException as e:
        print(e)
        return False
    finally:
        f.close()


def selectGroupDir(du_util: DuUtil):
    """
    选择要同步的群文件目录

    :param du_util: 初始化过的DuUtil对象
    :return: {
        "gid",
        "from_uk",
        "msg_id",
        "fs_ids"
    }
    """
    group_page = 1
    group_num = 20
    # 后面要用的gid, uk在group中
    group = None
    while group is None:
        groups = du_util.getGroupList(page=group_page, num=group_num)
        print("请选择群聊列表：\n\t[0] 结束程序")
        for i in range(1, len(groups) + 1):
            print("\t[{0}] {1}".format(i, groups[i - 1]["name"]))

        if group_page > 1:
            print("\t[<] 上一页\t\t当前第{0}页".format(group_page))

        if len(groups) == group_num:
            print("\t[>] 下一页\t\t当前第{0}页".format(group_page))

        group_ipt = input()
        if group_ipt == '0':
            return False
        if group_ipt == '<':
            group_page -= 1
            continue
        if group_ipt == '>':
            group_page += 1
            continue
        try:
            group_ipt_int = int(group_ipt)
            if group_ipt_int > (len(groups) + 1):
                raise IndexError
        except (ValueError,IndexError):
            print("请输入合法字符")
        else:
            group = groups[group_ipt_int - 1]
    print("已选择群组：{}".format(group['name']))

    # 后面要用的msg_id,fs_id在root_dir中
    root_dir = None
    root_list = du_util.getGroupRoot(group["gid"])
    print("请选择要同步的文件夹：\n\t[0] 结束程序")
    for i in range(1, len(root_list) + 1):
        try:
            print("\t[{0}] {1}".format(i, root_list[i - 1]['file_list'][0]['server_filename']))
        except BaseException as e:
            print("显示群文件目录时出错")
            print(e)
    root_ipt = None
    while root_ipt is None:
        try:
            root_ipt = input()
            root_ipt_int = int(root_ipt)
            if root_ipt_int > len(root_list):
                raise IndexError
        except (ValueError,IndexError) as e:
            print("请输入合法字符")
            root_ipt = None
        else:
            root_dir = root_list[root_ipt_int - 1]
    print("已选择目录：{}".format(root_dir['file_list'][0]['server_filename']))

    path_ipt = None
    path_page = 1
    path_num = 50
    select_dir = root_dir['file_list'][0]
    select_dir['path'] = urllib.parse.unquote(select_dir['path'])
    while path_ipt is None:
        print("请选择需要同步的文件夹：\n\t[0] 结束\n\t[1] 当前文件夹({})".format(select_dir['server_filename']))
        path_list = du_util.getGroupDir(group['uk'], root_dir['msg_id'], select_dir['fs_id'],
                                        group['gid'], path_page,
                                        path_num)
        for i in range(1, len(path_list) + 1):
            try:
                print("\t[{0}] 转到 {1}".format(i + 1, path_list[i - 1]['server_filename']))
            except BaseException as e:
                print("显示群文件目录时出错")
                print(e)
        if path_page > 1:
            print("\t[<] 上一页\t\t当前第{}页".format(path_page))
        if len(path_list) == path_num:
            print("\t[>] 下一页\t\t当前第{}页".format(path_page))

        path_ipt = input()

        if path_ipt == '0':
            return False
        if path_ipt == '1':
            continue
        if path_ipt == '>':
            path_page += 1
            continue
        if path_ipt == '<':
            path_page -= 1
            continue
        try:
            path_ipt_int = int(path_ipt)
            if path_ipt_int > (len(path_list) + 1):
                raise IndexError
        except (ValueError, IndexError) as e:
            print("请输入合法字符")
            path_ipt = None
        else:
            select_dir = path_list[path_ipt_int - 2]
            path_ipt = None
    print("已选择同步目录：{}".format(select_dir['path']))
    return {
        "gid": group['gid'],
        "from_uk": group['uk'],
        "msg_id": root_dir['msg_id'],
        "fs_ids": [select_dir['fs_id']],
        "sync_dir": select_dir['path']
    }


def selectPanDir(du_util: DuUtil):
    """
    让用户选择网盘目录

    :param du_util:
    :return:
    """
    path = "/"
    ipt_num = None
    page = 1
    num = 100
    while ipt_num is None:
        print("请选择要保存的目录：\n\t[0] 结束\n\t[1] 当前文件夹({})".format(path.split('/')[-1]))
        file_list = du_util.getFileList(path=path, isdir=True, page=page, num=num)
        for i in range(1, len(file_list) + 1):
            try:
                print("\t[{0}] 跳转到 {1}".format(i + 1, file_list[i - 1]['path'].split('/')[-1]))
            except BaseException as e:
                print("显示网盘目录错误")
                print(e)
        if page > 1:
            print("\t[<] 上一页\t\t当前第{}页".format(page))
        if len(file_list) == num:
            print("\t[>] 下一页\t\t当前第{}页".format(page))

        ipt_num = input()

        if ipt_num == '0':
            return False
        if ipt_num == '1':
            continue
        if ipt_num == '<':
            page -= 1
            continue
        if ipt_num == '>':
            page += 1
            continue
        try:
            ipt_num_int = int(ipt_num)
            if ipt_num_int > (len(file_list) + 1):
                raise IndexError
        except (ValueError, IndexError) as e:
            print("请输入合法字符")
            ipt_num = None
        else:
            path = file_list[ipt_num_int - 2]['path']
            ipt_num = None

    return path


def makeNewSync(du_util: DuUtil):
    """
    设置一个新的同步目录

    :param du_util:
    :return:
    """
    sync_data = getSyncData()
    # 这里不能用assert或者not sync_data，不然数组为空时也会报错
    if sync_data == False:
        logger.warning("获取同步数据文件错误，请检查/temp/sync.json是否存在")
        return False
    group_data = selectGroupDir(du_util)
    assert group_data
    for d in sync_data:
        if d['gid'] == group_data['gid'] and d['fs_ids'][0] == group_data['fs_ids'][0]:
            logger.info("当前目录已设置自动同步")
            return False
    save_path = selectPanDir(du_util)
    assert save_path
    if du_util.saveDir(group_data['from_uk'], group_data['msg_id'], save_path, group_data['fs_ids'][0],
                       group_data['gid']):
        sync_data.append({
            "gid": group_data['gid'],
            "from_uk": group_data['from_uk'],
            "msg_id": group_data['msg_id'],
            "fs_ids": group_data['fs_ids'],
            "path": "{0}/{1}".format(save_path, group_data['sync_dir'].split('/')[-1]),
            "sync_dir": group_data['sync_dir']
        })
        if setSyncData(sync_data):
            logger.info("已将目录 {} 设置自动同步".format(group_data['sync_dir']))
        else:
            logger.warning("目录 {} 已设置同步，但同步文件未写入成功".format(group_data['sync_dir']))
            logger.info(json.dumps(sync_data))
    else:
        logger.warning("目录 {} 保存失败，请重试".format(group_data['sync_dir']))


def delSyncData(d):
    """
    删除设置的自动同步

    :param d: 自动同步的对象，只用path和sync_dir判断
    :return:
    """
    datas = getSyncData()

    def filter_fun(s): return s if (s['path'] != d['path'] and s['sync_dir'] != d['sync_dir']) else None

    result = list(filter(filter_fun, datas))
    logger.info('删除自动同步项：{}'.format(d['sync_dir']))
    setSyncData(result)


def printSyncList():
    """
    打印所有同步列表

    :return:
    """
    data = getSyncData()
    print('[0] 退出')
    print('\t\t群文件路径\t保存路径\t\t(输入对应数字进行操作)')
    for i in range(1, len(data) + 1):
        print('[{0}]\t{1}\t{2}'.format(i, data[i - 1]['sync_dir'], data[i - 1]['path']))

    ipt1 = ''
    while ipt1 != '0':
        ipt1 = input()
        try:
            ipt_int = int(ipt1)
            if ipt_int > (len(data) + 1) or ipt_int < 1:
                raise IndexError
        except (ValueError, IndexError):
            print('请输入合法字符')
        else:
            print('[0] 取消\n[1] 删除')
            ipt2 = input()
            if ipt2 == '0':
                ipt1 = '0'
                printSyncList()
            elif ipt2 == '1':
                delSyncData(data[ipt_int - 1])
                ipt1 = '0'
                printSyncList()
