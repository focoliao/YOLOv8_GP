# Copyright (c) Foco Liao. All rights reserved.
__author__ = 'Foco Liao'

#加载开源包
import sys
import yaml
import torch
from ultralytics import YOLO

#加载本目录文件
from misc_tools import read_txt_file, get_files_in_directory, check_and_make_dirs
import misc_tools
from image_tools import predict_data_check


#加载上级目录下的文件
sys.path.append("..")   #切换目录位置


#配置文件
config_file = "../configs/yolov8_gp.yaml"

def main():
    #加载配置信息
    with open(config_file,'r') as file:
        config_dict = yaml.safe_load(file)
    config = misc_tools.dict_to_namespace(config_dict)

    device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    print("----GPU信息检查")
    index = int(device.index)
    print("- GPU索引号：",index)
    print("- GPU名称：",torch.cuda.get_device_name(index))

    # 加载模型
    model = YOLO(config.model_yaml).load(config.checkpoint).to(device)

    # 训练
    model.train(data=config.data_yaml, epochs=config.epochs)


if __name__ == '__main__':
    main()