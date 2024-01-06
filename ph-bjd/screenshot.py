import json
import os
import random

import cv2
import numpy as np
import requests

from tool import generate_image_filename


# 参数：video_path：源视频路径；output_path：输出图片路径；num_images：截图的总数量；start_pct：截图的起始帧占比，避免截取黑帧；
# end_pct：截图的结束帧占比，中间的范围不要太小，否则会导致截图数量不够；min_interval_pct：最小帧间隔占比，避免连续截图；
# some_threshold：参数，用于判断关键帧的复杂程度，数字越大越复杂，不宜过大，否则可能会导致截图数量不够
def extract_complex_keyframes(video_path, output_path, num_images, some_threshold, start_pct, end_pct,
                              min_interval_pct=0.01):
    # 确保输出路径存在
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print("已创建输出路径")
    except PermissionError:
        print("权限不足，无法创建目录。")
        return False, ["权限不足，无法创建目录。"]
    except FileExistsError:
        print("路径已存在，且不是目录。")
        return False, ["路径已存在，且不是目录。"]
    except Exception as e:
        print(f"创建目录时出错：{e}")
        return False, [f"创建目录时出错：{e}"]

    # 加载视频
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("无法加载视频。")
        return False, ["无法加载视频。"]
    else:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps
        print("加载视频成功")

        # 计算起止时间帧编号
        start_frame = int(total_frames * start_pct)
        end_frame = int(total_frames * end_pct)
        min_interval = duration * min_interval_pct
        print("起止帧：" + str(start_frame) + " 终止帧：" + str(end_frame) + " 最小帧间隔" + str(min_interval))

        # 初始化变量
        extracted_images = []
        bbsurls = ""
        last_keyframe_time = -min_interval

        # 生成随机时间戳
        timestamps = sorted(random.sample(range(start_frame, end_frame), num_images))

        for timestamp in timestamps:
            # 跳转到特定帧
            cap.set(cv2.CAP_PROP_POS_FRAMES, timestamp)
            ret, frame = cap.read()
            if not ret:
                continue

            current_time = timestamp / fps
            if current_time >= last_keyframe_time + min_interval:
                std_dev = np.std(frame)
                print(f"Frame ID: {timestamp}, Timestamp: {current_time}, Std Dev: {std_dev}")  # 调试信息

                if std_dev > some_threshold:
                    frame_path = generate_image_filename(output_path)
                    cv2.imwrite(frame_path, frame)
                    extracted_images.append(frame_path)
                    last_keyframe_time = current_time

        cap.release()

        print(extracted_images)
        return True, extracted_images


def get_thumbnails(video_path, output_path, cols, rows, start_pct, end_pct):
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            print("已创建输出路径")
    except PermissionError:
        print("权限不足，无法创建目录。")
        return False, ["权限不足，无法创建目录。"]
    except FileExistsError:
        print("路径已存在，且不是目录。")
        return False, ["路径已存在，且不是目录。"]
    except Exception as e:
        print(f"创建目录时出错：{e}")
        return False, [f"创建目录时出错：{e}"]

    try:
        video_capture = cv2.VideoCapture(video_path)

        if not video_capture.isOpened():
            raise Exception("Error: 无法打开视频文件")

        total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

        # 计算开始和结束帧
        start_frame = int(total_frames * start_pct)
        end_frame = int(total_frames * end_pct)

        # 计算每张截取图像的时间间隔
        interval = (end_frame - start_frame) // (rows * cols)

        images = []

        for i in range((rows * cols)):
            frame_number = start_frame + i * interval
            if frame_number >= end_frame:
                break

            video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = video_capture.read()

            if not ret:
                raise Exception(f"Error: 无法读取第 {i + 1} 张图像")

            images.append(frame)

        # 处理图像数量小于预期的情况
        if len(images) < (rows * cols):
            print(f"Warning: 只能获取 {len(images)} 张图像，小于预期的 {rows * cols} 张")

        resized_images = [cv2.resize(image, (0, 0), fx=1.0 / cols, fy=1.0 / cols) for image in images]

        border_size = 5
        concatenated_image = np.ones((rows * (resized_images[0].shape[0] + 2 * border_size),
                                      cols * (resized_images[0].shape[1] + 2 * border_size), 3), dtype=np.uint8) * 255

        for i in range(rows):
            for j in range(cols):
                index = i * cols + j
                if index >= len(resized_images):
                    break
                y_offset = i * (resized_images[0].shape[0] + 2 * border_size) + border_size
                x_offset = j * (resized_images[0].shape[1] + 2 * border_size) + border_size

                concatenated_image[y_offset:y_offset + resized_images[0].shape[0],
                x_offset:x_offset + resized_images[0].shape[1]] = resized_images[index]

        sv_path = generate_image_filename(output_path)
        cv2.imwrite(sv_path, concatenated_image)

    except Exception as e:
        print(f"发生异常: {e}")
        return False, str(e)

    finally:
        video_capture.release()

    print(f"拼接后的图像已保存到{sv_path}")
    return True, sv_path


# 此处仅提供一个简单的示例，具体实现起来方案有很多，可按需开发
def upload_screenshot(api_url, api_token, frame_path):
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
        return False, {"请求过程中出现错误:" + str(e)}

    # 关闭文件流，避免资源泄露
    files['uploadedFile'][1].close()

    # 将响应文本转换为字典
    try:
        api_response = json.loads(res.text)
    except json.JSONDecodeError:
        print("响应不是有效的JSON格式")
        return False, {}

    # 打印提取的url
    if api_response.get("statusCode", "") == "200":
        print(api_response.get("bbsurl", ""))

    # 返回完整的响应数据，以便进一步处理
    return True, api_response


def upload_free_screenshot(api_url, api_token, frame_path):
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
        bbsurl = '[img]' + res.text + '[/img]'
        print(bbsurl)
        return True, bbsurl
    else:
        return False, res.text
