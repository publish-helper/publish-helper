from flask import Flask, request, jsonify

from mediainfo import get_media_info
from screenshot import get_screenshot
from tool import check_path_and_find_video, get_settings

api = Flask(__name__)


def run_api():
    api.run(port=int(get_settings("api_port")), debug=True, use_reloader=False, threaded=True)


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
    # 从请求URL中获取path
    path = request.args.get('path', default=0, type=str)
    is_video_path, video_path = check_path_and_find_video(path)  # 视频资源的路径
    if is_video_path == 1 or is_video_path == 2:
        get_media_info_success, media_info = get_media_info(video_path)
        if get_media_info_success:
            return jsonify({
                "success": True,
                "data": {
                    "videoPath": video_path,
                    "mediaInfo": media_info
                },
                "message": "操作成功。"  # 提示信息
            })
        else:
            return jsonify({
                "success": True,
                "data": {
                    "videoPath": video_path,
                    "mediaInfo": ""
                },
                "message": "获取视频路径成功，获取MediaInfo失败。"  # 提示信息
            })
    else:
        return jsonify({
            "success": True,
            "data": {
                "videoPath": "",
                "mediaInfo": ""
            },
            "message": "获取视频路径失败，您输入的路径错误。"  # 提示信息
        })


@api.route('/api/getScreenshot', methods=['GET'])
# 用于获取MediaInfo，传入一个文件地址或者一个文件夹地址，返回视频文件路径和MediaInfo
def api_get_screenshot():
    # 从请求URL中获取filePath
    path = request.args.get('path', default='', type=str)
    screenshot_path = request.args.get('screenshotPath', default=get_settings("screenshot_path"), type=str)
    screenshot_number = int(request.args.get('screenshotNumber', default=get_settings("screenshot_number"), type=str))
    screenshot_threshold = float(
        request.args.get('screenshotThreshold', default=get_settings("screenshot_threshold"), type=str))
    screenshot_start_percentage = float(request.args.get('screenshotStartPercentage', default=get_settings("screenshot_start_percentage"), type=str))
    screenshot_end_percentage = float(request.args.get('screenshotEndPercentage', default=get_settings("screenshot_end_percentage"), type=str))
    screenshot_min_interval_percentage = float(request.args.get('screenshotMinIntervalPercentage', default="0.01", type=str))
    if screenshot_number > 0:
        if screenshot_number < 6:
            is_video_path, video_path = check_path_and_find_video(path)  # 视频资源的路径
            if is_video_path == 1 or is_video_path == 2:
                screenshot_success, response = get_screenshot(video_path, screenshot_path, screenshot_number,
                                                              screenshot_threshold, screenshot_start_percentage,
                                                              screenshot_end_percentage, screenshot_min_interval_percentage)
                if screenshot_success:
                    screenshot_path = ''
                    screenshot_number = 0
                    for r in response:
                        screenshot_path += r
                        screenshot_path += '\n'
                        screenshot_number += 1
                    return jsonify({
                        "success": True,
                        "data": {
                            "screenshotNumber": str(screenshot_number),
                            "screenshotPath": screenshot_path
                        },
                        "message": "获取截图成功。"  # 提示信息
                    })
                else:
                    return jsonify({
                        "success": False,
                        "data": {
                            "screenshotNumber": "0",
                            "screenshotPath": ""
                        },
                        "message": response[0]  # 提示信息
                    })
            else:
                return jsonify({
                    "success": False,
                    "data": {
                        "screenshotNumber": "0",
                        "screenshotPath": ""
                    },
                    "message": "获取视频路径失败，您输入的路径错误。"  # 提示信息
                })
        else:
            return jsonify({
                "success": False,
                "data": {
                    "screenshotNumber": "0",
                    "screenshotPath": ""
                },
                "message": "一次获取的截图数量不能大于5张。"  # 提示信息
            })
    else:
        return jsonify({
            "success": False,
            "data": {
                "screenshotNumber": "0",
                "screenshotPath": ""
            },
            "message": "一次获取的截图数量不能小于1张。"  # 提示信息
        })
