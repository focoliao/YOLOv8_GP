# Copyright (c) Foco Liao. All rights reserved.
__author__ = 'Foco Liao'

import torch
import platform

print("\n=========================环境检测-开始=========================")
print("1.系统环境")
print(f"- 操作系统: {platform.system()}")
print(f"- 节点名称: {platform.node()}")
print(f"- 发布: {platform.release()}")
print(f"- 版本: {platform.version()}")
print(f"- 设备: {platform.machine()}")
print(f"- Platform: {platform.platform()}")
print(f"- Uname: {platform.uname()}")
print(f"- 架构: {platform.architecture()}")
print("2.Python")
print(f"- Python版本: {platform.python_version()}")
print("- PyTorch版本：", torch.__version__)
print("- CUDA是否可用：", torch.cuda.is_available())
print("- GPU数量：", torch.cuda.device_count())
print("- torch方法查看CUDA版本：", torch.version.cuda)
index = torch.cuda.current_device()
print("- GPU索引号：",index)
print("- GPU名称：",torch.cuda.get_device_name(index))
print("=========================环境检测-结束=========================\n")