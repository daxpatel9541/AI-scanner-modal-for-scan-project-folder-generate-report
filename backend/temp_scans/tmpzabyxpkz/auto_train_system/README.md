# Product Recognition System

A complete AI-powered product recognition system that allows you to train and detect products using computer vision.

## Features

- **Train Mode**: Capture 50 images of products automatically from different angles
- **Detect Mode**: Real-time product recognition with confidence scores
- **YOLO Object Detection**: Uses YOLOv8 for robust object detection
- **Feature Extraction**: ResNet50-based feature extraction
- **Vector Search**: FAISS-powered similarity search for fast recognition
- **Web Interface**: Modern, responsive UI with camera integration

## System Architecture

```
Camera Stream → YOLO Detection → Crop Object → Feature Extraction (ResNet50) → FAISS Vector Store
                                                                                      ↓
                                                                              Product Recognition
```

## Requirements

- Python 3.8+
- Webcam
- Modern web browser with camera access

## Installation

1. Clone the repository:
```bash
cd auto_train_system
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

The required packages are:
- `ultralytics` - YOLOv8 object detection
- `opencv-python` - Image processing
- `torch` - PyTorch deep learning framework
- `torchvision` - Pre-trained models
- `faiss-cpu` - Vector similarity search
- `numpy` - Numerical operations
- `flask` - Web framework

## Usage

### Starting the Application

Run the web application:
```bash
python run.py
```

Then open your browser to:
```
http://localhost:5000
```

### Training a New Product

1. Click **"Train Mode"** on the home page
2. Enter a product name (e.g., "Coffee Mug", "Phone", "Book")
3. Click **"Start Capture"**
4. Allow camera access when prompted
5. Position the product in front of the camera
6. Slowly rotate the product to capture different angles
7. The system will automatically capture 50 distinct images
8. Click **"Finish Training"** when capture is complete
9. Wait for feature extraction and model training

### Detecting Products

1. Click **"Detect Mode"** on the home page
2. Click **"Start Detection"**
3. Show any trained product to the camera
4. Real-time results will display:
   - Product name
   - Confidence percentage
   - Similarity score
   - Vote ratio

### Understanding Detection Results

- **Confidence**: Percentage of matches (higher is better)
  - High (70%+): Strong match
  - Medium (40-70%): Moderate match
  - Low (<40%): Weak match
- **Similarity Score**: Cosine similarity (closer to 1.0 is better)
- **Votes**: Number of matching vectors out of top-k results

## Project Structure

```
auto_train_system/
├── app.py                     # Flask application with API endpoints
├── run.py                     # Application entry point
├── requirements.txt           # Python dependencies
├── yolov8n.pt                # Pre-trained YOLO model weights
│
├── camera/
│   └── capture.py            # CLI-based capture (legacy)
│
├── models/
│   ├── yolo.py               # YOLO object detection
│   └── feature_extractor.py  # ResNet50 feature extraction
│
├── storage/
│   └── vector_store.py       # FAISS vector database operations
│
├── templates/
│   └── index.html            # Web UI
│
├── static/
│   ├── css/
│   │   └── style.css         # Styling
│   └── js/
│       └── script.js         # Frontend logic
│
├── data/                     # Created at runtime
│   └── products/             # Captured product images
│       └── {product_name}/   # Individual product folders
│
└── storage/                  # Created at runtime
    ├── index.faiss           # FAISS vector index
    └── products.json         # Product metadata
```

## How It Works

### Training Process

1. **Capture**: Camera stream is processed frame by frame
2. **Detection**: YOLO detects and crops the largest object
3. **Filtering**: Only captures images with significant differences (threshold-based)
4. **Storage**: Saves 50 distinct images to `data/products/{product_name}/`
5. **Feature Extraction**: ResNet50 extracts 2048-dimensional feature vectors
6. **Indexing**: Vectors are normalized and added to FAISS index
7. **Metadata**: Product name is mapped to vector indices

### Detection Process

1. **Real-time Processing**: Camera frames are processed every 0.5 seconds
2. **Object Detection**: YOLO identifies and crops objects
3. **Feature Extraction**: Extract feature vector from cropped image
4. **Search**: Query FAISS index for top-k similar vectors
5. **Voting**: Count matches per product
6. **Result**: Return product with most votes and confidence score

## Configuration

### Adjust Capture Settings

In [app.py](app.py):
```python
TARGET_IMAGES = 50      # Number of images to capture per product
DIFF_THRESHOLD = 18     # Minimum difference between consecutive captures
```

### Adjust Detection Settings

In [storage/vector_store.py](storage/vector_store.py):
```python
def search_product(query_vector, top_k=5):  # Number of neighbors to search
```

## Troubleshooting

### Camera Not Working
- Ensure camera permissions are granted in browser
- Check if another application is using the camera
- Try a different browser (Chrome/Edge recommended)

### "No module named 'torch'"
```bash
pip install torch torchvision
```

### "FAISS module not found"
```bash
pip install faiss-cpu
```

### Slow Performance
- Reduce capture frequency in [script.js](static/js/script.js) (line 215):
  ```javascript
  detectIntervalId = setInterval(detectFrame, 1000); // Change from 500 to 1000ms
  ```

### Poor Recognition Accuracy
- Capture more diverse angles during training
- Ensure good lighting conditions
- Train with at least 50 images
- Avoid similar-looking products

## API Endpoints

### POST `/capture`
Capture and save a training image
- Body: `{product_name: string, image: base64}`
- Returns: `{count: number, target: number}`

### POST `/finish`
Finalize training and extract features
- Body: `{product_name: string}`
- Returns: `{status: string, message: string}`

### POST `/detect`
Detect product from image
- Body: `{image: base64}`
- Returns: `{detected: boolean, product_name?: string, confidence?: number, ...}`

### GET `/products`
Get list of all trained products
- Returns: `{products: string[]}`

## Technical Details

- **YOLO Model**: YOLOv8n (nano) for fast inference
- **Feature Model**: ResNet50 pre-trained on ImageNet
- **Vector Dimension**: 2048 (ResNet50 output)
- **Similarity Metric**: Cosine similarity (Inner Product after normalization)
- **Index Type**: FAISS IndexFlatIP (flat inner product)

## Security Considerations

- Product names are sanitized to prevent directory traversal
- Input validation on all endpoints
- Image size is not explicitly limited (consider adding limits)
- Debug mode should be disabled in production

## Future Enhancements

- [ ] Add product deletion functionality
- [ ] Export/import trained models
- [ ] Batch training from uploaded images
- [ ] Confidence threshold settings
- [ ] Multi-object detection support
- [ ] Database integration for persistence
- [ ] User authentication
- [ ] REST API documentation

## License

This project is for educational and development purposes.

## Credits

- **YOLOv8**: Ultralytics
- **ResNet50**: torchvision/PyTorch
- **FAISS**: Facebook AI Research
