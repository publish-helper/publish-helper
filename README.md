Publish Helper for Movie v1.1.4

使用前务必请先看设置！！！

目前支持的免费公共图床：https://freeimage.host/

图床的api地址和密钥请去图床主页左上角获取

如果您发现自动命名时视频、音频的编码格式没有正确识别，请参考格式修改以下文件：

static/abbreviation.json

    "Dolby TrueHD with Dolby Atmos": "Atmos TrueHD",
    "Dolby Digital Plus with Dolby Atmos": "Atmos DDP",
    "Dolby Digital Plus": "DDP",
    "DTS-HD Master Audio": "DTS-HD MA",
    "没有正确识别所产生的信息": "你想要的缩略信息",

如需修改来源名称或小组名称，请访问：

static/source.json
static/team.json

软件获取地址：

https://gitee.com/bjdbjd/ph-bjd-movie/releases

Python 3.10

Created by bjd