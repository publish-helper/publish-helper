from flask import Flask, request, jsonify
from mediainfo import get_media_info
from tool import check_path_and_find_video, get_settings

api = Flask(__name__)


def run_api():
    api.run(port=int(get_settings("api_port")), debug=True, use_reloader=False)


@api.route('/api/add', methods=['GET'])
# 例子，用于计算两个数字的和
def api_add_numbers():
    # 从请求URL中获取两个参数'a'和'b'
    a = request.args.get('a', default=0, type=int)
    b = request.args.get('b', default=0, type=int)
    # 计算和
    result = a + b
    # 返回结果
    return jsonify({'result': result})


@api.route('/api/getMediaInfo', methods=['GET'])
# 用于获取MediaInfo，传入一个文件地址或者一个文件夹地址，返回视频文件路径和MediaInfo
def api_get_media_info():
    # 从请求URL中获取filePath
    file_path = request.args.get('filePath', default=0, type=str)
    is_video_path, video_path = check_path_and_find_video(file_path)  # 视频资源的路径
    if is_video_path == 1 or is_video_path == 2:
        get_media_info_success, media_info = get_media_info(video_path)
        if get_media_info_success:
            return jsonify({'videoPath': video_path, 'mediaInfo': media_info})
        else:
            return jsonify({'videoPath': video_path, 'mediaInfo': "获取MediaInfo失败。"})
    else:
        return jsonify({'videoPath': '未获取到视频文件路径。', 'mediaInfo': "您输入的路径错误。"})
