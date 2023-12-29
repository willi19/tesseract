import math
import cv2
import time
import os
import numpy as np

def merge_into_square_grid(img_dir):
    img_list = sorted(os.listdir(img_dir))
    if len(img_list) == 0:
        return None
    images = [cv2.imread(os.path.join(img_dir, img_name)) for img_name in img_list]
    target_size = (4096, 3072)
    # Determine grid size
    grid_size = math.ceil(math.sqrt(len(images)))
    
    num_col = grid_size
    num_row = (len(images) -1) // num_col + 1
     
    while len(images) < num_col * num_row:
        # Add blank images if necessary to complete the square
        images.append(np.zeros_like(images[0]))

    # Resize images for consistency
    
    resized_images = [cv2.resize(image, (target_size[0] // num_row, target_size[1] // num_col)) for image in images]

    # Create rows and merge
    rows = [np.hstack(resized_images[i * num_col:(i + 1) * num_col]) for i in range(num_row)]
    merged_image = np.vstack(rows)

    return merged_image

def display_images():
    while True:
        img = merge_into_square_grid('current_scene')
        if img is not None:
            cv2.imshow('Image', img)
            cv2.waitKey(1)  # Display for a short duration
            time.sleep(5)  # Check the folder every 5 seconds
            
if __name__ == '__main__':
    while True:
        display_images()