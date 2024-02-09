import datetime
import json
import os
import random
import shutil
from tkinter import filedialog, Tk

from torf import Torrent


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


def get_settings(parameter_name):
    """
    从 static/settings.json 文件中获取特定参数的值。
    如果参数不存在，则返回 None。

    参数:
    parameter_name (str): 参数名称

    返回:
    参数的值或 None
    """
    settings_file = 'static/settings.json'
    if not os.path.exists(settings_file):
        return None

    with open(settings_file, 'r') as file:
        settings = json.load(file)
    print(str(parameter_name) + ":" + str(settings.get(parameter_name)))
    return str(settings.get(parameter_name))


def rename_file_with_same_extension(old_name, new_name_without_extension):
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
        return False, (f"未找到文件: '{old_name}'")
    except OSError as e:
        print(f"重命名文件时出错: {e}")
        return False, (f"重命名文件时出错: {e}")


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
    date_time = now.strftime("%Y%m%d_%H%M%S")
    letters = random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 6)
    random_str = ''.join(letters)
    filename = f"{date_time}_{random_str}.png"
    path = base_path + '/' + filename
    return path


def get_file_path():
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
        print('是文件，但不符合视频类型')
        return 0, '是文件，但不符合视频类型'  # 是文件，但不符合视频类型

    # 检查路径是否是一个文件夹
    elif os.path.isdir(path):
        for file in os.listdir(path):
            if any(file.endswith(ext) for ext in video_extensions):
                print(path + file)
                return 2, path + '/' + file  # 在文件夹中找到符合类型的视频文件
        print('文件夹中没有符合类型的视频文件')
        return 0, '文件夹中没有符合类型的视频文件'  # 文件夹中没有符合类型的视频文件

    else:
        print('路径既不是文件也不是文件夹')
        return 0, '路径既不是文件也不是文件夹'  # 路径既不是文件也不是文件夹


# create_torrent("src", "out")
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
        t = Torrent(path=folder_path, trackers=['http://tracker.example.com/announce'], created_by='ph-bjd',
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
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data[name]
