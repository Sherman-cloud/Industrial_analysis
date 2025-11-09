"""
数据查询工具模块
"""

import os
import pandas as pd
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class DataQuery:
    """数据查询工具类"""
    
    def __init__(self, data_dir: Union[str, Any] = "data"):
        """
        初始化数据查询工具
        
        Args:
            data_dir: 数据目录路径或数据加载器实例
        """
        # 检查是否是数据加载器实例
        if hasattr(data_dir, 'data_root_path'):
            # 这是一个数据加载器实例
            self.data_loader = data_dir
            self.data_dir = data_dir.data_root_path
        else:
            # 这是一个路径字符串
            self.data_dir = data_dir
            self.data_loader = None
        
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.warning(f"数据目录 {self.data_dir} 不存在，已创建")
    
    def get_data_summary(self, file_name: str) -> Dict[str, Any]:
        """
        获取数据文件摘要
        
        Args:
            file_name: 数据文件名
            
        Returns:
            数据摘要字典
        """
        file_path = os.path.join(self.data_dir, file_name)
        
        if not os.path.exists(file_path):
            logger.warning(f"数据文件 {file_path} 不存在")
            return {
                "status": "error",
                "error": f"数据文件 {file_path} 不存在",
                "summary": ""
            }
        
        try:
            # 读取CSV文件
            df = pd.read_csv(file_path)
            
            # 生成摘要
            summary = f"""
            文件名: {file_name}
            数据行数: {len(df)}
            数据列数: {len(df.columns)}
            列名: {', '.join(df.columns.tolist())}
            
            数据预览:
            {df.head().to_string()}
            
            数据统计信息:
            {df.describe().to_string()}
            """
            
            return {
                "status": "success",
                "file_name": file_name,
                "data_shape": df.shape,
                "columns": df.columns.tolist(),
                "summary": summary,
                "data": df
            }
            
        except Exception as e:
            logger.error(f"读取数据文件 {file_path} 失败: {str(e)}")
            return {
                "status": "error",
                "error": f"读取数据文件失败: {str(e)}",
                "summary": ""
            }
    
    def list_available_files(self) -> list:
        """
        列出可用的数据文件
        
        Returns:
            可用数据文件列表
        """
        try:
            files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
            return files
        except Exception as e:
            logger.error(f"列出数据文件失败: {str(e)}")
            return []
    
    def get_file_path(self, file_name: str) -> str:
        """
        获取数据文件的完整路径
        
        Args:
            file_name: 数据文件名
            
        Returns:
            数据文件的完整路径
        """
        return os.path.join(self.data_dir, file_name)