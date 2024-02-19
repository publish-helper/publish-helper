# 此处仅提供一个简单的示例，具体实现起来方案有很多，可按需开发
import json

import requests



def upload_screenshot(api_url, api_token, frame_path):
    if api_url == 'https://img.agsvpt.com/api/upload/':
        return agsv_ficture_bed(api_url, api_token, frame_path)
    if api_url == 'https://freeimage.host/api/1/upload':
        return freeimage_ficture_bed(api_url, api_token, frame_path)
    return False, '图床暂不支持'



def agsv_ficture_bed(api_url, api_token, frame_path):
    print("开始上传图床")
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


def freeimage_ficture_bed(api_url, api_token, frame_path):
    print('接受到上传其他图床请求')
    url = api_url
    files = {'source': (frame_path, open(frame_path, 'rb'), "image/png")}
    data = {'key': api_token,
            # 'action': 'upload',
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
