# 1 剪裁图片
数据流：source -> output_crop
命令：data_crop
功能：选择指定区域进行裁剪

# 2 移动图片 和 检查标注信息
数据流：output_crop -> output_visualized
命令：moveannotatedimages
功能1：将图片转移至目标文件夹
命令2：browse_pictures
功能2：仅用图片信息和标注信息来检查标注是否正确

# 3 生成标注文件
数据流：output_crop -> annotations
命令：导出
功能：汇总标注文件

# 4 划分数据集
数据流：data_dataset_coco -> output
命令：split_coco_dataset

# 其他：
classes.txt是类别标签
file_check.py是检查生成文件中 image_*.png、image_*.json、image_*_annotated.png三者缺少哪一个

# 文件夹：
annotations 汇总的json文件
data_dataset_coco 转成的数据集，包含图片和annotations.json
new_delete 在 source 中不合理的数据集剪切到这里
output 划分数据集的输出文件夹
output_crop 裁剪标注后的输出文件夹
output_visualized 保存生成的可视化图片（手动剪切过来）
source 标注好的源文件

