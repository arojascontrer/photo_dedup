from PIL import Image

def tiny_hash(image):
    img = image.resize((16,16)).convert("L")
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    hash_int = 0
    for p in pixels:
        hash_int = (hash_int << 1) | (1 if p > avg else 0)
    return hash_int
