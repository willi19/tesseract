from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    pc_id = request.form.get('pc_id')  # Identifier for each PC
    image = request.files['image']

    if image:
        directory = f"./images_from_{pc_id}"  # Folder for each PC
        if not os.path.exists(directory):
            os.makedirs(directory)

        filepath = os.path.join(directory, f"{image.filename}")
        image.save(filepath)
        return f"Image saved from PC {pc_id}", 200

    return "No image found", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
