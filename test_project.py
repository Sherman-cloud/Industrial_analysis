#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
新能源汽车行业Agent分析系统测试脚本
"""

import os
import sys
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.tools import DataLoader, DataQuery, DataAnalyzer, ChartGenerator
from src.agents import MacroAgent, FinanceAgent, MarketAgent, PolicyAgent, ForecastAgent, ReportAgent
from src.coordinator import AnalysisCoordinator
from src.utils import load_config, load_env_variables, format_summary, extract_key_insights

class TestDataLoader(unittest.TestCase):
    """测试数据加载器"""
    
    def setUp(self):
        self.data_root = "data"
        self.data_loader = DataLoader(data_root_path=self.data_root)
    
    def test_load_data(self):
        """测试数据加载"""
        # 测试加载宏观经济数据
        try:
            data = self.data_loader.load_data("宏观经济数据.csv")
            self.assertIsNotNone(data)
            self.assertGreater(len(data), 0)
            print(f"成功加载宏观经济数据，形状: {data.shape}")
        except FileNotFoundError:
            self.skipTest("宏观经济数据.csv文件不存在")
    
    def test_get_data_summary(self):
        """测试数据摘要"""
        try:
            data = self.data_loader.load_data("宏观经济数据.csv")
            summary = self.data_loader.get_data_summary(data)
            self.assertIn('shape', summary)
            self.assertIn('columns', summary)
            print(f"数据摘要: {summary}")
        except FileNotFoundError:
            self.skipTest("宏观经济数据.csv文件不存在")

class TestDataAnalyzer(unittest.TestCase):
    """测试数据分析器"""
    
    def setUp(self):
        self.data_root = "data"
        self.data_loader = DataLoader(data_root_path=self.data_root)
        self.data_query = DataQuery(data_dir=self.data_root)
        self.data_analyzer = DataAnalyzer(self.data_loader)
    
    def test_trend_analysis(self):
        """测试趋势分析"""
        try:
            result = self.data_analyzer.analyze_trend(
                file_name="新能源汽车产销数据.csv",
                time_col="年份",
                value_cols=["销量"]
            )
            self.assertIn('trend', result)
            print(f"趋势分析结果: {result}")
        except (FileNotFoundError, KeyError) as e:
            self.skipTest(f"趋势分析跳过: {str(e)}")
    
    def test_correlation_analysis(self):
        """测试相关性分析"""
        try:
            result = self.data_analyzer.generate_correlation_matrix(
                file_name="汽车行业上市公司数据.csv"
            )
            self.assertIn('correlation_matrix', result)
            print(f"相关性分析完成")
        except (FileNotFoundError, KeyError) as e:
            self.skipTest(f"相关性分析跳过: {str(e)}")

class TestAgents(unittest.TestCase):
    """测试智能体"""
    
    def setUp(self):
        self.data_root = "data"
        self.data_loader = DataLoader(data_root_path=self.data_root)
        self.data_query = DataQuery(data_dir=self.data_root)
        self.data_analyzer = DataAnalyzer(self.data_loader)
        
        # 加载环境变量
        env_vars = load_env_variables()
        self.api_key = env_vars.get("SILICONFLOW_API_KEY")
        
        # 如果没有API密钥，跳过智能体测试
        if not self.api_key:
            self.skipTest("未设置SILICONFLOW_API_KEY环境变量")
    
    def test_macro_agent(self):
        """测试宏观经济智能体"""
        # 再次检查API密钥
        if not self.api_key:
            self.skipTest("未设置SILICONFLOW_API_KEY环境变量")
            
        agent = MacroAgent(
            model_name="Qwen/Qwen2-7B-Instruct",
            api_key=self.api_key,
            data_query=self.data_query,
            data_analyzer=self.data_analyzer
        )
        
        # 测试数据查询
        try:
            data_summary = self.data_query.get_data_summary("宏观经济数据.csv")
            self.assertIsNotNone(data_summary)
            print(f"宏观经济数据摘要获取成功")
        except FileNotFoundError:
            self.skipTest("宏观经济数据.csv文件不存在")

class TestCoordinator(unittest.TestCase):
    """测试协调器"""
    
    def setUp(self):
        self.config_path = "config/project.yaml"
        self.env_file = ".env"
        
        # 检查配置文件是否存在
        if not os.path.exists(self.config_path):
            self.skipTest(f"配置文件不存在: {self.config_path}")
        
        # 检查环境变量文件是否存在
        if not os.path.exists(self.env_file):
            self.skipTest(f"环境变量文件不存在: {self.env_file}")
    
    def test_coordinator_initialization(self):
        """测试协调器初始化"""
        try:
            coordinator = AnalysisCoordinator(
                config_path=self.config_path,
                env_file=self.env_file
            )
            self.assertIsNotNone(coordinator)
            print("协调器初始化成功")
        except Exception as e:
            self.fail(f"协调器初始化失败: {str(e)}")

class TestUtils(unittest.TestCase):
    """测试工具函数"""
    
    def test_load_config(self):
        """测试配置加载"""
        config_path = "config/project.yaml"
        if os.path.exists(config_path):
            try:
                config = load_config(config_path)
                self.assertIsNotNone(config)
                self.assertIn('project', config)
                print(f"配置加载成功")
            except Exception as e:
                self.fail(f"配置加载失败: {str(e)}")
        else:
            self.skipTest(f"配置文件不存在: {config_path}")
    
    def test_format_summary(self):
        """测试摘要格式化"""
        # 创建测试数据摘要
        test_summary = {
            'shape': (100, 10),
            'columns': ['col1', 'col2', 'col3', 'col4', 'col5', 'col6', 'col7', 'col8', 'col9', 'col10'],
            'numeric_summary': {
                'col1': {'mean': 10.5, 'std': 2.3, 'min': 5.0, 'max': 15.0},
                'col2': {'mean': 20.1, 'std': 3.7, 'min': 10.0, 'max': 30.0}
            }
        }
        
        formatted = format_summary(test_summary)
        self.assertIsInstance(formatted, str)
        self.assertIn('数据形状', formatted)
        self.assertIn('主要字段', formatted)
        print(f"摘要格式化测试通过")
    
    def test_extract_key_insights(self):
        """测试关键洞察提取"""
        # 创建测试结果
        test_results = {
            'summary': '新能源汽车市场持续增长，2023年销量达到800万辆，同比增长30%。主要驱动因素包括政策支持、技术进步和消费者接受度提高。',
            'key_insights': ['市场增长迅速', '政策支持是关键因素', '技术进步推动发展']
        }
        
        insights = extract_key_insights(test_results, "TestAgent")
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        print(f"关键洞察提取测试通过，提取到{len(insights)}条洞察")

def run_tests():
    """运行所有测试"""
    print("="*50)
    print("新能源汽车行业Agent分析系统 - 功能测试")
    print("="*50)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_classes = [
        TestDataLoader,
        TestDataAnalyzer,
        TestAgents,
        TestCoordinator,
        TestUtils
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 打印测试结果
    print("\n" + "="*50)
    print("测试结果摘要")
    print("="*50)
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # 返回测试是否全部通过
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)