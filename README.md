# CatWarehouse
An open-source software for storing household inventory, suitable for Windows and Android
=======

A lightweight inventory management software for personal and small business use, supporting both Windows and Android platforms.

一个轻量级的库存管理软件，适用于个人和小型商家，支持 Windows 和 Android 双平台。

## Features / 功能特性

- **Inventory Management / 库存管理** - Track stock in, stock out, and current quantities
- **Product Management / 商品管理** - Add, edit, delete, and query products
- **Data Statistics / 数据统计** - Inventory reports and data visualization
- **Multi-user Support / 多用户支持** - Collaborative use with permission management

## Tech Stack / 技术栈

| Component / 组件 | Technology / 技术 |
|------------------|-------------------|
| Backend / 后端 | Python (FastAPI/Flask) |
| Frontend / 前端 | Vue.js |
| Android | WebView |

## Project Structure / 项目结构

```
CatWarehouse/
├── CwServer/       # Backend API server / 后端 API 服务
├── Cw_WebUi/       # Vue.js frontend / Vue.js 前端
└── README.md
```

## Quick Start / 快速开始

### Backend / 后端

```bash
cd CwServer
pip install -r requirements.txt
python main.py
```

### Frontend / 前端

```bash
cd Cw_WebUi
npm install
npm run dev
```

### Android / 安卓端

Build the WebView wrapper and point it to the backend API URL.

构建 WebView 套壳应用，将地址指向后端 API 即可。

## License / 许可证

MIT
