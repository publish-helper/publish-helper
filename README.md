Publish Helper v1.3.6

**使用前务必请先看设置！！！**

目前的一些简单的功能有：

1. 自动获取PT-Gen简介信息（需要PT-Gen Api）
2. 自动获取MediaInfo信息
3. 自动截图
4. 自动获取缩略图
5. 并上传图床（需要自行获取图床的Api）
6. 根据简介信息和MediaInfo信息自动分析生成主副标题和文件名
7. 自动将资源塞入文件夹并重命名
8. 自动将资源制作种子
9. 剧集、短剧资源自动批量重命名（新）
10. 支持剧集短剧分集命名（新）
11. 自定义重命名规则（新）
12. 结合auto_feed脚本实现一键上传内容（新）
13. 短剧一键生成简介（新）

软件使用方法请见WiKi：https://github.com/publish-helper/publish-helper-gui/wiki/Publish-Helper-Wiki

目前支持的免费公共图床：https://freeimage.host/ https://imgbb.com/

其他官方图床如有需要欢迎申请定制。

图床的api地址和密钥请去图床主页左上角获取。

如果您发现自动命名时视频、音频的编码格式没有正确识别，请参考格式修改以下文件：

**static/abbreviation.json**

    {
        "SMPTE ST 2094 App 4, Version 1, HDR10+ Profile B compatible" : "HDR10+",
        "SMPTE ST 2086, HDR10 compatible": "HDR10",
    
        "Dolby Digital Plus with Dolby Atmos": "Atmos DDP",
        "Dolby TrueHD with Dolby Atmos": "Atmos TrueHD",
        "DTS-HD Master Audio": "DTS-HD MA",
    
        "L R C LFE Ls Rs Lb Rb": "7.1",
        "L R C LFE Ls Rs": "5.1",
        "L R": "2.0"
    
        "1 920 pixels": "1080p",
        "1 280 pixels": "720p",
        "640 pixels": "480p",
    
        "HEVC": "HEVC",
        "AVC": "AVC",
        "AV1": "AV1",
    
        "没有正确识别所产生的信息": "你想要的缩略信息",
        "无需识别的信息": ""（留空）
    }

如需修改来源名称、小组名称或短剧类型，请访问：

**来源名称：static/source.json**

    {
        "source": [
          "WEB-DL",
          "Remux",
          "Blu-ray",
          "UHD Blu-ray",
          "你想要的来源名称"
        ]
    }

**小组名称：static/team.json**

    {
        "team": [
          "AGSVWEB",
          "AGSVMUS",
          "AGSVPT",
          "GodDramas",
          "CatEDU",
          "Pack",
          "你想要的小组名称"
        ]
    }

**短剧类型：static/type.json**

    {
        "type": [
          "网络收费短剧",
          "网络免费短剧",
          "你想要的短剧类型"
        ]
    }

**软件获取地址：**

https://github.com/publish-helper/publish-helper-gui/releases

https://gitee.com/publish-helper/publish-helper-gui/releases

更新时只需要保留static文件夹即可将配置完美迁移。

如果出现错误，可能是配置文件结构有变化，请使用最新的static文件。

Powered by Python 3.10

Created by bjd