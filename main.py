#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新能源汽车行业Agent分析系统主程序
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.coordinator import AnalysisCoordinator
from src.utils import load_config, load_env_variables

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="新能源汽车行业Agent分析系统")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/project.yaml",
        help="配置文件路径"
    )
    parser.add_argument(
        "--env", 
        type=str, 
        default=".env",
        help="环境变量文件路径"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default=None,
        help="输出目录路径"
    )
    parser.add_argument(
        "--focus", 
        type=str, 
        nargs="+",
        choices=["宏观经济", "财务", "市场", "政策", "预测"],
        help="指定重点分析领域"
    )
    parser.add_argument(
        "--data-files", 
        type=str, 
        nargs="+",
        help="指定要加载的数据文件"
    )
    parser.add_argument(
        "--no-charts", 
        action="store_true",
        help="不生成图表"
    )
    
    args = parser.parse_args()
    
    # 初始化协调器
    try:
        coordinator = AnalysisCoordinator(
            config_path=args.config,
            env_file=args.env
        )
        logger.info("分析协调器初始化成功")
    except Exception as e:
        logger.error(f"初始化分析协调器失败: {str(e)}")
        sys.exit(1)
    
    # 加载数据
    try:
        load_results = coordinator.load_data(args.data_files)
        logger.info("数据加载完成")
        
        # 检查数据加载是否成功
        failed_files = [file for file, result in load_results.items() 
                       if result.get("status") == "error"]
        
        if failed_files:
            logger.warning(f"以下数据文件加载失败: {', '.join(failed_files)}")
    except Exception as e:
        logger.error(f"数据加载失败: {str(e)}")
        sys.exit(1)
    
    # 运行分析
    try:
        analysis_results = coordinator.run_analysis(args.focus)
        logger.info("分析完成")
    except Exception as e:
        logger.error(f"分析失败: {str(e)}")
        sys.exit(1)
    
    # 保存结果
    try:
        saved_files = coordinator.save_results(args.output)
        logger.info("结果保存完成")
        
        # 打印保存的文件路径
        print("\n分析结果已保存到以下文件:")
        for file_type, file_path in saved_files.items():
            print(f"- {file_type}: {file_path}")
    except Exception as e:
        logger.error(f"保存结果失败: {str(e)}")
    
    # 生成图表
    if not args.no_charts:
        try:
            chart_files = coordinator.generate_charts(args.output)
            logger.info("图表生成完成")
            
            if chart_files:
                print("\n图表已生成:")
                for chart_type, chart_path in chart_files.items():
                    print(f"- {chart_type}: {chart_path}")
        except Exception as e:
            logger.error(f"生成图表失败: {str(e)}")
    
    # 打印分析摘要
    try:
        summary = coordinator.get_analysis_summary()
        print("\n" + "="*50)
        print("分析摘要")
        print("="*50)
        print(summary)
    except Exception as e:
        logger.error(f"获取分析摘要失败: {str(e)}")
    
    print("\n分析完成!")

if __name__ == "__main__":
    main()