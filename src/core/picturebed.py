# 此处仅提供一个简单的示例，具体实现起来方案有很多，可按需开发
import json
import os

import requests

from src.core.tool import get_picture_bed_type


def upload_picture(picture_bed_api_url, picture_bed_api_token, picture_path):
    print(picture_bed_api_url, picture_bed_api_token, picture_path)
    if not os.path.exists(picture_path):
        print("图片文件路径不存在")
        return False, "图片文件路径不存在"
    else:
        print("开始获取图床类型")
        get_picture_bed_type_success, picture_bed_type = get_picture_bed_type(picture_bed_api_url)
        if get_picture_bed_type_success:
            print(f"获取到图床的类型：{picture_bed_type}")
            if picture_bed_type == "lsky-pro":
                return lsky_pro_picture_bed(picture_bed_api_url, picture_bed_api_token, picture_path)
            elif picture_bed_type == "bohe":
                return agsv_picture_bed(picture_bed_api_url, picture_bed_api_token, picture_path)
            elif picture_bed_type == "chevereto":
                return chevereto_picture_bed(picture_bed_api_url, picture_bed_api_token, picture_path)
            elif picture_bed_type == "freeimage":
                return freeimage_picture_bed(picture_bed_api_url, picture_bed_api_token, picture_path)
            elif picture_bed_type == "imgbb":
                return imgbb_picture_bed(picture_bed_api_url, picture_bed_api_token, picture_path)
            else:
                return False, "你改了图床配置文件？冒号前面的类型是不能随便改的！如果需要支持更多新类型的图床请提Issues，前提是图床支持API上传！"
        else:
            return False, picture_bed_type


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
        print("请求过程中出现错误：", e)
        return False, "请求过程中出现错误：" + str(e)

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
    data = {'key': api_token, 'format': 'txt'}
    files = {'source': (frame_path, open(frame_path, 'rb'), "image/png")}
    print('值已经获取')
    try:
        # 发送POST请求
        print("开始发送上传图床的请求")
        res = requests.post(url, data=data, files=files)
        print("已成功发送上传图床的请求")
    except requests.RequestException as e:
        print("请求过程中出现错误：", e)
        return False, "请求过程中出现错误：" + str(e)

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
    data = {'expiration': '600', 'key': api_token}
    files = {'image': (frame_path, open(frame_path, 'rb'), "image/png")}
    print('值已经获取')
    try:
        # 发送POST请求
        print("开始发送上传图床的请求")
        res = requests.post(url, data=data, files=files)
        print("已成功发送上传图床的请求")
    except requests.RequestException as e:
        print("请求过程中出现错误：", e)
        return False, "请求过程中出现错误：" + str(e)

    try:
        data = json.loads(res.text)
        # 提取所需的URL
        image_url = data["data"]["image"]["url"]
        print(image_url)
        return True, '[img]' + image_url + '[/img]'
    except KeyError as e:
        print(False, "图床响应结果缺少所需的值：" + str(e))
        return False, "图床响应结果缺少所需的值：" + str(e) + str(res)
    except json.JSONDecodeError as e:
        print(False, "处理返回的JSON过程中出现错误：" + str(e))
        return False, "处理返回的JSON过程中出现错误：" + str(e) + str(res)


def lsky_pro_picture_bed(api_url, api_token, frame_path):
    print('接受到上传ptvicomo图床请求')
    url = api_url
    files = {'file': (frame_path, open(frame_path, 'rb'), "image/png")}
    headers = {'Authorization': api_token, 'Accept': 'json'}
    data = {}
    print('值已经获取')
    try:
        # 发送POST请求
        print("开始发送上传图床的请求")
        res = requests.post(url, headers=headers, data=data, files=files)
        print("已成功发送上传图床的请求")
    except requests.RequestException as e:
        print("请求过程中出现错误：", e)
        return False, "请求过程中出现错误：" + str(e)

    try:
        data = json.loads(res.text)
        # 提取所需的URL
        image_url = data["data"]["links"]["bbcode"]
        print(image_url)
        return True, image_url
    except KeyError as e:
        print(False, "图床响应结果缺少所需的值：" + str(e))
        return False, "图床响应结果缺少所需的值：" + str(e) + str(res)
    except json.JSONDecodeError as e:
        print(False, "处理返回的JSON过程中出现错误：" + str(e))
        return False, "处理返回的JSON过程中出现错误：" + str(e) + str(res)


def chevereto_picture_bed(api_url, api_token, frame_path):
    print('接受到上传chevereto图床请求')
    url = api_url
    data = {'expiration': 'PT5M', 'X-API-Key': api_token, "key": api_token}
    files = {'source': (frame_path, open(frame_path, 'rb'), "image/png")}
    print('值已经获取')
    try:
        # 发送POST请求
        print("开始发送上传图床的请求")
        res = requests.post(url, data=data, files=files)
        print("已成功发送上传图床的请求")
    except requests.RequestException as e:
        print("请求过程中出现错误：", e)
        return False, "请求过程中出现错误：" + str(e)

    try:
        print(res.text)
        data = json.loads(res.text)
        # 提取所需的URL
        image_url = data["image"]["url"]
        print(image_url)
        return True, '[img]' + image_url + '[/img]'
    except KeyError as e:
        print(False, "图床响应结果缺少所需的值：" + str(e))
        return False, "图床响应结果缺少所需的值：" + str(e) + str(res)
    except json.JSONDecodeError as e:
        print(False, "处理返回的JSON过程中出现错误：" + str(e))
        return False, "处理返回的JSON过程中出现错误：" + str(e) + str(res)
