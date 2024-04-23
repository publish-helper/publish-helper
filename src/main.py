"""
Publish Helper  Copyright (C) 2023  BJD
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.

The licensing of this program is under the GNU General Public License version 3 (GPLv3) or later.
For more information on this license, you can visit https://www.gnu.org/licenses/gpl-3.0.html
"""
"""
打包编译方式(Windows)：安装Python 3.10，执行pip install pyinstaller，安装“requirements.txt”中的所有相关模块后，在项目根目录下执行下面的代码：

pyinstaller -F -w -i static/ph-bjd.ico ph-bjd/main.py -n "Publish Helper.exe"
xcopy static dist\static /E /I /Y
copy Mandarin.dat dist\
copy LICENSE dist\
copy README.md dist\
copy readme.txt dist\

项目根目录下生成的dist文件夹就是打包好的软件。
项目仓库地址：https://github.com/publish-helper/publish-helper
如果有帮助到您，请帮忙给仓库点亮Star，万分感谢！！！
"""

from src.api.startapi import start_api  # API启动

# 作者：bjdbjd ID：bjd
# 贡献者：Pixel-LH、EasonWong0603
if __name__ == '__main__':
    start_api()  # API启动
