import os
import sys
import time


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask, render_template, Response, request, jsonify
from app.camera_manager import CameraManager
from app.detection_manager import DetectionManager
from app.alert_manager import AlertManager
from app.motion_manager import MotionDetector as MotionManager
from app.settings_manager import settings_manager

# Initialize Flask App
# We specify the template and static folders explicitly to point to the 'web' directory structure.
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Initialize Core Managers
detection_manager = DetectionManager()
alert_manager = AlertManager()
camera_manager = CameraManager(detection_manager, alert_manager)
motion_manager = MotionManager()

# AI toggle state (camera_id -> bool)
camera_ai_state = {0: True, 1: False, 2: False, 3: False}

# --- View Routing (UI Pages) ---
@app.route('/')
def dashboard():
    """Render the main dashboard page."""
    return render_template('dashboard.html')

@app.route('/cameras')
def cameras_page():
    """Render the camera management page."""
    return render_template('cameras.html')

@app.route('/alerts')
def alerts_page():
    """Render the alert timeline page."""
    return render_template('alerts.html')

@app.route('/history')
def history_page():
    """Render the detection history database page."""
    return render_template('history.html')

@app.route('/settings')
def settings_page():
    """Render the system configuration page."""
    return render_template('settings.html')


# --- API & Core Endpoints ---

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    """
    Video streaming route. Put this in the src attribute of an img tag.
    Generates a stream of JPEG frames directly from the DetectionManager.
    """
    def generate_frames(cam_id):
        # We start the stream here if not started.
        camera_manager.start_camera(cam_id)
        
        # Synchronize AI state
        camera_manager.set_ai_state(cam_id, camera_ai_state.get(cam_id, False))
        
        while True:
            frame_bytes = camera_manager.get_latest_jpeg(cam_id)
            if frame_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                # Wait for next theoretical frame (~30 FPS)
                time.sleep(1/30)
            else:
                # If camera is just starting or no frame ready
                time.sleep(0.1)

    return Response(generate_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_ai', methods=['POST'])
def toggle_ai():
    data = request.json
    cam_id = data.get('camera_id', 0)
    current_state = camera_ai_state.get(cam_id, False)
    new_state = not current_state
    camera_ai_state[cam_id] = new_state
    camera_manager.set_ai_state(cam_id, new_state)
    return jsonify({"success": True, "ai_enabled": new_state})

@app.route('/start_camera', methods=['POST'])
def start_camera():
    data = request.json
    cam_id = data.get('camera_id', 0)
    success = camera_manager.start_camera(cam_id)
    return jsonify({"success": success})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    data = request.json
    cam_id = data.get('camera_id', 0)
    success = camera_manager.stop_camera(cam_id)
    return jsonify({"success": success})


@app.route('/stop_all', methods=['POST'])
def stop_all():
    camera_manager.stop_all()
    return jsonify({"success": True})


import sqlite3
import random
from datetime import datetime, timedelta

def get_db_connection():
    db_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'database', 'detections.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

import base64
from PIL import Image
import io

@app.route('/upload', methods=['POST'])
def handle_upload():
    # Single image detection
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No image provided"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400

    try:
        # Read the image
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes))
        
        # Run detection
        annotated_frame, detections = detection_manager.run(image)
        
        # Convert annotated frame back to base64 to send to UI
        import cv2
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        b64_img = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "success": True, 
            "detections": detections,
            "image": f"data:image/jpeg;base64,{b64_img}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/snapshot/<int:camera_id>', methods=['POST'])
def take_snapshot(camera_id):
    """Grab a single frame from the camera, run detection, and return."""
    try:
        ret, frame = camera_manager.get_frame(camera_id)
        if not ret or frame is None:
            return jsonify({"success": False, "error": "Could not read from camera"}), 500
            
        annotated_frame, detections = detection_manager.run(frame)
        
        import cv2
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        b64_img = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "success": True, 
            "detections": detections,
            "image": f"data:image/jpeg;base64,{b64_img}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/get_detections')
def get_detections():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM detection_history ORDER BY timestamp DESC LIMIT 200")
        rows = cur.fetchall()
        detections = [dict(ix) for ix in rows]
        conn.close()
        return jsonify({"detections": detections})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/get_alerts')
def get_alerts():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 100")
        rows = cur.fetchall()
        alerts = [dict(ix) for ix in rows]
        conn.close()
        return jsonify({"alerts": alerts})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/alert_image')
def alert_image():
    """Serve a saved alert snapshot by absolute file path."""
    import mimetypes
    from flask import send_file, abort
    path = request.args.get('path', '')
    if not path or not os.path.isfile(path):
        abort(404)
    mime = mimetypes.guess_type(path)[0] or 'image/jpeg'
    return send_file(path, mimetype=mime)

@app.route('/delete_alert/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/clear_alerts', methods=['DELETE'])
def clear_alerts():
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM alerts")
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/verify_password', methods=['POST'])
def verify_password():
    data = request.json
    password = data.get('password', '')
    stored_password = settings_manager.settings.get('system_password', 'admin')
    
    if password == stored_password:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": "Invalid password"}), 401

@app.route('/api/settings', methods=['GET', 'POST'])
def manage_settings():
    if request.method == 'GET':
        settings = settings_manager.settings.copy()
        # Hide password in API response for basic security
        if "system_password" in settings:
            settings["system_password"] = "******"
        return jsonify(settings)
    elif request.method == 'POST':
        data = request.json
        auth_password = data.get('auth_password', '')
        
        # Verify password
        stored_password = settings_manager.settings.get('system_password', 'admin')
        if auth_password != stored_password:
            return jsonify({"success": False, "error": "Invalid security password"}), 403

        # Remove auth_password from settings blob
        new_settings = {k: v for k, v in data.items() if k != 'auth_password'}
        
        # If new password is provided, update it
        if "new_system_password" in new_settings:
            val = new_settings.pop("new_system_password")
            if val and len(val) >= 4:
                new_settings["system_password"] = val

        if settings_manager.save_settings(new_settings):
            # Dynamically update the detection manager confidence if it changed
            if "confidence_threshold" in new_settings:
                new_conf = float(new_settings["confidence_threshold"]) / 100.0
                detection_manager.conf = new_conf

            return jsonify({"success": True, "message": "Settings saved successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to save settings"}), 500

@app.route('/get_stats')
def get_stats():
    now = datetime.now()
    monday = now - timedelta(days=now.weekday())  # Monday of current week
    labels = [(monday + timedelta(days=i)).strftime("%A") for i in range(7)]
    day_dates = [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    # Query real counts from DB
    person_counts = [0] * 7
    weapon_counts = [0] * 7
    total_detections = 0
    total_alerts = 0

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Per-day detection breakdown for chart (Mon-Sun this week)
        cur.execute("""
            SELECT DATE(timestamp) as day, object_class, COUNT(*) as cnt
            FROM detection_history
            WHERE DATE(timestamp) >= ? AND DATE(timestamp) <= ?
            GROUP BY day, object_class
        """, (day_dates[0], day_dates[6]))
        for row in cur.fetchall():
            if row['day'] in day_dates:
                idx = day_dates.index(row['day'])
                cls = (row['object_class'] or '').lower()
                if cls == 'person':
                    person_counts[idx] += row['cnt']
                else:
                    weapon_counts[idx] += row['cnt']

        # Total detections ever
        cur.execute("SELECT COUNT(*) as cnt FROM detection_history")
        total_detections = cur.fetchone()['cnt'] or 0

        # Total alerts ever
        cur.execute("SELECT COUNT(*) as cnt FROM alerts")
        total_alerts = cur.fetchone()['cnt'] or 0

        conn.close()
    except Exception as e:
        pass  # Fallback: all zeros

    active_cams = sum(1 for cam_id in range(4) if camera_manager.get_frame(cam_id)[0])

    return jsonify({
        "labels": labels,
        "datasets": [
            {
                "label": "Human",
                "data": person_counts,
                "borderColor": "#a855f7",
                "backgroundColor": "rgba(168, 85, 247, 0.1)",
                "fill": True,
                "tension": 0.4
            },
            {
                "label": "Weapon",
                "data": weapon_counts,
                "borderColor": "#0ea5e9",
                "backgroundColor": "rgba(14, 165, 233, 0.1)",
                "fill": True,
                "tension": 0.4
            }
        ],
        "summary": {
            "active_cameras": active_cams,
            "total_detections": total_detections,
            "alerts_triggered": total_alerts,
            "uptime": "99.9%"
        }
    })

if __name__ == '__main__':
    # Run server on 0.0.0.0 to allow external access within local network
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
