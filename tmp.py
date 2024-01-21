import shutil
import os


os.makedirs("data/capture", exist_ok=True)

os.makedirs("data/extrinsic/1230", exist_ok = True)

scene_cnt = 0
for extrinsic_name in ["face1", "final", "final2", "final3", "ground"]:
    ext_path = os.path.join("data","extrinsic",extrinsic_name)
    for scene_name in os.listdir(ext_path):
        if scene_name[-4:] == "json":
            continue
        cur_path = os.path.join(ext_path, scene_name)
        new_path = f"data/extrinsic/1230/scene{scene_cnt}"
        shutil.copytree(cur_path, new_path)
        scene_cnt += 1
        

os.makedirs("data/extrinsic/0118", exist_ok = True)

scene_cnt = 0
for extrinsic_name in ["flight","flight_ground"]:
    ext_path = os.path.join("data","extrinsic",extrinsic_name)
    for scene_name in os.listdir(ext_path):
        if scene_name[-4:] == "json":
            continue
        cur_path = os.path.join(ext_path, scene_name)
        new_path = f"data/extrinsic/0118/scene{scene_cnt}"
        shutil.copytree(cur_path, new_path)
        scene_cnt += 1

for capture_name in ["box", "box_ramen", "face", "face_hand", "face_hat", "face_sticker_hat", "face_sticker1"]:
    shutil.copytree(capture_name, "data/capture/"+capture_name)
