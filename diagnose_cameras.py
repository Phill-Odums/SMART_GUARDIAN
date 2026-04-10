import cv2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CameraDiagnostics")

def diagnose():
    print("--- Camera Diagnostics ---")
    
    backends = [
        ("CAP_MSMF", cv2.CAP_MSMF),
        ("CAP_DSHOW", cv2.CAP_DSHOW),
        ("CAP_VFW", cv2.CAP_VFW),
        ("CAP_ANY", cv2.CAP_ANY)
    ]
    
    found_any = False
    for i in range(5):
        print(f"\nChecking Index {i}:")
        for name, backend in backends:
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap.isOpened():
                    w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    print(f"  [SUCCESS] Backend {name} opened camera {i} ({int(w)}x{int(h)} @ {fps} FPS)")
                    cap.release()
                    found_any = True
                else:
                    print(f"  [FAILED ] Backend {name} could not open camera {i}")
            except Exception as e:
                print(f"  [ERROR  ] Backend {name} raised error: {e}")
    
    if not found_any:
        print("\nNo cameras found on indices 0-4.")

if __name__ == "__main__":
    diagnose()
