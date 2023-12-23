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
import argparse

class ExtrinsicCalibrater:
    def set_config(self, config_path):
        config_file = open(config_path, 'r')
        data = json.load(config_file)
        self.config = Config(**data)

    
    def __init__(self, name):
        self.flag_exit = False

        config_path = 'config/pyk4a.json'
        self.set_config(config_path)

        self.devices = [PyK4A(config = self.config, device_id=device_ind) for device_ind in range(4)]
        for i in range(4):
            self.devices[i].start()
        self.ids = [device.serial for device in self.devices]
        
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
        
        self.input_thread = threading.Thread(target=self.run)   
        self.input_thread.input_thread.start()
                         

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
        os.makedirs(os.path.join(self.dirname, str(self.capture_cnt)), exist_ok=True)
        self.capture_cnt += 1
        print("capture_cnt: ", self.capture_cnt)
        return
    
    async def send_image_to_server(self, image, url, session, device_id):
        data = FormData()
        data.add_field('device_id', str(device_id))
        data.add_field('image', image, filename=f'{device_id}.png', content_type='image/png')
        async with session.post(url, data=data) as response:
            return await response.text()
        
    
    async def send_all_images(self, img_list):
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.create_task(self.send_image_to_server(img, 'http://192.168.0.34/upload', session, id)) for id, img in img_list]
            await asyncio.gather(*tasks)
            
    async def async_capture(self, index):
        capture = await self.devices.get_capture()
        if capture.color is None:
            return None
        id = self.ids[index]
        return cv2.cvtColor(capture.color, cv2.COLOR_RGBA2RGB), id
    
    async def get_all_captures(self):
        return await asyncio.gather(*(self.async_capture(i) for i in range(4)))

    async def process_loop(self):
        while self.flag_exit:
            img_list = await self.get_all_captures()
            if img_list:
                await self.send_all_images(img_list)
                # Optionally save images locally
                if self.capture_status < self.capture_cnt:
                    for id, img in id, img_list:
                        cv2.imwrite(f'data/calib/scene{self.capture_status}/{id}.png', img)
                    self.capture_status += 1
                    
    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.process_loop())
        finally:        
            self.close()
            loop.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Azure kinect mkv recorder.')
    parser.add_argument('--name', type=str, help='calibration setting name')
    args = parser.parse_args()
    
    calibrater = ExtrinsicCalibrater(args.name)
    calibrater.run()