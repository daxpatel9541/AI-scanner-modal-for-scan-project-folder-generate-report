import faiss
import json
import numpy as np
import os

VECTOR_SIZE = 2048

def save_product(product_name, vectors):
    """Save product vectors to FAISS index and metadata"""
    os.makedirs("storage", exist_ok=True)

    if os.path.exists("storage/index.faiss"):
        index = faiss.read_index("storage/index.faiss")
    else:
        index = faiss.IndexFlatIP(VECTOR_SIZE)

    vectors = np.array(vectors).astype("float32")
    vectors /= np.linalg.norm(vectors, axis=1, keepdims=True)

    # Get the starting index before adding new vectors
    start_idx = index.ntotal

    index.add(vectors)
    faiss.write_index(index, "storage/index.faiss")

    # Load existing metadata
    meta = {}
    if os.path.exists("storage/products.json"):
        with open("storage/products.json", "r") as f:
            meta = json.load(f)

    # Map all vector indices to product name
    for i in range(len(vectors)):
        meta[str(start_idx + i)] = product_name

    with open("storage/products.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"✅ Saved {len(vectors)} vectors for product: {product_name}")


def search_product(query_vector, top_k=5):
    """Search for similar products in FAISS index"""
    if not os.path.exists("storage/index.faiss"):
        return None

    if not os.path.exists("storage/products.json"):
        return None

    # Load index and metadata
    index = faiss.read_index("storage/index.faiss")
    with open("storage/products.json", "r") as f:
        meta = json.load(f)

    # Normalize query vector
    query_vector = np.array([query_vector]).astype("float32")
    query_vector /= np.linalg.norm(query_vector, axis=1, keepdims=True)

    # Search in FAISS
    distances, indices = index.search(query_vector, top_k)

    # Count votes for each product
    product_votes = {}
    product_scores = {}

    for dist, idx in zip(distances[0], indices[0]):
        if str(idx) in meta:
            product_name = meta[str(idx)]
            if product_name not in product_votes:
                product_votes[product_name] = 0
                product_scores[product_name] = []
            product_votes[product_name] += 1
            product_scores[product_name].append(float(dist))

    # Get the product with most votes
    if not product_votes:
        return None

    best_product = max(product_votes, key=product_votes.get)
    avg_score = np.mean(product_scores[best_product])
    confidence = (product_votes[best_product] / top_k) * 100

    return {
        "product_name": best_product,
        "confidence": round(confidence, 2),
        "similarity_score": round(avg_score, 4),
        "votes": f"{product_votes[best_product]}/{top_k}"
    }
