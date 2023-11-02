import open3d as o3d

import argparse
import os

import numpy as np

                    
# Python program to illustrate Python get current time
import time


class ViewerWithCallback:

    def __init__(self, config, device, align_depth_to_color):
        self.flag_exit = False
        self.align_depth_to_color = align_depth_to_color

        self.sensors = [o3d.io.AzureKinectSensor(config) for _ in range(4)]
        for i, sensor in enumerate(self.sensors):
            if not sensor.connect(i):
                raise RuntimeError('Failed to connect to sensor')
        self.capture_cnt = 0
        self.capture_status = [0 for _ in range(4)]

        t = time.localtime()

        current_time = time.strftime("%H%M%S", t)
        self.dirname = current_time
        os.makedirs(self.dirname, exist_ok=True)
                        

    def escape_callback(self, vis):
        self.flag_exit = True
        return False

    def space_callback(self, vis):
        self.capture_cnt = 10000
        for i in range(4):
            os.makedirs(os.path.join(self.dirname, str(i)), exist_ok=True)
        return False

    def run(self):
        glfw_key_escape = 256
        glfw_key_space = 32
        vis = [o3d.visualization.VisualizerWithKeyCallback() for _ in range(4)]
        for i, v in enumerate(vis):
            v.register_key_callback(glfw_key_escape, self.escape_callback)
            v.register_key_callback(glfw_key_space, self.space_callback)
            v.create_window(f'viewer{i}', 1920, 540)
        print("Sensor initialized. Press [ESC] to exit.")

        vis_geometry_added = [False for _ in range(4)]

        while not self.flag_exit:
            for i in range(4):
                rgbd = self.sensors[i].capture_frame(self.align_depth_to_color)
                if rgbd is None:
                    continue

                if not vis_geometry_added[i]:
                    vis[i].add_geometry(rgbd)
                    vis_geometry_added[i] = True

                vis[i].update_geometry(rgbd)
                vis[i].poll_events()
                vis[i].update_renderer()

                if self.capture_status[i] < self.capture_cnt:
                    self.capture_status[i] += 1
                    t = time.localtime()

                    current_time = time.strftime("%H%M%S", t)
                    print(current_time)
                    o3d.io.write_image(os.path.join(self.dirname, str(i), f'color_{current_time}.jpg'), rgbd.color)
                    o3d.io.write_image(os.path.join(self.dirname, str(i), f'depth_{current_time}.png'), rgbd.depth)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Azure kinect mkv recorder.')
    parser.add_argument('--config', type=str, default='capture_config.json', help='input json kinect config')
    parser.add_argument('--list',
                        action='store_true',
                        help='list available azure kinect sensors')
    parser.add_argument('--device',
                        type=int,
                        default=0,
                        help='input kinect device id')
    parser.add_argument('-a',
                        '--align_depth_to_color',
                        action='store_true',
                        help='enable align depth image to color')
    args = parser.parse_args()

    if args.list:
        o3d.io.AzureKinectSensor.list_devices()
        exit()

    if args.config is not None:
        config = o3d.io.read_azure_kinect_sensor_config(args.config)
    else:
        config = o3d.io.AzureKinectSensorConfig()

    device = args.device
    if device < 0 or device > 255:
        print('Unsupported device id, fall back to 0')
        device = 0

    v = ViewerWithCallback(config, device, args.align_depth_to_color)
    v.run()