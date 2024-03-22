# 此处仅提供一个简单的示例，具体实现起来方案有很多，可按需开发
import json

import requests


def upload_screenshot(api_url, api_token, frame_path):
    print(api_url, api_token, frame_path)
    if 'https://img.agsv.top/api/' in api_url:
        return agsv_picture_bed(api_url, api_token, frame_path)
    if 'https://freeimage.host/api' in api_url:
        return freeimage_picture_bed(api_url, api_token, frame_path)
    if 'https://api.imgbb.com/1/upload' in api_url:
        return imgbb_picture_bed(api_url, api_token, frame_path)
    return False, '图床暂不支持'


def agsv_picture_bed(api_url, api_token, frame_path):
    print("开始上传官方图床")
    url = api_url
    files = {'uploadedFile': (frame_path, open(frame_path, 'rb'), "image/png")}
    data = {'api_token': api_token, 'image_compress': 0, 'image_compress_level': 80}

    try:
        # 发送POST请求
        res = requests.post(url, data=data, files=files)
        print("已成功发送上传图床的请求")
    except requests.RequestException as e:
        print("请求过程中出现错误:", e)
        return False, "请求过程中出现错误:" + str(e)

    # 关闭文件流，避免资源泄露
    files['uploadedFile'][1].close()

    # 将响应文本转换为字典
    try:
        print(str(res.text))
        api_response = json.loads(res.text)
    except json.JSONDecodeError:
        print("响应不是有效的JSON格式")
        return False, "响应不是有效的JSON格式"

    # 打印提取的url
    if api_response.get("statusCode", "") == "200":
        print(api_response.get("bbsurl", ""))
        if api_response.get("statusCode", "") == "200":
            bbs_url = str(api_response.get("bbsurl", ""))
            return True, bbs_url
        if api_response.get("statusCode", "") == "":
            return False, "未接受到响应"
        else:
            return False, str(api_response)


def freeimage_picture_bed(api_url, api_token, frame_path):
    print('接受到上传freeimage图床请求')
    url = api_url
    files = {'source': (frame_path, open(frame_path, 'rb'), "image/png")}
    data = {'key': api_token,
            'format': 'txt'
            }
    print('值已经获取')
    try:
        # 发送POST请求
        print("开始发送上传图床的请求")
        res = requests.post(url, data=data, files=files)
        print("已成功发送上传图床的请求")
    except requests.RequestException as e:
        print("请求过程中出现错误:", e)
        return False, "请求过程中出现错误:" + str(e)

    print(res.text)
    if res.text[:4] == "http":
        bbs_url = '[img]' + res.text + '[/img]'
        print(bbs_url)
        return True, bbs_url
    else:
        return False, res.text


def imgbb_picture_bed(api_url, api_token, frame_path):
    print('接受到上传imgbb图床请求')
    url = api_url
    files = {'image': (frame_path, open(frame_path, 'rb'), "image/png")}
    data = {'expiration': '600',
            'key': api_token,
            }
    print('值已经获取')
    try:
        # 发送POST请求
        print("开始发送上传图床的请求")
        res = requests.post(url, data=data, files=files)
        print("已成功发送上传图床的请求")
    except requests.RequestException as e:
        print("请求过程中出现错误:", e)
        return False, "请求过程中出现错误:" + str(e)

    try:
        data = json.loads(res.text)
        # 提取所需的URL
        image_url = data["data"]["image"]["url"]
        print(image_url)
        return True, '[img]' + image_url + '[/img]'
    except KeyError as e:
        print(False, "您输入的Api密钥有问题" + str(e))
        return False, "您输入的Api密钥有问题" + str(e) + str(res)
    except json.JSONDecodeError as e:
        print(False, "处理返回的JSON过程中出现错误:" + str(e))
        return False, "处理返回的JSON过程中出现错误:" + str(e) + str(res)
