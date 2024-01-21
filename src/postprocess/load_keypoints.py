import cv2
import os
import numpy as np
import shutil
import argparse

def find_keypoints_scene(source_dir, dest_dir, debug=False): #Save 
    img_list = os.listdir(source_dir)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    for img_name in img_list:
        img = cv2.imread(os.path.join(source_dir, img_name))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (7, 10), None)

        if ret == True:
            corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
            np.save(os.path.join(dest_dir, img_name[:-4]), corners2)
            corners = corners[:,0,:]
            if debug:
                for i, pt in enumerate(corners):
                    img = cv2.circle(img, (int(pt[0]), int(pt[1])), 4, (0,0,255) if i <35 else (255,0,0), -1)

                img = cv2.resize(img, (img.shape[1]//4, img.shape[0]//4))
                cv2.imshow('img', img)
                cv2.waitKey(0)
    return

def find_checkpoint_root(root, debug=True):
    os.makedirs(os.path.join(root, 'checkpoint'), exist_ok=True)
    scene_list = os.listdir(os.path.join(root, 'scene'))
    for i, scene_name in enumerate(scene_list):
        if not os.path.isdir(os.path.join(root, 'scene', scene_name)):
            continue
        os.makedirs(os.path.join(root, 'checkpoint', scene_name), exist_ok=True)

        source_dir = os.path.join(root, 'scene', scene_name)
        dest_dir = os.path.join(root, 'checkpoint', scene_name)
        find_keypoints_scene(source_dir, dest_dir, debug=debug)
        print(str((i / len(scene_list)) * 100) + "%" + "done")
    print("done")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required = True, help='data/calibrate/root')
    args = parser.parse_args()
    find_checkpoint_root(f"data/calibrate/{args.root}", debug=False)