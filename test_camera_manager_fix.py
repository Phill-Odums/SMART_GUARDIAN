import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.camera_manager import CameraManager

class TestCameraManagerFix(unittest.TestCase):
    def setUp(self):
        self.cm = CameraManager()

    @patch('cv2.VideoCapture')
    def test_stop_camera_not_found(self, mock_vc):
        """Test stop_camera does not raise AttributeError if index not in self.cameras."""
        # Ensure cameras is empty
        self.cm.cameras = {}
        try:
            self.cm.stop_camera(99)
        except AttributeError as e:
            self.fail(f"stop_camera raised AttributeError: {e}")

    @patch('cv2.VideoCapture')
    def test_stop_all(self, mock_vc):
        """Test stop_all releases all cameras."""
        mock_cam1 = MagicMock()
        mock_cam2 = MagicMock()
        
        self.cm.cameras = {0: mock_cam1, 1: mock_cam2}
        
        self.cm.stop_all()
        
        mock_cam1.release.assert_called_once()
        mock_cam2.release.assert_called_once()
        self.assertEqual(len(self.cm.cameras), 0)

if __name__ == "__main__":
    unittest.main()
