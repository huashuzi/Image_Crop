import json
import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from labelme import utils
from labelme.utils import shape_to_mask
import uuid
import imgviz
from matplotlib.backend_bases import MouseButton


# 标签编码映射
label_name_to_value = {
    "_background_": 0,  # 通常用0表示背景
    "1": 1,
    "2": 2,
    # 继续添加更多的标签和值...
}


# 初始化全局变量以存储图形和轴
# fig, ax = plt.subplots()
# plt.axis('off')  # 只需要在开始时设置一次


# 更新visualize_annotation函数以使用imgviz
def visualize_annotation(ax, json_file, images_dir=''):
    global label_name_to_value

    with open(json_file, 'r') as file:
        data = json.load(file)

    # 加载图像
    if data['imageData'] is not None:
        img = utils.img_b64_to_arr(data['imageData'])
    else:
        img_path = os.path.join(images_dir, data['imagePath'])
        img = np.array(Image.open(img_path))

    # 生成cls和ins（此处忽略ins）
    cls, _ = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value)

    # 使用imgviz可视化cls
    label_names = {v: k for k, v in label_name_to_value.items()}
    lbl_viz = imgviz.label2rgb(cls, img, label_names=label_names, font_size=15)

    ax.imshow(lbl_viz)
    ax.axis('off')
    plt.draw()  # 请求重绘图形


# 更新visualize_annotation函数以使用imgviz
def visualize_annotation_update(ax, json_file, images_dir=''):
    global label_name_to_value
    
    with open(json_file, 'r') as file:
        data = json.load(file)

    # 加载图像
    if data['imageData'] is not None:
        img = utils.img_b64_to_arr(data['imageData'])
    else:
        img_path = os.path.join(images_dir, data['imagePath'])
        img = np.array(Image.open(img_path))

    # 生成cls和ins（此处忽略ins）
    cls, _ = utils.shapes_to_label(img.shape, data['shapes'], label_name_to_value)

    # 使用imgviz可视化cls
    label_names = {v: k for k, v in label_name_to_value.items()}
    lbl_viz = imgviz.label2rgb(cls, img, label_names=label_names, font_size=15)

    ax.clear()
    ax.imshow(lbl_viz)
    ax.axis('off')
    plt.draw()  # 请求重绘图形

    
# 保留change_image函数，用于切换图片
def change_image(event, ax, json_files, current_index, images_dir):
    print("shubiao1shijian1")
    if event.button == 1:  # 鼠标左键
        current_index[0] = (current_index[0] - 1) % len(json_files)
        print("左键点击，切换到上一张图片")
    elif event.button == 3:  # 鼠标右键
        current_index[0] = (current_index[0] + 1) % len(json_files)
        print("右键点击，切换到下一张图片")
    # plt.close()
    visualize_annotation_update(ax, json_files[current_index[0]], images_dir)


# 这个函数将在鼠标点击事件发生时被调用
def on_click(event):
    # event.button 1是鼠标左键，2是中键，3是右键
    if event.button == 1:
        print(f"左键点击位置：({event.xdata}, {event.ydata})")
    elif event.button == 3:
        print(f"右键点击位置：({event.xdata}, {event.ydata})")

# 主函数
# 此函数用于读取指定目录下的JSON文件，并通过matplotlib展示其中的图像及对应的注解信息。
# 参数:
#   - directory (str): 指定包含JSON文件的目录路径
#   - images_dir (str, optional): 图像文件所在目录，默认为空字符串，表示与JSON文件在同一目录下

def main(directory, images_dir=''):



    global fig, ax
    # plt.ion()  # 开启交互模式
    json_files = sorted([os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')])
    if not json_files:
        print("No JSON files found in the directory.")
        return

    current_index = [0]
    fig, ax = plt.subplots()
    current_index = [0]  # 使用列表以便在函数内修改

    # 学习鼠标事件绑定函数
    # ax.plot([0, 1], [0, 1], 'k-')
    # cid = fig.canvas.mpl_connect('button_press_event', on_click)
    # plt.show()

    fig.canvas.mpl_connect('button_press_event', lambda event: change_image(event, ax, json_files, current_index, images_dir))
    
    visualize_annotation(ax, json_files[current_index[0]], images_dir)

    plt.show()
    

if __name__ == '__main__':
    directory = './output_crop'  # JSON文件的目录路径
    images_dir = './output_crop'  # 如果imagePath是相对路径，这里设置图片所在的目录路径
    main(directory, images_dir)
