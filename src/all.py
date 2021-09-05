import os
import cv2
import time
from cruiser import Cruiser
from detectors import SignDetector,TaskDetector
from camera import Camera
import config
from driver import Driver
from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate

driver = Driver()
cruiser = Cruiser()
led = Light(2)
image_extensions = [".png",".jpg",".jpeg"]
#程序开启运行开关
start_button = Button(1, "UP")
#程序关闭开关
stop_button = Button(1, "DOWN")
#left_button
left_button = Button(1, "LEFT")
#保存视频标志位
save_video_flag = 0
#保存图片标注位
save_image_flag = 0
image_num = 10916
image_dir = "/run/media/sda1/front720"


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
    area = 0
    results_center = [0, 0]
    for item in results:
        print(item)
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

def black_img(frame):
    frame[0:120][0:640] = 0
    frame[400:480][0:640] = 0
    return frame

tower_list = [0, 0, 0, 0, 0]
target_list = [0, 0, 0, 0, 0]
cereal_list = [0, 0, 0, 0, 0]
lump_list = [0, 0, 0, 0, 0]
campsite_list = [0, 0, 0, 0, 0]
if __name__ == "__main__":
    ################
    # 摄像头初始化
    front_camera = Camera(config.front_cam, [640, 480])
    side_camera = Camera(config.side_cam, [640, 480])
    #time.sleep(3)
    front_camera.start()
    side_camera.start()
    time.sleep(3)
    # side_camera.start()
    ################
    # 舵机，电机初始化
    camera_servo = Servo(1)  # 1摄像头舵机
    # time.sleep(2)
    #camera_servo.servocontrol(124, 50)
    #time.sleep(2)
    dunhuang_servo = Servo_pwm(3)  # 敦煌旗帜
    #dunhuang_servo.servocontrol(-15, 50)  # 初始化
    daijun_servo = Servo_pwm(4)  # 代郡旗帜
    #daijun_servo.servocontrol(-5, 80)
    dingxiagn_servo = Servo_pwm(5)  # 定襄旗帜
    #dingxiagn_servo.servocontrol(-1, 80)
    rab_servo = Servo(2) #2夹块智能舵机
    rab_pwm_servo = Servo_pwm(2) #夹块舵机
    cereal_pwm = Servo_pwm(6) #放球舵机
    # time.sleep(0)
    target_motor = Motor_rotate(2)
    cereal_motor = Motor_rotate(1)
    # 检测模型
    sd = SignDetector()  # 地标检测模型
    # td = TaskDetector() #侧边检测模型
    time.sleep(1)
    ################
    #巡航参数
    car_speed = 45
    angle_pid_flag = 0
    tower_Kx = 0.86
    target_Kx = 0.82  # 0.92
    campsite_Kx = 0.89   # 0.85
    lump_Kx = 1.0  # 1.2#1.1#1.04
    cereal_Kx = 0.86  # 0.83
    #driver.set_speed_kx = 30 #麦轮分解系数
    #driver.set_speed(35) #35#基础速度
    #driver.cart.Kx = 0.9 #0.9转向系数
    #driver.cart.speed_kx = 40
    driver.set_speed(car_speed)
    # 转弯系数
    driver.cart.Kx = tower_Kx#0.73#1.05
    #driver.cart.speed_kx = 25
    driver.cart.slow_ratio = 1
    #############
    #保存视频
    if save_video_flag == 1:
        save_video = cv2.VideoWriter('/run/media/sda1/video/output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 6.0, (640, 480))
    while True:
        if start_button.clicked():
            time.sleep(0.3)
            break
        print("Wait for start!")
    right_button_flag = 0
    tower_num = 0
    target_num = 0
    while True:
        front_image = front_camera.read()
        front_image = black_img(front_image)
        if stop_button.clicked():
            driver.cart.move([0, 0, 0, 0])
            rab_pwm_servo.servocontrol(60, 50)
            tower_num = 0
            target_num = 0
            while True:
                if start_button.clicked():
                    driver.set_speed(car_speed)
                    # 转弯系数
                    driver.cart.Kx = tower_Kx # 1.05
                    # driver.cart.speed_kx = 25
                    driver.cart.slow_ratio = 1
                    time.sleep(0.3)
                    break
                '''elif left_button.clicked():
                    car_speed2 = 45
                    tower_Kx2 = 1.05
                    target_Kx2 = 1.25  # 0.92
                    campsite_Kx2 = 1.12  # 0.78
                    lump_Kx2 = 1.35  # 1.2#1.1#1.04
                    cereal_Kx2 = 1.45
                    driver.cart.slow_ratio = 1
                    driver.set_speed(car_speed2)
                    driver.cart.Kx = tower_Kx2  # 1.05
                    sd = SignDetector()
                    target_zhuan_flag = 0
                    lump_zhuan_flag = 0
                    tower_list2 = [0, 0, 0, 0, 0]
                    target_list2 = [0, 0, 0, 0, 0]
                    cereal_list2 = [0, 0, 0, 0, 0]
                    lump_list2 = [0, 0, 0, 0, 0]
                    campsite_list2 = [0, 0, 0, 0, 0]
                    while True:
                        front_image = front_camera.read()
                        res = driver.go(front_image)
                        print(res)
                        signs, index = sd.detect(front_image)
                        #driver.cart.steer(res)
                        if len(signs) > 0:
                            frame, area, sign_center = draw_res(front_image, signs)
                            # print(area)
                            # print(sign_center)
                            driver.cart.steer(res)
                        else:
                            driver.cart.steer(res)
                        if len(signs) > 0 and signs[0].name == "tower":
                            del (tower_list2[0])
                            tower_list2.append(1)
                            #print(target_list)
                            if tower_list2.count(1) > 2 and sign_center[1] > 300 and abs(sign_center[0] - 320) < 75:
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(1)
                                driver.cart.Kx = tower_Kx2
                                #driver.cart.steer(res)
                        else:
                            del (tower_list2[0])
                            tower_list2.append(0)
                        if len(signs) > 0 and signs[0].name == "target":
                            del (target_list2[0])
                            target_list2.append(1)
                            if target_list2.count(1) > 1 and sign_center[1] > 280 and abs(
                                    sign_center[0] - 320) < 180 and res > 0.2:
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(1)
                                driver.cart.Kx = target_Kx2
                                #driver.cart.steer(res)
                        else:
                            del (target_list2[0])
                            target_list2.append(0)
                        if len(signs) > 0 and signs[0].name == "campsite":
                            del (campsite_list2[0])
                            campsite_list2.append(1)
                            if campsite_list2.count(1) > 2 and area > 3500 and area < 24000 and abs(
                                    sign_center[1] - 320) < 50:
                                time.sleep(0.5)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(1)
                                driver.cart.Kx = campsite_Kx2
                                #driver.cart.steer(res)
                        else:
                            del (campsite_list2[0])
                            campsite_list2.append(0)
                        if len(signs) > 0 and signs[0].name == "lump" and area > 3000 and area < 12000:
                            # print(area)
                            del (lump_list2[0])
                            lump_list2.append(1)
                            if lump_list2.count(1) > 2 and area > 4500:
                                driver.cart.move([0, 0, 0, 0])
                                #time.sleep(1)
                                driver.cart.Kx = lump_Kx2
                                #driver.cart.steer(res)
                        else:
                            del (lump_list2[0])
                            lump_list2.append(0)
                        if len(signs) > 0 and signs[0].name == "cereal" and area < 12000:
                            del (cereal_list2[0])
                            cereal_list2.append(1)
                            if cereal_list2.count(1) > 1 and area > 4500:  # 4500
                                time.sleep(0.5)
                                driver.cart.move([0, 0, 0, 0])
                                time.sleep(1)
                                driver.cart.Kx = cereal_Kx2
                                driver.cart.steer(res)
                        else:
                            del (cereal_list2[0])
                            cereal_list2.append(0)'''
                #print("Wait for start")
        #side_image = side_camera.read()
        if save_image_flag == 1:
            path = "{}/{}.jpg".format(image_dir, image_num)
            cv2.imwrite(path, front_image)
            cv2.waitKey(60)
            print(image_num)
            image_num += 1
            continue
        res = driver.go(front_image)
        print(res)
        if angle_pid_flag == 1:
            if res > 0.65:
                res = res - (res - 0.65) * 0.5
            elif res < -0.55:
                res = res - (res + 0.65) * 0.5
        else:
            res = res
        #print(res)
        signs, index = sd.detect(front_image)
        sign_center = [0, 0]
        if len(signs) > 0:
            frame, area, sign_center = draw_res(front_image, signs)
            #print(area)
            #print(sign_center)
            driver.cart.steer(res)
            #if signs[0].name == 'campsite':
            #    driver.cart.Kx = 1.1
        else:
            driver.cart.steer(res)
        #print(res)
        #城堡识别并举旗
        if len(signs) > 0 and signs[0].name == "tower":
            del (tower_list[0])
            tower_list.append(1)
            print(target_list)
            if tower_list.count(1) > 1 and sign_center[1] > 300 and abs(sign_center[0] - 320) < 180:#and abs(res) < 0.1 and area > 5500:
                #time.sleep(0.65)
                time.sleep(0.42)
                driver.cart.move([0, 0, 0, 0])
                tower_num += 1
                td = TaskDetector()  # 侧边检测模型
                #side_camera = Camera(config.side_cam, [640, 480])
                #side_camera.start()
                #side_image = side_camera.read()
                if tower_num == 1 or tower_num == 3:
                    camera_servo.servocontrol(124, 50)
                elif tower_num == 2:
                    camera_servo.servocontrol(-40, 50)
                time.sleep(1)
                find_tower_frame_num = 0
                find_tower_flag = 0
                tasks = [0, 0]
                forward_flag = 0
                backward_flag = 0
                for i in range(30):
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    if len(tasks) > 0 and score > 0.75 and (tasks[0].name == 'daijun' or tasks[0].name == 'dunhuang' or tasks[0].name == 'dingxiang'):
                        draw_res(side_image, tasks)
                        find_tower_frame_num += 1
                        #print(tasks[0].name)
                    #print(find_tower_frame_num)
                    if find_tower_frame_num >= 3: # 5
                        #print('back_flag', backward_flag)
                        #print('forward_flag', forward_flag)
                        find_tower_flag = 1
                        if forward_flag == 1:
                            forward_flag = 0
                            driver.cart.move([-15, 15, -15, 15])
                            time.sleep(1.3)
                            driver.cart.move([0, 0, 0, 0])
                        if backward_flag == 1:
                            backward_flag = 0
                            driver.cart.move([15, -15, 15, -15])
                            time.sleep(1.3)
                            driver.cart.move([0, 0, 0, 0])
                        break
                    if i == 10 and find_tower_flag == 0:
                        find_tower_frame_num = 0
                        forward_flag = 1
                        backward_flag = 0
                        driver.cart.move([15, -15, 15, -15])
                        time.sleep(1.3)
                        driver.cart.move([0, 0, 0, 0])
                    if i == 20 and find_tower_flag == 0:
                        find_tower_frame_num = 0
                        forward_flag = 0
                        backward_flag = 1
                        driver.cart.move([-15, 15, -15, 15])
                        time.sleep(2.6)
                        driver.cart.move([0, 0, 0, 0])
                if forward_flag == 1:
                    forward_flag = 0
                    driver.cart.move([-15, 15, -15, 15])
                    time.sleep(1.3)
                    driver.cart.move([0, 0, 0, 0])
                if backward_flag == 1:
                    backward_flag = 0
                    driver.cart.move([15, -15, 15, -15])
                    time.sleep(1.3)
                    driver.cart.move([0, 0, 0, 0])
                #print('find_tower_flag = ', find_tower_flag)
                '''if find_tower_flag == 0:
                    find_tower_frame_num = 0
                    camera_servo.servocontrol(-40, 50)
                    time.sleep(2)
                    for i in range(30):
                        side_image = side_camera.read()
                        tasks, score = td.detect(side_image)
                        #draw_res(side_image, tasks)
                        print(i, tasks)
                        if len(tasks) > 0 and score > 0.85 and (tasks[0].name == 'daijun' or tasks[0].name == 'dunhuang' or tasks[0].name == 'dingxiang'):
                            draw_res(side_image, tasks)
                            find_tower_frame_num += 1
                            #print(tasks[0].name)
                        if find_tower_frame_num >= 5:
                            find_tower_flag = 1
                            if forward_flag == 1:
                                forward_flag = 0
                                driver.cart.move([-15, 15, -15, 15])
                                time.sleep(1.3)
                                driver.cart.move([0, 0, 0, 0])
                            if backward_flag == 1:
                                backward_flag = 0
                                driver.cart.move([15, -15, 15, -15])
                                time.sleep(1.3)
                                driver.cart.move([0, 0, 0, 0])
                            break
                        if i == 10 and find_tower_flag == 0:
                            find_tower_frame_num = 0
                            forward_flag = 1
                            backward_flag = 0
                            driver.cart.move([15, -15, 15, -15])
                            time.sleep(1.3)
                            driver.cart.move([0, 0, 0, 0])
                        if i == 20 and find_tower_flag == 0:
                            find_tower_frame_num = 0
                            forward_flag = 0
                            backward_flag = 1
                            driver.cart.move([-15, 15, -15, 15])
                            time.sleep(2.6)
                            driver.cart.move([0, 0, 0, 0])
                        #print(find_tower_frame_num)'''
                driver.cart.Kx = tower_Kx
                angle_pid_flag = 1
                if len(tasks) > 0 and tasks[0].name == 'dunhuang':
                    print(tasks[0].name)
                    dunhuang_servo.servocontrol(85, 50)
                    time.sleep(0.1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        #time.sleep(0.1)
                        led.lightoff()
                        #time.sleep(0.1)
                    dunhuang_servo.servocontrol(-15, 50)
                    #time.sleep(1)
                elif len(tasks) > 0 and tasks[0].name == "daijun":
                    print(tasks[0].name)
                    daijun_servo.servocontrol(45, 80)
                    #time.sleep(1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        #time.sleep(0.1)
                        led.lightoff()
                        #time.sleep(0.1)
                    daijun_servo.servocontrol(-5, 50)
                    #time.sleep(1)
                elif len(tasks) > 0 and tasks[0].name == "dingxiang":
                    print(tasks[0].name)
                    dingxiagn_servo.servocontrol(45, 80)
                    time.sleep(0.1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        #time.sleep(0.1)
                        led.lightoff()
                        #time.sleep(0.1)
                    #time.sleep(5)
                    dingxiagn_servo.servocontrol(-1, 80)
                    #time.sleep(1)
                #draw_res(side_image, tasks)
                #side_camera.stop()
                #side_camera.relase_camera()
        else:
            del (tower_list[0])
            tower_list.append(0)
            #print(target_list)

        # 打把
        if len(signs) > 0 and signs[0].name == "target":
            del (target_list[0])
            target_list.append(1)
            if target_list.count(1) > 1 and sign_center[1] > 260 and abs(sign_center[0] - 320) < 180: #230and abs(res) < 0.1 and area > 5500:
                #time.sleep(0.35)
                #print(target_list)
                driver.cart.Kx = target_Kx
                angle_pid_flag = 0
                driver.cart.move([0, 0, 0, 0]) #    停车
                td = TaskDetector()  # 侧边检测模型
                #side_camera = Camera(config.side_cam, [640, 480])
                #side_camera.start()
                camera_servo.servocontrol(-40, 50)
                time.sleep(1)
                zhuan_flag = 0
                x1_flag = 0
                #while True:
                #target_center_list = [0, 0, 0, 0, 0]
                last_target_center = [0, 0]
                last_last_target_center = [0, 0]
                target_center = [0,0]
                nfind_target_flag = 0
                for i in range(80):
                    front_image = front_camera.read()
                    front_image = black_img(front_image)
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    res = driver.go(front_image)
                    print("res:",res)
                    if res > 0.25:
                        res = 0.05
                    elif res < -0.25:
                        res = -0.05
                    #driver.set_speed(10)
                    find_target_flag = 0
                    target_center_x = 0
                    if len(tasks) > 0 and score > 0.5 and tasks[0].name == 'red_target':
                        # 添加
                        last_last_target_center[0] = last_target_center[0]
                        last_target_center[0] = target_center[0]

                        side_image, target_area, target_center = draw_res(side_image, tasks)
                        nfind_target_flag = 0
                        print("target_center = ", target_center)

                        if last_target_center[0] == 0 and last_last_target_center[0] != 0:
                            target_center_x = (target_center[0] + last_last_target_center[0]) / 2
                        elif last_target_center[0] != 0 and last_last_target_center[0] == 0:
                            target_center_x = (target_center[0] + last_target_center[0]) / 2
                        elif last_target_center[0] != 0 and last_last_target_center[0] != 0:
                            target_center_x = (target_center[0] + + last_last_target_center[0] + last_target_center[0]) / 3
                        elif last_target_center[0] == 0 and last_last_target_center[0] == 0:
                            target_center_x = target_center[0]
                        find_target_flag = 1
                    elif len(tasks) == 0 and zhuan_flag == 1:
                        driver.cart.move([-10, 10, -10, 10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        nfind_target_flag += 1


                    if abs(res) > 0.02 and zhuan_flag == 0:
                        val = 30 * res
                        if val < 10:
                            val = 10
                        elif val > 25:
                            val = 10
                        driver.cart.move([val, val, val, val])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        continue
                    elif abs(res) < 0.02 and zhuan_flag == 0:
                        driver.cart.move([15, -15, 15, -15])
                        time.sleep(1.8)
                        driver.cart.move([0, 0, 0, 0])
                           #time.sleep(1)`
                        zhuan_flag = 1


                    if find_target_flag == 1 and abs(target_center[1] - 200) < 15 and x1_flag == 0:
                        x1_flag = 1
                    elif find_target_flag == 1 and target_center[1] - 200 > 15 and x1_flag == 0:
                        driver.cart.move([-20, -20, 20, 20])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_target_flag == 1 and target_center[1] - 200 < -15 and x1_flag == 0:
                        driver.cart.move([20, 20, -20, -20])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    if (find_target_flag == 1 and x1_flag == 1 and abs(int(target_center[0]) - 295) < 1 and zhuan_flag) or i == 79 or nfind_target_flag == 5:
                        #print("iiiiiiiiiiiii=== ", i)
                        print(nfind_target_flag)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        target_motor.motor_rotate(-40)
                        time.sleep(0.5)
                        target_motor.motor_rotate(0)
                        time.sleep(0.5)
                        target_motor.motor_rotate(15)
                        time.sleep(3.2)
                        target_motor.motor_rotate(0)
                        time.sleep(1)
                        driver.cart.move([-10, -10, 10, 10])
                        time.sleep(0.4)
                        driver.cart.move([0, 0, 0, 0])
                        target_num +=1
                        driver.set_speed(car_speed)
                        break
                    elif find_target_flag == 1 and x1_flag == 1 and (int(target_center[0]) - 295) > 1 and zhuan_flag:
                        driver.cart.move([-8, 8, -8, 8])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_target_flag == 1 and x1_flag == 1 and (int(target_center[0]) - 295) < -1 and zhuan_flag:
                        driver.cart.move([8, -8, 8, -8])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    '''if (find_target_flag == 1 and (abs(target_center[1] - 200) < 5 and abs(int(target_center_x) - 260) < 5 and zhuan_flag)) or i == 29 or nfind_target_flag == 1:
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        target_motor.motor_rotate(-40)
                        time.sleep(1.2)
                        target_motor.motor_rotate(0)
                        time.sleep(1)
                        target_motor.motor_rotate(15)
                        time.sleep(3.2)
                        target_motor.motor_rotate(0)
                        time.sleep(1)
                        driver.set_speed(car_speed)
                        break
                    elif find_target_flag == 1 and abs(target_center[1] - 200) < 5 and target_center_x - 260 > 5 and zhuan_flag:
                        driver.cart.move([-5, 5, -5, 5])
                    elif find_target_flag == 1 and abs(target_center[1] - 200) < 5 and target_center_x - 260 < -5 and zhuan_flag:
                        driver.cart.move([5, -5, 5, -5])
                    elif find_target_flag == 1 and target_center[1] - 200 > 5 and abs(int(target_center_x) - 260) < 5 and zhuan_flag:
                        driver.cart.move([-5, -5, 5, 5])
                    elif find_target_flag == 1 and target_center[1] - 200 > 5 and target_center_x - 260 > 5 and zhuan_flag:
                        driver.cart.move([-10, 0, 0, 10])
                    elif find_target_flag == 1 and target_center[1] - 200 > 5 and target_center_x - 260 < -5 and zhuan_flag:
                        driver.cart.move([0, -10, 10, 0])
                    elif find_target_flag == 1 and target_center[1] - 200 < -5 and abs(int(target_center_x) - 260) < 5 and zhuan_flag:
                        driver.cart.move([5, 5, -5, -5])
                    elif find_target_flag == 1 and target_center[1] - 200 < -5 and target_center_x - 260 > 5 and zhuan_flag:
                        driver.cart.move([0, 10, -10, 0])
                    elif find_target_flag == 1 and target_center[1] - 200 < -5 and target_center_x - 260 < -5 and zhuan_flag:
                        driver.cart.move([10, 0, 0, -10])'''
                #side_camera.stop()
                #side_camera.relase_camera()
        else:
            del (target_list[0])
            target_list.append(0)

        # 粮草
        if len(signs) > 0 and signs[0].name == "cereal" and area < 12000:
            del (cereal_list[0])
            cereal_list.append(1)
            #print(cereal_list)
            if cereal_list.count(1) > 1 and area > 4500: #4500
                driver.cart.Kx = cereal_Kx
                angle_pid_flag = 0
                time.sleep(0.5)
                driver.cart.move([0, 0, 0, 0])
                #time.sleep(1)
                td = TaskDetector()  # 侧边检测模型
                #side_camera = Camera(config.side_cam, [640, 480])
                #side_camera.start()
                camera_servo.servocontrol(-40, 50)
                time.sleep(1)
                nfind_cereal_num = 0
                zhuan_flag = 0

                # while True:
                for i in range(100):
                    front_image = front_camera.read()
                    front_image = black_img(front_image)
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    res = driver.go(front_image)
                    if abs(res) > 0.2:
                        res = 0
                    # driver.set_speed(10)
                    find_liangcao_flag = 0
                    if len(tasks) > 0 and score > 0.7 and tasks[0].name == 'liangcao':
                        side_image, liangcao_area, liangcao_center = draw_res(side_image, tasks)
                        find_liangcao_flag = 1
                    if abs(res) > 0.07 and zhuan_flag == 0:
                        val = 30 * res
                        if val < 10:
                            val = 10
                        driver.cart.move([val, val, val, val])
                        continue
                    elif abs(res) < 0.07 and zhuan_flag == 0:
                        driver.cart.move([0,0,0,0])
                        #time.sleep(1)
                        zhuan_flag = 1
                    if find_liangcao_flag == 1 and (abs(liangcao_center[1] - 385) < 5 and abs(liangcao_center[0] - 170) < 5) or i == 99:
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        cereal_motor.motor_rotate(11)
                        time.sleep(0.1)
                        cereal_motor.motor_rotate(0)
                        time.sleep(1)
                        cereal_pwm.servocontrol(-60, 50) # 控制舵机
                        time.sleep(2)
                        cereal_pwm.servocontrol(80, 50)
                        time.sleep(1)
                        cereal_motor.motor_rotate(-20)
                        time.sleep(0.1)
                        cereal_motor.motor_rotate(0)
                        '''cereal_motor.motor_rotate(20)
                        time.sleep(0.25)
                        cereal_motor.motor_rotate(0)
                        time.sleep(3)
                        cereal_motor.motor_rotate(-20)
                        time.sleep(0.12)
                        cereal_motor.motor_rotate(0)
                        time.sleep(1)'''
                        driver.cart.move([-20, -20, 20, 20])
                        time.sleep(0.4)
                        driver.cart.move([0, 0, 0, 0])
                        driver.set_speed(car_speed)
                        break
                    elif find_liangcao_flag == 1 and abs(liangcao_center[1] - 385) < 5 and liangcao_center[0] - 170 > 5:
                        driver.cart.move([-10, 10, -10, 10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_liangcao_flag == 1 and abs(liangcao_center[1] - 385) < 5 and liangcao_center[0] - 170 < -5:
                        driver.cart.move([10, -10, 10, -10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_liangcao_flag == 1 and liangcao_center[1] - 385 > 5 and abs(liangcao_center[0] - 170) < 5:
                        driver.cart.move([-10, -10, 10, 10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_liangcao_flag == 1 and liangcao_center[1] - 385 > 5 and liangcao_center[0] - 170 > 5:
                        driver.cart.move([-15, 0, 0, 15])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_liangcao_flag == 1 and liangcao_center[1] - 385 > 5 and liangcao_center[0] - 170 < -5:
                        driver.cart.move([0, -15, 15, 0])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_liangcao_flag == 1 and liangcao_center[1] - 385 < -5 and abs(liangcao_center[0] - 170) < 5:
                        driver.cart.move([10, 10, -10, -10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_liangcao_flag == 1 and liangcao_center[1] - 385 < -5 and liangcao_center[0] - 170 > 5:
                        driver.cart.move([0, 15, -15, 0])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_liangcao_flag == 1 and liangcao_center[1] - 385 < -5 and liangcao_center[0] - 170 < -5:
                        driver.cart.move([15, 0, 0, -15])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                #side_camera.stop()
                #side_camera.relase_camera()
        else:
            del (cereal_list[0])
            cereal_list.append(0)
        # 物块
        if len(signs) > 0 and signs[0].name == "lump" and area > 3500 and area < 12000:
            #print(area)
            del (lump_list[0])
            lump_list.append(1)
            if lump_list.count(1) > 2 and area > 4500:
                #driver.cart.steer(res)
                #time.sleep(0.1)
                driver.cart.Kx = lump_Kx
                angle_pid_flag = 0
                driver.cart.move([0, 0, 0, 0])
                td = TaskDetector()  # 侧边检测模型
                #side_camera = Camera(config.side_cam, [640, 480])
                #side_camera.start()
                camera_servo.servocontrol(124, 50)
                time.sleep(1)
                x_flag = 0
                zhuan_flag = 0
                # while True:
                nfind_rab_num = 0
                for i in range(100):
                    front_image = front_camera.read()
                    front_image = black_img(front_image)
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    res = driver.go(front_image)
                    find_rab_flag = 0
                    if len(tasks) > 0 and score > 0.6 and tasks[0].name == 'rab':
                        side_image, rab_area, rab_center = draw_res(side_image, tasks)
                        find_rab_flag = 1
                        nfind_rab_num = 0
                        #print(rab_center)
                    elif len(tasks) == 0 and zhuan_flag == 1:
                        driver.cart.move([10, -10, 10, -10])
                        time.sleep(0.1)
                        nfind_rab_num += 1
                    if nfind_rab_num >= 8:
                        driver.cart.move([20, 20, -20, -20])
                        time.sleep(0.4)
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        driver.set_speed(car_speed)
                        break
                    if abs(res) > 0.07 and zhuan_flag == 0:
                        val = 30 * res
                        if val < 10:
                            val = 10
                        driver.cart.move([-val, -val, -val, -val])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        continue
                    elif abs(res) < 0.07 and zhuan_flag == 0:
                        for _ in range(15):
                            driver.cart.move([15, -15, 15, -15])
                            time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                        #time.sleep(1)
                        zhuan_flag = 1
                    #print(find_rab_flag)
                    #if find_rab_flag == 0: #and (rab_center[0] == 0 or rab_center[1] == 0):
                        #driver.cart.move([0, 0, 0, 0])
                    if find_rab_flag == 1 and (abs(rab_center[1] - 360) < 5 and abs(rab_center[0] - 320) < 15 and zhuan_flag) or i == 99:
                        driver.cart.move([-15, 15, -15, 15])
                        time.sleep(0.8)
                        driver.cart.move([0, 0, 0, 0])
                        #time.sleep(1)
                        rab_pwm_servo.servocontrol(120, 50)
                        time.sleep(0.5)
                        rab_servo.servocontrol(80, 60)
                        time.sleep(1)
                        rab_pwm_servo.servocontrol(12, 50)
                        time.sleep(0.5)
                        rab_servo.servocontrol(15, 80)
                        time.sleep(1)
                        driver.cart.move([20, 20, -20, -20])
                        time.sleep(0.25)
                        driver.cart.move([0, 0, 0, 0])
                        flag = 0
                        driver.set_speed(car_speed)
                        #driver.cart.Kx = 0.95#1.05
                        break
                    elif find_rab_flag == 1 and abs(rab_center[1] - 360) < 5 and rab_center[0] - 320 < -15 and zhuan_flag:
                        driver.cart.move([-10, 10, -10, 10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_rab_flag == 1 and abs(rab_center[1] - 360) < 5 and rab_center[0] - 320 > 15 and zhuan_flag:
                        driver.cart.move([10, -10, 10, -10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_rab_flag == 1 and rab_center[1] - 360 < -5 and abs(rab_center[0] - 320) < 15 and zhuan_flag:
                        driver.cart.move([-10, -10, 10, 10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_rab_flag == 1 and rab_center[1] - 360 < -5 and rab_center[0] - 320 < -15 and zhuan_flag:
                        driver.cart.move([-15, 0, 0, 15])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_rab_flag == 1 and rab_center[1] - 360 < -5 and rab_center[0] - 320 > 15 and zhuan_flag:
                        driver.cart.move([0, -15, 15, 0])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_rab_flag == 1 and rab_center[1] - 360 > 5 and abs(rab_center[0] - 320) < 15 and zhuan_flag:
                        driver.cart.move([10, 10, -10, -10])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_rab_flag == 1 and rab_center[1] - 360 > 5 and rab_center[0] - 320 < -15 and zhuan_flag:
                        driver.cart.move([0, 15, -15, 0])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    elif find_rab_flag == 1 and rab_center[1] - 360 > 5 and rab_center[0] - 320 > 15 and zhuan_flag:
                        driver.cart.move([15, 0, 0, -15])
                        time.sleep(0.1)
                        driver.cart.move([0, 0, 0, 0])
                    '''if abs(rab_center[1] - 360) < 5:
                        x_flag = 1
                    elif rab_center[1] - 360 > 5:
                        driver.cart.move([15, 15, -15, -15])
                        #time.sleep(0.05)
                        #driver.cart.move([0, 0, 0, 0])
                    elif rab_center[1] - 360 < -5:
                        driver.cart.move([-15, -15, 15, 15])
                    if abs(rab_center[0] - 480) < 50 and x_flag == 1: #and rab_center[0] != 0:
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        rab_pwm_servo.servocontrol(120, 50)
                        time.sleep(1)
                        rab_servo.servocontrol(80, 60)
                        time.sleep(2)
                        rab_pwm_servo.servocontrol(12, 50)
                        time.sleep(1)
                        rab_servo.servocontrol(5, 80)
                        time.sleep(2)
                        driver.set_speed(car_speed)
                        #driver.cart.Kx = 0.9
                        break
                    elif rab_center[0] - 480 > 20:# and rab_center[0] != 0:
                        driver.cart.move([10, -10, 10, -10])
                    elif rab_center[0] - 480 < -20:# and rab_center[0] != 0:
                        driver.cart.move([-10, 10, -10, 10])'''
                #side_camera.stop()
                #side_camera.relase_camera()
        else:
            del (lump_list[0])
            lump_list.append(0)
        # 营地
        if len(signs) > 0 and signs[0].name == "campsite":
            del (campsite_list[0])
            campsite_list.append(1)
            if campsite_list.count(1) > 2 and area > 3500 and area < 24000 and abs(sign_center[1] - 320) < 50:
                time.sleep(0.4)
                driver.cart.move([0, 0, 0, 0])
                #time.sleep(1)
                td = TaskDetector()  # 侧边检测模型
                #side_camera = Camera(config.side_cam, [640, 480])
                #side_camera.start()
                camera_servo.servocontrol(-44, 50)
                time.sleep(1)
                for _ in range(10):
                    driver.cart.move([-50, -50, 50, 50])
                    time.sleep(0.1)
                driver.cart.move([0, 0, 0, 0])
                # while True:
                for i in range(100):
                    side_image = side_camera.read()
                    tasks, score = td.detect(side_image)
                    find_campsite_flag = 0
                    if len(tasks) > 0 and score > 0.7 and tasks[0].name == 'campsite':
                        side_image, campsite_area, campsite_center = draw_res(side_image, tasks)
                        find_campsite_flag = 1
                        print(campsite_center[1])
                    if (find_campsite_flag == 1 and abs(campsite_center[1] - 260) < 10) or i == 99:
                        driver.cart.Kx = campsite_Kx
                        angle_pid_flag = 0
                        driver.cart.move([0, 0, 0, 0])
                        #time.sleep(1)
                        for i in range(3):
                            led.lightcontrol(2, 255, 0, 0)
                            #time.sleep(0.1)
                            led.lightoff()
                            #time.sleep(0.1)
                        break
                    elif find_campsite_flag == 1 and campsite_center[1] - 260 > 10:
                        driver.cart.move([-20, -20, 20, 20])
                    elif find_campsite_flag == 1 and campsite_center[1] - 260 < -10:
                        driver.cart.move([20, 20, -20, -20])
                for _ in range(9):
                    driver.cart.move([50, 50, -50, -50])
                    time.sleep(0.1)
                '''for _ in range(14):
                    driver.cart.move([40, 40, -40, -40])
                    time.sleep(0.1)'''
                '''for _ in range(19):
                    driver.cart.move([30, 30, -30, -30])
                    time.sleep(0.1)'''
                #time.sleep(1.7)#1.6
                driver.cart.move([0, 0, 0, 0])
                time.sleep(1)
                #side_camera.stop()
                #side_camera.relase_camera()
        else:
            del (campsite_list[0])
            campsite_list.append(0)
        if save_video_flag == 1:
            save_video.write(front_image)
    front_camera.stop()
    #side_image.stop()
