import json
import os

from pymediainfo import MediaInfo


def get_media_info(file_path):
    if not os.path.exists(file_path):
        print("文件路径不存在")
        return False, "视频文件路径不存在"

    try:
        # 尝试解析媒体信息
        media_info = MediaInfo.parse(file_path)
        json_data = media_info.to_json()

        # 解析 JSON 数据
        data = json.loads(json_data)

        # 初始化输出字符串
        output = ""

        # 初始化计数器
        audio_count, text_count = 1, 1

        # 遍历所有 track
        for track in data["tracks"]:
            if track["track_type"] == "General":
                # 处理 General 类型的 track
                output += "General\n"
                for key, label in [
                    ("other_unique_id", "Unique ID"),
                    ("complete_name", "Complete name"),
                    ("other_format", "Format"),
                    ("format_version", "Format version"),
                    ("other_file_size", "File size"),
                    ("other_duration", "Duration"),
                    ("other_overall_bit_rate_mode", "Overall bit rate mode"),
                    ("other_overall_bit_rate", "Overall bit rate"),
                    ("other_frame_rate", "Frame rate"),
                    ("movie_name", "Movie name"),
                    ("encoded_date", "Encoded date"),
                    ("writing_application", "Writing application"),
                    ("writing_library", "Writing library"),
                    ("comment", "Comment")
                ]:
                    value = track[key][0] if isinstance(track.get(key), list) else track.get(key)
                    if value is not None:
                        output += f"{label:36}: {value}\n"
                output += "\n"

            elif track["track_type"] == "Video":
                # 处理 Video 类型的 track
                output += "Video\n"
                for key, label in [
                    ("track_id", "ID"),
                    ("other_format", "Format"),
                    ("format_info", "Format/Info"),
                    ("format_profile", "Format profile"),
                    ("format_settings", "Format settings"),
                    ("format_settings__cabac", "Format settings, CABAC"),
                    ("other_format_settings__reference_frames", "Format settings, Reference frames"),
                    ("other_hdr_format", "HDR format"),
                    ("codec_id", "Codec ID"),
                    ("other_duration", "Duration"),
                    ("other_bit_rate", "Bit rate"),
                    ("other_width", "Width"),
                    ("other_height", "Height"),
                    ("other_display_aspect_ratio", "Display aspect ratio"),
                    ("other_frame_rate_mode", "Frame rate mode"),
                    ("other_frame_rate", "Frame rate"),
                    ("color_space", "Color space"),
                    ("other_chroma_subsampling", "Chroma subsampling"),
                    ("other_bit_depth", "Bit depth"),
                    ("scan_type", "Scan type"),
                    ("bits__pixel_frame", "Bits/(Pixel*Frame)"),
                    ("other_stream_size", "Stream size"),
                    ("other_writing_library", "Writing library"),
                    ("encoding_settings", "Encoding settings"),
                    ("default", "Default"),
                    ("forced", "Forced"),
                    ("color_range", "Color range"),
                    ("color_primaries", "Color primaries"),
                    ("transfer_characteristics", "Transfer characteristics"),
                    ("matrix_coefficients", "Matrix coefficients"),
                    ("mastering_display_color_primaries", "Mastering display color primaries"),
                    ("mastering_display_luminance", "Mastering display luminance"),
                    ("maximum_content_light_level", "Maximum Content Light Level"),
                    ("maxcll_original", "MaxCLL Original"),
                    ("maximum_frameaverage_light_level", "Maximum Frame-Average Light Level"),
                    ("maxfall_original", "MaxFALL Original"),
                ]:
                    value = track[key][0] if isinstance(track.get(key), list) else track.get(key)
                    if value is not None:
                        output += f"{label:36}: {value}\n"
                output += "\n"

            elif track["track_type"] == "Audio":
                # 处理 Audio 类型的 track
                output += f"\nAudio #{audio_count}\n"
                audio_count += 1
                for key, label in [
                    ("track_id", "ID"),
                    ("other_format", "Format"),
                    ("format_info", "Format/Info"),
                    ("other_commercial_name", "Commercial name"),
                    ("codec_id", "Codec ID"),
                    ("other_duration", "Duration"),
                    ("other_bit_rate_mode", "Bit rate mode"),
                    ("other_bit_rate", "Bit rate"),
                    ("other_maximum_bit_rate", "Maximum bit rate"),
                    ("other_channel_s", "Channel(s)"),
                    ("channel_layout", "Channel layout"),
                    ("other_sampling_rate", "Sampling rate"),
                    ("other_frame_rate", "Frame rate"),
                    ("other_compression_mode", "Compression mode"),
                    ("other_delay_relative_to_video", "Delay relative to video"),
                    ("other_stream_size", "Stream size"),
                    ("title", "Title"),
                    ("other_language", "Language"),
                    ("default", "Default"),
                    ("forced", "Forced"),
                    ("complexity_index", "Complexity index"),
                    ("number_of_dynamic_objects", "Number of dynamic objects"),
                    ("other_bed_channel_count", "Bed channel count"),
                    ("bed_channel_configuration", "Bed channel configuration"),
                ]:
                    value = track[key][0] if isinstance(track.get(key), list) else track.get(key)
                    if value is not None:
                        output += f"{label:36}: {value}\n"
                output += "\n"

            elif track["track_type"] == "Text":
                # 处理 Text 类型的 track
                output += f"\nText #{text_count}\n"
                text_count += 1
                for key, label in [
                    ("other_track_id", "ID"),
                    ("other_format", "Format"),
                    ("muxing_mode", "Muxing mode"),
                    ("codec_id", "Codec ID"),
                    ("codec_id_info", "Codec ID/Info"),
                    ("other_duration", "Duration"),
                    ("other_bit_rate", "Bit rate"),
                    ("other_frame_rate", "Frame rate"),
                    ("count_of_elements", "Count of elements"),
                    ("other_stream_size", "Stream size"),
                    ("title", "Title"),
                    ("other_language", "Language"),
                    ("default", "Default"),
                    ("forced", "Forced"),
                ]:
                    value = track[key][0] if isinstance(track.get(key), list) else track.get(key)
                    if value is not None:
                        output += f"{label:36}: {value}\n"
                output += "\n"
        output += "Created by ph-bjd"

        return True, output

    except OSError as e:
        # 文件路径相关的错误
        print(f"文件路径错误: {e}")
        return False, f"文件路径错误: {e}"
    except Exception as e:
        # MediaInfo无法解析文件
        print(f"无法解析文件: {e}")
        return False, f"无法解析文件: {e}"
