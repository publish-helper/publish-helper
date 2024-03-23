from flask import Flask, request, jsonify

from mediainfo import get_media_info
from ptgen import get_pt_gen_description
from rename import get_video_info
from screenshot import get_screenshot, get_thumbnail
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
    path = request.args.get('path', default='', type=str)
    is_video_path, video_path = check_path_and_find_video(path)  # 视频资源的路径
    if is_video_path == 1 or is_video_path == 2:
        get_media_info_success, response = get_media_info(video_path)
        if get_media_info_success:
            return jsonify({
                "data": {
                    "mediaInfo": response,
                    "videoPath": video_path
                },
                "message": "获取MediaInfo成功。",  # 提示信息
                "success": True
            })
        else:
            return jsonify({
                "data": {
                    "mediaInfo": "",
                    "videoPath": video_path,
                },
                "message": f"获取视频路径成功，但是获取MediaInfo失败，错误：{response}",  # 提示信息
                "success": False
            })
    else:
        return jsonify({
            "data": {
                "mediaInfo": "",
                "videoPath": ""
            },
            "message": f"获取视频路径失败，{video_path}",  # 提示信息
            "success": False
        })


@api.route('/api/getScreenshot', methods=['GET'])
# 用于获取MediaInfo，传入一个文件地址或者一个文件夹地址，返回视频文件路径和MediaInfo
def api_get_screenshot():
    # 从请求URL中获取参数
    path = request.args.get('path', default='', type=str)
    screenshot_path = request.args.get('screenshotPath', default=get_settings("screenshot_path"), type=str)
    screenshot_number = int(request.args.get('screenshotNumber', default=get_settings("screenshot_number"), type=str))
    screenshot_threshold = float(
        request.args.get('screenshotThreshold', default=get_settings("screenshot_threshold"), type=str))
    screenshot_start_percentage = float(
        request.args.get('screenshotStartPercentage', default=get_settings("screenshot_start_percentage"), type=str))
    screenshot_end_percentage = float(
        request.args.get('screenshotEndPercentage', default=get_settings("screenshot_end_percentage"), type=str))
    screenshot_min_interval_percentage = float(
        request.args.get('screenshotMinIntervalPercentage', default="0.01", type=str))
    if screenshot_number > 0:
        if screenshot_number < 6:
            if 0 < screenshot_start_percentage < 1 and 0 < screenshot_end_percentage < 1:
                if screenshot_start_percentage < screenshot_end_percentage:
                    is_video_path, video_path = check_path_and_find_video(path)  # 视频资源的路径
                    if is_video_path == 1 or is_video_path == 2:
                        screenshot_success, response = get_screenshot(video_path, screenshot_path, screenshot_number,
                                                                      screenshot_threshold, screenshot_start_percentage,
                                                                      screenshot_end_percentage,
                                                                      screenshot_min_interval_percentage)
                        if screenshot_success:
                            screenshot_path = ''
                            screenshot_number = 0
                            for r in response:
                                screenshot_path += r
                                screenshot_path += '\n'
                                screenshot_number += 1
                            return jsonify({
                                "data": {
                                    "screenshotNumber": str(screenshot_number),
                                    "screenshotPath": screenshot_path,
                                    "videoPath": video_path
                                },
                                "message": "获取截图成功。",  # 提示信息
                                "success": True
                            })
                        else:
                            return jsonify({
                                "data": {
                                    "screenshotNumber": "0",
                                    "screenshotPath": "",
                                    "videoPath": video_path
                                },
                                "message": f"获取截图失败：{response[0]}",  # 提示信息
                                "success": False
                            })
                    else:
                        return jsonify({
                            "data": {
                                "screenshotNumber": "0",
                                "screenshotPath": "",
                                "videoPath": ""
                            },
                            "message": f"获取视频路径失败，{video_path}",  # 提示信息
                            "success": False
                        })
                else:
                    return jsonify({
                        "data": {
                            "screenshotNumber": "0",
                            "screenshotPath": "",
                            "videoPath": ""
                        },
                        "message": "截图起始点不能大于终止点。",  # 提示信息
                        "success": False
                    })
            else:
                return jsonify({
                    "data": {
                        "screenshotNumber": "0",
                        "screenshotPath": "",
                        "videoPath": ""
                    },
                    "message": "截图起始点和终止点不能小于0或大于1。",  # 提示信息
                    "success": False
                })
        else:
            return jsonify({
                "data": {
                    "screenshotNumber": "0",
                    "screenshotPath": "",
                    "videoPath": ""
                },
                "message": "一次获取的截图数量不能大于5张。",  # 提示信息
                "success": False
            })
    else:
        return jsonify({
            "data": {
                "screenshotNumber": "0",
                "screenshotPath": "",
                "videoPath": "",
            },
            "message": "一次获取的截图数量不能小于1张。",  # 提示信息
            "success": False
        })


@api.route('/api/getThumbnail', methods=['GET'])
# 用于获取MediaInfo，传入一个文件地址或者一个文件夹地址，返回视频文件路径和MediaInfo
def api_get_thumbnail():
    # 从请求URL中获取参数
    path = request.args.get('path', default='', type=str)
    screenshot_path = request.args.get('screenshotPath', default=get_settings("screenshot_path"), type=str)
    thumbnail_rows = int(request.args.get('thumbnailRows', default=get_settings("thumbnail_rows"), type=str))
    thumbnail_cols = int(request.args.get('thumbnailCols', default=get_settings("thumbnail_cols"), type=str))
    screenshot_start_percentage = float(
        request.args.get('screenshotStartPercentage', default=get_settings("screenshot_start_percentage"), type=str))
    screenshot_end_percentage = float(
        request.args.get('screenshotEndPercentage', default=get_settings("screenshot_end_percentage"), type=str))
    if thumbnail_rows > 0 and thumbnail_cols > 0:
        if 0 < screenshot_start_percentage < 1 and 0 < screenshot_end_percentage < 1:
            if screenshot_start_percentage < screenshot_end_percentage:
                is_video_path, video_path = check_path_and_find_video(path)  # 视频资源的路径
                if is_video_path == 1 or is_video_path == 2:

                    get_thumbnail_success, response = get_thumbnail(video_path, screenshot_path, thumbnail_rows,
                                                                    thumbnail_cols, screenshot_start_percentage,
                                                                    screenshot_end_percentage)
                    if get_thumbnail_success:
                        return jsonify({
                            "data": {
                                "thumbnailPath": response,
                                "videoPath": video_path
                            },
                            "message": "获取截图成功。",  # 提示信息
                            "success": True
                        })
                    else:
                        return jsonify({
                            "data": {
                                "thumbnailPath": "",
                                "videoPath": video_path
                            },
                            "message": f"获取截图失败：{response}",  # 提示信息
                            "success": False
                        })
                else:
                    return jsonify({
                        "data": {
                            "thumbnailPath": "",
                            "videoPath": ""
                        },
                        "message": f"获取视频路径失败，{video_path}",  # 提示信息
                        "success": False
                    })
            else:
                return jsonify({
                    "data": {
                        "thumbnailPath": "",
                        "videoPath": ""
                    },
                    "message": "截图起始点不能大于终止点。",  # 提示信息
                    "success": False
                })
        else:
            return jsonify({
                "data": {
                    "thumbnailPath": "",
                    "videoPath": ""
                },
                "message": "截图起始点和终止点不能小于0或大于1。",  # 提示信息
                "success": False
            })
    else:
        return jsonify({
            "data": {
                "thumbnailPath": "",
                "videoPath": ""
            },
            "message": "缩略图横向、纵向数量均需要大于0。",  # 提示信息
            "success": False
        })


@api.route('/api/getVideoInfo', methods=['GET'])
# 用于获取视频关键信息，传入一个文件地址或者一个文件夹地址，返回视频文件路径和关键信息
def api_get_video_info():
    # 从请求URL中获取path
    path = request.args.get('path', default='', type=str)
    is_video_path, video_path = check_path_and_find_video(path)  # 视频资源的路径
    if is_video_path == 1 or is_video_path == 2:
        get_video_info_success, output = get_video_info(video_path)
        if get_video_info_success:
            print("获取到关键参数：" + str(output))
            video_format = output[0]
            video_codec = output[1]
            bit_depth = output[2]
            hdr_format = output[3]
            frame_rate = output[4]
            audio_codec = output[5]
            channels = output[6]
            return jsonify({
                "data": {
                    "videoPath": video_path,
                    "videoFormat": video_format,
                    "videoCodec": video_codec,
                    "bitDepth": bit_depth,
                    "hdrFormat": hdr_format,
                    "frameRate": frame_rate,
                    "audioCodec": audio_codec,
                    "channel": channels
                },
                "message": "获取视频关键参数成功。",  # 提示信息
                "success": True
            })
    else:
        return jsonify({
            "data": {
                "videoPath": "",
                "videoFormat": "",
                "videoCodec": "",
                "bitDepth": "",
                "hdrFormat": "",
                "frameRate": "",
                "audioCodec": "",
                "channel": ""
            },
            "message": f"获取视频路径失败，{video_path}",  # 提示信息
            "success": False
        })


@api.route('/api/getPtGenDescription', methods=['GET'])
# 用于获取PT-Gen简介，传入一个豆瓣链接，返回PT-Gen简介
def api_get_pt_gen_description():
    # 从请求URL中获取参数
    resource_url = request.args.get('resourceUrl', default='', type=str)
    pt_gen_api_url = request.args.get('ptGenApiUrl', default=get_settings("pt_gen_api_url"), type=str)
    if pt_gen_api_url == '':
        pt_gen_api_url = get_settings("pt_gen_api_url")
    get_pt_gen_description_success, response = get_pt_gen_description(pt_gen_api_url, resource_url)
    if get_pt_gen_description_success:
        return jsonify({
            "data": {
                "description": response
            },
            "message": "获取PT-Gen简介成功。",  # 提示信息
            "success": True
        })
    else:
        return jsonify({
            "data": {
                "description": ""
            },
            "message": f"获取PT-Gen简介失败，{response}",  # 提示信息
            "success": False
        })
