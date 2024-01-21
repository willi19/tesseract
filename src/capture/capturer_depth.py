import open3d as o3d
import os
import numpy as np
import cv2
import json
from pyk4a import PyK4A, Config, connected_device_count
from src.capture.utils import convert_to_bgra_if_required
import threading
import asyncio
import shutil
import time
import queue

class ViewerWithCallback:
    def set_config(self, config_path):
        with open(config_path, 'r') as config_file:
            data = json.load(config_file)
        return Config(**data)
    
    def read_config(self, config_path):
        with open(config_path, 'r') as config_file:
            data = json.load(config_file)
        return data
    
    def __init__(self):
        self.flag_exit = False

        # Load configurations
        subordinate_config = self.set_config('config/pyk4a_subordinate.json')
        master_config = self.set_config('config/pyk4a_master.json')
        self.config = self.set_config('config/pyk4a.json')

        configs = [subordinate_config] * 4  # Assuming 4 devices for example
        wire_setting = self.read_config('env/wire.json')
        if wire_setting['is_master']:
            configs[-1] = master_config
            
        self.device_num = connected_device_count()
        self.devices = [PyK4A(config=configs[device_ind], device_id=device_ind) for device_ind in range(self.device_num)]
        self.capture_start = False
        self.capture_queue = queue.Queue()
        # Start devices and create a thread for each device
        self.device_threads = []
        for device in self.devices:
            device.start()
            print(f"Starting device {device.serial} {device.sync_jack_status}")
            thread = threading.Thread(target=self.thread_capture, args=(device,))
            self.device_threads.append(thread)

        for thread in self.device_threads:
            thread.start()
        
        self.input_thread = threading.Thread(target=self.thread_input)
        self.input_thread.start()

        self.process_thread = threading.Thread(target=self.thread_process)
        self.process_thread.start()

    def thread_input(self):
        while not self.flag_exit:
            key = input()
            if key == 'exit':
                self.flag_exit = True
            if key == 'start':
                self.capture_start = True
                print("Start capturing")
            if key == 'stop':
                self.capture_start = False

    def thread_capture(self, device):
        os.makedirs(f'sync/{device.serial}', exist_ok=True)
        while not self.flag_exit:
            capture = device.get_capture()
            serial = device.serial
            if self.capture_start:
                print("capture device serial: ", serial)
                self.capture_queue.put((serial, capture))
    
    def thread_process(self):
        while not self.flag_exit or not self.capture_queue.empty():
            if not self.capture_queue.empty():
                serial, capture = self.capture_queue.get()
                if capture.color is not None:
                    img = convert_to_bgra_if_required(self.config.color_format, capture.color)
                    # Process and save the image
                    cv2.imwrite(f'sync/{serial}/{capture.color_timestamp_usec // 10 ** 3}.jpg', img)
                if capture.transformed_depth is not None:
                    depth = capture.transformed_depth
                    # Process and save the depth
                    np.save(f'sync/{serial}/{capture.depth_timestamp_usec // 10 ** 3}.npy', depth)
                    
    def close(self):
        for device in self.devices:
            device.stop()
        for thread in self.device_threads:
            thread.join()
        self.input_thread.join()
        self.process_thread.join()
        print("All devices closed")

    def run(self):
        if not os.path.exists('sync'):
            os.makedirs('sync', exist_ok=True)
        try:
            while not self.flag_exit:
                time.sleep(1)
        finally:
            self.close()

if __name__ == "__main__":
    shutil.rmtree('sync', ignore_errors=True)
    viewer = ViewerWithCallback()
    viewer.run()
