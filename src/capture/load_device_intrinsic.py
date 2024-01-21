from pyk4a import PyK4A, connected_device_count, Config
import open3d as o3d
import json
import numpy as np
import cv2
import os
from src.capture import utils
import time
import shutil

def get_depth_config(depth_config):
    if depth_config == 'K4A_DEPTH_MODE_OFF':
        return 0
    if depth_config == 'K4A_DEPTH_MODE_NFOV_2X2BINNED':
        return 1
    if depth_config == 'K4A_DEPTH_MODE_NFOV_UNBINNED':
        return 2
    if depth_config == 'K4A_DEPTH_MODE_WFOV_2X2BINNED':
        return 3
    if depth_config == 'K4A_DEPTH_MODE_WFOV_UNBINNED':
        return 4
    if depth_config == 'K4A_DEPTH_MODE_PASSIVE_IR':
        return 5

def get_color_config(color_config):
    if color_config == 'K4A_COLOR_RESOLUTION_OFF':
        return 0
    if color_config == 'K4A_COLOR_RESOLUTION_720P':
        return 1
    if color_config == 'K4A_COLOR_RESOLUTION_1080P':
        return 2
    if color_config == 'K4A_COLOR_RESOLUTION_1440P':
        return 3
    if color_config == 'K4A_COLOR_RESOLUTION_1536P':
        return 4
    if color_config == 'K4A_COLOR_RESOLUTION_2160P':
        return 5
    if color_config == 'K4A_COLOR_RESOLUTION_3072P':
        return 6

cnt = connected_device_count()
if not cnt:
    print("No devices available")
    exit()


config_path = 'config/pyk4a.json'
config_file = open(config_path, 'r')
data = json.load(config_file)
config = Config(**data)

print(f"Available devices: {cnt}")

t = time.localtime()
current_time = time.strftime("%m%d%H%M%S", t)

save_path = os.path.join('data','intrinsic_kinect',current_time)
os.makedirs(save_path,exist_ok=True)
shutil.copyfile(config_path, os.path.join(save_path, 'config.json'))

for device_id in range(cnt):
    device = PyK4A(config = config, device_id=device_id)
    device.start()

    print(f"{device_id}: {device.serial}")
    os.makedirs(os.path.join(save_path, 'json'), exist_ok=True)
    os.makedirs(os.path.join(save_path, 'view'), exist_ok=True)

    device.save_calibration_json(os.path.join(save_path, 'json', f'{device.serial}.json'))
    
    while 1:
        capture = device.get_capture()
        if capture.color is None:
            continue
        img = utils.convert_to_bgra_if_required(config.color_format, capture.color)
        if np.any(capture.color):
            cv2.imwrite(os.path.join(save_path, "view", f'{device.serial}.png'), img)
            break
    device.stop()