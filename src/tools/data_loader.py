import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """数据加载器，负责加载和管理各种数据源"""
    
    def __init__(self, data_root_path: str = "../数据"):
        self.data_root_path = Path(data_root_path)
        self.data_cache = {}
        
    def load_data(self, file_name: str, **kwargs) -> pd.DataFrame:
        """加载指定的数据文件"""
        file_path = self.data_root_path / file_name
        
        if file_name in self.data_cache:
            logger.info(f"从缓存中加载数据: {file_name}")
            return self.data_cache[file_name]
        
        if not file_path.exists():
            logger.error(f"数据文件不存在: {file_path}")
            raise FileNotFoundError(f"数据文件不存在: {file_path}")
        
        try:
            if file_name.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8', **kwargs)
            elif file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                df = pd.read_excel(file_path, **kwargs)
            else:
                raise ValueError(f"不支持的文件格式: {file_name}")
            
            # 缓存数据
            self.data_cache[file_name] = df
            logger.info(f"成功加载数据: {file_name}, 形状: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"加载数据失败: {file_name}, 错误: {str(e)}")
            raise
    
    def get_data_info(self, file_name: str) -> Dict[str, Any]:
        """获取数据文件的基本信息"""
        if file_name not in self.data_cache:
            self.load_data(file_name)
        
        df = self.data_cache[file_name]
        return {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
    
    def get_data_summary(self, file_name: str) -> Dict[str, Any]:
        """获取数据文件的摘要统计信息"""
        if file_name not in self.data_cache:
            self.load_data(file_name)
        
        df = self.data_cache[file_name]
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        summary = {
            "numeric_summary": df[numeric_cols].describe().to_dict(),
            "categorical_summary": {}
        }
        
        # 对于分类变量的摘要
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            summary["categorical_summary"][col] = {
                "unique_count": df[col].nunique(),
                "top_values": df[col].value_counts().head(10).to_dict()
            }
        
        return summary


class DataQuery:
    """数据查询工具，提供各种数据查询和分析功能"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
    
    def query_data(self, file_name: str, filters: Optional[Dict] = None, 
                   columns: Optional[List[str]] = None, 
                   limit: Optional[int] = None) -> pd.DataFrame:
        """查询数据"""
        df = self.data_loader.load_data(file_name)
        
        # 应用列过滤
        if columns:
            df = df[columns]
        
        # 应用行过滤
        if filters:
            for col, condition in filters.items():
                if isinstance(condition, dict):
                    if 'eq' in condition:
                        df = df[df[col] == condition['eq']]
                    elif 'ne' in condition:
                        df = df[df[col] != condition['ne']]
                    elif 'gt' in condition:
                        df = df[df[col] > condition['gt']]
                    elif 'lt' in condition:
                        df = df[df[col] < condition['lt']]
                    elif 'gte' in condition:
                        df = df[df[col] >= condition['gte']]
                    elif 'lte' in condition:
                        df = df[df[col] <= condition['lte']]
                    elif 'in' in condition:
                        df = df[df[col].isin(condition['in'])]
                    elif 'contains' in condition:
                        df = df[df[col].str.contains(condition['contains'], na=False)]
                else:
                    df = df[df[col] == condition]
        
        # 应用限制
        if limit:
            df = df.head(limit)
        
        return df
    
    def get_time_series_data(self, file_name: str, time_col: str, 
                            value_cols: List[str], 
                            start_date: Optional[str] = None, 
                            end_date: Optional[str] = None) -> pd.DataFrame:
        """获取时间序列数据"""
        df = self.data_loader.load_data(file_name)
        
        # 确保时间列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
            df[time_col] = pd.to_datetime(df[time_col])
        
        # 应用时间范围过滤
        if start_date:
            df = df[df[time_col] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df[time_col] <= pd.to_datetime(end_date)]
        
        # 按时间排序
        df = df.sort_values(time_col)
        
        return df[[time_col] + value_cols]
    
    def get_correlation_matrix(self, file_name: str, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """计算相关性矩阵"""
        df = self.data_loader.load_data(file_name)
        
        # 只选择数值列
        numeric_df = df.select_dtypes(include=[np.number])
        
        if columns:
            # 确保指定的列都是数值型
            numeric_cols = [col for col in columns if col in numeric_df.columns]
            if not numeric_cols:
                raise ValueError("指定的列中没有数值型列")
            numeric_df = numeric_df[numeric_cols]
        
        # 计算相关性矩阵
        corr_matrix = numeric_df.corr()
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "high_correlations": self._find_high_correlations(corr_matrix)
        }
    
    def _find_high_correlations(self, corr_matrix: pd.DataFrame, threshold: float = 0.7) -> List[Dict]:
        """找出高相关性的变量对"""
        high_corr = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) >= threshold:
                    high_corr.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": corr_val
                    })
        
        return high_corr
    
    def compute_financial_ratios(self, file_name: str, company_col: str, 
                                period_col: str, ratio_definitions: Dict[str, Dict]) -> pd.DataFrame:
        """计算财务比率"""
        df = self.data_loader.load_data(file_name)
        
        results = []
        
        for company, group in df.groupby(company_col):
            for _, row in group.iterrows():
                ratios = {}
                
                for ratio_name, definition in ratio_definitions.items():
                    try:
                        numerator = row[definition['numerator']]
                        denominator = row[definition['denominator']]
                        
                        # 处理除零情况
                        if denominator == 0:
                            ratios[ratio_name] = np.nan
                        else:
                            ratios[ratio_name] = numerator / denominator
                    except KeyError as e:
                        logger.warning(f"缺少计算比率所需的列: {e}")
                        ratios[ratio_name] = np.nan
                
                result_row = {
                    company_col: company,
                    period_col: row[period_col],
                    **ratios
                }
                results.append(result_row)
        
        return pd.DataFrame(results)
    
    def aggregate_by_period(self, file_name: str, group_cols: List[str], 
                           agg_cols: List[str], agg_funcs: List[str]) -> pd.DataFrame:
        """按时期聚合数据"""
        df = self.data_loader.load_data(file_name)
        
        # 定义聚合字典
        agg_dict = {}
        for col in agg_cols:
            agg_dict[col] = agg_funcs
        
        # 执行聚合
        result = df.groupby(group_cols).agg(agg_dict).reset_index()
        
        # 展平多级列名
        if isinstance(result.columns, pd.MultiIndex):
            result.columns = ['_'.join(col).strip() if col[1] else col[0] for col in result.columns.values]
        
        return result