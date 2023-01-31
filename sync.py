from loguru import logger

from DuUtil import DuUtil
from syncSetter import getSyncData
from util import Notices, getConfig


def getSyncDir(sync_data, du_util: DuUtil, update_list=None):
    logger.info("正在同步：{}".format(sync_data['path']))
    print("正在同步：{}".format(sync_data['path']))
    if update_list is None:
        update_list = []
    wait_list = []
    page = 1
    page_size = 50
    ignore_dir = getConfig()["ignore"]
    sync_path = sync_data['sync_dir'].split('/')
    group_root_list = du_util.getGroupRoot(sync_data['gid'])
    temp_fs_id = None
    for grl in group_root_list:
        if grl['file_list'][0]['server_filename'] == sync_path[0]:
            sync_data['msg_id'] = grl['msg_id']
            sync_data['from_uk'] = grl['uk']
            temp_fs_id = grl['file_list'][0]['fs_id']
            break

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

    group_dir_list = du_util.getGroupDir(sync_data['from_uk'], sync_data['msg_id'], sync_data['fs_ids'][0],
                                         sync_data['gid'], page, page_size)
    if group_dir_list == False:
        print("文件夹{}已不存在".format(sync_data['sync_dir']))
        return []
    page = 1
    while len(group_dir_list) == page * page_size:
        page += 1
        temp_list = du_util.getGroupDir(sync_data['from_uk'], sync_data['msg_id'], sync_data['fs_ids'][0],
                                        sync_data['gid'], page, page_size)
        group_dir_list += temp_list if temp_list is not False else []
    # sp = sync_data['path'].split('/')
    # sp.pop(len(sp) - 1)
    # save_path = '/'.join(tuple(sp))
    save_path = sync_data['path']
    page = 1
    file_list = du_util.getFileList(save_path, page=page, num=page_size, order="name")
    while len(file_list) == page * page_size:
        page += 1
        temp_list = du_util.getFileList(save_path, page=page, num=page_size, order="name")
        file_list += temp_list if temp_list is not False else []
    for i in range(0, len(group_dir_list)):
        existed = False
        for j in range(0, len(file_list)):
            if group_dir_list[i]['server_filename'] == file_list[j]['server_filename']:
                file_list.pop(j)
                existed = True
                break
        if not existed:
            group_dir_list[i]['save_path'] = sync_data['path']
            logger.info("发现未保存{0}：{1}".format("目录" if group_dir_list[i]['isdir'] == 1 else "文件",
                                                   group_dir_list[i]['server_filename']))
            update_list.append(group_dir_list[i])
        elif group_dir_list[i]['isdir'] == 1:
            ig = False
            for ignore in ignore_dir:
                if group_dir_list[i]['server_filename'] == ignore:
                    ig = True
                    break
            if not ig:
                wait_list.append(group_dir_list[i])

    for w in wait_list:
        update_list += getSyncDir({
            "gid": sync_data['gid'],
            "from_uk": sync_data['from_uk'],
            "msg_id": sync_data['msg_id'],
            "fs_ids": [w['fs_id']],
            "path": "{0}/{1}".format(save_path, w['server_filename']),
            "sync_dir": w['path']
        }, du_util)

    return update_list


def syncDir(sync_data, du_util: DuUtil, notices: Notices):
    update_list = getSyncDir(sync_data, du_util)
    logger.info("共发现{}个待更新文件/文件夹".format(len(update_list)))
    s = 0
    for item in update_list:
        if du_util.saveDir(sync_data['from_uk'], sync_data['msg_id'], item['save_path'], item['fs_id'],
                           sync_data['gid']):
            notices.addSuccess(item)
            s += 1
        else:
            notices.addFail(item)

    logger.info("{0}同步完成，共更新了{1}个文件/文件夹".format(sync_data['sync_dir'], s))
    print("{0}同步完成，共更新了{1}个文件/文件夹".format(sync_data['sync_dir'], s))


def syncAllDir(du_util: DuUtil):
    sd = getSyncData()
    if sd == False:
        logger.warning("读取同步文件失败，请检查/temp/sync.json是否存在")
        print("读取同步文件失败，请检查/temp/sync.json是否存在")
        return False
    notices = Notices()

    for d in sd:
        syncDir(d, du_util, notices)

    notices.send()
    notices.send_sub()
