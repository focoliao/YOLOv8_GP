# Copyright (c) Foco Liao. All rights reserved.
__author__ = 'Foco Liao'


import os
import random
import yaml
import logging
from types import SimpleNamespace
import shutil
import re
import pandas as pd
import cv2


def dict_to_namespace(d):
    #递归将字典转换为simple_name_space对象
    if isinstance(d, dict):
        for key, value in d.items():
            d[key] = dict_to_namespace(value)
        return SimpleNamespace(**d)
    elif isinstance(d, list):
        return [dict_to_namespace(item) for item in d]
    else:
        return d

def get_files_in_directory(directory):
    # 确保路径存在且是一个目录
    if not os.path.exists(directory):
        raise ValueError(f"The directory {directory} does not exists.")
    if not os.path.isdir(directory):
        raise ValueError(f"The path {directory} is not a direcotry.")
    
    # 计数文件数量
    file_count = sum([len(files) for _,_, files in os.walk(directory)])
    
    # 获取目录下的所有文件名
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    return file_count, files

def resize_and_copy_image(source_dir, target_dir, file_name, resize_value=(640,640)):
    #检查源目录是否存在，如果没有则报错返回
    if not os.path.exists(source_dir):
        raise ValueError(f"The directory {source_dir} does not exists.")
        return
    if not os.path.isdir(source_dir):
        raise ValueError(f"The path {source_dir} is not a direcotry.")
        return
    #确保目标目录存在，如果不存在则创建
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    source_file = os.path.join(source_dir, file_name)
    target_file = os.path.join(target_dir, file_name)
    # 读取原始图像
    image = cv2.imread(source_file)  # 替换为你原始图片的路径
    # 使用 OpenCV 将图像大小调整为 640x640
    resized_image = cv2.resize(image, resize_value)
    # 保存调整后的图像
    cv2.imwrite(target_file, resized_image)  # 保存为新的文件

def copy_file(source_dir, target_dir, file_name):
    #检查源目录是否存在，如果没有则报错返回
    if not os.path.exists(source_dir):
        raise ValueError(f"The directory {source_dir} does not exists.")
        return
    if not os.path.isdir(source_dir):
        raise ValueError(f"The path {source_dir} is not a direcotry.")
        return
    #确保目标目录存在，如果不存在则创建
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    source_file = os.path.join(source_dir, file_name)
    target_file = os.path.join(target_dir, file_name)
    shutil.copy(source_file, target_file)

def save_to_txt_file(file_path, file_name, content):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    try:
        with open(file_path + '/' + file_name, 'w') as file:
            for item in content:
                file.write(f"{item}\n")
    except IOError as e:
        logging.info(f"Error saving file: {e}")

def save_to_csv_file(file_path, file_name, content):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    try:
        data = {'data': content}
        df = pd.DataFrame(data)
        df.to_csv(file_path + file_name, index=False)
    except IOError as e:
        logging.info(f"Error saving file: {e}")

def read_txt_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content_lines = file.readlines()
        return content_lines
    except FileNotFoundError:
        logging.info(f"File '{file_path}' not found.")
    except IOError as e:
        logging.info(f"Error reading File:{e}")


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File {file_path} has been deleted.")
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
    except PermissionError:
        print(f"Permission denied: unable to delete {file_path}.")
    except Exception as e:
        print(f"Error occurred while deleting file {file_path}: {e}")

def check_and_make_dirs(base_save_dir, increasing_dir_prefix):
    # 核查base_dir是否存在并创建
    current_directory = os.getcwd()
    abs_base_save_dir = current_directory + base_save_dir
    if not os.path.exists(abs_base_save_dir):
        os.makedirs(abs_base_save_dir)
    # 在此dir下，检查并根据prefix递增创建文件夹
    subfolders = [f.name for f in os.scandir(abs_base_save_dir) if f.is_dir()]
    max_number = 0
    if subfolders == []:
        os.mkdir(abs_base_save_dir + increasing_dir_prefix)
        return abs_base_save_dir + increasing_dir_prefix + '/'
    else:
        for subfolder in subfolders:
            match = re.match(r"([a-zA-Z]+)(\d+)", subfolder)
            if match:
                if(match.group(1) == increasing_dir_prefix):
                    if(int(match.group(2)) > max_number):
                        max_number = int(match.group(2))
        os.mkdir(abs_base_save_dir + increasing_dir_prefix + str(max_number+1))
        return abs_base_save_dir + increasing_dir_prefix + str(max_number+1) + '/'   
     