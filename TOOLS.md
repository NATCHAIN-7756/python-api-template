# TOOLS.md - Python API Template

## META
- project: python-api-template
- tech: python
- tier: critical
- scale_version: 10.0
- created: 2026-05-21

## TECH_STACK
- Python 3.10+
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL

## COMMANDS
dev: python -m uvicorn app.main:app --reload
build: pip install -e .
test: pytest
lint: ruff check .
typecheck: mypy .

## RED_LINES
- R1: 零数据丢失
- R2: 零静默失败
- R3: 零硬编码密钥
- R4: 零幻觉
- R5: 零甩锅

## Related
- [SCALE-CONSTITUTION.md](~/.openclaw/workspace/SCALE-CONSTITUTION.md)
- [GITHUB-SYNC.md](~/.openclaw/workspace/GITHUB-SYNC.md)
- [WECOM-SYNC.md](~/.openclaw/workspace/WECOM-SYNC.md)
