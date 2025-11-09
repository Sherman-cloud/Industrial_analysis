# 新能源汽车行业分析系统 - 分享指南

本指南介绍如何将新能源汽车行业分析系统分享给他人使用，包括多种分享方式和部署方案。

## 分享方式

### 1. 项目打包分享

使用提供的打包脚本创建完整项目包：

```bash
# 运行打包脚本
python package.py
```

这将创建以下文件：
- `new-energy-analysis-v1.0.zip` - ZIP格式压缩包
- `new-energy-analysis-v1.0.tar.gz` - TAR.GZ格式压缩包
- `install.sh` - Linux/Mac安装脚本
- `install.bat` - Windows安装脚本

### 2. Git仓库分享

将项目推送到Git仓库：

```bash
# 初始化Git仓库
git init
git add .
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/yourusername/new-energy-analysis.git

# 推送到远程仓库
git push -u origin main
```

### 3. Docker镜像分享

构建并分享Docker镜像：

```bash
# 构建镜像
docker build -t yourusername/new-energy-analysis:v1.0 .

# 推送到Docker Hub
docker push yourusername/new-energy-analysis:v1.0
```

## 部署方案

### 方案一：本地部署

#### 步骤1：下载项目

用户可以通过以下方式获取项目：
- 下载ZIP压缩包并解压
- 克隆Git仓库：`git clone https://github.com/yourusername/new-energy-analysis.git`

#### 步骤2：安装依赖

**使用安装脚本（推荐）：**

Linux/Mac:
```bash
chmod +x install.sh
./install.sh
```

Windows:
```cmd
install.bat
```

**手动安装：**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

#### 步骤3：配置环境

```bash
# 复制环境变量模板
cp .env.template .env

# 编辑.env文件，填入API密钥
nano .env
```

#### 步骤4：运行系统

```bash
# 运行完整分析
python main.py

# 运行示例
python run_example.py
```

### 方案二：Docker部署

#### 步骤1：安装Docker

确保系统已安装Docker和Docker Compose。

#### 步骤2：获取项目

下载项目或克隆Git仓库。

#### 步骤3：配置环境

```bash
# 复制环境变量模板
cp .env.template .env

# 编辑.env文件，填入API密钥
nano .env
```

#### 步骤4：部署容器

**使用部署脚本（推荐）：**

Linux/Mac:
```bash
chmod +x deploy-docker.sh
./deploy-docker.sh
```

Windows:
```cmd
deploy-docker.bat
```

**手动部署：**
```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d
```

#### 步骤5：运行分析

```bash
# 运行完整分析
docker-compose exec new-energy-analysis python main.py

# 运行示例
docker-compose exec new-energy-analysis python run_example.py
```

### 方案三：云服务器部署

#### 步骤1：准备云服务器

选择云服务提供商（如AWS、阿里云、腾讯云等），创建云服务器实例。

#### 步骤2：安装环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 步骤3：部署应用

```bash
# 克隆项目
git clone https://github.com/yourusername/new-energy-analysis.git
cd new-energy-analysis

# 配置环境
cp .env.template .env
nano .env

# 部署容器
chmod +x deploy-docker.sh
./deploy-docker.sh
```

#### 步骤4：配置域名和SSL（可选）

使用Nginx作为反向代理，配置域名和SSL证书。

## 用户指南

### 快速开始

1. 下载并解压项目
2. 安装依赖（运行安装脚本或手动安装）
3. 配置环境变量（设置API密钥）
4. 运行示例（`python run_example.py`）

### 获取API密钥

1. 访问[硅基流动](https://siliconflow.cn/)
2. 注册账号并登录
3. 在控制台获取API密钥
4. 将API密钥填入`.env`文件

### 使用自定义数据

1. 将数据文件放入`data`目录
2. 确保数据格式与示例数据一致
3. 运行分析：`python main.py`

### 查看结果

分析结果保存在`output`目录中，包括：
- Markdown格式报告
- 数据分析图表
- 各领域分析结果

## 常见问题

### Q: 如何更换模型？

A: 修改`.env`文件中的`MODEL_NAME`参数。

### Q: 如何添加新的智能体？

A: 参考`src/agents/base_agent.py`中的实现，创建新的智能体类。

### Q: 如何自定义分析报告？

A: 修改`src/agents/report_agent.py`中的报告生成逻辑。

### Q: 如何处理大量数据？

A: 调整`.env`文件中的`MAX_CONCURRENT_REQUESTS`参数，增加并发请求数。

### Q: 如何优化性能？

A: 
1. 使用更快的硬件
2. 调整并发参数
3. 使用缓存功能
4. 优化数据结构

## 技术支持

如遇到问题，请：
1. 查看文档：`docs/INSTALLATION.md`和`docs/DOCKER_DEPLOYMENT.md`
2. 查看日志：`logs/`目录中的日志文件
3. 提交Issue到项目仓库
4. 联系技术支持

## 更新维护

### 更新项目

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重新部署（Docker）
docker-compose down
docker-compose build
docker-compose up -d
```

### 备份数据

```bash
# 备份数据和结果
tar -czf backup-$(date +%Y%m%d).tar.gz data/ output/

# 恢复数据
tar -xzf backup-20231109.tar.gz
```

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献指南

欢迎贡献代码、报告问题或提出建议！详见CONTRIBUTING.md文件。