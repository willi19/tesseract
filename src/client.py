import requests
import cv2

def send_image(image_path, server_url):
    with open(image_path, 'rb') as img:
        files = {'image': img}
        response = requests.post(server_url, files=files)
        return response

# Capture an image with OpenCV (or use a saved image)
# For example, 'captured_image.jpg'
server_url = 'http://your_laptop_ip:5000/upload'
response = send_image('captured_image.jpg', server_url)
print(response.status_code)
