import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
from pathlib import Path
import json

# 配置日志
logger = logging.getLogger(__name__)

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class DataAnalyzer:
    """数据分析工具，提供各种数据分析功能"""
    
    def __init__(self, data_query):
        self.data_query = data_query
    
    def analyze_trend(self, file_name: str, time_col: str, value_cols: List[str], 
                    method: str = 'linear') -> Dict[str, Any]:
        """分析数据趋势"""
        data_result = self.data_query.get_data_summary(file_name)
        
        if data_result["status"] == "error":
            return {"error": data_result["error"]}
        
        df = data_result["data"]
        
        # 确保时间列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
            # 尝试多种日期格式
            try:
                df[time_col] = pd.to_datetime(df[time_col], format='%Y/%m/%d')
            except:
                try:
                    df[time_col] = pd.to_datetime(df[time_col], format='%Y-%m-%d')
                except:
                    try:
                        df[time_col] = pd.to_datetime(df[time_col], format='ISO8601')
                    except:
                        df[time_col] = pd.to_datetime(df[time_col], format='mixed')
        
        # 按时间排序
        df = df.sort_values(time_col)
        
        results = {}
        
        for col in value_cols:
            if col not in df.columns:
                logger.warning(f"列不存在: {col}")
                continue
                
            # 移除缺失值
            valid_data = df[[time_col, col]].dropna()
            
            if len(valid_data) < 2:
                results[col] = {"error": "有效数据点不足"}
                continue
            
            # 计算趋势
            x = np.arange(len(valid_data))
            y = valid_data[col].values
            
            if method == 'linear':
                # 线性趋势
                coeffs = np.polyfit(x, y, 1)
                trend = np.polyval(coeffs, x)
                slope = coeffs[0]
                
                # 计算R²
                y_mean = np.mean(y)
                ss_tot = np.sum((y - y_mean) ** 2)
                ss_res = np.sum((y - trend) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                results[col] = {
                    "trend_type": "linear",
                    "slope": slope,
                    "intercept": coeffs[1],
                    "r_squared": r_squared,
                    "direction": "上升" if slope > 0 else "下降" if slope < 0 else "平稳",
                    "trend_strength": "强" if abs(r_squared) > 0.7 else "中" if abs(r_squared) > 0.3 else "弱"
                }
            
            elif method == 'moving_average':
                # 移动平均趋势
                window = min(12, len(valid_data) // 3)  # 自适应窗口大小
                moving_avg = valid_data[col].rolling(window=window).mean()
                
                # 计算趋势方向（基于移动平均的斜率）
                ma_slope = np.polyfit(np.arange(len(moving_avg.dropna())), 
                                     moving_avg.dropna().values, 1)[0]
                
                results[col] = {
                    "trend_type": "moving_average",
                    "window_size": window,
                    "slope": ma_slope,
                    "direction": "上升" if ma_slope > 0 else "下降" if ma_slope < 0 else "平稳"
                }
        
        return results
    
    def analyze_seasonality(self, file_name: str, time_col: str, value_col: str, 
                           period: str = 'year') -> Dict[str, Any]:
        """分析季节性"""
        data_result = self.data_query.get_data_summary(file_name)
        
        if data_result["status"] == "error":
            return {"error": data_result["error"]}
        
        df = data_result["data"]
        
        # 确保时间列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
            try:
                # 尝试多种日期格式
                df[time_col] = pd.to_datetime(df[time_col], format='%Y/%m/%d')
            except:
                try:
                    df[time_col] = pd.to_datetime(df[time_col], format='%Y-%m-%d')
                except:
                    try:
                        df[time_col] = pd.to_datetime(df[time_col])
                    except Exception as e:
                        logger.error(f"无法解析日期格式: {e}")
                        raise ValueError(f"无法解析日期列 {time_col} 的格式")
        
        # 提取时间特征
        if period == 'year':
            df['period'] = df[time_col].dt.year
        elif period == 'quarter':
            df['period'] = df[time_col].dt.quarter
        elif period == 'month':
            df['period'] = df[time_col].dt.month
        else:
            raise ValueError(f"不支持的时间周期: {period}")
        
        # 按周期分组计算统计量
        grouped = df.groupby('period')[value_col].agg(['mean', 'std', 'min', 'max'])
        
        # 计算季节性强度（基于变异系数）
        cv = grouped['std'] / grouped['mean']
        seasonality_strength = cv.std() / cv.mean() if cv.mean() != 0 else 0
        
        return {
            "period_type": period,
            "period_stats": grouped.to_dict(),
            "seasonality_strength": seasonality_strength,
            "seasonality_level": "强" if seasonality_strength > 0.5 else "中" if seasonality_strength > 0.2 else "弱"
        }
    
    def compare_periods(self, file_name: str, time_col: str, value_col: str, 
                       period1: Tuple[str, str], period2: Tuple[str, str]) -> Dict[str, Any]:
        """比较两个时期的数据"""
        data_result = self.data_query.get_data_summary(file_name)
        
        if data_result["status"] == "error":
            return {"error": data_result["error"]}
        
        df = data_result["data"]
        
        # 确保时间列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
            df[time_col] = pd.to_datetime(df[time_col])
        
        # 提取两个时期的数据
        start1, end1 = period1
        start2, end2 = period2
        
        data1 = df[(df[time_col] >= start1) & (df[time_col] <= end1)][value_col].dropna()
        data2 = df[(df[time_col] >= start2) & (df[time_col] <= end2)][value_col].dropna()
        
        if len(data1) == 0 or len(data2) == 0:
            return {"error": "指定时期内没有有效数据"}
        
        # 计算统计量
        stats1 = {
            "mean": data1.mean(),
            "median": data1.median(),
            "std": data1.std(),
            "min": data1.min(),
            "max": data1.max()
        }
        
        stats2 = {
            "mean": data2.mean(),
            "median": data2.median(),
            "std": data2.std(),
            "min": data2.min(),
            "max": data2.max()
        }
        
        # 计算变化率
        mean_change = (stats2["mean"] - stats1["mean"]) / stats1["mean"] if stats1["mean"] != 0 else 0
        
        # 进行t检验（如果样本量足够）
        t_test = None
        if len(data1) > 2 and len(data2) > 2:
            from scipy import stats
            t_stat, p_value = stats.ttest_ind(data1, data2)
            t_test = {
                "t_statistic": t_stat,
                "p_value": p_value,
                "significant_difference": p_value < 0.05
            }
        
        return {
            "period1": {"range": period1, "stats": stats1},
            "period2": {"range": period2, "stats": stats2},
            "mean_change_rate": mean_change,
            "t_test": t_test
        }
    
    def analyze_distribution(self, file_name: str, column: str) -> Dict[str, Any]:
        """分析数据分布"""
        data_result = self.data_query.get_data_summary(file_name)
        
        if data_result["status"] == "error":
            return {"error": data_result["error"]}
        
        df = data_result["data"]
        
        if column not in df.columns:
            return {"error": f"列不存在: {column}"}
        
        data = df[column].dropna()
        
        if len(data) == 0:
            return {"error": "没有有效数据"}
        
        # 基本统计量
        stats = {
            "count": len(data),
            "mean": data.mean(),
            "median": data.median(),
            "std": data.std(),
            "min": data.min(),
            "max": data.max()
        }
        
        # 计算偏度和峰度
        from scipy import stats
        skewness = stats.skew(data)
        kurtosis = stats.kurtosis(data)
        
        # 正态性检验
        normality_test = None
        if len(data) >= 8:
            _, p_value = stats.normaltest(data)
            normality_test = {
                "p_value": p_value,
                "is_normal": p_value > 0.05
            }
        
        return {
            "stats": stats,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "distribution_type": "正态分布" if normality_test and normality_test["is_normal"] else "非正态分布",
            "normality_test": normality_test
        }
    
    def generate_correlation_matrix(self, file_name: str, columns: List[str] = None) -> Dict[str, Any]:
        """生成相关性矩阵"""
        data_result = self.data_query.get_data_summary(file_name)
        
        if data_result["status"] == "error":
            return {"error": data_result["error"]}
        
        df = data_result["data"]
        
        # 如果没有指定列，使用所有数值列
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 检查列是否存在
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            return {"error": f"列不存在: {missing_cols}"}
        
        # 计算相关性矩阵
        corr_matrix = df[columns].corr()
        
        # 找出强相关关系（|r| > 0.7）
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_correlations.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": corr_val,
                        "strength": "强正相关" if corr_val > 0.7 else "强负相关"
                    })
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
            "columns": columns
        }
    
    def detect_outliers(self, file_name: str, column: str, method: str = 'iqr') -> Dict[str, Any]:
        """检测异常值"""
        data_result = self.data_query.get_data_summary(file_name)
        
        if data_result["status"] == "error":
            return {"error": data_result["error"]}
        
        df = data_result["data"]
        
        if column not in df.columns:
            return {"error": f"列不存在: {column}"}
        
        data = df[column].dropna()
        
        if method == 'iqr':
            # IQR方法
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            return {
                "method": "IQR",
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "outliers": outliers.tolist(),
                "outlier_count": len(outliers),
                "outlier_percentage": len(outliers) / len(data) * 100
            }
        
        elif method == 'zscore':
            # Z-score方法
            z_scores = np.abs((data - data.mean()) / data.std())
            outliers = data[z_scores > 3]
            
            return {
                "method": "Z-score",
                "threshold": 3,
                "outliers": outliers.tolist(),
                "outlier_count": len(outliers),
                "outlier_percentage": len(outliers) / len(data) * 100
            }
        
        else:
            return {"error": f"不支持的异常值检测方法: {method}"}
    
    def generate_summary_report(self, file_name: str) -> Dict[str, Any]:
        """生成数据摘要报告"""
        data_result = self.data_query.get_data_summary(file_name)
        
        if data_result["status"] == "error":
            return {"error": data_result["error"]}
        
        df = data_result["data"]
        
        # 基本信息
        info = {
            "file_name": file_name,
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "memory_usage": df.memory_usage(deep=True).sum()
        }
        
        # 缺失值统计
        missing_values = df.isnull().sum()
        missing_percentage = (missing_values / len(df)) * 100
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_stats = df[numeric_cols].describe().to_dict() if numeric_cols else {}
        
        # 分类列统计
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        categorical_stats = {}
        for col in categorical_cols:
            value_counts = df[col].value_counts().head(10).to_dict()
            categorical_stats[col] = {
                "unique_count": df[col].nunique(),
                "top_values": value_counts
            }
        
        return {
            "info": info,
            "missing_values": missing_values.to_dict(),
            "missing_percentage": missing_percentage.to_dict(),
            "numeric_stats": numeric_stats,
            "categorical_stats": categorical_stats
        }


class ChartGenerator:
    """图表生成工具，支持matplotlib和plotly两种方式"""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_trend_chart(self, file_name: str, time_col: str, value_cols: List[str], 
                           title: str = "", engine: str = "plotly", 
                           save_path: Optional[str] = None) -> str:
        """生成趋势图"""
        # 尝试多个可能的路径
        possible_paths = [
            f"../数据/{file_name}",
            f"data/{file_name}",
            file_name
        ]
        
        df = None
        for path in possible_paths:
            try:
                df = pd.read_csv(path)
                break
            except FileNotFoundError:
                continue
        
        if df is None:
            raise FileNotFoundError(f"无法找到数据文件: {file_name}")
        
        # 确保时间列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
            df[time_col] = pd.to_datetime(df[time_col])
        
        # 按时间排序
        df = df.sort_values(time_col)
        
        if engine == "plotly":
            fig = make_subplots(specs=[[{"secondary_y": False}]])
            
            for col in value_cols:
                if col in df.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=df[time_col], 
                            y=df[col], 
                            mode='lines+markers',
                            name=col,
                            line=dict(width=2)
                        )
                    )
            
            fig.update_layout(
                title=title or f"{', '.join(value_cols)} 趋势图",
                xaxis_title="时间",
                yaxis_title="数值",
                hovermode="x unified"
            )
            
            if not save_path:
                save_path = self.output_dir / f"{file_name.split('.')[0]}_trend.html"
            
            fig.write_html(save_path)
            return str(save_path)
        
        else:  # matplotlib
            plt.figure(figsize=(12, 6))
            
            for col in value_cols:
                if col in df.columns:
                    plt.plot(df[time_col], df[col], marker='o', label=col)
            
            plt.title(title or f"{', '.join(value_cols)} 趋势图")
            plt.xlabel("时间")
            plt.ylabel("数值")
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if not save_path:
                save_path = self.output_dir / f"{file_name.split('.')[0]}_trend.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return str(save_path)
    
    def generate_correlation_heatmap(self, file_name: str, columns: Optional[List[str]] = None,
                                   title: str = "", engine: str = "plotly",
                                   save_path: Optional[str] = None) -> str:
        """生成相关性热力图"""
        # 尝试多个可能的路径
        possible_paths = [
            f"../数据/{file_name}",
            f"data/{file_name}",
            file_name
        ]
        
        df = None
        for path in possible_paths:
            try:
                df = pd.read_csv(path)
                break
            except FileNotFoundError:
                continue
        
        if df is None:
            raise FileNotFoundError(f"无法找到数据文件: {file_name}")
        
        # 只选择数值列
        numeric_df = df.select_dtypes(include=[np.number])
        
        if columns:
            numeric_df = numeric_df[columns]
        
        # 计算相关性矩阵
        corr_matrix = numeric_df.corr()
        
        if engine == "plotly":
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="RdBu_r",
                title=title or "相关性热力图"
            )
            
            if not save_path:
                save_path = self.output_dir / f"{file_name.split('.')[0]}_correlation.html"
            
            fig.write_html(save_path)
            return str(save_path)
        
        else:  # matplotlib
            plt.figure(figsize=(12, 10))
            
            sns.heatmap(
                corr_matrix, 
                annot=True, 
                cmap='RdBu_r', 
                center=0,
                square=True,
                linewidths=.5
            )
            
            plt.title(title or "相关性热力图")
            plt.tight_layout()
            
            if not save_path:
                save_path = self.output_dir / f"{file_name.split('.')[0]}_correlation.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return str(save_path)
    
    def generate_distribution_chart(self, file_name: str, column: str,
                                 title: str = "", engine: str = "plotly",
                                 save_path: Optional[str] = None) -> str:
        """生成分布图"""
        # 尝试多个可能的路径
        possible_paths = [
            f"../数据/{file_name}",
            f"data/{file_name}",
            file_name
        ]
        
        df = None
        for path in possible_paths:
            try:
                df = pd.read_csv(path)
                break
            except FileNotFoundError:
                continue
        
        if df is None:
            raise FileNotFoundError(f"无法找到数据文件: {file_name}")
        
        if column not in df.columns:
            raise ValueError(f"列不存在: {column}")
        
        data = df[column].dropna()
        
        if engine == "plotly":
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('直方图', '箱线图'),
                vertical_spacing=0.1
            )
            
            # 直方图
            fig.add_trace(
                go.Histogram(
                    x=data,
                    nbinsx=30,
                    name='分布'
                ),
                row=1, col=1
            )
            
            # 箱线图
            fig.add_trace(
                go.Box(
                    y=data,
                    name='箱线图'
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title=title or f"{column} 分布图",
                height=600
            )
            
            if not save_path:
                save_path = self.output_dir / f"{file_name.split('.')[0]}_{column}_distribution.html"
            
            fig.write_html(save_path)
            return str(save_path)
        
        else:  # matplotlib
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # 直方图
            ax1.hist(data, bins=30, alpha=0.7)
            ax1.set_title('直方图')
            ax1.set_ylabel('频数')
            
            # 箱线图
            ax2.boxplot(data, vert=False)
            ax2.set_title('箱线图')
            ax2.set_xlabel(column)
            
            plt.suptitle(title or f"{column} 分布图")
            plt.tight_layout()
            
            if not save_path:
                save_path = self.output_dir / f"{file_name.split('.')[0]}_{column}_distribution.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return str(save_path)
    
    def generate_comparison_chart(self, file_name: str, group_col: str, value_col: str,
                                title: str = "", engine: str = "plotly",
                                save_path: Optional[str] = None) -> str:
        """生成对比图"""
        # 尝试多个可能的路径
        possible_paths = [
            f"../数据/{file_name}",
            f"data/{file_name}",
            file_name
        ]
        
        df = None
        for path in possible_paths:
            try:
                df = pd.read_csv(path)
                break
            except FileNotFoundError:
                continue
        
        if df is None:
            raise FileNotFoundError(f"无法找到数据文件: {file_name}")
        
        if group_col not in df.columns or value_col not in df.columns:
            raise ValueError(f"列不存在: {group_col} 或 {value_col}")
        
        # 按组计算平均值
        grouped = df.groupby(group_col)[value_col].mean().reset_index()
        
        if engine == "plotly":
            fig = px.bar(
                grouped,
                x=group_col,
                y=value_col,
                title=title or f"{value_col} 按 {group_col} 分组对比",
                labels={value_col: '平均值', group_col: group_col}
            )
            
            if not save_path:
                save_path = self.output_dir / f"{file_name.split('.')[0]}_comparison.html"
            
            fig.write_html(save_path)
            return str(save_path)
        
        else:  # matplotlib
            plt.figure(figsize=(12, 6))
            
            plt.bar(grouped[group_col], grouped[value_col])
            plt.title(title or f"{value_col} 按 {group_col} 分组对比")
            plt.xlabel(group_col)
            plt.ylabel(f"{value_col} 平均值")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            if not save_path:
                save_path = self.output_dir / f"{file_name.split('.')[0]}_comparison.png"
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return str(save_path)