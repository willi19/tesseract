import cv2
import os
import numpy as np
import shutil
import json
import argparse

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

def save_checkpoint_root(root, is_kinect, debug=True):
    intrinsic = {}
    save_path = None
    cam_list = []

    if is_kinect:
        save_path = os.path.join(root, 'kinect_kypt')
        intrinsic_json_path = os.path.join(root, 'intrinsic_kinect','json')
        for json_name in os.listdir(intrinsic_json_path):
            cam_name = json_name.split('.')[0]
            cam_list.append(cam_name)
            intrinsic[cam_name] = load_kinect_intrinsic(os.path.join(intrinsic_json_path, json_name))
    
    else:
        save_path = os.path.join(root, 'opencv_kypt')
        intrinsic_path = os.path.join(root, 'intrinsic')
        for cam_name in os.listdir(intrinsic_path):
            cam_list.append(cam_name)
            intrinsic[cam_name] = load_intrinsic(os.path.join(intrinsic_path, cam_name))            
    
    os.makedirs(save_path, exist_ok=True)
        
    scene_list = os.listdir(os.path.join(root, 'scene'))
    
    for i, scene_name in enumerate(scene_list):
        dest_dir = os.path.join(save_path, scene_name)
        source_dir = os.path.join(root, 'scene', scene_name)
        
        os.makedirs(dest_dir, exist_ok=True)
        find_keypoints_undistort_scene(source_dir, dest_dir, intrinsic)
        
        print(str(i / len(scene_list) * 100)+"%"+ " done")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required = True, help='data/calibrate/root')
    parser.add_argument("--type", required = True, help='all-kinect-opencv')
    
    args = parser.parse_args()
    
    root_path = f'data/calibrate/{args.root}'
    
    if args.type not in ['all', 'kinect', 'opencv']:
        print("type should be one of [all ,kinect, opencv]")
    
    if args.type in ['all', 'kinect']:
        save_checkpoint_root(root_path, is_kinect = True, debug=False)
    if args.type in ['all', 'kinect']:
        save_checkpoint_root(root_path, is_kinect = False, debug=False)
