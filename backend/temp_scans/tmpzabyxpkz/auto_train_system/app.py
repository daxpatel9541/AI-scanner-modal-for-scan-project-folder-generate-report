from flask import Flask, request, jsonify, render_template
import os
import cv2
import numpy as np
from models.yolo import detect_object
from models.feature_extractor import extract_feature
from storage.vector_store import save_product, search_product
import base64
import re

app = Flask(__name__)

TARGET_IMAGES = 50
DIFF_THRESHOLD = 18

# Global state for simplicity (in production, use sessions or database)
capture_state = {}

def sanitize_product_name(name):
    """Sanitize product name to prevent directory traversal"""
    # Remove special characters, keep only alphanumeric, spaces, hyphens, underscores
    name = re.sub(r'[^\w\s\-]', '', name)
    # Replace spaces with underscores
    name = name.strip().replace(' ', '_')
    return name[:50]  # Limit length

def preprocess(img):
    return cv2.resize(img, (224, 224))

def image_diff(a, b):
    a = preprocess(a)
    b = preprocess(b)
    return np.mean(cv2.absdiff(a, b))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.json
        product_name = sanitize_product_name(data.get('product_name', ''))
        image_data = data.get('image', '')

        if not product_name:
            return jsonify({'error': 'Invalid product name'}), 400

        if not image_data:
            return jsonify({'error': 'No image data'}), 400

        # Decode base64 image
        header, encoded = image_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400

        if product_name not in capture_state:
            capture_state[product_name] = {'count': 0, 'last_crop': None, 'saved': []}

        state = capture_state[product_name]

        box = detect_object(frame)

        if box is not None:
            x1, y1, x2, y2 = box
            crop = frame[y1:y2, x1:x2]

            if crop.size != 0:
                if state['last_crop'] is None or image_diff(crop, state['last_crop']) > DIFF_THRESHOLD:
                    save_dir = f"data/products/{product_name}"
                    os.makedirs(save_dir, exist_ok=True)
                    cv2.imwrite(f"{save_dir}/{state['count']}.jpg", crop)
                    state['saved'].append(f"{save_dir}/{state['count']}.jpg")
                    state['last_crop'] = crop.copy()
                    state['count'] += 1

        return jsonify({'count': state['count'], 'target': TARGET_IMAGES})

    except Exception as e:
        print(f"Error in capture: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/finish', methods=['POST'])
def finish():
    try:
        data = request.json
        product_name = sanitize_product_name(data.get('product_name', ''))

        if not product_name:
            return jsonify({'status': 'error', 'message': 'Invalid product name'}), 400

        if product_name in capture_state:
            state = capture_state[product_name]
            if state['count'] >= TARGET_IMAGES:
                vectors = []
                for img_path in state['saved']:
                    img = cv2.imread(img_path)
                    if img is not None:
                        vector = extract_feature(img)
                        vectors.append(vector)

                if vectors:
                    save_product(product_name, vectors)
                    del capture_state[product_name]
                    return jsonify({'status': 'success', 'message': f'Product {product_name} trained successfully!'})
                else:
                    return jsonify({'status': 'error', 'message': 'No valid images found'}), 400
            else:
                return jsonify({'status': 'error', 'message': f'Need {TARGET_IMAGES} images, only have {state["count"]}'}), 400

        return jsonify({'status': 'error', 'message': 'Product not found in capture state'}), 404

    except Exception as e:
        print(f"Error in finish: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/detect', methods=['POST'])
def detect():
    """Detect/recognize product from camera image"""
    try:
        data = request.json
        image_data = data.get('image', '')

        if not image_data:
            return jsonify({'error': 'No image data'}), 400

        # Decode base64 image
        header, encoded = image_data.split(",", 1)
        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'error': 'Invalid image'}), 400

        # Detect object in frame
        box = detect_object(frame)

        if box is None:
            return jsonify({'detected': False, 'message': 'No object detected'})

        x1, y1, x2, y2 = box
        crop = frame[y1:y2, x1:x2]

        if crop.size == 0:
            return jsonify({'detected': False, 'message': 'Invalid crop'})

        # Extract features and search
        vector = extract_feature(crop)
        result = search_product(vector, top_k=10)

        if result is None:
            return jsonify({'detected': False, 'message': 'No trained products found in database'})

        return jsonify({
            'detected': True,
            'product_name': result['product_name'],
            'confidence': result['confidence'],
            'similarity_score': result['similarity_score'],
            'votes': result['votes']
        })

    except Exception as e:
        print(f"Error in detect: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/products', methods=['GET'])
def get_products():
    """Get list of all trained products"""
    try:
        if not os.path.exists("storage/products.json"):
            return jsonify({'products': []})

        import json
        with open("storage/products.json", "r") as f:
            meta = json.load(f)

        # Get unique product names
        products = list(set(meta.values()))
        return jsonify({'products': products})

    except Exception as e:
        print(f"Error getting products: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)