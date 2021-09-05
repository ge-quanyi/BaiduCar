# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 20:19:51 2021

@author: DYP
"""


import json
import base64
import cv2
#from PIL import Image
from io import BytesIO
import numpy as np
import base64
import json
import time
import requests
import os


url = "http://192.168.1.34:3000/tccapi"


# 发送numpy 数组
def send_img(img):
    img_encode = np.array(cv2.imencode('.jpg', img)[1]).tobytes()
    bast64_data = base64.b64encode(img_encode)
    bast64_str = str(bast64_data, 'utf-8')

    send_json = dict()
    send_json['img'] = bast64_str
    send_json['decode'] = None
    send_json = json.dumps(send_json)

    start = time.time()

    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    s = requests.session()
    s.keep_alive = False  # 关闭多余连接

    res = s.post(url, send_json, timeout=10)
    cost_time = time.time() - start
    return res, cost_time


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
all_time = time.time()
while 1:
    ret, frame = cap.read()
    #cv2.imshow("capture", frame)
    start = time.time()
    ret, cost_time = send_img(frame)
    print(time.time() - start, ret)

'''img_path = "/home/root/workspace/autostart/model_test/models/img"
imlist = os.listdir(img_path)[:100]


all_time = time.time()
for imname in imlist:
    print(len(imlist))
    print(os.path.join(img_path, imname))
    fin=cv2.imread(os.path.join(img_path, imname))
    #cv2.imshow("fin", fin)
    #cv2.waitKey(0)
    start = time.time()
    ret, cost_time = send_img(fin)
    print(time.time() - start, ret)
    #break
    
print('Using_time  ', time.time() - all_time)'''



