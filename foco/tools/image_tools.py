# Copyright (c) Foco Liao. All rights reserved.
__author__ = 'Foco Liao'


import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import re
import misc_tools
    

def predict_data_check(image_dir, label_dir, prefix, image_suffix, label_suffix, predict_result, this_predict_save_dir):
    img = mpimg.imread(image_dir + prefix + image_suffix)
    img_height, img_width = img.shape[:2]

    # 创建图形对象和坐标系
    fig, ax = plt.subplots()

    label_path = label_dir + prefix + label_suffix
    #加载数据
    labels_frame = {'label':[]}
    with open(label_path, encoding = 'utf-8') as f:
        readlines = f.readlines()
        if readlines != []:
            for item in readlines:
                label = re.findall(r"\d+(?:\.\d+)?",item)
                tuples_list = [(float(label[i+1]), float(label[i+2])) for i in range(0, len(label)-1, 2)]
                #tuples_list.append(tuples_list[0])
                labels_frame['label'].append(tuples_list)

    # 遍历原始多边形列表，绘制每个多边形
    print(f"labels_frame: {labels_frame['label']}")
    for quad in labels_frame['label']:
        x_tmp, y_tmp = zip(*quad)  # 将多边形的 x 和 y 坐标分离
        x = tuple(num_tmp*img_width for num_tmp in x_tmp)
        y = tuple(num_tmp*img_height for num_tmp in y_tmp)

        # 绘制每个顶点
        for i in range(len(x)):
            plt.plot(x[i], y[i], label=f'Vertex {i+1}')

        ax.plot(x, y, marker='.', color='g')  # 绘制多边形，顶点处绘制圆圈

    # 遍历推理多边形列表，绘制每个多边形
    print(f"predict_result:{predict_result}")
    ordered_result = []
    for i in range(len(predict_result[0])):
        ordered_result.append((predict_result[0][i][0], predict_result[0][i][1]))
    for quad in [ordered_result]:
        x_tmp, y_tmp = zip(*quad)  # 将多边形的 x 和 y 坐标分离
        x = tuple(num_tmp*img_width for num_tmp in x_tmp)
        y = tuple(num_tmp*img_height for num_tmp in y_tmp)

        # 绘制每个顶点
        for i in range(len(x)):
            plt.plot(x[i], y[i], label=f'Vertex {i+1}')

        ax.plot(x, y, marker='.', color='r')  # 绘制多边形，顶点处绘制圆圈

    # 显示图像
    ax.imshow(img)  


    # 显示图形
    #plt.grid(True)  # 显示网格
    #plt.show()
    plt.savefig(this_predict_save_dir +  prefix + image_suffix)
    misc_tools.save_to_txt_file(this_predict_save_dir, prefix + '_predict' + label_suffix, ordered_result)