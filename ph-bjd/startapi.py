import os

from flask import Flask, request, jsonify

from mediainfo import get_media_info
from picturebed import upload_picture
from ptgen import get_pt_gen_description
from rename import get_video_info, get_pt_gen_info
from screenshot import get_screenshot, get_thumbnail
from tool import check_path_and_find_video, get_settings, make_torrent

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


@api.route('/api/getScreenshot', methods=['GET'])
# 用于获取MediaInfo，传入一个文件地址或者一个文件夹地址，返回视频文件路径和MediaInfo
def api_get_screenshot():
    # 从请求URL中获取参数
    path = request.args.get('path', default='', type=str)

    screenshot_storage_path = request.args.get('screenshotStoragePath', default=get_settings("screenshot_storage_path"),
                                               type=str)
    if screenshot_storage_path == '':
        screenshot_storage_path = get_settings("screenshot_storage_path")

    screenshot_number = request.args.get('screenshotNumber', default=get_settings("screenshot_number"), type=str)
    if screenshot_number == '':
        screenshot_number = int(get_settings("screenshot_number"))
    else:
        screenshot_number = int(screenshot_number)

    screenshot_threshold = request.args.get('screenshotThreshold', default=get_settings("screenshot_threshold"),
                                            type=str)
    if screenshot_threshold == '':
        screenshot_threshold = float(get_settings("screenshot_threshold"))
    else:
        screenshot_threshold = float(screenshot_threshold)

    screenshot_start_percentage = request.args.get('screenshotStartPercentage',
                                                   default=get_settings("screenshot_start_percentage"), type=str)
    if screenshot_start_percentage == '':
        screenshot_start_percentage = float(get_settings("screenshot_start_percentage"))
    else:
        screenshot_start_percentage = float(screenshot_start_percentage)

    screenshot_end_percentage = request.args.get('screenshotEndPercentage',
                                                 default=get_settings("screenshot_end_percentage"), type=str)
    if screenshot_end_percentage == '':
        screenshot_end_percentage = float(get_settings("screenshot_end_percentage"))
    else:
        screenshot_end_percentage = float(screenshot_end_percentage)

    screenshot_min_interval_percentage = request.args.get('screenshotMinIntervalPercentage', default="0.01", type=str)
    if screenshot_min_interval_percentage == '':
        screenshot_min_interval_percentage = 0.01
    else:
        screenshot_min_interval_percentage = float(screenshot_min_interval_percentage)

    if screenshot_number > 0:
        if screenshot_number < 6:
            if 0 < screenshot_start_percentage < 1 and 0 < screenshot_end_percentage < 1:
                if screenshot_start_percentage < screenshot_end_percentage:
                    is_video_path, video_path = check_path_and_find_video(path)  # 视频资源的路径
                    if is_video_path == 1 or is_video_path == 2:
                        screenshot_success, response = get_screenshot(video_path, screenshot_storage_path,
                                                                      screenshot_number,
                                                                      screenshot_threshold, screenshot_start_percentage,
                                                                      screenshot_end_percentage,
                                                                      screenshot_min_interval_percentage)
                        if screenshot_success:
                            screenshot_storage_path = ''
                            screenshot_number = 0
                            for r in response:
                                screenshot_storage_path += r
                                screenshot_storage_path += '\n'
                                screenshot_number += 1
                            return jsonify({
                                "data": {
                                    "code": "OK",
                                    "message": "获取截图成功。",  # 提示信息
                                    "screenshotNumber": str(screenshot_number),
                                    "screenshotPath": screenshot_storage_path,
                                    "videoPath": video_path
                                },
                                "success": True
                            })
                        else:
                            return jsonify({
                                "data": {
                                    "code": "GENERAL_ERROR",
                                    "message": f"获取截图失败：{response[0]}",  # 提示信息
                                    "screenshotNumber": "0",
                                    "screenshotPath": "",
                                    "videoPath": video_path
                                },
                                "success": True
                            })
                    else:
                        return jsonify({
                            "data": {
                                "code": "FILE_PATH_ERROR",
                                "message": f"获取视频路径失败，{video_path}",  # 提示信息
                                "screenshotNumber": "0",
                                "screenshotPath": "",
                                "videoPath": ""
                            },
                            "success": True
                        })
                else:
                    return jsonify({
                        "data": {
                            "code": "VALUE_RELATIONSHIP_ERROR",
                            "message": "截图起始点不能大于终止点。",  # 提示信息
                            "screenshotNumber": "0",
                            "screenshotPath": "",
                            "videoPath": ""
                        },
                        "success": True
                    })
            else:
                return jsonify({
                    "data": {
                        "code": "VALUE_RANGE_ERROR",
                        "message": "截图起始点和终止点不能小于0或大于1。",  # 提示信息
                        "screenshotNumber": "0",
                        "screenshotPath": "",
                        "videoPath": ""
                    },
                    "success": True
                })
        else:
            return jsonify({
                "data": {
                    "code": "VALUE_RANGE_ERROR",
                    "message": "一次获取的截图数量不能大于5张。",  # 提示信息
                    "screenshotNumber": "0",
                    "screenshotPath": "",
                    "videoPath": ""
                },
                "success": True
            })
    else:
        return jsonify({
            "data": {
                "code": "VALUE_RANGE_ERROR",
                "message": "一次获取的截图数量不能小于1张。",  # 提示信息
                "screenshotNumber": "0",
                "screenshotPath": "",
                "videoPath": "",
            },
            "success": True
        })


@api.route('/api/getThumbnail', methods=['GET'])
# 用于获取缩略图，传入相关参数，返回缩略图路径
def api_get_thumbnail():
    # 从请求URL中获取参数
    path = request.args.get('path', default='', type=str)

    screenshot_storage_path = request.args.get('screenshotStoragePath', default=get_settings("screenshot_storage_path"),
                                               type=str)
    if screenshot_storage_path == '':
        screenshot_storage_path = get_settings("screenshot_storage_path")

    thumbnail_rows = request.args.get('thumbnailRows', default=get_settings("thumbnail_rows"), type=str)
    if thumbnail_rows == '':
        thumbnail_rows = int(get_settings("thumbnail_rows"))
    else:
        thumbnail_rows = int(thumbnail_rows)

    thumbnail_cols = request.args.get('thumbnailCols', default=get_settings("thumbnail_cols"), type=str)
    if thumbnail_cols == '':
        thumbnail_cols = int(get_settings("thumbnail_cols"))
    else:
        thumbnail_cols = int(thumbnail_cols)

    screenshot_start_percentage = request.args.get('screenshotStartPercentage',
                                                   default=get_settings("screenshot_start_percentage"), type=str)
    if screenshot_start_percentage == '':
        screenshot_start_percentage = float(get_settings("screenshot_start_percentage"))
    else:
        screenshot_start_percentage = float(screenshot_start_percentage)

    screenshot_end_percentage = request.args.get('screenshotEndPercentage',
                                                 default=get_settings("screenshot_end_percentage"), type=str)
    if screenshot_end_percentage == '':
        screenshot_end_percentage = float(get_settings("screenshot_end_percentage"))
    else:
        screenshot_end_percentage = float(screenshot_end_percentage)

    if thumbnail_rows > 0 and thumbnail_cols > 0:
        if 0 < screenshot_start_percentage < 1 and 0 < screenshot_end_percentage < 1:
            if screenshot_start_percentage < screenshot_end_percentage:
                is_video_path, video_path = check_path_and_find_video(path)  # 视频资源的路径
                if is_video_path == 1 or is_video_path == 2:

                    get_thumbnail_success, response = get_thumbnail(video_path, screenshot_storage_path, thumbnail_rows,
                                                                    thumbnail_cols, screenshot_start_percentage,
                                                                    screenshot_end_percentage)
                    if get_thumbnail_success:
                        return jsonify({
                            "data": {
                                "code": "OK",
                                "message": "获取截图成功。",  # 提示信息
                                "thumbnailPath": response,
                                "videoPath": video_path
                            },
                            "success": True
                        })
                    else:
                        return jsonify({
                            "data": {
                                "code": "GENERAL_ERROR",
                                "message": f"获取截图失败：{response}",  # 提示信息
                                "thumbnailPath": "",
                                "videoPath": video_path
                            },
                            "success": True
                        })
                else:
                    return jsonify({
                        "data": {
                            "code": "FILE_PATH_ERROR",
                            "message": f"获取视频路径失败，{video_path}",  # 提示信息
                            "thumbnailPath": "",
                            "videoPath": ""
                        },
                        "success": True
                    })
            else:
                return jsonify({
                    "data": {
                        "code": "VALUE_RELATIONSHIP_ERROR",
                        "message": "截图起始点不能大于终止点。",  # 提示信息
                        "thumbnailPath": "",
                        "videoPath": ""
                    },
                    "success": True
                })
        else:
            return jsonify({
                "data": {
                    "code": "VALUE_RANGE_ERROR",
                    "message": "截图起始点和终止点不能小于0或大于1。",  # 提示信息
                    "thumbnailPath": "",
                    "videoPath": ""
                },
                "success": True
            })
    else:
        return jsonify({
            "data": {
                "code": "VALUE_RANGE_ERROR",
                "message": "缩略图横向、纵向数量均需要大于0。",  # 提示信息
                "thumbnailPath": "",
                "videoPath": ""
            },
            "success": True
        })


@api.route('/api/uploadPicture', methods=['GET'])
#  用于上传本地图片到图床
def api_upload_picture():
    # 从请求URL中获取参数
    picture_path = request.args.get('picturePath', default='', type=str)

    picture_bed_api_url = request.args.get('pictureBedApiUrl', default=get_settings("picture_bed_api_url"), type=str)
    if picture_bed_api_url == '':
        picture_bed_api_url = get_settings("picture_bed_api_url")

    picture_bed_api_token = request.args.get('pictureBedApiToken', default=get_settings("picture_bed_api_token"),
                                             type=str)
    if picture_bed_api_token == '':
        picture_bed_api_token = get_settings("picture_bed_api_token")

    if os.path.exists(picture_path):
        upload_picture_success, response = upload_picture(picture_bed_api_url, picture_bed_api_token, picture_path)
        if upload_picture_success:
            return jsonify({
                "data": {
                    "code": "OK",
                    "message": "上传图片成功。",  # 提示信息
                    "pictureUrl": response  # 注意是[img]1.png[/img]的bbcode格式
                },
                "success": True
            })
        else:
            return jsonify({
                "data": {
                    "code": "GENERAL_ERROR",
                    "message": f"上传图片失败：{response}。",  # 提示信息
                    "pictureUrl": ""  # 注意是[img]1.png[/img]的bbcode格式
                },
                "success": True
            })

    else:
        return jsonify({
            "data": {
                "code": "FILE_PATH_ERROR",
                "message": "您提供的图片路径有误。",  # 提示信息
                "pictureUrl": ""
            },
            "success": True
        })


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
                    "code": "OK",
                    "message": "获取MediaInfo成功。",  # 提示信息
                    "mediaInfo": response,
                    "videoPath": video_path
                },
                "success": True
            })
        else:
            return jsonify({
                "data": {
                    "code": "GENERAL_ERROR",
                    "message": f"获取视频路径成功，但是获取MediaInfo失败，错误：{response}。",  # 提示信息
                    "mediaInfo": "",
                    "videoPath": video_path
                },
                "success": True
            })
    else:
        return jsonify({
            "data": {
                "code": "FILE_PATH_ERROR",
                "message": f"获取视频路径失败，{video_path}。",  # 提示信息
                "mediaInfo": "",
                "videoPath": ""
            },
            "success": True
        })


@api.route('/api/getVideoInfo', methods=['GET'])
# 用于获取视频关键信息，传入一个文件地址或者一个文件夹地址，返回视频文件路径和关键信息
def api_get_video_info():
    # 从请求URL中获取path
    path = request.args.get('path', default='', type=str)

    is_video_path, video_path = check_path_and_find_video(path)  # 视频资源的路径
    if is_video_path == 1 or is_video_path == 2:
        get_video_info_success, response = get_video_info(video_path)
        if get_video_info_success:
            print("获取到关键参数：" + str(response))
            video_format = response[0]
            video_codec = response[1]
            bit_depth = response[2]
            hdr_format = response[3]
            frame_rate = response[4]
            audio_codec = response[5]
            channels = response[6]
            return jsonify({
                "data": {
                    "code": "OK",
                    "message": "获取视频关键参数成功。",  # 提示信息
                    "videoPath": video_path,
                    "videoFormat": video_format,
                    "videoCodec": video_codec,
                    "bitDepth": bit_depth,
                    "hdrFormat": hdr_format,
                    "frameRate": frame_rate,
                    "audioCodec": audio_codec,
                    "channels": channels
                },
                "success": True
            })
        else:
            return jsonify({
                "data": {
                    "code": "GENERAL_ERROR",
                    "message": f"获取视频关键参数失败：{response[0]}。",  # 提示信息
                    "videoPath": video_path,
                    "videoFormat": "",
                    "videoCodec": "",
                    "bitDepth": "",
                    "hdrFormat": "",
                    "frameRate": "",
                    "audioCodec": "",
                    "channels": "",
                },
                "success": True
            })
    else:
        return jsonify({
            "data": {
                "code": "FILE_PATH_ERROR",
                "message": f"获取视频路径失败，{video_path}。",  # 提示信息
                "videoPath": "",
                "videoFormat": "",
                "videoCodec": "",
                "bitDepth": "",
                "hdrFormat": "",
                "frameRate": "",
                "audioCodec": "",
                "channels": ""
            },
            "success": True
        })


@api.route('/api/getPtGenDescription', methods=['GET'])
# 用于获取PT-Gen简介，传入一个豆瓣链接，返回PT-Gen简介
def api_get_pt_gen_description():
    # 从请求URL中获取参数
    resource_url = request.args.get('resourceUrl', default='', type=str)

    pt_gen_api_url = request.args.get('ptGenApiUrl', default=get_settings("pt_gen_api_url"), type=str)
    if pt_gen_api_url == '':
        pt_gen_api_url = get_settings("pt_gen_api_url")

    if pt_gen_api_url == '':
        pt_gen_api_url = get_settings("pt_gen_api_url")
    get_pt_gen_description_success, response = get_pt_gen_description(pt_gen_api_url, resource_url)
    if get_pt_gen_description_success:
        return jsonify({
            "data": {
                "code": "OK",
                "message": "获取PT-Gen简介成功。",  # 提示信息
                "description": response
            },
            "success": True
        })
    else:
        return jsonify({
            "data": {
                "code": "GENERAL_ERROR",
                "message": f"获取PT-Gen简介失败，{response}。",  # 提示信息
                "description": ""
            },
            "success": True
        })


@api.route('/api/getPtGenInfo', methods=['GET'])
# 用于获取PT-Gen简介，传入一个豆瓣链接，返回PT-Gen简介
def api_get_pt_gen_info():
    # 从请求URL中获取参数
    description = request.args.get('description', default='', type=str)

    if description and description != '':
        try:
            original_title, english_title, year, other_names_sorted, category, actors_list = get_pt_gen_info(
                description)
            print(original_title, english_title, year, other_names_sorted, category, actors_list)
            actors = ''
            other_titles = ''
            is_first = True
            for data in actors_list:  # 把演员名转化成str
                if is_first:
                    actors += data
                    is_first = False
                else:
                    actors += ' / '
                    actors += data
            for data in other_names_sorted:  # 把别名转化为str
                other_titles += data
                other_titles += ' / '
            other_titles = other_titles[: -3]
            return jsonify({
                "data": {
                    "code": "OK",
                    "message": "获取PT-Gen简介关键参数成功。",  # 提示信息
                    "originalTitle": original_title,
                    "englishTitle": english_title,
                    "year": year,
                    "otherTitles": other_titles,
                    "category": category,
                    "actors": actors
                },
                "success": True
            })
        except Exception as e:
            return jsonify({
                "data": {
                    "code": "GENERAL_ERROR",
                    "message": f"对于简介的分析有错误：{e}。",  # 提示信息
                    "originalTitle": "",
                    "englishTitle": "",
                    "year": "",
                    "otherTitles": "",
                    "category": "",
                    "actors": ""
                },
                "success": True
            })
    else:
        return jsonify({
            "data": {
                "code": "MISSING_REQUIRED_PARAMETER",
                "message": "您输入的简介为空。",  # 提示信息
                "originalTitle": "",
                "englishTitle": "",
                "year": "",
                "otherTitles": "",
                "category": "",
                "actors": ""
            },
            "success": True
        })


@api.route('/api/makeTorrent', methods=['GET'])
# 用于获取PT-Gen简介，传入一个豆瓣链接，返回PT-Gen简介
def api_make_torrent():
    # 从请求URL中获取参数
    path = request.args.get('path', default='', type=str)

    torrent_storage_path = request.args.get('torrentStoragePath', default=get_settings("torrent_storage_path"),
                                            type=str)
    if torrent_storage_path == '':
        torrent_storage_path = get_settings("torrent_storage_path")

    if os.path.exists(path):
        make_torrent_success, response = make_torrent(path, torrent_storage_path)
        if make_torrent_success:
            return jsonify({
                "data": {
                    "code": "OK",
                    "message": "制作种子成功。",  # 提示信息
                    "torrentPath": response
                },
                "success": True
            })
        else:
            return jsonify({
                "data": {
                    "code": "GENERAL_ERROR",
                    "message": f"制作种子失败，{response}。",  # 提示信息
                    "torrentPath": ""
                },
                "success": True
            })
    else:
        return jsonify({
            "data": {
                "code": "FILE_PATH_ERROR",
                "message": "文件路径不存在。",  # 提示信息
                "torrentPath": ""
            },
            "success": True
        })
