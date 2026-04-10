import traceback
import sys

try:
    import web.app
    print("SUCCESS: web.app imported")
except ImportError as e:
    print(f"IMPORT ERROR: {e}")
except Exception as e:
    print(f"OTHER ERROR: {traceback.format_exc()}")
