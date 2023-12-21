import open3d as o3d

import os

import numpy as np

import time
import cv2

import json
import shutil
from pyk4a import PyK4A, connected_device_count, Config
from .utils import convert_to_bgra_if_required

class IntrinsicCalibrater:
    def set_config(self, config_path):
        config_file = open(config_path, 'r')
        data = json.load(config_file)
        self.config = Config(**data)

    def __init__(self, device_ind):
        self.flag_exit = False

        config_path = 'config/pyk4a.json'
        self.set_config(config_path)
        
        self.device = PyK4A(config = self.config, device_id=device_ind)
        self.device.start()

        self.capture_cnt = 0
        self.capture_status = 0

        t = time.localtime()
        current_time = time.strftime("%m%d%H%M%S", t)

        self.dirname = os.path.join('data','intrinsic',str(self.device.serial),current_time)
        os.makedirs(self.dirname, exist_ok=True)

        shutil.copyfile(config_path, os.path.join(self.dirname, 'config.json'))

    def escape_callback(self, vis):
        self.device.stop()
        self.flag_exit = True
        return False

    def space_callback(self, vis):
        self.capture_cnt += 1
        return False

    def get_capture(self): #save image and return visualized image
        capture = self.device.get_capture()
        if capture.color is None:
            return None

        img = convert_to_bgra_if_required(self.config.color_format, capture.color)
        
        if self.capture_status < self.capture_cnt:
            cv2.imwrite(os.path.join(self.dirname, f'{self.capture_status}.png'), img)
            self.capture_status += 1
        img = cv2.resize(img, (2048, 1536))
        return img
        

    def run(self):
        glfw_key_escape = 256
        glfw_key_space = 32
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.register_key_callback(glfw_key_escape, self.escape_callback)
        vis.register_key_callback(glfw_key_space, self.space_callback)
        vis.create_window(f'viewer', 2048, 1536)
        print("Sensor initialized. Press [ESC] to exit.")

        vis_geometry_added = False
        step = 0
        
        while not self.flag_exit:
            img = self.get_capture()
            if img is None:
                continue

            step += 1
            cv2.putText(img, str(step), (512,512),cv2.FONT_HERSHEY_SIMPLEX ,3, (255, 255, 0) )
            img = o3d.geometry.Image(img.astype(np.uint8))
            vis.clear_geometries()
            vis.add_geometry(img)
                #vis_geometry_added = True
            vis.update_geometry(img)
            vis.poll_events()
            vis.update_renderer()