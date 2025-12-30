# GUM-SHT1 - 切片停机监控系统

## 项目概述

GUM-SHT1是一个实时监控切片生产设备运行状态的系统，通过可视化图表展示设备的速度、温度等关键参数，并提供停机时间统计功能。该系统采用混合架构部署，前端页面托管在GitHub Pages，通过内网穿透访问内部API获取实时数据。

## 功能特性

- ✅ **实时数据监控**：通过Chart.js实现数据可视化，展示切片整线速度、挤压出口胶温度、冷辊入口胶温度等关键参数
- ✅ **时间段选择**：支持最近1小时、6小时、12小时、24小时、7天等快速时间范围选择
- ✅ **自定义时间查询**：可手动选择任意时间范围进行数据查询
- ✅ **自动刷新**：支持开启/关闭自动刷新功能，实时更新数据
- ✅ **停机时间统计**：自动统计设备停机时间并展示详细记录
- ✅ **响应式设计**：适配不同屏幕尺寸的设备

## 技术架构

### 前端技术栈
- **HTML5/CSS3/JavaScript**：基础页面结构和交互逻辑
- **Chart.js**：数据可视化图表库

### 后端/代理技术
- **Python Flask**：内网代理服务器，处理API请求转发
- **Ngrok/FRP**：内网穿透工具，将内网代理服务暴露到公网

### 部署架构
```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  GitHub Pages   │──────▶│  Ngrok/FRP      │──────▶│  内网代理服务器  │
│  前端页面       │       │  内网穿透       │       │  (Python Flask) │
└─────────────────┘       └─────────────────┘       └────────┬────────┘
                                                             │
                                                             ▼
                                                   ┌─────────────────┐
                                                   │  内部API服务器  │
                                                   │  (10.157.85.11)  │
                                                   └─────────────────┘
```

## 部署指南

### 1. 前端部署（GitHub Pages）

将代码推送到GitHub仓库的`main`或`master`分支，GitHub Actions会自动将项目部署到GitHub Pages。

### 2. 内网代理服务器部署

#### 2.1 安装依赖
```bash
pip install flask requests
```

#### 2.2 启动代理服务器
```bash
python internal_proxy.py
```

代理服务器将在端口5000上运行，监听所有网络接口。

### 3. 内网穿透配置

#### 3.1 使用Ngrok
```bash
ngrok http 5000
```
获取生成的公网URL（格式：https://xxxx.ngrok-free.dev）

#### 3.2 使用FRP
1. 配置frpc.ini文件：
```ini
[common]
server_addr = frp服务器地址
server_port = 7000

[http_proxy]
type = http
local_ip = 127.0.0.1
local_port = 5000
custom_domains = your-domain.com
```

2. 启动FRP客户端：
```bash
frpc -c frpc.ini
```

### 4. 更新前端配置

在`index.html`文件中更新API请求的公网URL：
```javascript
const url = `https://apolonia-seminomadic-yvone.ngrok-free.dev/api/huacore.forms/documentapi/getvalue?t=${new Date().getTime()}`;
```

## 文件结构

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Pages自动部署工作流
├── internal_proxy.py          # 内网代理服务器
├── index.html                 # 主页面
├── styles.css                 # 页面样式
├── chart.umd.min.js           # Chart.js库
├── README.md                  # 项目说明文档
└── .gitignore                 # Git忽略文件
```

## API说明

### 数据请求接口

- **URL**: `/api/huacore.forms/documentapi/getvalue`
- **方法**: `POST`
- **参数**:
  - `start_datetime`: 开始时间戳（秒）
  - `end_datetime`: 结束时间戳（秒）

- **响应示例**:
  ```json
  [
    {
      "CEMGT": 37.984665,
      "EGRMT": 45.71759,
      "MATXT": "DMPE",
      "SXSRS": 210.362747,
      "UAUTC": "2024-12-30T13:20:00.0000000"
    },
    // ... 更多数据
  ]
  ```

## 使用指南

1. 访问GitHub Pages部署的前端页面
2. 使用快速选择按钮或自定义时间范围选择要查看的数据时间段
3. 点击"查询"按钮或等待自动刷新获取最新数据
4. 查看图表中的实时数据趋势
5. 在页面下方的"停机时间统计"表格中查看详细的停机记录

## 配置说明

### 代理服务器配置（internal_proxy.py）
- `internal_api_url`: 内部API服务器地址
- `port`: 代理服务器监听端口（默认：5000）

### 前端配置（index.html）
- `api_url`: API请求的公网URL（需根据内网穿透配置更新）
- `auto_refresh_interval`: 自动刷新间隔（默认：45秒）

## 常见问题

### Q: 页面显示无数据？
A: 检查以下几点：
   1. 内网代理服务器是否正常运行
   2. 内网穿透工具是否配置正确且运行中
   3. 前端页面中的API URL是否与内网穿透生成的URL一致

### Q: 图表不显示？
A: 检查浏览器控制台是否有JavaScript错误，确认Chart.js库是否正确加载。

### Q: 自动刷新不工作？
A: 确认页面中的"自动刷新"开关已开启。

## 许可证

MIT License

