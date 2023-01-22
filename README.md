# 度盘群文件同步工具

本程序所有操作均基于百度网盘web端API操作

## 使用条件

1. 由于程序使用到了`selenium`技术，所以需要系统安装Chrome浏览器，同时项目根目录中的`chromedriver`文件需要与Chrome版本对应，可以在[官方网站](http://chromedriver.storage.googleapis.com/index.html)或[阿里云镜像](https://registry.npmmirror.com/binary.html?path=chromedriver/)下载
2. 安装有`python3`环境，作者使用的python3.9环境
3. 会看本文档

## 使用方法

1. 把本项目拉到本地
2. 安装对应版本的chromedriver
   - 本项目使用的是macOS版Chrome 109.0.5414.87适配的chromedriver
3. 安装相关库
   ```shell
    pip install -r requirements.txt
    ```
4. 运行`main.py`
   ```shell
   # 有些人可能是python3 main.py
   python main.py
    ```
5. 根据命令行中的提示进行选择（主要懒得再做个页面）
6. 第一次登录时如果扫不了控制台的二维码就去扫保存到本地的二维码图片
   - 默认地址在`/temp/login.png`
   - `config.json`里的`qrCodeImagePath`可以改默认保存地址
7. 设置好后可以使用下面的命令直接执行同步方法，不显示操作菜单
   ```shell
   python -c "from main import shellSync;shellSync()"
   ```
   - 使用此命令可以方便的设置crontab，iOS快捷指令的SSH模块等方式进行操作

# TODO
- [x] 同步（现在只能设置同步的目录，设置时会自动保存一次）
- [ ] 定时任务自动执行
- [ ] 新文件同步提醒
- [ ] iOS快捷指令（或许会做）
