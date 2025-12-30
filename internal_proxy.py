from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 允许所有跨域请求
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
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
        
        # 转发请求到内部API服务器
        response = requests.post(internal_api_url, json=data)
        
        # 返回响应
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 监听所有网络接口，端口5000
    app.run(host='0.0.0.0', port=5000, debug=False)
