import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from src.agents import MacroAgent, FinanceAgent, MarketAgent, PolicyAgent, ForecastAgent, ReportAgent
from src.tools import MappedDataLoader, DataQuery, DataAnalyzer, ChartGenerator
from src.utils import (
    load_config, 
    load_env_variables, 
    create_output_directory, 
    save_results,
    format_summary,
    get_current_date,
    extract_key_insights,
    create_report_summary
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisCoordinator:
    """分析协调器，负责协调各个智能体完成分析任务"""
    
    def __init__(self, config_path: str = "config/project.yaml", env_file: str = ".env"):
        """
        初始化协调器
        
        Args:
            config_path: 配置文件路径
            env_file: 环境变量文件路径
        """
        # 获取项目根目录
        project_root = Path(__file__).parent.parent
        
        # 解析配置文件路径
        config_path = project_root / config_path if not os.path.isabs(config_path) else Path(config_path)
        env_file = project_root / env_file if not os.path.isabs(env_file) else Path(env_file)
        
        # 加载配置
        self.config = load_config(str(config_path))
        self.env_vars = load_env_variables(str(env_file))
        
        # 初始化数据工具
        self.data_loader = MappedDataLoader(
            data_root_path=self.env_vars.get("DATA_ROOT_PATH", "../数据"),
            mapping_config_path=self.env_vars.get("DATA_MAPPING_CONFIG", "config/data_mapping.yaml")
        )
        self.data_query = DataQuery(self.data_loader)
        self.data_analyzer = DataAnalyzer(self.data_loader)
        self.chart_generator = ChartGenerator(output_dir="output")
        
        # 初始化智能体
        model_name = self.config["project"]["llm_models"]["main_llm"]["model_name"]
        
        # 创建LLM实例
        from src.agents import SiliconFlowChat
        llm = SiliconFlowChat(
            api_key=self.env_vars.get("SILICONFLOW_API_KEY"),
            model_name=model_name
        )
        
        self.agents = {
            "MacroAgent": MacroAgent(
                model_name=model_name,
                api_key=self.env_vars.get("SILICONFLOW_API_KEY"),
                data_query=self.data_query,
                data_analyzer=self.data_analyzer
            ),
            "FinanceAgent": FinanceAgent(
                model_name=model_name,
                api_key=self.env_vars.get("SILICONFLOW_API_KEY"),
                data_query=self.data_query,
                data_analyzer=self.data_analyzer
            ),
            "MarketAgent": MarketAgent(
                model_name=model_name,
                api_key=self.env_vars.get("SILICONFLOW_API_KEY"),
                data_query=self.data_query,
                data_analyzer=self.data_analyzer
            ),
            "PolicyAgent": PolicyAgent(
                model_name=model_name,
                api_key=self.env_vars.get("SILICONFLOW_API_KEY"),
                data_query=self.data_query,
                data_analyzer=self.data_analyzer
            ),
            "ForecastAgent": ForecastAgent(
                llm=llm,
                tools=["data_query", "data_analyzer"]
            ),
            "ReportAgent": ReportAgent(
                llm=llm,
                tools=["data_query", "data_analyzer"]
            )
        }
        
        # 存储分析结果
        self.analysis_results = {}
        
        logger.info("分析协调器初始化完成")
    
    def load_data(self, data_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        加载数据
        
        Args:
            data_files: 要加载的数据文件列表，如果为None则加载所有数据
            
        Returns:
            数据加载结果
        """
        logger.info("开始加载数据...")
        
        if data_files is None:
            # 默认加载所有数据
            data_files = [
                "宏观经济数据.csv",
                "汽车行业上市公司数据.csv",
                "新能源汽车产销数据.csv",
                "充电基础设施数据.csv",
                "电池技术数据.csv",
                "政策法规数据.csv"
            ]
        
        load_results = {}
        
        for file_name in data_files:
            try:
                data = self.data_loader.load_data(file_name)
                load_results[file_name] = {
                    "status": "success",
                    "shape": data.shape,
                    "columns": data.columns.tolist()
                }
                logger.info(f"成功加载数据: {file_name} -> {self.data_loader._resolve_file_name(file_name)}, 形状: {data.shape}")
            except Exception as e:
                load_results[file_name] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"加载数据失败: {file_name}, 错误: {str(e)}")
        
        return load_results
    
    def run_analysis(self, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        运行分析
        
        Args:
            focus_areas: 重点分析领域，如果为None则分析所有领域
            
        Returns:
            分析结果
        """
        logger.info("开始运行分析...")
        
        # 确定要运行的智能体
        agents_to_run = []
        
        if focus_areas is None:
            # 默认运行所有智能体，除了报告智能体
            agents_to_run = [
                "MacroAgent", "FinanceAgent", "MarketAgent", 
                "PolicyAgent", "ForecastAgent"
            ]
        else:
            # 根据重点领域选择智能体
            area_to_agent = {
                "宏观经济": "MacroAgent",
                "财务": "FinanceAgent",
                "市场": "MarketAgent",
                "政策": "PolicyAgent",
                "预测": "ForecastAgent"
            }
            
            for area in focus_areas:
                if area in area_to_agent:
                    agents_to_run.append(area_to_agent[area])
        
        # 运行选定的智能体
        for agent_name in agents_to_run:
            if agent_name in self.agents:
                logger.info(f"运行智能体: {agent_name}")
                try:
                    # 特殊处理ForecastAgent，需要提供inputs参数
                    if agent_name == "ForecastAgent":
                        inputs = {
                            "industry_data": {"summary": "行业财务数据摘要"},
                            "production_data": {"summary": "产销数据摘要"}
                        }
                        result = self.agents[agent_name].run(inputs)
                    else:
                        result = self.agents[agent_name].run()
                    self.analysis_results[agent_name] = result
                    logger.info(f"智能体 {agent_name} 运行完成")
                except Exception as e:
                    logger.error(f"智能体 {agent_name} 运行失败: {str(e)}")
                    self.analysis_results[agent_name] = {
                        "status": "error",
                        "error": str(e)
                    }
        
        # 生成报告
        logger.info("生成综合报告...")
        try:
            report_result = self.agents["ReportAgent"].run(inputs=self.analysis_results)
            self.analysis_results["ReportAgent"] = report_result
            logger.info("报告生成完成")
        except Exception as e:
            logger.error(f"报告生成失败: {str(e)}")
            self.analysis_results["ReportAgent"] = {
                "status": "error",
                "error": str(e)
            }
        
        return self.analysis_results
    
    def save_results(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        保存分析结果
        
        Args:
            output_dir: 输出目录，如果为None则使用配置中的默认目录
            
        Returns:
            保存的文件路径
        """
        if output_dir is None:
            output_dir = self.env_vars.get("OUTPUT_PATH", "output")
        
        # 创建输出目录
        output_path = create_output_directory(output_dir)
        
        # 保存各智能体的分析结果
        saved_files = {}
        
        for agent_name, result in self.analysis_results.items():
            # 保存JSON格式的结果
            json_file = output_path / f"{agent_name}_results.json"
            save_results(result, str(json_file), "json")
            saved_files[f"{agent_name}_json"] = str(json_file)
            
            # 如果有报告内容，保存为Markdown
            if agent_name == "ReportAgent" and "report_content" in result:
                md_file = output_path / f"{agent_name}_report.md"
                save_results(result, str(md_file), "markdown")
                saved_files[f"{agent_name}_md"] = str(md_file)
        
        # 保存综合摘要
        summary = create_report_summary(self.analysis_results)
        summary_file = output_path / "analysis_summary.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        saved_files["summary"] = str(summary_file)
        
        logger.info(f"分析结果已保存到: {output_path}")
        return saved_files
    
    def generate_charts(self, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        生成图表
        
        Args:
            output_dir: 输出目录，如果为None则使用配置中的默认目录
            
        Returns:
            生成的图表文件路径
        """
        if output_dir is None:
            output_dir = self.env_vars.get("OUTPUT_PATH", "output")
        
        # 创建输出目录
        output_path = create_output_directory(output_dir)
        charts_dir = output_path / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        # 生成图表
        chart_files = {}
        
        try:
            # 生成趋势图
            trend_chart = charts_dir / "market_trends.png"
            self.chart_generator.generate_trend_chart(
                file_name="2新能源汽车分厂商产销(207家厂商，201812-202210月度数据).csv",
                time_col="数据日期",
                value_cols=["产量", "销量"],
                title="新能源汽车产销趋势",
                save_path=str(trend_chart)
            )
            chart_files["trend"] = str(trend_chart)
            
            # 生成相关性热力图
            corr_chart = charts_dir / "correlation_heatmap.png"
            self.chart_generator.generate_correlation_heatmap(
                file_name="24汽车A股上市公司财务摘要（269家，10个指标，2006-2022）.csv",
                title="汽车行业上市公司财务指标相关性",
                save_path=str(corr_chart)
            )
            chart_files["correlation"] = str(corr_chart)
            
            # 生成分布图
            dist_chart = charts_dir / "distribution.png"
            self.chart_generator.generate_distribution_chart(
                file_name="2新能源汽车分厂商产销(207家厂商，201812-202210月度数据).csv",
                column="销量",
                title="新能源汽车销量分布",
                save_path=str(dist_chart)
            )
            chart_files["distribution"] = str(dist_chart)
            
            logger.info(f"图表已生成并保存到: {charts_dir}")
            
        except Exception as e:
            logger.error(f"生成图表失败: {str(e)}")
        
        return chart_files
    
    def get_analysis_summary(self) -> str:
        """
        获取分析摘要
        
        Returns:
            分析摘要字符串
        """
        if not self.analysis_results:
            return "尚未运行分析"
        
        summary = f"## 分析摘要 - {get_current_date()}\n\n"
        
        # 添加各智能体的关键洞察
        for agent_name, result in self.analysis_results.items():
            if agent_name == "ReportAgent":
                continue
                
            insights = extract_key_insights(result, agent_name)
            
            if insights:
                agent_display_name = {
                    "MacroAgent": "宏观经济环境",
                    "FinanceAgent": "行业财务表现",
                    "MarketAgent": "市场产销趋势",
                    "PolicyAgent": "政策与环境影响",
                    "ForecastAgent": "预测与展望"
                }.get(agent_name, agent_name)
                
                summary += f"### {agent_display_name}\n\n"
                for insight in insights:
                    summary += f"- {insight}\n"
                summary += "\n"
        
        # 添加报告摘要（如果有）
        if "ReportAgent" in self.analysis_results and "summary" in self.analysis_results["ReportAgent"]:
            summary += "### 综合分析\n\n"
            summary += self.analysis_results["ReportAgent"]["summary"]
        
        return summary