import time
import struct
from serial_port import serial_connection
from camera import Camera
import config
serial = serial_connection

class Button:
    def __init__(self, port, buttonstr):
        self.state = False
        self.port = port
        self.buttonstr = buttonstr
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 05 00 01 E1 {} 01 0A'.format(port_str))

    def clicked(self):
        serial.write(self.cmd_data)
        response = serial.read()
        buttonclick="no"
        if len(response) == 9 and  response[5]==0xE1 and response[6]==self.port:
            button_byte=response[3:5]+bytes.fromhex('00 00')
            button_value=struct.unpack('<i', struct.pack('4B', *(button_byte)))[0]
            # print("%x"%button_value)
            if button_value>=0x1f1 and button_value<=0x20f:
                buttonclick="UP"
            elif button_value>=0x330 and button_value<=0x33f:
                buttonclick = "LEFT"
            elif button_value>=0x2ff and button_value<=0x30f:
                buttonclick = "DOWN"
            elif button_value>=0x2a0 and button_value<=0x2af:
                buttonclick = "RIGHT"
            else:
                buttonclick
        return self.buttonstr==buttonclick

class LimitSwitch:
    def __init__(self, port):
        self.state = False;
        self.port = port;
        self.state = True;
        port_str = '{:02x}'.format(port)
        # print (port_str)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 DD {} 0A'.format(port_str))

    # print('77 68 04 00 01 DD {} 0A'.format(port_str))

    def clicked(self):
        serial.write(self.cmd_data);
        response = serial.read();  # 77 68 01 00 0D 0A
        if len(response) < 8 or response[4] != 0xDD or response[5] != self.port \
                or response[2] != 0x01:
            return False;
        state = response[3] == 0x01
        # print("state=",state)
        # print("elf.state=", self.state)
        clicked = False
        if state == True and self.state == True and clicked == False:
            clicked = True;
        if state == False and self.state == True and clicked == True:
            clicked = False
        # print('clicked=',clicked)
        return clicked


class UltrasonicSensor():
    def __init__(self, port):
        self.port = port
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 D1 {} 0A'.format(port_str))

    def read(self):
        serial.write(self.cmd_data)
        # time.sleep(0.01)
        return_data = serial.read()
        if len(return_data)<11 or return_data[7] != 0xD1 or return_data[8] != self.port:
            return None
        # print(return_data.hex())
        return_data_ultrasonic = return_data[3:7]
        ultrasonic_sensor = struct.unpack('<f', struct.pack('4B', *(return_data_ultrasonic)))[0]
        # print(ultrasonic_sensor)
        return int(ultrasonic_sensor)


class Servo:
    def __init__(self, ID):
        self.ID = ID
        self.ID_str = '{:02x}'.format(ID)
        #print(self.ID_str)

    def servocontrol(self, angle, speed):
        cmd_servo_data = bytes.fromhex('77 68 06 00 02 36') + bytes.fromhex(self.ID_str) + speed.to_bytes(1,
                                                                                                            byteorder='big', \
                                                                                                            signed=True) + angle.to_bytes(1, byteorder='big', signed=True) + bytes.fromhex('0A')

        # for i in range(0,2):
        #print(cmd_servo_data)
        serial.write(cmd_servo_data)
        #     time.sleep(0.3)

class Servo_pwm:
    def __init__(self, ID):
        self.ID = ID
        self.ID_str = '{:02x}'.format(ID)

    def servocontrol(self, angle, speed):
        cmd_servo_data = bytes.fromhex('77 68 06 00 02 0B') + bytes.fromhex(self.ID_str) + speed.to_bytes(1,
                                                                                                            byteorder='big', \
                                                                                                            signed=True) + angle.to_bytes(1, byteorder='big', signed=True) + bytes.fromhex('0A')
        # for i in range(0,2):
        #print(cmd_servo_data)
        serial.write(cmd_servo_data)
        # time.sleep(0.3)

class Light:
    def __init__(self, port):
        self.port = port
        self.port_str = '{:02x}'.format(port)

    def lightcontrol(self, which, Red, Green, Blue):  # 0代表全亮，其他值对应灯珠亮，1~4
        which_str = '{:02x}'.format(which)
        Red_str = '{:02x}'.format(Red)
        Green_str = '{:02x}'.format(Green)
        Blue_str = '{:02x}'.format(Blue)
        cmd_servo_data = bytes.fromhex('77 68 08 00 02 3B {} {} {} {} {} 0A'.format(self.port_str, which_str, Red_str \
                                                                                    , Green_str, Blue_str))
        serial.write(cmd_servo_data)



    def lightoff(self):
        cmd_servo_data1 = bytes.fromhex('77 68 08 00 02 3B 02 00 00 00 00 0A')
        cmd_servo_data2 = bytes.fromhex('77 68 08 00 02 3B 03 00 00 00 00 0A')
        cmd_servo_data = cmd_servo_data1 + cmd_servo_data2
        serial.write(cmd_servo_data)


class Motor_rotate:
    def __init__(self, port):
        self.port = port
        self.port_str = '{:02x}'.format(port)

    def motor_rotate(self, speed):
        cmd_servo_data = bytes.fromhex('77 68 06 00 02 0C 02') + bytes.fromhex(self.port_str) + \
                         speed.to_bytes(1, byteorder='big', signed=True) + bytes.fromhex('0A')
        serial.write(cmd_servo_data)


class Infrared_value:
    def __init__(self, port):
        port_str = '{:02x}'.format(port)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 D4 {} 0A'.format(port_str))

    def read(self):
        serial.write(self.cmd_data)
        return_data = serial.read()
        if return_data[2] != 0x04:
            return None
        if return_data[3] == 0x0a:
            return None
        # print("**********************************")
        # print("return_data[3]=%x" % return_data[3])
        # print(type(return_data[3]))
        # print("return_data[4]=%x" % return_data[4])
        # print("return_data[5]=%x" % return_data[5])
        # print("return_data[6]=%x" % return_data[6])
        # print(return_data.hex())
        return_data_infrared = return_data[3:7]
        print(return_data_infrared)
        infrared_sensor = struct.unpack('<i', struct.pack('4B', *(return_data_infrared)))[0]
        # print(ultrasonic_sensor)
        return infrared_sensor


class Buzzer:
    def __init__(self):
        self.cmd_data = bytes.fromhex('77 68 06 00 02 3D 03 02 0A')

    def rings(self):
        serial.write(self.cmd_data)
class Magneto_sensor:
    def __init__(self,port):
        self.port=port
        port_str = '{:02x}'.format(self.port)
        self.cmd_data = bytes.fromhex('77 68 04 00 01 CF {} 0A'.format(port_str))

    def read(self):
        serial.write(self.cmd_data)
        return_data = serial.read()
        # print("return_data=",return_data[8])
        if len(return_data) < 11 or return_data[7] != 0xCF or return_data[8] != self.port:
            return None
        # print(return_data.hex())
        return_data = return_data[3:7]
        mag_sensor = struct.unpack('<i', struct.pack('4B', *(return_data)))[0]
        # print(ultrasonic_sensor)
        return int(mag_sensor)
class Test:
    pass
def serial_keep():
    while True:
        serial.write(bytes.fromhex('77 68 06'))
        time.sleep(1.0)

if __name__ == '__main__':
    front_camera = Camera(config.front_cam, [640, 480])
    # side_camera = Camera(config.side_cam, [640, 480])
    # time.sleep(1)
    front_camera.start()
    time.sleep(3)
    motor=Motor_rotate(1)
    removemotor=Motor_rotate(2)
    rab_servo = Servo(2)
    camera_servo = Servo(1)
    rab_pwm_servo = Servo_pwm(2)
    time.sleep(2)
    #rab_servo.servocontrol(10, 50)
    #time.sleep(3)
    side_camera = Camera(config.side_cam, [640, 480])
    # side_camera = Camera(config.side_cam, [640, 480])
    # time.sleep(1)
    side_camera.start()
    time.sleep(3)
    cereal_motor = Motor_rotate(1)
    #servo2=Servo_pwm(4)
    # side_camera.start()
    # time.sleep(1)
    # #拉起线程
    #servo2.servocontrol(-2, 80)
    #time.sleep(2)
    #time.sleep(0.5)
    #threading.Thread(target=serial.write(bytes.fromhex('77 68 06')), args=()).start()
    #threading.Thread(target=serial.write(bytes.fromhex('77 68 06')), args=()).start()
    #threading.Thread(target=serial_keep(), args=()).start()
    #motor.motor_rotate(20)
    #time.sleep(0.21)
    #motor.motor_rotate(-25)
    #time.sleep(0.5)
    #motor.motor_rotate(0)
    #rab_pwm_servo.servocontrol(12, 50)
    #time.sleep(2)
    removemotor.motor_rotate(-40)
    time.sleep(0.5)
    removemotor.motor_rotate(40)
    time.sleep(0.5)
    removemotor.motor_rotate(0)
    while True:
        print('a')
        '''rab_pwm_servo.servocontrol(120, 50)
        time.sleep(1)
        rab_servo.servocontrol(73, 60)
        time.sleep(1)
        rab_pwm_servo.servocontrol(12, 50)
        time.sleep(1)
        rab_servo.servocontrol(5, 80)
        time.sleep(2)'''

        '''rab_pwm_servo.servocontrol(120, 50)
        time.sleep(1)
        rab_servo.servocontrol(80, 60)
        time.sleep(2)
        rab_pwm_servo.servocontrol(12, 50)
        time.sleep(1)
        rab_servo.servocontrol(5, 80)
        time.sleep(2)'''
        '''rab_servo.servocontrol(5, 80)
        time.sleep(1)
        camera_servo.servocontrol(20, 80)
        time.sleep(1)
        rab_servo.servocontrol(80, 80)
        time.sleep(1)
        camera_servo.servocontrol(60, 80)
        time.sleep(3)'''
        '''cereal_motor.motor_rotate(10)
        time.sleep(0.03)
        cereal_motor.motor_rotate(0)
        time.sleep(3)
        cereal_motor.motor_rotate(-30)
        time.sleep(0.01)
        cereal_motor.motor_rotate(0)
        time.sleep(3)'''
        # #拉起线程
        #servo2.servocontrol(-2, 80)
        #time.sleep(2)
        '''servo3.servocontrol(124, 50)
        time.sleep(2)
        #servo1.servocontrol(55,50)
        servo3.servocontrol(-40, 50)
        time.sleep(2)'''
        '''motor.motor_rotate(40)
        time.sleep(5)
        motor.motor_rotate(-40)
        time.sleep(5)'''
        #motor.motor_rotate(-15)
        #time.sleep(1)
        '''led_blue.lightcontrol(2, 255, 0, 0)
        time.sleep(5)
        led_blue.lightcontrol(2, 0, 255, 0)
        time.sleep(5)'''
    front_camera.stop()

