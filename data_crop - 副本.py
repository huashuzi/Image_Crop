import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from shapely.geometry import Polygon as Polygon_geo
from PIL import Image, ImageDraw
import numpy as np
import os

# 图片和标注文件路径
image_path = './source/Image_20240219215242300.png'
annotation_path = './source/Image_20240219215242300.json'
output_dir = './output_crop/'


def crop_annotations(annotations, left, top):
    cropped_annotations = []
    clip_polygon = Polygon_geo([(left, top), (left + 512, top), (left + 512, top + 512), (left, top + 512)])
    for annotation in annotations:
        # 将多边形的坐标转换为 Shapely Polygon 对象
        polygon = Polygon_geo(annotation)

        # 计算多边形与裁剪框的交集
        intersection_polygon = polygon.intersection(clip_polygon)
        
        # 如果交集为空，则跳过当前多边形
        if intersection_polygon.is_empty:
            continue
        
        # 转换交集多边形的坐标为列表
        coords = list(intersection_polygon.exterior.coords)
        
        # 将交集多边形的坐标转换为相对于截图区域左上角的坐标
        cropped_coords = [(max(0, min(511, int(x) - left)), max(0, min(511, int(y) - top))) for x, y in coords]
        
        # 添加到裁剪后的标注信息中
        cropped_annotations.append(cropped_coords)
    
    return cropped_annotations


def draw_annotations_on_image_pil(image, annotations):
    # 如果图像不是RGBA模式，转换为RGBA
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # 创建一个绘图对象
    draw = ImageDraw.Draw(image)
    
    # 绘制每个标注
    for annotation in annotations:
        # 在PIL中绘制多边形需要将其平展为一维列表
        flattened = [coord for point in annotation for coord in point]
        draw.polygon(flattened, outline='red', fill=None)
    
    # 保存图像
    image.save(output_dir + "image_with_annotations.png")
    # 显示图像
    image.show()

def on_move(event, fig):
    # 检查鼠标是否在图像上
    if event.xdata is not None and event.ydata is not None:
        # 更新矩形框的位置，以鼠标位置为中心
        rect.set_xy((event.xdata - 256, event.ydata - 256))
        rect.set_visible(True)  # 确保矩形框可见
        fig.canvas.draw_idle()  # 重绘图像

def on_click(event, img, polygons):
    global output_dir

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
        output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, 'cropped_image.png')
        cropped_img.save(output_path)
        print("保存截图到：", output_path)

        # 截取标注信息
        cropped_annotations = crop_annotations(polygons, left, top)
        output_annotation_path = os.path.join(output_dir, 'cropped_annotation.json')
        with open(output_annotation_path, 'w') as outfile:
            json.dump({"shapes": cropped_annotations}, outfile)
        print("保存标注信息到:", output_annotation_path)

        # 绘制截图上的标注
        draw_annotations_on_image_pil(cropped_img, cropped_annotations)






# 读取图片
img = Image.open(image_path).convert('L')

# 读取标注文件
with open(annotation_path, 'r') as file:
    annotation_data = json.load(file)

# 获取标注中的多边形点（这里需要根据实际的JSON结构进行调整）
# 假设每个标注包含一个多边形，每个多边形由点的列表表示
polygons = [shape['points'] for shape in annotation_data['shapes']]

# 使用matplotlib进行可视化
fig, ax = plt.subplots()
# 显示图片
ax.imshow(img, cmap='gray')

# 绘制每个多边形
for poly in polygons:
    polygon = Polygon(poly, linewidth=1, edgecolor='g', facecolor='none', alpha=0.5)
    ax.add_patch(polygon)

# 初始化一个矩形框，但初始时不可见
rect = patches.Rectangle((0, 0), 512, 512, linewidth=1, edgecolor='r', facecolor='none', visible=False, alpha=0.5)
ax.add_patch(rect)

# 连接事件处理函数
fig.canvas.mpl_connect('motion_notify_event', lambda event: on_move(event, fig))

# 连接事件处理函数改为处理鼠标点击
fig.canvas.mpl_connect('button_press_event', lambda event: on_click(event, img, polygons))

plt.axis('off')  # 不显示坐标轴
plt.show()
