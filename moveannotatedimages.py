import glob
import shutil
import os

# 设置源文件夹和目标文件夹的路径
source_folder = './new_delete'
target_folder = './output_visualized'

# 确保目标文件夹存在，如果不存在则创建
os.makedirs(target_folder, exist_ok=True)

# 查找所有以_annotated.png结尾的文件
for file_path in glob.glob(os.path.join(source_folder, '*_annotated.png')):
    # 构建目标文件的完整路径
    target_path = os.path.join(target_folder, os.path.basename(file_path))
    # 移动文件
    shutil.move(file_path, target_path)
    print(f'文件 {file_path} 已移动到 {target_path}')
