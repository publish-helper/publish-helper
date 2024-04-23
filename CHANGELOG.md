# 发布记录

## v1.4.5

* 标准化项目结构
  * 当前ph-bjd当包名报错
* 将gui与api分离在不同包
  * 方便在API打包时剥离gui依赖
  * 因为服务器部署时，环境不支持gui相关依赖，而python项目在启动时只要import gui包，就会自动加载gui相关依赖，导致启动失败
* 增加docker构建脚本
* 增加pyproject.toml文件，管理版本及依赖，*当前未启用*
* 注释掉requirements.txt文件中，pyqt6-plugins与pyqt6-tools，在PyQt6新版本中已经集成，不注释依赖冲突
* 增加.gitignore配置文件