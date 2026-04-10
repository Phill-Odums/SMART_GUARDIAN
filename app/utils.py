# app/utils.py
import os
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
from app.logger import logger

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def timestamp_file():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def to_jpg_bytes(image, quality:int=90):
    """
    Accepts: OpenCV BGR np.ndarray, PIL.Image, or RGB ndarray.
    Returns JPEG bytes or raises ValueError.
    """
    if image is None:
        raise ValueError("No image provided")

    # PIL -> BGR
    if isinstance(image, Image.Image):
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)

    if isinstance(image, np.ndarray):
        # If shape is HxWx3, assume color image.
        if image.ndim == 3 and image.shape[2] == 3:
            # Heuristic: if mean of channel 0 less than channel 2, likely RGB -> convert to BGR
            # But safer: if dtype is uint8 and common ordering, allow as-is if using OpenCV.
            try:
                # If it looks like RGB (common for PIL->np.array), convert:
                # We'll convert from RGB to BGR if the mean red is larger than blue.
                if image[...,0].mean() < image[...,2].mean():
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            except Exception:
                pass
        # encode
        ret, buf = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        if not ret:
            raise ValueError("Failed to encode image to JPEG")
        return buf.tobytes()

    raise ValueError("Unsupported image type for to_jpg_bytes")

def save_jpg_bytes(image_bytes, folder, prefix="alert"):
    ensure_dir(folder)
    filename = f"{prefix}_{timestamp_file()}.jpg"
    path = os.path.join(folder, filename)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return path
