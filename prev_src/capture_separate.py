import open3d as o3d

import argparse
import os

import numpy as np

                    
# Python program to illustrate Python get current time
import time


class ViewerWithCallback:
    def __init__(self, config, device, capture_num, root, align_depth_to_color=True):
        self.flag_exit = False
        self.align_depth_to_color = align_depth_to_color

        self.sensor = o3d.io.AzureKinectSensor(config)
        if not self.sensor.connect(device):
            raise RuntimeError('Failed to connect to sensor')
        
        self.capture_num = capture_num
        self.capture_cnt = 0
        self.device = device
        self.dir = os.path.join(root, str(device))
        self.capture_start = False
        os.makedirs(self.dir, exist_ok=True)

    def escape_callback(self, vis):
        self.flag_exit = True
        return False

    def space_callback(self, vis): #capture start and capture capture_num frame
        self.capture_start = True
        return False

    def run(self):
        glfw_key_escape = 256
        glfw_key_space = 32
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.register_key_callback(glfw_key_escape, self.escape_callback)
        vis.register_key_callback(glfw_key_space, self.space_callback)
        vis.create_window(f'viewer{self.device}', 1920, 540)
        
        print("Sensor initialized. Press [ESC] to exit.")

        vis_geometry_added = False

        while not self.flag_exit and self.capture_cnt < self.capture_num:
            rgbd = self.sensor.capture_frame(self.align_depth_to_color)
            if rgbd is None:
                continue

            if not vis_geometry_added:
                vis.add_geometry(rgbd)
                vis_geometry_added = True

            vis.update_geometry(rgbd)
            vis.poll_events()
            vis.update_renderer()

            if self.capture_start:
                self.capture_cnt += 1
                o3d.io.write_image(os.path.join(self.dir, f'color{self.capture_cnt}.jpg'), rgbd.color)
                o3d.io.write_image(os.path.join(self.dir, f'depth{self.capture_cnt}.png'), rgbd.depth)
        
        self.sensor.disconnect()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Azure kinect mkv recorder.')
    parser.add_argument('--config', type=str, default='capture_config.json', help='input json kinect config')
    parser.add_argument('--list',
                        action='store_true',
                        help='list available azure kinect sensors')

    parser.add_argument('-a',
                        '--align_depth_to_color',
                        action='store_true',
                        default=True,
                        help='enable align depth image to color')

    args = parser.parse_args()

    if args.list:
        o3d.io.AzureKinectSensor.list_devices()
        exit()

    if args.config is not None:
        config = o3d.io.read_azure_kinect_sensor_config(args.config)
    else:
        config = o3d.io.AzureKinectSensorConfig()


    t = time.localtime()

    current_time = time.strftime("%H%M%S", t)
    dirname = "sep_"+current_time
    os.makedirs(dirname, exist_ok=True)

    for device in range(4):
        v = ViewerWithCallback(config, device, 100, dirname)
        v.run()