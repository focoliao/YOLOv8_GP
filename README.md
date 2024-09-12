# foco_mono_gp
利用yolov8网络结构，通过修改单目推理车辆4个接地点


## 运行环境
- 操作系统：Linux
- Python

## 文件结构说明
- configs: 所有配置文件
- data: 主要是自定义dataset
- engine: 方法核心引擎
- tools: 各种工具

## 修改思路：
### 不改变整体网络架构，在修改head层，将ltrb修改成l(dx,dy),t(dx,dy),r(dx,dy),b(dx,dy)，同步修改损失函数及后处理。
### 修改head层：
- 在cv2层，修改输出，从4修改为8。具体见ultralytics/nn/modules/head.py 
- 
### 修改损失函数
### 修改配置文件
- 
### 修改predict


## 执行步骤
### 1. 完成原始代码全链条，用以验证原始代码的可用性
#### 1.1 环境配置等
#### 1.2 测试predict
#### 1.3 测试train的pipeline
#### 1.4 验证完成，代码定义为V1.0， release V1.0
### 2. 修改源代码
#### 2.1 修改head层
#### 2.2 修改损失函数
#### 2.3 修改predict
### 3. 测试新代码
#### 3.1 测试train的pipeline
#### 3.2 测试predict