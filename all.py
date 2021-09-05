import os
import cv2
import time
from cruiser import Cruiser
from detectors import SignDetector, TaskDetector
from camera import Camera
import config
from driver import Driver
from widgets import Button, Light
from widgets_servo_test import Servo, Servo_pwm, Motor_rotate

driver = Driver()
cruiser = Cruiser()
led = Light(2)
image_extensions = [".png", ".jpg", ".jpeg"]
# 程序开启运行开关
start_button = Button(1, "UP")
# 程序关闭开关
stop_button = Button(1, "DOWN")
# 保存视频标志位
save_video_flag = 0
# 保存图片标注位
save_image_flag = 0
image_num = 2414
image_dir = "/run/media/sda1/front629"


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

tower_list = [0, 0, 0, 0, 0]
target_list = [0, 0, 0, 0, 0]
cereal_list = [0, 0, 0, 0, 0]
lump_list = [0, 0, 0, 0, 0]
campsite_list = [0, 0, 0, 0, 0]
if __name__ == "__main__":
    ################
    # 摄像头初始化
    front_camera = Camera(config.front_cam, [640, 480])
    # side_camera = Camera(config.side_cam, [640, 480])
    front_camera.start()
    # side_camera.start()
    ################
    # 舵机，电机初始化
    camera_servo = Servo(1)  # 摄像头舵机
    # time.sleep(2)
    #camera_servo.servocontrol(124, 50)
    dunhuang_servo = Servo_pwm(3)  # 敦煌旗帜
    #dunhuang_servo.servocontrol(-15, 50)  # 初始化
    daijun_servo = Servo_pwm(4)  # 代郡旗帜
    daijun_servo.servocontrol(-5, 80)
    dingxiagn_servo = Servo_pwm(5)  # 定襄旗帜
    dingxiagn_servo.servocontrol(-1, 80)
    rab_servo = Servo(2) #夹块智能舵机
    rab_pwm_servo = Servo_pwm(6) #夹块舵机
    # time.sleep(0)
    target_motor = Motor_rotate(2)
    cereal_motor = Motor_rotate(1)
    # 检测模型
    sd = SignDetector()  # 地标检测模型
    # td = TaskDetector() #侧边检测模型
    time.sleep(2)
    ################
    #巡航参数
    #driver.set_speed_kx = 30 #麦轮分解系数
    driver.set_speed(35) #35#基础速度
    driver.cart.Kx = 0.9 #0.9转向系数
    #############
    #保存视频
    if save_video_flag == 1:
        save_video = cv2.VideoWriter('/run/media/sda1/video/output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 6.0, (640, 480))

    '''while True:
        if start_button.clicked():
            time.sleep(0.8)
            break
        print("Wait for start!")'''
    while True:
        front_image = front_camera.read()
        #side_image = side_camera.read()
        if save_image_flag == 1:
            path = "{}/{}.jpg".format(image_dir, image_num)
            cv2.imwrite(path, front_image)
            cv2.waitKey(100)
            print(image_num)
            image_num += 1
            continue
        res = driver.go(front_image)
        #print(res)
        #driver.cart.steer(res)
        signs, index = sd.detect(front_image)
        sign_center = [0, 0]
        if len(signs) > 0:
            frame, area, sign_center = draw_res(front_image, signs)
            #print(area)
            print(signs[0].name)
            if signs[0].name == 'campsite':
                driver.cart.Kx = 1.6
            '''if signs[0].name == 'cereal': #and area > 3000:
                res2 = (sign_center[0] - 280) / 100
                res3 = res + res2
                driver.cart.steer(res3)
                driver.set_speed(15)
            else:
                driver.cart.steer(res)
                driver.set_speed(35)'''
        else:
            driver.cart.steer(res)
        #城堡识别并举旗
        if len(signs) > 0 and signs[0].name == "tower":
            del (tower_list[0])
            tower_list.append(1)
            #print(target_list)
            if tower_list.count(1) > 2 and sign_center[1] > 350 and abs(sign_center[0] - 320) < 75:#and abs(res) < 0.1 and area > 5500:
                #time.sleep(0.65)
                time.sleep(0.45)
                driver.cart.move([0, 0, 0, 0])
                td = TaskDetector()  # 侧边检测模型
                side_camera = Camera(config.side_cam, [640, 480])
                side_camera.start()
                #side_image = side_camera.read()
                camera_servo.servocontrol(124, 50)
                time.sleep(2)
                find_tower_frame_num = 0
                find_tower_flag = 0
                tasks = []
                for i in range(10):
                    side_image = side_camera.read()
                    tasks = td.detect(side_image)
                    draw_res(side_image, tasks)
                    print(i, tasks)
                    if len(tasks) > 0:
                        find_tower_frame_num += 1
                        print(tasks[0].name)
                    if find_tower_frame_num >= 5:
                        find_tower_flag = 1
                        break
                    print(find_tower_frame_num)
                if find_tower_flag == 0:
                    find_tower_frame_num = 0
                    camera_servo.servocontrol(-40, 50)
                    time.sleep(1)
                    for i in range(10):
                        side_image = side_camera.read()
                        tasks = td.detect(side_image)
                        #draw_res(side_image, tasks)
                        #print(i, tasks)
                        if len(tasks) > 0:
                            find_tower_frame_num += 1
                            #print(tasks[0].name)
                        if find_tower_frame_num >= 5:
                            find_tower_flag = 1
                            break
                        print(find_tower_frame_num)
                #print(tasks[0].name)
                '''if len(tasks) == 0:
                    driver.cart.move([10, 10, 10, 10])
                    time.sleep(2)
                    camera_servo.servocontrol(124, 50)
                    time.sleep(1)
                    for i in range(10):
                        side_image = side_camera.read()
                        tasks = td.detect(side_image)
                        draw_res(side_image, tasks)
                        print(i, tasks)
                        if len(tasks) > 0:
                            find_tower_frame_num += 1
                            print(tasks[0].name)
                        if find_tower_frame_num >= 5:
                            find_tower_flag = 1
                            break
                        print(find_tower_frame_num)
                    if find_tower_flag == 0:
                        find_tower_frame_num = 0
                        camera_servo.servocontrol(-40, 50)
                        time.sleep(1)
                        for i in range(10):
                            side_image = side_camera.read()
                            tasks = td.detect(side_image)
                            # draw_res(side_image, tasks)
                            # print(i, tasks)
                            if len(tasks) > 0:
                                find_tower_frame_num += 1
                                # print(tasks[0].name)
                            if find_tower_frame_num >= 5:
                                find_tower_flag = 1
                                break
                            print(find_tower_frame_num)
                if len(tasks) == 0:
                    driver.cart.move([-10, -10, -10, -10])
                    time.sleep(4)
                    for i in range(10):
                        side_image = side_camera.read()
                        tasks = td.detect(side_image)
                        draw_res(side_image, tasks)
                        print(i, tasks)
                        if len(tasks) > 0:
                            find_tower_frame_num += 1
                            print(tasks[0].name)
                        if find_tower_frame_num >= 5:
                            find_tower_flag = 1
                            break
                        print(find_tower_frame_num)
                    if find_tower_flag == 0:
                        find_tower_frame_num = 0
                        camera_servo.servocontrol(-40, 50)
                        time.sleep(1)
                        for i in range(10):
                            side_image = side_camera.read()
                            tasks = td.detect(side_image)
                            # draw_res(side_image, tasks)
                            # print(i, tasks)
                            if len(tasks) > 0:
                                find_tower_frame_num += 1
                                # print(tasks[0].name)
                            if find_tower_frame_num >= 5:
                                find_tower_flag = 1
                                break
                            print(find_tower_frame_num)
                print(tasks)'''
                if len(tasks) > 0 and tasks[0].name == 'dunhuang':
                    print(tasks[0].name)
                    dunhuang_servo.servocontrol(85, 50)
                    rab_pwm_servo.servocontrol(12, 50)
                    time.sleep(1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        time.sleep(1)
                        led.lightoff()
                        time.sleep(1)
                    #time.sleep(5)
                    dunhuang_servo.servocontrol(-15, 50)
                    rab_pwm_servo.servocontrol(12, 50)
                    time.sleep(1)
                elif len(tasks) > 0 and tasks[0].name == "daijun":
                    print(tasks[0].name)
                    daijun_servo.servocontrol(45, 80)
                    rab_pwm_servo.servocontrol(12, 50)
                    time.sleep(1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        time.sleep(1)
                        led.lightoff()
                        time.sleep(1)
                    #time.sleep(5)
                    daijun_servo.servocontrol(-5, 50)
                    rab_pwm_servo.servocontrol(12, 50)
                    time.sleep(1)
                elif len(tasks) > 0 and tasks[0].name == "dingxiang":
                    print(tasks[0].name)
                    dingxiagn_servo.servocontrol(45, 80)
                    time.sleep(1)
                    for i in range(3):
                        led.lightcontrol(2, 0, 255, 0)
                        print('daddddddd')
                        time.sleep(1)
                        led.lightoff()
                        time.sleep(1)
                    #time.sleep(5)
                    dingxiagn_servo.servocontrol(-1, 80)
                    rab_pwm_servo.servocontrol(12, 50)
                    time.sleep(1)
                #draw_res(side_image, tasks)
                side_camera.stop()
                side_camera.relase_camera()
        else:
            del (tower_list[0])
            tower_list.append(0)
            #print(target_list)
        if len(signs) > 0 and signs[0].name == "target":
            del (target_list[0])
            target_list.append(1)
            if target_list.count(1) > 1 and sign_center[1] > 330 and abs(sign_center[0] - 320) < 75: #and abs(res) < 0.1 and area > 5500:
                # time.sleep(0.65)
                time.sleep(0.45)
                driver.cart.move([0, 0, 0, 0])
                #driver.set_speed(0)
                td = TaskDetector()  # 侧边检测模型
                side_camera = Camera(config.side_cam, [640, 480])
                side_camera.start()
                camera_servo.servocontrol(-40, 50)
                time.sleep(2)
                nfind_target_num = 0
                while True:
                    side_image = side_camera.read()
                    tasks = td.detect(side_image)
                    #driver.set_speed(10)
                    side_image, target_area, target_center = draw_res(side_image, tasks)
                    print("area", target_area)
                    print("center", target_center)
                    if len(tasks) == 0:
                        nfind_target_num += 1
                    if nfind_target_num >= 10:
                        nfind_target_num = 0
                        driver.set_speed(35)
                        break
                    if abs(target_center[0] - 288) < 5 and target_center[0] != 0:
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        target_motor.motor_rotate(-40)
                        time.sleep(1.6)
                        target_motor.motor_rotate(0)
                        time.sleep(1)
                        target_motor.motor_rotate(40)
                        time.sleep(1.6)
                        target_motor.motor_rotate(0)
                        time.sleep(1)
                        driver.set_speed(35)
                        break
                    elif target_center[0] - 288 > 5 and target_center[0] != 0:
                        driver.cart.move([-10, -10, -10, -10])
                    elif target_center[0] - 288 < -5 and target_center[0] != 0:
                        driver.cart.move([10, 10, 10, 10])
                side_camera.stop()
                side_camera.relase_camera()
        else:
            del (target_list[0])
            target_list.append(0)
        if len(signs) > 0 and signs[0].name == "cereal":
            del (cereal_list[0])
            cereal_list.append(1)
            if cereal_list.count(1) > 1 and abs(res) < 0.1 and area > 4500: #4500
                time.sleep(0.5)
                driver.cart.move([0, 0, 0, 0])
                time.sleep(1)
                td = TaskDetector()  # 侧边检测模型
                side_camera = Camera(config.side_cam, [640, 480])
                side_camera.start()
                camera_servo.servocontrol(-40, 50)
                time.sleep(2)
                nfind_cereal_num = 0
                while True:
                    side_image = side_camera.read()
                    tasks = td.detect(side_image)
                    # driver.set_speed(10)
                    side_image, liangcao_area, liangcao_center = draw_res(side_image, tasks)
                    print("area", liangcao_area)
                    print("center", liangcao_center)
                    if len(tasks) == 0:
                        nfind_cereal_num += 1
                    if nfind_cereal_num >= 10:
                        nfind_cereal_num = 0
                        driver.set_speed(35)
                        break
                    if abs(liangcao_center[0] - 195) < 10 and liangcao_center[0] != 0:
                        driver.cart.move([0, 0, 0, 0])
                        time.sleep(1)
                        cereal_motor.motor_rotate(20)
                        time.sleep(0.21)
                        cereal_motor.motor_rotate(0)
                        time.sleep(1)
                        '''cereal_motor.motor_rotate(-20)
                        time.sleep(0.21)
                        cereal_motor.motor_rotate(0)
                        time.sleep(1)'''
                        driver.set_speed(35)
                        break
                    elif liangcao_center[0] - 195 > 10 and liangcao_center[0] != 0:
                        driver.cart.move([-10, -10, -10, -10])
                    elif liangcao_center[0] - 195 < -10 and liangcao_center[0] != 0:
                        driver.cart.move([10, 10, 10, 10])
                '''cereal_motor.motor_rotate(20)
                time.sleep(0.21)
                cereal_motor.motor_rotate(0)
                time.sleep(1)'''
                side_camera.stop()
                side_camera.relase_camera()
        else:
            del (cereal_list[0])
            cereal_list.append(0)
        if len(signs) > 0 and signs[0].name == "lump":
            del (lump_list[0])
            lump_list.append(1)
            if lump_list.count(1) > 2 and area > 4500:
                driver.cart.steer(res)
                time.sleep(0.6)
                driver.cart.move([0, 0, 0, 0])
                td = TaskDetector()  # 侧边检测模型
                side_camera = Camera(config.side_cam, [640, 480])
                side_camera.start()
                camera_servo.servocontrol(124, 50)
                time.sleep(1)
                nfind_lump_num = 0
                while True:
                    side_image = side_camera.read()
                    tasks = td.detect(side_image)
                    side_image, rab_area, rab_center = draw_res(side_image, tasks)
                    if len(tasks) == 0:
                        nfind_lump_num += 1
                    if nfind_lump_num > 10:
                        nfind_lump_num = 0
                        driver.set_speed(35)
                        driver.cart.Kx = 0.9
                        break
                    if abs(rab_center[0] - 450) < 50 and rab_center[0] != 0:
                        driver.cart.move([0, 0, 0, 0])
                        rab_pwm_servo.servocontrol(120, 50)
                        time.sleep(1)
                        rab_servo.servocontrol(80, 60)
                        time.sleep(2)
                        rab_pwm_servo.servocontrol(12, 50)
                        time.sleep(1)
                        rab_servo.servocontrol(5, 80)
                        time.sleep(2)
                        driver.set_speed(35)
                        driver.cart.Kx = 0.9
                        break
                    elif rab_center[0] - 420 > 20 and rab_center[0] != 0:
                        driver.cart.move([15, 15, 15, 15])
                    elif rab_center[0] - 420 < -20 and rab_center[0] != 0:
                        driver.cart.move([-15, -15, -15, -15])
                side_camera.stop()
                side_camera.relase_camera()
        else:
            del (lump_list[0])
            lump_list.append(0)
        ''''if len(signs) > 0 and signs[0].name == "campsite":
            del (campsite_list[0])
            campsite_list.append(1)
            if campsite_list.count(1) > 2 and area > 4500:
                time.sleep(1.9)
                driver.cart.move([0, 0, 0, 0])
                time.sleep(5)
                driver.cart.move([-10, -15, -10, -15])
                time.sleep(4.2)
                driver.cart.move([-10, -10, -10, -10])
                time.sleep(3.2)
                driver.cart.move([0, 0, 0, 0])
                time.sleep(10)
        else:
            del (campsite_list[0])
            campsite_list.append(0)'''
        if save_video_flag == 1:
            save_video.write(front_image)
    front_camera.stop()
    #side_image.stop()
