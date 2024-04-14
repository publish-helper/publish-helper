import json
import os
import re

from pymediainfo import MediaInfo

from tool import get_settings, get_abbreviation


def get_pt_gen_info(description):
    description = description.replace("\\n", "\n")
    description = description.replace("\\\n", "\\n")
    print(description)
    # 正则表达式
    year_match = re.search(r"◎年　　代\s*(\d{4})", description)
    category_match = re.search(r"◎类　　别\s*([^\n]*)", description)

    # 正则表达式获取名称
    pattern = r"◎片　　名　(.*?)\n|◎译　　名　(.*?)\n"
    matches = re.findall(pattern, description)

    # 将片名放第一位
    if matches:
        matches.insert(0, matches.pop())

    # Extract and separate the titles
    titles = [title for match in matches for title in match if title]
    separated_titles = [title.strip() for titles_group in titles for title in titles_group.split('/')]
    print("获取的名称" + str(separated_titles))

    english_title = ""
    english_pattern = r"^[A-Za-z\-\—\:\s\(\)\'\"\@\#\$\%\^\&\*\!\?\,\.\;\[\]\{\}\|\<\>\`\~\d\u2160-\u2188]+$"
    for title in separated_titles:
        if re.match(english_pattern, title):
            english_title += title
            print("英文名称是 " + title)
            break

    original_title = ""
    original_pattern = (r"[\u4e00-\u9fa5\-\—\:\：\s\(\)\（\）\'\"\@\#\$\%\^\&\*\!\?\,\;\！\？\,\.\;\，\。\；\[\]\{"
                        r"\}\|\<\>\【\】\《\》\`\~\·\d\u0041-\u005A\u0061-\u007A\u00C0-\u00FF\u0400-\u04FF\u0600-\u06FF"
                        r"\u0750-\u077F\u08A0-\u08FF\u0E00-\u0E7F\u0F00-\u0FFF\u3040-\u309F\u30A0-\u30FF\u3400-\u4DBF\u4e00-\u9fff\uAC00-\uD7AF]+")
    for title in separated_titles:
        if re.search(original_pattern, title) and not re.match(english_pattern, title):
            original_title += title
            print("原始名称是 " + title)
            break
    print("所有名称是 " + str(separated_titles))
    other_titles = [title for title in separated_titles if title not in [english_title, original_title]]
    print("其他名称是 " + str(other_titles))

    # 类别
    category = category_match.group(1).strip() if category_match else None

    # 正则表达式匹配“◎主　　演”行和接下来的四行
    actor_pattern = r'◎主　　演\s+(.*?)\n(.*?)\n(.*?)\n(.*?)\n(.*?)\n' or r'◎演　　员\s+(.*?)\n(.*?)\n(.*?)\n(.*?)\n(.*?)\n'
    actor_match = re.search(actor_pattern, description, re.DOTALL)

    actors = []
    if actor_match:
        for i in range(1, 6):
            # 提取并清洗演员名称，只保留中文部分
            cleaned_actor = re.search(r"[\u4e00-\u9fa5·]+", actor_match.group(i))
            if cleaned_actor:
                actors.append(cleaned_actor.group())
                if len(actors) == 5:  # 提取前五个演员后停止
                    break
    if '◎语　　言' in category:
        category = "暂无分类"
    print("原始名称:", original_title)
    print("英文名称:", english_title)
    print("年份:", year_match.group(1) if year_match else None)
    print("其他名称:", other_titles)
    print("类别:", category)
    print("演员:", str(actors))
    return original_title, english_title, year_match.group(1) if year_match else None, other_titles, category, actors


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
                    width += track.other_width[0]
                if track.other_width:
                    height += track.other_height[0]
                if track.other_format:
                    video_codec += track.other_format[0]
                if track.other_hdr_format:
                    hdr_format += track.other_hdr_format[0]
                if track.other_bit_depth:
                    bit_depth += track.other_bit_depth[0]
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
            video_format += width
        else:
            video_format += height

        video_format = get_abbreviation(video_format)
        # 如果没有获取到别称（通过以 ' pixels' 结尾为特征判断）
        if video_format[-7:] == ' pixels':
            # 自动获取默认的值
            video_format = approximate_resolution_by_width(extract_numbers(video_format))

        return True, [video_format, get_abbreviation(video_codec), get_abbreviation(bit_depth),
                      get_abbreviation(hdr_format), get_abbreviation(frame_rate), get_abbreviation(audio_codec),
                      get_abbreviation(channels)]
    except OSError as e:
        # 文件路径相关的错误
        print(f"文件路径错误: {e}。")
        return False, [f"文件路径错误: {e}。"]
    except Exception as e:
        # MediaInfo无法解析文件
        print(f"无法解析文件: {e}。")
        return False, [f"无法解析文件: {e}。"]


# 通过分段分辨率信息获取默认分辨率简称
def approximate_resolution_by_width(width):
    midpoints = load_min_widths_from_json("static/abbreviation.json")

    for midpoint in sorted(midpoints.keys(), reverse=True):
        if width >= midpoint:
            return midpoints[midpoint]
    return "240p"  # 其他更小的分辨率


# 从json读取分段分辨率简写信息
def load_min_widths_from_json(filepath="static/abbreviation.json"):
    default_min_widths = {
        "9600": "8640p",
        "4608": "4320p",
        "3200": "2160p",
        "2240": "1440p",
        "1600": "1080p",
        "900": "720p",
        "533": "480p"
    }

    # 尝试读取文件，检查是否存在 "min_widths" 键
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            # 如果已经存在 "min_widths"，直接返回这个字典
            if "min_widths" in data:
                return {int(k): v for k, v in data["min_widths"].items()}
    except FileNotFoundError:
        # 如果文件不存在，将创建一个包含 default_min_widths 的新文件
        print(f"File not found: {filepath}. Creating a new file with default min_widths.")
        data = {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {filepath}. Creating a new file with default min_widths.")
        data = {}

    # 如果 "min_widths" 键不存在或者在尝试读取文件时出现了错误，更新数据并写回文件
    if "min_widths" not in data:
        data["min_widths"] = default_min_widths
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

    return {int(k): v for k, v in default_min_widths.items()}


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


def get_name_from_template(english_title, original_title, season, episode, year, video_format, source, video_codec,
                           bit_depth, hdr_format, frame_rate, audio_codec, channels, team, other_titles, season_number,
                           total_episode, playlet_source, category, actors, template):
    name = get_settings(template)
    name = name.replace("{en_title}", english_title)
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
    name = name.replace("{playlet_source}", playlet_source)
    name = name.replace("{category}", category)
    name = name.replace("{actors}", actors)
    return name
