# app/camera_manager.py
import cv2
import threading
import time
from typing import Tuple, Optional
from app.logger import logger
from app.settings_manager import settings_manager

class ThreadedCamera:
    """
    High-Performance Threaded Camera
    - Handles capture, optional AI processing, and JPEG encoding in background.
    - Resolves 'frame skipping' by decoupling acquisition from streaming.
    """
    def __init__(self, index, detection_manager=None, alert_manager=None, width=1280, height=720, fps=30):
        self.index = index
        self.width = width
        self.height = height
        self.fps = fps
        self.detection_manager = detection_manager
        self.alert_manager = alert_manager
        
        self.cap = None
        self.raw_frame = None
        self.processed_frame = None
        self.jpeg_bytes = None
        
        self.stopped = False
        self.ai_enabled = False
        self.lock = threading.Lock()
        
        # Performance control
        self.last_inference_time = 0
        self.inference_fps = 5 # Run AI at 5 FPS to save CPU, while streaming at 30 FPS.

    def _open_camera(self):
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        for backend in backends:
            try:
                cam = cv2.VideoCapture(self.index, backend)
                if cam.isOpened():
                    cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                    cam.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    return cam
                cam.release()
            except Exception: pass
        return cv2.VideoCapture(self.index)

    def start(self):
        self.cap = self._open_camera()
        if not self.cap or not self.cap.isOpened():
            return False
            
        self.stopped = False
        # Thread 1: Fast Capture
        threading.Thread(target=self._capture_loop, daemon=True).start()
        # Thread 2: Encoding & AI (The Bottleneck Thread)
        threading.Thread(target=self._processing_loop, daemon=True).start()
        return True

    def _capture_loop(self):
        """Continuously grab the latest raw frame from hardware."""
        while not self.stopped:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.raw_frame = frame
            else:
                time.sleep(0.1)
            time.sleep(0.005)

    def _processing_loop(self):
        """Handle AI detection and JPEG encoding at a controlled rate."""
        import time
        last_alert_time = 0
        
        while not self.stopped:
            with self.lock:
                frame = self.raw_frame.copy() if self.raw_frame is not None else None
            
            if frame is not None:
                display_frame = frame
                
                # AI Inference logic
                if self.ai_enabled and self.detection_manager:
                    now = time.time()
                    # Throttle AI to avoid pegging CPU, but keep streaming fast
                    if now - self.last_inference_time > (1.0 / self.inference_fps):
                        device = settings_manager.settings.get("inference_device", "cpu")
                        display_frame, detections = self.detection_manager.run(frame, device=device)
                        self.last_inference_time = now
                        
                        # Trigger alerts if objects found (filtering based on target_classes settings)
                        if detections and self.alert_manager:
                            target_classes = settings_manager.settings.get("target_classes", {})
                            filtered_detections = [
                                d for d in detections 
                                if target_classes.get(d['label'].lower().strip(), True)
                            ]
                            
                            if filtered_detections:
                                cooldown = settings_manager.settings.get("alert_cooldown", 30)
                                if now - last_alert_time >= cooldown:
                                    last_alert_time = now
                                    logger.info(f"Triggering alert. Detections: {[d['label'] for d in detections]}, Filtered: {[d['label'] for d in filtered_detections]}")
                                    self._trigger_async_alert(display_frame.copy(), filtered_detections)
                            else:
                                if detections:
                                    logger.debug(f"Filtered out all detections: {[d['label'] for d in detections]}")

                # JPEG Encoding (Done once per frame for all clients)
                success, buffer = cv2.imencode('.jpg', display_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if success:
                    with self.lock:
                        self.jpeg_bytes = buffer.tobytes()
            
            # Control processing speed to match desired FPS (around 30)
            time.sleep(1.0 / self.fps)

    def _trigger_async_alert(self, frame, detections):
        if not self.alert_manager: return
        labels = ", ".join(set(d["label"] for d in detections))
        subject = f"ALERT: {labels} on Camera {self.index}"
        body = f"Detected: {labels}\nTime: {time.strftime('%H:%M:%S')}"
        import threading
        threading.Thread(
            target=self.alert_manager.send_alert,
            args=(frame,),
            kwargs={"subject": subject, "body": body, "camera_id": str(self.index), "detections": detections},
            daemon=True
        ).start()

    def get_jpeg(self) -> Optional[bytes]:
        with self.lock:
            return self.jpeg_bytes

    def set_ai(self, state: bool):
        self.ai_enabled = state

    def get_frame(self) -> Tuple[bool, Optional[cv2.Mat]]:
        with self.lock:
            if self.raw_frame is not None:
                return True, self.raw_frame.copy()
        return False, None

    def stop(self):
        self.stopped = True
        if self.cap:
            self.cap.release()

class CameraManager:
    def __init__(self, detection_manager=None, alert_manager=None):
        self.cameras = {} 
        self.detection_manager = detection_manager
        self.alert_manager = alert_manager
        logger.info("CameraManager initialized (Ultra-Smooth High-Res Mode)")

    def add_camera(self, index:int=0, width:int=1280, height:int=720, fps:int=30) -> bool:
        if index in self.cameras:
            self.remove_camera(index)
        
        t_cam = ThreadedCamera(index, self.detection_manager, self.alert_manager, width, height, fps)
        if t_cam.start():
            self.cameras[index] = t_cam
            return True
        return False

    def get_latest_jpeg(self, index:int=0) -> Optional[bytes]:
        t_cam = self.cameras.get(index)
        return t_cam.get_jpeg() if t_cam else None

    def set_ai_state(self, index:int, state:bool):
        t_cam = self.cameras.get(index)
        if t_cam:
            t_cam.set_ai(state)

    def remove_camera(self, index:int=0):
        t_cam = self.cameras.get(index)
        if t_cam:
            t_cam.stop()
            del self.cameras[index]

    def start_camera(self, index:int=0) -> bool:
        if index not in self.cameras:
            return self.add_camera(index)
        return True

    def get_frame(self, index:int=0) -> Tuple[bool, Optional[cv2.Mat]]:
        t_cam = self.cameras.get(index)
        if t_cam:
            return t_cam.get_frame()
        return False, None

    def stop_camera(self, index:int=0):
        self.remove_camera(index)

    def stop_all(self):
        for index in list(self.cameras.keys()):
            self.remove_camera(index)
        logger.info("All cameras stopped")
