import sys
import cv2
import os
import numpy as np
np.set_printoptions(precision=3)

# import openpose
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

params = dict()
# model path
params["model_folder"] = "models/"
# body setting
params["body"] = 1
params["render_pose"] = 0
params["render_threshold"] = 0.15  # 0.05
# params["3d"] = True
# params['number_people_max'] = 1
# hand setting
params["hand"] = True
params["hand_render"] = 1
params["hand_detector"] = 0
params["hand_scale_number"] = 1
params["hand_scale_range"] = 0.4
params["hand_render_threshold"] = 0.2  # 0.2
# face setting
params["face"] = False
params["face_render"] = 0
params["face_detector"] = 0
params["face_render_threshold"] = 0.4  # 0.4


# Init openpose wrapper
opWrapper = op.WrapperPython()
opWrapper.configure(params)
opWrapper.start()
datum = op.Datum()

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
while True:
    ret, frame = cap.read()
    if frame is not None:
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])
        # Output keypoints
        print("Body keypoints: \n" + str(datum.poseKeypoints))
        print("Left hand keypoints: \n" + str(datum.handKeypoints[0]))
        print("Right hand keypoints: \n" + str(datum.handKeypoints[1]))
        # Display Image
        out_img = datum.cvOutputData
        cv2.imshow("OpenPose", out_img)
        if cv2.waitKey(1) == ord('q'):
            break
