
from flask import Flask, request, jsonify
import os
from PIL import Image, ImageDraw

app = Flask(__name__)

COLOR_STOPS = [
    (0,   (0, 0, 255)),
    (85,  (0, 255, 0)),
    (170, (255, 255, 0)),
    (255, (255, 0, 0))
]

def interpolate_color(val):
    for i in range(len(COLOR_STOPS) - 1):
        v0, c0 = COLOR_STOPS[i]
        v1, c1 = COLOR_STOPS[i + 1]
        if v0 <= val <= v1:
            ratio = (val - v0) / (v1 - v0)
            r = int(c0[0] + (c1[0] - c0[0]) * ratio)
            g = int(c0[1] + (c1[1] - c0[1]) * ratio)
            b = int(c0[2] + (c1[2] - c0[2]) * ratio)
            return (r, g, b)
    return (0, 0, 0)

def create_color_grid(bytes_list, filename):
    canvas_size = 224
    n = len(bytes_list)
    cols = int(n ** 0.5)
    if cols * cols < n:
        cols += 1
    rows = (n + cols - 1) // cols
    cell_w = cell_h = canvas_size // max(cols, rows)

    image = Image.new('RGB', (canvas_size, canvas_size), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    for i, byte_val in enumerate(bytes_list):
        row = i // cols
        col = i % cols
        x0 = col * cell_w
        y0 = row * cell_h
        x1 = x0 + cell_w
        y1 = y0 + cell_h

        color = interpolate_color(byte_val)
        draw.rectangle([x0, y0, x1, y1], fill=color)

    if not os.path.exists("moviendo"):
        os.makedirs("moviendo")

    full_path = os.path.join("moviendo", filename + ".png")
    image.save(full_path)
    return full_path

@app.route("/create_image", methods=["POST"])
def create_image():
    data = request.json
    hex_data = data.get("hex_data", [])
    if not hex_data:
        return jsonify({"error": "No hex_data provided"}), 400
    
    try:
        bytes_list = [int(b, 16) for b in hex_data]
    except:
        return jsonify({"error": "Invalid hex data"}), 400

    filename = data.get("filename", "image")
    path = create_color_grid(bytes_list, filename)
    return jsonify({"message": "Image created", "path": path})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
