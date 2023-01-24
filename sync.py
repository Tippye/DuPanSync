from loguru import logger

from DuUtil import DuUtil
from syncSetter import getSyncData
from util import Notices


def getSyncDir(sync_data, du_util: DuUtil, page=1, update_list=None):
    if update_list is None:
        update_list = []
    wait_list = []
    group_dir_list = du_util.getGroupDir(sync_data['from_uk'], sync_data['msg_id'], sync_data['fs_ids'][0],
                                         sync_data['gid'], page, 50)
    sp = sync_data['path'].split('/')
    sp.pop(len(sp) - 1)
    # save_path = '/'.join(tuple(sp))
    save_path = sync_data['path']
    file_list = du_util.getFileList(save_path, page=page, num=50)

    for i in range(0, len(group_dir_list)):
        existed = False
        for j in range(0, len(file_list)):
            if group_dir_list[i]['server_filename'] == file_list[j]['server_filename']:
                existed = True
                break
        if not existed:
            group_dir_list[i]['save_path'] = sync_data['path']
            logger.info("发现未保存{0}：{1}".format("目录" if group_dir_list[i]['isdir'] == 1 else "文件", group_dir_list[i]['server_filename']))
            update_list.append(group_dir_list[i])
        elif group_dir_list[i]['isdir'] == 1:
            wait_list.append(group_dir_list[i])

    if len(group_dir_list) >= 50:
        update_list = getSyncDir(sync_data, du_util, page + 1, update_list)

    for w in wait_list:
        update_list += getSyncDir({
            "gid": sync_data['gid'],
            "from_uk": sync_data['from_uk'],
            "msg_id": sync_data['msg_id'],
            "fs_ids": [w['fs_id']],
            "path": "{0}/{1}".format(save_path, w['server_filename'])
        }, du_util)

    return update_list


def syncDir(sync_data, du_util: DuUtil):
    update_list = getSyncDir(sync_data, du_util)
    logger.info("共发现{}个待更新文件/文件夹".format(len(update_list)))
    notices = Notices()
    for item in update_list:
        if du_util.saveDir(sync_data['from_uk'], sync_data['msg_id'], item['save_path'], item['fs_id'],
                           sync_data['gid']):
            notices.addSuccess(item)
        else:
            notices.addFail(item)

    logger.info("{0}同步完成，共更新了{1}个文件/文件夹".format(sync_data['sync_dir'], notices.success_num))
    print("{0}同步完成，共更新了{1}个文件/文件夹".format(sync_data['sync_dir'], notices.success_num))
    notices.send()


def syncAllDir(du_util: DuUtil):
    sd = getSyncData()
    if sd == False:
        logger.warning("读取同步文件失败，请检查/temp/sync.json是否存在")
        print("读取同步文件失败，请检查/temp/sync.json是否存在")
        return False
    for d in sd:
        syncDir(d, du_util)
