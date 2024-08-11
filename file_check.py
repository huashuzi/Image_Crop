import os
import glob

# 指定你的文件夹路径
folder_path = './output_crop'

# 获取文件夹中所有的文件名
all_files = os.listdir(folder_path)

# 分离出基本文件名，去掉扩展名和末尾的 "_annotated"（如果有）
base_names = set()
for file_name in all_files:
    if file_name.endswith(('.png', '.json')):
        base_name = file_name.replace('_annotated.png', '').replace('.png', '').replace('.json', '')
        base_names.add(base_name)

# 检查每个 base_name 对应的三种文件是否都存在
missing_files = []
for base_name in base_names:
    expected_files = [
        f"{base_name}.json",
        f"{base_name}.png",
        f"{base_name}_annotated.png"
    ]
    # 对每个期望的文件进行检查
    for expected_file in expected_files:
        if expected_file not in all_files:
            missing_files.append((base_name, expected_file))

# 打印缺失的文件信息
for base_name, missing_file in missing_files:
    print(f"Missing: {missing_file} for base name: {base_name}")
