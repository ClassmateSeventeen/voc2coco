import os
import json
import glob
import shutil
import xml.etree.ElementTree as ET

# 定义标签从1开始编号并给定类别对应数字标签
START_BOUNDING_BOX_ID = 1
PRE_DEFINE_CATEGORIES = {"echinus": 1, "holothurian": 2, "scallop": 3, "starfish": 4, "waterweeds": 5}

def get(root, name):
    vars = root.findall(name)
    return vars

def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise ValueError("Can not find %s in %s." % (name, root.tag))
    if length > 0 and len(vars) != length:
        raise ValueError(
            "The size of %s is supposed to be %d, but is %d."
            % (name, length, len(vars))
        )
    if length == 1:
        vars = vars[0]
    return vars

def get_filename_as_int(filename):
    try:
        filename = filename.replace("\\", "/")
        filename = os.path.splitext(os.path.basename(filename))[0]
        return int(filename)
    except:
        raise ValueError(
            "Filename %s is supposed to be an integer." % (filename))

def get_categories(xml_files):
    """Generate category name to id mapping from a list of xml files.

    Arguments:
        xml_files {list} -- A list of xml file paths.

    Returns:
        dict -- category name to id mapping.
    """
    classes_names = []
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for member in root.findall("object"):
            classes_names.append(member[0].text)
    classes_names = list(set(classes_names))
    classes_names.sort()
    return {name: i for i, name in enumerate(classes_names)}

def convert(xml_files, json_file):
    json_dict = {"images": [], "type": "instances",
                 "annotations": [], "categories": []}
    if PRE_DEFINE_CATEGORIES is not None:
        categories = PRE_DEFINE_CATEGORIES
    else:
        categories = get_categories(xml_files)
    bnd_id = START_BOUNDING_BOX_ID
    nums = len(xml_files)
    i = 1
    for xml_file in xml_files:
        print('\r converting xml to json : {}/{}'.format(i, nums), end = "")
        i += 1
        tree = ET.parse(xml_file)
        root = tree.getroot()
        path = get(root, "path")

        # The filename must be a number
        image_id = get_filename_as_int(xml_file)
        size = get_and_check(root, "size", 1)
        width = int(get_and_check(size, "width", 1).text)
        height = int(get_and_check(size, "height", 1).text)
        image = {
            "file_name": xml_file,
            "height": height,
            "width": width,
            "id": image_id,
        }
        json_dict["images"].append(image)
        # Currently we do not support segmentation.
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        for obj in get(root, "object"):
            category = get_and_check(obj, "name", 1).text
            if category not in categories:
                new_id = len(categories)
                categories[category] = new_id
            category_id = categories[category]
            bndbox = get_and_check(obj, "bndbox", 1)
            xmin = int(get_and_check(bndbox, "xmin", 1).text) - 1
            ymin = int(get_and_check(bndbox, "ymin", 1).text) - 1
            xmax = int(get_and_check(bndbox, "xmax", 1).text)
            ymax = int(get_and_check(bndbox, "ymax", 1).text)
            assert xmax > xmin
            assert ymax > ymin
            o_width = abs(xmax - xmin)
            o_height = abs(ymax - ymin)
            ann = {
                "area": o_width * o_height,
                "iscrowd": 0,
                "image_id": image_id,
                "bbox": [xmin, ymin, o_width, o_height],
                "category_id": category_id,
                "id": bnd_id,
                "ignore": 0,
                "segmentation": [],
            }
            json_dict["annotations"].append(ann)
            bnd_id = bnd_id + 1
    print()
    for cate, cid in categories.items():
        cat = {"supercategory": "none", "id": cid, "name": cate}
        json_dict["categories"].append(cat)

    os.makedirs(os.path.dirname(json_file), exist_ok=True)
    json_fp = open(json_file, "w")
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()


if __name__ == "__main__":
    voc_path = r"D:\thetest\yolov7-pytorch-master\VOCdevkit\VOC2007"
    
    #  保存coco格式数据集根目录
    save_coco_path = r"D:\thetest\yolov7-pytorch-master\cocouw"
    
    #  VOC只分了训练集和验证集即train.txt和val.txt
    data_type_list = ["train", "val"]
    for data_type in data_type_list:
        try:
            os.makedirs(os.path.join(save_coco_path, data_type))
            os.makedirs(os.path.join(save_coco_path, data_type+"_xml"))
            with open(os.path.join(voc_path, "ImageSets"+os.sep+"Main", data_type+".txt"), "r") as f:
                txt_ls = f.readlines()
            txt_ls = [i.strip() for i in txt_ls]
            idx = 0
            for i in os.listdir(os.path.join(voc_path, "JPEGImages")):
                print('\rcopying imgs', end = "")
                if os.path.splitext(i)[0] in txt_ls:
                    shutil.copy(os.path.join(voc_path, "JPEGImages", i),
                                os.path.join(save_coco_path, data_type, str(idx) + ".jpg"))
                    shutil.copy(os.path.join(voc_path, "Annotations", i[:-4]+".xml"), os.path.join(
                        save_coco_path, data_type+"_xml", str(idx)+".xml"))
                    idx += 1
        except:
            print("sdfsf")
        xml_path = os.path.join(save_coco_path, data_type+"_xml")
        xml_files = glob.glob(os.path.join(xml_path, "*.xml"))
        convert(xml_files, os.path.join(save_coco_path,
                "annotations", "instances_"+data_type+".json"))
        shutil.rmtree(xml_path)
