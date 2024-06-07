# 感谢明日大佬、N佬做出的贡献！！！ID：tomorrow505、Exception
import re

from src.core.tool import get_settings, base64encoding
from urllib.parse import quote


def get_auto_feed_link(mian_title, second_title, description, media_info, file_name, category, team, source,
                       torrent_url):
    auto_feed_link = str(get_settings("auto_feed_link"))
    name = mian_title  # 主标题
    small_descr = second_title  # 副标题
    url = ''  # IMDb链接
    dburl = ''  # 豆瓣链接
    descr = description  # 简介
    media_info = media_info  # MI
    torrent_name = file_name + '.torrent'  # 种子名称
    category = category  # 类型
    source_sel = ''  # 地区
    standard_sel = ''  # 分辨率
    audiocodec_sel = ''  # 音频编码
    codec_sel = ''  # 视频编码
    medium_sel = ''  # 媒介
    team = team  # 小组
    print("变量初始化完成")

    # 获取IMDb链接
    imdb_pattern = r"https://www\.imdb\.com/title/tt\d+/"
    match = re.search(imdb_pattern, description)
    # If a match is found, return it as a string, otherwise return an empty string
    url += match.group(0) if match else ""
    print("获取到IMDb链接" + url)

    # 获取豆瓣链接
    douban_pattern = r"https://movie\.douban\.com/subject/\d+/"
    match = re.search(douban_pattern, description)
    # If a match is found, return it as a string, otherwise return an empty string
    dburl += match.group(0) if match else ""
    print("获取到豆瓣链接" + dburl)

    # 获取其他类型 电影/纪录/体育/剧集/动画/综艺……
    category_pattern = r"◎类　　别　([^\n]+)"
    match = re.search(category_pattern, description)
    # If a match is found, return it as a string, otherwise return an empty string
    t = match.group(0) if match else ""
    if "纪录" in t:
        category = "纪录"
    if "体育" in t:
        category = "体育"
    if "动画" in t:
        category = "动画"
    if "综艺" in t or "脱口秀" in t:
        category = "综艺"
    if "短片" in t:
        category = "短剧"
    print("获取到类型" + category)

    # 获取产地 欧美/大陆/港台/日本/韩国/印度
    area_pattern = r"◎产　　地　([^\n]+)"
    match = re.search(area_pattern, description)
    # If a match is found, return the matched location, otherwise return an empty string
    s = match.group(1) if match else ""
    if "美国" in s or "英国" in s or "德国" in s or "法国" in s:
        source_sel = "欧美"
    if "大陆" in s:
        source_sel = "大陆"
    if "香港" in s or "台湾" in s:
        source_sel = "港台"
    if "日本" in s:
        source_sel = "日本"
    if "韩国" in s:
        source_sel = "韩国"
    if "印度" in s:
        source_sel = "印度"
    print("获取到产地" + source_sel)

    # 获取分辨率 4K/1080p/1080i/720p/SD
    if "3840p" in mian_title or "3840P" in mian_title or "3840i" in mian_title:
        standard_sel = "8K"
    if "2160p" in mian_title or "2160P" in mian_title or "2160i" in mian_title:
        standard_sel = "4K"
    if "1080p" in mian_title or "1080P" in mian_title:
        standard_sel = "1080p"
    if "1080i" in mian_title:
        standard_sel = "1080i"
    if "720p" in mian_title or "720P" in mian_title:
        standard_sel = "720p"
    if "720i" in mian_title:
        standard_sel = "720i"
    if "480p" in mian_title or "480P" in mian_title:
        standard_sel = "480p"
    if "720i" in mian_title:
        standard_sel = "480i"
    print("获取到分辨率" + standard_sel)

    # 获取音频编码 AAC/AC3/DTS…………
    if "AAC" in mian_title:
        audiocodec_sel = "AAC"
    if "AC3" in mian_title or "DD" in mian_title:
        audiocodec_sel = "AC3"
    if "EAC3" in mian_title or "E-AC3" in mian_title or "DDP" in mian_title or "DD+" in mian_title:
        audiocodec_sel = "EAC3"
    if "DTS" in mian_title:
        if "HD" in mian_title and "MA" in mian_title:
            audiocodec_sel = "DTS-HDMA"
        else:
            audiocodec_sel = "DTS"
    if "Atmos" in mian_title or "ATMOS" in mian_title:
        audiocodec_sel = "Atmos"
    if "TrueHD" in mian_title or "TRUEHD" in mian_title:
        audiocodec_sel = "TrueHD"
    if "Flac" in mian_title or "FLAC" in mian_title:
        audiocodec_sel = "Flac"
    print("获取到音频编码" + audiocodec_sel)

    # 获取视频编码 H264/H265……
    if "H264" in mian_title or "H.264" in mian_title or "h264" in mian_title or "h.264" in mian_title or "AVC" in mian_title or "avc" in mian_title:
        codec_sel = "H264"
    if "H265" in mian_title or "H.265" in mian_title or "h265" in mian_title or "h.265" in mian_title or "HEVC" in mian_title or "hevc" in mian_title:
        codec_sel = "H265"
    if "H266" in mian_title or "H.266" in mian_title or "h266" in mian_title or "h.266" in mian_title or "VVC" in mian_title or "vvc" in mian_title:
        codec_sel = "H266"
    if "X264" in mian_title or "x264" in mian_title:
        codec_sel = "X264"
    if "X265" in mian_title or "x265" in mian_title:
        codec_sel = "X265"
    if "X266" in mian_title or "x266" in mian_title:
        codec_sel = "X266"
    if "AV1" in mian_title or "av1" in mian_title:
        codec_sel = "AV1"
    print("获取到视频编码" + codec_sel)

    # 获取媒介 web-dl/remux/encode……
    if source == "WEB-DL" or "WEB-DL" in mian_title or source == "Web-DL" or "Web-DL" in mian_title or source == "web-dl" or "web-dl" in mian_title or source == "WEBDL" or "WEBDL" in mian_title or source == "WebDL" or "WebDL" in mian_title or source == "webdl" or "webdl" in mian_title:
        medium_sel = "WEB-DL"
    if source == "Blu-ray" or "Blu-ray" in mian_title or source == "Blu-Ray" or "Blu-Ray" in mian_title or source == "BluRay" or "BluRay" in mian_title or source == "UHD Blu-ray" or source == "UHD Blu-Ray" or source == "UHD BluRay":
        if "X26" in codec_sel:
            medium_sel = "Encode"
        else:
            if "Remux" in mian_title or "REMUX" in mian_title or "remux" in mian_title or "mkv" in media_info:
                medium_sel = "Remux"
    if source == "HDTV" or "HDTV" in mian_title:
        medium_sel = "HDTV"
    if source == "DVD" or "DVD" in mian_title:
        medium_sel = "DVD"
    print("获取到媒介" + medium_sel)

    # auto_feed_link = auto_feed_link.replace('{主标题}', name)
    # auto_feed_link = auto_feed_link.replace('{副标题}', small_descr)
    # auto_feed_link = auto_feed_link.replace('{IMDB}', url)
    # auto_feed_link = auto_feed_link.replace('{豆瓣}', dburl)
    # auto_feed_link = auto_feed_link.replace('{简介}', descr)
    # auto_feed_link = auto_feed_link.replace('{MediaInfo}', media_info)
    # auto_feed_link = auto_feed_link.replace('{种子名称}', torrent_name)
    # auto_feed_link = auto_feed_link.replace('{类型}', category)
    # auto_feed_link = auto_feed_link.replace('{地区}', source_sel)
    # auto_feed_link = auto_feed_link.replace('{分辨率}', standard_sel)
    # auto_feed_link = auto_feed_link.replace('{音频编码}', audiocodec_sel)
    # auto_feed_link = auto_feed_link.replace('{视频编码}', codec_sel)
    # auto_feed_link = auto_feed_link.replace('{媒介}', medium_sel)
    # auto_feed_link = auto_feed_link.replace('{小组}', team)
    # auto_feed_link = auto_feed_link.replace('{种子链接}', torrent_url)
    # auto_feed_link = auto_feed_link.replace('%', '%25')
    # auto_feed_link = auto_feed_link.replace('　', '%E3%80%80')
    # auto_feed_link = auto_feed_link.replace(' ', '%20')
    # auto_feed_link = auto_feed_link.replace('\n', '%0A')
    auto_feed_link = auto_feed_link.replace('{主标题}', quote(name))
    auto_feed_link = auto_feed_link.replace('{副标题}', quote(small_descr))
    auto_feed_link = auto_feed_link.replace('{IMDB}', quote(url))
    auto_feed_link = auto_feed_link.replace('{豆瓣}', quote(dburl))
    auto_feed_link = auto_feed_link.replace('{简介}', quote(descr))
    auto_feed_link = auto_feed_link.replace('{MediaInfo}', quote(media_info))
    auto_feed_link = auto_feed_link.replace('{种子名称}', quote(torrent_name))
    auto_feed_link = auto_feed_link.replace('{类型}', quote(category))
    auto_feed_link = auto_feed_link.replace('{地区}', quote(source_sel))
    auto_feed_link = auto_feed_link.replace('{分辨率}', quote(standard_sel))
    auto_feed_link = auto_feed_link.replace('{音频编码}', quote(audiocodec_sel))
    auto_feed_link = auto_feed_link.replace('{视频编码}', quote(codec_sel))
    auto_feed_link = auto_feed_link.replace('{媒介}', quote(medium_sel))
    auto_feed_link = auto_feed_link.replace('{小组}', quote(team))
    auto_feed_link = auto_feed_link.replace('{种子链接}', quote(torrent_url))
    # auto_feed_link = auto_feed_link.replace('%', '%25')
    # auto_feed_link = auto_feed_link.replace('　', '%E3%80%80')
    # auto_feed_link = auto_feed_link.replace(' ', '%20')
    # auto_feed_link = auto_feed_link.replace('\n', '%0A')

    string_to_encode = auto_feed_link.split('#separator#')[1]
    string_encoded = base64encoding(string_to_encode)
    auto_feed_link = auto_feed_link.replace(string_to_encode, "") + string_encoded
    print("获取到auto_feed_link" + auto_feed_link)
    return auto_feed_link

# "https://example.com/upload.php#seperator#name#linkstr#{主标题}#linkstr#small_descr#linkstr#{副标题}#linkstr#url
# #linkstr#{IMDB}#linkstr#dburl#linkstr{豆瓣}#linkstr#descr#linkstr#{简介}[quote]{MediaInfo}[/quote]#linkstr#log_info
# #linkstr##linkstr#tracklist#linkstr##linkstr#music_type#linkstr##linkstr#music_media#linkstr##linkstr#edition_info
# #linkstr##linkstr#music_name#linkstr##linkstr#music_author#linkstr##linkstr#animate_info#linkstr##linkstr#anidb
# #linkstr##linkstr#torrentName#linkstr##linkstr#images#linkstr##linkstr#torrent_name#linkstr#{种子名称}#linkstr#torrent_url
# #linkstr##linkstr#type#linkstr#{类型}#linkstr#source_sel#linkstr#{地区}#linkstr#standard_sel#linkstr#{分辨率}#linkstr
# #audiocodec_sel#linkstr#{音频编码}#linkstr#codec_sel#linkstr#{视频编码}#linkstr#medium_sel#linkstr#{媒介}#linkstr
# #origin_site#linkstr#{小组}#linkstr#origin_url#linkstr##linkstr#golden_torrent#linkstr#false#linkstr#mediainfo_cmct#linkstr#
# #linkstr#imgs_cmct#linkstr##linkstr#full_mediainfo#linkstr##linkstr#subtitles#linkstr##linkstr#youtube_url#linkstr#
# #linkstr#ptp_poster#linkstr##linkstr#comparisons#linkstr##linkstr#version_info#linkstr##linkstr#multi_mediainfo
# #linkstr##linkstr#labels#linkstr#100"
