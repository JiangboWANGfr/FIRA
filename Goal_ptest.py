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
for i in range(1,21):
    Img_info = cv2.imread("/home/zzdr12/Documents/FIRA/imagesrc/" + str(i) +".jpg")
    cv2.imshow("src" , Img_info)
    kernel_2 = np.ones((2, 2), np.uint8)  # 2x2的卷积核
    kernel_3 = np.ones((3, 3), np.uint8)  # 3x3的卷积核
    kernel_4 = np.ones((4, 4), np.uint8)  # 4x4的卷积核

    if Img_info is not None:  # 判断图片是否读入
        kernel_2 = np.ones((2, 2), np.uint8)  # 2x2的卷积核
    kernel_3 = np.ones((3, 3), np.uint8)  # 3x3的卷积核
    kernel_4 = np.ones((4, 4), np.uint8)  # 4x4的卷积核

    if Img_info is not None:  # 判断图片是否读入
        HSV = cv2.cvtColor(Img_info, cv2.COLOR_BGR2HSV)  # 把BGR图像转换为HSV格式
        #下面两个值是要识别的颜色范围 H:0 — 180 S:0 — 255 V:0 — 255
        #蓝色，球门
        Lower = np.array([90, 40, 40])  # 要识别颜色的下限
        Upper = np.array([130, 255, 255])  # 要识别的颜色的上限

        # mask是把HSV图片中在颜色范围内的区域变成白色，其他区域变成黑色
        mask = cv2.inRange(HSV, Lower, Upper)
        cv2.imshow("mask" , mask)
        # 下面四行是用卷积进行滤波
        # erode()函数可以对输入图像用特定结构元素进行腐蚀操作，该结构元素确定腐蚀操作过程中的邻域的形状，
        # 各点像素值将被替换为对应邻域上的最小值：
        erosion = cv2.erode(mask, kernel_3, iterations=1)
        erosion = cv2.erode(erosion, kernel_3, iterations=1)
        # dilate()函数可以对输入图像用特定结构元素进行膨胀操作，该结构元素确定膨胀操作过程中的邻域的形状，
        # 各点像素值将被替换为对应邻域上的最大值：
        dilation = cv2.dilate(erosion, kernel_3, iterations=1)
        dilation = cv2.dilate(dilation, kernel_3, iterations=1)

        # target是把原图中的非目标颜色区域去掉剩下的图像
        #target = cv2.bitwise_and(Img_info, Img_info, mask=dilation)

        # 将滤波后的图像变成二值图像放在binary中
        ret, binary = cv2.threshold(dilation, 127, 255, cv2.THRESH_BINARY)
        cv2.imshow("binary" , binary)
        # 在binary中发现轮廓，轮廓按照面积从小到大排列
        binary, contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        p = 0
        
        x_append, y_append, w_append, h_append = [], [], [], []
        for i in contours:  # 遍历所有的轮廓
            x, y, w, h = cv2.boundingRect(i)  # 将轮廓分解为识别对象的左上角坐标和宽、高
            #去除误判框，门框没有误判
            #if w < 30 or h < 30:
            #    continue
            
            count = 0 #计数，当前障碍物的高在已有记录中排第几，从小到大
            for h_info in h_append:
                if h > h_info:
                    count += 1
            x_append.insert(count, x) #下标，参数
            y_append.insert(count, y) #下标，参数
            w_append.insert(count, w) #下标，参数
            h_append.insert(count, h) #下标，参数
            # 在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
            cv2.rectangle(Img_info, (x, y), (x + w, y + h), (0, 255,), 3)
            # 给识别对象写上标号
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(Img_info, str(p), (x - 10, y + 10), font, 1, (0, 0, 255), 2)  # 加减10是调整字符位置
            cv2.imshow("src1" , Img_info)
            p += 1

            #print('红色方块的数量是', p, '个')  # 终端输出目标数量
            
        # cv2.imshow('target', target)
        # cv2.imshow('Mask', mask)
        # cv2.imshow("prod", dilation)


        #cv2.namedWindow("Img-goal",0)
        #cv2.imshow('Img-goal', Img_info)
        #cv2.waitKey(1)
        cv2.imwrite('Img-goal.png', Img_info)  # 将画上矩形的图形保存到当前目录
        print("x_append, y_append, w_append, h_append, p",x_append, y_append, w_append, h_append, p)
   
    cv2.waitKey(100000)