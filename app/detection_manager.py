# app/detection_manager.py
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from app.logger import logger


class DetectionManager:
    def __init__(self, model_path:str=None, device:str="cpu", conf:float=0.50):
        # Default to local project model
        if model_path is None:
            import os
            self.model_path = os.path.join(os.path.dirname(__file__), '..', 'weapon_detect_v5n.pt')
        else:
            self.model_path = model_path
        self.device = device
        self.conf = conf
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Loaded YOLO model: {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None

    def _ensure_bgr(self, image):
        if image is None:
            return None
        if isinstance(image, Image.Image):
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGBA2GRAY)
        if isinstance(image, np.ndarray):
            if image.ndim == 3 and image.shape[2] == 3:
                # Heuristic: if likely RGB, convert to BGR
                # We don't strictly enforce conversion here; YOLO handles RGB or BGR in many versions,
                # but OpenCV display expects BGR.
                return image
        return None

    def _parse_boxes(self, results):
        detections = []
        if not results:
            return detections
        r = results[0]
        for b in r.boxes:
            cls = int(b.cls) if hasattr(b, "cls") else int(b[5])
            conf = float(b.conf) if hasattr(b, "conf") else float(b[4])
            xyxy = b.xyxy.tolist()[0] if hasattr(b.xyxy, "tolist") else b[:4]
            label = r.names.get(cls, str(cls))
            detections.append({"label": label, "confidence": conf , "bbox": xyxy})
        return detections

    def run(self, image, conf=None, device=None, model_path=None):
        if model_path and model_path != self.model_path:
            self.model_path = model_path
            self._load_model()
        
        conf = conf if conf is not None else self.conf
        # Use provided device or instance device
        device = device if device is not None else self.device

        frame = self._ensure_bgr(image)
        if frame is None:
            logger.warning("Received invalid image for detection")
            return None, []

        if self.model is None:
            logger.error("YOLO model not loaded")
            return frame, []

        try:
            # Note: For strict switching, we pass the device to the call. 
            # YOLO internally handles hardware moving if device changed.
            results = self.model(frame, conf=conf, device=device, verbose=False)
            annotated = results[0].plot() if results and len(results)>0 else frame
            detections = self._parse_boxes(results)
            return annotated, detections
        except Exception as e:
            logger.error(f"YOLO detection error: {e}")
            return frame, []



