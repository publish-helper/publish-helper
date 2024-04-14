import os
import os
import re
import sys
import time
import webbrowser

import pyperclip
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication, QDialog, QInputDialog, QMessageBox, QWidget, QLineEdit

from autofeed import get_auto_feed_link
from mediainfo import get_media_info
from picturebed import upload_picture
from ptgen import get_pt_gen_description
from rename import get_pt_gen_info, get_video_info, get_name_from_template
from screenshot import get_screenshot, get_thumbnail
from startapi import run_api
from tool import update_settings, get_settings, get_video_file_path, move_file_to_folder, \
    get_folder_path, check_path_and_find_video, rename_directory, make_torrent, chinese_name_to_pinyin, \
    get_video_files, get_picture_file_path, is_filename_too_long, get_playlet_description, delete_season_number, \
    rename_file, get_combo_box_data
from ui.mainwindow import Ui_Mainwindow
from ui.settings import Ui_Settings


def start_gui():
    gui = QApplication(sys.argv)
    my_mainwindow = mainwindow()
    my_ico = QIcon("static/ph-bjd.ico")
    my_mainwindow.setWindowIcon(my_ico)
    my_mainwindow.show()
    sys.exit(gui.exec())


def git_clicked():
    webbrowser.open('https://github.com/publish-helper/publish-helper-gui')


class mainwindow(QMainWindow, Ui_Mainwindow):
    def __init__(self):
        super().__init__()

        self.my_settings = None
        self.setupUi(self)  # 设置界面

        # 初始化线程
        self.get_pt_gen_thread = None
        self.get_pt_gen_for_name_thread = None
        self.upload_picture_thread0 = None
        self.upload_picture_thread1 = None
        self.upload_picture_thread2 = None
        self.upload_picture_thread3 = None
        self.upload_picture_thread4 = None
        self.upload_picture_thread5 = None
        self.upload_cover_thread = None
        self.make_torrent_thread = None
        self.api_thread = None

        # 初始化
        self.videoPathMovie.setDragEnabled(True)
        self.descriptionBrowserMovie.setText("")
        self.pictureUrlBrowserMovie.setText("")
        self.mediainfoBrowserMovie.setText("")
        self.debugBrowserMovie.setText("")
        self.initialize_team_combobox()
        self.initialize_source_combobox()
        self.initialize_playlet_source_combobox()
        self.torrent_url = ''

        # 绑定点击信号和槽函数
        # Movie
        self.actionsettings.triggered.connect(self.settings_clicked)
        self.actiongit.triggered.connect(git_clicked)
        self.getPtGenButtonMovie.clicked.connect(self.get_pt_gen_button_movie_clicked)
        self.getPictureButtonMovie.clicked.connect(self.get_picture_button_movie_clicked)
        self.selectVideoButtonMovie.clicked.connect(self.select_video_button_movie_clicked)
        self.selectVideoFolderButtonMovie.clicked.connect(self.select_video_folder_button_movie_clicked)
        self.getMediaInfoButtonMovie.clicked.connect(self.get_media_info_button_movie_clicked)
        self.getNameButtonMovie.clicked.connect(self.get_name_button_movie_clicked)
        self.makeTorrentButtonMovie.clicked.connect(self.make_torrent_button_movie_clicked)
        self.startButtonMovie.clicked.connect(self.start_button_movie_clicked)
        self.autoFeedButtonMovie.clicked.connect(self.auto_feed_button_movie_clicked)

        # TV
        self.actionsettings.triggered.connect(self.settings_clicked)
        self.getPtGenButtonTV.clicked.connect(self.get_pt_gen_button_tv_clicked)
        self.getPictureButtonTV.clicked.connect(self.get_picture_button_tv_clicked)
        self.selectVideoFolderButtonTV.clicked.connect(self.select_video_folder_button_tv_clicked)
        self.getMediaInfoButtonTV.clicked.connect(self.get_media_info_button_tv_clicked)
        self.getNameButtonTV.clicked.connect(self.get_name_button_tv_clicked)
        self.makeTorrentButtonTV.clicked.connect(self.make_torrent_button_tv_clicked)
        self.startButtonTV.clicked.connect(self.start_button_tv_clicked)
        self.autoFeedButtonTV.clicked.connect(self.auto_feed_button_tv_clicked)

        # Playlet
        self.getDescriptionButtonPlaylet.clicked.connect(self.get_description_playlet_clicked)
        self.getPictureButtonPlaylet.clicked.connect(self.get_picture_button_playlet_clicked)
        self.uploadCoverButtonPlaylet.clicked.connect(self.upload_cover_button_playlet_clicked)
        self.selectVideoFolderButtonPlaylet.clicked.connect(self.select_video_folder_button_playlet_clicked)
        self.selectCoverFolderButtonPlaylet.clicked.connect(self.select_cover_folder_button_playlet_clicked)
        self.getMediaInfoButtonPlaylet.clicked.connect(self.get_media_info_button_playlet_clicked)
        self.getNameButtonPlaylet.clicked.connect(self.get_name_button_playlet_clicked)
        self.makeTorrentButtonPlaylet.clicked.connect(self.make_torrent_button_playlet_clicked)
        self.startButtonPlaylet.clicked.connect(self.start_button_playlet_clicked)
        self.autoFeedButtonPlaylet.clicked.connect(self.auto_feed_button_playlet_clicked)

        # 初始化成功
        self.debugBrowserMovie.append(
            "程序初始化成功，使用前请查看设置中的说明！制作不易，如有帮助请帮忙点亮仓库的Star！\n作者：BJD 仓库地址：https://github.com/publish-helper/publish-helper-gui")

        if get_settings("enable_api"):
            self.run_api_thread()

    def initialize_team_combobox(self):
        get_data_success, data = get_combo_box_data('team')
        if get_data_success:
            for name in data:
                self.teamMovie.addItem(name)
                self.teamTV.addItem(name)
                self.teamPlaylet.addItem(name)
        else:
            self.debugBrowserMovie.append(f"获取制作组信息出错：{data[0]}")
            self.debugBrowserTV.append(f"获取制作组信息出错：{data[0]}")
            self.debugBrowserPlaylet.append(f"获取制作组信息出错：{data[0]}")

    def initialize_source_combobox(self):
        get_data_success, data = get_combo_box_data('source')
        if get_data_success:
            for name in data:
                self.sourceMovie.addItem(name)
                self.sourceTV.addItem(name)
                self.sourcePlaylet.addItem(name)
        else:
            self.debugBrowserMovie.append(f"获取资源来源信息出错：{data[0]}")
            self.debugBrowserTV.append(f"获取资源来源信息出错：{data[0]}")
            self.debugBrowserPlaylet.append(f"获取资源来源信息出错：{data[0]}")

    def initialize_playlet_source_combobox(self):
        get_data_success, data = get_combo_box_data('playlet-source')
        if get_data_success:
            for name in data:
                self.playletSource.addItem(name)
        else:
            self.debugBrowserPlaylet.append(f"获取短剧来源信息出错：{data[0]}")

    def settings_clicked(self):  # click对应的槽函数
        self.my_settings = settings()
        self.my_settings.getSettings()
        my_ico = QIcon("static/ph-bjd.ico")
        self.my_settings.setWindowIcon(my_ico)
        self.my_settings.show()  # 加上self避免页面一闪而过

    def run_api_thread(self):
        self.debugBrowserMovie.append("您选择启用API功能，正在尝试启动api_thread")
        self.api_thread = apiThread()
        self.api_thread.result_signal.connect(self.handle_run_api_result)  # 连接信号
        self.api_thread.start()  # 启动线程
        self.debugBrowserMovie.append("api_thread启动成功，监听端口：" + str(get_settings("api_port")))

    def handle_run_api_result(self, response):
        self.debugBrowserMovie.append(response)

    # 以下是Movie页面的代码

    def start_button_movie_clicked(self):
        if get_settings("second_confirm_file_name"):
            self.debugBrowserMovie.append("如需一键启动，请到设置关闭二次确认文件名功能")
            return
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

    def auto_feed_button_movie_clicked(self):
        mian_title, second_title, description, media_info, file_name, category, team, source = '', '', '', '', '', '', '', ''
        mian_title += self.mainTitleBrowserMovie.toPlainText()
        second_title += self.secondTitleBrowserMovie.toPlainText()
        description += self.descriptionBrowserMovie.toPlainText()
        media_info += self.mediainfoBrowserMovie.toPlainText()
        file_name += self.fileNameBrowserMovie.toPlainText()
        category += "电影"
        team += self.teamMovie.currentText()
        source += self.sourceMovie.currentText()
        auto_feed_link = get_auto_feed_link(mian_title, second_title, description, media_info, file_name, category,
                                            team, source, self.torrent_url)
        self.debugBrowserMovie.append("auto_feed_link: " + auto_feed_link)
        pyperclip.copy(auto_feed_link)
        self.debugBrowserMovie.append("auto_feed链接已经复制到剪切板，请粘贴到浏览器访问")
        if get_settings("open_auto_feed_link"):
            webbrowser.open(auto_feed_link)

    def get_pt_gen_button_movie_clicked(self):
        self.descriptionBrowserMovie.setText("")
        pt_gen_path = get_settings("pt_gen_api_url")
        pt_gen_url = self.ptGenUrlMovie.text()

        if pt_gen_url == "":
            self.debugBrowserMovie.append("请输入输入豆瓣号、Imdb号、豆瓣、IMDb等资源链接")
            return
        if pt_gen_path == "":
            self.debugBrowserMovie.append("请在设置中输入Pt-Gen链接")
            return
        print("尝试启动pt_gen_thread")
        self.debugBrowserMovie.append("尝试启动pt_gen_thread，您选择的Pt-Gen接口是：" + pt_gen_path)
        self.get_pt_gen_thread = GetPtGenThread(pt_gen_path, pt_gen_url)
        self.get_pt_gen_thread.result_signal.connect(self.handle_get_pt_gen_movie_result)  # 连接信号
        self.get_pt_gen_thread.start()  # 启动线程
        print("启动pt_gen_thread成功，请耐心等待Api返回结果并分析...")
        self.debugBrowserMovie.append("启动pt_gen_thread成功，请耐心等待Api返回结果并分析...")

    def handle_get_pt_gen_movie_result(self, get_success, response):
        if get_success:
            if response:
                print(response)
                self.descriptionBrowserMovie.setText(response)
                self.debugBrowserMovie.append("成功获取Pt-Gen信息")
            else:
                self.debugBrowserMovie.append("获取Pt-Gen信息失败")
        else:
            self.debugBrowserMovie.append("未成功获取到任何Pt-Gen信息" + response)

    def get_picture_button_movie_clicked(self):
        self.pictureUrlBrowserMovie.setText("")
        is_video_path, video_path = check_path_and_find_video(
            self.videoPathMovie.text().replace('file:///', ''))  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            self.debugBrowserMovie.append("获取视频" + video_path + "的截图")
            screenshot_storage_path = get_settings("screenshot_storage_path")  # 截图储存路径
            picture_bed_path = get_settings("picture_bed_api_url")  # 图床地址
            picture_bed_token = get_settings("picture_bed_api_token")  # 图床Token
            screenshot_number = int(get_settings("screenshot_number"))
            screenshot_threshold = float(get_settings("screenshot_threshold"))
            screenshot_start_percentage = float(get_settings("screenshot_start_percentage"))
            screenshot_end_percentage = float(get_settings("screenshot_end_percentage"))
            do_get_thumbnail = bool(get_settings("do_get_thumbnail"))
            thumbnail_rows = int(get_settings("thumbnail_rows"))
            thumbnail_cols = int(get_settings("thumbnail_cols"))
            auto_upload_screenshot = bool(get_settings("auto_upload_screenshot"))
            self.debugBrowserMovie.append("图床参数获取成功，图床地址是：" + picture_bed_path + "\n开始执行截图函数")
            print("参数获取成功，开始执行截图函数")
            res = []
            screenshot_success, response = get_screenshot(video_path, screenshot_storage_path, screenshot_number,
                                                          screenshot_threshold, screenshot_start_percentage,
                                                          screenshot_end_percentage, screenshot_min_interval=0.01)
            print("成功获取截图函数的返回值")
            self.debugBrowserMovie.append("成功获取截图函数的返回值")
            if do_get_thumbnail:
                get_thumbnail_success, thumbnail_path = get_thumbnail(video_path, screenshot_storage_path,
                                                                      thumbnail_rows,
                                                                      thumbnail_cols,
                                                                      screenshot_start_percentage,
                                                                      screenshot_end_percentage)
                if get_thumbnail_success:
                    res.append(thumbnail_path)
            if screenshot_success:
                res = response + res
                self.debugBrowserMovie.append("成功获取截图：" + str(res))
                # 判断是否需要上传图床
                if auto_upload_screenshot:
                    self.debugBrowserMovie.append("开始自动上传截图到图床：" + picture_bed_path)
                    self.pictureUrlBrowserMovie.setText("")
                    if len(res) > 0:
                        if do_get_thumbnail and len(res) == 1:
                            self.upload_picture_thread0 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[0],
                                                                              False, True)
                        else:
                            self.upload_picture_thread0 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[0],
                                                                              False, False)
                        self.upload_picture_thread0.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread0.start()  # 启动线程
                        print("启动线程0")
                    if len(res) > 1:
                        if do_get_thumbnail and len(res) == 2:
                            self.upload_picture_thread1 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[1],
                                                                              False, True)
                        else:
                            self.upload_picture_thread1 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[1],
                                                                              False, False)
                        self.upload_picture_thread1.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread1.start()  # 启动线程
                        print("启动线程1")
                    if len(res) > 2:
                        if do_get_thumbnail and len(res) == 3:
                            self.upload_picture_thread2 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[2],
                                                                              False, True)
                        else:
                            self.upload_picture_thread2 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[2],
                                                                              False, False)
                        self.upload_picture_thread2.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread2.start()  # 启动线程
                        print("启动线程2")
                    if len(res) > 3:
                        if do_get_thumbnail and len(res) == 4:
                            self.upload_picture_thread3 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[3],
                                                                              False, True)
                        else:
                            self.upload_picture_thread3 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[3],
                                                                              False, False)
                        self.upload_picture_thread3.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread3.start()  # 启动线程
                        print("启动线程3")
                    if len(res) > 4:
                        if do_get_thumbnail and len(res) == 5:
                            self.upload_picture_thread4 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[4],
                                                                              False, True)
                        else:
                            self.upload_picture_thread4 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[4],
                                                                              False, False)
                        self.upload_picture_thread4.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread4.start()  # 启动线程
                        print("启动线程4")
                    if len(res) > 5:
                        if do_get_thumbnail and len(res) == 6:
                            self.upload_picture_thread5 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[5],
                                                                              False, True)
                        else:
                            self.upload_picture_thread5 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[5],
                                                                              False, False)
                        self.upload_picture_thread5.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread5.start()  # 启动线程
                        print("启动线程5")
                    print("上传图床线程全部启动")
                    self.debugBrowserMovie.append("上传图床线程启动，请耐心等待图床Api的响应...")

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
        self.debugBrowserMovie.append("接受到线程请求的结果")
        if upload_success:
            self.pictureUrlBrowserMovie.append(api_response)
            paste_screenshot_url = bool(get_settings("paste_screenshot_url"))
            delete_screenshot = bool(get_settings("delete_screenshot"))
            if paste_screenshot_url:
                self.descriptionBrowserMovie.append(api_response)
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
        path = get_video_file_path()
        self.videoPathMovie.setText(path)

    def select_video_folder_button_movie_clicked(self):
        path = get_folder_path()
        self.videoPathMovie.setText(path)

    def get_media_info_button_movie_clicked(self):
        self.mediainfoBrowserMovie.setText("")
        is_video_path, video_path = check_path_and_find_video(
            self.videoPathMovie.text().replace('file:///', ''))  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            get_media_info_success, media_info = get_media_info(video_path)
            if get_media_info_success:
                self.mediainfoBrowserMovie.setText(media_info)
                self.mediainfoBrowserMovie.append('\n')
                self.debugBrowserMovie.append("成功获取到MediaInfo")
            else:
                self.debugBrowserMovie.append(media_info)
        else:
            self.debugBrowserMovie.append("您的视频文件路径有误")

    def get_name_button_movie_clicked(self):
        try:
            self.descriptionBrowserMovie.setText("")
            pt_gen_path = get_settings("pt_gen_api_url")
            pt_gen_url = self.ptGenUrlMovie.text()
            if pt_gen_url == "":
                self.debugBrowserMovie.append("请输入输入豆瓣号、Imdb号、豆瓣、IMDb等资源链接")
                return
            if pt_gen_path == "":
                self.debugBrowserMovie.append("请在设置中输入Pt-Gen链接")
                return
            print("尝试启动pt_gen_thread")
            self.debugBrowserMovie.append("尝试启动pt_gen_thread，您选择的Pt-Gen接口是：" + pt_gen_path)
            self.get_pt_gen_for_name_thread = GetPtGenThread(pt_gen_path, pt_gen_url)
            self.get_pt_gen_for_name_thread.result_signal.connect(self.handle_get_pt_gen_for_name_movie_result)  # 连接信号
            self.get_pt_gen_for_name_thread.start()  # 启动线程
            print("启动pt_gen_thread成功，请耐心等待Api返回结果并分析...")
            self.debugBrowserMovie.append("启动pt_gen_thread成功，请耐心等待Api返回结果并分析...")
        except Exception as e:
            print(f"启动PtGen线程出错：{e}")
            return False, [f"启动PtGen线程出错：{e}"]

    def handle_get_pt_gen_for_name_movie_result(self, get_success, response):
        try:
            if get_success:
                self.descriptionBrowserMovie.setText(response)
                if response:
                    print("获得的Pt-Gen Api响应：" + response)
                    if response == "":
                        self.debugBrowserMovie.append("获取Pt-Gen信息失败")
                        return
                else:
                    self.debugBrowserMovie.append("获取Pt-Gen信息失败")
                    return
                video_format = ""
                video_codec = ""
                bit_depth = ""
                hdr_format = ""
                frame_rate = ""
                audio_codec = ""
                channels = ""
                other_titles = ""
                actors = ""
                make_dir = get_settings("make_dir")
                do_rename_file = get_settings("rename_file")
                second_confirm_file_name = get_settings("second_confirm_file_name")
                is_video_path, video_path = check_path_and_find_video(
                    self.videoPathMovie.text().replace('file:///', ''))
                if is_video_path == 1 or is_video_path == 2:
                    print("重命名初始化完成")
                    self.debugBrowserMovie.append("重命名初始化完成")
                    if not response:
                        print("Pt-Gen的响应为空")
                        self.debugBrowserMovie.append("Pt-Gen的响应为空")
                        return
                    else:
                        print("获取到了Pt-Gen Api的响应，开始获取Pt-Gen关键信息")
                        self.debugBrowserMovie.append("获取到了Pt-Gen Api的响应，开始获取Pt-Gen关键信息")
                        try:
                            original_title, english_title, year, other_names_sorted, category, actors_list = get_pt_gen_info(
                                response)
                        except Exception as e:
                            self.debugBrowserMovie.append(
                                f"获取到了Pt-Gen Api的响应，但是对于响应的分析有错误：{e}" + "\n获取到的响应是" + str(
                                    response) + "\n请重试！")
                            print(
                                f"获取到了Pt-Gen Api的响应，但是对于响应的分析有错误：{e}" + "\n获取到的响应是" + str(
                                    response) + "\n请重试！")
                            return False, [
                                f"获取到了Pt-Gen Api的响应，但是对于响应的分析有错误：{e}" + "\n获取到的响应是" + str(
                                    response) + "\n请重试！"]
                        print(original_title, english_title, year, other_names_sorted, category, actors_list)
                        self.debugBrowserMovie.append(
                            "分析后的结果为：" + original_title + english_title + year + str(
                                other_names_sorted) + category +
                            str(actors_list))
                        if year == "" or year is None:
                            print("Pt-Gen分析结果不包含年份，存在错误")
                            self.debugBrowserMovie.append("Pt-Gen分析结果不包含年份，存在错误")
                            return
                        else:
                            self.debugBrowserMovie.append('获取到发布年份：' + year)
                        print("获取Pt-Gen关键信息成功")
                        self.debugBrowserMovie.append("获取Pt-Gen关键信息成功")
                        is_first = True
                        for data in actors_list:  # 把演员名转化成str
                            if is_first:
                                actors += data
                                is_first = False
                            else:
                                actors += ' / '
                                actors += data

                        for data in other_names_sorted:  # 把别名转化为str
                            other_titles += data
                            other_titles += ' / '
                        other_titles = other_titles[: -3]
                    english_pattern = r'^[A-Za-z\-\—\:\s\(\)\'\"\@\#\$\%\^\&\*\!\?\,\.\;\[\]\{\}\|\<\>\`\~\d\u2160-\u2188]+$'
                    widget = QWidget(self)
                    if original_title != '':
                        if english_title == '':
                            ok = QMessageBox.information(self, 'Pt-Gen未获取到英文名称',
                                                         '资源的名称是：' + original_title + '\n是否使用汉语拼音作为英文名称？（仅限中文）',
                                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            print('你的选择是', ok)
                            if ok == QMessageBox.StandardButton.Yes:
                                english_title = chinese_name_to_pinyin(original_title)
                            if not re.match(english_pattern, english_title):
                                print("first_english_name does not match the english_pattern.")
                                if ok == QMessageBox.StandardButton.Yes:
                                    QMessageBox.warning(widget, '警告', '资源名称不是汉语，无法使用汉语拼音')
                                text, ok = QInputDialog.getText(self, '输入资源的英文名称',
                                                                'Pt-Gen未检测到英文名称，请注意使用英文标点符号')
                                if ok:
                                    print(f'您输入的数据为: {text}')
                                    self.debugBrowserMovie.append(f'您输入的数据为: {text}')
                                    english_title = text.replace('.', ' ')
                                    invalid_characters = ''
                                    for char in english_title:
                                        if not re.match(english_pattern, char):
                                            invalid_characters += char
                                    print("不匹配的字符：", invalid_characters)
                                    if invalid_characters != '':
                                        QMessageBox.warning(widget, '警告',
                                                            '您输入的英文名称包含非英文字符或符号\n有以下这些：' + '|'.join(
                                                                invalid_characters) + '\n请重新核对后再生成标准命名')
                                        return

                                else:
                                    print('未输入任何数据')
                                    self.debugBrowserMovie.append('未输入任何数据')
                                    english_title = ''
                    get_video_info_success, output = get_video_info(video_path)
                    if get_video_info_success:
                        print("获取到关键参数：" + str(output))
                        self.debugBrowserMovie.append("获取到关键参数：" + str(output))
                        video_format = output[0]
                        video_codec = output[1]
                        bit_depth = output[2]
                        hdr_format = output[3]
                        frame_rate = output[4]
                        audio_codec = output[5]
                        channels = output[6]
                    source = self.sourceMovie.currentText()
                    team = self.teamMovie.currentText()
                    print("关键参数赋值成功")
                    self.debugBrowserMovie.append("关键参数赋值成功")
                    main_title = get_name_from_template(english_title, original_title, "", "", year,
                                                        video_format, source, video_codec, bit_depth, hdr_format,
                                                        frame_rate, audio_codec, channels, team, other_titles, "",
                                                        "", "", category, actors, "main_title_movie")
                    main_title = main_title.replace('_', ' ')
                    main_title = re.sub(r'\s+', ' ', main_title)  # 将连续的空格变成一个
                    print(main_title)
                    second_title = get_name_from_template(english_title, original_title, "", "", year, video_format,
                                                          source, video_codec, bit_depth, hdr_format, frame_rate,
                                                          audio_codec, channels, team, other_titles, "", "", "",
                                                          category, actors, "second_title_movie")
                    second_title = second_title.replace(' /  | ', ' | ')  # 避免单别名导致的错误
                    print("SecondTitle" + second_title)
                    file_name = get_name_from_template(english_title, original_title, "", "", year, video_format,
                                                       source, video_codec, bit_depth, hdr_format, frame_rate,
                                                       audio_codec, channels, team, other_titles, "", "",
                                                       "",
                                                       category, actors, "file_name_movie")
                    file_name = re.sub(r'[<>:\"/\\|?*\s]', '.', file_name)
                    file_name = re.sub(r'\.{2,}', '.', file_name)  # 将连续的'.'变成一个
                    if second_confirm_file_name:
                        text, ok = QInputDialog.getText(self, '确认', '请确认文件名称，如有问题请修改',
                                                        QLineEdit.EchoMode.Normal, file_name)
                        if ok:
                            print(f'您确认文件名为: {text}')
                            self.debugBrowserMovie.append(f'您确认文件名为: {text}')
                            file_name = text
                        else:
                            print('您点了取消确认，重命名已取消')
                            self.debugBrowserMovie.append('您点了取消确认，重命名已取消')
                            return
                    if is_filename_too_long(file_name):
                        text, ok = QInputDialog.getText(self, '警告',
                                                        '文件名过长，请修改文件名称！', QLineEdit.EchoMode.Normal,
                                                        file_name)
                        if ok:
                            print(f'您修改文件名为: {text}')
                            self.debugBrowserMovie.append(f'您修改文件名为: {text}')
                            file_name = text
                        else:
                            print('您点了取消确认，重命名已取消')
                            self.debugBrowserMovie.append('您点了取消确认，重命名已取消')
                            return
                        if is_filename_too_long(file_name):
                            QMessageBox.warning(widget, '警告',
                                                '您输入的文件名过长，请重新核对后再生成标准命名！')
                            self.debugBrowserMovie.append('您输入的文件名过长，请重新核对后再生成标准命名！')
                            return
                    print("FileName" + file_name)
                    self.mainTitleBrowserMovie.setText(main_title)
                    self.secondTitleBrowserMovie.setText(second_title)
                    self.fileNameBrowserMovie.setText(file_name)
                    if make_dir and is_video_path == 1:
                        print("开始创建文件夹")
                        self.debugBrowserMovie.append("开始创建文件夹")
                        move_file_to_folder_success, output = move_file_to_folder(video_path, file_name)
                        if move_file_to_folder_success:
                            self.videoPathMovie.setText(output)
                            video_path = output
                            self.debugBrowserMovie.append("视频成功移动到：" + video_path)
                        else:
                            self.debugBrowserMovie.append("创建文件夹失败：" + output)
                    if do_rename_file and is_video_path == 1:
                        print("开始对文件重新命名")
                        self.debugBrowserMovie.append("开始对文件重新命名")
                        rename_file_success, output = rename_file(video_path, file_name)
                        if rename_file_success:
                            self.videoPathMovie.setText(output)
                            video_path = output
                            self.debugBrowserMovie.append("视频成功重新命名为：" + video_path)
                        else:
                            self.debugBrowserMovie.append("重命名失败：" + output)
                    if do_rename_file and is_video_path == 2:
                        print("对文件夹重新命名")
                        self.debugBrowserMovie.append("开始对文件夹重新命名")
                        rename_directory_success, output = rename_directory(os.path.dirname(video_path), file_name)
                        if rename_directory_success:
                            self.videoPathMovie.setText(output)
                            video_path = output
                            self.debugBrowserMovie.append("视频地址成功重新命名为：" + video_path)
                        else:
                            self.debugBrowserMovie.append("重命名失败：" + output)

                else:
                    self.debugBrowserMovie.append("您的视频文件路径有误")
            else:
                self.debugBrowserMovie.append("未成功获取到任何Pt-Gen信息：" + response)
        except Exception as e:
            self.debugBrowserMovie.append(f"启动PtGen线程成功，但是重命名出错：{e}")
            print(f"启动PtGen线程成功，但是重命名出错：{e}")
            return False, [f"启动PtGen线程成功，但是重命名出错：{e}"]

    def make_torrent_button_movie_clicked(self):
        self.torrent_url = ''
        is_video_path, video_path = check_path_and_find_video(
            self.videoPathMovie.text().replace('file:///', ''))  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            torrent_storage_path = str(get_settings("torrent_storage_path"))
            folder_path = os.path.dirname(video_path)
            self.debugBrowserMovie.append("开始将" + folder_path + "制作种子，储存在" + torrent_storage_path)
            self.make_torrent_thread = MakeTorrentThread(folder_path, torrent_storage_path)
            self.make_torrent_thread.result_signal.connect(self.handle_make_torrent_movie_result)  # 连接信号
            self.make_torrent_thread.start()  # 启动线程
            self.debugBrowserMovie.append("制作种子线程启动成功，正在后台制作种子，请耐心等待种子制作完毕...")
        else:
            self.debugBrowserMovie.append("制作种子失败：" + video_path)

    def handle_make_torrent_movie_result(self, get_success, response):
        if get_success:
            self.torrent_url = f'http://127.0.0.1:{get_settings("api_port")}/api/getFile?filePath={response}'
            self.debugBrowserMovie.append("成功制作种子：" + response)
        else:
            self.debugBrowserMovie.append("制作种子失败：" + response)

    # 以上是Movie页面的代码
    # 以下是TV页面的代码
    def start_button_tv_clicked(self):
        if get_settings("second_confirm_file_name"):
            self.debugBrowserMovie.append("如需一键启动，请到设置关闭二次确认文件名功能")
            return
        self.get_name_button_tv_clicked()
        QApplication.processEvents()  # 处理所有挂起的事件，更新页面
        time.sleep(0)  # 等待 0 毫秒
        self.get_picture_button_tv_clicked()
        QApplication.processEvents()  # 再次处理事件
        time.sleep(2)  # 等待 2000 毫秒
        self.get_media_info_button_tv_clicked()
        QApplication.processEvents()  # 处理事件
        time.sleep(2)  # 等待 2000 毫秒
        self.make_torrent_button_tv_clicked()
        QApplication.processEvents()  # 处理事件

    def auto_feed_button_tv_clicked(self):
        mian_title, second_title, description, media_info, file_name, category, team, source = '', '', '', '', '', '', '', ''
        mian_title += self.mainTitleBrowserTV.toPlainText()
        second_title += self.secondTitleBrowserTV.toPlainText()
        description += self.descriptionBrowserTV.toPlainText()
        media_info += self.mediainfoBrowserTV.toPlainText()
        file_name += self.fileNameBrowserTV.toPlainText()
        category += "剧集"
        team += self.teamTV.currentText()
        source += self.sourceTV.currentText()
        auto_feed_link = get_auto_feed_link(mian_title, second_title, description, media_info, file_name, category,
                                            team, source, self.torrent_url)
        self.debugBrowserTV.append("auto_feed_link: " + auto_feed_link)
        pyperclip.copy(auto_feed_link)
        self.debugBrowserTV.append("auto_feed链接已经复制到剪切板，请粘贴到浏览器访问")
        if get_settings("open_auto_feed_link"):
            webbrowser.open(auto_feed_link)

    def get_pt_gen_button_tv_clicked(self):
        self.descriptionBrowserTV.setText("")
        pt_gen_path = get_settings("pt_gen_api_url")
        pt_gen_url = self.ptGenUrlTV.text()

        if pt_gen_url == "":
            self.debugBrowserTV.append("请输入输入豆瓣号、Imdb号、豆瓣、IMDb等资源链接")
            return
        if pt_gen_path == "":
            self.debugBrowserTV.append("请在设置中输入Pt-Gen链接")
            return
        print("尝试启动pt_gen_thread")
        self.debugBrowserTV.append("尝试启动pt_gen_thread，您选择的Pt-Gen接口是：" + pt_gen_path)
        self.get_pt_gen_thread = GetPtGenThread(pt_gen_path, pt_gen_url)
        self.get_pt_gen_thread.result_signal.connect(self.handle_get_pt_gen_tv_result)  # 连接信号
        self.get_pt_gen_thread.start()  # 启动线程
        print("启动pt_gen_thread成功，请耐心等待Api返回结果并分析...")
        self.debugBrowserTV.append("启动pt_gen_thread成功，请耐心等待Api返回结果并分析...")

    def handle_get_pt_gen_tv_result(self, get_success, response):
        if get_success:
            if response:
                print(response)
                self.descriptionBrowserTV.setText(response)
                self.debugBrowserTV.append("成功获取Pt-Gen信息")
            else:
                self.debugBrowserTV.append("获取Pt-Gen信息失败")
        else:
            self.debugBrowserTV.append("未成功获取到任何Pt-Gen信息" + response)

    def get_picture_button_tv_clicked(self):
        self.pictureUrlBrowserTV.setText("")
        is_video_path, video_path = check_path_and_find_video(
            self.videoPathTV.text().replace('file:///', ''))  # 视频资源的路径

        if is_video_path == 1 or is_video_path == 2:
            self.debugBrowserTV.append("获取视频" + video_path + "的截图")
            screenshot_storage_path = get_settings("screenshot_storage_path")  # 截图储存路径
            picture_bed_path = get_settings("picture_bed_api_url")  # 图床地址
            picture_bed_token = get_settings("picture_bed_api_token")  # 图床Token
            screenshot_number = int(get_settings("screenshot_number"))
            screenshot_threshold = float(get_settings("screenshot_threshold"))
            screenshot_start_percentage = float(get_settings("screenshot_start_percentage"))
            screenshot_end_percentage = float(get_settings("screenshot_end_percentage"))
            do_get_thumbnail = bool(get_settings("do_get_thumbnail"))
            thumbnail_rows = int(get_settings("thumbnail_rows"))
            thumbnail_cols = int(get_settings("thumbnail_cols"))
            auto_upload_screenshot = bool(get_settings("auto_upload_screenshot"))
            self.debugBrowserTV.append("图床参数获取成功，图床地址是：" + picture_bed_path + "\n开始执行截图函数")
            print("参数获取成功，开始执行截图函数")
            res = []
            screenshot_success, response = get_screenshot(video_path, screenshot_storage_path, screenshot_number,
                                                          screenshot_threshold, screenshot_start_percentage,
                                                          screenshot_end_percentage, screenshot_min_interval=0.01)
            print("成功获取截图函数的返回值")
            self.debugBrowserTV.append("成功获取截图函数的返回值")
            if do_get_thumbnail:
                get_thumbnail_success, thumbnail_path = get_thumbnail(video_path, screenshot_storage_path,
                                                                      thumbnail_rows,
                                                                      thumbnail_cols,
                                                                      screenshot_start_percentage,
                                                                      screenshot_end_percentage)
                if get_thumbnail_success:
                    res.append(thumbnail_path)
            if screenshot_success:
                res = response + res
                self.debugBrowserTV.append("成功获取截图：" + str(res))
                # 判断是否需要上传图床
                if auto_upload_screenshot:
                    self.debugBrowserTV.append("开始自动上传截图到图床：" + picture_bed_path)
                    self.pictureUrlBrowserTV.setText("")
                    if len(res) > 0:
                        if do_get_thumbnail and len(res) == 1:
                            self.upload_picture_thread0 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[0],
                                                                              False, True)
                        else:
                            self.upload_picture_thread0 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[0],
                                                                              False, False)
                        self.upload_picture_thread0.result_signal.connect(self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread0.start()  # 启动线程
                        print("启动线程0")
                    if len(res) > 1:
                        if do_get_thumbnail and len(res) == 2:
                            self.upload_picture_thread1 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[1],
                                                                              False, True)
                        else:
                            self.upload_picture_thread1 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[1],
                                                                              False, False)
                        self.upload_picture_thread1.result_signal.connect(self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread1.start()  # 启动线程
                        print("启动线程1")
                    if len(res) > 2:
                        if do_get_thumbnail and len(res) == 3:
                            self.upload_picture_thread2 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[2],
                                                                              False, True)
                        else:
                            self.upload_picture_thread2 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[2],
                                                                              False, False)
                        self.upload_picture_thread2.result_signal.connect(self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread2.start()  # 启动线程
                        print("启动线程2")
                    if len(res) > 3:
                        if do_get_thumbnail and len(res) == 4:
                            self.upload_picture_thread3 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[3],
                                                                              False, True)
                        else:
                            self.upload_picture_thread3 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[3],
                                                                              False, False)
                        self.upload_picture_thread3.result_signal.connect(self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread3.start()  # 启动线程
                        print("启动线程3")
                    if len(res) > 4:
                        if do_get_thumbnail and len(res) == 5:
                            self.upload_picture_thread4 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[4],
                                                                              False, True)
                        else:
                            self.upload_picture_thread4 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[4],
                                                                              False, False)
                        self.upload_picture_thread4.result_signal.connect(self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread4.start()  # 启动线程
                        print("启动线程4")
                    if len(res) > 5:
                        if do_get_thumbnail and len(res) == 6:
                            self.upload_picture_thread5 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[5],
                                                                              False, True)
                        else:
                            self.upload_picture_thread5 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[5],
                                                                              False, False)
                        self.upload_picture_thread5.result_signal.connect(self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread5.start()  # 启动线程
                        print("启动线程5")
                    print("上传图床线程全部启动")
                    self.debugBrowserTV.append("上传图床线程启动，请耐心等待图床Api的响应...")
                else:
                    self.debugBrowserTV.append("未选择自动上传图床功能，图片已储存在本地")
                    output = ""
                    for r in res:
                        output += r
                        output += '\n'
                    self.pictureUrlBrowserTV.setText(output)
            else:
                self.debugBrowserTV.append("截图失败" + str(res))
        else:
            self.debugBrowserTV.append("您的视频文件路径有误")

    def handle_upload_picture_tv_result(self, upload_success, api_response, screenshot_path):
        # 这个函数用于处理上传的结果，它将在主线程中被调用
        # 更新UI，显示上传结果等
        print("接受到线程请求的结果")
        self.debugBrowserTV.append("接受到线程请求的结果")
        if upload_success:
            self.pictureUrlBrowserTV.append(api_response)
            paste_screenshot_url = bool(get_settings("paste_screenshot_url"))
            delete_screenshot = bool(get_settings("delete_screenshot"))
            if paste_screenshot_url:
                self.descriptionBrowserTV.append(api_response)
                self.debugBrowserTV.append("成功将图片链接粘贴到简介后")
            if delete_screenshot:
                if os.path.exists(screenshot_path):
                    # 删除文件
                    os.remove(screenshot_path)
                    print(f"文件 {screenshot_path} 已被删除。")
                    self.debugBrowserTV.append(f"文件 {screenshot_path} 已被删除。")
                else:
                    print(f"文件 {screenshot_path} 不存在。")
                    self.debugBrowserTV.append(f"文件 {screenshot_path} 不存在。")
        else:
            self.debugBrowserTV.append("图床响应无效：" + api_response)

    def select_video_folder_button_tv_clicked(self):
        path = get_folder_path()
        self.videoPathTV.setText(path)

    def get_media_info_button_tv_clicked(self):
        self.mediainfoBrowserTV.setText("")
        is_video_path, video_path = check_path_and_find_video(
            self.videoPathTV.text().replace('file:///', ''))  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            get_media_info_success, media_info = get_media_info(video_path)
            if get_media_info_success:
                self.mediainfoBrowserTV.setText(media_info)
                self.mediainfoBrowserTV.append('\n')
                self.debugBrowserTV.append("成功获取到MediaInfo")
            else:
                self.debugBrowserTV.append(media_info)
        else:
            self.debugBrowserTV.append("您的视频文件路径有误")

    def get_name_button_tv_clicked(self):
        try:
            self.descriptionBrowserTV.setText("")
            pt_gen_path = get_settings("pt_gen_api_url")
            pt_gen_url = self.ptGenUrlTV.text()

            if pt_gen_url == "":
                self.debugBrowserTV.append("请输入输入豆瓣号、Imdb号、豆瓣、IMDb等资源链接")
                return
            if pt_gen_path == "":
                self.debugBrowserTV.append("请在设置中输入Pt-Gen链接")
                return
            print("尝试启动pt_gen_thread")
            self.debugBrowserTV.append("尝试启动pt_gen_thread，您选择的Pt-Gen接口是：" + pt_gen_path)
            self.get_pt_gen_for_name_thread = GetPtGenThread(pt_gen_path, pt_gen_url)
            self.get_pt_gen_for_name_thread.result_signal.connect(self.handle_get_pt_gen_for_name_tv_result)  # 连接信号
            self.get_pt_gen_for_name_thread.start()  # 启动线程
            print("启动pt_gen_thread成功，请耐心等待Api返回结果并分析...")
            self.debugBrowserTV.append("启动pt_gen_thread成功，请耐心等待Api返回结果并分析...")
        except Exception as e:
            print(f"启动Pt-Gen线程出错：{e}")
            return False, [f"启动Pt-Gen线程出错：{e}"]

    def handle_get_pt_gen_for_name_tv_result(self, get_success, response):
        try:
            if get_success:
                self.descriptionBrowserTV.setText(response)
                if response:
                    print("获得的Pt-Gen Api响应：" + response)
                    if response == "":
                        self.debugBrowserTV.append("获取Pt-Gen信息失败")
                        return
                else:
                    self.debugBrowserTV.append("获取Pt-Gen信息失败")
                    return
                season = self.seasonBoxTV.text()
                total_episode = ""
                episode_num = 0
                episode_start_number = int(self.episodeStartBoxTV.text())
                season_number = season
                if len(season) < 2:
                    season = '0' + season
                video_format = ""
                video_codec = ""
                bit_depth = ""
                hdr_format = ""
                frame_rate = ""
                audio_codec = ""
                channels = ""
                other_titles = ""
                actors = ""
                do_rename_file = get_settings("rename_file")
                second_confirm_file_name = get_settings("second_confirm_file_name")
                is_video_path, video_path = check_path_and_find_video(self.videoPathTV.text().replace('file:///', ''))
                english_pattern = r'^[A-Za-z\-\—\:\s\(\)\'\"\@\#\$\%\^\&\*\!\?\,\.\;\[\]\{\}\|\<\>\`\~\d\u2160-\u2188]+$'
                widget = QWidget(self)
                if is_video_path == 2:  # 视频路径是文件夹
                    get_video_files_success, video_files = get_video_files(
                        self.videoPathTV.text().replace('file:///', ''))  # 获取文件夹内部的所有文件
                    if get_video_files_success:
                        print('检测到以下文件：', video_files)
                        episode_num = len(video_files)  # 获取视频文件的总数
                        if episode_start_number == 1:
                            total_episode = '全' + str(episode_num) + '集'
                        else:
                            if str(episode_start_number) == str(episode_start_number + episode_num - 1):
                                total_episode = '第' + str(episode_start_number) + '集'
                            else:
                                total_episode = '第' + str(episode_start_number) + '-' + str(
                                    episode_start_number + episode_num - 1) + '集'
                        print(total_episode)
                    else:
                        print("获取文件失败")
                    print("重命名初始化完成")
                    self.debugBrowserTV.append("重命名初始化完成")
                    if not response:
                        print("Pt-Gen响应为空")
                        self.debugBrowserTV.append("Pt-Gen响应为空")
                        return
                    else:
                        print("开始获取Pt-Gen关键信息")
                        self.debugBrowserTV.append("开始获取Pt-Gen关键信息")
                        try:
                            original_title, english_title, year, other_names_sorted, category, actors_list = get_pt_gen_info(
                                response)
                        except Exception as e:
                            self.debugBrowserTV.append(
                                f"获取到了Pt-Gen Api的响应，但是对于响应的分析有错误：{e}" + "\n获取到的响应是" + str(
                                    response) + "\n请重试！")
                            print(
                                f"获取到了Pt-Gen Api的响应，但是对于响应的分析有错误：{e}" + "\n获取到的响应是" + str(
                                    response) + "\n请重试！")
                            return False, [
                                f"获取到了Pt-Gen Api的响应，但是对于响应的分析有错误：{e}" + "\n获取到的响应是" + str(
                                    response) + "\n请重试！"]
                        print(original_title, english_title, year, other_names_sorted, category, actors_list)
                        self.debugBrowserTV.append(
                            "分析后的结果为：" + original_title + english_title + year + str(
                                other_names_sorted) + category +
                            str(actors_list))
                        if year == "" or year is None:
                            print("Pt-Gen分析结果不包含年份，存在错误")
                            self.debugBrowserTV.append("Pt-Gen分析结果不包含年份，存在错误")
                            return
                        if original_title != '':
                            if english_title == '':
                                ok = QMessageBox.information(self, 'Pt-Gen未获取到英文名称',
                                                             '资源的名称是：' + original_title + '\n是否使用汉语拼音作为英文名称？（仅限中文）',
                                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                print('你的选择是', ok)
                                if ok == QMessageBox.StandardButton.Yes:
                                    english_title = chinese_name_to_pinyin(original_title)
                                if not re.match(english_pattern, english_title):
                                    print("first_english_name does not match the english_pattern.")
                                    if ok == QMessageBox.StandardButton.Yes:
                                        QMessageBox.warning(widget, '警告', '资源名称不是汉语，无法使用汉语拼音')
                                    text, ok = QInputDialog.getText(self, '输入资源的英文名称',
                                                                    'Pt-Gen未检测到英文名称，请注意使用英文标点符号')
                                    if ok:
                                        print(f'您输入的数据为: {text}')
                                        self.debugBrowserTV.append(f'您输入的数据为: {text}')
                                        english_title = text.replace('.', ' ')
                                        invalid_characters = ''
                                        for char in english_title:
                                            if not re.match(english_pattern, char):
                                                invalid_characters += char
                                        print("不匹配的字符：", invalid_characters)
                                        if invalid_characters != '':
                                            QMessageBox.warning(widget, '警告',
                                                                '您输入的英文名称包含非英文字符或符号\n有以下这些：' + '|'.join(
                                                                    invalid_characters) + '\n请重新核对后再生成标准命名')
                                            return

                                    else:
                                        print('未输入任何数据')
                                        self.debugBrowserTV.append('未输入任何数据')
                                        english_title = ''
                        print(original_title, english_title, year, other_names_sorted, category,
                              actors_list)
                        print("获取Pt-Gen关键信息成功")
                        self.debugBrowserTV.append("获取Pt-Gen关键信息成功")
                        is_first = True
                        for data in actors_list:  # 把演员名转化成str
                            if is_first:
                                actors += data
                                is_first = False
                            else:
                                actors += ' / '
                                actors += data

                        for data in other_names_sorted:  # 把别名转化为str
                            other_titles += data
                            other_titles += ' / '
                        other_titles = other_titles[: -3]
                    get_video_info_success, output = get_video_info(video_path)
                    if get_video_info_success:
                        print("获取到关键参数：" + str(output))
                        self.debugBrowserTV.append("获取到关键参数：" + str(output))
                        video_format = output[0]
                        video_codec = output[1]
                        bit_depth = output[2]
                        hdr_format = output[3]
                        frame_rate = output[4]
                        audio_codec = output[5]
                        channels = output[6]
                    source = self.sourceTV.currentText()
                    team = self.teamTV.currentText()
                    print("关键参数赋值成功")
                    self.debugBrowserTV.append("关键参数赋值成功")
                    english_title = delete_season_number(english_title, season_number)
                    main_title = get_name_from_template(english_title, original_title, season, "", year, video_format,
                                                        source, video_codec, bit_depth, hdr_format, frame_rate,
                                                        audio_codec, channels, team, other_titles, season_number,
                                                        total_episode, "", category, actors, "main_title_tv")
                    main_title = main_title.replace('_', ' ')
                    main_title = re.sub(r'\s+', ' ', main_title)  # 将连续的空格变成一个
                    print(main_title)
                    second_title = get_name_from_template(english_title, original_title, season, "", year, video_format,
                                                          source, video_codec, bit_depth, hdr_format, frame_rate,
                                                          audio_codec, channels, team, other_titles, season_number,
                                                          total_episode, "", category, actors, "second_title_tv")
                    second_title = second_title.replace(' /  | ', ' | ')  # 避免单别名导致的错误
                    print("SecondTitle" + second_title)
                    file_name = get_name_from_template(english_title, original_title, season, '@@', year, video_format,
                                                       source, video_codec, bit_depth, hdr_format, frame_rate,
                                                       audio_codec, channels, team, other_titles, season_number,
                                                       total_episode, "", category, actors, "file_name_tv")
                    file_name = re.sub(r'[<>:\"/\\|?*\s]', '.', file_name)
                    file_name = re.sub(r'\.{2,}', '.', file_name)  # 将连续的'.'变成一个
                    if second_confirm_file_name:
                        text, ok = QInputDialog.getText(self, '确认',
                                                        '请确认文件名称，如有问题请修改（@@表示集数，请勿删除）',
                                                        QLineEdit.EchoMode.Normal,
                                                        file_name)
                        if ok:
                            print(f'您确认文件名为: {text}')
                            self.debugBrowserTV.append(f'您确认文件名为: {text}')
                            file_name = text
                        else:
                            print('您点了取消确认，重命名已取消')
                            self.debugBrowserTV.append('您点了取消确认，重命名已取消')
                            return
                    if is_filename_too_long(file_name):
                        text, ok = QInputDialog.getText(self, '警告',
                                                        '文件名过长，请修改文件名称！', QLineEdit.EchoMode.Normal,
                                                        file_name)
                        if ok:
                            print(f'您修改文件名为: {text}')
                            self.debugBrowserTV.append(f'您修改文件名为: {text}')
                            file_name = text
                        else:
                            print('您点了取消确认，重命名已取消')
                            self.debugBrowserTV.append('您点了取消确认，重命名已取消')
                            return
                        if is_filename_too_long(file_name):
                            QMessageBox.warning(widget, '警告',
                                                '您输入的文件名过长，请重新核对后再生成标准命名！')
                            self.debugBrowserTV.append('您输入的文件名过长，请重新核对后再生成标准命名！')
                            return
                    print("FileName" + file_name)
                    self.mainTitleBrowserTV.setText(main_title)
                    self.secondTitleBrowserTV.setText(second_title)
                    self.fileNameBrowserTV.setText(file_name)
                    if do_rename_file:
                        print("对文件重新命名")
                        self.debugBrowserTV.append("开始对文件重新命名")
                        i = episode_start_number
                        for video_file in video_files:
                            e = str(i)
                            while len(e) < len(str(episode_start_number + episode_num - 1)):
                                e = '0' + e
                            if len(e) == 1:
                                e = '0' + e
                            rename_file_success, output = rename_file(video_file, file_name.replace('@@', e))
                            if rename_file_success:
                                self.videoPathTV.setText(output)
                                video_path = output
                                self.debugBrowserTV.append("视频成功重新命名为：" + video_path)
                            else:
                                self.debugBrowserTV.append("重命名失败：" + output)
                            i += 1
                        print("对文件夹重新命名")
                        self.debugBrowserTV.append("开始对文件夹重新命名")
                        rename_directory_success, output = rename_directory(os.path.dirname(video_path), file_name.
                                                                            replace('E@@', '').
                                                                            replace('@@', ''))
                        if rename_directory_success:
                            self.videoPathTV.setText(output)
                            video_path = output
                            self.debugBrowserTV.append("视频地址成功重新命名为：" + video_path)
                        else:
                            self.debugBrowserTV.append("重命名失败：" + output)
                else:
                    self.debugBrowserTV.append("您的视频文件路径有误")
            else:
                self.debugBrowserTV.append("未成功获取到任何Pt-Gen信息：" + response)
        except Exception as e:
            print(f"启动PtGen线程成功，但是重命名出错：{e}")
            return False, [f"启动PtGen线程成功，但是重命名出错：{e}"]

    def make_torrent_button_tv_clicked(self):
        self.torrent_url = ''
        is_video_path, video_path = check_path_and_find_video(
            self.videoPathTV.text().replace('file:///', ''))  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            torrent_storage_path = str(get_settings("torrent_storage_path"))
            folder_path = os.path.dirname(video_path)
            self.debugBrowserTV.append("开始将" + folder_path + "制作种子，储存在" + torrent_storage_path)
            self.make_torrent_thread = MakeTorrentThread(folder_path, torrent_storage_path)
            self.make_torrent_thread.result_signal.connect(self.handle_make_torrent_tv_result)  # 连接信号
            self.make_torrent_thread.start()  # 启动线程
            self.debugBrowserTV.append("制作种子线程启动成功，正在后台制作种子，请耐心等待种子制作完毕...")
        else:
            self.debugBrowserTV.append("制作种子失败：" + video_path)

    def handle_make_torrent_tv_result(self, get_success, response):
        if get_success:
            self.torrent_url = f'http://127.0.0.1:{get_settings("api_port")}/api/getFile?filePath={response}'
            self.debugBrowserTV.append("成功制作种子：" + response)
        else:
            self.debugBrowserTV.append("制作种子失败：" + response)

    # 以上是TV页面的代码
    # 以下是Playlet页面的代码

    def start_button_playlet_clicked(self):
        if get_settings("second_confirm_file_name"):
            self.debugBrowserMovie.append("如需一键启动，请到设置关闭二次确认文件名功能")
            return
        self.get_name_button_playlet_clicked()
        QApplication.processEvents()  # 处理所有挂起的事件，更新页面
        time.sleep(0)  # 等待 0 毫秒
        self.get_picture_button_playlet_clicked()
        QApplication.processEvents()  # 再次处理事件
        time.sleep(0)  # 等待 2000 毫秒
        self.upload_cover_button_playlet_clicked()
        QApplication.processEvents()  # 再次处理事件
        time.sleep(2)  # 等待 2000 毫秒
        self.get_media_info_button_playlet_clicked()
        QApplication.processEvents()  # 处理事件
        time.sleep(2)  # 等待 2000 毫秒
        self.make_torrent_button_playlet_clicked()
        QApplication.processEvents()  # 处理事件

    def auto_feed_button_playlet_clicked(self):
        mian_title, second_title, description, media_info, file_name, category, team, source = '', '', '', '', '', '', '', ''
        mian_title += self.mainTitleBrowserPlaylet.toPlainText()
        second_title += self.secondTitleBrowserPlaylet.toPlainText()
        description += self.descriptionBrowserPlaylet.toPlainText()
        media_info += self.mediainfoBrowserPlaylet.toPlainText()
        file_name += self.fileNameBrowserPlaylet.toPlainText()
        category += "短剧"
        team = self.teamPlaylet.currentText()
        source = self.sourcePlaylet.currentText()
        auto_feed_link = get_auto_feed_link(mian_title, second_title, description, media_info, file_name, category,
                                            team, source, self.torrent_url)
        self.debugBrowserPlaylet.append("auto_feed_link: " + auto_feed_link)
        pyperclip.copy(auto_feed_link)
        self.debugBrowserPlaylet.append("auto_feed链接已经复制到剪切板，请粘贴到浏览器访问")
        if get_settings("open_auto_feed_link"):
            webbrowser.open(auto_feed_link)

    def get_description_playlet_clicked(self):
        try:
            self.descriptionBrowserPlaylet.setText('')
            original_title = self.originalNameEditPlaylet.text()
            if original_title:
                year, area, category, language = '', '', '', ''
                year += self.yearEditPlaylet.text()
                area += self.areaPlaylet.currentText()
                category = self.get_category()
                language += self.languagePlaylet.currentText()
                season_number = self.seasonBoxPlaylet.text()
                self.descriptionBrowserPlaylet.append(
                    get_playlet_description(original_title, year, area, category, language, season_number))
            else:
                self.debugBrowserPlaylet.append('您没有填写资源名称！')
        except Exception as e:
            print(f"获取简介出错：{e}")
            return False, [f"获取简介出错：{e}"]

    def upload_cover_button_playlet_clicked(self):
        cover_path = self.coverPathPlaylet.text()
        if cover_path and cover_path != '':
            self.debugBrowserPlaylet.append("上传封面" + cover_path)
            picture_bed_path = get_settings("picture_bed_api_url")  # 图床地址
            picture_bed_token = get_settings("picture_bed_api_token")  # 图床Token
            self.debugBrowserPlaylet.append("图床参数获取成功，图床地址是：" + picture_bed_path)

            self.upload_cover_thread = UploadPictureThread(picture_bed_path, picture_bed_token, cover_path, True, False)
            self.upload_cover_thread.result_signal.connect(self.handle_upload_picture_playlet_result)  # 连接信号
            self.upload_cover_thread.start()  # 启动线程
            print("上传图床线程启动")
            self.debugBrowserPlaylet.append("上传图床线程启动，请耐心等待图床Api的响应...")
        else:
            self.debugBrowserPlaylet.append("封面路径为空")

    def get_picture_button_playlet_clicked(self):
        self.pictureUrlBrowserPlaylet.setText("")
        is_video_path, video_path = check_path_and_find_video(
            self.videoPathPlaylet.text().replace('file:///', ''))  # 视频资源的路径

        if is_video_path == 1 or is_video_path == 2:
            self.debugBrowserPlaylet.append("获取视频" + video_path + "的截图")
            screenshot_storage_path = get_settings("screenshot_storage_path")  # 截图储存路径
            picture_bed_path = get_settings("picture_bed_api_url")  # 图床地址
            picture_bed_token = get_settings("picture_bed_api_token")  # 图床Token
            screenshot_number = int(get_settings("screenshot_number"))
            screenshot_threshold = float(get_settings("screenshot_threshold"))
            screenshot_start_percentage = float(get_settings("screenshot_start_percentage"))
            screenshot_end_percentage = float(get_settings("screenshot_end_percentage"))
            do_get_thumbnail = bool(get_settings("do_get_thumbnail"))
            thumbnail_rows = int(get_settings("thumbnail_rows"))
            thumbnail_cols = int(get_settings("thumbnail_cols"))
            auto_upload_screenshot = bool(get_settings("auto_upload_screenshot"))
            self.debugBrowserPlaylet.append("图床参数获取成功，图床地址是：" + picture_bed_path + "\n开始执行截图函数")
            print("参数获取成功，开始执行截图函数")
            res = []
            screenshot_success, response = get_screenshot(video_path, screenshot_storage_path, screenshot_number,
                                                          screenshot_threshold, screenshot_start_percentage,
                                                          screenshot_end_percentage, screenshot_min_interval=0.01)
            print("成功获取截图函数的返回值")
            self.debugBrowserPlaylet.append("成功获取截图函数的返回值")
            if do_get_thumbnail:
                get_thumbnail_success, thumbnail_path = get_thumbnail(video_path, screenshot_storage_path,
                                                                      thumbnail_rows,
                                                                      thumbnail_cols, screenshot_start_percentage,
                                                                      screenshot_end_percentage)
                if get_thumbnail_success:
                    res.append(thumbnail_path)
            if screenshot_success:
                res = response + res
                self.debugBrowserPlaylet.append("成功获取截图：" + str(res))
                # 判断是否需要上传图床
                if auto_upload_screenshot:
                    print("开始自动上传截图到图床：" + picture_bed_path)
                    self.debugBrowserPlaylet.append("开始自动上传截图到图床：" + picture_bed_path)
                    self.pictureUrlBrowserPlaylet.setText("")
                    if len(res) > 0:
                        if do_get_thumbnail and len(res) == 1:
                            self.upload_picture_thread0 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[0],
                                                                              False, True)
                        else:
                            self.upload_picture_thread0 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[0],
                                                                              False, False)
                        self.upload_picture_thread0.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread0.start()  # 启动线程
                        print("启动线程0")
                    if len(res) > 1:
                        if do_get_thumbnail and len(res) == 2:
                            self.upload_picture_thread1 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[1],
                                                                              False, True)
                        else:
                            self.upload_picture_thread1 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[1],
                                                                              False, False)
                        self.upload_picture_thread1.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread1.start()  # 启动线程
                        print("启动线程1")
                    if len(res) > 2:
                        if do_get_thumbnail and len(res) == 3:
                            self.upload_picture_thread2 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[2],
                                                                              False, True)
                        else:
                            self.upload_picture_thread2 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[2],
                                                                              False, False)
                        self.upload_picture_thread2.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread2.start()  # 启动线程
                        print("启动线程2")
                    if len(res) > 3:
                        if do_get_thumbnail and len(res) == 4:
                            self.upload_picture_thread3 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[3],
                                                                              False, True)
                        else:
                            self.upload_picture_thread3 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[3],
                                                                              False, False)
                        self.upload_picture_thread3.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread3.start()  # 启动线程
                        print("启动线程3")
                    if len(res) > 4:
                        if do_get_thumbnail and len(res) == 5:
                            self.upload_picture_thread4 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[4],
                                                                              False, True)
                        else:
                            self.upload_picture_thread4 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[4],
                                                                              False, False)
                        self.upload_picture_thread4.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread4.start()  # 启动线程
                        print("启动线程4")
                    if len(res) > 5:
                        if do_get_thumbnail and len(res) == 6:
                            self.upload_picture_thread5 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[5],
                                                                              False, True)
                        else:
                            self.upload_picture_thread5 = UploadPictureThread(picture_bed_path, picture_bed_token,
                                                                              res[5],
                                                                              False, False)
                        self.upload_picture_thread5.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread5.start()  # 启动线程
                        print("启动线程5")
                    print("上传图床线程全部启动")
                    self.debugBrowserPlaylet.append("上传图床线程启动，请耐心等待图床Api的响应...")

                else:
                    self.debugBrowserPlaylet.append("未选择自动上传图床功能，图片已储存在本地")
                    screenshot_path = ""
                    for r in res:
                        screenshot_path += r
                        screenshot_path += '\n'
                    self.pictureUrlBrowserMovie.setText(screenshot_path)
            else:
                self.debugBrowserPlaylet.append("截图失败" + str(res))
        else:
            self.debugBrowserPlaylet.append("您的视频文件路径有误")

    def handle_upload_picture_playlet_result(self, upload_success, api_response, screenshot_path, is_cover):
        # 这个函数用于处理上传的结果，它将在主线程中被调用
        # 更新UI，显示上传结果等
        print('is_cover ', is_cover)
        print("接受到线程请求的结果")
        self.debugBrowserPlaylet.append("接受到线程请求的结果")
        if upload_success:
            self.pictureUrlBrowserPlaylet.append(api_response)
            paste_screenshot_url = bool(get_settings("paste_screenshot_url"))
            delete_screenshot = bool(get_settings("delete_screenshot"))
            if paste_screenshot_url:
                if is_cover:
                    temp = self.descriptionBrowserPlaylet.toPlainText()
                    temp = api_response + '\n' + temp
                    self.descriptionBrowserPlaylet.setText(temp)
                    self.debugBrowserPlaylet.append("成功将封面链接粘贴到简介前")
                else:
                    self.descriptionBrowserPlaylet.append(api_response)
                    self.debugBrowserPlaylet.append("成功将图片链接粘贴到简介后")
            if delete_screenshot:
                if not is_cover:
                    if os.path.exists(screenshot_path):
                        # 删除文件
                        os.remove(screenshot_path)
                        print(f"文件 {screenshot_path} 已被删除。")
                        self.debugBrowserPlaylet.append(f"文件 {screenshot_path} 已被删除。")
                    else:
                        print(f"文件 {screenshot_path} 不存在。")
                        self.debugBrowserPlaylet.append(f"文件 {screenshot_path} 不存在。")
        else:
            self.debugBrowserPlaylet.append("图床响应无效：" + api_response)

    def select_cover_folder_button_playlet_clicked(self):
        path = get_picture_file_path()
        self.coverPathPlaylet.setText(path)

    def select_video_folder_button_playlet_clicked(self):
        path = get_folder_path()
        self.videoPathPlaylet.setText(path)

    def get_media_info_button_playlet_clicked(self):
        self.mediainfoBrowserPlaylet.setText("")
        is_video_path, video_path = check_path_and_find_video(
            self.videoPathPlaylet.text().replace('file:///', ''))  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            get_media_info_success, mediainfo = get_media_info(video_path)
            if get_media_info_success:
                self.mediainfoBrowserPlaylet.setText(mediainfo)
                self.mediainfoBrowserPlaylet.append('\n')
                self.debugBrowserPlaylet.append("成功获取到MediaInfo")
            else:
                self.debugBrowserPlaylet.append(mediainfo)
        else:
            self.debugBrowserPlaylet.append("您的视频文件路径有误")

    def get_name_button_playlet_clicked(self):
        try:
            self.get_description_playlet_clicked()
            original_title = self.originalNameEditPlaylet.text()
            english_title = ''
            english_pattern = r'^[A-Za-z\-\—\:\s\(\)\'\"\@\#\$\%\^\&\*\!\?\,\.\;\[\]\{\}\|\<\>\`\~\d\u2160-\u2188]+$'
            widget = QWidget(self)
            if original_title != '':
                if not re.match(english_pattern, original_title):
                    ok = QMessageBox.information(self, '资源名称不是英文',
                                                 '资源的名称是：' + original_title + '\n是否使用汉语拼音作为英文名称？（仅限中文）',
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    print('你的选择是', ok)
                    if ok == QMessageBox.StandardButton.Yes:
                        english_title = chinese_name_to_pinyin(original_title)
                    if not re.match(english_pattern, english_title):
                        print("first_english_name does not match the english_pattern.")
                        if ok == QMessageBox.StandardButton.Yes:
                            QMessageBox.warning(widget, '警告', '资源名称不是汉语，无法使用汉语拼音')
                        text, ok = QInputDialog.getText(self, '输入资源的英文名称',
                                                        'Pt-Gen未检测到英文名称，请注意使用英文标点符号')
                        if ok:
                            print(f'您输入的数据为: {text}')
                            self.debugBrowserTV.append(f'您输入的数据为: {text}')
                            english_title = text.replace('.', ' ')
                            invalid_characters = ''
                            for char in english_title:
                                if not re.match(english_pattern, char):
                                    invalid_characters += char
                            print("不匹配的字符：", invalid_characters)
                            if invalid_characters != '':
                                QMessageBox.warning(widget, '警告',
                                                    '您输入的英文名称包含非英文字符或符号\n有以下这些：' + '|'.join(
                                                        invalid_characters) + '\n请重新核对后再生成标准命名')
                                return
                        else:
                            print('未输入任何数据')
                            self.debugBrowserTV.append('未输入任何数据')
                            english_title = ''
                year = self.yearEditPlaylet.text()
                season = self.seasonBoxPlaylet.text()
                total_episode = ""
                episode_num = 0
                episode_start_number = int(self.episodeStartBoxPlaylet.text())
                season_number = season
                if len(season) < 2:
                    season = '0' + season
                video_format = ""
                video_codec = ""
                bit_depth = ""
                hdr_format = ""
                frame_rate = ""
                audio_codec = ""
                channels = ""
                playlet_source = ""
                do_rename_file = get_settings("rename_file")
                second_confirm_file_name = get_settings("second_confirm_file_name")
                is_video_path, video_path = check_path_and_find_video(
                    self.videoPathPlaylet.text().replace('file:///', ''))  # 获取视频的路径
                get_video_info_success, response = get_video_info(video_path)  # 通过视频获取视频的MI参数
                print(get_video_info_success, response)
                if is_video_path == 2:  # 视频路径是文件夹
                    get_video_files_success, video_files = get_video_files(
                        self.videoPathPlaylet.text().replace('file:///', ''))  # 获取文件夹内部的所有文件
                    if get_video_files_success:
                        print('检测到以下文件：', video_files)
                        episode_num = len(video_files)  # 获取视频文件的总数
                        if episode_start_number == 1:
                            total_episode = '全' + str(episode_num) + '集'
                        else:
                            if str(episode_start_number) == str(episode_start_number + episode_num - 1):
                                total_episode = '第' + str(episode_start_number) + '集'
                            else:
                                total_episode = '第' + str(episode_start_number) + '-' + str(
                                    episode_start_number + episode_num - 1) + '集'
                    if get_video_info_success:
                        self.debugBrowserPlaylet.append("获取到关键参数：" + str(response))
                        video_format = response[0]
                        video_codec = response[1]
                        bit_depth = response[2]
                        hdr_format = response[3]
                        frame_rate = response[4]
                        audio_codec = response[5]
                        channels = response[6]
                    source = self.sourcePlaylet.currentText()
                    team = self.teamPlaylet.currentText()
                    playlet_source += self.playletSource.currentText()
                    print("收费类型、来源和小组参数获取成功")
                    self.debugBrowserPlaylet.append("收费类型、来源和小组参数获取成功")
                    category = self.get_category()
                    print('类型为：' + category)
                    self.debugBrowserPlaylet.append('类型为：' + category)
                    main_title = get_name_from_template(english_title, original_title, season, "", year, video_format,
                                                        source, video_codec, bit_depth, hdr_format, frame_rate,
                                                        audio_codec,
                                                        channels, team, "", season_number, total_episode,
                                                        playlet_source,
                                                        category,
                                                        "", "main_title_playlet")
                    main_title = re.sub(r'\s+', ' ', main_title)  # 将连续的空格变成一个
                    print(main_title)
                    second_title = get_name_from_template(english_title, original_title, season, "", year, video_format,
                                                          source, video_codec, bit_depth, hdr_format, frame_rate,
                                                          audio_codec, channels, team, "", season_number, total_episode,
                                                          playlet_source,
                                                          category, "", "second_title_playlet")
                    print("SecondTitle" + second_title)
                    # NPC我要跟你谈恋爱 | 全95集 | 2023年 | 网络收费短剧 | 类型：剧集 爱情
                    file_name = get_name_from_template(english_title, original_title, season, '@@', year, video_format,
                                                       source, video_codec, bit_depth, hdr_format, frame_rate,
                                                       audio_codec, channels, team, "", season_number, total_episode,
                                                       playlet_source,
                                                       category, "", "file_name_playlet")
                    file_name = re.sub(r'[<>:\"/\\|?*\s]', '.', file_name)
                    file_name = re.sub(r'\.{2,}', '.', file_name)  # 将连续的'.'变成一个
                    if second_confirm_file_name:
                        text, ok = QInputDialog.getText(self, '确认',
                                                        '请确认文件名称，如有问题请修改（@@表示集数，请勿删除）',
                                                        QLineEdit.EchoMode.Normal, file_name)
                        if ok:
                            print(f'您确认文件名为: {text}')
                            self.debugBrowserPlaylet.append(f'您确认文件名为: {text}')
                            file_name = text
                        else:
                            print('您点了取消确认，重命名已取消')
                            self.debugBrowserPlaylet.append('您点了取消确认，重命名已取消')
                            return
                    if is_filename_too_long(file_name):
                        text, ok = QInputDialog.getText(self, '警告',
                                                        '文件名过长，请修改文件名称！', QLineEdit.EchoMode.Normal,
                                                        file_name)
                        if ok:
                            print(f'您修改文件名为: {text}')
                            self.debugBrowserPlaylet.append(f'您修改文件名为: {text}')
                            file_name = text
                        else:
                            print('您点了取消确认，重命名已取消')
                            self.debugBrowserPlaylet.append('您点了取消确认，重命名已取消')
                            return
                        if is_filename_too_long(file_name):
                            widget = QWidget(self)
                            QMessageBox.warning(widget, '警告',
                                                '您输入的文件名过长，请重新核对后再生成标准命名！')
                            self.debugBrowserPlaylet.append('您输入的文件名过长，请重新核对后再生成标准命名！')
                            return
                    print("FileName" + file_name)
                    self.mainTitleBrowserPlaylet.setText(main_title)
                    self.secondTitleBrowserPlaylet.setText(second_title)
                    self.fileNameBrowserPlaylet.setText(file_name)
                    if do_rename_file:
                        print("对文件重新命名")
                        self.debugBrowserPlaylet.append("开始对文件重新命名")
                        i = episode_start_number
                        for video_file in video_files:
                            e = str(i)
                            while len(e) < len(str(episode_start_number + episode_num - 1)):
                                e = '0' + e
                            if len(e) == 1:
                                e = '0' + e
                            rename_file_success, response = rename_file(video_file,
                                                                        file_name.replace('@@', e))

                            if rename_file_success:
                                self.videoPathPlaylet.setText(response)
                                video_path = response
                                self.debugBrowserPlaylet.append("视频成功重新命名为：" + video_path)
                            else:
                                self.debugBrowserPlaylet.append("重命名失败：" + response)
                            i += 1

                        print("对文件夹重新命名")
                        self.debugBrowserPlaylet.append("开始对文件夹重新命名")
                        rename_directory_success, response = rename_directory(os.path.dirname(video_path), file_name.
                                                                              replace('E@@', '').
                                                                              replace('@@', ''))
                        if rename_directory_success:
                            self.videoPathPlaylet.setText(response)
                            video_path = response
                            self.debugBrowserPlaylet.append("视频地址成功重新命名为：" + video_path)
                        else:
                            self.debugBrowserPlaylet.append("重命名失败：" + response)
                else:
                    self.debugBrowserPlaylet.append("您的视频文件路径有误")
            else:
                self.debugBrowserPlaylet.append('获取中文名失败')
        except Exception as e:
            print(f"获取命名出错：{e}")
            return False, [f"获取命名出错：{e}"]

    def make_torrent_button_playlet_clicked(self):
        self.torrent_url = ''
        is_video_path, video_path = check_path_and_find_video(
            self.videoPathPlaylet.text().replace('file:///', ''))  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            torrent_storage_path = str(get_settings("torrent_storage_path"))
            folder_path = os.path.dirname(video_path)
            self.debugBrowserPlaylet.append("开始将" + folder_path + "制作种子，储存在" + torrent_storage_path)
            self.make_torrent_thread = MakeTorrentThread(folder_path, torrent_storage_path)
            self.make_torrent_thread.result_signal.connect(self.handle_make_torrent_result_playlet)  # 连接信号
            self.make_torrent_thread.start()  # 启动线程
            self.debugBrowserPlaylet.append("制作种子线程启动成功，正在后台制作种子，请耐心等待种子制作完毕...")
        else:
            self.debugBrowserPlaylet.append("制作种子失败：" + video_path)

    def handle_make_torrent_result_playlet(self, get_success, response):
        if get_success:
            self.torrent_url = f'http://127.0.0.1:{get_settings("api_port")}/api/getFile?filePath={response}'
            self.debugBrowserPlaylet.append("成功制作种子：" + response)
        else:
            self.debugBrowserPlaylet.append("制作种子失败：" + response)

    def get_category(self):
        category = ''
        if self.checkBox_0.isChecked():
            category += '剧情 '
        if self.checkBox_1.isChecked():
            category += '爱情 '
        if self.checkBox_2.isChecked():
            category += '喜剧 '
        if self.checkBox_3.isChecked():
            category += '甜虐 '
        if self.checkBox_4.isChecked():
            category += '甜宠 '
        if self.checkBox_5.isChecked():
            category += '恐怖 '
        if self.checkBox_6.isChecked():
            category += '动作 '
        if self.checkBox_7.isChecked():
            category += '穿越 '
        if self.checkBox_8.isChecked():
            category += '重生 '
        if self.checkBox_9.isChecked():
            category += '逆袭 '
        if self.checkBox_10.isChecked():
            category += '科幻 '
        if self.checkBox_11.isChecked():
            category += '武侠 '
        if self.checkBox_12.isChecked():
            category += '都市 '
        if self.checkBox_13.isChecked():
            category += '古装 '
        if self.checkBox_14.isChecked():
            category += '神豪 '
        if self.checkBox_15.isChecked():
            category += '霸总 '
        if category != "":
            category = category[: -1]
            category = category.replace(' ', ' / ')
        return category

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
            self.screenshotStoragePath.setText(path)

    def selectTorrentPathButtonClicked(self):
        path = get_folder_path()
        if path != '':
            self.torrentStoragePath.setText(path)

    def getSettings(self):
        self.screenshotStoragePath.setText(str(get_settings("screenshot_storage_path")))
        self.torrentStoragePath.setText(str(get_settings("torrent_storage_path")))
        self.ptGenApiUrl.setText(get_settings("pt_gen_api_url"))
        self.pictureBedApiUrl.setText(get_settings("picture_bed_api_url"))
        self.pictureBedApiToken.setText(get_settings("picture_bed_api_token"))
        self.screenshotNumber.setValue(int(get_settings("screenshot_number")))
        self.screenshotThreshold.setValue(float(get_settings("screenshot_threshold")))
        self.screenshotStartPercentage.setValue(float(get_settings("screenshot_start_percentage")))
        self.screenshotEndPercentage.setValue(float(get_settings("screenshot_end_percentage")))
        self.doGetThumbnail.setChecked(bool(get_settings("do_get_thumbnail")))
        self.thumbnailRows.setValue(int(get_settings("thumbnail_rows")))
        self.thumbnailCols.setValue(int(get_settings("thumbnail_cols")))
        self.thumbnailDelay.setValue(float(get_settings("thumbnail_delay")))
        self.autoUploadScreenshot.setChecked(bool(get_settings("auto_upload_screenshot")))
        self.pasteScreenshotUrl.setChecked(bool(get_settings("paste_screenshot_url")))
        self.deleteScreenshot.setChecked(bool(get_settings("delete_screenshot")))
        self.mediaInfoSuffix.setChecked(bool(get_settings("media_info_suffix")))
        self.makeDir.setChecked(bool(get_settings("make_dir")))
        self.renameFile.setChecked(bool(get_settings("rename_file")))
        self.secondConfirmFileName.setChecked(bool(get_settings("second_confirm_file_name")))
        self.enableApi.setChecked(bool(get_settings("enable_api")))
        self.apiPort.setValue(int(get_settings("api_port")))
        self.mainTitleMovie.setText(str(get_settings("main_title_movie")))
        self.secondTitleMovie.setText(str(get_settings("second_title_movie")))
        self.fileNameMovie.setText(str(get_settings("file_name_movie")))
        self.mainTitleTV.setText(str(get_settings("main_title_tv")))
        self.secondTitleTV.setText(str(get_settings("second_title_tv")))
        self.fileNameTV.setText(str(get_settings("file_name_tv")))
        self.mainTitlePlaylet.setText(str(get_settings("main_title_playlet")))
        self.secondTitlePlaylet.setText(str(get_settings("second_title_playlet")))
        self.fileNamePlaylet.setText(str(get_settings("file_name_playlet")))
        self.autoFeedLink.setText(str(get_settings("auto_feed_link")))
        self.openAutoFeedLink.setChecked(bool(get_settings("open_auto_feed_link")))

    def updateSettings(self):
        update_settings("screenshot_storage_path", self.screenshotStoragePath.text())
        update_settings("torrent_storage_path", self.torrentStoragePath.text())
        update_settings("pt_gen_api_url", self.ptGenApiUrl.text())
        update_settings("picture_bed_api_url", self.pictureBedApiUrl.text())
        update_settings("picture_bed_api_token", self.pictureBedApiToken.text())
        update_settings("screenshot_number", str(self.screenshotNumber.text()))
        update_settings("screenshot_threshold", str(self.screenshotThreshold.text()))
        update_settings("screenshot_start_percentage", str(self.screenshotStartPercentage.text()))
        update_settings("screenshot_end_percentage", str(self.screenshotEndPercentage.text()))
        if self.doGetThumbnail.isChecked():
            update_settings("do_get_thumbnail", "True")
        else:
            update_settings("do_get_thumbnail", "")
        update_settings("thumbnail_rows", str(self.thumbnailRows.text()))
        update_settings("thumbnail_cols", str(self.thumbnailCols.text()))
        update_settings("thumbnail_delay", str(self.thumbnailDelay.text()))
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
        if self.mediaInfoSuffix.isChecked():
            update_settings("media_info_suffix", "True")
        else:
            update_settings("media_info_suffix", "")
        if self.makeDir.isChecked():
            update_settings("make_dir", "True")
        else:
            update_settings("make_dir", "")
        if self.renameFile.isChecked():
            update_settings("rename_file", "True")
        else:
            update_settings("rename_file", "")
        if self.secondConfirmFileName.isChecked():
            update_settings("second_confirm_file_name", "True")
        else:
            update_settings("second_confirm_file_name", "")
        if self.enableApi.isChecked():
            update_settings("enable_api", "True")
        else:
            update_settings("enable_api", "")
        update_settings("api_port", self.apiPort.text())
        update_settings("main_title_movie", self.mainTitleMovie.text())
        update_settings("second_title_movie", self.secondTitleMovie.text())
        update_settings("file_name_movie", self.fileNameMovie.text())
        update_settings("main_title_tv", self.mainTitleTV.text())
        update_settings("second_title_tv", self.secondTitleTV.text())
        update_settings("file_name_tv", self.fileNameTV.text())
        update_settings("main_title_playlet", self.mainTitlePlaylet.text())
        update_settings("second_title_playlet", self.secondTitlePlaylet.text())
        update_settings("file_name_playlet", self.fileNamePlaylet.text())
        update_settings("auto_feed_link", self.autoFeedLink.toPlainText())
        if self.openAutoFeedLink.isChecked():
            update_settings("open_auto_feed_link", "True")
        else:
            update_settings("open_auto_feed_link", "")

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
            get_pt_gen_description_success, response = get_pt_gen_description(self.api_url, self.resource_url)

            # 发送信号，包括请求的结果
            print("Pt-Gen请求成功，开始返回结果")
            self.result_signal.emit(get_pt_gen_description_success, response)
            print("返回结果成功")
        except Exception as e:
            print(f"异常发生: {e}")
            # 这里可以发射一个包含错误信息的信号


class UploadPictureThread(QThread):
    # 创建一个信号，用于在数据处理完毕后与主线程通信
    result_signal = pyqtSignal(bool, str, str, bool, bool)

    def __init__(self, picture_bed_api_path, picture_bed_api_token, picture_path, is_cover, is_thumbnail):
        super().__init__()
        self.picture_bed_api_path = picture_bed_api_path
        self.picture_bed_api_token = picture_bed_api_token
        self.picture_path = picture_path
        self.is_cover = is_cover
        self.is_thumbnail = is_thumbnail
        print("上传图床初始化完成")

    def run(self):
        try:
            if self.is_thumbnail:
                time.sleep(float(get_settings("thumbnail_delay")))  # 等待
            # 这里放置耗时的HTTP请求操作
            upload_picture_success, response = upload_picture(self.picture_bed_api_path, self.picture_bed_api_token,
                                                              self.picture_path)

            # 发送信号，包括请求的结果
            print("上传图床成功，开始返回结果")
            self.result_signal.emit(upload_picture_success, response, self.picture_path, self.is_cover,
                                    self.is_thumbnail)
            print("返回结果成功")
        except Exception as e:
            print(f"异常发生: {e}")
            self.result_signal.emit(False, f"异常发生: {e}", self.picture_path)
            # 这里可以发射一个包含错误信息的信号


class MakeTorrentThread(QThread):
    # 创建一个信号，用于在数据处理完毕后与主线程通信
    result_signal = pyqtSignal(bool, str)

    def __init__(self, path, torrent_storage_path):
        super().__init__()
        self.path = path
        self.torrent_storage_path = torrent_storage_path

    def run(self):
        try:
            # 这里放置耗时的制作torrent操作
            make_torrent_success, response = make_torrent(self.path, self.torrent_storage_path)

            # 发送信号
            print("Torrent请求成功，开始等待返回结果")
            self.result_signal.emit(make_torrent_success, response)
            print("返回结果成功")
        except Exception as e:
            print(f"异常发生: {e}")
            # 这里可以发射一个包含错误信息的信号


class apiThread(QThread):
    # 创建一个信号，用于在数据处理完毕后与主线程通信
    result_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            print("尝试启动API")
            run_api()
            print("API线程终止")
            self.result_signal.emit("API线程终止")
        except Exception as e:
            print(f"异常发生: {e}")
            self.result_signal.emit(f"异常发生: {e}")
