# Python API Template - Docker 部署文档

## 快速开始

### 开发环境

```bash
# 启动开发环境
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 生产环境（单机）

```bash
# 设置环境变量
export SECRET_KEY="your-secret-key-here"
export DB_PASSWORD="your-db-password-here"

# 启动
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 架构说明

### 开发环境架构

```
┌─────────────────────────────────────┐
│           Docker Network            │
│  ┌─────────┐  ┌─────────┐          │
│  │   API   │  │  Redis  │          │
│  │ :8000   │  │ :6379   │          │
│  └────┬────┘  └─────────┘          │
│       │                             │
│  ┌────▼────┐                        │
│  │PostgreSQL│                       │
│  │  :5432  │                        │
│  └─────────┘                        │
└─────────────────────────────────────┘
```

### 生产环境架构（负载均衡）

```
┌─────────────────────────────────────────────────────┐
│                  Docker Network                     │
│                                                     │
│  ┌───────────────────────────────────────┐         │
│  │            Nginx (LB)                  │         │
│  │           :80 / :443                   │         │
│  └───────────────┬───────────────────────┘         │
│                  │                                  │
│     ┌────────────┼────────────┐                     │
│     │            │            │                     │
│  ┌──▼──┐     ┌──▼──┐     ┌──▼──┐                  │
│  │API-1│     │API-2│     │API-3│                  │
│  │:8000│     │:8000│     │:8000│                  │
│  └──┬──┘     └──┬──┘     └──┬──┘                  │
│     │           │           │                      │
│     └───────────┼───────────┘                      │
│                 │                                   │
│  ┌──────────────▼──────────────┐  ┌────────────┐  │
│  │      PostgreSQL             │  │   Redis    │  │
│  │         :5432               │  │   :6379    │  │
│  └─────────────────────────────┘  └────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 负载均衡配置

### 默认配置（3 个 API 容器）

```yaml
# docker-compose.prod.yml
services:
  api-1:
    # API 容器 1
  api-2:
    # API 容器 2
  api-3:
    # API 容器 3
```

### 动态扩容

```bash
# 扩展到 5 个容器
./scripts/scale.sh up 5

# 缩减到 2 个容器
./scripts/scale.sh down 2

# 查看状态
./scripts/scale.sh status
```

### 负载均衡算法

Nginx 配置使用 `least_conn` 算法：
- 将新请求分配给当前连接数最少的服务器
- 适合长连接场景（WebSocket、文件上传）

可选算法：
- `round-robin`（默认）：轮询
- `ip_hash`：基于 IP 哈希，同一 IP 分配到同一服务器
- `least_conn`：最少连接数

---

## 部署步骤

### 1. 准备服务器

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 克隆代码

```bash
git clone https://github.com/NATCHAIN-7756/python-api-template.git
cd python-api-template
```

### 3. 配置环境变量

```bash
# 创建 .env 文件
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)
EOF
```

### 4. 配置 SSL 证书

```bash
# 生成自签名证书（测试用）
mkdir -p docker/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/ssl/key.pem \
  -out docker/ssl/cert.pem \
  -subj "/CN=localhost"

# 生产环境建议使用 Let's Encrypt
# certbot certonly --standalone -d your-domain.com
```

### 5. 部署

```bash
# 赋予执行权限
chmod +x scripts/*.sh

# 部署
./scripts/deploy.sh
```

---

## 运维命令

### 查看日志

```bash
# 所有服务日志
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# 单个服务日志
docker logs python-api-1 -f
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.yml -f docker-compose.prod.yml restart

# 重启单个服务
docker restart python-api-1
```

### 数据库备份

```bash
# 备份
docker exec python-api-db-primary pg_dump -U postgres appdb > backup.sql

# 恢复
cat backup.sql | docker exec -i python-api-db-primary psql -U postgres appdb
```

---

## 性能调优

### API 容器数量

建议公式：`容器数 = CPU核心数 * 2`

示例：
- 4 核 CPU：建议 8 个容器
- 8 核 CPU：建议 16 个容器

### 数据库连接池

```python
# app/config.py
DATABASE_POOL_SIZE = 20  # 每个容器的连接数
DATABASE_MAX_OVERFLOW = 10
```

总连接数 = 容器数 × (POOL_SIZE + MAX_OVERFLOW)

### Redis 缓存

启用 Redis 缓存可显著提升性能：
- Session 存储
- 热点数据缓存
- 搜索结果缓存

---

## 监控

### 健康检查

```bash
# API 健康检查
curl http://localhost/health

# 数据库健康检查
docker exec python-api-db-primary pg_isready
```

### Prometheus + Grafana（可选）

```yaml
# 添加监控服务
services:
  prometheus:
    image: prom/prometheus
    # ...

  grafana:
    image: grafana/grafana
    # ...
```

---

## 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker logs python-api-1

# 查看容器状态
docker inspect python-api-1
```

### 数据库连接失败

```bash
# 检查数据库是否运行
docker exec python-api-db-primary pg_isready

# 检查网络连通性
docker exec python-api-1 ping db-primary
```

### 负载不均衡

```bash
# 查看 Nginx 状态
docker exec python-api-nginx nginx -t

# 查看 Nginx 日志
docker logs python-api-nginx
```

---

## SCALE OS v10.0
