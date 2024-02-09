import os
import sys
import time

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QDialog

from mediainfo import get_media_info
from ptgen import fetch_and_format_ptgen_data
from rename import extract_details_from_ptgen, get_video_info
from screenshot import extract_complex_keyframes, upload_screenshot, upload_free_screenshot, get_thumbnails
from tool import update_settings, get_settings, get_file_path, rename_file_with_same_extension, move_file_to_folder, \
    get_folder_path, check_path_and_find_video, rename_directory, create_torrent, load_names
from ui.mainwindow import Ui_Mainwindow
from ui.settings import Ui_Settings


def starui():
    app = QApplication(sys.argv)
    myMainwindow = mainwindow()
    myico = QIcon("static/ph-bjd.ico")
    myMainwindow.setWindowIcon(myico)
    myMainwindow.show()
    sys.exit(app.exec())


class mainwindow(QMainWindow, Ui_Mainwindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 设置界面

        self.get_pt_gen_thread = None
        self.get_pt_gen_for_name_thread = None
        self.upload_picture_thread0 = None
        self.upload_picture_thread1 = None
        self.upload_picture_thread2 = None
        self.upload_picture_thread3 = None
        self.upload_picture_thread4 = None
        self.upload_picture_thread5 = None
        self.upload_free_picture_thread0 = None
        self.upload_free_picture_thread1 = None
        self.upload_free_picture_thread2 = None
        self.upload_free_picture_thread3 = None
        self.upload_free_picture_thread4 = None
        self.upload_free_picture_thread5 = None
        self.make_torrent_thread = None

        # 初始化
        self.videoPath.setDragEnabled(True)
        self.ptGenBrowser.setText("")
        self.pictureUrlBrowser.setText("")
        self.mediainfoBrowser.setText("")
        self.debugBrowser.setText("")
        self.initialize_team_combobox()
        self.initialize_source_combobox()

        # 绑定点击信号和槽函数
        self.actionsettings.triggered.connect(self.settingsClicked)
        self.getPtGenButton.clicked.connect(self.getPtGenButtonClicked)
        self.getPictureButton.clicked.connect(self.getPictureButtonClicked)
        self.selectVideoButton.clicked.connect(self.selectVideoButtonClicked)
        self.selectVideoFolderButton.clicked.connect(self.selectVideoFolderButtonClicked)
        self.getMediaInfoButton.clicked.connect(self.getMediaInfoButtonClicked)
        self.getNameButton.clicked.connect(self.getNameButtonClicked)
        self.startButton.clicked.connect(self.startButtonClicked)
        self.makeTorrentButton.clicked.connect(self.makeTorrentButtonClicked)

        self.debugBrowser.append("程序初始化成功，使用前请查看设置中的说明")

    def initialize_team_combobox(self):
        team_names = load_names('static/team.json', 'team')
        for name in team_names:
            self.team.addItem(name)

    def initialize_source_combobox(self):
        source_names = load_names('static/source.json', 'source')
        for name in source_names:
            self.source.addItem(name)

    def startButtonClicked(self):
        self.getNameButtonClicked()
        QApplication.processEvents()  # 处理所有挂起的事件，更新页面
        time.sleep(0)  # 等待 0 毫秒
        self.getPictureButtonClicked()
        QApplication.processEvents()  # 再次处理事件
        time.sleep(2)  # 等待 2000 毫秒
        self.getMediaInfoButtonClicked()
        QApplication.processEvents()  # 处理事件
        time.sleep(2)  # 等待 2000 毫秒
        self.makeTorrentButtonClicked()
        QApplication.processEvents()  # 处理事件

    def settingsClicked(self):  # click对应的槽函数
        self.mySettings = settings()
        self.mySettings.getSettings()
        myico = QIcon("static/ph-bjd.ico")
        self.mySettings.setWindowIcon(myico)
        self.mySettings.show()  # 加上self避免页面一闪而过

    def getPtGenButtonClicked(self):
        self.ptGenBrowser.setText("")
        ptGenPath = get_settings("ptGenPath")
        ptGenUrl = self.ptGenUrl.text()

        if ptGenUrl == "":
            self.debugBrowser.append("请输入输入豆瓣号、Imdb号、豆瓣、IMDb等资源链接")
            return
        if ptGenPath == "":
            self.debugBrowser.append("请在设置中输入Pt-Gen链接")
            return
        print("尝试启动pt_gen_thread")
        self.get_pt_gen_thread = GetPtGenThread(ptGenPath, ptGenUrl)
        self.get_pt_gen_thread.result_signal.connect(self.handleGetPtGenResult)  # 连接信号
        self.get_pt_gen_thread.start()  # 启动线程
        print("启动pt_gen_thread成功")

    def handleGetPtGenResult(self, get_success, response):
        if get_success:
            if response:
                print(response)
                self.ptGenBrowser.setText(response)
                self.debugBrowser.append("成功获取Pt-Gen信息")
            else:
                self.debugBrowser.append("获取Pt-Gen信息失败")
        else:
            self.debugBrowser.append("未成功获取到任何Pt-Gen信息" + response)

    def getPictureButtonClicked(self):
        self.pictureUrlBrowser.setText("")
        isVideoPath, videoPath = check_path_and_find_video(self.videoPath.text())  # 视频资源的路径

        if isVideoPath == 1 or isVideoPath == 2:
            self.debugBrowser.append("获取视频" + videoPath + "的截图")
            screenshotPath = get_settings("screenshotPath")  # 截图储存路径
            figureBedPath = get_settings("figureBedPath")  # 图床地址
            figureBedToken = get_settings("figureBedToken")  # 图床Token
            screenshotNumber = int(get_settings("screenshotNumber"))
            screenshotThreshold = float(get_settings("screenshotThreshold"))
            screenshotStart = float(get_settings("screenshotStart"))
            screenshotEnd = float(get_settings("screenshotEnd"))
            getThumbnails = bool(get_settings("getThumbnails"))
            rows = int(get_settings("rows"))
            cols = int(get_settings("cols"))
            autoUploadScreenshot = bool(get_settings("autoUploadScreenshot"))
            self.debugBrowser.append("参数获取成功，开始执行截图函数")

            screenshot_success, res = extract_complex_keyframes(videoPath, screenshotPath, screenshotNumber,
                                                                screenshotThreshold, screenshotStart,
                                                                screenshotEnd, min_interval_pct=0.01)
            print("成功获取截图函数的返回值")
            self.debugBrowser.append("成功获取截图函数的返回值")
            if getThumbnails:
                get_thumbnails_success, sv_path = get_thumbnails(videoPath, screenshotPath, rows, cols, screenshotStart,
                                                                 screenshotEnd)
                if get_thumbnails_success:
                    res.append(sv_path)
            self.debugBrowser.append("成功获取截图：" + str(res))
            if screenshot_success:
                # 判断是否需要上传图床
                if autoUploadScreenshot:
                    self.debugBrowser.append("开始自动上传截图到图床" + figureBedPath)
                    self.pictureUrlBrowser.setText("")
                    if figureBedPath == "https://img.agsvpt.com/api/upload/" or figureBedPath == "http://img.agsvpt.com/api/upload/":
                        if len(res) > 0:
                            self.upload_picture_thread0 = UploadPictureThread(figureBedPath, figureBedToken, res[0])
                            self.upload_picture_thread0.result_signal.connect(self.handleUploadPictureResult)  # 连接信号
                            self.upload_picture_thread0.start()  # 启动线程
                        if len(res) > 1:
                            self.upload_picture_thread1 = UploadPictureThread(figureBedPath, figureBedToken, res[1])
                            self.upload_picture_thread1.result_signal.connect(self.handleUploadPictureResult)  # 连接信号
                            self.upload_picture_thread1.start()  # 启动线程
                        if len(res) > 2:
                            self.upload_picture_thread2 = UploadPictureThread(figureBedPath, figureBedToken, res[2])
                            self.upload_picture_thread2.result_signal.connect(self.handleUploadPictureResult)  # 连接信号
                            self.upload_picture_thread2.start()  # 启动线程
                        if len(res) > 3:
                            self.upload_picture_thread3 = UploadPictureThread(figureBedPath, figureBedToken, res[3])
                            self.upload_picture_thread3.result_signal.connect(self.handleUploadPictureResult)  # 连接信号
                            self.upload_picture_thread3.start()  # 启动线程
                        if len(res) > 4:
                            self.upload_picture_thread4 = UploadPictureThread(figureBedPath, figureBedToken, res[4])
                            self.upload_picture_thread4.result_signal.connect(self.handleUploadPictureResult)  # 连接信号
                            self.upload_picture_thread4.start()  # 启动线程
                        if len(res) > 5:
                            self.upload_picture_thread5 = UploadPictureThread(figureBedPath, figureBedToken, res[5],
                                                                              False)
                            self.upload_picture_thread5.result_signal.connect(self.handleUploadPictureResult)  # 连接信号
                            self.upload_picture_thread5.start()  # 启动线程
                        print("上传图床线程启动")
                        self.debugBrowser.append("上传图床线程启动")
                    else:
                        if len(res) > 0:
                            self.upload_free_picture_thread0 = UploadFreePictureThread(figureBedPath, figureBedToken,
                                                                                       res[0])
                            self.upload_free_picture_thread0.result_signal.connect(
                                self.handleUploadFreePictureResult)  # 连接信号
                            self.upload_free_picture_thread0.start()  # 启动线程
                        if len(res) > 1:
                            self.upload_free_picture_thread1 = UploadFreePictureThread(figureBedPath, figureBedToken,
                                                                                       res[1])
                            self.upload_free_picture_thread1.result_signal.connect(
                                self.handleUploadFreePictureResult)  # 连接信号
                            self.upload_free_picture_thread1.start()  # 启动线程
                        if len(res) > 2:
                            self.upload_free_picture_thread2 = UploadFreePictureThread(figureBedPath, figureBedToken,
                                                                                       res[2])
                            self.upload_free_picture_thread2.result_signal.connect(
                                self.handleUploadFreePictureResult)  # 连接信号
                            self.upload_free_picture_thread2.start()  # 启动线程
                        if len(res) > 3:
                            self.upload_free_picture_thread3 = UploadFreePictureThread(figureBedPath, figureBedToken,
                                                                                       res[3])
                            self.upload_free_picture_thread3.result_signal.connect(
                                self.handleUploadFreePictureResult)  # 连接信号
                            self.upload_free_picture_thread3.start()  # 启动线程
                        if len(res) > 4:
                            self.upload_free_picture_thread4 = UploadFreePictureThread(figureBedPath, figureBedToken,
                                                                                       res[4])
                            self.upload_free_picture_thread4.result_signal.connect(
                                self.handleUploadFreePictureResult)  # 连接信号
                            self.upload_free_picture_thread4.start()  # 启动线程
                        if len(res) > 5:
                            self.upload_free_picture_thread5 = UploadFreePictureThread(figureBedPath, figureBedToken,
                                                                                       res[5], False)
                            self.upload_free_picture_thread5.result_signal.connect(
                                self.handleUploadFreePictureResult)  # 连接信号
                            self.upload_free_picture_thread5.start()  # 启动线程
                        print("上传图床线程启动")
                        self.debugBrowser.append("上传图床线程启动")
                else:
                    self.debugBrowser.append("未选择自动上传图床功能，图片已储存在本地")
                    output = ""
                    for r in res:
                        output += r
                        output += '\n'
                    self.pictureUrlBrowser.setText(output)
            else:
                self.debugBrowser.append("截图失败" + str(res))
        else:
            self.debugBrowser.append("您的视频文件路径有误")

    def handleUploadPictureResult(self, upload_success, api_response, screenshot_path):
        # 这个函数用于处理上传的结果，它将在主线程中被调用
        # 更新UI，显示上传结果等
        print("接受到线程请求的结果")
        self.debugBrowser.append("接受到线程请求的结果")
        if upload_success:
            if api_response.get("statusCode", "") == "200":
                pasteScreenshotUrl = bool(get_settings("pasteScreenshotUrl"))
                deleteScreenshot = bool(get_settings("deleteScreenshot"))
                bbsurl = str(api_response.get("bbsurl", ""))
                self.pictureUrlBrowser.append(bbsurl)
                if pasteScreenshotUrl:
                    self.ptGenBrowser.append(bbsurl)
                    self.debugBrowser.append("成功将图片链接粘贴到简介后")
                if deleteScreenshot:
                    if os.path.exists(screenshot_path):
                        # 删除文件
                        os.remove(screenshot_path)
                        print(f"文件 {screenshot_path} 已被删除。")
                        self.debugBrowser.append(f"文件 {screenshot_path} 已被删除。")
                    else:
                        print(f"文件 {screenshot_path} 不存在。")
                        self.debugBrowser.append(f"文件 {screenshot_path} 不存在。")
            else:
                if api_response.get("statusCode", "") == "":
                    self.debugBrowser.append("未接受到图床的任何响应" + '\n')
                else:
                    self.debugBrowser.append(str(api_response) + '\n')

        else:
            self.debugBrowser.append("图床响应不是有效的JSON格式")

    def handleUploadFreePictureResult(self, upload_success, api_response, screenshot_path):
        # 这个函数用于处理上传的结果，它将在主线程中被调用
        # 更新UI，显示上传结果等
        print("接受到线程请求的结果")
        self.debugBrowser.append("接受到线程请求的结果")
        if upload_success:
            self.pictureUrlBrowser.append(api_response)
            pasteScreenshotUrl = bool(get_settings("pasteScreenshotUrl"))
            deleteScreenshot = bool(get_settings("deleteScreenshot"))
            if pasteScreenshotUrl:
                self.ptGenBrowser.append(api_response)
                self.debugBrowser.append("成功将图片链接粘贴到简介后")
            if deleteScreenshot:
                if os.path.exists(screenshot_path):
                    # 删除文件
                    os.remove(screenshot_path)
                    print(f"文件 {screenshot_path} 已被删除。")
                    self.debugBrowser.append(f"文件 {screenshot_path} 已被删除。")
                else:
                    print(f"文件 {screenshot_path} 不存在。")
                    self.debugBrowser.append(f"文件 {screenshot_path} 不存在。")
        else:
            self.debugBrowser.append("图床响应无效：" + api_response)

    def selectVideoButtonClicked(self):
        path = get_file_path()
        self.videoPath.setText(path)

    def selectVideoFolderButtonClicked(self):
        path = get_folder_path()
        self.videoPath.setText(path)

    def getMediaInfoButtonClicked(self):
        self.mediainfoBrowser.setText("")
        isVideoPath, videoPath = check_path_and_find_video(self.videoPath.text())  # 视频资源的路径
        if isVideoPath == 1 or isVideoPath == 2:
            get_media_info_success, mediainfo = get_media_info(videoPath)
            if get_media_info_success:
                self.mediainfoBrowser.setText(mediainfo)
                self.mediainfoBrowser.append('\n')
                self.debugBrowser.append("成功获取到MediaInfo")
            else:
                self.debugBrowser.append(mediainfo)
        else:
            self.debugBrowser.append("您的视频文件路径有误")

    def getNameButtonClicked(self):
        self.ptGenBrowser.setText("")
        ptGenPath = get_settings("ptGenPath")
        ptGenUrl = self.ptGenUrl.text()

        if ptGenUrl == "":
            self.debugBrowser.append("请输入输入豆瓣号、Imdb号、豆瓣、IMDb等资源链接")
            return
        if ptGenPath == "":
            self.debugBrowser.append("请在设置中输入Pt-Gen链接")
            return
        print("尝试启动pt_gen_thread")
        self.debugBrowser.append("尝试启动pt_gen_thread")
        self.get_pt_gen_for_name_thread = GetPtGenThread(ptGenPath, ptGenUrl)
        self.get_pt_gen_for_name_thread.result_signal.connect(self.handleGetPtGenForNameResult)  # 连接信号
        self.get_pt_gen_for_name_thread.start()  # 启动线程
        print("启动pt_gen_thread成功")
        self.debugBrowser.append("启动pt_gen_thread成功")

    def handleGetPtGenForNameResult(self, get_success, response):
        if get_success:
            self.ptGenBrowser.setText(response)
            if response:
                print(response)
                self.debugBrowser.append("成功获取Pt-Gen信息")
            else:
                self.debugBrowser.append("获取Pt-Gen信息失败")
            first_chinese_name = ""
            first_english_name = ""
            year = ""
            width = ""
            format = ""
            hdr_format = ""
            commercial_name = ""
            channel_layout = ""
            other_names = ""
            category = ""
            actors = ""
            make_dir = get_settings("makeDir")
            rename_file = get_settings("renameFile")
            isVideoPath, videoPath = check_path_and_find_video(self.videoPath.text())
            if isVideoPath == 1 or isVideoPath == 2:
                print("重命名初始化完成")
                self.debugBrowser.append("重命名初始化完成")
                if response == "":
                    print("未获取到ptgen")
                    self.debugBrowser.append("未获取到ptgen")
                else:
                    print("开始获取ptgen关键信息")
                    self.debugBrowser.append("开始获取ptgen关键信息")
                    first_chinese_name, first_english_name, year, other_names_sorted, category, actors_list = extract_details_from_ptgen(
                        response)
                    print(first_chinese_name, first_english_name, year, other_names_sorted, category, actors_list)
                    print("获取ptgen关键信息成功")
                    self.debugBrowser.append("获取ptgen关键信息成功")
                    is_first = True
                    for data in actors_list:  # 把演员名转化成str
                        if is_first:
                            actors += data
                            is_first = False
                        else:
                            actors += ' / '
                            actors += data

                    for data in other_names_sorted:  # 把别名转化为str
                        other_names += ' / '
                        other_names += data

                get_video_info_success, output = get_video_info(videoPath)
                print("获取到关键参数：" + str(output))
                self.debugBrowser.append("获取到关键参数：" + str(output))
                if get_video_info_success:
                    width = output[0]
                    format = output[1]
                    hdr_format = output[2]
                    commercial_name = output[3]
                    channel_layout = output[4]
                source = self.source.currentText()
                team = self.team.currentText()
                print("关键参数赋值成功")
                self.debugBrowser.append("关键参数赋值成功")
                # print(first_english_name)
                # print(year)
                # print(width)
                # print(source)
                # print(format)
                # print(hdr_format)
                # print(commercial_name)
                # print(channel_layout)
                # print(team)
                mainTitle = first_english_name + ' ' + year + ' ' + width + ' ' + source + ' ' + format + ' ' + hdr_format + ' ' + commercial_name + ' ' + channel_layout + '-' + team
                mainTitle = mainTitle.replace('_', ' ')
                mainTitle = mainTitle.replace('  ', ' ')
                mainTitle = mainTitle.replace('  ', ' ')
                print("MainTitle" + mainTitle)
                secondTitle = (first_chinese_name + other_names + ' | 类型：' + category + ' | 主演：' + actors)
                print("SecondTitle" + secondTitle)
                fileName = (
                        first_chinese_name + '.' + first_english_name + '.' + year + '.' + width + '.' + source + '.' +
                        format + '.' + hdr_format + '.' + commercial_name + '.' + channel_layout + '-' + team)
                fileName = fileName.replace(' – ', '.')
                fileName = fileName.replace(' - ', '.')
                fileName = fileName.replace('_', '.')
                fileName = fileName.replace(': ', '.')
                fileName = fileName.replace(' ', '.')
                fileName = fileName.replace('..', '.')
                print("FileName" + fileName)
                self.mainTitleBrowser.setText(mainTitle)
                self.secondTitleBrowser.setText(secondTitle)
                self.fileNameBrowser.setText(fileName)
                if make_dir and isVideoPath == 1:
                    print("开始创建文件夹")
                    self.debugBrowser.append("开始创建文件夹")
                    move_file_to_folder_success, output = move_file_to_folder(videoPath, fileName)
                    if move_file_to_folder_success:
                        self.videoPath.setText(output)
                        videoPath = output
                        self.debugBrowser.append("视频成功移动到：" + videoPath)
                    else:
                        self.debugBrowser.append("创建文件夹失败：" + output)
                if rename_file and isVideoPath == 1:
                    print("开始对文件重新命名")
                    self.debugBrowser.append("开始对文件重新命名")
                    rename_file_success, output = rename_file_with_same_extension(videoPath, fileName)
                    if rename_file_success:
                        self.videoPath.setText(output)
                        videoPath = output
                        self.debugBrowser.append("视频成功重新命名为：" + videoPath)
                    else:
                        self.debugBrowser.append("重命名失败：" + output)
                if rename_file and isVideoPath == 2:
                    print("对文件夹重新命名")
                    self.debugBrowser.append("开始对文件夹重新命名")
                    rename_directory_success, output = rename_directory(os.path.dirname(videoPath), fileName)
                    if rename_directory_success:
                        self.videoPath.setText(output)
                        videoPath = output
                        self.debugBrowser.append("视频地址成功重新命名为：" + videoPath)
                    else:
                        self.debugBrowser.append("重命名失败：" + output)

            else:
                self.debugBrowser.append("您的视频文件路径有误")
        else:
            self.debugBrowser.append("未成功获取到任何Pt-Gen信息：" + response)

    def makeTorrentButtonClicked(self):
        isVideoPath, videoPath = check_path_and_find_video(self.videoPath.text())  # 视频资源的路径
        if isVideoPath == 1 or isVideoPath == 2:
            torrent_path = str(get_settings("torrentPath"))
            folder_path = os.path.dirname(videoPath)
            self.debugBrowser.append("开始将" + folder_path + "制作种子，储存在" + torrent_path)
            self.make_torrent_thread = MakeTorrentThread(folder_path, torrent_path)
            self.make_torrent_thread.result_signal.connect(self.handleMakeTorrentResult)  # 连接信号
            self.make_torrent_thread.start()  # 启动线程
            self.debugBrowser.append("制作种子线程启动成功")
        else:
            self.debugBrowser.append("制作种子失败：" + videoPath)

    def handleMakeTorrentResult(self, get_success, response):
        if get_success:
            self.debugBrowser.append("成功制作种子：" + response)
        else:
            self.debugBrowser.append("制作种子失败：" + response)


class settings(QDialog, Ui_Settings):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 设置界面

        # 绑定点击信号和槽函数
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        self.selectScreenshotPathButton.clicked.connect(self.selectScreenshotPathButtonClicked)
        self.selectTorrentPathButton.clicked.connect(self.selectTorrentPathButtonClicked)

    def saveButtonClicked(self):
        self.updateSettings()
        self.close()

    def cancelButtonClicked(self):
        self.close()

    def selectScreenshotPathButtonClicked(self):
        path = get_folder_path()
        if path != '':
            self.screenshotPath.setText(path)

    def selectTorrentPathButtonClicked(self):
        path = get_folder_path()
        if path != '':
            self.torrentPath.setText(path)

    def getSettings(self):
        self.screenshotPath.setText(str(get_settings("screenshotPath")))
        self.torrentPath.setText(str(get_settings("torrentPath")))
        self.ptGenPath.setText(get_settings("ptGenPath"))
        self.figureBedPath.setText(get_settings("figureBedPath"))
        self.figureBedToken.setText(get_settings("figureBedToken"))
        self.screenshotNumber.setValue(int(get_settings("screenshotNumber")))
        self.screenshotThreshold.setValue(float(get_settings("screenshotThreshold")))
        self.screenshotStart.setValue(float(get_settings("screenshotStart")))
        self.screenshotEnd.setValue(float(get_settings("screenshotEnd")))
        self.getThumbnails.setChecked(bool(get_settings("getThumbnails")))
        self.rows.setValue(int(get_settings("rows")))
        self.cols.setValue(int(get_settings("cols")))
        self.autoUploadScreenshot.setChecked(bool(get_settings("autoUploadScreenshot")))
        self.pasteScreenshotUrl.setChecked(bool(get_settings("pasteScreenshotUrl")))
        self.deleteScreenshot.setChecked(bool(get_settings("deleteScreenshot")))
        self.makeDir.setChecked(bool(get_settings("makeDir")))
        self.renameFile.setChecked(bool(get_settings("renameFile")))

    def updateSettings(self):
        update_settings("screenshotPath", self.screenshotPath.text())
        update_settings("torrentPath", self.torrentPath.text())
        update_settings("ptGenPath", self.ptGenPath.text())
        update_settings("figureBedPath", self.figureBedPath.text())
        update_settings("figureBedToken", self.figureBedToken.text())
        update_settings("screenshotNumber", str(self.screenshotNumber.text()))
        update_settings("screenshotThreshold", str(self.screenshotThreshold.text()))
        update_settings("screenshotStart", str(self.screenshotStart.text()))
        update_settings("screenshotEnd", str(self.screenshotEnd.text()))
        if self.getThumbnails.isChecked():
            update_settings("getThumbnails", "True")
        else:
            update_settings("getThumbnails", "")
        update_settings("rows", str(self.rows.text()))
        update_settings("cols", str(self.cols.text()))
        if self.autoUploadScreenshot.isChecked():
            update_settings("autoUploadScreenshot", "True")
        else:
            update_settings("autoUploadScreenshot", "")
        if self.pasteScreenshotUrl.isChecked():
            update_settings("pasteScreenshotUrl", "True")
        else:
            update_settings("pasteScreenshotUrl", "")
        if self.deleteScreenshot.isChecked():
            update_settings("deleteScreenshot", "True")
        else:
            update_settings("deleteScreenshot", "")
        if self.makeDir.isChecked():
            update_settings("makeDir", "True")
        else:
            update_settings("makeDir", "")
        if self.renameFile.isChecked():
            update_settings("renameFile", "True")
        else:
            update_settings("renameFile", "")


class GetPtGenThread(QThread):
    # 创建一个信号，用于在数据处理完毕后与主线程通信
    result_signal = pyqtSignal(bool, str)

    def __init__(self, api_url, resource_url):
        super().__init__()
        self.api_url = api_url
        self.resource_url = resource_url

    def run(self):
        try:
            # 这里放置耗时的HTTP请求操作
            get_success, response = fetch_and_format_ptgen_data(self.api_url, self.resource_url)

            # 发送信号，包括请求的结果
            print("Pt-Gen请求成功，开始返回结果")
            self.result_signal.emit(get_success, response)
            print("返回结果成功")
            # self.result_signal(upload_success,api_response)
        except Exception as e:
            print(f"异常发生: {e}")
            # 这里可以发射一个包含错误信息的信号


class UploadPictureThread(QThread):
    # 创建一个信号，用于在数据处理完毕后与主线程通信
    result_signal = pyqtSignal(bool, dict, str)

    def __init__(self, figureBedPath, figureBedToken, screenshot_path):
        super().__init__()
        self.figureBedPath = figureBedPath
        self.figureBedToken = figureBedToken
        self.screenshot_path = screenshot_path

    def run(self):
        try:
            # 这里放置耗时的HTTP请求操作
            upload_success, api_response = upload_screenshot(self.figureBedPath, self.figureBedToken,
                                                             self.screenshot_path)

            # 发送信号，包括请求的结果
            print("上传图床成功，开始返回结果")
            self.result_signal.emit(upload_success, api_response, self.screenshot_path)
            print("返回结果成功")
            # self.result_signal(upload_success,api_response)
        except Exception as e:
            print(f"异常发生: {e}")
            self.result_signal.emit(False, f"异常发生: {e}", self.screenshot_path)
            # 这里可以发射一个包含错误信息的信号


class UploadFreePictureThread(QThread):
    # 创建一个信号，用于在数据处理完毕后与主线程通信
    result_signal = pyqtSignal(bool, str, str)

    def __init__(self, figureBedPath, figureBedToken, screenshot_path):
        super().__init__()
        self.figureBedPath = figureBedPath
        self.figureBedToken = figureBedToken
        self.screenshot_path = screenshot_path

    def run(self):
        try:
            # 这里放置耗时的HTTP请求操作
            upload_success, api_response = upload_free_screenshot(self.figureBedPath, self.figureBedToken,
                                                                  self.screenshot_path)

            # 发送信号，包括请求的结果
            print("上传图床成功，开始返回结果")
            self.result_signal.emit(upload_success, api_response, self.screenshot_path)
            print("返回结果成功")
            # self.result_signal(upload_success,api_response)
        except Exception as e:
            print(f"异常发生: {e}")
            self.result_signal.emit(False, f"异常发生: {e}", self.screenshot_path)
            # 这里可以发射一个包含错误信息的信号


class MakeTorrentThread(QThread):
    # 创建一个信号，用于在数据处理完毕后与主线程通信
    result_signal = pyqtSignal(bool, str)

    def __init__(self, folder_path, torrent_path):
        super().__init__()
        self.folder_path = folder_path
        self.torrent_path = torrent_path

    def run(self):
        try:
            # 这里放置耗时的制作torrent操作
            get_success, response = create_torrent(self.folder_path, self.torrent_path)

            # 发送信号
            print("Torrent请求成功，开始等待返回结果")
            self.result_signal.emit(get_success, response)
            print("返回结果成功")
            # self.result_signal(upload_success,api_response)
        except Exception as e:
            print(f"异常发生: {e}")
            # 这里可以发射一个包含错误信息的信号
