import shutil
import os


os.makedirs("data/capture", exist_ok=True)

for date in ["1230", "0118"]:
    root = f"data/calibrate/{date}"
    os.makedirs(os.path.join(root, "scene"), exist_ok = True)
    for scene_name in os.listdir(root):
        if scene_name == "scene":
            continue
        scene_num = scene_name[5:]
        cur_path = os.path.join(root, scene_name)
        new_path = os.path.join(root, "scene", scene_num)
        shutil.copytree(cur_path, new_path)
