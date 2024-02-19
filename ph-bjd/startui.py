import os
import sys
import time

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QDialog

from ficturebed import upload_screenshot
from mediainfo import get_media_info
from ptgen import fetch_and_format_ptgen_data
from rename import extract_details_from_ptgen, get_video_info
from screenshot import extract_complex_keyframes, get_thumbnail
from tool import update_settings, get_settings, get_file_path, rename_file_with_same_extension, move_file_to_folder, \
    get_folder_path, check_path_and_find_video, rename_directory, create_torrent, load_names
from ui.mainwindow import Ui_Mainwindow
from ui.settings import Ui_Settings


def start_ui():
    app = QApplication(sys.argv)
    my_mainwindow = mainwindow()
    my_ico = QIcon("static/ph-bjd.ico")
    my_mainwindow.setWindowIcon(my_ico)
    my_mainwindow.show()
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
        self.make_torrent_thread = None

        # 初始化
        self.videoPathMovie.setDragEnabled(True)
        self.ptGenBrowserMovie.setText("")
        self.pictureUrlBrowserMovie.setText("")
        self.mediainfoBrowserMovie.setText("")
        self.debugBrowserMovie.setText("")
        self.initialize_team_combobox()
        self.initialize_source_combobox()
        self.initialize_type_combobox()

        # 绑定点击信号和槽函数
        self.actionsettings.triggered.connect(self.settings_clicked)
        self.getPtGenButtonMovie.clicked.connect(self.get_pt_gen_button_movie_clicked)
        self.getPictureButtonMovie.clicked.connect(self.get_picture_button_movie_clicked)
        self.selectVideoButtonMovie.clicked.connect(self.select_video_button_movie_clicked)
        self.selectVideoFolderButtonMovie.clicked.connect(self.select_video_folder_button_movie_clicked)
        self.getMediaInfoButtonMovie.clicked.connect(self.get_media_info_button_movie_clicked)
        self.getNameButtonMovie.clicked.connect(self.get_name_button_movie_clicked)
        self.startButtonMovie.clicked.connect(self.start_button_movie_clicked)
        self.makeTorrentButtonMovie.clicked.connect(self.make_torrent_button_movie_clicked)

        self.debugBrowserMovie.append("程序初始化成功，使用前请查看设置中的说明")

    def initialize_team_combobox(self):
        team_names = load_names('static/team.json', 'team')
        for name in team_names:
            self.teamMovie.addItem(name)
            self.teamPlaylet.addItem(name)

    def initialize_source_combobox(self):
        source_names = load_names('static/source.json', 'source')
        for name in source_names:
            self.sourceMovie.addItem(name)
            self.sourcePlaylet.addItem(name)

    def initialize_type_combobox(self):
        type_names = load_names('static/type.json', 'type')
        for name in type_names:
            self.typePlaylet.addItem(name)

    def settings_clicked(self):  # click对应的槽函数
        self.mySettings = settings()
        self.mySettings.getSettings()
        myico = QIcon("static/ph-bjd.ico")
        self.mySettings.setWindowIcon(myico)
        self.mySettings.show()  # 加上self避免页面一闪而过

    # 以下是Movie页面的代码

    def start_button_movie_clicked(self):
        self.get_name_button_movie_clicked()
        QApplication.processEvents()  # 处理所有挂起的事件，更新页面
        time.sleep(0)  # 等待 0 毫秒
        self.get_picture_button_movie_clicked()
        QApplication.processEvents()  # 再次处理事件
        time.sleep(2)  # 等待 2000 毫秒
        self.get_media_info_button_movie_clicked()
        QApplication.processEvents()  # 处理事件
        time.sleep(2)  # 等待 2000 毫秒
        self.make_torrent_button_movie_clicked()
        QApplication.processEvents()  # 处理事件

    def get_pt_gen_button_movie_clicked(self):
        self.ptGenBrowserMovie.setText("")
        pt_gen_path = get_settings("pt_gen_path")
        pt_gen_url = self.ptGenUrlMovie.text()

        if pt_gen_url == "":
            self.debugBrowserMovie.append("请输入输入豆瓣号、Imdb号、豆瓣、IMDb等资源链接")
            return
        if pt_gen_path == "":
            self.debugBrowserMovie.append("请在设置中输入Pt-Gen链接")
            return
        print("尝试启动pt_gen_thread")
        self.get_pt_gen_thread = GetPtGenThread(pt_gen_path, pt_gen_url)
        self.get_pt_gen_thread.result_signal.connect(self.handle_get_pt_gen_movie_result)  # 连接信号
        self.get_pt_gen_thread.start()  # 启动线程
        print("启动pt_gen_thread成功")

    def handle_get_pt_gen_movie_result(self, get_success, response):
        if get_success:
            if response:
                print(response)
                self.ptGenBrowserMovie.setText(response)
                self.debugBrowserMovie.append("成功获取Pt-Gen信息")
            else:
                self.debugBrowserMovie.append("获取Pt-Gen信息失败")
        else:
            self.debugBrowserMovie.append("未成功获取到任何Pt-Gen信息" + response)

    def get_picture_button_movie_clicked(self):
        self.pictureUrlBrowserMovie.setText("")
        is_video_path, video_path = check_path_and_find_video(self.videoPathMovie.text())  # 视频资源的路径

        if is_video_path == 1 or is_video_path == 2:
            self.debugBrowserMovie.append("获取视频" + video_path + "的截图")
            screenshot_path = get_settings("screenshot_path")  # 截图储存路径
            figure_bed_path = get_settings("figure_bed_path")  # 图床地址
            figure_bed_token = get_settings("figure_bed_token")  # 图床Token
            screenshot_number = int(get_settings("screenshot_number"))
            screenshot_threshold = float(get_settings("screenshot_threshold"))
            screenshot_start = float(get_settings("screenshot_start"))
            screenshot_end = float(get_settings("screenshot_end"))
            get_thumbnails = bool(get_settings("get_thumbnails"))
            rows = int(get_settings("rows"))
            cols = int(get_settings("cols"))
            auto_upload_screenshot = bool(get_settings("auto_upload_screenshot"))
            self.debugBrowserMovie.append("参数获取成功，开始执行截图函数")
            print("参数获取成功，开始执行截图函数")
            screenshot_success, res = extract_complex_keyframes(video_path, screenshot_path, screenshot_number,
                                                                screenshot_threshold, screenshot_start,
                                                                screenshot_end, min_interval_pct=0.01)
            print("成功获取截图函数的返回值")
            self.debugBrowserMovie.append("成功获取截图函数的返回值")
            if get_thumbnails:
                get_thumbnails_success, sv_path = get_thumbnail(video_path, screenshot_path, rows, cols,
                                                                screenshot_start, screenshot_end)
                if get_thumbnails_success:
                    res.append(sv_path)
            self.debugBrowserMovie.append("成功获取截图：" + str(res))
            if screenshot_success:
                # 判断是否需要上传图床
                if auto_upload_screenshot:
                    self.debugBrowserMovie.append("开始自动上传截图到图床" + figure_bed_path)
                    self.pictureUrlBrowserMovie.setText("")
                    if len(res) > 0:
                        self.upload_picture_thread0 = UploadPictureThread(figure_bed_path, figure_bed_token, res[0])
                        self.upload_picture_thread0.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread0.start()  # 启动线程
                    if len(res) > 1:
                        self.upload_picture_thread1 = UploadPictureThread(figure_bed_path, figure_bed_token, res[1])
                        self.upload_picture_thread1.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread1.start()  # 启动线程
                    if len(res) > 2:
                        self.upload_picture_thread2 = UploadPictureThread(figure_bed_path, figure_bed_token, res[2])
                        self.upload_picture_thread2.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread2.start()  # 启动线程
                    if len(res) > 3:
                        self.upload_picture_thread3 = UploadPictureThread(figure_bed_path, figure_bed_token, res[3])
                        self.upload_picture_thread3.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread3.start()  # 启动线程
                    if len(res) > 4:
                        self.upload_picture_thread4 = UploadPictureThread(figure_bed_path, figure_bed_token, res[4])
                        self.upload_picture_thread4.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread4.start()  # 启动线程
                    if len(res) > 5:
                        self.upload_picture_thread5 = UploadPictureThread(figure_bed_path, figure_bed_token, res[5])
                        self.upload_picture_thread5.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread5.start()  # 启动线程
                    print("上传图床线程启动")
                    self.debugBrowserMovie.append("上传图床线程启动")

                else:
                    self.debugBrowserMovie.append("未选择自动上传图床功能，图片已储存在本地")
                    output = ""
                    for r in res:
                        output += r
                        output += '\n'
                    self.pictureUrlBrowserMovie.setText(output)
            else:
                self.debugBrowserMovie.append("截图失败" + str(res))
        else:
            self.debugBrowserMovie.append("您的视频文件路径有误")

    def handle_upload_picture_movie_result(self, upload_success, api_response, screenshot_path):
        # 这个函数用于处理上传的结果，它将在主线程中被调用
        # 更新UI，显示上传结果等
        print("接受到线程请求的结果")
        self.debugBrowserMovie.append("接受到线程请求的结果")
        if upload_success:
            self.pictureUrlBrowserMovie.append(api_response)
            paste_screenshot_url = bool(get_settings("paste_screenshot_url"))
            delete_screenshot = bool(get_settings("delete_screenshot"))
            if paste_screenshot_url:
                self.ptGenBrowserMovie.append(api_response)
                self.debugBrowserMovie.append("成功将图片链接粘贴到简介后")
            if delete_screenshot:
                if os.path.exists(screenshot_path):
                    # 删除文件
                    os.remove(screenshot_path)
                    print(f"文件 {screenshot_path} 已被删除。")
                    self.debugBrowserMovie.append(f"文件 {screenshot_path} 已被删除。")
                else:
                    print(f"文件 {screenshot_path} 不存在。")
                    self.debugBrowserMovie.append(f"文件 {screenshot_path} 不存在。")
        else:
            self.debugBrowserMovie.append("图床响应无效：" + api_response)


    def select_video_button_movie_clicked(self):
        path = get_file_path()
        self.videoPathMovie.setText(path)

    def select_video_folder_button_movie_clicked(self):
        path = get_folder_path()
        self.videoPathMovie.setText(path)

    def get_media_info_button_movie_clicked(self):
        self.mediainfoBrowserMovie.setText("")
        isVideoPath, videoPath = check_path_and_find_video(self.videoPathMovie.text())  # 视频资源的路径
        if isVideoPath == 1 or isVideoPath == 2:
            get_media_info_success, mediainfo = get_media_info(videoPath)
            if get_media_info_success:
                self.mediainfoBrowserMovie.setText(mediainfo)
                self.mediainfoBrowserMovie.append('\n')
                self.debugBrowserMovie.append("成功获取到MediaInfo")
            else:
                self.debugBrowserMovie.append(mediainfo)
        else:
            self.debugBrowserMovie.append("您的视频文件路径有误")

    def get_name_button_movie_clicked(self):
        try:
            self.ptGenBrowserMovie.setText("")
            ptGenPath = get_settings("pt_gen_path")
            ptGenUrl = self.ptGenUrlMovie.text()

            if ptGenUrl == "":
                self.debugBrowserMovie.append("请输入输入豆瓣号、Imdb号、豆瓣、IMDb等资源链接")
                return
            if ptGenPath == "":
                self.debugBrowserMovie.append("请在设置中输入Pt-Gen链接")
                return
            print("尝试启动pt_gen_thread")
            self.debugBrowserMovie.append("尝试启动pt_gen_thread")
            self.get_pt_gen_for_name_thread = GetPtGenThread(ptGenPath, ptGenUrl)
            self.get_pt_gen_for_name_thread.result_signal.connect(self.handle_get_pt_gen_for_name_movie_result)  # 连接信号
            self.get_pt_gen_for_name_thread.start()  # 启动线程
            print("启动pt_gen_thread成功")
            self.debugBrowserMovie.append("启动pt_gen_thread成功")
        except Exception as e:
            print(f"启动PtGen线程出错：{e}")
            return False, [f"启动PtGen线程出错：{e}"]

    def handle_get_pt_gen_for_name_movie_result(self, get_success, response):
        try:
            if get_success:
                self.ptGenBrowserMovie.setText(response)
                if response:
                    print(response)
                    self.debugBrowserMovie.append("成功获取Pt-Gen信息")
                else:
                    self.debugBrowserMovie.append("获取Pt-Gen信息失败")
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
                isVideoPath, videoPath = check_path_and_find_video(self.videoPathMovie.text())
                if isVideoPath == 1 or isVideoPath == 2:
                    print("重命名初始化完成")
                    self.debugBrowserMovie.append("重命名初始化完成")
                    if response == "":
                        print("未获取到ptgen")
                        self.debugBrowserMovie.append("未获取到ptgen")
                    else:
                        print("开始获取ptgen关键信息")
                        self.debugBrowserMovie.append("开始获取ptgen关键信息")
                        first_chinese_name, first_english_name, year, other_names_sorted, category, actors_list = extract_details_from_ptgen(
                            response)
                        print(first_chinese_name, first_english_name, year, other_names_sorted, category, actors_list)
                        print("获取ptgen关键信息成功")
                        self.debugBrowserMovie.append("获取ptgen关键信息成功")
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
                    self.debugBrowserMovie.append("获取到关键参数：" + str(output))
                    if get_video_info_success:
                        width = output[0]
                        format = output[1]
                        hdr_format = output[2]
                        commercial_name = output[3]
                        channel_layout = output[4]
                    source = self.sourceMovie.currentText()
                    team = self.teamMovie.currentText()
                    print("关键参数赋值成功")
                    self.debugBrowserMovie.append("关键参数赋值成功")
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
                    self.mainTitleBrowserMovie.setText(mainTitle)
                    self.secondTitleBrowserMovie.setText(secondTitle)
                    self.fileNameBrowserMovie.setText(fileName)
                    if make_dir and isVideoPath == 1:
                        print("开始创建文件夹")
                        self.debugBrowserMovie.append("开始创建文件夹")
                        move_file_to_folder_success, output = move_file_to_folder(videoPath, fileName)
                        if move_file_to_folder_success:
                            self.videoPathMovie.setText(output)
                            videoPath = output
                            self.debugBrowserMovie.append("视频成功移动到：" + videoPath)
                        else:
                            self.debugBrowserMovie.append("创建文件夹失败：" + output)
                    if rename_file and isVideoPath == 1:
                        print("开始对文件重新命名")
                        self.debugBrowserMovie.append("开始对文件重新命名")
                        rename_file_success, output = rename_file_with_same_extension(videoPath, fileName)
                        if rename_file_success:
                            self.videoPathMovie.setText(output)
                            videoPath = output
                            self.debugBrowserMovie.append("视频成功重新命名为：" + videoPath)
                        else:
                            self.debugBrowserMovie.append("重命名失败：" + output)
                    if rename_file and isVideoPath == 2:
                        print("对文件夹重新命名")
                        self.debugBrowserMovie.append("开始对文件夹重新命名")
                        rename_directory_success, output = rename_directory(os.path.dirname(videoPath), fileName)
                        if rename_directory_success:
                            self.videoPathMovie.setText(output)
                            videoPath = output
                            self.debugBrowserMovie.append("视频地址成功重新命名为：" + videoPath)
                        else:
                            self.debugBrowserMovie.append("重命名失败：" + output)

                else:
                    self.debugBrowserMovie.append("您的视频文件路径有误")
            else:
                self.debugBrowserMovie.append("未成功获取到任何Pt-Gen信息：" + response)
        except Exception as e:
            print(f"启动PtGen线程成功，但是重命名出错：{e}")
            return False, [f"启动PtGen线程成功，但是重命名出错：{e}"]

    def make_torrent_button_movie_clicked(self):
        isVideoPath, videoPath = check_path_and_find_video(self.videoPathMovie.text())  # 视频资源的路径
        if isVideoPath == 1 or isVideoPath == 2:
            torrent_path = str(get_settings("torrent_path"))
            folder_path = os.path.dirname(videoPath)
            self.debugBrowserMovie.append("开始将" + folder_path + "制作种子，储存在" + torrent_path)
            self.make_torrent_thread = MakeTorrentThread(folder_path, torrent_path)
            self.make_torrent_thread.result_signal.connect(self.handle_make_torrent_movie_result)  # 连接信号
            self.make_torrent_thread.start()  # 启动线程
            self.debugBrowserMovie.append("制作种子线程启动成功")
        else:
            self.debugBrowserMovie.append("制作种子失败：" + videoPath)

    def handle_make_torrent_movie_result(self, get_success, response):
        if get_success:
            self.debugBrowserMovie.append("成功制作种子：" + response)
        else:
            self.debugBrowserMovie.append("制作种子失败：" + response)

    # 以上是Movie页面的代码
    # 以下是TV页面的代码

    # 以上是TV页面的代码
    # 以下是Playlet页面的代码

    # 以上是Playlet页面的代码

    # 以上是Playlet页面的代码
    # 以下是Settings页面的代码


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
        self.screenshotPath.setText(str(get_settings("screenshot_path")))
        self.torrentPath.setText(str(get_settings("torrent_path")))
        self.ptGenPath.setText(get_settings("pt_gen_path"))
        self.figureBedPath.setText(get_settings("figure_bed_path"))
        self.figureBedToken.setText(get_settings("figure_bed_token"))
        self.screenshotNumber.setValue(int(get_settings("screenshot_number")))
        self.screenshotThreshold.setValue(float(get_settings("screenshot_threshold")))
        self.screenshotStart.setValue(float(get_settings("screenshot_start")))
        self.screenshotEnd.setValue(float(get_settings("screenshot_end")))
        self.getThumbnails.setChecked(bool(get_settings("get_thumbnails")))
        self.rows.setValue(int(get_settings("rows")))
        self.cols.setValue(int(get_settings("cols")))
        self.autoUploadScreenshot.setChecked(bool(get_settings("auto_upload_screenshot")))
        self.pasteScreenshotUrl.setChecked(bool(get_settings("paste_screenshot_url")))
        self.deleteScreenshot.setChecked(bool(get_settings("delete_screenshot")))
        self.makeDir.setChecked(bool(get_settings("make_dir")))
        self.renameFile.setChecked(bool(get_settings("rename_file")))

    def updateSettings(self):
        update_settings("screenshot_path", self.screenshotPath.text())
        update_settings("torrent_path", self.torrentPath.text())
        update_settings("pt_gen_path", self.ptGenPath.text())
        update_settings("figure_bed_path", self.figureBedPath.text())
        update_settings("figure_bed_token", self.figureBedToken.text())
        update_settings("screenshot_number", str(self.screenshotNumber.text()))
        update_settings("screenshot_threshold", str(self.screenshotThreshold.text()))
        update_settings("screenshot_start", str(self.screenshotStart.text()))
        update_settings("screenshot_end", str(self.screenshotEnd.text()))
        if self.getThumbnails.isChecked():
            update_settings("get_thumbnails", "True")
        else:
            update_settings("get_thumbnails", "")
        update_settings("rows", str(self.rows.text()))
        update_settings("cols", str(self.cols.text()))
        if self.autoUploadScreenshot.isChecked():
            update_settings("auto_upload_screenshot", "True")
        else:
            update_settings("auto_upload_screenshot", "")
        if self.pasteScreenshotUrl.isChecked():
            update_settings("paste_screenshot_url", "True")
        else:
            update_settings("paste_screenshot_url", "")
        if self.deleteScreenshot.isChecked():
            update_settings("delete_screenshot", "True")
        else:
            update_settings("delete_screenshot", "")
        if self.makeDir.isChecked():
            update_settings("make_dir", "True")
        else:
            update_settings("make_dir", "")
        if self.renameFile.isChecked():
            update_settings("rename_file", "True")
        else:
            update_settings("rename_file", "")

    # 以上是Settings页面的代码
    # 以下是多线程的代码


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
    result_signal = pyqtSignal(bool, str, str)

    def __init__(self, figure_bed_path, figure_bed_token, screenshot_path):
        super().__init__()
        self.figure_bed_path = figure_bed_path
        self.figure_bed_token = figure_bed_token
        self.screenshot_path = screenshot_path

    def run(self):
        try:
            # 这里放置耗时的HTTP请求操作
            upload_success, api_response = upload_screenshot(self.figure_bed_path, self.figure_bed_token,
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
