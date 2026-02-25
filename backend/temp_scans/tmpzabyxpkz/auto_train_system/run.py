# For CLI usage (original functionality)
# Uncomment below to use CLI version

# import os
# from camera.capture import auto_capture
# from models.feature_extractor import extract_feature
# from storage.vector_store import save_product
# import cv2

# product_name = input("Enter product name: ")

# auto_capture(product_name)

# vectors = []
# path = f"data/products/{product_name}"

# for img_name in os.listdir(path):
#     img = cv2.imread(os.path.join(path, img_name))
#     vector = extract_feature(img)
#     vectors.append(vector)

# save_product(product_name, vectors)

# print("✅ Product auto-trained successfully")

# Web app version
from app import app

if __name__ == '__main__':
    print("Starting web application...")
    print("Open your browser and go to http://localhost:5000")
    app.run(debug=True)
