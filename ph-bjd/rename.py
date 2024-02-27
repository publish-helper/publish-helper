import json
import os
import re

from pymediainfo import MediaInfo

from tool import get_settings


def extract_details_from_ptgen(data):
    # 正则表达式
    year_match = re.search(r"◎年　　代\s*(\d{4})", data)
    category_match = re.search(r"◎类　　别\s*([^\n]*)", data)

    # 正则表达式获取名称
    pattern = r"◎片　　名　(.*?)\n|◎译　　名　(.*?)\n"
    matches = re.findall(pattern, data)

    # 将片名放第一位
    if matches:
        matches.insert(0, matches.pop())

    # Extract and separate the names
    names = [name for match in matches for name in match if name]
    separated_names = [name.strip() for names_group in names for name in names_group.split('/')]
    print("获取的名称" + str(separated_names))

    english_name = ""
    english_pattern = r"^[A-Za-z\-\—\:\s\(\)\'\"\@\#\$\%\^\&\*\!\?\,\.\;\[\]\{\}\|\<\>\`\~\d\u2160-\u2188]+$"
    for name in separated_names:
        if re.match(english_pattern, name):
            english_name = name
            print("英文名称是 " + name)
            break

    original_name = ""
    original_pattern = (r"[\u4e00-\u9fa5\-\—\:\：\s\(\)\（\）\'\"\@\#\$\%\^\&\*\!\?\,\;\！\？\,\.\;\，\。\；\[\]\{"
                        r"\}\|\<\>\【\】\《\》\`\~\·\d\u2160-\u2188]+")
    for name in separated_names:
        if re.search(original_pattern, name) and not re.match(english_pattern, name):
            original_name = name
            print("原始名称是 " + name)
            break
    print("所有名称是 " + str(separated_names))
    other_names = [name for name in separated_names if name not in [english_name, original_name]]
    print("其他名称是 " + str(other_names))

    # 类别
    category = category_match.group(1).strip() if category_match else None

    # 正则表达式匹配“◎主　　演”行和接下来的四行
    actor_pattern = r'◎主　　演\s+(.*?)\n(.*?)\n(.*?)\n(.*?)\n(.*?)\n' or r'◎演　　员\s+(.*?)\n(.*?)\n(.*?)\n(.*?)\n(.*?)\n'
    actor_match = re.search(actor_pattern, data, re.DOTALL)

    actors = []
    if actor_match:
        for i in range(1, 6):
            # 提取并清洗演员名称，只保留中文部分
            cleaned_actor = re.search(r"[\u4e00-\u9fa5·]+", actor_match.group(i))
            if cleaned_actor:
                actors.append(cleaned_actor.group())
                if len(actors) == 5:  # 提取前五个演员后停止
                    break
    special_characters = r'\/:*?"<>|'
    for char in special_characters:
        original_name = original_name.replace(char, '_')
        english_name = english_name.replace(char, "_")
    if '◎语　　言' in category:
        category = "暂无分类"
    print("原始名称:", original_name)
    print("英文名称:", english_name)
    print("年份:", year_match.group(1) if year_match else None)
    print("其他名称:", other_names)
    print("类别:", category)
    print("演员:", str(actors))

    return original_name, english_name, year_match.group(1) if year_match else None, other_names, category, actors


def get_video_info(file_path):
    if not os.path.exists(file_path):
        print("文件路径不存在")
        return False, ["视频文件路径不存在"]
    try:
        media_info = MediaInfo.parse(file_path)
        print(media_info.to_json())
        video_format = ""
        video_codec = ""
        bit_depth = ""
        hdr_format = ""
        frame_rate = ""
        audio_codec = ""
        channels = ""
        width = ""
        height = ""
        for track in media_info.tracks:
            if track.track_type == "General":
                if track.other_frame_rate:
                    frame_rate = track.other_frame_rate[0]
                # ... 添加其他General信息
            elif track.track_type == "Video":
                if track.other_width:
                    width = track.other_width[0]
                if track.other_width:
                    height = track.other_height[0]
                if track.other_format:
                    video_codec = track.other_format[0]
                if track.other_hdr_format:
                    hdr_format = track.other_hdr_format[0]
                if track.other_bit_depth:
                    bit_depth = track.other_bit_depth[0]
                if track.writing_library:  # 判断是否为x26*重编码
                    if "x264" in track.writing_library:
                        video_codec = "x264"
                    if "x265" in track.writing_library:
                        video_codec = "x265"
                    if "x266" in track.writing_library:
                        video_codec = "x266"

                        # ... 添加其他Video信息
            elif track.track_type == "Audio":
                audio_codec = track.commercial_name
                channels = track.channel_layout
                break
                # ... 添加其他Audio信息
        if extract_numbers(width) > extract_numbers(height):  # 获取较长边的分辨率
            video_format = width
        else:
            video_format = height
        return True, [get_abbreviation(video_format), get_abbreviation(video_codec), get_abbreviation(bit_depth),
                      get_abbreviation(hdr_format), get_abbreviation(frame_rate), get_abbreviation(audio_codec),
                      get_abbreviation(channels)]
    except OSError as e:
        # 文件路径相关的错误
        print(f"文件路径错误: {e}")
        return False, [f"文件路径错误: {e}"]
    except Exception as e:
        # MediaInfo无法解析文件
        print(f"无法解析文件: {e}")
        return False, [f"无法解析文件: {e}"]


# 用于在分辨率中提取数字
def extract_numbers(string):
    result = ""
    for char in string:
        if char.isdigit():
            result += char
    if result:
        return int(result)
    else:
        return None


def get_abbreviation(original_name, json_file_path="static/abbreviation.json"):
    """
    Gets the abbreviation for a given name from a specified JSON file.

    Parameters:
    original_name (str): The original name to find the abbreviation for.
    json_file_path (str): Path to the JSON file containing abbreviations.

    Returns:
    str: Abbreviation if found in the JSON file, else returns the original name.
    """
    print("开始对参数名称进行转化")
    try:
        with open(json_file_path, 'r') as file:
            abbreviation_map = json.load(file)

        # Return the abbreviation if found, else return the original name
        return abbreviation_map.get(original_name, original_name)
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        return original_name
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")
        return original_name


def get_name_from_example(en_title, original_title, season, episode, year, video_format, source, video_codec, bit_depth,
                          hdr_format, frame_rate, audio_codec, channels, team, other_titles, season_number,
                          total_episode, type,
                          category, actors, example):
    name = get_settings(example)
    name = name.replace("{en_title}", en_title)
    name = name.replace("{original_title}", original_title)
    name = name.replace("{season}", season)
    name = name.replace("{episode}", episode)
    name = name.replace("{year}", str(year))
    name = name.replace("{video_format}", video_format)
    name = name.replace("{source}", source)
    name = name.replace("{video_codec}", video_codec)
    name = name.replace("{bit_depth}", bit_depth)
    name = name.replace("{hdr_format}", hdr_format)
    name = name.replace("{frame_rate}", frame_rate)
    name = name.replace("{audio_codec}", audio_codec)
    name = name.replace("{channels}", str(channels))
    name = name.replace("{team}", str(team))
    name = name.replace("{other_titles}", other_titles)
    name = name.replace("{season_number}", season_number)
    name = name.replace("{total_episode}", total_episode)
    name = name.replace("{type}", type)
    name = name.replace("{category}", category)
    name = name.replace("{actors}", actors)
    return name
