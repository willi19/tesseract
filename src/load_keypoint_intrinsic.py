import os
import cv2

import cv2
import os
import numpy as np
import json

def load_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def load_checkpoint(root, debug=True):
    file_list = os.listdir(os.path.join(root, 'checkpoint'))
    keypoint_list = {}
    objpoint_list = {}
    objp = np.zeros((10*7,3), np.float32)
    objp[:,:2] = np.mgrid[0:7,0:10].T.reshape(-1,2)
    for fname in file_list:
        scene_list = os.listdir(os.path.join(root, 'checkpoint', fname))
        for scene_name in scene_list:
            img_list = os.listdir(os.path.join(root, 'checkpoint', fname, scene_name))
            for img_name in img_list:
                keypoint = np.load(os.path.join(root, 'checkpoint', fname, scene_name, img_name))
                if img_name[:-4] not in keypoint_list:
                    keypoint_list[img_name[:-4]] = [keypoint]
                    objpoint_list[img_name[:-4]] = [objp]
                else:
                    keypoint_list[img_name[:-4]].append(keypoint)
                    objpoint_list[img_name[:-4]].append(objp)
    return keypoint_list, objpoint_list

if __name__ == "__main__":
    keypoint_list, objpoint_list = load_checkpoint('data', debug=False)
    os.makedirs('data/intrinsic', exist_ok=True)
    for cam_name, kypt in keypoint_list.items():
        data = load_json(os.path.join('data', 'intrinsic_kinect', '0103011524','json',cam_name + '.json'))
        for camparam in data['CalibrationInformation']['Cameras']:
            if camparam['Purpose'] == 'CALIBRATION_CameraPurposePhotoVideo':
                param = camparam['Intrinsics']['ModelParameters']
        os.makedirs(os.path.join('data/intrinsic', cam_name), exist_ok=True)

        x = 4096
        y = 3072

        cx = param[0] * x
        cy = param[1] * y
        fx = param[2] * x
        fy = param[3] * y
        k1 = param[4]
        k2 = param[5]
        k3 = param[6]
        k4 = param[7]
        k5 = param[8]
        k6 = param[9]
        p2 = param[12]
        p1 = param[13]
        
        print(cam_name, "--------------------")
        
        #ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoint_list[cam_name], kypt, (4096, 3072), None, None, flags = cv2.CALIB_RATIONAL_MODEL)
        #print(mtx[0][0], mtx[1][1], mtx[0][2], mtx[1][2], dist[0][0], dist[0][1], dist[0][4], dist[0][5], dist[0][6], dist[0][7], dist[0][2], dist[0][3])
        
        cam_mtx = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
        dist = np.array([[k1, k2, p1, p2, k3, k4, k5, k6]])

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoint_list[cam_name], kypt, (4096, 3072), None, None, flags = cv2.CALIB_RATIONAL_MODEL)
        print("keypoint : ", ret)

        np.save(os.path.join('data/intrinsic', cam_name, 'mtx'), mtx)
        np.save(os.path.join('data/intrinsic', cam_name, 'dist'), dist)

        cam_mtx = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
        dist = np.array([[k1, k2, p1, p2, k3, k4, k5, k6]])

        flags = cv2.CALIB_RATIONAL_MODEL | cv2.CALIB_FIX_K1 | cv2.CALIB_FIX_K2 | cv2.CALIB_FIX_K3 | cv2.CALIB_FIX_K4 | cv2.CALIB_FIX_K5 | cv2.CALIB_FIX_K6 | cv2.CALIB_FIX_FOCAL_LENGTH | cv2.CALIB_FIX_PRINCIPAL_POINT | cv2.CALIB_USE_INTRINSIC_GUESS | cv2.CALIB_FIX_TANGENT_DIST
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoint_list[cam_name], kypt, (4096, 3072), cam_mtx, dist, flags = flags)
        print("device : ", ret)
        
        