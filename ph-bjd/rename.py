import json
import os
import re

from pymediainfo import MediaInfo


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

    chinese_name = ""
    chinese_pattern = r"[\u4e00-\u9fff\-\—\:\：\s\(\)\（\）\'\"\@\#\$\%\^\&\*\!\?\,\;\！\？\,\.\;\，\。\；\[\]\{\}\|\<\>\【\】\《\》\`\~\·\d\u2160-\u2188]+"
    for name in separated_names:
        if re.search(chinese_pattern, name) and not re.match(english_pattern, name):
            chinese_name = name
            print("中文名称是 " + name)
            break
    print("所有名称是 " + str(separated_names))
    other_names = [name for name in separated_names if name not in [english_name, chinese_name]]
    print("其他名称是 " + str(other_names))

    # 类别
    category = category_match.group(1).strip() if category_match else None

    lines = data.split('\n')

    # Find the index where actor information starts
    actor_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('◎演　　员' or '◎主　　演'):
            actor_idx = i
            break

    # Extract the first five actors' names
    actors = []
    if actor_idx != -1:
        # Extract the first actor's name from the line with "◎演　　员"
        first_actor = lines[actor_idx].split('　')[-1].split()[0]
        actors.append(first_actor)

        # Extract the next four actors' names
        for line in lines[actor_idx + 1:]:
            # Check if we have already collected five actors or the line is not an actor line
            if len(actors) >= 5 or not line.startswith('　　　　　'):
                break
            # Extract the actor's Chinese name
            chinese_actor_name = line.split()[0]
            actors.append(chinese_actor_name)

    print("中文名称:", chinese_name)
    print("英文名称:", english_name)
    print("年份:", year_match.group(1) if year_match else None)
    print("其他名称:", other_names)
    print("类别:", category)
    print("演员:", str(actors))

    return chinese_name, english_name, year_match.group(1) if year_match else None, other_names, category, actors


def get_video_info(file_path):
    if not os.path.exists(file_path):
        print("文件路径不存在")
        return False, ["视频文件路径不存在"]
    try:
        media_info = MediaInfo.parse(file_path)
        print(media_info.to_json())
        width = ""
        format = ""
        hdr_format = ""
        commercial_name = ""
        channel_layout = ""

        for track in media_info.tracks:
            if track.track_type == "General":
                pass
                # ... 添加其他General信息
            elif track.track_type == "Video":
                if track.other_width:
                    width = track.other_width[0]
                if track.other_format:
                    format = track.other_format[0]
                if track.other_hdr_format:
                    hdr_format = track.other_hdr_format[0]
                # ... 添加其他Video信息
            elif track.track_type == "Audio":
                commercial_name = track.commercial_name
                channel_layout = track.channel_layout
                break
                # ... 添加其他Audio信息

        return True, [get_abbreviation(width), get_abbreviation(format), get_abbreviation(hdr_format),
                      get_abbreviation(commercial_name), get_abbreviation(channel_layout)]
    except OSError as e:
        # 文件路径相关的错误
        print(f"文件路径错误: {e}")
        return False, [f"文件路径错误: {e}"]
    except Exception as e:
        # MediaInfo无法解析文件
        print(f"无法解析文件: {e}")
        return False, [f"无法解析文件: {e}"]


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
