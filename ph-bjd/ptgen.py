import requests


def fetch_and_format_pt_gen_data(api_url, resource_url):
    try:
        # 设置一个合理的超时时间，例如10秒
        response = requests.get(f"{api_url}?url={resource_url}", timeout=10)

        # 检查响应是否成功
        if response.status_code != 200:
            print("请求失败，状态码:", response.status_code)
            return False, "Pt-Gen请求失败，状态码:" + str(response.status_code)

        # 尝试解析JSON响应
        try:
            data = response.json()
        except ValueError:
            print("响应不是有效的JSON格式")
            return False, "Pt-Gen响应不是有效的JSON格式"

        # 根据响应结构获取format字段
        format_data = data.get("format") if "format" in data else data.get("data", {}).get("format", "")

        # 返回处理后的format字段
        # print(format_data)
        format_data += '\n'
        format_data = format_data.replace('img1', 'img2')
        return True, format_data

    except requests.Timeout:
        # 处理超时异常
        print("请求超时")
        return False, "Pt-Gen请求超时"

    except requests.RequestException as e:
        # 处理请求过程中的其他异常
        print(f"请求发生错误: {e}")
        return False, f"Pt-Gen请求发生错误: {e}"
