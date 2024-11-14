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
### 不改变整体网络架构，修改head层，将ltrb修改成l(dx,dy),t(dx,dy),r(dx,dy),b(dx,dy)，同步修改损失函数及后处理。具体内容参见“执行步骤”

## 执行步骤
### 1. 完成原始代码全链条，用以验证原始代码的可用性
#### 1.1 拉取文件、配置环境、安装框架及依赖等
##### 1.1.1 拉区文件及准备
- 创建文件夹：YOLOv8_GP，并进入文件夹
- git clone https://github.com/focoliao/YOLOv8_GP
- 拉取远程分支: git pull origin dev_V1.0:dev_V1.0, 并切换到分支: git switch dev_V1.0
##### 1.1.2 配置环境
- 使用之前gp环境：conda activate gp
- 根目录下运行python foco/tools/env_test_foco.py可以看到环境检测结果
##### 1.1.3 安装框架及依赖
- 在使用gp之后，似乎不用再安装这些了，可以正常跑预测
#### 1.2 测试predict: 由于ultralytics高度封装YOLOv8, 只能遵循ultralytics的要求，通过新建文件的方式调用。
- predict代码在foco/tools/test_original_yolov8_predict.py
- 对应配置在foco/configs/test_original_yolov8_predict.yaml中
- 运行python test_original_yolov8_predict.py即可完成预测
#### 1.3 测试train的pipeline
##### 1.3.1 准备数据集：
- 数据集图像存储：~/images/train/, ~/images/val/
- 数据集label存储：~/labels/train/, ~/labels/val/
##### 1.3.2 准备相应文件：
- 新建数据yaml文件，见foco/configs/test_original_yolov8_data.yaml
- train代码在foco/tools/test_original_yolov8_train.py
##### 1.3.3 训练及测试
- 运行 foco/tools/test_original_yolov8_train.py，可以看到结果
#### 1.4 验证完成，代码定义为V1.0， release V1.0
- 合并代码，删除本地开发分支，打V1.0 tag，推送到github，删除远程开发分支
- 远程发布release V1.0

### 2. 修改源代码
#### 冻结YOLOv8的卷积层部分（backbone），只训练Head层
#### 2.1 修改head层:由于需要自定义输出框，需要修改head层的内容
- 在cv2层，修改输出，从4修改为8。具体见ultralytics/nn/modules/head.py
- 
#### 2.2 修改损失函数
- 
#### 2.3 修改predict：由于修改了输出框，需要更改predict的处理逻辑和输出内容
- 
#### 2.4 修改配置文件
- 新建数据yaml文件，见foco/configs/yolov8_gp_data.yaml。classes聚焦在道路物体上，不需要原始那么多分类。并按照自己定义的分类设置数据
- 新建训练yaml文件，见见foco/configs/yolov8_gp.yaml。
#### 2.5 修改train：
- 冻结head层之前的参数，不参与初始化训练。具体见：
- 
### 3. 测试新代码
#### 3.1 测试train的pipeline
#### 3.2 测试predict