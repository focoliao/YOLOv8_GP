# Copyright (c) Foco Liao. All rights reserved.
__author__ = 'Foco Liao'

#加载开源包
import sys
import os
import yaml
import torch

#加载本目录文件
from misc_tools import read_txt_file, get_files_in_directory, check_and_make_dirs
import misc_tools
from image_tools import predict_data_check


#加载上级目录下的文件
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))   #切换目录位置到上一级
from ultralytics import YOLO


#配置文件
config_file = "../configs/yolov8_gp_predict.yaml"

def main():
    #加载配置信息
    with open(config_file,'r') as file:
        config_dict = yaml.safe_load(file)
    config = misc_tools.dict_to_namespace(config_dict)

    device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    # 检查并打印所用device
    if torch.cuda.is_available():
        print("----GPU信息检查")
        index = int(device.index)
        print("- GPU索引号：",index)
        print("- GPU名称：",torch.cuda.get_device_name(index))
    else:
        print("----GPU信息检查----")
        print("- GPU是否可用：否")
        print("- 使用的设备：CPU")

    #加载模型
    model = YOLO(config.checkpoint).to(device)

    # 推理并保存结果
    model.predict(source=config.test_images_dir,save=True,save_conf=True,save_txt=True,name='output')

if __name__ == '__main__':
    main()