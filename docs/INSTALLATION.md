# 新能源汽车行业分析系统 - 安装与使用指南

## 概述

本系统是一个基于LangChain框架和硅基流动模型的多智能体系统，能够自动完成新能源汽车行业的多维数据分析、趋势判断和报告生成。

## 系统要求

- Python 3.8 或更高版本
- 至少 4GB 可用内存
- 有效的硅基流动API密钥
- 稳定的网络连接

## 安装方法

### 方法一：使用安装脚本（推荐）

#### Linux/macOS

```bash
# 解压下载的包
tar -xzf new_energy_vehicle_analysis.tar.gz
cd new_energy_vehicle_analysis

# 运行安装脚本
chmod +x install.sh
./install.sh
```

#### Windows

```batch
# 解压下载的包
# 使用资源管理器或解压软件解压 new_energy_vehicle_analysis.zip

# 进入项目目录
cd new_energy_vehicle_analysis

# 运行安装脚本
install.bat
```

### 方法二：手动安装

1. **解压项目包**
   ```bash
   tar -xzf new_energy_vehicle_analysis.tar.gz
   cd new_energy_vehicle_analysis
   ```

2. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp .env.template .env
   
   # 编辑 .env 文件，填入您的API密钥
   nano .env  # Linux/macOS
   # 或
   notepad .env  # Windows
   ```

## 配置说明

### 环境变量配置

编辑 `.env` 文件，设置以下变量：

```env
# 硅基流动API密钥（必需）
SILICONFLOW_API_KEY=your_api_key_here

# 数据根目录路径（可选，默认为 ./data）
DATA_ROOT_PATH=./data

# 日志级别（可选，默认为 INFO）
LOG_LEVEL=INFO
```

### 获取API密钥

1. 访问 [硅基流动官网](https://siliconflow.cn/)
2. 注册账号并登录
3. 在控制台中创建API密钥
4. 将密钥填入 `.env` 文件中的 `SILICONFLOW_API_KEY` 字段

## 使用方法

### 快速开始

运行示例脚本，体验系统功能：

```bash
python run_example.py
```

### 完整分析

运行完整的新能源汽车行业分析：

```bash
python main.py
```

### 指定分析领域

只分析特定领域：

```bash
python main.py --focus 市场 财务
```

### 不生成图表

如果不需要生成图表，可以加快分析速度：

```bash
python main.py --no-charts
```

### 运行测试

运行测试套件，验证系统功能：

```bash
python test_project.py
```

## 输出结果

分析结果保存在 `output/` 目录下，按日期组织：

```
output/
└── 20251109/          # 分析日期
    ├── analysis_summary.md    # 分析摘要
    ├── ReportAgent_report.md  # 完整报告
    ├── MacroAgent_results.json
    ├── FinanceAgent_results.json
    ├── MarketAgent_results.json
    ├── PolicyAgent_results.json
    ├── ForecastAgent_results.json
    └── charts/           # 图表目录
        ├── trend_chart.html
        ├── correlation_heatmap.png
        └── ...
```

## 常见问题

### 1. API调用失败

**问题**：出现 "400 Client Error" 或 "401 Unauthorized" 错误

**解决方案**：
- 检查 `.env` 文件中的API密钥是否正确
- 确认API密钥是否有效且未过期
- 检查网络连接是否正常

### 2. 数据加载失败

**问题**：出现 "FileNotFoundError" 错误

**解决方案**：
- 确认数据文件路径是否正确
- 检查 `DATA_ROOT_PATH` 环境变量设置
- 确认数据文件是否存在且可读

### 3. 内存不足

**问题**：分析过程中出现内存不足错误

**解决方案**：
- 关闭其他占用内存的程序
- 使用 `--focus` 参数只分析特定领域
- 使用 `--no-charts` 参数跳过图表生成

### 4. 依赖安装失败

**问题**：pip install 过程中出现错误

**解决方案**：
- 更新pip：`pip install --upgrade pip`
- 使用国内镜像：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`
- 检查Python版本是否符合要求

## 高级用法

### 自定义配置

您可以修改 `config/project.yaml` 文件来自定义系统配置：

```yaml
project:
  name: "新能源汽车行业分析系统"
  version: "1.0.0"
  
  llm_models:
    main_llm:
      model_name: "deepseek-ai/DeepSeek-R1"  # 可更改模型
      temperature: 0.1
      max_tokens: 4000
```

### 添加自定义数据

1. 将数据文件放入 `data/` 目录
2. 在代码中引用新数据文件
3. 修改相关智能体的提示词

### 扩展智能体

您可以创建新的智能体来扩展系统功能：

1. 在 `src/agents/` 目录下创建新文件
2. 继承 `BaseAgent` 类
3. 实现 `run` 方法
4. 在 `coordinator.py` 中注册新智能体

## 技术支持

如果您在使用过程中遇到问题，可以：

1. 查看日志文件：`logs/` 目录
2. 运行测试套件：`python test_project.py`
3. 检查配置文件：`config/` 目录

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。

## 更新日志

### v1.0.0
- 初始版本发布
- 实现六大智能体分析功能
- 支持多种数据格式
- 提供完整可视化功能

---

感谢您使用新能源汽车行业分析系统！