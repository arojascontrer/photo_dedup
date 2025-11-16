from PIL import Image
import numpy as np

def deep_similarity(img1: Image.Image, img2: Image.Image, size=(64, 64), tolerance=10) -> float:
    """
    Pixel-by-pixel deep comparison using GRAYSCALE.
    Returns % similarity.
    - `tolerance` allows small luminosity differences (0–255).

    """
    i1 = img1.resize(size).convert("L")
    i2 = img2.resize(size).convert("L")
    
    a1 = np.array(i1, dtype=np.int16)
    a2 = np.array(i2, dtype=np.int16)
    
    matches = np.sum(np.abs(a1 - a2) <= tolerance)
    total = a1.size
    
    return (matches / total) * 100.0
