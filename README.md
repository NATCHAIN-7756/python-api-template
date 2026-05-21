# Python API Template

> SCALE OS v10.0 · FastAPI 模板项目

---

## 快速开始

```bash
# 安装依赖
pip install -e .

# 开发
python -m uvicorn app.main:app --reload

# 测试
pytest

# Lint
ruff check .
```

---

## 项目结构

```
app/
├── __init__.py
├── main.py           # FastAPI 入口
├── config.py         # 配置管理
├── database.py       # 数据库连接
├── models/           # SQLAlchemy 模型
├── schemas/          # Pydantic 模型
├── routers/          # API 路由
└── services/         # 业务逻辑
tests/
├── conftest.py
└── test_*.py
docs/
├── api/              # API 文档
├── architecture/     # 架构设计
└── guides/           # 开发指南
```

---

## 内置功能

- ✅ 配置管理 (Pydantic Settings)
- ✅ 数据库连接 (SQLAlchemy)
- ✅ 结构化日志
- ✅ 统一异常处理
- ✅ JWT 认证
- ✅ 健康检查
- ✅ OpenAPI 文档
- ✅ Docker 支持

---

## SCALE OS 集成

- [TOOLS.md](TOOLS.md) - 项目配置
- [scale-workflow.json](scale-workflow.json) - 工作流状态
- [GITHUB-SYNC.md](GITHUB-SYNC.md) - GitHub 同步
- [WECOM-SYNC.md](WECOM-SYNC.md) - 企业微信同步

---

## 相关链接

- [SCALE-CONSTITUTION.md](~/.openclaw/workspace/SCALE-CONSTITUTION.md) - SCALE OS 宪法
- [GitHub](https://github.com/NATCHAIN-7756/python-api-template)

---

<!-- SCALE OS v10.0 · Python API Template -->
