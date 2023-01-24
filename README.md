# 度盘群文件同步工具

本程序所有操作均基于百度网盘web端API操作

## 使用条件

1. 由于程序使用到了`selenium`技术，所以需要系统安装Chrome浏览器，同时项目根目录中的`chromedriver`文件需要与Chrome版本对应，可以在[官方网站](http://chromedriver.storage.googleapis.com/index.html)或[阿里云镜像](https://registry.npmmirror.com/binary.html?path=chromedriver/)下载
2. 安装有`python3`环境，作者使用的python3.9环境
3. 会看本文档

## 使用方法

### 电脑(macOS/Windows)

1. 把本项目拉到本地
2. 安装对应版本的chromedriver
   - 本项目使用的是macOS版Chrome 109.0.5414.87适配的chromedriver
3. 安装相关库
   ```shell
    pip install -r requirements.txt
    ```
4. 设置通知
   - 修改位置为[config.json](./config.json)
   - 邮箱密码是在对应邮箱设置里申请的授权码
5. 运行`main.py`
   ```shell
   # 有些人可能是python3 main.py
   python main.py
    ```
6. 根据命令行中的提示进行选择（主要懒得再做个页面）
7. 第一次登录时如果扫不了控制台的二维码就去扫保存到本地的二维码图片
   - 默认地址在`/temp/login.png`
   - `config.json`里的`qrCodeImagePath`可以改默认保存地址
8. 设置好后可以使用下面的命令直接执行同步方法，不显示操作菜单
   ```shell
   python -c "from main import shellSync;shellSync()"
   ```
   - 使用此命令可以方便的设置crontab，iOS快捷指令的SSH模块等方式进行操作

### 树莓派(arm64架构的Ubuntu系统)

1. ssh连接树莓派
2. 把项目放到本地（也可以直接用ftp, smb, sftp等方式直接复制过去）
   ```shell
   git clone https://gitee.com/tippy_q/du-pan-sync.git
   ```

3. 配置树莓派selenium环境
   1. 下载安装包, 作者这里使用的是`90.0.4430.72`版本，可以到[Launchpad.net](http://ports.ubuntu.com/pool/universe/c/chromium-browser/)查找下载其他版本，需要注意这三个版本号一定要一致
      ```shell
      # 下载chromium-browser
      wget 'http://ports.ubuntu.com/pool/universe/c/chromium-browser/chromium-browser_90.0.4430.72-0ubuntu0.16.04.1_arm64.deb'
      # 下载chromium-codecs-ffmpeg-extra
      wget 'http://ports.ubuntu.com/pool/universe/c/chromium-browser/chromium-codecs-ffmpeg-extra_90.0.4630.72-0ubuntu0.16.04.1_arm64.deb'
      # 下载chromium-chromedriver
      wget 'http://ports.ubuntu.com/pool/universe/c/chromium-browser/chromium-chromedriver_90.0.4430.72-0ubuntu0.16.04.1_arm64.deb'
      ```
      
   2. 安装，顺序是`chromium-codecs-ffmpeg-extra`–>`chromium-browser`->`chromium-chromedriver`
      ```shell
      # chromium-codecs-ffmpeg-extra
      sudo dpkg -i chromium-codecs-ffmpeg-extra_90.0.4430.72-0ubuntu0.16.04.1_arm64.deb
      # chromium-browser
      sudo dpkg -i chromium-browser_90.0.4430.72-0ubuntu0.16.04.1_arm64.deb
      # chromium-chromedriver
      sudo dpkg -i chromium-chromedriver_90.0.4430.72-0ubuntu0.16.04.1_arm64.deb
      ```
      
   3. 更新`apt`包管理器，可以忽略这步，我更新时树莓派卡死就直接跳过了
      ```shell
      sudo apt update
      sudo apt upgrade
      ```
      
   4. 验证,只要出来版本号了就算成功了
      ```shell
      # 查看chromedriver版本
      chromedriver -v
      # 查看chromium版本
      chromium-browser -version
      ```
   5. 树莓派selenium教程参考[树莓派安装高版本Chromium和Chromedriver](https://blog.csdn.net/weixin_43890033/article/details/122313492)
4. 进入项目文件夹
   ```shell
   cd du-pan-sync
   ```
5. 安装python包
   ```shell
   pip install -r requirements.txt
   ```

6. 执行程序
   ```shell
   python main.py
   ```

7. 如果需要直接执行更新命令或者设置`crontab`可以使用下面的命令
   - `cd`后面的路径是自己项目存放的路径 
   ```shell
   cd /home/pi/du-pan-sync && python -c "from main import shellSync;shellSync()"
   ```
   
8. 如果出现报错是`Permission denied`开头的，请给项目文件夹下所有文件权限,最后面是项目路径
   ```shell
   sudo chmod -R 777 ./du-pan-sync
   ```
# TODO
- [x] 同步（现在只能设置同步的目录，设置时会自动保存一次）
- [ ] 定时任务自动执行
- [x] 新文件同步提醒
- [ ] iOS快捷指令（或许会做）
