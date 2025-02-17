# Copyright (c) Foco Liao. All rights reserved.
__author__ = 'Foco Liao'

#加载开源包
import sys
import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
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
config_file = "../configs/yolov8_gp.yaml"

torch.autograd.set_detect_anomaly(True)

def main():
    #加载配置信息
    with open(config_file,'r') as file:
        config_dict = yaml.safe_load(file)
    config = misc_tools.dict_to_namespace(config_dict)

    # 指定设备
    print("\033[1;34m加速硬件信息检查\033[0m")
    if torch.backends.mps.is_available():   # 考虑到mac因素，使用m芯片进行训练
        # device = torch.device("mps")  # 指定 MPS 设备 实际发现特别慢
        device = torch.device("cpu")  # 回退到 CPU
        print("- 使用Apple Silicon芯片加速")
    elif torch.cuda.is_available():
        device = torch.device("cuda:0")  # 指定Nvidia GPU 0
        index = int(device.index)
        print("- 使用GPU加速")
        print("- GPU索引号：",index)
        print("- GPU名称：",torch.cuda.get_device_name(index))
    else:
        device = torch.device("cpu")  # 回退到 CPU
        print("- 使用CPU加速")

    
    if config.new:
        model = YOLO(config.model_yaml).load(config.checkpoint).to(device)      # 加载模型
        model.train(data=config.data_yaml, epochs=config.preset_tatal_epochs, batch=8, amp=False, save_period=1, resume=False)   # 训练
    else:
        # 加载检查点文件
        checkpoint = torch.load(config.resume_checkpoint)
        # 修改总轮数为新的
        checkpoint["train_args"]["epochs"] = config.resume_tatal_epochs        # 设置为resume时的完成轮数
        # 保存修改后的检查点文件
        torch.save(checkpoint, config.resume_checkpoint)
        # 加载模型并训练
        model = YOLO(config.resume_checkpoint).to(device)      # 加载模型
        model.train(data=config.data_yaml, batch=8, amp=True, save_period=1, resume=True)       # 训练


if __name__ == '__main__':
    main()