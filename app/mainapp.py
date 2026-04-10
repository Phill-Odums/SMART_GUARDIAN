# app/mainapp.py
import time
import logging
import cv2
import numpy as np
from app.camera_manager import CameraManager
from app.detection_manager import DetectionManager
from app.alert_manager import AlertManager
from app.motion_manager import MotionDetector
from app.logger import logger
from app.config import Config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MainApp:
    def __init__(self):
        self.cam_mgr = CameraManager()
        self.detector = DetectionManager(model_path=Config.DEFAULT_MODEL, device=Config.DEVICE, conf=Config.DEFAULT_CONFIDENCE)
        self.alerts = AlertManager(telegram_token=Config.TELEGRAM_TOKEN, telegram_chat_id=Config.TELEGRAM_CHAT_ID)
        self.motion_detectors = {}
        self.last_alert = {}
        self.alert_cooldown = Config.ALERT_COOLDOWN

    def start_stream(self, camera_index=0, width=Config.DEFAULT_WIDTH, height=Config.DEFAULT_HEIGHT, fps=Config.DEFAULT_FPS):
        cam = self.cam_mgr.add_camera(camera_index, width=width, height=height, fps=fps)
        if cam is None:
            return False
        if camera_index not in self.motion_detectors:
            self.motion_detectors[camera_index] = MotionDetector(min_area=Config.MOTION_MIN_AREA)
        self.last_alert.setdefault(camera_index, 0)
        return True

    def stop_stream(self, camera_index=0):
        md = self.motion_detectors.get(camera_index)
        if md:
            md.stop()
        self.cam_mgr.remove_camera(camera_index)

    def _should_alert(self, camera_index, detections):
        if not detections:
            return False
        now = time.time()
        last = self.last_alert.get(camera_index, 0)
        if now - last < self.alert_cooldown:
            return False
        self.last_alert[camera_index] = now
        return True

    def process_frame(self, cam_index=0, conf=None, device=None, model_path=None, use_motion=True):
        ok, frame = self.cam_mgr.get_frame(cam_index)
        if not ok or frame is None:
            return None, []

        if use_motion:
            md = self.motion_detectors.get(cam_index)
            if md:
                motion, annotated_motion = md.detect(frame.copy())
                frame = annotated_motion
                if not motion:
                    return frame, []

        annotated, detections = self.detector.run(frame, conf=conf, device=device, model_path=model_path)
        image_to_use = annotated if annotated is not None else frame

        if detections and self._should_alert(cam_index, detections):
            subject = f"🚨 Camera {cam_index} - {len(detections)} objects"
            body = ", ".join([d["label"] for d in detections[:3]])
            try:
                self.alerts.send_alert(image_to_use, subject=subject, body=body)
            except Exception as e:
                logger.error(f"Alert send failed: {e}")

        return image_to_use, detections

    # UI-facing wrappers
    def process_image_interface(self, image, conf=Config.DEFAULT_CONFIDENCE, device=Config.DEVICE, model_path=None):
        annotated, dets = self.detector.run(image, conf=conf, device=device, model_path=model_path)
        if annotated is None:
            return None, "❌ Detection failed"
        if not dets:
            return annotated, "No objects detected"
        summary = "\n".join([f"{d['label']} ({d['confidence']:.2f})" for d in dets])
        return annotated, f"Detected:\n{summary}"

    def single_capture_interface(self, conf=Config.DEFAULT_CONFIDENCE, device=Config.DEVICE, model_path=None, camera_index=0):
        if not self.start_stream(camera_index):
            return None, "❌ Failed to open camera"
        time.sleep(0.3)
        frame, dets = self.process_frame(camera_index, conf=conf, device=device, model_path=model_path, use_motion=False)
        self.stop_stream(camera_index)
        if frame is None:
            return None, "❌ Failed to capture frame"
        if not dets:
            return frame, "No objects detected"
        summary = "\n".join([f"{d['label']} ({d['confidence']:.2f})" for d in dets])
        return frame, f"Detected:\n{summary}"

    def start_live_stream(self, conf=Config.DEFAULT_CONFIDENCE, device=Config.DEVICE, model_path=None, camera_index=0, enable_alerts=False, resolution="320x240", cooldown=10):
        ok = self.start_stream(camera_index)
        if not ok:
            return None, "🔴 Failed to start", "🔴 Error"
        return None, "🟢 Streaming started", "🟢 Running"

    def stop_live_stream(self):
        self.cam_mgr.stop_all()
        return None, "🔴 Streaming stopped", "🔴 Stopped"

    def process_live_frame(self, conf=Config.DEFAULT_CONFIDENCE, device=Config.DEVICE, model_path=None, enable_alerts=False, cooldown=10, resolution="320x240"):
        frame, dets = self.process_frame(0, conf=conf, device=device, model_path=model_path, use_motion=True)
        label = f"{len(dets)} detections" if dets else "No detections"
        return frame, f"Updated — {label}", "🟢 Running"

    def continuous_stream_generator(self, selected_camera, conf=Config.DEFAULT_CONFIDENCE, device=Config.DEVICE, model_path=None, enable_alerts=False, cooldown=10, resolution="320x240"):
        w, h = map(int, resolution.split("x"))
        cam_id = int(str(selected_camera).split(" - ")[0]) if isinstance(selected_camera, str) else int(selected_camera)
        if not self.start_stream(camera_index=cam_id):
            yield None
            return
        while True:
            frame, dets = self.process_frame(cam_id, conf=conf, device=device, model_path=model_path, use_motion=True)
            if frame is None:
                yield None
                continue
            try:
                resized = cv2.resize(frame, (w,h))
            except Exception:
                resized = frame
            yield resized
