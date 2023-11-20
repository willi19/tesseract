from pyk4a import PyK4A, connected_device_count, Config
import open3d as o3d
import json
import numpy as np
import cv2
import os

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

config_mode = ['calib', 'capture']
config = {}

for mode in config_mode:
    config_file = open(f'{mode}_config.json')
    data = json.load(config_file)
    color_config = get_color_config(data['color_resolution'])
    depth_config = get_depth_config(data['depth_mode'])
    config[mode] = (Config(color_resolution = color_config, depth_mode = depth_config, camera_fps = 0))
    
print(f"Available devices: {cnt}")
os.makedirs('intrinsic',exist_ok=True)


for mode in config_mode:
    for device_id in range(cnt):
        device = PyK4A(config = config[mode], device_id=device_id)
        device.start()
    
        print(f"{device_id}: {device.serial}")
        os.makedirs(os.path.join('intrinsic', str(device_id)), exist_ok=True)

        device.save_calibration_json(os.path.join('intrinsic', str(device_id), f'{mode}.json'))
        while 1:
            capture = device.get_capture()
            if np.any(capture.color):
                cv2.imwrite(os.path.join('intrinsic', str(device_id), "view.png"), capture.color[:, :, :3])
                break
        device.stop()