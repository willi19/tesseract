import os

import numpy as np

import time
import cv2
from pyk4a import PyK4A, connected_device_count, Config
import threading
import asyncio
import json
import shutil
from aiohttp import FormData
import aiohttp
import argparse
from src.capture.utils import convert_to_bgra_if_required

class ExtrinsicCalibrater:
    def read_config(self, config_path):
        config_file = open(config_path, 'r')
        data = json.load(config_file)
        return Config(**data)
    
    def read_json(self, json_path):
        json_file = open(json_path, 'r')
        data = json.load(json_file)
        return data
    
    def __init__(self, name):
        self.flag_exit = False
        subordinate_config_path = 'config/pyk4a_subordinate.json'
        subordinate_config = self.read_config('config/pyk4a_subordinate.json')
        master_config = self.read_config('config/pyk4a_master.json')
        
        
        self.config = subordinate_config         
        self.device_num = connected_device_count()
        configs = [subordinate_config] * self.device_num  # Assuming 4 devices for example
        wire_setting = self.read_json('env/wire.json')
        if wire_setting['is_master']:
            configs[-1] = master_config

        self.devices = [PyK4A(config=configs[device_ind], device_id=device_ind) for device_ind in range(self.device_num)]
        for i in range(self.device_num):
            self.devices[i].start()
        self.ids = [device.serial for device in self.devices]
        
        self.capture_cnt = 0
        self.capture_status = 0

        #t = time.localtime()
        #current_time = time.strftime("%m%d%H%M%S", t)

        self.name = name

        self.dirname = os.path.join('data','extrinsic',self.name)

        os.makedirs(self.dirname, exist_ok=True)
        shutil.copyfile(subordinate_config_path, os.path.join(self.dirname, 'config.json'))
        
        self.input_thread = threading.Thread(target=self.thread_input)   
        self.input_thread.start()
                         
        self.session = aiohttp.ClientSession()

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

    def increase_capture_cnt(self):
        os.makedirs(os.path.join(self.dirname, "scene"+str(self.capture_cnt)), exist_ok=True)
        self.capture_cnt += 1
        print("capture_cnt: ", self.capture_cnt)
        return
    
    async def send_image_to_server(self, image, url, session, device_id):
        if image is None:
            return
        data = FormData()
        data.add_field('device_id', str(device_id))
        image = cv2.resize(image, (image.shape[1]//4, image.shape[0]//4))
        success, encoded_image = cv2.imencode('.jpg', image)
        image_bytes = encoded_image.tobytes()

        data.add_field('image', image_bytes, filename=f'{device_id}.png', content_type='image/png')
        async with session.post(url, data=data) as response:
            return await response.text()
        
    
    async def send_all_images(self, img_list):
        tasks = [asyncio.create_task(self.send_image_to_server(img, 'http://192.168.0.34:5000/upload', self.session, id)) for id, img in img_list]
        await asyncio.gather(*tasks)
            
    async def async_capture(self, index):
        id = self.ids[index]
        capture = self.devices[index].get_capture()
        if capture.color is None:
            return id, None
        img = convert_to_bgra_if_required(self.config.color_format, capture.color)
        return id, img
    
    async def get_all_captures(self):
        return await asyncio.gather(*(self.async_capture(index) for index in range(self.device_num)))

    async def process_loop(self):
        while not self.flag_exit:
            img_list = await self.get_all_captures()
            if img_list is not None:
                await self.send_all_images(img_list)
                # Optionally save images locally
                if self.capture_status < self.capture_cnt:
                    for id, img in img_list:
                        if img is not None:
                            cv2.imwrite(f'{self.dirname}/scene{self.capture_status}/{id}.png', img)
                    self.capture_status += 1
                    
    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.process_loop())
        finally:
            loop.close()
            self.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Azure kinect mkv recorder.')
    parser.add_argument('--name', type=str, help='calibration setting name')
    args = parser.parse_args()
    
    calibrater = ExtrinsicCalibrater(args.name)
    calibrater.run()
