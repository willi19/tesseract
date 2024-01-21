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
            
# Start the visualization thread

if __name__ == '__main__':
    img_queue = queue.Queue()
    img_dir = 'current_scene'
    #os.removedirs(img_dir, exist_ok=True)
    shutil.rmtree(img_dir, ignore_errors=True)
    os.makedirs(img_dir, exist_ok=True)
    # Start consumer (image displayer) thread
    #threading.Thread(target=display_images, args=(img_queue,), daemon=True).start()
    
    app.run(host='192.168.0.34', port=5000, debug=True)


