# Copyright (c) Foco Liao. All rights reserved.
__author__ = "Foco Liao"


import os
import random
import yaml
import logging
from types import SimpleNamespace
import shutil
import re
from misc_tools import dict_to_namespace, get_files_in_directory, copy_file, save_to_txt_file, read_txt_file, save_to_csv_file, delete_file

config_file = '../configs/data_preparation_yolov8_gp_config.yaml'

#根据原始数据内容及YOLOv8 GP标注要求，转换标注数据，并保存
def convert_annotation_YOLOv8_GP_3DBox(source_dir, target_dir, file_name, image_size):
    #检查源目录是否存在，如果没有则报错返回
    if not os.path.exists(source_dir):
        raise ValueError(f"The directory {source_dir} does not exists.")
        return
    if not os.path.isdir(source_dir):
        raise ValueError(f"The path {source_dir} is not a direcotry.")
        return
    
    #截取“***.png”中的***
    rematch = re.match(r'^(.*)\.png$', file_name).group(1)

    #读取源label
    source_file_path = source_dir + '/' + rematch + '.txt'    
    content_lines = read_txt_file(source_file_path)
    content_converted = []
    labels_converted = []
    for line in content_lines:
        single_line_converted = []
        single_label_converted = []
        #通过正则表达式，提取一行中的内容，成为list
        single_line = re.findall(r'\b[a-zA-Z]+(?:_[a-zA-Z]+)?\b|-?\d+\.?\d*', line)
        for i in range(17):       #只取前八个（x,y）点
            if i == 0:      #类型：default --> 0:car; default_bus --> 1:bus
                if(single_line[i] == "0"):
                    single_line_converted.append('0')
                elif(single_line[i] == "1"):
                    single_line_converted.append('1')
            elif i %2 == 1:
                #检查数据归一情况
                if(float(single_line[i])/image_size[0] > 1):
                    print(f"发现大于图片X-MAX的数，在 {file_name}")
                single_line_converted.append(str(float(single_line[i])/image_size[0])) 
                single_label_converted.append(float(single_line[i])/image_size[0])
            else:
                #检查数据归一情况
                if(float(single_line[i])/image_size[1] > 1):
                    print(f"发现大于图片Y-MAX的数，在 {file_name}")
                single_line_converted.append(str(1-float(single_line[i])/image_size[1]))
                single_label_converted.append(1-float(single_line[i])/image_size[1]) 
        content_converted.append(' '.join(single_line_converted))
        labels_converted.append(single_label_converted)

    save_to_txt_file(target_dir, rematch + '.txt', content_converted)
    return labels_converted


#准备数据集
def main():
    #加载配置信息
    with open(config_file,'r') as file:
        config_dict = yaml.safe_load(file)
    config = dict_to_namespace(config_dict)
    #检查image和label是否一一对应，没有对应的，需要删除
    print("\033[1;34mStep1: 检查image和label，确保一一匹配，不匹配的删除\033[0m")
    print("->>>核对项1：有image的都必须有label")
    image_to_label_flag = 0     # 0:初始态；1：存在有图片没label；2：不存在有图片没label
    while(image_to_label_flag !=2 ):
        exist_flag = 0  #异常存在flag
        try:
            total_data_num_image, list_file_image = get_files_in_directory(config.original_data_path.image)
            total_data_num_label, list_file_label = get_files_in_directory(config.original_data_path.label)
        except ValueError as e:
            logging.info(e)
        for i in range(total_data_num_image):
            if(list_file_image[i] != '.DS_Store'):
                prefix_image = re.match(r'^(.*)\.png$', list_file_image[i]).group(1)
                if (prefix_image + '.txt') not in list_file_label:
                    print(f"有image没有label: {prefix_image}")
                    #删除有图片没label的图片
                    delete_file(config.original_data_path.image + list_file_image[i])
                    print(f"有image没有label: {list_file_image[i]} 删除完毕")
                    exist_flag = 1
                    image_to_label_flag = 1
        if(exist_flag == 0):
            image_to_label_flag = 2
            print("-<<<核对项1完成：有image的都有label")
    
    print("->>>核对项2：有label的都必须有image")
    label_to_image_flag = 0     # 0:初始态；1：存在有label没图片；2：不存在有label没图片
    while(label_to_image_flag !=2 ):
        exist_flag = 0  #异常存在flag
        try:
            total_data_num_image, list_file_image = get_files_in_directory(config.original_data_path.image)
            total_data_num_label, list_file_label = get_files_in_directory(config.original_data_path.label)
        except ValueError as e:
            logging.info(e)
        for i in range(total_data_num_label):
            if(list_file_label[i] != '.DS_Store'):
                prefix_label = re.match(r'^(.*)\.txt$', list_file_label[i]).group(1)
                if (prefix_label + '.png') not in list_file_image:
                    print(f"有label没有image: {prefix_label}")
                    #删除有label没图片的label
                    delete_file(config.original_data_path.label + list_file_label[i])
                    print(f"有label没有image: {list_file_label[i]} 删除完毕")
                    exist_flag = 1
                    label_to_image_flag = 1
        if(exist_flag == 0):
            label_to_image_flag = 2
            print("-<<<核对项2完成：有label的都有image")
    print("\033[1;34mStepClear:image和label一一对应关系检查完成，符合要求\033[0m")

    #检查label数据合法性
    print("\033[1;34mStep2: 检查label数据合法性\033[0m")
    #检查空label，空label删除label及对应image
    print("->>>核对项1：检查空label，空label删除label及对应image")
    empty_label_flag = 0     # 0:初始态；1：存在空label；2：不存在空label
    while(empty_label_flag != 2):
        exist_flag = 0
        try:
            total_data_num_label, list_file_label = get_files_in_directory(config.original_data_path.label)
        except ValueError as e:
            logging.info(e)
        for i in range(total_data_num_label):
            if(list_file_label[i] != '.DS_Store'):  # in case of Mac
                if (read_txt_file(config.original_data_path.label + list_file_label[i]) == []):
                    delete_file(config.original_data_path.label + list_file_label[i])   #删除label文件
                    delete_file(config.original_data_path.image + list_file_label[i].replace(".txt",".png"))   #删除对应image
                    exist_flag = 1
                    empty_label_flag = 1
        if(exist_flag == 0):
            empty_label_flag = 2
    print("-<<<核对项1完成:所有空label及对应image都已删除")

    #检查label值超出图片最大尺寸，超出尺寸，删除label及对应image
    print("->>>核对项2：检查label值超出图片最大尺寸，超出尺寸删除label对应行")
    exceed_label_flag = 0     # 0:初始态；1：存在超尺寸label；2：不存在超尺寸label
    while(exceed_label_flag != 2):
        exist_flag = 0
        try:
            total_data_num_label, list_file_label = get_files_in_directory(config.original_data_path.label)
        except ValueError as e:
            logging.info(e)
        for i in range(total_data_num_label):
            if (list_file_label[i] != '.DS_Store'):  # in case of Mac
                content_lines = read_txt_file(config.original_data_path.label + list_file_label[i])
                new_content_lines = []  # 用于存储修改后的行
                for line in content_lines:
                    #通过正则表达式，提取一行中的内容，成为list
                    single_line = re.findall(r'\b[a-zA-Z]+(?:_[a-zA-Z]+)?\b|-?\d+\.?\d*', line)
                    should_keep_line = True  # 默认保留这一行
                    # 检查label超出最大值的行，删除之
                    for j in range(len(single_line)):
                        if j == 0:
                            continue  # 跳过第一项，通常是标签ID
                        elif j %2 == 1:
                            #检查数据归一情况
                            if(float(single_line[j])/config.image_size_MAXX > 1):
                                print(f"发现大于图片X-MAX的数，在 {list_file_label[i]}")
                                should_keep_line = False  # 该行不符合条件，标记为删除
                                exist_flag = 1
                                exceed_label_flag = 1
                                break  # 不再继续检查当前行
                        else:
                            #检查数据归一情况
                            if(float(single_line[j])/config.image_size_MAXY > 1):
                                print(f"发现大于图片Y-MAX的数，在 {list_file_label[i]}")
                                should_keep_line = False  # 该行不符合条件，标记为删除
                                exist_flag = 1
                                exceed_label_flag = 1
                                break  # 不再继续检查当前行
                    # 检查label外接矩形面积过小的行，删除之
                    xx = [float(i) for i in single_line[1::2]]  # 转换为浮动数
                    yy = [float(i) for i in single_line[2::2]]  # 转换为浮动数
                    x0, x1, y0, y1 = min(xx), max(xx), min(yy), max(yy)
                    if (x1-x0)*(y1-y0) < config.rect_area_threshold:
                        should_keep_line = False  # 该行不符合条件，标记为删除
                        exist_flag = 1
                        exceed_label_flag = 1
                    if should_keep_line:
                        new_content_lines.append(line.rstrip('\n'))  # 保留符合条件的行
                # 如果修改了内容（删除了行），则保存回文件
                if len(new_content_lines) != len(content_lines):
                    save_to_txt_file(config.original_data_path.label, list_file_label[i], new_content_lines)
                    print(f"更新文件: {config.original_data_path.label + list_file_label[i]}，已删除超出范围/像素太少的目标label。")        
        if(exist_flag == 0):
            exceed_label_flag = 2
    print("-<<<核对项2完成：超出尺寸，删除label对应行")
    print("\033[1;34mStepClear:所有label数据检查合法\033[0m")
    
    #从整理好的原始数据路径读取数据，并按照train, val, test分割数据
    print("\033[1;34mStep3: 从整理好的原始数据路径读取数据，并按照train, val, test分割数据\033[0m")
    #读取数据集，并按照比例制造随机数
    try:
        total_data_num_image, list_file_image = get_files_in_directory(config.original_data_path.image)
        total_data_num_label, list_file_label = get_files_in_directory(config.original_data_path.label)
    except ValueError as e:
        logging.info(e)
    total_trainval_num = int(total_data_num_image * config.trainval_percent)
    total_train_num = int(total_trainval_num * config.train_percent)
    trainval_list = random.sample(range(total_data_num_image), total_trainval_num)
    train_list = random.sample(trainval_list, total_train_num)

    train_image_paths, train_labels = [], []

    for i in range(total_data_num_image):
        if i in trainval_list:
            if i in train_list:     #train数据集
                if (list_file_image[i] != '.DS_Store'): # in case of Mac
                    copy_file(config.original_data_path.image, config.destination_data_path.train.image, list_file_image[i])        #将原始图片拷贝到train/image下
                    train_label = convert_annotation_YOLOv8_GP_3DBox(config.original_data_path.label, config.destination_data_path.train.label, list_file_image[i], [config.image_size_MAXX, config.image_size_MAXY])   #将原始label转换成FocoMono3D label并保存到train/label下
                    train_image_paths.append(config.destination_data_path.train.image + list_file_image[i])    
                    train_labels.append(train_label)
            else:       #val数据集
                if (list_file_image[i] != '.DS_Store'): # in case of Mac
                    copy_file(config.original_data_path.image, config.destination_data_path.val.image, list_file_image[i])         #将原始图片拷贝到val/image下
                    convert_annotation_YOLOv8_GP_3DBox(config.original_data_path.label, config.destination_data_path.val.label, list_file_image[i], [config.image_size_MAXX, config.image_size_MAXY])            #将原始label转换成FocoMono3D label并保存到train/label下
        else:       #test数据集
            if (list_file_image[i] != '.DS_Store'): # in case of Mac    
                copy_file(config.original_data_path.image, config.destination_data_path.test.image, list_file_image[i])         #将原始图片拷贝到testimage下

    # save_to_txt_file(config.image_paths_dir, config.train_image_paths_name, train_image_paths)   # 保存image路径文件，在某些训练时需要
    # save_to_txt_file(config.labels_dir, config.train_lables_name, train_labels)      # 保存label路径文件，在某些训练时需要 
    print(f'--train数据集image保存在：{config.destination_data_path.train.image}')
    print(f'--train数据集label保存在：{config.destination_data_path.train.label}')
    print(f'--val数据集image保存在：{config.destination_data_path.val.image}')
    print(f'--val数据集label保存在：{config.destination_data_path.val.label}')
    print(f'--所有images路径文件保存在：{config.image_paths_dir + config.train_image_paths_name}')
    print(f'--所有labels内容文件保存在：{config.labels_dir + config.train_lables_name}')
    print("\033[1;34mStepClear:数据集合准备完成\033[0m")
    

if __name__ == '__main__':
    main()