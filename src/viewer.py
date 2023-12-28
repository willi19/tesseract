import open3d as o3d

import argparse
import os

import numpy as np

import time
import cv2
import json
from pyk4a import PyK4A, Config, connected_device_count
from utils import convert_to_bgra_if_required

class ViewerWithCallback:
    def set_config(self, config_path):
        config_file = open(config_path, 'r')
        data = json.load(config_file)
        self.config = Config(**data)

    def __init__(self):
        self.flag_exit = False
        config_path = 'config/pyk4a.json'
        self.set_config(config_path)
        self.device_num = connected_device_count()
        print(f"Found {self.device_num} connected devices")
        self.devices = [PyK4A(config = self.config, device_id=device_ind) for device_ind in range(self.device_num)]
        for i in range(self.device_num):
            self.devices[i].start()
                        

    def escape_callback(self, vis):
        self.flag_exit = True
        for device in self.devices:
            device.stop()
        return False

    def run(self):
        glfw_key_escape = 256
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.register_key_callback(glfw_key_escape, self.escape_callback)
        vis.create_window(f'viewer', 2048, 1536)
        print("Sensor initialized. Press [ESC] to exit.")

        vis_geometry_added = False
        step = 0
        while not self.flag_exit:
            tot_img = []
            for i in range(self.device_num):
                rgbd =  self.devices[i].get_capture().color
                if rgbd is None:
                    print(i)
                    break
                rgbd = convert_to_bgra_if_required(self.config.color_format, rgbd)
                rgbd = cv2.cvtColor(rgbd, cv2.COLOR_BGRA2RGB)
                tot_img.append(cv2.resize(np.array(rgbd),(1024, 768)))

            if len(tot_img) < self.device_num:
                continue

            step+= 1
            print(step)
            if step%2 != 0:
                continue

            if len(tot_img) < 4:
                for i in range(4-len(tot_img)):
                    tot_img.append(np.zeros((768,1024,3), dtype=np.uint8))
            tmpimg1 = np.concatenate((tot_img[0],tot_img[1]), axis=1)
            tmpimg2 = np.concatenate((tot_img[2],tot_img[3]), axis=1)
            img = np.concatenate((tmpimg1,tmpimg2), axis=0)
            cv2.putText(img, str(step), (512,512),cv2.FONT_HERSHEY_SIMPLEX ,3, (255, 255, 0) )
            img = o3d.geometry.Image(img.astype(np.uint8))
            vis.clear_geometries()
            vis.add_geometry(img)
                #vis_geometry_added = True
            vis.update_geometry(img)
            vis.poll_events()
            vis.update_renderer()

if __name__ == "__main__":
    viewer = ViewerWithCallback()
    viewer.run()