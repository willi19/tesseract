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
    os.makedirs('intrinsic', exist_ok=True)
    for cam_name, kypt in keypoint_list.items():
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoint_list[cam_name], kypt, (4096, 3072), None, None, flags = cv2.CALIB_RATIONAL_MODEL)
        os.makedirs(os.path.join('intrinsic', cam_name), exist_ok=True)
        np.save(os.path.join('intrinsic', cam_name, 'mtx.npy'), mtx)
        np.save(os.path.join('intrinsic', cam_name, 'dist.npy'), dist)
        print(ret, mtx[0][0], mtx[1][1], mtx[0][2], mtx[1][2], dist[0][0], dist[0][1], dist[0][4], dist[0][5], dist[0][6], dist[0][7], dist[0][2], dist[0][3])
