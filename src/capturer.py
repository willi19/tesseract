import open3d as o3d
import os
import numpy as np
import cv2
import json
from pyk4a import PyK4A, Config, connected_device_count
from utils import convert_to_bgra_if_required
import threading
import asyncio
import shutil
import time

class ViewerWithCallback:
    def set_config(self, config_path):
        with open(config_path, 'r') as config_file:
            data = json.load(config_file)
        return Config(**data)

    def __init__(self):
        self.flag_exit = False

        # Load configurations
        subordinate_config = self.set_config('config/pyk4a_subordinate.json')
        master_config = self.set_config('config/pyk4a_master.json')
        self.config = self.set_config('config/pyk4a.json')

        configs = [subordinate_config] * 4  # Assuming 4 devices for example
        #configs[-1] = master_config
        self.device_num = connected_device_count()
        self.devices = [PyK4A(config=configs[device_ind], device_id=device_ind) for device_ind in range(self.device_num)]

        # Start devices and create a thread for each device
        self.device_threads = []
        for device in self.devices:
            device.start()
            thread = threading.Thread(target=self.capture_and_process, args=(device,))
            self.device_threads.append(thread)

        for thread in self.device_threads:
            thread.start()
        self.input_thread = threading.Thread(target=self.thread_input)
        self.input_thread.start()

        self.capture_start = False

    def thread_input(self):
        while not self.flag_exit:
            key = input()
            if key == 'exit':
                self.flag_exit = True
            if key == 'start':
                self.capture_start = True

    def capture_and_process(self, device):
        os.makedirs(f'sync/{device.serial}', exist_ok=True)
        while not self.flag_exit:
            capture = device.get_capture()
            if capture.color is not None and self.capture_start:
                img = convert_to_bgra_if_required(self.config.color_format, capture.color)
                # Process and save the image
                cv2.imwrite(f'sync/{device.serial}/{capture.color_timestamp_usec // 10 ** 3}.jpg', img)

    def close(self):
        for device in self.devices:
            device.stop()
        for thread in self.device_threads:
            thread.join()
        self.input_thread.join()
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
    viewer = ViewerWithCallback()
    viewer.run()
