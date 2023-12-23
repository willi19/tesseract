from flask import Flask, request
import os
import numpy as np
import cv2
import time
import threading
import math

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    device_id = request.form.get('device_id')
    image = request.files.get('image')

    if not image:
        return 'No image uploaded', 400

    # You can use device_id for additional processing or naming
    filename = f"{device_id}_{image.filename}"
    filepath = os.path.join('uploads', filename)

    # Ensure the 'uploads' directory exists or create it
    os.makedirs('uploads', exist_ok=True)

    # Save the image
    image.save(filepath)

    return f'Image {filename} uploaded successfully', 200

def merge_into_square_grid(image_paths):
    images = [cv2.imread(path) for path in image_paths]
    target_size = (3072, 4096)
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
        img = merge_into_square_grid(sorted(os.listdir('uploads')))
        cv2.imshow('Image', img)
        cv2.waitKey(1)  # Display for a short duration
        time.sleep(5)  # Check the folder every 5 seconds

# Start the visualization thread

if __name__ == '__main__':
    threading.Thread(target=display_images, daemon=True).start()
    app.run(host='192.168.0.34', port=5000, debug=True)


