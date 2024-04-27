import datetime
import glob
import json
import os
import random
import re
import shutil

from torf import Torrent
from xpinyin import Pinyin


# 更新settings
def update_settings(settings_name, settings_data):
    """
    更新 static/settings.json 文件中的数据。
    如果指定的参数不存在，则创建该参数。

    参数:
    parameter_name (str): 参数名称
    value: 要设置的值
    """
    settings_file = combine_directories('static/settings.json')
    os.makedirs(os.path.dirname(settings_file), exist_ok=True)

    # 读取现有的设置
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            settings = json.load(file)
    else:
        settings = {}

    # 更新设置
    settings[settings_name] = settings_data

    # 写回文件
    with open(settings_file, 'w') as file:
        json.dump(settings, file, indent=4)
    print("写入数据" + f"{settings_name}: {settings_data}")


### 写一个方法，取当前工程工作目录与传入的目录，组合成一个新的目录
def combine_directories(path):
    """
    取当前工程工作目录与传入相对路径，生成新的路径

    返回:
    参数的值
    """
    project_dir = os.getcwd()
    return os.path.join(project_dir, path)


def get_settings(settings_name):
    """
    从 static/settings.json 文件中获取特定参数的值。
    如果参数不存在，则创建一个并赋值为标准值。

    参数:
    parameter_name (str): 参数名称

    返回:
    参数的值
    """
    settings_file = combine_directories('static/settings.json')

    if not os.path.exists(settings_file):
        # 如果文件不存在，创建一个空的 JSON 文件并设置默认值
        with open(settings_file, 'w', encoding='utf-8') as file:
            default_settings = {
                "api_port": "5372",
                "auto_feed_link": "https://example.com/upload.php#seperator#name#linkstr#{\u4e3b\u6807\u9898}#linkstr#small_descr#linkstr#{\u526f\u6807\u9898}#linkstr#url#linkstr#{IMDB}#linkstr#dburl#linkstr#{\u8c46\u74e3}#linkstr#descr#linkstr#{\u7b80\u4ecb}[quote]{MediaInfo}[/quote]#linkstr#log_info#linkstr##linkstr#tracklist#linkstr##linkstr#music_type#linkstr##linkstr#music_media#linkstr##linkstr#edition_info#linkstr##linkstr#music_name#linkstr##linkstr#music_author#linkstr##linkstr#animate_info#linkstr##linkstr#anidb#linkstr##linkstr#torrentName#linkstr##linkstr#images#linkstr##linkstr#torrent_name#linkstr#{\u79cd\u5b50\u540d\u79f0}#linkstr#torrent_url#linkstr#{\u79cd\u5b50\u94fe\u63a5}#linkstr#type#linkstr#{\u7c7b\u578b}#linkstr#source_sel#linkstr#{\u5730\u533a}#linkstr#standard_sel#linkstr#{\u5206\u8fa8\u7387}#linkstr#audiocodec_sel#linkstr#{\u97f3\u9891\u7f16\u7801}#linkstr#codec_sel#linkstr#{\u89c6\u9891\u7f16\u7801}#linkstr#medium_sel#linkstr#{\u5a92\u4ecb}#linkstr#origin_site#linkstr#{\u5c0f\u7ec4}#linkstr#origin_url#linkstr##linkstr#golden_torrent#linkstr#false#linkstr#mediainfo_cmct#linkstr##linkstr#imgs_cmct#linkstr##linkstr#full_mediainfo#linkstr##linkstr#subtitles#linkstr##linkstr#youtube_url#linkstr##linkstr#ptp_poster#linkstr##linkstr#comparisons#linkstr##linkstr#version_info#linkstr##linkstr#multi_mediainfo#linkstr##linkstr#labels#linkstr#0",
                "auto_upload_screenshot": True,
                "delete_screenshot": True,
                "do_get_thumbnail": True,
                "enable_api": True,
                "file_name_movie": "{original_title}.{en_title}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}.{audio_num}-{team}",
                "file_name_playlet": "{original_title}.{en_title}.S{season}E{episode}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}.{audio_num}-{team}",
                "file_name_tv": "{original_title}.{en_title}.S{season}E{episode}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}.{audio_num}-{team}",
                "main_title_movie": "{en_title} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels} {audio_num}-{team}",
                "main_title_playlet": "{en_title} S{season} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels} {audio_num}-{team}",
                "main_title_tv": "{en_title} S{season} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels} {audio_num}-{team}",
                "make_dir": True,
                "media_info_suffix": True,
                "open_auto_feed_link": True,
                "paste_screenshot_url": True,
                "picture_bed_api_token": "6d207e02198a847aa98d0a2a901485a5",
                "picture_bed_api_url": "https://freeimage.host/api/1/upload",
                "pt_gen_api_url": "https://ptgen.agsvpt.work/",
                "rename_file": True,
                "screenshot_end_percentage": "0.90",
                "screenshot_number": "3",
                "screenshot_start_percentage": "0.10",
                "screenshot_storage_path": "temp/pic",
                "screenshot_threshold": "30.00",
                "second_confirm_file_name": True,
                "second_title_movie": "{original_title} / {other_titles} | \u7c7b\u578b\uff1a{category} | \u6f14\u5458\uff1a{actors}",
                "second_title_playlet": "{original_title} | {total_episode} | {year}\u5e74 | {playlet_source} | \u7c7b\u578b\uff1a{category}",
                "second_title_tv": "{original_title} / {other_titles} | {total_episode} | \u7c7b\u578b\uff1a{category} | \u6f14\u5458\uff1a{actors}",
                "thumbnail_cols": "3",
                "thumbnail_delay": "2.0",
                "thumbnail_rows": "3",
                "torrent_storage_path": "temp/torrent"
            }
            json.dump(default_settings, file)

    with open(settings_file, 'r', encoding='utf-8') as file:
        settings = json.load(file)

    # 设置参数的标准值
    standard_values = {
        "screenshot_storage_path": "temp/pic",
        "torrent_storage_path": "temp/torrent",
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
        "enable_api": "True",
        "api_port": "5372",
        "main_title_movie": "{en_title} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels} {audio_num}-{team}",
        "second_title_movie": "{original_title} / {other_titles} | \u7c7b\u578b\uff1a{category} | \u6f14\u5458\uff1a{actors}",
        "file_name_movie": "{original_title}.{en_title}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}.{audio_num}-{team}",
        "main_title_tv": "{en_title} S{season} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels} {audio_num}-{team}",
        "second_title_tv": "{original_title} / {other_titles} | {total_episode} | \u7c7b\u578b\uff1a{category} | \u6f14\u5458\uff1a{actors}",
        "file_name_tv": "{original_title}.{en_title}.S{season}E{episode}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}.{audio_num}-{team}",
        "main_title_playlet": "{en_title} S{season} {year} {video_format} {source} {video_codec} {bit_depth} {hdr_format} {frame_rate} {audio_codec} {channels} {audio_num}-{team}",
        "second_title_playlet": "{original_title} | {total_episode} | {year}\u5e74 | {playlet_source} | \u7c7b\u578b\uff1a{category}",
        "file_name_playlet": "{original_title}.{en_title}.S{season}E{episode}.{year}.{video_format}.{source}.{video_codec}.{bit_depth}.{hdr_format}.{frame_rate}.{audio_codec}.{channels}.{audio_num}-{team}",
        "auto_feed_link": "https://example.com/upload.php#seperator#name#linkstr#{主标题}#linkstr#small_descr#linkstr#{副标题}#linkstr#url#linkstr#{IMDB}#linkstr#dburl#linkstr#{豆瓣}#linkstr#descr#linkstr#{简介}[quote]{MediaInfo}[/quote]#linkstr#log_info#linkstr##linkstr#tracklist#linkstr##linkstr#music_type#linkstr##linkstr#music_media#linkstr##linkstr#edition_info#linkstr##linkstr#music_name#linkstr##linkstr#music_author#linkstr##linkstr#animate_info#linkstr##linkstr#anidb#linkstr##linkstr#torrentName#linkstr##linkstr#images#linkstr##linkstr#torrent_name#linkstr#{种子名称}#linkstr#torrent_url#linkstr#{种子链接}#linkstr#type#linkstr#{类型}#linkstr#source_sel#linkstr#{地区}#linkstr#standard_sel#linkstr#{分辨率}#linkstr#audiocodec_sel#linkstr#{音频编码}#linkstr#codec_sel#linkstr#{视频编码}#linkstr#medium_sel#linkstr#{媒介}#linkstr#origin_site#linkstr#{小组}#linkstr#origin_url#linkstr##linkstr#golden_torrent#linkstr#false#linkstr#mediainfo_cmct#linkstr##linkstr#imgs_cmct#linkstr##linkstr#full_mediainfo#linkstr##linkstr#subtitles#linkstr##linkstr#youtube_url#linkstr##linkstr#ptp_poster#linkstr##linkstr#comparisons#linkstr##linkstr#version_info#linkstr##linkstr#multi_mediainfo#linkstr##linkstr#labels#linkstr#0",
        "open_auto_feed_link": "True"
    }

    # 如果参数名在标准值中，但不存在于当前设置中，将其添加到当前设置中
    if settings_name in standard_values and settings_name not in settings:
        settings[settings_name] = standard_values[settings_name]
        with open(settings_file, 'w') as file:
            json.dump(settings, file)

    # 环境变量覆盖配置，优先级最高，环境变量名称必须是变量的大写
    # docker环境变量配置过的参数，将来不支持修改
    settings_data = os.environ.get(
        str(settings_name).upper(), settings.get(settings_name, "")
    )
    print("读取数据" + f"{settings_name}: {settings_data}")

    return settings_data


def get_settings_json():
    """
    获取整个json，由于项目启动时static/settings.json会被初始化，暂不考虑空指针
    """
    settings_file = combine_directories('static/settings.json')
    with open(settings_file, 'r', encoding='utf-8') as file:
        settings = json.load(file)
    # 设置参数的标准值
    return settings


def update_settings_json(settings_json):
    # 如果文件不存在，创建一个空的 JSON 文件并设置默认值
    settings_file = combine_directories('static/settings.json')
    with open(settings_file, 'w', encoding='utf-8') as file:
        json.dump(settings_json, file)


def get_combo_box_data(data_name):
    try:
        # Define the file path
        file_path = combine_directories('static/combo-box-data.json')

        default_content = {}

        # Define default content if key is missing
        if data_name == 'playlet-source':
            default_content = {
                "playlet-source": [
                    "网络收费短剧",
                    "网络免费短剧",
                    "抖音短剧",
                    "快手短剧",
                    "腾讯短剧",
                    ""
                ]
            }

        elif data_name == 'source':
            default_content = {
                "source": [
                    "WEB-DL",
                    "Remux",
                    "Blu-ray",
                    "UHD Blu-ray",
                    "Blu-ray Remux",
                    "UHD Blu-ray Remux",
                    "HDTV",
                    "DVD",
                    ""
                ]
            }

        elif data_name == 'team':
            default_content = {
                "team": [
                    "AGSVWEB",
                    "AGSVMUS",
                    "AGSVPT",
                    "GodDramas",
                    "CatEDU",
                    "Pack",
                    ""
                ]
            }

        # Check if the file exists
        if not os.path.exists(file_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Write the default content to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(default_content, file, ensure_ascii=False, indent=4)

        # Load content from the file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Check if the specified data_name key exists in the loaded data
        if data_name not in data:
            # Update data with default content if not present
            data.update(default_content)
            # Save updated data back to the file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

        return True, data[data_name]

    except Exception as e:
        # Return False and the error message if an exception occurs
        return False, [str(e)]


def update_combo_box_data(configuration_data, configuration_name):
    # 将给定的字符串分割成列表
    sources_list = configuration_data.split('\\n')

    # 文件路径
    file_path = combine_directories('static/combo-box-data.json')

    try:
        # 尝试打开现有的 JSON 文件并加载其内容
        with open(file_path, 'r', encoding='utf-8') as file:
            existing_data = json.load(file)

        # 检查是否存在指定的配置名称，如果不存在则创建
        if configuration_name not in existing_data:
            existing_data[configuration_name] = []

        # 更新指定的配置名称的数据
        existing_data[configuration_name] = sources_list

        # 将更新后的数据写回到 JSON 文件中
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)

        return True, "更新成功"

    except FileNotFoundError:
        # 文件不存在时，创建新文件并写入数据
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump({configuration_name: sources_list}, file, ensure_ascii=False, indent=4)
        return True, "文件不存在，已创建新文件并更新"

    except json.JSONDecodeError:
        return False, "JSON解码错误，文件内容可能损坏"

    except Exception as e:
        # 处理可能发生的其他异常
        return False, f"更新失败，错误：{str(e)}"


def get_picture_bed_type(picture_bed_api_url):
    try:
        # Define the file path
        file_path = combine_directories('static/picture-bed-data.json')

        # Define default content if key is missing
        default_content = {
            "lsky-pro": [
                "https://picture.agsv.top/api/v1/upload",
                "https://img.ptvicomo.net/api/v1/upload"
            ],
            "bohe": [
                "https://img.agsv.top/api/upload"
            ],
            "freeimage": [
                "https://freeimage.host/api/1/upload"
            ],
            "imgbb": [
                "https://api.imgbb.com/1/upload"
            ],
            "pixhost": [
                "https://api.pixhost.to/images"
            ]
        }

        # Check if the file exists and load existing content or initialize with default content
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                existing_content = json.load(file)
        else:
            existing_content = {}

        # Merge default content into the existing content if it's missing
        updated = False
        for key, urls in default_content.items():
            if key not in existing_content:
                existing_content[key] = urls
                updated = True
            else:
                # Check each URL in the default content's URL list
                for url in urls:
                    if url not in existing_content[key]:
                        existing_content[key].append(url)
                        updated = True

        # Save the updated content back to the file if there were updates
        if updated:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(existing_content, file, ensure_ascii=False, indent=4)

        # Now, try to find the API type
        get_picture_bed_type_success, picture_bed_type = find_picture_bed_type(picture_bed_api_url,
                                                                               existing_content)
        if get_picture_bed_type_success:
            print(picture_bed_type)
            return True, picture_bed_type
        else:
            print(picture_bed_type)
            return False, picture_bed_type

    except Exception as e:
        # Return False and the error message if an exception occurs
        return False, str(e)


def find_picture_bed_type(picture_bed_api_url, picture_bed_api_data):
    """
    根据给定的URL和JSON数据，寻找URL对应的标识符。
    如果URL以http开头，自动替换为https。
    如果URL最后一位是'/'，则去除这个'/'。
    如果找不到URL对应的标识符，返回"没找到"。

    参数:
    url (str): 需要查找的网址
    json_data (dict): 包含网址和对应标识符的JSON字典

    返回:
    str: URL对应的标识符或者"没找到"
    """
    # 替换http为https
    if picture_bed_api_url.startswith("http://"):
        picture_bed_api_url = "https://" + picture_bed_api_url[7:]

    # 去除URL末尾的'/'
    if picture_bed_api_url.endswith('/'):
        picture_bed_api_url = picture_bed_api_url[:-1]

    # 遍历JSON数据，查找对应的标识符
    for identifier, urls in picture_bed_api_data.items():
        if picture_bed_api_url in urls:
            return True, identifier

    # 如果找不到对应的标识符，返回"没找到"
    return False, f"您使用的图床上传接口{picture_bed_api_url}暂未配置，请检查static/picture-bed-data.json文件，如果您的图床符合其中的配置，可将上传接口URL按照格式添加到对应类型下"


def get_abbreviation(original_name, json_file_path="static/abbreviation.json"):
    print("开始对参数名称进行转化")
    try:

        json_file_path = combine_directories('static/abbreviation.json')

        # Check if the file exists; if not, create it with default data
        if not os.path.exists(json_file_path):
            default_data = {
                "min_widths": {
                    "9600": "8640p",
                    "4608": "4320p",
                    "3200": "2160p",
                    "2240": "1440p",
                    "1600": "1080p",
                    "900": "720p",
                    "533": "480p"
                },
                "7 680 pixels": "4320p",
                "3 840 pixels": "2160p",
                "2 560 pixels": "1440p",
                "1 920 pixels": "1080p",
                "1 440 pixels": "720p",
                "1 280 pixels": "720p",
                "720 pixels": "480p",
                "640 pixels": "480p",
                "HEVC": "HEVC",
                "AVC": "AVC",
                "AV1": "AV1",
                "x264": "x264",
                "x265": "x265",
                "x266": "x266",
                "12 bits": "12bit",
                "10 bits": "10bit",
                "8 bits": "",
                "Dolby Vision, Version 1.0, dvhe.05.06, BL+RPU": "DV",
                "SMPTE ST 2094 App 4, Version 1, HDR10+ Profile B compatible": "HDR10+",
                "SMPTE ST 2086, HDR10 compatible": "HDR10",
                "HDR Vivid, Version 1": "HDR",
                "60.000 FPS": "60FPS",
                "50.000 FPS": "50FPS",
                "48.000 FPS": "48FPS",
                "30.000 FPS": "",
                "29.970 FPS": "",
                "25.000 FPS": "",
                "24.037 FPS": "",
                "24.000 FPS": "",
                "23.976 FPS": "",
                "Dolby Digital Plus with Dolby Atmos": "Atmos DDP",
                "Dolby TrueHD with Dolby Atmos": "Atmos TrueHD",
                "DTS-HD Master Audio": "DTS-HD MA",
                "Dolby Digital Plus": "DDP",
                "Dolby Digital": "DD",
                "HE-AAC": "AAC",
                "L R C LFE Ls Rs Lb Rb": "7.1",
                "L R C LFE Ls Rs": "5.1",
                "C L R Ls Rs LFE": "5.1",
                "L R": "2.0",
                "Audio": "Audio"
            }
            with open(json_file_path, 'w', encoding='utf-8') as file:
                json.dump(default_data, file, ensure_ascii=False, indent=4)

        # Open and load the abbreviation map
        with open(json_file_path, 'r', encoding='utf-8') as file:
            abbreviation_map = json.load(file)

        # Return the abbreviation if found, else return the original name
        return abbreviation_map.get(original_name, original_name)
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        return original_name
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")
        return original_name


def rename_file(file_path, new_file_name):
    new_file_name = re.sub(r'[<>:\"/\\|?*]', '.', new_file_name)
    # 分割原始文件名以获取扩展名和目录
    file_dir, file_base = os.path.split(file_path)
    file_name, file_extension = os.path.splitext(file_base)

    # 构建新文件名，保留原扩展名
    new_name = file_dir + '/' + new_file_name + file_extension

    # 重命名文件
    try:
        os.rename(file_path, new_name)
        print(file_path, "文件成功重命名为", new_name)
        return True, new_name

    except FileNotFoundError:
        print(f"未找到文件: '{file_path}'")
        return False, f"未找到文件: '{file_path}'"

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
            print("提供的路径不是一个目录或不存在")
            raise ValueError("提供的路径不是一个目录或不存在")

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


def move_file_to_folder(file_path, folder_name):
    """
    将文件移动到同目录下的指定文件夹中，除非文件已在该文件夹中。

    参数:
    file_name (str): 要移动的文件名。
    folder_name (str): 目标文件夹名称。
    """
    # 获取文件的目录和文件名
    print("开始移动文件", file_path, folder_name)
    file_dir, file_base = os.path.split(file_path)
    print(file_base, file_dir)

    # 检查文件是否已在目标文件夹中
    if os.path.basename(file_dir) == folder_name:
        print(f"文件 '{file_path}' 已在 '{folder_name}' 中，无需移动")
        return False, f"文件 '{file_path}' 已在 '{folder_name}' 中，无需移动"

    # 目标文件夹的完整路径
    target_folder = file_dir + '/' + folder_name

    # 如果目标文件夹不存在，创建它
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 构建目标文件路径
    target_file = target_folder + '/' + file_base

    # 移动文件
    try:
        shutil.move(file_path, target_file)
        print(f"文件 '{file_path}' 已成功移动到 '{target_file}'")
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
        print(f'路径下获取到文件{path}，但该文件不符合视频类型')
        return 0, f'路径下获取到文件{path}，但该文件不符合视频类型'  # 是文件，但不符合视频类型

    # 检查路径是否是一个文件夹
    elif os.path.isdir(path):
        for file in os.listdir(path):
            if any(file.endswith(ext) for ext in video_extensions):
                print(path + file)
                return 2, path + '/' + file  # 在文件夹中找到符合类型的视频文件
        print('文件夹中没有符合类型的视频文件')
        return 0, '文件夹中没有符合类型的视频文件'  # 文件夹中没有符合类型的视频文件

    else:
        print('您提供的路径既不是文件也不是文件夹')
        return 0, '您提供的路径既不是文件也不是文件夹'  # 路径既不是文件也不是文件夹


def get_playlet_description(original_title, year, area, category, language, season_number):
    if season_number != '1':
        original_title += ' 第' + num_to_chinese(int(season_number)) + '季'
    return f'\n◎片　　名　{original_title}\n◎年　　代　{year}\n◎产　　地　{area}\n◎类　　别　{category}\n◎语　　言　{language}\n◎简　　介　\n'


# 为了防止出现意外，此方法默认只对文件夹做种子，如果传入的path是一个文件，那么会自动读取其上级文件夹
def make_torrent(path, torrent_storage_path):
    print(path + '  ' + torrent_storage_path)
    try:
        # 检查路径是否存在
        if not os.path.exists(path):
            raise ValueError("提供的路径不存在")

        # 检查路径是否指向一个文件
        if os.path.isfile(path):
            # 如果是，获取文件的上级目录
            path = os.path.dirname(path)

        # 然后检查这个路径是否是一个非空目录
        if os.path.isdir(path) and not os.listdir(path):
            raise ValueError("路径指向一个空目录")

        # 构造完整的torrent文件路径
        torrent_file_name = os.path.basename(path.rstrip("/\\")) + '.torrent'
        torrent_file_path = torrent_storage_path + '/' + torrent_file_name

        # 确保torrent文件的目录存在
        os.makedirs(os.path.dirname(torrent_file_path), exist_ok=True)

        # 如果目标 Torrent 文件已存在，则删除它
        if os.path.exists(torrent_file_path):
            os.remove(torrent_file_path)

        # 获取当前时间
        current_time = datetime.datetime.now()

        # 创建 Torrent 对象，添加当前时间作为创建时间
        t = Torrent(path=path, trackers=['https://tracker.example.com/announce'], created_by='Publish Helper',
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
    result = convert_chinese_punctuation_to_english(result)
    result = result.replace(' ,', ',')
    result = result.replace(' .', '.')
    result = result.replace(' !', '!')
    result = result.replace(' ?', '?')
    result = result.replace(' :', ':')
    result = result.replace(' ;', ';')
    result = result.replace('( ', '(')
    result = result.replace(' )', ')')
    result = result.replace('[ ', '[')
    result = result.replace(' ]', ']')
    result = result.replace('< ', '<')
    result = result.replace(' >', '>')
    result = re.sub(r'\s+', ' ', result)  # 将连续的空格变成一个

    return result


def convert_chinese_punctuation_to_english(text):
    # Mapping of Chinese punctuation to English punctuation
    punctuation_map = {
        "，": ", ",  # Comma
        "。": ". ",  # Period
        "！": "! ",  # Exclamation mark
        "？": "? ",  # Question mark
        "：": ": ",  # Colon
        "；": "; ",  # Semicolon
        "“": "\"",  # Double quotation mark (opening)
        "”": "\"",  # Double quotation mark (closing)
        "‘": "'",  # Single quotation mark (opening)
        "’": "'",  # Single quotation mark (closing)
        "（": " (",  # Left parenthesis
        "）": ") ",  # Right parenthesis
        "【": " [",  # Left square bracket
        "】": "] ",  # Right square bracket
        "《": " <",  # Less than sign
        "》": "> ",  # Greater than sign
        "、": ", ",  # Enumeration comma
        "——": "--",  # Dash
        "…": "..."  # Ellipsis
        # Add more mappings if necessary
    }

    # Replace each Chinese punctuation mark with its English equivalent
    for chinese, english in punctuation_map.items():
        text = text.replace(chinese, english)

    return text


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


def delete_season_number(title, season_number):
    lowercase_season_info_without_spaces = ' season' + season_number  # 用于后期替换多余的season名称
    uppercase_season_info_without_spaces = ' Season' + season_number  # 用于后期替换多余的Season名称
    lowercase_season_info_with_spaces = ' season ' + season_number  # 用于后期替换多余的season名称
    uppercase_season_info_with_spaces = ' Season ' + season_number  # 用于后期替换多余的Season名称
    number_season_name = ' ' + season_number  # 用于后期替换多余的数字季名称
    roman_season_name = ' ' + int_to_roman(int(season_number))  # 用于后期替换多余的罗马季名称
    special_roman_season_name = ' ' + int_to_special_roman(int(season_number))  # 用于后期替换多余的特殊罗马季名称

    # Remove the specified strings from the title
    title = title.replace(lowercase_season_info_without_spaces, '')
    title = title.replace(uppercase_season_info_without_spaces, '')
    title = title.replace(lowercase_season_info_with_spaces, '')
    title = title.replace(uppercase_season_info_with_spaces, '')
    title = title.replace(number_season_name, '')
    title = title.replace(roman_season_name, '')
    title = title.replace(special_roman_season_name, '')

    return title.strip()
