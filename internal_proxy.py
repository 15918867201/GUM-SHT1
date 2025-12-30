from flask import Flask, request, jsonify, abort, redirect, url_for
import requests
from datetime import datetime

app = Flask(__name__)

# 生产环境HTTPS强制重定向 - 已禁用以支持Ngrok内网穿透
# Ngrok会将HTTPS请求转换为HTTP请求转发到本地服务器
# 因此不需要强制重定向到HTTPS
@app.before_request
def enforce_https():
    pass

# 允许所有跨域请求
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, ngrok-skip-browser-warning'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24小时
    return response

# 全局处理OPTIONS请求
@app.route('/api/huacore.forms/documentapi/getvalue', methods=['OPTIONS'])
def handle_options():
    return '', 200

# 代理API请求
@app.route('/api/huacore.forms/documentapi/getvalue', methods=['GET', 'POST'])
def proxy_api():
    
    try:
        # 内部API服务器地址
        internal_api_url = 'http://10.157.85.11/api/huacore.forms/documentapi/getvalue'
        
        # 获取请求数据 - 支持GET和POST
        if request.method == 'GET':
            # 从查询参数获取数据
            start_datetime = request.args.get('start_datetime')
            end_datetime = request.args.get('end_datetime')
            
            # 验证必要参数
            if not start_datetime or not end_datetime:
                return jsonify({'error': 'Missing required parameters: start_datetime and end_datetime'}), 400
                
            # 转换为整数
            try:
                start_datetime = int(start_datetime)
                end_datetime = int(end_datetime)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid parameters: start_datetime and end_datetime must be integers'}), 400
                
            data = {'start_datetime': start_datetime, 'end_datetime': end_datetime}
        else:
            # 从POST请求体获取数据
            data = request.get_json()
            
            # 验证必要参数
            if not data:
                return jsonify({'error': 'Missing request body'}), 400
                
            if 'start_datetime' not in data or 'end_datetime' not in data:
                return jsonify({'error': 'Missing required parameters: start_datetime and end_datetime'}), 400
                
            # 验证参数类型
            try:
                start_datetime = int(data['start_datetime'])
                end_datetime = int(data['end_datetime'])
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid parameters: start_datetime and end_datetime must be integers'}), 400
        
        # 验证时间范围
        if start_datetime > end_datetime:
            return jsonify({'error': 'Invalid time range: start_datetime must be less than or equal to end_datetime'}), 400
            
        # 创建清理后的请求数据（仅保留必要参数）
        cleaned_data = {
            'start_datetime': start_datetime,
            'end_datetime': end_datetime
        }
        
        # 转发请求到内部API服务器，设置超时时间
        try:
            # 根据时间范围动态调整超时时间
            time_range_hours = (end_datetime - start_datetime) / 3600
            if time_range_hours <= 24:
                timeout = 15  # 1小时-24小时：15秒超时
            elif time_range_hours <= 72:
                timeout = 45  # 24小时-3天：45秒超时
            elif time_range_hours <= 168:
                timeout = 90  # 3天-1周：90秒超时
            elif time_range_hours <= 336:
                timeout = 120  # 1周-2周：120秒超时
            else:
                timeout = 180  # 2周以上：3分钟超时
                
            response = requests.post(internal_api_url, json=cleaned_data, timeout=timeout)
            
            # 验证响应格式
            try:
                response_data = response.json()
                # 确保响应是字典格式
                if not isinstance(response_data, dict):
                    response_data = {'data': response_data}
            except ValueError:
                return jsonify({'error': 'Invalid response from internal API'}), 500
                
            return jsonify(response_data), response.status_code
        except requests.Timeout:
            return jsonify({'error': 'Request timed out. Please try a smaller time range.'}), 408
        except requests.RequestException as e:
            return jsonify({'error': 'Failed to connect to internal API'}), 503
            
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # 监听所有网络接口，端口5000
    app.run(host='0.0.0.0', port=8000, debug=False)
