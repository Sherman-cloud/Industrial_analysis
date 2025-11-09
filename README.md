# 新能源汽车行业分析系统

基于LangChain框架和硅基流动模型的多智能体系统，自动完成新能源汽车行业的多维数据分析、趋势判断和报告生成。

## 项目结构

```
agent_analysis_project/
├── config/                 # 配置文件
│   ├── project.yaml       # 项目配置
│   ├── agent.yaml         # 智能体配置
│   └── prompt.yaml        # 提示词配置
├── src/                   # 源代码
│   ├── agents/            # 智能体实现
│   ├── tools/             # 工具实现
│   └── utils/             # 工具函数
├── data/                  # 数据文件
├── output/                # 输出结果
├── logs/                  # 日志文件
├── requirements.txt       # 依赖包
├── .env                   # 环境变量
└── README.md             # 项目说明
```

## 安装与配置

### 方式一：本地安装

1. 克隆项目并进入目录
```bash
cd agent_analysis_project
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.template .env

# 编辑.env文件，设置API密钥
nano .env
```

### 方式二：Docker部署

1. 配置环境变量
```bash
# 复制环境变量模板
cp .env.template .env

# 编辑.env文件，设置API密钥
nano .env
```

2. 使用部署脚本
```bash
# Linux/Mac
chmod +x deploy-docker.sh
./deploy-docker.sh

# Windows
deploy-docker.bat
```

详细部署说明请参考 [Docker部署指南](docs/DOCKER_DEPLOYMENT.md)

### 方式三：一键安装脚本

```bash
# Linux/Mac
chmod +x install.sh
./install.sh

# Windows
install.bat
```

## 使用方法

1. 运行完整分析
```bash
python main.py
```

2. 运行测试套件
```bash
python test_project.py
```

3. 运行示例
```bash
python run_example.py
```

## 智能体说明

- **MacroAgent**: 分析宏观经济数据与行业趋势关系
- **FinanceAgent**: 分析行业财务指标
- **MarketAgent**: 分析市场产销趋势和结构
- **PolicyAgent**: 评估政策环境影响
- **ForecastAgent**: 预测未来发展趋势
- **ReportAgent**: 整合所有分析结果生成报告

## 数据说明

系统使用的数据包括：
- 宏观经济数据（GDP、CPI）
- 新能源汽车行业上市公司财务数据
- 新能源汽车产销数据
- 充电设施数据

详细数据说明请参考 `../数据说明.md`

## 输出结果

分析结果保存在 `output/` 目录下，包括：
- 各智能体分析结果（JSON格式）
- 综合分析报告（Markdown格式）
- 数据可视化图表（PNG/HTML格式）

## 技术架构

- **框架**: LangChain
- **模型**: 硅基流动API (deepseek-ai/DeepSeek-R1)
- **数据处理**: pandas, numpy
- **可视化**: matplotlib, plotly
- **Web界面**: Streamlit

## 注意事项

1. 确保数据文件路径正确
2. API密钥需要有效额度
3. 大规模分析可能需要较长时间
4. 结果仅供参考，不构成投资建议

## 项目分享与部署

本项目支持多种分享和部署方式：

### 分享方式

1. **项目打包分享**
   ```bash
   # 使用打包脚本
   python share_project.py
   ```
   将生成 `new-energy-analysis-package.zip` 文件，包含所有必要文件和说明。

2. **Git仓库分享**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

3. **Docker镜像分享**
   ```bash
   # 构建镜像
   docker build -t new-energy-analysis:latest .
   
   # 推送到Docker Hub
   docker tag new-energy-analysis:latest yourusername/new-energy-analysis:latest
   docker push yourusername/new-energy-analysis:latest
   ```

### 部署选项

1. **本地部署**
   - 适合个人使用和开发测试
   - 详见 [安装说明](docs/INSTALLATION.md)

2. **Docker部署**
   - 适合服务器部署和团队协作
   - 详见 [Docker部署指南](docs/DOCKER_DEPLOYMENT.md)

3. **云服务器部署**
   - 适合生产环境和远程访问
   - 详见 [Docker部署指南](docs/DOCKER_DEPLOYMENT.md#云服务器部署)

### 示例数据

项目包含示例数据，位于 `example_data/` 目录：
- 宏观经济数据示例
- 行业销售数据示例
- 企业财务数据示例
- 政策文件数据示例
- 市场调研数据示例
- 技术指标数据示例

详细说明请参考 [示例数据说明](example_data/README.md)

## 技术支持

如需技术支持或遇到问题，请参考：
- [安装说明](docs/INSTALLATION.md)
- [Docker部署指南](docs/DOCKER_DEPLOYMENT.md)
- [项目分享指南](docs/SHARING_GUIDE.md)

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。