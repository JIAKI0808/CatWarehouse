# CwServer FastAPI 后端架构搭建计划

## 技术栈
- Python 3.12 (conda: H:\Anaconda\envs\backEnd)
- FastAPI + Uvicorn
- SQLAlchemy + SQLite
- Pydantic 配置管理

## Phase 1: 安装依赖
- 在 backEnd 环境中安装 sqlalchemy、aiosqlite
- 创建 requirements.txt 记录依赖
- **验证**: 依赖安装成功，requirements.txt 存在

## Phase 2: 创建项目结构与配置
- 创建目录结构：app/api、app/core、app/models、app/schemas
- 创建 app/core/config.py（Pydantic Settings 配置管理）
- 创建 app/core/database.py（SQLAlchemy 引擎与会话）
- 创建 app/core/logging.py（日志配置）
- **验证**: 配置模块可正常导入

## Phase 3: 创建 FastAPI 应用入口
- 创建 app/main.py（FastAPI 实例、CORS 中间件、路由注册）
- 创建 app/api/router.py（示例接口）
- 创建 app/models/item.py（示例模型）
- 创建 app/schemas/item.py（示例 Pydantic schema）
- **验证**: `uvicorn app.main:app` 启动成功，/docs 可访问

## Phase 4: 完善与验证
- 创建 .env.example 示例配置文件
- 运行 uvicorn 验证服务启动
- 访问 /docs 验证 API 文档
- **验证**: 服务正常运行，示例接口返回正确数据
