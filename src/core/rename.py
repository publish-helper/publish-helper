import errno
import json
import os
import re
import shutil

from pymediainfo import MediaInfo

from src.core.tool import get_settings, get_abbreviation


# 从PT-Gen响应中读取关键数据
def get_pt_gen_info(description):
    print(f'获取到简介：{description}')
    description = description.replace('\\n', '\n')
    description = description.replace('\\\n', '\\n')

    # 正则表达式
    categories_match = re.search(r'◎类　　别\s*([^\n]*)', description)
    episodes_match = re.search(r'◎集　　数\s*(\d+)', description)  # 匹配集数
    year_match = re.search(r'◎年　　代\s*(\d{4})', description)
    if not year_match:
        year_match = re.search(r'◎上映日期\s*(\d{4})', description)

    # 正则表达式获取名称
    pattern = r'◎片　　名　(.*?)\n|◎译　　名　(.*?)\n'
    matches = re.findall(pattern, description)

    # 将片名放第一位
    if matches:
        matches.insert(0, matches.pop())

    # Extract and separate the titles
    titles = [title for match in matches for title in match if title]
    separated_titles = [title.strip() for titles_group in titles for title in titles_group.split('/')]
    print(f'获取的名称：{str(separated_titles)}')

    english_title = ''
    english_pattern = r'^[A-Za-z\-\—\:\s\(\)\'\'\@\#\$\%\^\&\*\!\?\,\.\;\[\]\{\}\|\<\>\`\~\d\u2160-\u2188]+$'
    for title in separated_titles:
        if re.match(english_pattern, title):
            english_title += title
            print(f'英文名称是：{english_title}')
            break

    original_title = ''
    original_pattern = (r'[\u4e00-\u9fa5\-\—\:\：\s\(\)\（\）\'\'\@\#\$\%\^\&\*\!\?\,\;\！\？\,\.\;\，\。\；\[\]\{'
                        r'\}\|\<\>\【\】\《\》\`\~\·\d\u0041-\u005A\u0061-\u007A\u00C0-\u00FF\u0400-\u04FF\u0600-\u06FF'
                        r'\u0750-\u077F\u08A0-\u08FF\u0E00-\u0E7F\u0F00-\u0FFF\u3040-\u309F\u30A0-\u30FF\u3400-\u4DBF\u4e00-\u9fff\uAC00-\uD7AF]+')
    for title in separated_titles:
        if re.search(original_pattern, title) and not re.match(english_pattern, title):
            original_title += title
            print(f'原始名称是：{title}')
            break
    print(f'所有名称是：{str(separated_titles)}')
    other_titles = [title for title in separated_titles if title not in [english_title, original_title]]
    print(f'其他名称是：{str(other_titles)}')

    # 类别
    categories = categories_match.group(1).strip() if categories_match else ''

    # 匹配“◎主　　演”或“◎演　　员”及其后的多行内容
    actor_pattern = re.compile(
        r'(◎主　　演|◎演　　员)\s*((?:[\s　]*.*?(?:\n|$))*)',  # 注意这里的 [\s　] 用于匹配半角和全角空格
        re.MULTILINE | re.DOTALL
    )
    # 搜索匹配
    actor_match = actor_pattern.search(description)

    actors = []
    if actor_match:
        # 获取演员信息部分并按行分割
        actors_info = actor_match.group(2).strip().split('\n')

        for actor_line in actors_info:
            # 清洗每行数据，去除多余的空白（包括全角空格）
            cleaned_line = re.sub(r'[\s　]+', ' ', actor_line.strip())

            if not cleaned_line:
                continue

            # 提取并清洗演员名称，只保留中文部分
            cleaned_actor = re.search(r'([\u4e00-\u9fa5·]+)', cleaned_line)
            if cleaned_actor and cleaned_actor.group() != '简':  # 避免演员数量不足导致错误
                actors.append(cleaned_actor.group())
            else:
                break

            # 如果已经有五个演员，则停止
            if len(actors) == 5:
                break

    if '◎语　　言' in categories:
        categories = '暂无分类'

    # 提取集数
    episodes = int(episodes_match.group(1)) if episodes_match else None

    print('原始名称：', original_title)
    print('英文名称：', english_title)
    print('年份：', year_match.group(1) if year_match else '')
    print('其他名称：', other_titles)
    print('类别：', categories)
    print('演员：', str(actors))
    return original_title, english_title, year_match.group(
        1) if year_match else '', other_titles, categories, actors, episodes


def get_video_info(file_path):
    if not os.path.exists(file_path):
        print('文件路径不存在')
        return False, ['视频文件路径不存在']
    try:
        audio_count = 0
        media_info = MediaInfo.parse(file_path)
        print(media_info.to_json())
        # 初始化数据，避免空数据报错
        video_format = ''
        video_codec = ''
        bit_depth = ''
        hdr_format = ''
        frame_rate = ''
        audio_codec = ''
        channels = ''
        width = ''
        height = ''
        tags = []
        for track in media_info.tracks:
            # 添加General信息
            if track.track_type == 'General':
                if track.other_frame_rate:
                    frame_rate = track.other_frame_rate[0]

            # 添加Video信息
            elif track.track_type == 'Video':
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
                    if 'x264' in track.writing_library:
                        video_codec = 'x264'
                    if 'x265' in track.writing_library:
                        video_codec = 'x265'
                    if 'x266' in track.writing_library:
                        video_codec = 'x266'

            # 添加Audio信息
            elif track.track_type == 'Audio':
                if audio_count == 0:
                    if track.commercial_name:
                        audio_codec = track.commercial_name
                    if track.channel_layout:
                        channels = track.channel_layout
                if track.other_language == 'Chinese' and '国语' not in tags:
                    tags.append('国语')
                if track.other_language == 'English' and '英语' not in tags:
                    tags.append('英语')
                audio_count += 1

            # 添加Text信息
            elif track.track_type == 'Text':
                if track.other_language == 'Chinese' and '中字' not in tags:
                    tags.append('中字')
                if track.other_language == 'English' and '英字' not in tags:
                    tags.append('英字')

        if extract_numbers(width) > extract_numbers(height):  # 获取较长边的分辨率
            video_format += width
        else:
            video_format += height

        video_format = get_abbreviation(video_format)
        # 如果没有获取到别称（通过以 ' pixels' 结尾为特征判断）
        if video_format[-7:] == ' pixels':
            # 自动获取默认的值
            video_format = approximate_resolution_by_width(extract_numbers(video_format))

        if audio_count == 1:
            audio_num = ''
        else:
            audio_num = str(audio_count) + get_abbreviation('Audio')
        return True, [video_format, get_abbreviation(video_codec), get_abbreviation(bit_depth),
                      get_abbreviation(hdr_format), get_abbreviation(frame_rate), get_abbreviation(audio_codec),
                      get_abbreviation(channels), audio_num, tags]
    except OSError as e:
        # 文件路径相关的错误
        print(f'文件路径错误：{e}。')
        return False, [f'文件路径错误：{e}。']
    except Exception as e:
        # MediaInfo无法解析文件
        print(f'无法解析文件：{e}。')
        return False, [f'无法解析文件：{e}。']


# 通过分段分辨率信息获取默认分辨率简称
def approximate_resolution_by_width(width):
    midpoints = load_min_widths_from_json('static/abbreviation.json')

    for midpoint in sorted(midpoints.keys(), reverse=True):
        if width >= midpoint:
            return midpoints[midpoint]
    return '240p'  # 其他更小的分辨率


# 从json读取分段分辨率简写信息
def load_min_widths_from_json(filepath='static/abbreviation.json'):
    default_min_widths = {
        '9600': '8640p',
        '4608': '4320p',
        '3200': '2160p',
        '2240': '1440p',
        '1600': '1080p',
        '900': '720p',
        '533': '480p'
    }

    # 尝试读取文件，检查是否存在 'min_widths' 键
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # 如果已经存在 'min_widths'，直接返回这个字典
            if 'min_widths' in data:
                return {int(k): v for k, v in data['min_widths'].items()}
    except FileNotFoundError:
        # 如果文件不存在，将创建一个包含 default_min_widths 的新文件
        print(f'File not found: {filepath}. Creating a new file with default min_widths.')
        data = {}
    except json.JSONDecodeError:
        print(f'Error decoding JSON from file: {filepath}. Creating a new file with default min_widths.')
        data = {}

    try:
        # 如果 'min_widths' 键不存在或者在尝试读取文件时出现了错误，更新数据并写回文件
        if 'min_widths' not in data:
            data['min_widths'] = default_min_widths
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4)

    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

    return {int(k): v for k, v in default_min_widths.items()}


# 用于在分辨率中提取数字
def extract_numbers(string):
    result = ''
    for char in string:
        if char.isdigit():
            result += char
    if result:
        return int(result)
    else:
        return None


def get_name_from_template(english_title, original_title, season, episode, year, video_format, source, video_codec,
                           bit_depth, hdr_format, frame_rate, audio_codec, channels, audio_num, team, other_titles,
                           season_number, total_episodes, playlet_source, categories, actors, template):
    name = get_settings(template)  # 获取模板
    # 开始替换关键字
    name = name.replace('{en_title}', english_title)
    name = name.replace('{original_title}', original_title)
    name = name.replace('{season}', season)
    name = name.replace('{episode}', episode)
    name = name.replace('{year}', str(year))
    name = name.replace('{video_format}', video_format)
    name = name.replace('{source}', source)
    name = name.replace('{video_codec}', video_codec)
    name = name.replace('{bit_depth}', bit_depth)
    name = name.replace('{hdr_format}', hdr_format)
    name = name.replace('{frame_rate}', frame_rate)
    name = name.replace('{audio_codec}', audio_codec)
    name = name.replace('{channels}', channels)
    name = name.replace('{audio_num}', audio_num)
    name = name.replace('{team}', team)
    name = name.replace('{other_titles}', other_titles)
    name = name.replace('{season_number}', season_number)
    name = name.replace('{total_episodes}', total_episodes)
    name = name.replace('{playlet_source}', playlet_source)
    name = name.replace('{categories}', categories)
    name = name.replace('{actors}', actors)
    if 'main_title' in template:
        name = name.replace('_', ' ')
        name = re.sub(r'\s+', ' ', name)  # 将连续的空格变成一个
        name = re.sub(r' -', '-', name)  # 将' -'变成'-'
        name = re.sub(r' @', '@', name)  # 将' @'变成'@'
    if 'second_title' in template:
        name = name.replace(' /  | ', ' | ')  # 避免单别名导致的错误
        name = name.replace('标 / 简', '')  # 避免演员无中文名
        if name[:3] == ' | ':
            name = name[3:]  # 避免只有英文标题导致错误
    if 'file_name' in template:
        name = re.sub(r'[<>:\'/\\|?*\s]', '.', name)  # 将Windows不允许出现的字符变成'.'
        name = re.sub(r'\.{2,}', '.', name)  # 将连续的'.'变成一个
        name = re.sub(r'\.-', '-', name)  # 将'.-'变成'-'
        name = re.sub(r'\.@', '@', name)  # 将'.@'变成'@'
    if name[0] == '.' or name[0] == ' ':
        name = name[1:]  # 避免首字符为'.'或者' '
    return name


def rename_file(file_path, new_file_name):
    new_file_name = re.sub(r'[<>:\'/\\|?*]', '.', new_file_name)
    # 分割原始文件名以获取扩展名和目录
    file_dir, file_base = os.path.split(file_path)
    file_name, file_extension = os.path.splitext(file_base)

    # 构建新文件名，保留原扩展名
    new_name = file_dir + '/' + new_file_name + file_extension

    # 重命名文件
    try:
        os.rename(file_path, new_name)
        print(file_path, '文件成功重命名为', new_name)
        return True, new_name

    except FileNotFoundError:
        print(f'未找到文件：{file_path}')
        return False, f'未找到文件：{file_path}'

    except OSError as e:
        print(f'重命名文件时出错：{e}')
        return False, f'重命名文件时出错：{e}'


def rename_folder(current_folder_path, new_name):
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
        new_name = re.sub(r'[<>:\'/\\|?*]', '.', new_name)
        # 检查当前路径是否为一个存在的目录
        if not os.path.isdir(current_folder_path):
            print('提供的路径不是一个目录或不存在')
            raise ValueError('提供的路径不是一个目录或不存在')

        # 获取当前目录的父目录
        parent_dir = os.path.dirname(current_folder_path)
        # 构造新的目录路径
        new_dir = parent_dir + '/' + new_name

        # 重命名目录
        os.rename(current_folder_path, new_dir)
        print(f'目录已重命名为：{new_dir}')
        return True, new_dir

    except OSError as e:
        # 捕获并打印任何操作系统错误
        print(f'重命名目录时发生错误：{e}')
        return False, f'重命名目录时发生错误：{e}'


def move_file_to_folder(file_path, folder_name):
    """
    将文件移动到同目录下的指定文件夹中，除非文件已在该文件夹中。

    参数:
    file_name (str): 要移动的文件名。
    folder_name (str): 目标文件夹名称。
    """
    # 获取文件的目录和文件名
    print('开始移动文件', file_path, folder_name)
    file_dir, file_base = os.path.split(file_path)
    print(file_base, file_dir)

    # 检查文件是否已在目标文件夹中
    if os.path.basename(file_dir) == folder_name:
        print(f'文件"{file_path}"已在"{folder_name}"中，无需移动')
        return False, f'文件"{file_path}"已在"{folder_name}"中，无需移动'

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
        print(f'文件"{file_path}"已成功移动到"{target_file}"')
        return True, target_file

    except Exception as e:
        print(f'移动文件时出错：{e}')
        return False, f'移动文件时出错：{e}'


def create_hard_link(path):
    try:
        # 检查输入路径是否存在
        if not os.path.exists(path):
            return False, f'Path does not exist: {path}'

        # 如果路径是文件
        if os.path.isfile(path):
            # 拆分文件名和扩展名
            file_dir, file_name = os.path.split(path)
            name, ext = os.path.splitext(file_name)

            # 创建硬链接的新文件名（加上_hard_link）
            link_path = os.path.join(file_dir, f'{name}-hardlink{ext}')

            # 创建硬链接
            os.link(path, link_path)
            return True, link_path

        # 如果路径是文件夹
        elif os.path.isdir(path):
            # 创建硬链接的新文件夹路径
            link_path = path + '-hardlink'

            if not os.path.exists(link_path):
                os.makedirs(link_path)  # 创建新的文件夹

            # 遍历源文件夹中的所有文件和子目录
            for root, dirs, files in os.walk(path):
                # 计算相对路径以保持文件夹结构
                rel_dir = os.path.relpath(root, path)
                new_dir = os.path.join(link_path, str(rel_dir))

                # 在硬链接文件夹中创建相同的子目录
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)

                # 遍历并为每个文件创建硬链接
                for file in files:
                    src_file = os.path.join(root, file)
                    name, ext = os.path.splitext(file)  # 拆分文件名和后缀
                    dest_file = os.path.join(str(new_dir), f'{name}-hardlink{ext}')
                    os.link(src_file, dest_file)

            # 返回成功创建文件夹硬链接
            return True, link_path

    except FileExistsError:
        return False, 'Hard link already exists'

    except PermissionError:
        return False, 'Permission denied, unable to create the hard link'

    except OSError as e:
        # 捕捉其他操作系统错误
        if e.errno == errno.EXDEV:
            return False, 'Hard link cannot be created across different file systems'
        return False, f'OS error occurred: {str(e)}'

    except Exception as e:
        # 捕捉其他所有异常
        return False, f'Unexpected error: {str(e)}'
