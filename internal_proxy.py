from flask import Flask, request, jsonify, abort, redirect, url_for
import requests
from datetime import datetime

app = Flask(__name__)

# 生产环境HTTPS强制重定向
@app.before_request
def enforce_https():
    # 在生产环境中启用HTTPS强制重定向
    # 检查是否在生产环境（通过FLASK_ENV环境变量或DEBUG模式）
    if not app.debug and not request.is_secure:
        # 检查是否有反向代理设置的X-Forwarded-Proto头
        proto = request.headers.get('X-Forwarded-Proto')
        if proto == 'http':
            # 构建HTTPS URL
            url = request.url.replace('http://', 'https://')
            return redirect(url, code=301)

# 允许所有跨域请求
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24小时
    return response

# 代理API请求
@app.route('/api/huacore.forms/documentapi/getvalue', methods=['POST', 'OPTIONS'])
def proxy_api():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # 内部API服务器地址
        internal_api_url = 'http://10.157.85.11/api/huacore.forms/documentapi/getvalue'
        
        # 获取请求数据
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
            # 根据时间范围调整超时时间
            time_range_hours = (end_datetime - start_datetime) / 3600
            if time_range_hours <= 24:
                timeout = 10
            elif time_range_hours <= 72:
                timeout = 30
            else:
                timeout = 60
                
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
    app.run(host='0.0.0.0', port=5000, debug=False)
