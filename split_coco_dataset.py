from pycocotools.coco import COCO
import random
import os
import shutil
import json

def remove_prefix_from_filenames(coco, prefix):
    for image_info in coco.dataset['images']:
        image_info['file_name'] = image_info['file_name'].replace(prefix, '')

def remove_prefix_from_img_filenames(coco, prefix):
    for image_id, image_info in coco.imgs.items():
        image_info['file_name'] = image_info['file_name'].replace(prefix, '')

def add_annotations_to_coco(coco, coco_images, coco_annotations, image_id, destination_coco):
    # 根据图像ID获取对应的注释IDs
    annotation_ids = coco.getAnnIds(imgIds=image_id)

    # 根据注释IDs获取注释信息
    annotations = coco.loadAnns(annotation_ids)

    # 将注释信息添加到目标COCO注释对象
    destination_coco["annotations"].extend(annotations)

def split_coco_dataset(annotations_file, coco_JPEGImages_file, output_folder, train_ratio=0.9, random_seed=42):
    """
    将COCO数据集按照指定比例划分为训练集和验证集，并生成新的JSON注释文件。最好是labelme标注的，可以删除'JPEGImages\\'前缀，在json下images的filename里。

    Parameters:
        annotations_file (str): COCO注释文件的路径。
        coco_JPEGImages_file (str): 包含图像的文件夹路径。
        output_folder (str): 输出文件夹的路径，用于保存划分后的训练集、验证集以及新生成的JSON注释文件。
        train_ratio (float): 训练集占总数据集的比例，默认为0.9。
        random_seed (int): 随机种子，用于保证随机性的可重复性，默认为42。

    Returns:
        None
    """

    # 初始化COCO对象
    coco = COCO(annotations_file)

    # 移除图像文件名中的前缀'JPEGImages\\'
    remove_prefix_from_filenames(coco, 'JPEGImages\\')

    # 移除imgs下所有对象的'file_name'前缀'JPEGImages\\'
    remove_prefix_from_img_filenames(coco, 'JPEGImages\\')

    # 获取所有图片文件名
    all_image_ids = coco.getImgIds()
    all_images = coco.loadImgs(all_image_ids)

    # 设置随机种子
    random.seed(random_seed)

    # 按照比例计算训练集和验证集的数量
    num_images = len(all_images)
    num_train = int(num_images * train_ratio)
    num_val = num_images - num_train

    # 随机打乱图片顺序
    random.shuffle(all_images)

    # 创建训练集和验证集的文件夹
    train_folder = os.path.join(output_folder, 'train2017')
    val_folder = os.path.join(output_folder, 'val2017')
    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)

    # 创建训练集和验证集的COCO注释对象
    train_coco = {
        "info": coco.dataset["info"],
        "licenses": coco.dataset["licenses"],
        "images": [],
        "annotations": [],
        "categories": coco.dataset["categories"]
    }

    val_coco = {
        "info": coco.dataset["info"],
        "licenses": coco.dataset["licenses"],
        "images": [],
        "annotations": [],
        "categories": coco.dataset["categories"]
    }

    # 将图片复制到训练集和验证集文件夹
    for i, image_info in enumerate(all_images):
        image_filename = image_info['file_name']

        # image_filename = image_filename.replace('JPEGImages\\', '')  ## 由于labelme的标注信息中会带有'JPEGImages\\'前缀需要去除

        source_path = os.path.join(coco_JPEGImages_file, image_filename)

        if i < num_train:
            destination_folder = train_folder
            destination_coco = train_coco
        else:
            destination_folder = val_folder
            destination_coco = val_coco

        destination_path = os.path.join(destination_folder, image_filename)

        try:
            shutil.copy(source_path, destination_path)
            print(f"Copied {image_filename} to {destination_folder}")

            # 更新训练集和验证集的COCO注释信息
            destination_coco["images"].append(image_info)
            add_annotations_to_coco(coco, all_images, coco.dataset['annotations'], image_info['id'], destination_coco)
            # （可选）如果有相应的标注信息，也需要更新
            # destination_coco["annotations"].extend(...)

        except FileNotFoundError:
            print(f"File not found: {source_path}")
        except Exception as e:
            print(f"Error copying {image_filename}: {e}")

    # 创建标注信息文件夹,保存训练集和验证集的JSON文件
    ann_folder = os.path.join(output_folder, 'annotations')
    os.makedirs(ann_folder, exist_ok=True)
    with open(os.path.join(ann_folder, 'instances_train2017.json'), 'w') as train_file:
        json.dump(train_coco, train_file)

    with open(os.path.join(ann_folder, 'instances_val2017.json'), 'w') as val_file:
        json.dump(val_coco, val_file)

if __name__ == "__main__":
    # 替换以下路径为你的COCO注释文件路径，图片所在文件夹和输出文件夹路径
    coco_annotations_file = 'data_dataset_coco/annotations.json'
    coco_JPEGImages_file = 'data_dataset_coco/JPEGImages/'  # 图片所在文件夹，可能是 .png 格式图片
    output_folder_path = 'output'

    split_coco_dataset(coco_annotations_file, coco_JPEGImages_file, output_folder_path)
