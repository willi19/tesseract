from flask import Flask, request, send_file
import os
import numpy as np
import cv2
import time
import threading
import math
import queue
import shutil

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    device_id = request.form.get('device_id')
    image = request.files.get('image')

    if not image:
        return 'No image uploaded', 400

    # You can use device_id for additional processing or naming
    filename = f"{device_id}.jpg"
    filepath = os.path.join('current_scene', filename)

    # Ensure the 'uploads' directory exists or create it
    os.makedirs('uploads', exist_ok=True)

    # Save the image
    image.save(filepath)

    return f'Image {filename} uploaded successfully', 200

def merge_into_square_grid(img_dir):
    img_list = sorted(os.listdir(img_dir))
    if len(img_list) == 0:
        return 
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
    cv2.imwrite('merged_image.jpg', merged_image)
    time.sleep(5)
    return 

def display_images(img_queue):
    while True:
        merged_image = img_queue.get()  # Blocking call, waits for new image
        cv2.imshow('Merged Image', merged_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break
    cv2.destroyAllWindows()

@app.route('/merged-image')
def get_merged_image():
    if not os.path.exists('merged_image.jpg'):
        return "No image available", 404
    return send_file('../merged_image.jpg', mimetype='image/jpeg')

            
# Start the visualization thread

if __name__ == '__main__':
    img_queue = queue.Queue()
    img_dir = 'current_scene'
    #os.removedirs(img_dir, exist_ok=True)
    shutil.rmtree(img_dir, ignore_errors=True)
    os.makedirs(img_dir, exist_ok=True)
    threading.Thread(target=merge_into_square_grid, args=(img_dir, img_queue), daemon=True).start()
    # Start consumer (image displayer) thread
    #threading.Thread(target=display_images, args=(img_queue,), daemon=True).start()
    
    app.run(host='192.168.0.34', port=5000, debug=True)


