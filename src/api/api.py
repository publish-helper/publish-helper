# from flask import jsonify, request
#
# from src.api import flask_app as api
# from src.core.tool import get_settings_json, update_settings_json
#
#
# @api.route('/api/settings', methods=['GET'])
# # 用于获取settings.json的数据，返回所有参数
# def api_settings():
#     try:
#         # 从请求URL中获取参数
#         settings_json = get_settings_json()
#         return jsonify({
#             "data": {
#                 "settings": settings_json
#             },
#             "message": "获取设置信息成功。",
#             "statusCode": "OK"
#         })
#     except Exception as e:
#         return jsonify({
#             "data": {
#                 "settings": ""
#             },
#             "message": f"获取设置信息失败：{e}。",
#             "statusCode": "GENERAL_ERROR"
#         }), 400
#
#
# @api.route('/api/settings/update', methods=['POST'])
# # 更新所有参数
# def api_settings_update():
#     try:
#         # 从请求URL中获取参数
#         request_body = request.json
#         update_settings_json(request_body)
#         return jsonify({
#             "data": {},
#             "message": "更新设置信息成功。",
#             "statusCode": "OK"
#         })
#     except Exception as e:
#         return jsonify({
#             "data": {},
#             "message": f"更新设置信息失败：{e}。",
#             "statusCode": "GENERAL_ERROR"
#         }), 400
#
#
