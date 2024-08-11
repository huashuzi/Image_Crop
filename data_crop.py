import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from shapely.geometry import Polygon as Polygon_geo
from PIL import Image, ImageDraw
import numpy as np
import os
import copy
import glob
import threading
import time
from pynput import keyboard


source_dir = './source/'
output_dir = './output_crop/'

name_idx = 0

def initialize_name_idx(output_dir):
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        return 0  # 如果输出目录是新创建的，则从0开始命名

    # 仅计算JSON文件的数量
    json_file_count = len(glob.glob(os.path.join(output_dir, '*.json')))
    # 返回下一个索引，假设索引从0开始且连续
    return json_file_count


def crop_annotations_from_data(annotation_data, left, top):
    cropped_annotations = {
        "version": annotation_data["version"],
        "flags": annotation_data["flags"],
        "shapes": [],
        "imagePath": annotation_data["imagePath"],
        "imageData": annotation_data["imageData"],
        "imageHeight": annotation_data["imageHeight"],
        "imageWidth": annotation_data["imageWidth"],
    }
    clip_polygon = Polygon_geo([(left, top), (left + 512, top), (left + 512, top + 512), (left, top + 512)])
    
    for shape in annotation_data["shapes"]:
        polygon = Polygon_geo(shape["points"])
        
        intersection_polygon = polygon.intersection(clip_polygon)
        
        if intersection_polygon.is_empty:
            continue
        
        coords = list(intersection_polygon.exterior.coords)
        
        cropped_coords = [(max(0, min(511, int(x) - left)), max(0, min(511, int(y) - top))) for x, y in coords]
        
        # 使用原shape的属性创建新的shape字典，仅更新points属性
        new_shape = {
            "label": shape["label"],
            "points": cropped_coords,
            "group_id": shape.get("group_id", None),  # 使用get避免KeyError
            "description": shape.get("description", ""),
            "difficult": shape.get("difficult", False),
            "shape_type": shape.get("shape_type", "polygon"),
            "flags": shape.get("flags", {}),
            "attributes": shape.get("attributes", {})
        }

        cropped_annotations["shapes"].append(new_shape)
    
    return cropped_annotations


def draw_annotations_on_image_pil(image, cropped_annotations):
    global output_dir

    # 如果图像不是RGBA模式，转换为RGBA
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # 创建一个绘图对象
    draw = ImageDraw.Draw(image)
    
    # 绘制每个标注
    for shape in cropped_annotations["shapes"]:
        # 在PIL中绘制多边形需要将其平展为一维列表
        flattened = [coord for point in shape["points"] for coord in point]
        draw.polygon(flattened, outline='red', fill=None)
    
    # 保存图像
    if not output_dir.endswith("/"):
        output_dir += "/"
    image_path = output_dir + f"image_{name_idx}_annotated.png"
    image.save(image_path)
    # 如果你需要在非图形界面环境下工作，可能不需要显示图像
    # image.show()

    return image_path

def on_move(event, fig, rect):
    # 检查鼠标是否在图像上
    if event.xdata is not None and event.ydata is not None:
        # 更新矩形框的位置，以鼠标位置为中心
        rect.set_xy((event.xdata - 256, event.ydata - 256))
        rect.set_visible(True)  # 确保矩形框可见
        fig.canvas.draw_idle()  # 重绘图像



def on_click(event, img, annotation_data):
    global output_dir
    global name_idx

    name_idx = 1 + name_idx

    # 获取标注中的多边形点（这里需要根据实际的JSON结构进行调整）
    # 假设每个标注包含一个多边形，每个多边形由点的列表表示
    polygons = [shape['points'] for shape in annotation_data['shapes']]

    # 复制原有的annotation_data
    new_annotation_data = copy.deepcopy(annotation_data)
    # 修改一些信息
    new_annotation_data['version'] = annotation_data['version']
    new_annotation_data['flags'] = annotation_data['flags']
    new_annotation_data['shapes'] = annotation_data['shapes']
    new_annotation_data['imagePath'] = f'image_{name_idx}.png'
    new_annotation_data['imageData'] = annotation_data['imageData']
    new_annotation_data['imageHeight'] = 512
    new_annotation_data['imageWidth'] = 512
    

    # 检查鼠标是否在图像上
    if event.xdata is not None and event.ydata is not None and event.button == 1:  # 确保是鼠标左键点击
        # 获取鼠标点击的像素位置
        x_pixel, y_pixel = int(event.xdata), int(event.ydata)
        print(x_pixel, y_pixel)
        
        # 计算截图区域的左上角坐标
        left = max(x_pixel - 256, 0)
        top = max(y_pixel - 256, 0)
        
        # 截取图像区域
        right = min(left + 512, img.width)
        bottom = min(top + 512, img.height)
        cropped_img = img.crop((left, top, right, bottom))
        
        # 显示截图
        # cropped_img.show()

        # 保存截图
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, f'image_{name_idx}.png')
        cropped_img.save(output_path)
        print("保存截图到：", output_path)

        # 截取标注信息
        new_annotation_data = crop_annotations_from_data(new_annotation_data, left, top)

        output_annotation_path = os.path.join(output_dir, f'image_{name_idx}.json')
        with open(output_annotation_path, 'w') as outfile:
            json.dump(new_annotation_data, outfile, indent=4)
        print("保存标注信息到:", output_annotation_path)

        # 绘制截图上的标注
        draw_annotations_on_image_pil(cropped_img, new_annotation_data)


def process_image_and_annotation(image_path, annotation_path):
    # 读取图片
    img = Image.open(image_path).convert('L')

    # 读取标注文件
    with open(annotation_path, 'r') as file:
        annotation_data = json.load(file)

    # 使用matplotlib进行可视化
    fig, ax = plt.subplots()
    ax.imshow(img, cmap='gray')  # 显示图片

    # 绘制每个多边形
    polygons = [shape['points'] for shape in annotation_data['shapes']]
    for poly in polygons:
        polygon = Polygon(poly, linewidth=1, edgecolor='g', facecolor='none', alpha=0.5)
        ax.add_patch(polygon)

    # 初始化一个矩形框，但初始时不可见
    rect = patches.Rectangle((0, 0), 512, 512, linewidth=1, edgecolor='r', facecolor='none', visible=False, alpha=0.5)
    ax.add_patch(rect)

    # # 连接事件处理函数
    fig.canvas.mpl_connect('motion_notify_event', lambda event: on_move(event, fig, rect))

    # 连接事件处理函数改为处理鼠标点击
    fig.canvas.mpl_connect('button_press_event', lambda event: on_click(event, img, annotation_data))

    plt.axis('off')  # 不显示坐标轴
    plt.show()


def get_user_choice():
    """
    获取用户的选择并返回。
    """
    print("请选择以下选项中的一个：")
    print("[N] 下一张图片")
    print("[P] 上一张图片")
    print("[Q] 退出")
    choice = input("你的选择是（N/P/Q）：").strip().upper()
    return choice


def on_press(key, image_files, current_index):
    try:
        if key.char == 'n':
            current_index[0] = min(len(image_files) - 1, current_index[0] + 1)
        elif key.char == 'p':
            current_index[0] = max(0, current_index[0] - 1)
        elif key.char == 'q':
            print("退出程序。")
            return False  # 停止监听
    except AttributeError:
        pass


def listen_to_keyboard(image_files, current_index):
    with keyboard.Listener(
            on_press=lambda event: on_press(event, image_files, current_index)) as listener:
        listener.join()


def main():
    global source_dir
    global name_idx
    name_idx = initialize_name_idx(output_dir)
    image_files = sorted(glob.glob(os.path.join(source_dir, '*.png')))
    current_index = 0

    # # 创建并启动键盘监听线程
    # keyboard_thread = threading.Thread(target=listen_to_keyboard, args=(image_files, current_index))
    # keyboard_thread.start()

    while 0 <= current_index < len(image_files):
        image_path = image_files[current_index]
        base_name = os.path.basename(image_path)
        annotation_base_name = base_name.replace('.png', '.json')
        annotation_path = os.path.join(source_dir, annotation_base_name)

        if not os.path.exists(annotation_path):
            print(f"标注文件 {annotation_path} 不存在，跳过...")
            current_index += 1
            continue

        # 调用处理图片和标注的函数
        process_image_and_annotation(image_path, annotation_path)

        # 通过输入来切换图片
        user_choice = get_user_choice()
        if user_choice == 'N':
            current_index += 1
        elif user_choice == 'P':
            current_index = max(0, current_index - 1)
        elif user_choice == 'Q':
            print("退出程序。")
            break
        else:
            print("未知的选项，请重新选择。")


if __name__ == "__main__":
    
    main()
