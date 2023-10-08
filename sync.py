from loguru import logger

from DuUtil import DuUtil
from syncSetter import getSyncData
from util import Notices, getConfig


def getSyncDir(sync_data, du_util: DuUtil):
    # try:
    wait_list = [sync_data]
    page_size = 50
    update_list = []
    ignore_list = getConfig()["ignore"]
    ignore_dic = dict()
    for il in ignore_list:
        ignore_dic[il] = True
    while len(wait_list) > 0:
        sd = wait_list.pop(0)
        logger.info("正在同步：{}".format(sd['path']))
        try:
            # 获取群文件中的文件列表
            need_get_group_dir = True
            group_dir_list = []
            page = 1
            while need_get_group_dir:
                group_dir_list += du_util.getGroupDir(sd['from_uk'], sd['msg_id'], sd['fs_ids'][0],
                                                      sd['gid'], page, page_size)
                if page * page_size <= len(group_dir_list):
                    page += 1
                else:
                    need_get_group_dir = False
            if len(group_dir_list) == 0:
                logger.warning("获取群文件列表失败")
                print("获取群文件列表失败")
                return []
            # 获取自己网盘中的文件列表
            need_get_file_list = True
            file_list = []
            page = 1
            while need_get_file_list:
                file_list += du_util.getFileList(sd['path'], page=page, num=page_size, order="name")
                if page * page_size <= len(group_dir_list):
                    page += 1
                else:
                    need_get_file_list = False

            # 查找网盘里没有的文件
            for i in range(0, len(group_dir_list)):
                existed = False
                for j in range(0, len(file_list)):
                    if group_dir_list[i]['server_filename'] == file_list[j]['server_filename']:
                        file_list.pop(j)
                        existed = True
                        break
                if not existed:
                    # 不存在直接加入待更新列表
                    logger.info("发现未保存{0}：{1}".format("目录" if group_dir_list[i]['isdir'] == 1 else "文件",
                                                           group_dir_list[i]['server_filename']))

                    group_dir_list[i]['save_path'] = sd['path']
                    update_list.append(group_dir_list[i])
                elif group_dir_list[i]['isdir'] == 1:
                    # 如果存在但是是文件夹，而且不属于忽略目录，就添加到待同步目录中进入循环
                    try:
                        ignore_dic[group_dir_list[i]['server_filename']]
                    except KeyError:
                        wait_list.append({
                            "gid": sync_data['gid'],
                            "from_uk": sync_data['from_uk'],
                            "msg_id": sync_data['msg_id'],
                            "fs_ids": [group_dir_list[i]['fs_id']],
                            "path": "{0}/{1}".format(sd['path'], group_dir_list[i]['server_filename']),
                            "sync_dir": group_dir_list[i]['path']
                        })
            if len(file_list)>0:
                delete_list = ["{0}/{1}".format(sd['path'], fl['server_filename']) for fl in file_list]
                if du_util.removeFile(delete_list):
                    file_list = []
                else:
                    print("待删除列表：")
                    print(file_list)
        except BaseException as e:
            logger.error("{}同步出现错误".format(sd['sync_dir']))
            logger.error(e)
            # if sd['retry'] is not None:
            #     sd['retry'] += 1
            # else:
            #     sd['retry'] = 1
            try:
                sd['retry'] += 1
            except (KeyError, ValueError):
                sd['retry'] = 1

            if sd['retry'] < 6:
                wait_list.append(sd)

    return update_list
    # except BaseException as e:
    #     logger.error("{}同步出现错误".format(sync_data['sync_dir']))
    #     logger.error(e)
    #     return []


def syncDir(sync_data, du_util: DuUtil, notices: Notices):
    sync_path = sync_data['sync_dir'].split('/')
    group_root_list = du_util.getGroupRoot(sync_data['gid'])
    temp_fs_id = None
    for grl in group_root_list:
        if grl['file_list'][0]['server_filename'] == sync_path[0]:
            sync_data['msg_id'] = grl['msg_id']
            sync_data['from_uk'] = grl['uk']
            temp_fs_id = grl['file_list'][0]['fs_id']
            break

    page = 1
    page_size = 50
    for sp in sync_path:
        if sp == sync_path[0]:
            continue
        temp_dir = du_util.getGroupDir(group_id=sync_data['gid'], group_uk=sync_data['from_uk'],
                                       msg_id=sync_data['msg_id'], fs_id=temp_fs_id, page=page, num=page_size)
        page = 1
        while len(temp_dir) == page * page_size:
            page += 1
            temp_list = du_util.getGroupDir(group_id=sync_data['gid'], group_uk=sync_data['from_uk'],
                                            msg_id=sync_data['msg_id'], fs_id=temp_fs_id, page=page, num=page_size)
            temp_dir += temp_list if temp_list is not False else []

        for td in temp_dir:
            if td['server_filename'] == sp:
                temp_fs_id = td['fs_id']
                break

    sync_data['fs_ids'] = []
    sync_data['fs_ids'].append(temp_fs_id)

    update_list = getSyncDir(sync_data, du_util)
    logger.success("共发现{}个待更新文件/文件夹".format(len(update_list)))
    logger.info(update_list)
    s = 0
    for item in update_list:
        if du_util.saveDir(sync_data['from_uk'], sync_data['msg_id'], item['save_path'], item['fs_id'],
                           sync_data['gid']):
            notices.addSuccess(item)
            s += 1
        else:
            notices.addFail(item)

    logger.success("{0}同步完成，共更新了{1}个文件/文件夹".format(sync_data['sync_dir'], s))
    print("{0}同步完成，共更新了{1}个文件/文件夹".format(sync_data['sync_dir'], s))


def syncAllDir(du_util: DuUtil):
    notices = Notices()
    try:
        sd = getSyncData()
        if sd == False:
            logger.warning("读取同步文件失败，请检查/temp/sync.json是否存在")
            print("读取同步文件失败，请检查/temp/sync.json是否存在")
            return False

        for d in sd:
            syncDir(d, du_util, notices)
    except BaseException as e:
        logger.error(e)
    finally:
        notices.send()
        notices.send_sub()
