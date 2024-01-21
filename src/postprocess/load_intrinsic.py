import os
import cv2

import cv2
import os
import numpy as np
import json

import argparse

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
    scene_list = os.listdir(os.path.join(root, 'checkpoint'))
    for scene_name in scene_list:
        img_list = os.listdir(os.path.join(root, 'checkpoint', scene_name))
        for img_name in img_list:
            cam_name = img_name[:-4]
            keypoint = np.load(os.path.join(root, 'checkpoint', scene_name, img_name))
            if img_name[:-4] not in keypoint_list:
                keypoint_list[cam_name] = [keypoint]
                objpoint_list[cam_name] = [objp]
            else:
                keypoint_list[cam_name].append(keypoint)
                objpoint_list[cam_name].append(objp)
    return keypoint_list, objpoint_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required = True, help='data/calibrate/root')
    args = parser.parse_args()
    root_path = f'data/calibrate/{args.root}'
    keypoint_list, objpoint_list = load_checkpoint(root_path, debug=False)
    
    os.makedirs(os.path.join(root_path, 'intrinsic'), exist_ok=True)
    
    for cam_name, kypt in keypoint_list.items():
        os.makedirs(os.path.join(root_path, 'intrinsic', cam_name), exist_ok=True)
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoint_list[cam_name], kypt, (4096, 3072), None, None, flags = cv2.CALIB_RATIONAL_MODEL)
        
        np.save(os.path.join(root_path, 'intrinsic', cam_name, 'mtx'), mtx)
        np.save(os.path.join(root_path, 'intrinsic', cam_name, 'dist'), dist)

        print("device : ", ret, len(kypt))
    print("done")
        