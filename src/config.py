# -*- coding: utf-8 -*-
front_cam = 0
side_cam = 1
full_speed = 20
turn_speed = full_speed * 0.8
EMLARGE_RATIO = 1.2
model_prefix="/home/root/workspace/autostart/src/"
# mession config
# one more for background
MISSION_NUM = 9
mission_low = 0.3
mission_high = 0.75
MISS_DURATION = 200
mission_label_list = {
	0: "background",
	1: "daijun",
	2: "dingxiang",
	3: "dunhuang",
	4: "liangcao",
	5: "rab",
	6: "red_target",
	#7: "zhangpeng",
	7: "campsite"
}

# sign config
MAX_SIGN_PER_FRAME = 2
sign_list = {
	0: "background",
	1: "campsite",
	2: "cereal",
	3: "lump",
	4: "target",
	5: "tower",
	6: "enjoy"
}
# cruise model
cruise = {
	"model":model_prefix + "models/black_img720"
}
# sign models
sign = {
	"model": model_prefix + "models/sign707",
	"threshold": 0.4,
	"label_list": sign_list,
	# label = 0 is background
	"class_num": 7
}
# task model
task = {
	"model":model_prefix + "models/task715",
	"threshold":0.6,
	"label_list":mission_label_list,
	#"class_num": 6
}



# sign_threshold = 0.3;
# task_threshold = 0.4;
