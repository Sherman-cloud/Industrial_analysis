from src.tools.mapped_data_loader import MappedDataLoader
import os

# 设置数据目录
data_dir = 'data'
mapping_config = 'config/data_mapping.yaml'

# 创建数据加载器
loader = MappedDataLoader(data_root_path=data_dir, mapping_config_path=mapping_config)

# 列出可用文件
available_files = loader.list_available_files()
print('实际文件列表:')
for file in available_files['actual_files']:
    print(f'  - {file}')

print('\n映射文件列表:')
for logical, info in available_files['mapped_files'].items():
    status = '✓' if info['exists'] else '✗'
    print(f'  {status} {logical} -> {info["actual_file"]} ({info["description"]})')

# 测试加载一个文件
try:
    df = loader.load_data('宏观经济数据.csv')
    print(f'\n成功加载宏观经济数据.csv，形状: {df.shape}')
    print(f'列名: {list(df.columns)}')
except Exception as e:
    print(f'\n加载数据失败: {str(e)}')

# 测试加载另一个文件
try:
    df = loader.load_data('新能源汽车产销数据.csv')
    print(f'\n成功加载新能源汽车产销数据.csv，形状: {df.shape}')
    print(f'列名: {list(df.columns)}')
except Exception as e:
    print(f'\n加载数据失败: {str(e)}')