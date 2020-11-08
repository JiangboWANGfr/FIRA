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
# img1 = cv2.imread("./Img-obstacle5.png")
# img2 = cv2.imread("./Img-obstacle7.png")
# cv2.imshow("src" , img2)

for i in range(1,21):
    
    img = cv2.imread("/home/zzdr12/Documents/FIRA/imagefinally2/Img-obstacle" + str(i) +".png")
    # cv2.imshow("src" , img)
    ROI = img[280:480,0:640]
    # cv2.imshow("ROI_WIN",img)
    r, g, b = cv2.split(img)
    g_b = cv2.subtract(g, b)
    # for i in range(0,10):

    #     ret1, binary1 = cv2.threshold(g_b, 20, 255, cv2.THRESH_BINARY)
    #     cv2.imshow("binary" + str(i*5), binary1)
    ret1, binary1 = cv2.threshold(g_b, 20, 255, cv2.THRESH_BINARY)
    kernel_9 = np.ones((7, 7), np.uint8)  # 4x4的卷积核
    # erosion = cv2.erode(binary1, kernel_4, iterations=1)
    dilation = cv2.dilate(binary1, kernel_9, iterations=5)
    # cv2.imshow("dilation" + str(i), dilation)
    edges = cv2.Canny(dilation,50,150,apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)  # 函数将通过步长为1的半径和步长为π/180的角来搜索所有可能的直线
    # cv2.imshow("edges" + str(22), edges)
    if lines is not None:
        for line in lines[:1]:
            for  rho, theta in  line:
                # print(rho,theta)
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a)) 
                cv2.line(img,(x1,y1),(x2,y2),(0,0,255),1)
                intangle = round(theta/np.pi)*180
                # fit = np.polyfit((x1,y1),(x2,y2),1)
                print("xieili",(y2-y1)/(x2-x1))
                tens = -(y2-y1)/(x2-x1)
                print("tan",np.degrees(np.arctan(tens)))
                print("x1",x1,"y1",y1,"x2",x2,"y2",y2)

                A = y2 - y1 
                B  = x2 - x1
                C = y1 * x2 -x1 * y2
                distance =  abs(A * 480 + B * 320 + C) / np.sqrt(A*A + B*B)
                print("distance",distance)
                cv2.imshow("ROI_WIN",img)
                cv2.waitKey()

            # for line in lines :
            # rho, theta = line[0]  # 获取极值ρ长度和θ角度
            # a = np.cos(theta) # 获取角度cos值
            # b = np.sin(theta) # 获取角度sin值
            # x0 = a * rho# 获取x轴值
            # y0 = b * rho # 获取y轴值　　x0和y0是直线的中点
            # x1 = int(x0 + 1000 * (-b)) # 获取这条直线最大值点x1
            # y1 = int(y0 + 1000 * (a)) # 获取这条直线最大值点y1
            # x2 = int(x0 - 1000 * (-b))  # 获取这条直线最小值点x2　　
            # y2 = int(y0 - 1000 * (a)) # 获取这条直线最小值点y2　　其中*1000是内部规则
            # cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2) # 开始划线
            # cv2.imshow("image line", img)
            # cv2.imwrite("/home/zzdr12/Documents/FIRA/imagefially/image" + str(i) +".jpg",img)
