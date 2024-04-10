"""
Publish Helper  Copyright (C) 2023  BJD
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.

The licensing of this program is under the GNU General Public License version 3 (GPLv3) or later.
For more information on this license, you can visit https://www.gnu.org/licenses/gpl-3.0.html
"""

# 打包编译方式：安装Python 3.10或更高版本，执行pip install pyinstaller，安装“requirements.txt中的”所有相关模块后，在项目根目录下执行下面的代码。
# 打包编译代码：pyinstaller -F -w -i static/ph-bjd.ico ph-bjd/main.py -n "Publish Helper.exe"
# 打包编译后需要将项目根目录下的"static"文件夹和"temp"文件夹拷贝到"Publish Helper.exe"所在文件夹中方可运行。
# 项目仓库地址：https://github.com/publish-helper/publish-helper-gui

from startgui import start

# 作者：bjdbjd ID：bjd
if __name__ == '__main__':
    start()  # gui启动
