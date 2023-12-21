import open3d as o3d

import argparse
import os

import numpy as np

import time
import cv2
from pyk4a import PyK4A, connected_device_count, Config
from .utils import convert_to_bgra_if_required

class ExtrinsicCalibrater:
    def set_config(self, config_path):
        config_file = open(config_path, 'r')
        data = json.load(config_file)
        self.config = Config(**data)

    def __init__(self, mode, name):
        self.flag_exit = False

        config_path = 'config/pyk4a.json'
        self.set_config(config_path)

        self.devices = [PyK4A(config = self.config, device_id=device_ind) for device_ind in range(4)]
        
        for device in self.devices:
            device.start()

        self.capture_cnt = 0
        self.capture_status = 0

        #t = time.localtime()
        #current_time = time.strftime("%m%d%H%M%S", t)

        self.name = name

        self.dirname = os.path.join('data','extrinsic',self.name)

        shutil.copyfile(config_path, os.path.join(self.dirname, 'config.json'))
        os.makedirs(self.dirname, exist_ok=True)                        

    def escape_callback(self, vis):
        for device in self.devices:
            device.stop()
        self.flag_exit = True
        return False

    def space_callback(self, vis):
        os.makedirs(os.path.join(self.dirname, str(self.capture_cnt)), exist_ok=True)
        self.capture_cnt += 1

        if self.capture_cnt >= 1:
            f = open('data','extrinsic','latest.txt')
            f.write(self.name)
            f.close()
        
        return False

    def merge_image(self, image_list):
        for i in range(4):
            image_list[i] = cv2.resize(image_list[i], (1024, 768))

        tmpimg1 = np.concatenate((image_list[0],image_list[1]), axis=1)
        tmpimg2 = np.concatenate((image_list[2],image_list[3]), axis=1)
        img = np.concatenate((tmpimg1,tmpimg2), axis=0)
        return img

    def get_capture(self): #save image and return visualized image
        img_list = []
        for i in range(4):
            capture = self.devices[i].get_capture()
            if capture.color is None:
                break
            
            img = convert_to_bgra_if_required(self.config.color_format, capture.color)
            img_list.append(img)

        if len(img_list) < 4:
            return None

        if self.capture_status < self.capture_cnt:
            for i in range(4):
                cv2.imwrite(os.path.join(self.dirname, str(self.capture_status), f'{i}.png'), img_list[i])
            self.capture_status += 1
        
        return self.merge_image(img_list)
    
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

            step+= 1
            cv2.putText(img, str(step), (512,512),cv2.FONT_HERSHEY_SIMPLEX ,3, (255, 255, 0) )
            img = o3d.geometry.Image(img.astype(np.uint8))
            vis.clear_geometries()
            vis.add_geometry(img)
                #vis_geometry_added = True
            vis.update_geometry(img)
            vis.poll_events()
            vis.update_renderer()