import sys
import os

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.camera_manager import CameraManager

def test_reproduction():
    cm = CameraManager()
    print("Testing stop_camera(0) when no cameras are added...")
    try:
        cm.stop_camera(0)
        print("SUCCESS: stop_camera(0) called without error (unexpected if bug exists)")
    except AttributeError as e:
        print(f"CONFIRMED BUG: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

if __name__ == "__main__":
    test_reproduction()
