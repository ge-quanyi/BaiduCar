#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import datetime
import time
import cv2
import config
from widgets import Button
from camera import Camera
from driver import Driver, SLOW_DOWN_RATE
from detectors import SignDetector,TaskDetector
from cruiser import Cruiser
front_camera = Camera(config.front_cam, [640, 480])
side_camera = Camera(config.side_cam, [640, 480])
driver = Driver()
#程序开启运行开关
start_button = Button(1, "UP")
#程序关闭开关
stop_button = Button(1, "DOWN")

def draw_cruise_result(frame, res):
    color = (0, 244, 10)
    thickness = 2

    font = cv2.FONT_HERSHEY_SIMPLEX
    org = 450, 50

    fontScale = 1
    txt = "{:.4f}".format(round(res, 5))
    frame = cv2.putText(frame, txt, org, font,
                       fontScale, color, thickness, cv2.LINE_AA)
    #print("angle=",txt)
    return frame

def draw_res(frame, results):
    res = list(frame.shape)
    #print(results)
    area = 0
    results_center = [0, 0]
    for item in results:
        print(item)
        #print(type(item))
        left = item.relative_box[0] * res[1]
        top = item.relative_box[1] * res[0]
        right = item.relative_box[2] * res[1]
        bottom = item.relative_box[3] * res[0]
        start_point = (int(left), int(top))
        end_point = (int(right), int(bottom))
        width = end_point[0] - start_point[0]
        height = end_point[1] - start_point[1]
        #print(str(width) + 'dfas' + str(height))
        if width <= 0 or height <= 0:
            width = 0
            height = 0
        results_center[0] = int(left) + width/2
        results_center[1] = int(top) + height/2
        area = width * height
        #print("area:" + str(area))
        color = (0, 244, 10)
        thickness = 2
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = start_point[0], start_point[1] - 10
        area_org = 250, 50
        fontScale = 1
        frame = cv2.putText(frame, item.name, org, font, fontScale, color, thickness, cv2.LINE_AA)
    return frame, area, results_center

#确认"DOWN"按键是否按下，程序是否处于等待直行状态
def check_stop():
    if stop_button.clicked():
        return True
    return False

tower_list = [0, 0, 0, 0, 0]
target_list = [0, 0, 0, 0, 0]
cereal_list = [0, 0, 0, 0, 0]
lump_list = [0, 0, 0, 0, 0]
campsite_list = [0, 0, 0, 0, 0]
if __name__=='__main__':
    while True:
        for _ in range(18):
            driver.cart.move([-30, -30, 30, 30])
            #driver.cart.move([-30, -30, 30, 30])
            time.sleep(0.1)
        driver.cart.move([0, 0, 0, 0])
        time.sleep(5)
        for _ in range(18):
            driver.cart.move([30, 30, -30, -30])
            time.sleep(0.1)
        # time.sleep(1.7)#1.6
        driver.cart.move([0, 0, 0, 0])
        time.sleep(5)
    front_camera.stop()