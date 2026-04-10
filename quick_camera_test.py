import cv2
import logging
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("CameraQuickTest")

def test_camera(index=0):
    print(f"--- Quick Camera Test (Index {index}) ---")
    # Prioritize DSHOW as planned
    backend = cv2.CAP_DSHOW
    print(f"Attempting to open with CAP_DSHOW...")
    
    start_time = time.time()
    cap = cv2.VideoCapture(index, backend)
    
    if cap.isOpened():
        ret, frame = cap.read()
        duration = time.time() - start_time
        if ret:
            print(f"[SUCCESS] Camera {index} opened and read frame in {duration:.2f}s")
        else:
            print(f"[PARTIAL] Camera {index} opened but could not read frame")
        cap.release()
    else:
        print(f"[FAILED ] Camera {index} could not be opened with CAP_DSHOW")

if __name__ == "__main__":
    test_camera(0)
