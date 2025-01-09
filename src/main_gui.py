"""
Publish Helper  Copyright (C) 2023  BJD
This program comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
This is free software, and you are welcome to redistribute it
under certain conditions; type `show c' for details.

The licensing of this program is under the GNU General Public License version 3 (GPLv3) or later.
For more information on this license, you can visit https://www.gnu.org/licenses/gpl-3.0.html
"""

"""
打包编译方式(Windows)：安装Python 3.10，执行pip install pyinstaller，安装“docs/requirements.txt”中的所有相关模块后，在项目根目录（README文件所在目录）下执行下面的代码：

pyinstaller --paths="src;." -F -w -i static/ph-bjd.ico src/main_gui.py -n "Publish Helper.exe"
xcopy static dist\static /E /I /Y
if not exist "dist\media" mkdir dist\media\
copy Mandarin.dat dist\
copy LICENSE dist\
copy README.md dist\
copy readme.txt dist\

项目根目录下生成的dist文件夹就是打包好的软件。
项目仓库地址：https://github.com/bjdbjd/publish-helper
如果有帮助到您，请帮忙给仓库点亮Star，万分感谢！！！
"""
# GUI启动
from src.gui.startgui import start_gui

# 作者：bjdbjd ID：bjd
# 贡献者：Pixel-LH、EasonWong0603、sertion1126、TommyMerlin
if __name__ == '__main__':
    start_gui()  # GUI启动
