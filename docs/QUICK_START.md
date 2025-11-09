# 快速开始指南

欢迎使用新能源汽车行业分析系统！本指南将帮助您在几分钟内完成系统部署和运行。

## 🚀 一键部署（推荐）

### Docker部署（适用于所有操作系统）

1. **下载项目**
   ```bash
   git clone <repository-url>
   cd agent_analysis_project
   ```

2. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp .env.template .env
   
   # 编辑.env文件，设置您的API密钥
   nano .env  # Linux/Mac
   notepad .env  # Windows
   ```

3. **一键部署**
   ```bash
   # Linux/Mac
   chmod +x deploy-docker.sh
   ./deploy-docker.sh
   
   # Windows
   deploy-docker.bat
   ```

4. **访问系统**
   打开浏览器访问 http://localhost:8501

## 📦 项目包部署

1. **下载项目包**
   - 从分享者处获取 `new-energy-analysis-YYYYMMDD_HHMMSS.zip` 文件
   - 解压到目标目录

2. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp .env.template .env
   
   # 编辑.env文件，设置您的API密钥
   nano .env  # Linux/Mac
   notepad .env  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行系统**
   ```bash
   python main.py
   ```

## 🔧 环境变量配置

编辑 `.env` 文件，设置以下关键变量：

```bash
# 必需：API密钥
SILICONFLOW_API_KEY=your_api_key_here

# 可选：数据目录
DATA_DIR=./data
OUTPUT_DIR=./output

# 可选：日志级别
LOG_LEVEL=INFO
```

### 获取API密钥

1. 访问 [硅基流动官网](https://siliconflow.cn/)
2. 注册账号并登录
3. 进入控制台，创建API密钥
4. 将密钥复制到 `.env` 文件中

## 📊 使用示例数据

项目包含示例数据，位于 `example_data/` 目录：

1. **使用示例数据**
   ```bash
   python main.py --data-dir example_data
   ```

2. **查看示例数据说明**
   参考 `example_data/README.md` 了解数据结构

## 📋 常用命令

```bash
# 运行完整分析
python main.py

# 运行测试
python test_project.py

# 运行示例
python run_example.py

# 查看帮助
python main.py --help

# 打包项目
python share_project.py
```

## 🆘 遇到问题？

1. **API密钥问题**
   - 确保密钥有效且有足够额度
   - 检查 `.env` 文件是否正确配置

2. **依赖安装问题**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 使用国内镜像
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

3. **Docker问题**
   - 确保Docker已安装并运行
   - 检查端口8501是否被占用

4. **数据问题**
   - 确保数据文件路径正确
   - 检查数据文件格式是否正确

## 📖 更多资源

- [详细安装说明](docs/INSTALLATION.md)
- [Docker部署指南](docs/DOCKER_DEPLOYMENT.md)
- [项目分享指南](docs/SHARING_GUIDE.md)
- [示例数据说明](example_data/README.md)

## 🎉 开始使用

现在您可以开始使用新能源汽车行业分析系统了！

1. 访问 http://localhost:8501 查看Web界面
2. 上传您的数据或使用示例数据
3. 选择分析类型并开始分析
4. 查看生成的报告和图表

祝您使用愉快！如有问题，请参考文档或联系技术支持。