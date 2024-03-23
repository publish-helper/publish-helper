import datetime
import glob
import json
import os
import random
import re
import shutil
from tkinter import filedialog, Tk

from torf import Torrent
from xpinyin import Pinyin


# 更新settings
def update_settings(parameter_name, value):
    """
    更新 static/settings.json 文件中的数据。
    如果指定的参数不存在，则创建该参数。

    参数:
    parameter_name (str): 参数名称
    value: 要设置的值
    """
    settings_file = 'static/settings.json'
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)

    # 读取现有的设置
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            settings = json.load(file)
    else:
        settings = {}

    # 更新设置
    settings[parameter_name] = value

    # 写回文件
    with open(settings_file, 'w') as file:
        json.dump(settings, file, indent=4)
    print("写入数据" + f"{parameter_name}: {value}")


def get_settings(parameter_name):
    """
    从 static/settings.json 文件中获取特定参数的值。
    如果参数不存在，则创建一个并赋值为标准值。

    参数:
    parameter_name (str): 参数名称

    返回:
    参数的值
    """
    settings_file = 'static/settings.json'

    if not os.path.exists(settings_file):
        # 如果文件不存在，创建一个空的 JSON 文件并设置默认值
        with open(settings_file, 'w', encoding='utf-8') as file:
            default_settings = {
                "screenshot_path": "temp/pic",
                "torrent_path": "temp/torrent",
                "pt_gen_api_url": "https://ptgen.agsvpt.work/",
                "picture_bed_api_url": "https://freeimage.host/api/1/upload",
                "picture_bed_api_token": "6d207e02198a847aa98d0a2a901485a5",
                "screenshot_number": "3",
                "screenshot_threshold": "30.0",
                "screenshot_start_percentage": "0.10",
                "screenshot_end_percentage": "0.90",
                "do_get_thumbnail": "True",
                "thumbnail_rows": "3",
                "thumbnail_cols": "3",
                "thumbnail_delay": "2.0",
                "auto_upload_screenshot": "True",
                "paste_screenshot_url": "True",
                "delete_screenshot": "True",
                "media_info_suffix": "True",
                "make_dir": "True",
                "rename_file": "True",
                "second_confirm_file_name": "True",
                "enable_api": "",
                "api_port": "5372",
                "main_title_movie": "{en_title} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels}-{team}",
                "second_title_movie": "{original_title} / {other_titles} | \u7c7b\u578b\uff1a{category} | \u6f14\u5458\uff1a{actors}",
                "file_name_movie": "{original_title}.{en_title}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}-{team}",
                "main_title_tv": "{en_title} S{season} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels}-{team}",
                "second_title_tv": "{original_title} / {other_titles} | {total_episode} | \u7c7b\u578b\uff1a{category} | \u6f14\u5458\uff1a{actors}",
                "file_name_tv": "{original_title}.{en_title}.S{season}E{episode}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}-{team}",
                "main_title_playlet": "{en_title} S{season} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels}-{team}",
                "second_title_playlet": "{original_title} | \u7b2c{season_number}\u5b63 | {total_episode} | {year}\u5e74 | {type} | \u7c7b\u578b\uff1a{category}",
                "file_name_playlet": "{original_title}.{en_title}.S{season}E{episode}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}-{team}",
                "auto_feed_link": "https://example.com/upload.php#seperator#name#linkstr#{主标题}#linkstr#small_descr#linkstr#{副标题}#linkstr#url#linkstr#{IMDB}#linkstr#dburl#linkstr#{豆瓣}#linkstr#descr#linkstr#{简介}[quote]{MediaInfo}[/quote]#linkstr#log_info#linkstr##linkstr#tracklist#linkstr##linkstr#music_type#linkstr##linkstr#music_media#linkstr##linkstr#edition_info#linkstr##linkstr#music_name#linkstr##linkstr#music_author#linkstr##linkstr#animate_info#linkstr##linkstr#anidb#linkstr##linkstr#torrentName#linkstr##linkstr#images#linkstr##linkstr#torrent_name#linkstr#{种子名称}#linkstr#torrent_url#linkstr##linkstr#type#linkstr#{类型}#linkstr#source_sel#linkstr#{地区}#linkstr#standard_sel#linkstr#{分辨率}#linkstr#audiocodec_sel#linkstr#{音频编码}#linkstr#codec_sel#linkstr#{视频编码}#linkstr#medium_sel#linkstr#{媒介}#linkstr#origin_site#linkstr#{小组}#linkstr#origin_url#linkstr##linkstr#golden_torrent#linkstr#false#linkstr#mediainfo_cmct#linkstr##linkstr#imgs_cmct#linkstr##linkstr#full_mediainfo#linkstr##linkstr#subtitles#linkstr##linkstr#youtube_url#linkstr##linkstr#ptp_poster#linkstr##linkstr#comparisons#linkstr##linkstr#version_info#linkstr##linkstr#multi_mediainfo#linkstr##linkstr#labels#linkstr#0",
                "open_auto_feed_link": "True"
            }
            json.dump(default_settings, file)

    with open(settings_file, 'r', encoding='utf-8') as file:
        settings = json.load(file)

    # 设置参数的标准值
    standard_values = {
        "screenshot_path": "temp/pic",
        "torrent_path": "temp/torrent",
        "pt_gen_api_url": "https://ptgen.agsvpt.work/",
        "picture_bed_api_url": "https://freeimage.host/api/1/upload",
        "picture_bed_api_token": "6d207e02198a847aa98d0a2a901485a5",
        "screenshot_number": "3",
        "screenshot_threshold": "30.0",
        "screenshot_start_percentage": "0.10",
        "screenshot_end_percentage": "0.90",
        "do_get_thumbnail": "True",
        "thumbnail_rows": "3",
        "thumbnail_cols": "3",
        "thumbnail_delay": "2.0",
        "auto_upload_screenshot": "True",
        "paste_screenshot_url": "True",
        "delete_screenshot": "True",
        "media_info_suffix": "True",
        "make_dir": "True",
        "rename_file": "True",
        "second_confirm_file_name": "True",
        "enable_api": "",
        "api_port": "5372",
        "main_title_movie": "{en_title} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels}-{team}",
        "second_title_movie": "{original_title} / {other_titles} | \u7c7b\u578b\uff1a{category} | \u6f14\u5458\uff1a{actors}",
        "file_name_movie": "{original_title}.{en_title}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}-{team}",
        "main_title_tv": "{en_title} S{season} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels}-{team}",
        "second_title_tv": "{original_title} / {other_titles} | {total_episode} | \u7c7b\u578b\uff1a{category} | \u6f14\u5458\uff1a{actors}",
        "file_name_tv": "{original_title}.{en_title}.S{season}E{episode}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}-{team}",
        "main_title_playlet": "{en_title} S{season} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels}-{team}",
        "second_title_playlet": "{original_title} | {total_episode} | {year}\u5e74 | {type} | \u7c7b\u578b\uff1a{category}",
        "file_name_playlet": "{original_title}.{en_title}.S{season}E{episode}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}-{team}",
        "auto_feed_link": "https://example.com/upload.php#seperator#name#linkstr#{主标题}#linkstr#small_descr#linkstr#{副标题}#linkstr#url#linkstr#{IMDB}#linkstr#dburl#linkstr#{豆瓣}#linkstr#descr#linkstr#{简介}[quote]{MediaInfo}[/quote]#linkstr#log_info#linkstr##linkstr#tracklist#linkstr##linkstr#music_type#linkstr##linkstr#music_media#linkstr##linkstr#edition_info#linkstr##linkstr#music_name#linkstr##linkstr#music_author#linkstr##linkstr#animate_info#linkstr##linkstr#anidb#linkstr##linkstr#torrentName#linkstr##linkstr#images#linkstr##linkstr#torrent_name#linkstr#{种子名称}#linkstr#torrent_url#linkstr##linkstr#type#linkstr#{类型}#linkstr#source_sel#linkstr#{地区}#linkstr#standard_sel#linkstr#{分辨率}#linkstr#audiocodec_sel#linkstr#{音频编码}#linkstr#codec_sel#linkstr#{视频编码}#linkstr#medium_sel#linkstr#{媒介}#linkstr#origin_site#linkstr#{小组}#linkstr#origin_url#linkstr##linkstr#golden_torrent#linkstr#false#linkstr#mediainfo_cmct#linkstr##linkstr#imgs_cmct#linkstr##linkstr#full_mediainfo#linkstr##linkstr#subtitles#linkstr##linkstr#youtube_url#linkstr##linkstr#ptp_poster#linkstr##linkstr#comparisons#linkstr##linkstr#version_info#linkstr##linkstr#multi_mediainfo#linkstr##linkstr#labels#linkstr#0",
        "open_auto_feed_link": "True"
    }

    # 如果参数名在标准值中，但不存在于当前设置中，将其添加到当前设置中
    if parameter_name in standard_values and parameter_name not in settings:
        settings[parameter_name] = standard_values[parameter_name]
        with open(settings_file, 'w') as file:
            json.dump(settings, file)

    parameter_value = settings.get(parameter_name, "")
    print("读取数据" + f"{parameter_name}: {parameter_value}")

    return parameter_value


def rename_file_with_same_extension(old_name, new_name_without_extension):
    new_name_without_extension = re.sub(r'[<>:\"/\\|?*]', '.', new_name_without_extension)
    # 分割原始文件名以获取扩展名和目录
    file_dir, file_base = os.path.split(old_name)
    file_name, file_extension = os.path.splitext(file_base)

    # 构建新文件名，保留原扩展名
    new_name = file_dir + '/' + new_name_without_extension + file_extension

    # 重命名文件
    try:
        os.rename(old_name, new_name)
        print(old_name, "文件成功重命名为", new_name)
        return True, new_name
    except FileNotFoundError:
        print(f"未找到文件: '{old_name}'")
        return False, f"未找到文件: '{old_name}'"
    except OSError as e:
        print(f"重命名文件时出错: {e}")
        return False, f"重命名文件时出错: {e}"


def rename_directory(current_dir, new_name):
    """
    对目标文件夹进行重命名。

    参数:
    current_dir: str - 当前文件夹的完整路径。
    new_name: str - 新的文件夹名称。

    异常:
    ValueError - 如果提供的路径不是一个目录或不存在。
    OSError - 如果重命名操作失败。
    """
    try:
        new_name = re.sub(r'[<>:\"/\\|?*]', '.', new_name)
        # 检查当前路径是否为一个存在的目录
        if not os.path.isdir(current_dir):
            print("提供的路径不是一个目录或不存在。")
            raise ValueError("提供的路径不是一个目录或不存在。")

        # 获取当前目录的父目录
        parent_dir = os.path.dirname(current_dir)
        # 构造新的目录路径
        new_dir = parent_dir + '/' + new_name

        # 重命名目录
        os.rename(current_dir, new_dir)
        print(f"目录已重命名为: {new_dir}")
        return True, new_dir
    except OSError as e:
        # 捕获并打印任何操作系统错误
        print(f"重命名目录时发生错误: {e}")
        return False, f"重命名目录时发生错误: {e}"


def move_file_to_folder(file_name, folder_name):
    """
    将文件移动到同目录下的指定文件夹中，除非文件已在该文件夹中。

    参数:
    file_name (str): 要移动的文件名。
    folder_name (str): 目标文件夹名称。
    """
    # 获取文件的目录和文件名
    print("开始移动文件", file_name, folder_name)
    file_dir, file_base = os.path.split(file_name)
    print(file_base, file_dir)

    # 检查文件是否已在目标文件夹中
    if os.path.basename(file_dir) == folder_name:
        print(f"文件 '{file_name}' 已在 '{folder_name}' 中，无需移动。")
        return False, f"文件 '{file_name}' 已在 '{folder_name}' 中，无需移动。"

    # 目标文件夹的完整路径
    target_folder = file_dir + '/' + folder_name

    # 如果目标文件夹不存在，创建它
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 构建目标文件路径
    target_file = target_folder + '/' + file_base

    # 移动文件
    try:
        shutil.move(file_name, target_file)
        print(f"文件 '{file_name}' 已成功移动到 '{target_file}'")
        return True, target_file
    except Exception as e:
        print(f"移动文件时出错: {e}")
        return False, f"移动文件时出错: {e}"


# 此方法用于自动生成一个不易重复的图片文件名称
def generate_image_filename(base_path):
    now = datetime.datetime.now()
    date_time = now.strftime("%Y%m%d-%H%M%S")
    letters = random.sample('0123456789', 6)
    random_str = ''.join(letters)
    filename = f"{date_time}-{random_str}.png"
    path = base_path + '/' + filename
    return path


def get_picture_file_path():
    # 设置文件类型过滤器
    file_types = [('Picture files', '*.gif;*.png;*.jpg;*.jpeg;*.webp;*.avif;*.bmp;*.apng)'),
                  ('All files', '*.*')]

    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=file_types)

    # 返回选择的文件路径
    return file_path


def get_video_file_path():
    # 设置文件类型过滤器
    file_types = [('Video files', '*.mp4;*.m4v;*.avi;*.flv;*.mkv;*.mpeg;*.mpg;*.rm;*.rmvb;*.ts;*.m2ts'),
                  ('All files', '*.*')]

    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=file_types)

    # 返回选择的文件路径
    return file_path


def get_folder_path():
    # 创建一个 Tkinter 根窗口，但不显示
    root = Tk()
    root.withdraw()

    # 打开文件夹选择对话框
    folder_path = filedialog.askdirectory(title="Select a folder")

    # 关闭根窗口
    root.destroy()

    # 返回选择的文件夹路径
    return folder_path


def check_path_and_find_video(path):
    # 指定的视频文件类型列表
    video_extensions = [".mp4", ".m4v", ".avi", ".flv", ".mkv", ".mpeg", ".mpg", ".rm", ".rmvb", ".ts", ".m2ts"]

    # 如果最后一位加了'/'则默认去除
    if path.endswith('/'):
        path = path[:-1]

    # 如果最前面加了'file:///'则默认去除
    if path.startswith('file:///'):
        path = path.replace('file:///', '', 1)

    # 检查路径是否是一个文件
    if os.path.isfile(path):
        if any(path.endswith(ext) for ext in video_extensions):
            return 1, path  # 是文件且符合视频类型
        print(f'路径下获取到文件{path}，但该文件不符合视频类型。')
        return 0, f'路径下获取到文件{path}，但该文件不符合视频类型。'  # 是文件，但不符合视频类型

    # 检查路径是否是一个文件夹
    elif os.path.isdir(path):
        for file in os.listdir(path):
            if any(file.endswith(ext) for ext in video_extensions):
                print(path + file)
                return 2, path + '/' + file  # 在文件夹中找到符合类型的视频文件
        print('文件夹中没有符合类型的视频文件。')
        return 0, '文件夹中没有符合类型的视频文件。'  # 文件夹中没有符合类型的视频文件

    else:
        print('您提供的路径既不是文件也不是文件夹。')
        return 0, '您提供的路径既不是文件也不是文件夹。'  # 路径既不是文件也不是文件夹


def get_playlet_description(original_title, year, area, category, language, season):
    if season != '1':
        original_title += ' 第' + num_to_chinese(int(season)) + '季'
    return f'\n◎片　　名　{original_title}\n◎年　　代　{year}\n◎产　　地　{area}\n◎类　　别　{category}\n◎语　　言　{language}\n◎简　　介　\n'


def create_torrent(folder_path, torrent_path):
    print(folder_path + '  ' + torrent_path)
    try:
        # 检查路径是否存在
        if not os.path.exists(folder_path):
            raise ValueError("Provided folder path does not exist.")

        # 检查路径是否指向一个非空目录或一个文件
        if os.path.isdir(folder_path) and not os.listdir(folder_path):
            raise ValueError("Provided folder path is empty.")

        # 构造完整的torrent文件路径
        torrent_file_name = os.path.basename(folder_path.rstrip("/\\")) + '.torrent'
        torrent_file_path = torrent_path + '/' + torrent_file_name

        # 确保torrent文件的目录存在
        os.makedirs(os.path.dirname(torrent_file_path), exist_ok=True)

        # 如果目标 Torrent 文件已存在，则删除它
        if os.path.exists(torrent_file_path):
            os.remove(torrent_file_path)

        # 获取当前时间
        current_time = datetime.datetime.now()

        # 创建 Torrent 对象，添加当前时间作为创建时间
        t = Torrent(path=folder_path, trackers=['http://tracker.example.com/announce'], created_by='Publish Helper',
                    creation_date=current_time)

        # 生成和写入 Torrent 文件
        t.generate()
        t.write(torrent_file_path)

        print(f"Torrent created: {torrent_file_path}")
        return True, torrent_file_path

    except (OSError, IOError, ValueError) as e:
        # 捕获并处理文件操作相关的异常和值错误
        print(f"Error occurred: {e}")
        return False, str(e)

    except Exception as e:
        # 捕获所有其他异常
        print(f"An unexpected error occurred: {e}")
        return False, str(e)


def load_names(file_path, name):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data[name]


def chinese_name_to_pinyin(chinese_name):
    p = Pinyin()
    result = ''
    py = p.get_pinyin(chinese_name)
    s = py.split('-')
    for c in s:
        result += c.capitalize()
        result += ' '
    result = filter_string(result)
    result = result.replace(' :', ':')
    result = result.replace('( ', '(')
    result = result.replace(' )', ')')
    result = re.sub(r'\s+', ' ', result)  # 将连续的空格变成一个
    return result


def filter_string(original_str):
    # 使用正则表达式匹配允许的字符
    pattern = r"[A-Za-z\-\—\:\s\(\)\'\"\@\#\$\%\^\&\*\!\?\,\.\;\[\]\{\}\|\<\>\`\~\d\u2160-\u2188]+"

    # 找到所有匹配的字符
    matches = re.findall(pattern, original_str)

    # 将所有匹配的字符组合成一个新字符串
    filtered_str = ''.join(matches)
    return filtered_str


def natural_keys(text):
    """
    alist.sort(key=natural_keys) 使用这个函数作为key来按数字顺序排序文本
    """
    return [int(c) if c.isdigit() else c.lower() for c in re.split('(\d+)', text)]


def get_video_files(folder_path):
    try:
        # 要查找的视频文件扩展名列表
        video_extensions = [".mp4", ".m4v", ".avi", ".flv", ".mkv", ".mpeg", ".mpg", ".rm", ".rmvb", ".ts", ".m2ts"]

        # 检查文件夹路径是否有效和可访问
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise ValueError(f"您提供的路径 '{folder_path}' 不是一个有效的目录。")

        # 初始化一个空列表来存储文件路径
        video_files = []

        # 遍历每个扩展名，并将匹配的文件添加到列表中
        for extension in video_extensions:
            # Glob模式匹配文件
            pattern = os.path.join(folder_path, '*' + extension)
            # 查找匹配的文件并扩展列表
            video_files.extend(glob.glob(pattern))

        # 使用自定义的natural_keys函数进行排序
        video_files.sort(key=natural_keys)

        return True, video_files

    except Exception as e:
        # 返回错误信息
        return False, [f"错误：{e}"]


def int_to_roman(num):
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syms = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syms[i]
            num -= val[i]
        i += 1
    return roman_num


def int_to_special_roman(num):
    special_roman_dict = {
        1: 'Ⅰ',
        2: 'Ⅱ',
        3: 'Ⅲ',
        4: 'Ⅳ',
        5: 'Ⅴ',
        6: 'Ⅵ',
        7: 'Ⅶ',
        8: 'Ⅷ',
        9: 'Ⅸ',
        10: 'Ⅹ',
    }
    if num in special_roman_dict:
        return special_roman_dict[num]
    else:
        return str(num)


def num_to_chinese(num):
    if num < 0 or num > 9999:
        return "数字超出范围"

    digits = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    units = ["", "十", "百", "千"]
    parts = []

    if num == 0:
        return digits[0]

    # 处理千位到个位
    unit_index = 0
    while num > 0:
        digit = num % 10
        if digit > 0:
            parts.append(digits[digit] + units[unit_index])
        elif len(parts) > 0 and parts[-1] != digits[0]:
            parts.append(digits[0])
        num //= 10
        unit_index += 1

    # 处理完毕后，parts 数组是倒序的，需要反转回来
    return ''.join(parts[::-1])


def is_filename_too_long(filename):
    max_filename_length = 250  # Windows下文件名最长为255，去除掉后缀名为250
    if len(filename) > max_filename_length:
        return True
    else:
        return False
