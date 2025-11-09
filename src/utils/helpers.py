import os
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """加载YAML配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logger.info(f"成功加载配置文件: {config_path}")
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {config_path}, 错误: {str(e)}")
        raise

def load_env_variables(env_file: str = ".env") -> Dict[str, str]:
    """加载环境变量"""
    env_vars = {}
    
    if not os.path.exists(env_file):
        logger.warning(f"环境变量文件不存在: {env_file}")
        return env_vars
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    os.environ[key.strip()] = value.strip()
        
        logger.info(f"成功加载环境变量文件: {env_file}")
        return env_vars
    except Exception as e:
        logger.error(f"加载环境变量文件失败: {env_file}, 错误: {str(e)}")
        return {}

def create_output_directory(output_dir: str) -> Path:
    """创建输出目录"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 创建日期子目录
    date_str = datetime.now().strftime("%Y%m%d")
    date_dir = output_path / date_str
    date_dir.mkdir(exist_ok=True)
    
    logger.info(f"创建输出目录: {date_dir}")
    return date_dir

def save_results(results: Dict[str, Any], output_path: str, format: str = "json") -> None:
    """保存结果到文件"""
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        elif format.lower() == "markdown":
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(results.get('content', str(results)))
        else:
            raise ValueError(f"不支持的格式: {format}")
        
        logger.info(f"结果已保存到: {output_file}")
    except Exception as e:
        logger.error(f"保存结果失败: {output_file}, 错误: {str(e)}")

def format_summary(data_summary: Dict[str, Any], max_length: int = 500) -> str:
    """格式化数据摘要为字符串"""
    try:
        # 提取关键信息
        shape = data_summary.get('shape', '未知')
        columns = data_summary.get('columns', [])
        
        # 限制列显示数量
        if len(columns) > 10:
            columns_str = ', '.join(columns[:10]) + f"... (共{len(columns)}列)"
        else:
            columns_str = ', '.join(columns)
        
        # 构建摘要字符串
        summary = f"数据形状: {shape}\n"
        summary += f"主要字段: {columns_str}\n"
        
        # 如果有数值列的统计信息，添加部分统计量
        if 'numeric_summary' in data_summary:
            numeric_summary = data_summary['numeric_summary']
            if numeric_summary:
                # 选择几个关键指标
                key_metrics = ['mean', 'std', 'min', 'max']
                summary += "\n数值列统计摘要:\n"
                
                for col, stats in list(numeric_summary.items())[:5]:  # 只显示前5列
                    summary += f"- {col}: "
                    metric_strs = []
                    for metric in key_metrics:
                        if metric in stats:
                            metric_strs.append(f"{metric}={stats[metric]:.2f}")
                    summary += ', '.join(metric_strs) + "\n"
        
        # 限制长度
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    except Exception as e:
        logger.error(f"格式化数据摘要失败: {str(e)}")
        return f"数据摘要格式化失败: {str(e)}"

def get_current_date() -> str:
    """获取当前日期字符串"""
    return datetime.now().strftime("%Y年%m月%d日")

def extract_key_insights(results: Dict[str, Any], agent_name: str) -> List[str]:
    """从智能体结果中提取关键洞察"""
    insights = []
    
    try:
        # 尝试从不同字段提取洞察
        if 'key_insights' in results and isinstance(results['key_insights'], list):
            insights.extend(results['key_insights'])
        
        # 如果没有专门的洞察字段，尝试从总结中提取
        summary_fields = ['summary', f'{agent_name.lower()}_summary', 'analysis']
        for field in summary_fields:
            if field in results and isinstance(results[field], str):
                # 简单的句子分割，提取前几句作为洞察
                sentences = results[field].split('。')
                for sentence in sentences[:3]:  # 只取前3句
                    sentence = sentence.strip()
                    if sentence and len(sentence) > 10:  # 过滤太短的句子
                        insights.append(sentence + '。')
                break
        
        # 如果还是没有，尝试从整个结果中提取
        if not insights:
            for key, value in results.items():
                if isinstance(value, str) and len(value) > 50:
                    # 简单的句子分割
                    sentences = value.split('。')
                    for sentence in sentences[:2]:  # 只取前2句
                        sentence = sentence.strip()
                        if sentence and len(sentence) > 10:
                            insights.append(sentence + '。')
                    if len(insights) >= 3:  # 最多3条洞察
                        break
    
    except Exception as e:
        logger.error(f"提取关键洞察失败: {str(e)}")
        insights.append(f"提取洞察时出错: {str(e)}")
    
    return insights[:5]  # 最多返回5条洞察

def validate_data_files(data_files: List[str], data_root: str) -> Dict[str, bool]:
    """验证数据文件是否存在"""
    validation_results = {}
    data_root_path = Path(data_root)
    
    for file_name in data_files:
        file_path = data_root_path / file_name
        validation_results[file_name] = file_path.exists()
        
        if not file_path.exists():
            logger.warning(f"数据文件不存在: {file_path}")
    
    return validation_results

def create_report_summary(agent_results: Dict[str, Dict[str, Any]]) -> str:
    """创建报告摘要"""
    summary = "# 新能源汽车行业分析报告摘要\n\n"
    
    # 添加各智能体的关键洞察
    for agent_name, results in agent_results.items():
        if agent_name == "ReportAgent":
            continue  # 跳过报告智能体
            
        insights = extract_key_insights(results, agent_name)
        
        if insights:
            agent_display_name = {
                "MacroAgent": "宏观经济环境",
                "FinanceAgent": "行业财务表现",
                "MarketAgent": "市场产销趋势",
                "PolicyAgent": "政策与环境影响",
                "ForecastAgent": "预测与展望"
            }.get(agent_name, agent_name)
            
            summary += f"## {agent_display_name}\n\n"
            for insight in insights:
                summary += f"- {insight}\n"
            summary += "\n"
    
    return summary

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """合并两个字典"""
    result = dict1.copy()
    result.update(dict2)
    return result