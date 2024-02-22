Publish Helper v1.2.3

使用前务必请先看设置！！！

软件功能和界面请见WiKi：https://github.com/bjdbjd/publish-helper/wiki

目前支持的免费公共图床：https://freeimage.host/ https://imgbb.com/

图床的api地址和密钥请去图床主页左上角获取。

如果您发现自动命名时视频、音频的编码格式没有正确识别，请参考格式修改以下文件：

static/abbreviation.json

    "Dolby TrueHD with Dolby Atmos": "Atmos TrueHD",
    "Dolby Digital Plus with Dolby Atmos": "Atmos DDP",
    "Dolby Digital Plus": "DDP",
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
    "无需识别的信息": "（留空）",

如需修改来源名称或小组名称，请访问：

static/source.json
static/team.json

软件获取地址：

https://github.com/bjdbjd/publish-helper/releases/

https://gitee.com/bjdbjd/publish-helper/releases/

更新时只需要保留static文件夹即可将配置完美迁移。

如果出现错误，可能是配置文件结构有变化，请使用最新的static文件。

Python 3.10

Created by bjd