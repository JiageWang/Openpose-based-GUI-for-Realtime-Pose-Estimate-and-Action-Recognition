import sys
import cv2
import os
import argparse
import numpy as np
np.set_printoptions(precision=3)

# 导入openpose路径
dir_path = os.path.dirname(os.path.realpath(__file__))
try:
    sys.path.append(dir_path + '/openpose')
    os.environ['PATH'] = os.environ['PATH'] + ';' + dir_path + '/openpose;' + dir_path + '/3rdparty;'
    import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. \
            Did you enable `BUILD_PYTHON` in CMake and \
            have this Python script in the right folder?')
    raise e

# 自定义参数，具体参见openpose/flags.hpp
params = dict()
# 模型路径
params["model_folder"] = "models/"
# body相关参数
params["body"] = 1
params["render_pose"] = 0
params["render_threshold"] = 0.2  # 0.05
# hand相关参数
params["hand"] = True
params["hand_render"] = 1
params["hand_detector"] = 0
params["hand_scale_number"] = 1
params["hand_scale_range"] = 0.4
params["hand_render_threshold"] = 0.2  # 0.2
# face相关参数
params["face"] = False
params["face_render"] = 0
params["face_detector"] = 0
params["face_render_threshold"] = 0.4  # 0.4

# 命令行参数
parser = argparse.ArgumentParser()
parser.add_argument("--image_path", default="../../../examples/media/COCO_val2014_000000000192.jpg",
                    help="Process an image. Read all standard formats (jpg, png, bmp, etc.).")
args = parser.parse_known_args()

for i in range(0, len(args[1])):
    curr_item = args[1][i]
    if i != len(args[1]) - 1:
        next_item = args[1][i + 1]
    else:
        next_item = "1"
    if "--" in curr_item and "--" in next_item:
        key = curr_item.replace('-', '')
        if key not in params:
            params[key] = "1"
    elif "--" in curr_item and "--" not in next_item:
        key = curr_item.replace('-', '')
        if key not in params:
            params[key] = next_item

# 新建openpose的封装
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
while True:
    ret, frame = cap.read()
    if frame is not None:
        datum = op.Datum()
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])

        # Display Image
        print("Body keypoints: \n" + str(datum.poseKeypoints))
        print("Left hand keypoints: \n" + str(datum.handKeypoints[0]))
        print("Right hand keypoints: \n" + str(datum.handKeypoints[1]))

        cv2.imshow("OpenPose", datum.cvOutputData)
        if cv2.waitKey(1) == ord('q'):
            break
