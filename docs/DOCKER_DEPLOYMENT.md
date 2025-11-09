# Docker部署指南

本指南介绍如何使用Docker容器化部署新能源汽车行业分析系统，简化安装和运行过程。

## 为什么使用Docker？

Docker容器化部署有以下优势：
- **环境一致性**：确保在不同环境中运行结果一致
- **依赖隔离**：避免与系统Python环境冲突
- **快速部署**：一键启动，无需手动安装依赖
- **易于扩展**：可以轻松部署到云服务器

## 前置要求

1. 安装Docker Desktop（Windows/Mac）或Docker Engine（Linux）
   - Windows/Mac: [Docker Desktop下载](https://www.docker.com/products/docker-desktop)
   - Linux: [Docker Engine安装指南](https://docs.docker.com/engine/install/)

2. 确保Docker服务正在运行

## 快速部署

### 1. 准备环境变量文件

```bash
# 复制环境变量模板
cp .env.template .env

# 编辑.env文件，填入您的API密钥
nano .env
```

### 2. 一键部署

**Linux/Mac:**
```bash
chmod +x deploy-docker.sh
./deploy-docker.sh
```

**Windows:**
```cmd
deploy-docker.bat
```

### 3. 运行分析

```bash
# 运行完整分析
docker-compose exec new-energy-analysis python main.py

# 运行示例
docker-compose exec new-energy-analysis python run_example.py
```

## 详细部署步骤

### 1. 构建镜像

```bash
docker-compose build
```

### 2. 启动容器

```bash
docker-compose up -d
```

### 3. 查看容器状态

```bash
docker-compose ps
```

### 4. 查看日志

```bash
docker-compose logs -f new-energy-analysis
```

### 5. 停止容器

```bash
docker-compose down
```

## 常用命令

| 命令 | 描述 |
|------|------|
| `./deploy-docker.sh` | 一键部署 |
| `./deploy-docker.sh stop` | 停止容器 |
| `./deploy-docker.sh restart` | 重启容器 |
| `./deploy-docker.sh logs` | 查看日志 |
| `./deploy-docker.sh status` | 查看状态 |
| `./deploy-docker.sh help` | 显示帮助 |

## 数据持久化

以下目录已挂载到宿主机，确保数据持久化：
- `./data` - 数据文件
- `./output` - 分析结果
- `./logs` - 日志文件
- `./.env` - 环境变量配置

## 自定义配置

### 修改资源限制

在`docker-compose.yml`中添加资源限制：

```yaml
services:
  new-energy-analysis:
    build: .
    # ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### 添加数据库服务

取消注释`docker-compose.yml`中的PostgreSQL配置：

```yaml
services:
  # ...
  postgres:
    image: postgres:13
    container_name: new-energy-db
    environment:
      POSTGRES_DB: new_energy_analysis
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
```

## 故障排除

### 容器启动失败

1. 检查Docker是否正在运行
2. 检查端口是否被占用
3. 查看容器日志：
   ```bash
   docker-compose logs new-energy-analysis
   ```

### 内存不足错误

1. 增加Docker Desktop内存限制
2. 在`docker-compose.yml`中添加内存限制

### 网络连接问题

1. 检查防火墙设置
2. 确保容器可以访问互联网（API调用需要）

## 高级用法

### 自定义镜像标签

```bash
docker build -t new-energy-analysis:custom .
```

### 多阶段构建优化

对于生产环境，可以使用多阶段构建减小镜像大小：

```dockerfile
# 构建阶段
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
# ...
```

## 生产部署建议

1. **使用环境变量管理配置**，避免硬编码
2. **设置资源限制**，防止资源耗尽
3. **配置日志轮转**，避免日志文件过大
4. **定期备份数据**，确保数据安全
5. **监控容器状态**，及时发现异常

## 云服务器部署

### AWS ECS

1. 创建ECS集群
2. 定义任务定义
3. 创建服务

### Google Cloud Run

1. 构建镜像并推送到Container Registry
2. 部署到Cloud Run

### Azure Container Instances

1. 推送镜像到Container Registry
2. 创建容器组

## 安全考虑

1. **不要在镜像中包含敏感信息**
2. **使用最小权限原则运行容器**
3. **定期更新基础镜像**
4. **扫描镜像漏洞**

## 支持

如果遇到问题，请：
1. 查看日志文件
2. 检查配置文件
3. 提交Issue到项目仓库