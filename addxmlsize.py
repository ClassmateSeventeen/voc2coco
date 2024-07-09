import os
from PIL import Image
import xml.etree.ElementTree as ET

import pdb

# 指定 VOC 数据集的路径
voc_dir = './VOCdevkit/VOC2007'

# 遍历 Annotations 目录下的所有 XML 文件
for xml_file in os.listdir(os.path.join(voc_dir, 'Annotations')):
    # 构建 XML 文件的完整路径
    xml_path = os.path.join(voc_dir, 'Annotations', xml_file)
    
    # 解析 XML 文件
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # 获取图像文件名
    filename = xml_path.split('\\')[-1][:-4]
    # pdb.set_trace()

    # 构建图像的完整路径
    image_path = os.path.join(voc_dir, 'JPEGImages', filename + '.jpg')
    
    # 加载图像并获取尺寸和通道数信息
    # image = Image.open(image_path)
    # width, height = image.size
    # depth = len(image.getbands())
    
    # 更新 XML 文件中的尺寸和通道数信息
    # size = ET.SubElement(root, 'size')
    # width_elem = ET.SubElement(size, 'width')
    # width_elem.text = str(width)
    # height_elem = ET.SubElement(size, 'height')
    # height_elem.text = str(height)
    # depth_elem = ET.SubElement(size, 'depth')
    # depth_elem.text = str(depth)
    
    # 创建 filename 元素
    filename_element = ET.Element('filename')
    filename_element.text = filename + '.jpg'

    # 将 filename 元素添加到 root 元素下
    root.insert(0, filename_element)

    # 保存更新后的 XML 文件
    tree.write(xml_path)