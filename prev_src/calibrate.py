import open3d as o3d

import argparse
import os

import numpy as np

import time
import cv2

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
        self.capture_cnt += 1
        os.makedirs(os.path.join(self.dirname, str(self.capture_cnt)), exist_ok=True)
        return False

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
            tot_img = []
            for i in range(4):
                rgbd = self.sensors[i].capture_frame(self.align_depth_to_color)
                if rgbd is None:
                    print(i)
                    break

                if self.capture_status[i] < self.capture_cnt:
                    self.capture_status[i] += 1
                    o3d.io.write_image(os.path.join(self.dirname, str(self.capture_cnt), f'color{i}.jpg'), rgbd.color)
                    o3d.io.write_image(os.path.join(self.dirname, str(self.capture_cnt), f'depth{i}.png'), rgbd.depth)
                
                tot_img.append(cv2.resize(np.array(rgbd.color),(1024, 768) ))

            if len(tot_img) < 4:
                continue

            step+= 1
            print(step)
            if step%2 != 0:
                continue
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



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Azure kinect mkv recorder.')
    
    parser.add_argument('--list',
                        action='store_true',
                        help='list available azure kinect sensors')
    parser.add_argument('--device',
                        type=int,
                        default=0,
                        help='input kinect device id')
    
    args = parser.parse_args()

    config = o3d.io.read_azure_kinect_sensor_config(os.path.join('config','calib_config.json'))#o3d.io.AzureKinectSensorConfig()

    device = args.device
    if device < 0 or device > 255:
        print('Unsupported device id, fall back to 0')
        device = 0

    v = ViewerWithCallback(config, device, args.align_depth_to_color)
    v.run()