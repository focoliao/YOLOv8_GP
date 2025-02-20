# YOLOv8_GP
利用yolov8网络结构，通过修改单目推理车辆4个接地点


## 运行环境
- 操作系统：Linux
- Python

## 文件结构说明
1. 运行入口： /foco
- configs: 所有配置文件
- tools: 训练及预测代码，以及各种工具
2. YOLOv8代码：
- ultralytics：最主要的源代码，修改内容绝大部分在此处
- runs：运行结果，还是按照YOLOv8的结构来的
3. README：主要的介绍和修改内容说明

## YOLOv8原始结构训练及预测
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

## 修改思路：
### 不改变整体网络架构: 修改DataSet --> 
1. 修改DataSet，使之能正确载入16个点(8对(x,y))数据，正确进行训练。
- 输入label，设定：(前：front, 后：end)；(左：left,右：right)；(上：top，下：bottom)。点的顺序从车头左下-->车尾左上，具体顺序为：前左下(flb)->后左下(elb)->后右下(erb)->前右下(frb)->前左上(flt)->前右上(frt)->后右上(ert)->后左上(elt)。见下图：
![alt text](image.png)
- 按照上述设定，计算lt和rb为：所有点中(x_min,y_max)为lt，(x_max, y_min)为rb。
2. 修改目标分配策略，主要是修改TaskAlignedAssigner
- 修改anchor点在真值范围内的：修改select_candidates_in_gts
- 修改bbox_iou逻辑：ultralytics/utils/metrics.py bbox_iou
3. 修改head层，
- 将ltrb修改成flb, elb, erb, frb, flt, frt, ert, elt。每个点都包含(x,y)坐标。
- (2)修改损失函数;
- (3)修改后处理。具体内容参见“执行步骤”

## 修改执行步骤
### 1. 冻结0-21层：由于dfl层为天然冻结，所以0-21层都会冻结，22层中的dfl层会冻结
- 冻结head层之前的参数，不参与初始化训练。具体见：ultralytics/cfg/default.yaml
- freeze: [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
### 2. 修改源代码
#### 主体是修改Head层
#### 2.0 修改前需要做的动作
- 在根目录下，执行“pip install -e .” 用于保证修改源代码后，运行时会运行最新代码，而不是原始module中的代码。
- 需要注意conda环境和pip环境，以免出现不起作用的情况。
#### 2.1 修改DataLoader: 由于已经改变了DataSet的数据样式，需要修改Dataset和DataLoader
- 具体见ultralytics\data\dataset.py 中的YOLODataset。逐条处理人如下
- cache_labels：用于从文件中加载label并cache。实际在ultralytics\data\utils.py中的verify_image_label中,进行加载及处理逻辑。
- 修改判别为segment的逻辑，从>6改成>10：verify_image_label
- 修改xywh2xyxy，xyxy2xywh：变成直接输出，因为虽然我们让程序以为输入的为xywh，实际上，输入的是xyxy的16个点。ultralytics\utils\ops.py，ultralytics\data\augment.py _update_labels
- yolov8默认作了很多图像增强，在ultralytics\cfg\default.yaml中，将所有增强全都关闭：
  mosaic: 0.0          # Mosaic 关闭
  copy_paste: 0.0      # Copy-Paste 关闭
  mixup: 0.0           # MixUp 关闭
  degrees: 0.0         # 随机旋转角度设置为 0
  translate: 0.0       # 平移增强关闭
  scale: 0.0           # 缩放增强关闭
  shear: 0.0           # 剪切增强关闭
  perspective: 0.0     # 透视变换关闭
  hsv_h: 0.0           # 颜色增强关闭（色调调整）
  hsv_s: 0.0           # 颜色增强关闭（饱和度调整）
  hsv_v: 0.0           # 颜色增强关闭（亮度调整）
  flipud: 0.0          # 垂直翻转关闭
  fliplr: 0.0          # 水平翻转关闭
- 以上方法并不直接，在ultralytics\data\build.py buiild_yolo_dataset中，直接将augment设置为false(原始为augment=mode==train)
- 修改了loss计算时的缩放乘积问题。ultralytics\utils\loss.py __call__
- 通过以上内容，DataLoader基本修改完毕
#### 2.1 修改head层:由于需要自定义输出框，需要修改head层的内容(为YOLOv8网络架构的第22层)
- 在cv2层，修改输出，从4修改为16。具体见ultralytics/nn/modules/head.py
- 对应reg_max部分，都从*4改成*16。具体见ultralytics/nn/modules/head.py
#### 2.2 修改损失函数
- 修改输出部分，从4修改为8。具体见ultralytics/utils/loss.py
- 增加自定义GPLoss，做了大量修改。具体见ultralytics/utils/loss.py
- 修改输出层为reg_max * 16，具体见ultralytics/utils/loss.py
- 修改dist2bbox，具体见ultralytics/utils/tal.py dist2bbox
- 原来使用BboxLoss, 返回loss_iou和loss_dfl。采用GPLoss函数，尽量覆盖BboxLoss的内容。

#### 2.3 修改predict：由于修改了输出框，需要更改predict的处理逻辑和输出内容
- 最终代码为：foco/tolls/yolov8_gp_predict.py
- 配置文件为：foco/configs/yolov8_gp_predict.yaml
- 修改了results，在ultralytics/engine/results.py中，包括Boxes
- 修改了predictor，在ultralytics/models/yolo/detect/predict.py中的postprocess
#### 2.4 修改后处理部分：
- 我们相关的是检测，检测的后处理部分在:ultralytics/models/yolo/detect/predict.py DetectionPredictor postprocess
- 修改非极大值抑制：ultralytics/utils/ops.py non_max_suppression
- 主要原理是：从16个点中，找到边界xyxy，自定义函数, 还是使用xyxy的NMS，最后输出时，再把结果拼接回来
- 迭代NMS：不是用iou做判断，而是用接地点的重叠来计算，可以设置很低的重叠阈值
#### 2.4 修改配置文件
- 新建数据yaml文件，见foco/configs/yolov8_gp_data.yaml。classes聚焦在道路物体上，不需要原始那么多分类。并按照自己定义的分类设置数据
- 新建训练yaml文件，见见foco/configs/yolov8_gp.yaml。
#### 2.5 修改train：
- 核心model代码在ultralytics/nn/tasks.py BaseModel
- 修改val，代码在ultralytics/models/yolo/detect/val.py
- 同时会修改很多计算公式，在metrics.py中
- 修改DetectionValidator，在ultralytics/models/yolo/detect/val.py中
- 修改了DFL，在ultralytics/nn/modules/block.py DFL

#### 2.7 其他修改如计算公式等
- 修改修改xywh2xyxy，xyxy2xywh：变成直接输出，因为虽然我们让程序以为输入的为xywh，实际上，输入的是xyxy的16个点。ultralytics\utils\ops.py xyxy2xywh xywh2xyxy
- 修改select_candidates_in_gts: 修改lt(坐上)和rb(右下)计算逻辑。ultralytics/utils/tal.py TaskAlignedAssigner select_candidates_in_gts
- 修改了画图的内容，在ultralytics/utils/plotting.py
### 3. 测试新代码
#### 3.1 数据准备
- 数据处理分为两步：第一步是从开源等数据整理成yolov8_gp所需原始数据；第二步是将原始数据进行处理，满足train/val所要求的数据。
- 外部数据，label保存为.txt文件，文件中多个标注，每个标注数据的格式如下：
0 (510.3, 857.3) (516.1, 861.9) (500.6, 862.1) (494.1, 857.5) (510.1, 871.6) (493.8, 871.8) (500.4, 875.8) (516.0, 875.7)
第一个数据为分类，与foco/configs/yolov8_gp_data.yaml中的类别一致；
第2-9个数据为长方体8个定点的像素坐标(x, y)
- 运行foco/tools/data_preparation_yolov8_gp.py，会将数据转换为yolov8规定以及训练要求的数据（如resize），格式如下：
0 0.565625 0.2064814814814815 0.5411458333333333 0.20555555555555555 0.5411458333333333 0.21203703703703702 0.5666666666666667 0.21296296296296297 0.565625 0.175 0.5416666666666666 0.175 0.5416666666666666 0.17962962962962964 0.5671875 0.18055555555555555
第一个数据为分类，与foco/configs/yolov8_gp_data.yaml中的类别一致；
第2-17个数据为外部数据归一化后的点，从(x, y) --> x y
- 相关的配置文件在data_preparation_yolov8_gp_config.yaml中。有详细注释

#### 3.2 train
- 核对yolov8默认配置，在ultralytics/cfg/default.yaml中
- 进行训练配置，配置文件为foco/yolov8_gp.yaml
- 首次训练时， 设置new:True, 并配置checkpoint， model_yaml, preset_tatal_epochs。运行foco/tools/yolov8_gp_train.py开始训练。需要中断时，直接在terminal中按ctrl+z
- resume时，设置new:False，并按实际情况配置resume_checkpoint, resume_total_epochs。运行foco/tools/yolov8_gp_train.py开始训练。中断同理
- 结果内容都是yolov8自带的，可以查看。
#### 3.3 测试predict
- 准备test数据，放在test文件夹中。主要是注意图片的size。
- 进行训练配置，配置文件为foco/yolov8_gp_predict.yaml。
- 需要设置checkpoint，并将正确的checkpoint文件拷贝到foco/tolls目录下。
- 运行foco/tools/yolov8_gp_predict.py即可预测。可根据terminal中的打印内容查看预测结果。

## 训练经验
1. loss中，MSE Loss的权重应该调，按照经验，MSE Loss控制着点的精度，如果发现比较歪，可以修改此参数
- 尝试过1，0.001，0.01，0.1。结果表明，越小，框越不规整
2. loss中，可以尝试前面的epoch只用MSE Loss，后面再加入angle和translation
- MSE Loss能快速将立体框成型
- angle和translation可以精修
3. default.yaml中，修改iou，用于NMS的 iou threshold
- 值越大，保留的结果越多，尝试过从0.1到1.0的所有-1次方值
4. 奇怪，似乎在训练过程中改变loss, 效果会更好～～但是还没掌握改变的规律
