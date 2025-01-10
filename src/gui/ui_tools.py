from tkinter import filedialog, Tk


def get_picture_file_path():
    # 设置文件类型过滤器
    file_types = [('Picture files', '*.gif;*.png;*.jpg;*.jpeg;*.webp;*.avif;*.bmp;*.apng)'),
                  ('All files', '*.*')]

    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(title='Select a file', filetypes=file_types)

    # 返回选择的文件路径
    return file_path


def get_video_file_path():
    # 设置文件类型过滤器
    file_types = [('Video files', '*.mp4;*.m4v;*.avi;*.flv;*.mkv;*.mpeg;*.mpg;*.rm;*.rmvb;*.ts;*.m2ts'),
                  ('All files', '*.*')]

    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(title='Select a file', filetypes=file_types)

    # 返回选择的文件路径
    return file_path


def get_folder_path():
    # 创建一个 Tkinter 根窗口，但不显示
    root = Tk()
    root.withdraw()

    # 打开文件夹选择对话框
    folder_path = filedialog.askdirectory(title='Select a folder')

    # 关闭根窗口
    root.destroy()

    # 返回选择的文件夹路径
    return folder_path
