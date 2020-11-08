"""
# _*_ coding:utf-8 _*_
Name:.py
Date:
Author:zzdr112
connet:zzdr12
"""
import numpy as np
print("GET IT")
import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2

direction = float(0)   #机器人运行方向，正代表左，负代表右。区间[-100,100]
goal_direction = float(0)  #球门目标所在方向
v_record = []
v_set = 0.5 #设定速度
anlge_norm = 80 #角度归一化，[-80,80]
set_box_h = 300 #设置采取避障动作时，箱子高度阈值，
goal_flag = 0   #是否检测临近终点
flattion = 50 #最大膨胀比例
set_box_flt_h = 120 #设置远处箱子红色高度，小于这个高度则
duration = 10   #每次执行时长


hh = 0
for i in range(1,20):
    Img_info = cv2.imread("/home/zzdr12/Documents/FIRA/imagesrc/" + str(i) +".jpg")
    cv2.imshow("src" , Img_info)
    kernel_2 = np.ones((2, 2), np.uint8)  # 2x2的卷积核
    kernel_3 = np.ones((3, 3), np.uint8)  # 3x3的卷积核
    kernel_4 = np.ones((4, 4), np.uint8)  # 4x4的卷积核

    if Img_info is not None:  # 判断图片是否读入
        HSV = cv2.cvtColor(Img_info, cv2.COLOR_BGR2HSV)  # 把BGR图像转换为HSV格式
        #下面两个值是要识别的颜色范围 H:0 — 180 S:0 — 255 V:0 — 255
        #红色
        Lower1 = np.array([150, 20, 20])  # 要识别颜色的下限
        Upper1 = np.array([180, 255, 255])  # 要识别的颜色的上限

        # mask是把HSV图片中在颜色范围内的区域变成白色，其他区域变成黑色
        mask1 = cv2.inRange(HSV, Lower1, Upper1)
        # 下面四行是用卷积进行滤波
        # erode()函数可以对输入图像用特定结构元素进行腐蚀操作，该结构元素确定腐蚀操作过程中的邻域的形状，
        # 各点像素值将被替换为对应邻域上的最小值：
        erosion = cv2.erode(mask1, kernel_4, iterations=1)
        erosion = cv2.erode(erosion, kernel_4, iterations=1)
        # dilate()函数可以对输入图像用特定结构元素进行膨胀操作，该结构元素确定膨胀操作过程中的邻域的形状，
        # 各点像素值将被替换为对应邻域上的最大值：
        dilation = cv2.dilate(erosion, kernel_4, iterations=1)
        dilation1 = cv2.dilate(dilation, kernel_4, iterations=1)

        # 将滤波后的图像变成二值图像放在binary中
        ret1, binary1 = cv2.threshold(dilation1, 127, 255, cv2.THRESH_BINARY)

        
        #二值化滤掉图形, 滤掉远处的图形
        global set_box_flt_h
        pix_start = 439
        pix_end = 0
        for i_flt in range(0,640, 4):
            for j_flt in range(0,480, 4):
                if binary1[j_flt][i_flt] > 0:
                    pix_start = j_flt
                    break
            for j_flt in range(478, -2, -4):
                if binary1[j_flt][i_flt] > 0:
                    pix_end = j_flt
                    break
            if pix_end - pix_start < set_box_flt_h:
                binary1[0:479,i_flt] = 0

        # 在binary中发现轮廓，轮廓按照面积从小到大排列
        binary1, contours1, hierarchy1 = cv2.findContours(binary1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        p = 0
        x_append, y_append, w_append, h_append = [], [], [], []
        for i in reversed(contours1):  # 遍历所有的轮廓，从大到小遍历
            x, y, w, h = cv2.boundingRect(i)  # 将轮廓分解为识别对象的左上角坐标和宽、高
            #去除误判框
            
            if w < 20 or h < 20:
                continue
            #if h < set_box_h and (y+h)<460:   #如果障碍物很远，箱子高度小于设置的高度，则不算做障碍物
            #    continue
            
            if (y+h)>=460 and y>160:    #对于到底部的红色物体识别错误，没识别出来，这里强行补全
                y = 5
                h = 475

            global flattion
            w = int(w+flattion*(h/480))    #障碍物右侧膨胀
            if x + w > 640:
                w = 640 - x
            #障碍物膨胀，对宽度进行膨胀
            x_old = x
            x = int(x-flattion*h/480 )   #障碍物左侧膨胀
            if x < 0:
                x = 0
            w = w + (x_old - x)

            w_old = w
            w = int(w+flattion*h/480)    #障碍物右侧膨胀
            if x+w > 640:
                w = 640-x

            continue_flag = 0
            for j in range(p):
                if (x>=x_append[j] and (x+w)<=(x_append[j]+w_append[j])):   #如果有图像嵌套，则跳过
                    continue_flag = 1
                elif (x<=x_append[j] and (x+w)>=x_append[j] and (x+w)<=(x_append[j]+w_append[j])): #如果有图嵌套一部分，左边露出来
                    x_old = x_append[j]
                    x_append[j] = x
                    w_append[j] = w_append[j] + (x_old - x)
                    continue_flag = 1
                elif (x<=(x_append[j]+w_append[j]) and x>=x_append[j] and (x+w)>=(x_append[j]+w_append[j])):   #如果有图嵌套一部分，右边露出来
                    w_append[j] = w_append[j] + ((x+w)-(x_append[j]+w_append[j]))
                    continue_flag = 1
            
            if continue_flag == 1:
                continue

            x_append.append(x)
            y_append.append(y)
            w_append.append(w)
            h_append.append(h)
            # 在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
            print("x:",x," y:",y," w:",w,"h:",h)
            cv2.rectangle(Img_info, (x, y), (x + w, y + h), (0, 255,), 3)
            # 给识别对象写上标号
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(Img_info, str(p), (x - 10, y + 10), font, 1, (0, 0, 255), 2)  # 加减10是调整字符位置
            p += 1

        print('红色方块的数量是', p, '个')  # 终端输出目标数量
        # cv2.imshow('target', target)
        # cv2.imshow('Mask', mask)
        cv2.imshow("prod", dilation)
        global hh
        hh += 1
        '''if hh == 3:
            #cv2.namedWindow("Img-obstacle",0)
            #cv2.imshow('Img-obstacle', Img_info)
            #cv2.waitKey(1)
            cv2.imwrite('Img-obstacle.png', Img_info)  # 将画上矩形的图形保存到当前目录'''
        cv2.namedWindow("Img-obstacle",1)
        cv2.imshow('Img-obstacle', Img_info)
        cv2.waitKey(1)
        cv2.imwrite('/home/zzdr12/Documents/FIRA/imagefinally2/Img-obstacle{0}.png'.format(hh), Img_info)  # 将画上矩形的图形保存到当前目录
        print("Img-obstacle{0}".format(hh))

        print("x_append, y_append, w_append, h_append, p",x_append, y_append, w_append, h_append, p,)
    cv2.waitKey(1000000)