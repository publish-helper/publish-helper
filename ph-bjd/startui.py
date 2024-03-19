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
from picturebed import upload_screenshot
from ptgen import fetch_and_format_ptgen_data
from rename import extract_details_from_ptgen, get_video_info, get_name_from_example
from screenshot import extract_complex_keyframes, get_thumbnail
from tool import update_settings, get_settings, get_video_file_path, rename_file_with_same_extension, \
    move_file_to_folder, \
    get_folder_path, check_path_and_find_video, rename_directory, create_torrent, load_names, chinese_name_to_pinyin, \
    get_video_files, get_picture_file_path, int_to_roman, int_to_special_roman, is_filename_too_long
from ui.mainwindow import Ui_Mainwindow
from ui.settings import Ui_Settings


def start_ui():
    app = QApplication(sys.argv)
    my_mainwindow = mainwindow()
    my_ico = QIcon("static/ph-bjd.ico")
    my_mainwindow.setWindowIcon(my_ico)
    my_mainwindow.show()
    sys.exit(app.exec())


def git_clicked():
    webbrowser.open('https://github.com/bjdbjd/publish-helper')


class mainwindow(QMainWindow, Ui_Mainwindow):
    def __init__(self):
        super().__init__()

        self.my_settings = None
        self.setupUi(self)  # 设置界面

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
            "程序初始化成功，使用前请查看设置中的说明！\n制作不易，如有帮助请帮忙点亮仓库的Star！\n地址：https://github.com/bjdbjd/publish-helper")

    def initialize_team_combobox(self):
        team_names = load_names('static/team.json', 'team')
        for name in team_names:
            self.teamMovie.addItem(name)
            self.teamTV.addItem(name)
            self.teamPlaylet.addItem(name)

    def initialize_source_combobox(self):
        source_names = load_names('static/source.json', 'source')
        for name in source_names:
            self.sourceMovie.addItem(name)
            self.sourceTV.addItem(name)
            self.sourcePlaylet.addItem(name)

    def initialize_type_combobox(self):
        type_names = load_names('static/type.json', 'type')
        for name in type_names:
            self.typePlaylet.addItem(name)

    def settings_clicked(self):  # click对应的槽函数
        self.my_settings = settings()
        self.my_settings.getSettings()
        my_ico = QIcon("static/ph-bjd.ico")
        self.my_settings.setWindowIcon(my_ico)
        self.my_settings.show()  # 加上self避免页面一闪而过

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
        mian_title, second_title, description, media_info, file_name, type, team, source = '', '', '', '', '', '', '', ''
        mian_title = self.mainTitleBrowserMovie.toPlainText()
        second_title = self.secondTitleBrowserMovie.toPlainText()
        description = self.ptGenBrowserMovie.toPlainText()
        media_info = self.mediainfoBrowserMovie.toPlainText()
        file_name = self.fileNameBrowserMovie.toPlainText()
        type = "电影"
        team = self.teamMovie.currentText()
        source = self.sourceMovie.currentText()
        auto_feed_link = get_auto_feed_link(mian_title, second_title, description, media_info, file_name, type, team,
                                            source)
        self.debugBrowserMovie.append("auto_feed_link: " + auto_feed_link)
        pyperclip.copy(auto_feed_link)
        self.debugBrowserMovie.append("auto_feed链接已经复制到剪切板，请粘贴到浏览器访问")
        if get_settings("open_auto_feed_link"):
            webbrowser.open(auto_feed_link)

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
            picture_bed_path = get_settings("picture_bed_path")  # 图床地址
            picture_bed_token = get_settings("picture_bed_token")  # 图床Token
            screenshot_number = int(get_settings("screenshot_number"))
            screenshot_threshold = float(get_settings("screenshot_threshold"))
            screenshot_start = float(get_settings("screenshot_start"))
            screenshot_end = float(get_settings("screenshot_end"))
            get_thumbnails = bool(get_settings("get_thumbnails"))
            rows = int(get_settings("rows"))
            cols = int(get_settings("cols"))
            auto_upload_screenshot = bool(get_settings("auto_upload_screenshot"))
            self.debugBrowserMovie.append("图床参数获取成功，图床地址是：" + picture_bed_path + "\n开始执行截图函数")
            print("参数获取成功，开始执行截图函数")
            res = []
            screenshot_success, response = extract_complex_keyframes(video_path, screenshot_path, screenshot_number,
                                                                     screenshot_threshold, screenshot_start,
                                                                     screenshot_end, min_interval_pct=0.01)
            print("成功获取截图函数的返回值")
            self.debugBrowserMovie.append("成功获取截图函数的返回值")
            if get_thumbnails:
                get_thumbnails_success, sv_path = get_thumbnail(video_path, screenshot_path, rows, cols,
                                                                screenshot_start, screenshot_end)
                if get_thumbnails_success:
                    res.append(sv_path)
            if screenshot_success:
                res = response + res
                self.debugBrowserMovie.append("成功获取截图：" + str(res))
                # 判断是否需要上传图床
                if auto_upload_screenshot:
                    self.debugBrowserMovie.append("开始自动上传截图到图床" + picture_bed_path)
                    self.pictureUrlBrowserMovie.setText("")
                    if len(res) > 0:
                        self.upload_picture_thread0 = UploadPictureThread(picture_bed_path, picture_bed_token, res[0],
                                                                          False)
                        self.upload_picture_thread0.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread0.start()  # 启动线程
                        if get_thumbnails and len(res) == 2:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 1:
                        self.upload_picture_thread1 = UploadPictureThread(picture_bed_path, picture_bed_token, res[1],
                                                                          False)
                        self.upload_picture_thread1.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread1.start()  # 启动线程
                        if get_thumbnails and len(res) == 3:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 2:
                        self.upload_picture_thread2 = UploadPictureThread(picture_bed_path, picture_bed_token, res[2],
                                                                          False)
                        self.upload_picture_thread2.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread2.start()  # 启动线程
                        if get_thumbnails and len(res) == 4:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 3:
                        self.upload_picture_thread3 = UploadPictureThread(picture_bed_path, picture_bed_token, res[3],
                                                                          False)
                        self.upload_picture_thread3.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread3.start()  # 启动线程
                        if get_thumbnails and len(res) == 5:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 4:
                        self.upload_picture_thread4 = UploadPictureThread(picture_bed_path, picture_bed_token, res[4],
                                                                          False)
                        self.upload_picture_thread4.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread4.start()  # 启动线程
                        if get_thumbnails and len(res) == 6:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 5:
                        self.upload_picture_thread5 = UploadPictureThread(picture_bed_path, picture_bed_token, res[5],
                                                                          False)
                        self.upload_picture_thread5.result_signal.connect(
                            self.handle_upload_picture_movie_result)  # 连接信号
                        self.upload_picture_thread5.start()  # 启动线程
                    print("上传图床线程启动")
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
        path = get_video_file_path()
        self.videoPathMovie.setText(path)

    def select_video_folder_button_movie_clicked(self):
        path = get_folder_path()
        self.videoPathMovie.setText(path)

    def get_media_info_button_movie_clicked(self):
        self.mediainfoBrowserMovie.setText("")
        is_video_path, video_path = check_path_and_find_video(self.videoPathMovie.text())  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            get_media_info_success, mediainfo = get_media_info(video_path)
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
            pt_gen_path = get_settings("pt_gen_path")
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
                self.ptGenBrowserMovie.setText(response)
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
                rename_file = get_settings("rename_file")
                second_confirm_file_name = get_settings("second_confirm_file_name")
                is_video_path, video_path = check_path_and_find_video(self.videoPathMovie.text())
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
                            original_title, en_title, year, other_names_sorted, category, actors_list = extract_details_from_ptgen(
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
                        print(original_title, en_title, year, other_names_sorted, category, actors_list)
                        self.debugBrowserMovie.append(
                            "分析后的结果为：" + original_title + en_title + year + str(other_names_sorted) + category +
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
                        if en_title == '':
                            ok = QMessageBox.information(self, 'Pt-Gen未获取到英文名称',
                                                         '资源的名称是：' + original_title + '\n是否使用汉语拼音作为英文名称？（仅限中文）',
                                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                            print('你的选择是', ok)
                            if ok == QMessageBox.StandardButton.Yes:
                                en_title = chinese_name_to_pinyin(original_title)
                            if not re.match(english_pattern, en_title):
                                print("first_english_name does not match the english_pattern.")
                                if ok == QMessageBox.StandardButton.Yes:
                                    QMessageBox.warning(widget, '警告', '资源名称不是汉语，无法使用汉语拼音')
                                text, ok = QInputDialog.getText(self, '输入资源的英文名称',
                                                                'Pt-Gen未检测到英文名称，请注意使用英文标点符号')
                                if ok:
                                    print(f'您输入的数据为: {text}')
                                    self.debugBrowserMovie.append(f'您输入的数据为: {text}')
                                    en_title = text.replace('.', ' ')
                                    invalid_characters = ''
                                    for char in en_title:
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
                                    en_title = ''
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
                    main_title = get_name_from_example(en_title, original_title, "", "", year,
                                                       video_format, source, video_codec, bit_depth, hdr_format,
                                                       frame_rate, audio_codec, channels, team, other_titles, "",
                                                       "", "", category, actors, "main_title_movie")
                    main_title = main_title.replace('_', ' ')
                    main_title = re.sub(r'\s+', ' ', main_title)  # 将连续的空格变成一个
                    print(main_title)
                    second_title = get_name_from_example(en_title, original_title, "", "", year, video_format,
                                                         source, video_codec, bit_depth, hdr_format, frame_rate,
                                                         audio_codec, channels, team, other_titles, "", "", "",
                                                         category, actors, "second_title_movie")
                    second_title = second_title.replace(' /  | ', ' | ')  # 避免单别名导致的错误
                    print("SecondTitle" + second_title)
                    file_name = get_name_from_example(en_title, original_title, "", "", year, video_format,
                                                      source, video_codec, bit_depth, hdr_format, frame_rate,
                                                      audio_codec, channels, team, other_titles, "", "",
                                                      "",
                                                      category, actors, "file_name_movie")
                    file_name = file_name.replace(' – ', '.')
                    file_name = file_name.replace(' - ', '.')
                    file_name = file_name.replace('_', '.')
                    file_name = file_name.replace(': ', '.')
                    file_name = file_name.replace(' ', '.')
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
                    if rename_file and is_video_path == 1:
                        print("开始对文件重新命名")
                        self.debugBrowserMovie.append("开始对文件重新命名")
                        rename_file_success, output = rename_file_with_same_extension(video_path, file_name)
                        if rename_file_success:
                            self.videoPathMovie.setText(output)
                            video_path = output
                            self.debugBrowserMovie.append("视频成功重新命名为：" + video_path)
                        else:
                            self.debugBrowserMovie.append("重命名失败：" + output)
                    if rename_file and is_video_path == 2:
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
        is_video_path, video_path = check_path_and_find_video(self.videoPathMovie.text())  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            torrent_path = str(get_settings("torrent_path"))
            folder_path = os.path.dirname(video_path)
            self.debugBrowserMovie.append("开始将" + folder_path + "制作种子，储存在" + torrent_path)
            self.make_torrent_thread = MakeTorrentThread(folder_path, torrent_path)
            self.make_torrent_thread.result_signal.connect(self.handle_make_torrent_movie_result)  # 连接信号
            self.make_torrent_thread.start()  # 启动线程
            self.debugBrowserMovie.append("制作种子线程启动成功，正在后台制作种子，请耐心等待种子制作完毕...")
        else:
            self.debugBrowserMovie.append("制作种子失败：" + video_path)

    def handle_make_torrent_movie_result(self, get_success, response):
        if get_success:
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
        mian_title, second_title, description, media_info, file_name, type, team, source = '', '', '', '', '', '', '', ''
        mian_title = self.mainTitleBrowserTV.toPlainText()
        second_title = self.secondTitleBrowserTV.toPlainText()
        description = self.ptGenBrowserTV.toPlainText()
        media_info = self.mediainfoBrowserTV.toPlainText()
        file_name = self.fileNameBrowserTV.toPlainText()
        type = "剧集"
        team = self.teamTV.currentText()
        source = self.sourceTV.currentText()
        auto_feed_link = get_auto_feed_link(mian_title, second_title, description, media_info, file_name, type, team,
                                            source)
        self.debugBrowserTV.append("auto_feed_link: " + auto_feed_link)
        pyperclip.copy(auto_feed_link)
        self.debugBrowserTV.append("auto_feed链接已经复制到剪切板，请粘贴到浏览器访问")
        if get_settings("open_auto_feed_link"):
            webbrowser.open(auto_feed_link)

    def get_pt_gen_button_tv_clicked(self):
        self.ptGenBrowserTV.setText("")
        pt_gen_path = get_settings("pt_gen_path")
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
                self.ptGenBrowserTV.setText(response)
                self.debugBrowserTV.append("成功获取Pt-Gen信息")
            else:
                self.debugBrowserTV.append("获取Pt-Gen信息失败")
        else:
            self.debugBrowserTV.append("未成功获取到任何Pt-Gen信息" + response)

    def get_picture_button_tv_clicked(self):
        self.pictureUrlBrowserTV.setText("")
        is_video_path, video_path = check_path_and_find_video(self.videoPathTV.text())  # 视频资源的路径

        if is_video_path == 1 or is_video_path == 2:
            self.debugBrowserTV.append("获取视频" + video_path + "的截图")
            screenshot_path = get_settings("screenshot_path")  # 截图储存路径
            picture_bed_path = get_settings("picture_bed_path")  # 图床地址
            picture_bed_token = get_settings("picture_bed_token")  # 图床Token
            screenshot_number = int(get_settings("screenshot_number"))
            screenshot_threshold = float(get_settings("screenshot_threshold"))
            screenshot_start = float(get_settings("screenshot_start"))
            screenshot_end = float(get_settings("screenshot_end"))
            get_thumbnails = bool(get_settings("get_thumbnails"))
            rows = int(get_settings("rows"))
            cols = int(get_settings("cols"))
            auto_upload_screenshot = bool(get_settings("auto_upload_screenshot"))
            self.debugBrowserTV.append("图床参数获取成功，图床地址是：" + picture_bed_path + "\n开始执行截图函数")
            print("参数获取成功，开始执行截图函数")
            res = []
            screenshot_success, response = extract_complex_keyframes(video_path, screenshot_path, screenshot_number,
                                                                     screenshot_threshold, screenshot_start,
                                                                     screenshot_end, min_interval_pct=0.01)
            print("成功获取截图函数的返回值")
            self.debugBrowserTV.append("成功获取截图函数的返回值")
            if get_thumbnails:
                get_thumbnails_success, sv_path = get_thumbnail(video_path, screenshot_path, rows, cols,
                                                                screenshot_start, screenshot_end)
                if get_thumbnails_success:
                    res.append(sv_path)
            if screenshot_success:
                res = response + res
                self.debugBrowserTV.append("成功获取截图：" + str(res))
                # 判断是否需要上传图床
                if auto_upload_screenshot:
                    self.debugBrowserTV.append("开始自动上传截图到图床" + picture_bed_path)
                    self.pictureUrlBrowserTV.setText("")
                    if len(res) > 0:
                        self.upload_picture_thread0 = UploadPictureThread(picture_bed_path, picture_bed_token, res[0],
                                                                          False)
                        self.upload_picture_thread0.result_signal.connect(
                            self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread0.start()  # 启动线程
                        if get_thumbnails and len(res) == 2:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 1:
                        self.upload_picture_thread1 = UploadPictureThread(picture_bed_path, picture_bed_token, res[1],
                                                                          False)
                        self.upload_picture_thread1.result_signal.connect(
                            self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread1.start()  # 启动线程
                        if get_thumbnails and len(res) == 3:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 2:
                        self.upload_picture_thread2 = UploadPictureThread(picture_bed_path, picture_bed_token, res[2],
                                                                          False)
                        self.upload_picture_thread2.result_signal.connect(
                            self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread2.start()  # 启动线程
                        if get_thumbnails and len(res) == 4:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 3:
                        self.upload_picture_thread3 = UploadPictureThread(picture_bed_path, picture_bed_token, res[3],
                                                                          False)
                        self.upload_picture_thread3.result_signal.connect(
                            self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread3.start()  # 启动线程
                        if get_thumbnails and len(res) == 5:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 4:
                        self.upload_picture_thread4 = UploadPictureThread(picture_bed_path, picture_bed_token, res[4],
                                                                          False)
                        self.upload_picture_thread4.result_signal.connect(
                            self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread4.start()  # 启动线程
                        if get_thumbnails and len(res) == 6:
                            time.sleep(1)  # 等待 1000 毫秒
                    if len(res) > 5:
                        self.upload_picture_thread5 = UploadPictureThread(picture_bed_path, picture_bed_token, res[5],
                                                                          False)
                        self.upload_picture_thread5.result_signal.connect(
                            self.handle_upload_picture_tv_result)  # 连接信号
                        self.upload_picture_thread5.start()  # 启动线程
                    print("上传图床线程启动")
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
                self.ptGenBrowserTV.append(api_response)
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
        is_video_path, video_path = check_path_and_find_video(self.videoPathTV.text())  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            get_media_info_success, mediainfo = get_media_info(video_path)
            if get_media_info_success:
                self.mediainfoBrowserTV.setText(mediainfo)
                self.mediainfoBrowserTV.append('\n')
                self.debugBrowserTV.append("成功获取到MediaInfo")
            else:
                self.debugBrowserTV.append(mediainfo)
        else:
            self.debugBrowserTV.append("您的视频文件路径有误")

    def get_name_button_tv_clicked(self):
        try:
            self.ptGenBrowserTV.setText("")
            pt_gen_path = get_settings("pt_gen_path")
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
                self.ptGenBrowserTV.setText(response)
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
                episode_start = int(self.episodeStartBoxTV.text())
                lowercase_season_info_without_spaces = ' season' + season  # 用于后期替换多余的season名称
                uppercase_season_info_without_spaces = ' Season' + season  # 用于后期替换多余的Season名称
                lowercase_season_info_with_spaces = ' season ' + season  # 用于后期替换多余的season名称
                uppercase_season_info_with_spaces = ' Season ' + season  # 用于后期替换多余的Season名称
                main_title_number_season_name = ' ' + season + ' '  # 用于后期替换主标题多余的数字季名称
                file_number_season_name = '.' + season + '.'  # 用于后期替换文件名多余的数字季名称
                main_title_roman_season_name = ' ' + int_to_roman(int(season)) + ' '  # 用于后期替换主标题多余的罗马季名称
                main_title_special_roman_season_name = ' ' + int_to_special_roman(
                    int(season)) + ' '  # 用于后期替换主标题多余的特殊罗马季名称
                file_roman_season_name = '.' + int_to_roman(int(season)) + '.'  # 用于后期替换文件名多余的罗马季名称
                file_special_roman_season_name = '.' + int_to_special_roman(int(season)) + '.'  # 用于后期替换文件名多余的特殊罗马季名称
                print('需要替换的内容：',
                      lowercase_season_info_without_spaces,
                      uppercase_season_info_without_spaces,
                      lowercase_season_info_with_spaces,
                      uppercase_season_info_with_spaces,
                      main_title_number_season_name,
                      file_number_season_name,
                      main_title_roman_season_name,
                      main_title_special_roman_season_name,
                      file_roman_season_name,
                      file_special_roman_season_name)
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
                rename_file = get_settings("rename_file")
                second_confirm_file_name = get_settings("second_confirm_file_name")
                is_video_path, video_path = check_path_and_find_video(self.videoPathTV.text())
                english_pattern = r'^[A-Za-z\-\—\:\s\(\)\'\"\@\#\$\%\^\&\*\!\?\,\.\;\[\]\{\}\|\<\>\`\~\d\u2160-\u2188]+$'
                widget = QWidget(self)
                if is_video_path == 1 or is_video_path == 2:  # 视频路径是文件夹
                    get_video_files_success, video_files = get_video_files(
                        self.videoPathTV.text().replace('file:///', ''))  # 获取文件夹内部的所有文件
                    if get_video_files_success:
                        print('检测到以下文件：', video_files)
                        episode_num = len(video_files)  # 获取视频文件的总数
                        if episode_start == 1:
                            total_episode = '全' + str(episode_num) + '集'
                        else:
                            total_episode = '第' + str(episode_start) + '-' + str(episode_start + episode_num - 1) + '集'
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
                            original_title, en_title, year, other_names_sorted, category, actors_list = extract_details_from_ptgen(
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
                        print(original_title, en_title, year, other_names_sorted, category, actors_list)
                        self.debugBrowserTV.append(
                            "分析后的结果为：" + original_title + en_title + year + str(other_names_sorted) + category +
                            str(actors_list))
                        if year == "" or year is None:
                            print("Pt-Gen分析结果不包含年份，存在错误")
                            self.debugBrowserTV.append("Pt-Gen分析结果不包含年份，存在错误")
                            return
                        if original_title != '':
                            if en_title == '':
                                ok = QMessageBox.information(self, 'Pt-Gen未获取到英文名称',
                                                             '资源的名称是：' + original_title + '\n是否使用汉语拼音作为英文名称？（仅限中文）',
                                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                print('你的选择是', ok)
                                if ok == QMessageBox.StandardButton.Yes:
                                    en_title = chinese_name_to_pinyin(original_title)
                                if not re.match(english_pattern, en_title):
                                    print("first_english_name does not match the english_pattern.")
                                    if ok == QMessageBox.StandardButton.Yes:
                                        QMessageBox.warning(widget, '警告', '资源名称不是汉语，无法使用汉语拼音')
                                    text, ok = QInputDialog.getText(self, '输入资源的英文名称',
                                                                    'Pt-Gen未检测到英文名称，请注意使用英文标点符号')
                                    if ok:
                                        print(f'您输入的数据为: {text}')
                                        self.debugBrowserTV.append(f'您输入的数据为: {text}')
                                        en_title = text.replace('.', ' ')
                                        invalid_characters = ''
                                        for char in en_title:
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
                                        en_title = ''
                        print(original_title, en_title, year, other_names_sorted, category,
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
                    main_title = get_name_from_example(en_title, original_title, season, "", year, video_format,
                                                       source, video_codec, bit_depth, hdr_format, frame_rate,
                                                       audio_codec,
                                                       channels, team, other_titles, season_number, total_episode, "",
                                                       category,
                                                       actors, "main_title_tv")
                    main_title = main_title.replace(lowercase_season_info_without_spaces, '')
                    main_title = main_title.replace(uppercase_season_info_without_spaces, '')
                    main_title = main_title.replace(lowercase_season_info_with_spaces, '')
                    main_title = main_title.replace(uppercase_season_info_with_spaces, '')
                    main_title = main_title.replace('_', ' ')
                    main_title = re.sub(r'\s+', ' ', main_title)  # 将连续的空格变成一个
                    print(main_title)
                    second_title = get_name_from_example(en_title, original_title, season, "", year, video_format,
                                                         source, video_codec, bit_depth, hdr_format, frame_rate,
                                                         audio_codec, channels, team, other_titles, season_number,
                                                         total_episode, "",
                                                         category, actors, "second_title_tv")
                    second_title = second_title.replace(' /  | ', ' | ')  # 避免单别名导致的错误
                    print("SecondTitle" + second_title)
                    file_name = get_name_from_example(en_title, original_title, season, '??', year, video_format,
                                                      source, video_codec, bit_depth, hdr_format, frame_rate,
                                                      audio_codec, '^&*' + channels, team, other_titles, season_number,
                                                      total_episode,
                                                      "",
                                                      category, actors, "file_name_tv")
                    file_name = file_name.replace(lowercase_season_info_without_spaces, '')
                    file_name = file_name.replace(uppercase_season_info_without_spaces, '')
                    file_name = file_name.replace(lowercase_season_info_with_spaces, '')
                    file_name = file_name.replace(uppercase_season_info_with_spaces, '')
                    file_name = file_name.replace(' – ', '.')
                    file_name = file_name.replace(' - ', '.')
                    file_name = file_name.replace('_', '.')
                    file_name = file_name.replace(': ', '.')
                    file_name = file_name.replace(' ', '.')
                    file_name = re.sub(r'\.{2,}', '.', file_name)  # 将连续的'.'变成一个
                    file_name = file_name.replace(file_number_season_name, '.')
                    file_name = file_name.replace(file_roman_season_name, '.')
                    file_name = file_name.replace(file_special_roman_season_name, '.')
                    file_name = file_name.replace('.^&*', '.')  # 防止声道数量被误杀
                    if second_confirm_file_name:
                        text, ok = QInputDialog.getText(self, '确认',
                                                        '请确认文件名称，如有问题请修改', QLineEdit.EchoMode.Normal,
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
                    if rename_file:
                        print("对文件重新命名")
                        self.debugBrowserTV.append("开始对文件重新命名")
                        i = episode_start
                        for video_file in video_files:
                            e = str(i)
                            while len(e) < len(str(episode_start + episode_num - 1)):
                                e = '0' + e
                            if len(e) == 1:
                                e = '0' + e
                            rename_file_success, output = rename_file_with_same_extension(video_file,
                                                                                          file_name.replace('??', e))
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
                                                                            replace('E??', '').
                                                                            replace('??', ''))
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
        is_video_path, video_path = check_path_and_find_video(self.videoPathTV.text())  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            torrent_path = str(get_settings("torrent_path"))
            folder_path = os.path.dirname(video_path)
            self.debugBrowserTV.append("开始将" + folder_path + "制作种子，储存在" + torrent_path)
            self.make_torrent_thread = MakeTorrentThread(folder_path, torrent_path)
            self.make_torrent_thread.result_signal.connect(self.handle_make_torrent_tv_result)  # 连接信号
            self.make_torrent_thread.start()  # 启动线程
            self.debugBrowserTV.append("制作种子线程启动成功，正在后台制作种子，请耐心等待种子制作完毕...")
        else:
            self.debugBrowserTV.append("制作种子失败：" + video_path)

    def handle_make_torrent_tv_result(self, get_success, response):
        if get_success:
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
        mian_title, second_title, description, media_info, file_name, type, team, source = '', '', '', '', '', '', '', ''
        mian_title = self.mainTitleBrowserPlaylet.toPlainText()
        second_title = self.secondTitleBrowserPlaylet.toPlainText()
        description = self.introBrowserPlaylet.toPlainText()
        media_info = self.mediainfoBrowserPlaylet.toPlainText()
        file_name = self.fileNameBrowserPlaylet.toPlainText()
        type = "短剧"
        team = self.teamPlaylet.currentText()
        source = self.sourcePlaylet.currentText()
        auto_feed_link = get_auto_feed_link(mian_title, second_title, description, media_info, file_name, type, team,
                                            source)
        self.debugBrowserPlaylet.append("auto_feed_link: " + auto_feed_link)
        pyperclip.copy(auto_feed_link)
        self.debugBrowserPlaylet.append("auto_feed链接已经复制到剪切板，请粘贴到浏览器访问")
        if get_settings("open_auto_feed_link"):
            webbrowser.open(auto_feed_link)

    def upload_cover_button_playlet_clicked(self):
        cover_path = self.coverPathPlaylet.text()
        if cover_path and cover_path != '':
            self.debugBrowserPlaylet.append("上传封面" + cover_path)
            picture_bed_path = get_settings("picture_bed_path")  # 图床地址
            picture_bed_token = get_settings("picture_bed_token")  # 图床Token
            self.debugBrowserPlaylet.append("图床参数获取成功，图床地址是：" + picture_bed_path)

            self.upload_cover_thread = UploadPictureThread(picture_bed_path, picture_bed_token, cover_path, True)
            self.upload_cover_thread.result_signal.connect(self.handle_upload_picture_playlet_result)  # 连接信号
            self.upload_cover_thread.start()  # 启动线程
            print("上传图床线程启动")
            self.debugBrowserPlaylet.append("上传图床线程启动，请耐心等待图床Api的响应...")
        else:
            self.debugBrowserPlaylet.append("封面路径为空")

    def get_picture_button_playlet_clicked(self):
        self.pictureUrlBrowserPlaylet.setText("")
        is_video_path, video_path = check_path_and_find_video(self.videoPathPlaylet.text())  # 视频资源的路径

        if is_video_path == 1 or is_video_path == 2:
            self.debugBrowserPlaylet.append("获取视频" + video_path + "的截图")
            screenshot_path = get_settings("screenshot_path")  # 截图储存路径
            picture_bed_path = get_settings("picture_bed_path")  # 图床地址
            picture_bed_token = get_settings("picture_bed_token")  # 图床Token
            screenshot_number = int(get_settings("screenshot_number"))
            screenshot_threshold = float(get_settings("screenshot_threshold"))
            screenshot_start = float(get_settings("screenshot_start"))
            screenshot_end = float(get_settings("screenshot_end"))
            get_thumbnails = bool(get_settings("get_thumbnails"))
            rows = int(get_settings("rows"))
            cols = int(get_settings("cols"))
            auto_upload_screenshot = bool(get_settings("auto_upload_screenshot"))
            self.debugBrowserPlaylet.append("图床参数获取成功，图床地址是：" + picture_bed_path + "\n开始执行截图函数")
            print("参数获取成功，开始执行截图函数")
            res = []
            screenshot_success, response = extract_complex_keyframes(video_path, screenshot_path, screenshot_number,
                                                                     screenshot_threshold, screenshot_start,
                                                                     screenshot_end, min_interval_pct=0.01)
            print("成功获取截图函数的返回值")
            self.debugBrowserPlaylet.append("成功获取截图函数的返回值")
            if get_thumbnails:
                get_thumbnails_success, sv_path = get_thumbnail(video_path, screenshot_path, rows, cols,
                                                                screenshot_start, screenshot_end)
                if get_thumbnails_success:
                    res.append(sv_path)
            if screenshot_success:
                res = res + response
                self.debugBrowserPlaylet.append("成功获取截图：" + str(res))
                # 判断是否需要上传图床
                if auto_upload_screenshot:
                    self.debugBrowserPlaylet.append("开始自动上传截图到图床" + picture_bed_path)
                    self.pictureUrlBrowserPlaylet.setText("")
                    if len(res) > 0:
                        self.upload_picture_thread0 = UploadPictureThread(picture_bed_path, picture_bed_token, res[0],
                                                                          False)
                        self.upload_picture_thread0.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread0.start()  # 启动线程
                        if get_thumbnails:
                            time.sleep(0.8)  # 等待 800 毫秒
                    if len(res) > 1:
                        self.upload_picture_thread1 = UploadPictureThread(picture_bed_path, picture_bed_token, res[1],
                                                                          False)
                        self.upload_picture_thread1.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread1.start()  # 启动线程
                    if len(res) > 2:
                        self.upload_picture_thread2 = UploadPictureThread(picture_bed_path, picture_bed_token, res[2],
                                                                          False)
                        self.upload_picture_thread2.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread2.start()  # 启动线程
                    if len(res) > 3:
                        self.upload_picture_thread3 = UploadPictureThread(picture_bed_path, picture_bed_token, res[3],
                                                                          False)
                        self.upload_picture_thread3.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread3.start()  # 启动线程
                    if len(res) > 4:
                        self.upload_picture_thread4 = UploadPictureThread(picture_bed_path, picture_bed_token, res[4],
                                                                          False)
                        self.upload_picture_thread4.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread4.start()  # 启动线程
                    if len(res) > 5:
                        self.upload_picture_thread5 = UploadPictureThread(picture_bed_path, picture_bed_token, res[5],
                                                                          False)
                        self.upload_picture_thread5.result_signal.connect(
                            self.handle_upload_picture_playlet_result)  # 连接信号
                        self.upload_picture_thread5.start()  # 启动线程
                    print("上传图床线程启动")
                    self.debugBrowserPlaylet.append("上传图床线程启动，请耐心等待图床Api的响应...")

                else:
                    self.debugBrowserPlaylet.append("未选择自动上传图床功能，图片已储存在本地")
                    output = ""
                    for r in res:
                        output += r
                        output += '\n'
                    self.pictureUrlBrowserMovie.setText(output)
            else:
                self.debugBrowserPlaylet.append("截图失败" + str(res))
        else:
            self.debugBrowserPlaylet.append("您的视频文件路径有误")

    def handle_upload_picture_playlet_result(self, upload_success, api_response, screenshot_path, is_cover):
        # 这个函数用于处理上传的结果，它将在主线程中被调用
        # 更新UI，显示上传结果等
        print('is_cover', is_cover)
        print("接受到线程请求的结果")
        self.debugBrowserPlaylet.append("接受到线程请求的结果")
        if upload_success:
            self.pictureUrlBrowserPlaylet.append(api_response)
            paste_screenshot_url = bool(get_settings("paste_screenshot_url"))
            delete_screenshot = bool(get_settings("delete_screenshot"))
            if paste_screenshot_url:
                if is_cover:
                    temp = self.introBrowserPlaylet.toPlainText()
                    temp = api_response + '\n' + temp
                    self.introBrowserPlaylet.setText(temp)
                    self.debugBrowserPlaylet.append("成功将封面链接粘贴到简介前")
                else:
                    self.introBrowserPlaylet.append(api_response)
                    self.debugBrowserPlaylet.append("成功将图片链接粘贴到简介后")
            if delete_screenshot:
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
        is_video_path, video_path = check_path_and_find_video(self.videoPathPlaylet.text())  # 视频资源的路径
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

        original_title = self.chineseNameEditPlaylet.text()
        if original_title:

            print('获取中文名成功：' + original_title)
            self.debugBrowserPlaylet.append('获取中文名成功：' + original_title)
            en_title = chinese_name_to_pinyin(original_title)
            year = self.yearEditPlaylet.text()
            season = self.seasonBoxPlaylet.text()
            total_episode = ""
            episode_num = 0
            episode_start = int(self.episodeStartBoxPlaylet.text())
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
            type = ""
            category = ""
            rename_file = get_settings("rename_file")
            second_confirm_file_name = get_settings("second_confirm_file_name")
            is_video_path, video_path = check_path_and_find_video(self.videoPathPlaylet.text())  # 获取视频的路径
            get_video_info_success, output = get_video_info(video_path)  # 通过视频获取视频的MI参数
            print(get_video_info_success, output)
            if is_video_path == 2:  # 视频路径是文件夹
                get_video_files_success, video_files = get_video_files(
                    self.videoPathPlaylet.text().replace('file:///', ''))  # 获取文件夹内部的所有文件
                if get_video_files_success:
                    print('检测到以下文件：', video_files)
                    episode_num = len(video_files)  # 获取视频文件的总数
                    if episode_start == 1:
                        total_episode = '全' + str(episode_num) + '集'
                    else:
                        total_episode = '第' + str(episode_start) + '-' + str(episode_start + episode_num - 1) + '集'
                if get_video_info_success:
                    self.debugBrowserPlaylet.append("获取到关键参数：" + str(output))
                    video_format = output[0]
                    video_codec = output[1]
                    bit_depth = output[2]
                    hdr_format = output[3]
                    frame_rate = output[4]
                    audio_codec = output[5]
                    channels = output[6]
                source = self.sourcePlaylet.currentText()
                team = self.teamPlaylet.currentText()
                type += self.typePlaylet.currentText()
                print("收费类型、来源和小组参数获取成功")
                self.debugBrowserPlaylet.append("收费类型、来源和小组参数获取成功")
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
                if category != "":
                    category = category[: -1]
                    category = category.replace(' ', ' / ')
                print('类型为：' + category)
                self.debugBrowserPlaylet.append('类型为：' + category)
                main_title = get_name_from_example(en_title, original_title, season, "", year, video_format,
                                                   source, video_codec, bit_depth, hdr_format, frame_rate, audio_codec,
                                                   channels, team, "", season_number, total_episode, type, category,
                                                   "", "main_title_playlet")
                main_title = re.sub(r'\s+', ' ', main_title)  # 将连续的空格变成一个
                print(main_title)
                second_title = get_name_from_example(en_title, original_title, season, "", year, video_format,
                                                     source, video_codec, bit_depth, hdr_format, frame_rate,
                                                     audio_codec, channels, team, "", season_number, total_episode,
                                                     type,
                                                     category, "", "second_title_playlet")
                print("SecondTitle" + second_title)
                # NPC我要跟你谈恋爱 | 全95集 | 2023年 | 网络收费短剧 | 类型：剧集 爱情
                file_name = get_name_from_example(en_title, original_title, season, '??', year, video_format,
                                                  source, video_codec, bit_depth, hdr_format, frame_rate,
                                                  audio_codec, channels, team, "", season_number, total_episode, type,
                                                  category, "", "file_name_playlet")
                file_name = file_name.replace(' ', '.')
                file_name = re.sub(r'\.{2,}', '.', file_name)  # 将连续的'.'变成一个
                if second_confirm_file_name:
                    text, ok = QInputDialog.getText(self, '确认', '请确认文件名称，如有问题请修改',
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
                                                    '文件名过长，请修改文件名称！', QLineEdit.EchoMode.Normal, file_name)
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
                if rename_file:
                    print("对文件重新命名")
                    self.debugBrowserPlaylet.append("开始对文件重新命名")
                    i = episode_start
                    for video_file in video_files:
                        e = str(i)
                        while len(e) < len(str(episode_start + episode_num - 1)):
                            e = '0' + e
                        if len(e) == 1:
                            e = '0' + e
                        rename_file_success, output = rename_file_with_same_extension(video_file,
                                                                                      file_name.replace('??', e))

                        if rename_file_success:
                            self.videoPathPlaylet.setText(output)
                            video_path = output
                            self.debugBrowserPlaylet.append("视频成功重新命名为：" + video_path)
                        else:
                            self.debugBrowserPlaylet.append("重命名失败：" + output)
                        i += 1

                    print("对文件夹重新命名")
                    self.debugBrowserPlaylet.append("开始对文件夹重新命名")
                    rename_directory_success, output = rename_directory(os.path.dirname(video_path), file_name.
                                                                        replace('E??', '').
                                                                        replace('??', ''))
                    if rename_directory_success:
                        self.videoPathPlaylet.setText(output)
                        video_path = output
                        self.debugBrowserPlaylet.append("视频地址成功重新命名为：" + video_path)
                    else:
                        self.debugBrowserPlaylet.append("重命名失败：" + output)
            else:
                self.debugBrowserPlaylet.append("您的视频文件路径有误")
        else:
            self.debugBrowserPlaylet.append('获取中文名失败')

    def make_torrent_button_playlet_clicked(self):
        is_video_path, video_path = check_path_and_find_video(self.videoPathPlaylet.text())  # 视频资源的路径
        if is_video_path == 1 or is_video_path == 2:
            torrent_path = str(get_settings("torrent_path"))
            folder_path = os.path.dirname(video_path)
            self.debugBrowserPlaylet.append("开始将" + folder_path + "制作种子，储存在" + torrent_path)
            self.make_torrent_thread = MakeTorrentThread(folder_path, torrent_path)
            self.make_torrent_thread.result_signal.connect(self.handle_make_torrent_result_playlet)  # 连接信号
            self.make_torrent_thread.start()  # 启动线程
            self.debugBrowserPlaylet.append("制作种子线程启动成功，正在后台制作种子，请耐心等待种子制作完毕...")
        else:
            self.debugBrowserPlaylet.append("制作种子失败：" + video_path)

    def handle_make_torrent_result_playlet(self, get_success, response):
        if get_success:
            self.debugBrowserPlaylet.append("成功制作种子：" + response)
        else:
            self.debugBrowserPlaylet.append("制作种子失败：" + response)

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
        self.pictureBedPath.setText(get_settings("picture_bed_path"))
        self.pictureBedToken.setText(get_settings("picture_bed_token"))
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
        self.mediaInfoSuffix.setChecked(bool(get_settings("media_info_suffix")))
        self.makeDir.setChecked(bool(get_settings("make_dir")))
        self.renameFile.setChecked(bool(get_settings("rename_file")))
        self.secondConfirmFileName.setChecked(bool(get_settings("second_confirm_file_name")))
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
        update_settings("screenshot_path", self.screenshotPath.text())
        update_settings("torrent_path", self.torrentPath.text())
        update_settings("pt_gen_path", self.ptGenPath.text())
        update_settings("picture_bed_path", self.pictureBedPath.text())
        update_settings("picture_bed_token", self.pictureBedToken.text())
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
    result_signal = pyqtSignal(bool, str, str, bool)

    def __init__(self, picture_bed_path, picture_bed_token, screenshot_path, is_cover):
        super().__init__()
        self.picture_bed_path = picture_bed_path
        self.picture_bed_token = picture_bed_token
        self.screenshot_path = screenshot_path
        self.is_cover = is_cover

    def run(self):
        try:
            # 这里放置耗时的HTTP请求操作
            upload_success, api_response = upload_screenshot(self.picture_bed_path, self.picture_bed_token,
                                                             self.screenshot_path)

            # 发送信号，包括请求的结果
            print("上传图床成功，开始返回结果")
            self.result_signal.emit(upload_success, api_response, self.screenshot_path, self.is_cover)
            print("返回结果成功")
            # self.result_signal(upload_success,api_response)
        except Exception as e:
            print(f"异常发生: {e}")
            self.result_signal.emit(False, f"异常发生: {e}", self.screenshot_path, self.is_cover)
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
