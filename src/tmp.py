import open3d as o3d

import argparse
import os

import numpy as np

import time
import cv2
import json
from pyk4a import PyK4A, Config, connected_device_count
from utils import convert_to_bgra_if_required

import threading
import asyncio
import shutil

class ViewerWithCallback:
    def set_config(self, config_path):
        config_file = open(config_path, 'r')
        data = json.load(config_file)
        return Config(**data)
        #self.config = Config(**data)

    def __init__(self):
        self.flag_exit = False
        subordinate_config_path = 'config/pyk4a_subordinate.json'
        subordinate_config = self.set_config(subordinate_config_path)

        master_config_path = 'config/pyk4a_master.json'
        master_config = self.set_config(master_config_path)

        config_path = 'config/pyk4a.json'
        self.config = self.set_config(config_path)
        
        configs = [subordinate_config, subordinate_config,  subordinate_config, subordinate_config]
        #configs = [self.config, self.config, self.config, self.config]
        self.device_num = connected_device_count()
        self.devices = [PyK4A(config = configs[device_ind], device_id=device_ind) for device_ind in range(self.device_num)]
        for i in range(self.device_num):
            self.devices[i].start()
        self.ids = [device.serial for device in self.devices]
        self.ids_inv = {self.ids[i]:i for i in range(self.device_num)}

        self.input_thread = threading.Thread(target=self.thread_input)   
        self.input_thread.start()
                        
    def thread_input(self):
        while not self.flag_exit:
            key = input()
            if key == 'capture':
                self.increase_capture_cnt()
            elif key == 'exit':
                self.flag_exit = True
    
    def close(self):
        for device in self.devices:
            device.stop()
        self.input_thread.join()
        print("close device")
        return False
    
    async def async_capture(self, index):
        id = self.ids[index]
        capture = self.devices[index].get_capture()
        if capture.color is None:
            return id, None
        img = convert_to_bgra_if_required(self.config.color_format, capture.color)
        print(index, "device time(ms)", (capture.color_timestamp_usec // 10 ** 3), "system time(ms)", (capture.color_system_timestamp_nsec % 10**12) // 10**6)
        return id, img

    async def get_all_captures(self):
        return await asyncio.gather(*(self.async_capture(index) for index in range(4)))

    async def process_loop(self):
        step = 0
        while not self.flag_exit:
            print("started")
            img_list = await self.get_all_captures()
            if img_list is None:
                print("asdf")
            else:
                print(len(img_list))
            tot_img = [None for _ in range(4)]
            for id, img in img_list:
                tot_img[self.ids_inv[id]] = cv2.resize(np.array(img),(1024, 768)) if img is not None else np.zeros((768,1024,3), dtype = np.uint8)
            if img_list is not None:
                tmpimg1 = np.concatenate((tot_img[0],tot_img[1]), axis=1)
                tmpimg2 = np.concatenate((tot_img[2],tot_img[3]), axis=1)
                img = np.concatenate((tmpimg1,tmpimg2), axis=0)
                
                cv2.imwrite(f'sync/{step}.jpg', img)
                step += 1
                    
        
    def run(self):
        shutil.rmtree('sync')
        os.makedirs('sync', exist_ok=True)
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.process_loop())
        finally:
            loop.close()
            self.close()

if __name__ == "__main__":
    viewer = ViewerWithCallback()
    viewer.run()