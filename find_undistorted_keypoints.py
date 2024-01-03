import cv2
import os
import numpy as np
import shutil
import json

def load_intrinsic(path):
    mtx = np.load(os.path.join(path, "mtx.npy"))
    dist = np.load(os.path.join(path, "dist.npy"))
    return load_undistort_map(mtx, dist)
    return mtx, dist

def load_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def load_kinect_intrinsic(path):
    data = load_json(path)
    for camparam in data['CalibrationInformation']['Cameras']:
        if camparam['Purpose'] == 'CALIBRATION_CameraPurposePhotoVideo':
            param = camparam['Intrinsics']['ModelParameters']
            x = camparam['SensorWidth']
            y = camparam['SensorHeight']
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
            
            cam_mtx = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])
            dist = np.array([[k1, k2, p1, p2, k3, k4, k5, k6]])
            return load_undistort_map(cam_mtx, dist) 
            return mapx, mapy

def load_undistort_map(mtx, dist):
    map1, map2 = cv2.initUndistortRectifyMap(mtx, dist, None, None, (4096, 3072), cv2.CV_32FC1)
    return map1, map2

def find_keypoints_undistort_scene(source_dir, dest_dir, intrinsic_dict, debug=False):
    img_list = os.listdir(source_dir)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    for img_name in img_list:
        cam_name = img_name[:-4]
        img = cv2.imread(os.path.join(source_dir, img_name))
        mapx, mapy = intrinsic_dict[cam_name]
        img = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (7, 10), None)

        if ret == True:
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            np.save(os.path.join(dest_dir, cam_name), corners2)
            corners = corners[:,0,:]
            if debug:
                for i, pt in enumerate(corners):
                    img = cv2.circle(img, (int(pt[0]), int(pt[1])), 4, (0,0,255) if i <35 else (255,0,0), -1)

                img = cv2.resize(img, (img.shape[1]//4, img.shape[0]//4))
                cv2.imshow('img', img)
                cv2.waitKey(0)
    return

def find_checkpoint_root(root, debug=True):
    os.makedirs(os.path.join(root, 'checkpoint_undistort'), exist_ok=True)
    os.makedirs(os.path.join(root, 'checkpoint_kinect_undistort'), exist_ok=True)

    file_list = os.listdir(os.path.join(root, 'extrinsic'))
    
    cam_list = os.listdir(os.path.join(root, "intrinsic"))
    intrinsic_kinect = {}
    intrinsic = {}
    for cam_name in cam_list:
        intrinsic[cam_name] = load_intrinsic(os.path.join(root, "intrinsic", cam_name))
        intrinsic_kinect[cam_name] = load_kinect_intrinsic(os.path.join(root, "intrinsic_kinect", "json", cam_name+".json"))

    for fname in file_list:
        scene_list = os.listdir(os.path.join(root, 'extrinsic', fname))
        
        for scene_name in scene_list:
            if not os.path.isdir(os.path.join(root, 'extrinsic', fname, scene_name)):
                continue
            
            
            os.makedirs(os.path.join(root, 'checkpoint_undistort', fname, scene_name), exist_ok=True)
            source_dir = os.path.join(root, 'extrinsic', fname, scene_name)
            dest_dir = os.path.join(root, 'checkpoint_undistort', fname, scene_name)
            find_keypoints_undistort_scene(source_dir, dest_dir, intrinsic)
            
            os.makedirs(os.path.join(root, 'checkpoint_kinect_undistort', fname, scene_name), exist_ok=True)
            source_dir = os.path.join(root, 'extrinsic', fname, scene_name)
            dest_dir = os.path.join(root, 'checkpoint_kinect_undistort', fname, scene_name)
            find_keypoints_undistort_scene(source_dir, dest_dir, intrinsic_kinect)
    return

if __name__ == "__main__":
    find_checkpoint_root('data', debug=False)