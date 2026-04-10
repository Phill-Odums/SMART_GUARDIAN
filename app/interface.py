# U-interface
import os
import time
import cv2
import gradio as gr
from pathlib import Path
from app.mainapp import MainApp
from app.config import Config

app = MainApp()
CONFIG_DIR = Path("config")
CONFIG_DIR.mkdir(exist_ok=True)



def camera_choices(max_probe=6):
    choices = []
    for i in range(max_probe):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW if os.name=="nt" else 0)
        if cap.isOpened():
            choices.append(f"{i} - Camera {i}")
        cap.release()
    if not choices:
        choices = [f"{Config.DEFAULT_CAMERA_INDEX} - Camera {Config.DEFAULT_CAMERA_INDEX}"]
    return choices

def parse_cam_label(label):
    if label is None:
        return Config.DEFAULT_CAMERA_INDEX
    try:
        return int(str(label).split(" - ")[0])
    except Exception:
        return Config.DEFAULT_CAMERA_INDEX

def save_system_config(telegram_token, telegram_chat_id, gdrive_json, gdrive_folder, whatsapp_key, whatsapp_phone, username, api_key, phone_numbers):
    if gdrive_json:
        save_path = CONFIG_DIR / "gdrive_service.json"
        with open(save_path, "wb") as f:
            f.write(gdrive_json.read())
        app.alerts.gdrive_json = str(save_path)
        app.alerts.gdrive_folder = gdrive_folder or None
    app.alerts.telegram_token = telegram_token or None
    app.alerts.telegram_chat_id = telegram_chat_id or None
    app.alerts.whatsapp_key = whatsapp_key or None
    app.alerts.whatsapp_phone = whatsapp_phone or None
    app.alerts.username = username or None
    app.alerts.api_key = api_key or None
    if phone_numbers:
        app.alerts.phone_numbers = [num.strip() for num in phone_numbers.split(",") if num.strip()]
    return "Configuration saved ✅"

def analyze_upload(image, conf, device, model_path):
    return app.process_image_interface(image, conf=conf, device=device, model_path=model_path)

def single_capture(selected_camera, conf, device, model_path):
    cam_id = parse_cam_label(selected_camera)
    return app.single_capture_interface(conf=conf, device=device, model_path=model_path, camera_index=cam_id)

def start_stream_ui(selected_camera, conf, device, model_path, enable_alerts, resolution):
    cam_id = parse_cam_label(selected_camera)
    return app.start_live_stream(conf=conf, device=device, model_path=model_path, camera_index=cam_id, enable_alerts=enable_alerts, resolution=resolution)

def stop_stream_ui(selected_camera):
    cam_id = parse_cam_label(selected_camera)
    app.stop_stream(camera_index=cam_id)
    return None, f"Stopped camera {cam_id}", "🔴 Stopped"

def refresh_frame_ui(selected_camera, conf, device, model_path, enable_alerts, cooldown, resolution):
    cam_id = parse_cam_label(selected_camera)
    frame, dets = app.process_frame(cam_index=cam_id, conf=conf, device=device, model_path=model_path, use_motion=True)
    status = f"Camera {cam_id} — {len(dets)} detections" if dets else f"Camera {cam_id} — no detections"
    return frame, status, "🟢 Refreshed"

def switch_camera_ui(selected_camera):
    cam_id = parse_cam_label(selected_camera)+1
    app.cam_mgr.stop_all()
    time.sleep(0.1)
    ok = app.start_stream(camera_index=cam_id)
    return f"Switched to camera {cam_id}" if ok else f"Failed to start camera {cam_id}"

def live_generator(selected_camera, conf, device, model_path, enable_alerts, cooldown, resolution):
    cam_id = parse_cam_label(selected_camera)
    if Config.USE_BROWSER_WEBCAM:
        yield None
        return
    w, h = map(int, resolution.split("x"))
    if not app.start_stream(camera_index=cam_id):
        yield None
        return
    try:
        while True:
            frame, dets = app.process_frame(cam_id, conf=conf, device=device, model_path=model_path, use_motion=True)
            if frame is None:
                yield None
                continue
            try:
                resized = cv2.resize(frame, (w,h))
            except Exception:
                resized = frame
            yield resized
            time.sleep(0.02)
    finally:
        app.stop_stream(cam_id)

def build_ui():
    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🔍 AI SMARTGUARD ")
        with gr.Tab("📷 Image Analysis"):
            with gr.Row():
                with gr.Column():
                    upload = gr.Image(type="pil", label="Upload Image for Detection")
                    conf = gr.Slider(0.1, 0.9, value=Config.DEFAULT_CONFIDENCE, label="Confidence")
                    device = gr.Dropdown(["cpu","0"], value=Config.DEVICE, label="Device")
                    model_path = gr.Textbox(value=Config.DEFAULT_MODEL, label="Model Path")
                    analyze_btn = gr.Button("Analyze")
                with gr.Column():
                    upload_out = gr.Image(label="Result")
                    upload_summary = gr.Markdown("Upload an image and click Analyze")
            analyze_btn.click(fn=analyze_upload, inputs=[upload, conf, device, model_path], outputs=[upload_out, upload_summary])

        with gr.Tab("📸 Single Capture"):
            with gr.Row():
                with gr.Column():
                    cam_choices = camera_choices()
                    sc_camera = gr.Dropdown(choices=cam_choices, label="Camera", value=cam_choices[0])
                    sc_conf = gr.Slider(0.1,0.9, value=Config.DEFAULT_CONFIDENCE, label="Confidence")
                    sc_device = gr.Dropdown(["cpu","0"], value=Config.DEVICE, label="Device")
                    sc_model = gr.Textbox(value=Config.DEFAULT_MODEL, label="Model Path")
                    sc_btn = gr.Button("Capture & Analyze")
                with gr.Column():
                    sc_out = gr.Image()
                    sc_status = gr.Markdown("Status")
            sc_btn.click(fn=single_capture, inputs=[sc_camera, sc_conf, sc_device, sc_model], outputs=[sc_out, sc_status])

        with gr.Tab("🎥 Live Camera"):
            with gr.Row():
                with gr.Column():
                    live_cam_choices = camera_choices()
                    live_cam = gr.Dropdown(choices=live_cam_choices, value=live_cam_choices[0], label="Select Camera")
                    with gr.Row():
                        probe = gr.Button("Refresh Camera List")


                       

                    with gr.Row():

                        live_conf = gr.Slider(0.1,0.9,value=Config.DEFAULT_CONFIDENCE, label="Confidence")
                        live_device = gr.Dropdown(["cpu","0"], value=Config.DEVICE, label="Device")
                        live_model = gr.Textbox(value=Config.DEFAULT_MODEL, label="Model Path")
                        resolution = gr.Dropdown(choices=["320x240","640x480","1280x720"], value="640x480", label="Resolution")


                    with gr.Row():
                        switch = gr.Button("Switch Camera")
                        refresh = gr.Button("Refresh Frame")
                        stop = gr.Button("Stop Stream")

                    with gr.Row():
                        start = gr.Button("Start Stream")
                       

                    with gr.Row():
                        enable_alerts = gr.Checkbox(label="Enable Alerts", value=True)
                        cooldown = gr.Number(value=Config.ALERT_COOLDOWN)
                    
                with gr.Column():
                    if Config.USE_BROWSER_WEBCAM:
                        live_image = gr.Video(sources=["webcam"] , streaming=True, label="Browser Webcam Stream")
                    else:
                        
                        live_cam_feedback = camera_choices()
                        live_cam_feedback = gr.Video(sources=["webcam"], streaming=True, label="Live Camera Recorder")
                        
                        live_image = gr.Image(sources=["webcam"],streaming=True, label="Live Stream Detector")
                    live_status = gr.Markdown("**Status:** 🔴 Stopped")

            probe.click(fn=lambda: (camera_choices(), "Camera list refreshed"), inputs=[], outputs=[live_cam, live_status])
            switch.click(fn=switch_camera_ui, inputs=[live_cam], outputs=[live_status])
            start.click(fn=start_stream_ui, inputs=[live_cam, live_conf, live_device, live_model, enable_alerts, resolution], 
                        outputs=[live_image, live_status, live_status]).then(
                live_generator,
                inputs=[live_cam, live_conf, live_device, live_model, enable_alerts, cooldown, resolution],
                outputs=live_image
            )
            stop.click(fn=stop_stream_ui, inputs=[live_cam], outputs=[live_image, live_status, live_status])
            refresh.click(fn=refresh_frame_ui, inputs=[live_cam, live_conf, live_device, live_model, enable_alerts, cooldown, resolution], 
                          outputs=[live_image, live_status, live_status])

        with gr.Tab("⚙️ System Configuration"):
            with gr.Row():

                with gr.Column():
                    gr.Markdown("### Alert Configuration")
                    username = gr.Textbox(label="Username")
                    api_key = gr.Textbox(label="Alert API Key")
                    sms_phone_numbers = gr.Textbox(label="Alert Phone Numbers (comma separated)")


                with gr.Column():
                    telegram_token = gr.Textbox(label="Telegram Bot Token")
                    telegram_chat_id = gr.Textbox(label="Telegram Chat ID")

                with gr.Column():
                    gdrive_json = gr.File(label="Google Drive Service JSON (upload)")
                    gdrive_folder = gr.Textbox(label="Google Drive Folder ID (optional)")

                with gr.Column():
                    whatsapp_key = gr.Textbox(label="CallMeBot API Key (optional)")
                    whatsapp_phone = gr.Textbox(label="CallMeBot Phone (optional)")

                    with gr.Row():
                        save_cfg = gr.Button("Save Configuration")
                        cfg_status = gr.Markdown("")
            save_cfg.click(fn=save_system_config, inputs=[telegram_token, telegram_chat_id, gdrive_json, gdrive_folder, 
                                                          whatsapp_key, whatsapp_phone, username, api_key, sms_phone_numbers], outputs=[cfg_status])

        with gr.Tab(" 📖 About & User Guide"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### 📝 About This Application")
                    gr.Markdown("""
                        This AI Security Monitor leverages real-time object detection across multiple camera feeds.
                        It integrates motion detection to optimize performance and reduce false alerts.
                        The system supports various alerting mechanisms, including Telegram notifications and local storage of alerts.
                        """)
                    
                            
                    gr.Markdown("""###  Key Features:
                            - (Multi-camera + Motion + Cloud Alerts)
                            - Real-time multi-camera monitoring
                            - Motion detection to minimize false positives
                            - Configurable alerting via Telegram and local storage
                            - User-friendly interface with Gradio**
                            - Easy setup and configuration
                            """)
                    
                    gr.Markdown("""### 📊 System Information
                        **AI Security Monitor System
                        - Model:** YOLOv8n
                        - Default Confidence: 0.25
                        - Target Objects: Person, Animals, Vehicles, etc.
                        - Device: CPU / GPU
                        - Motion Detection: Enabled
                        - Architecture: Real-time Processing
                        - Alert System: Multiple methods (Email, Telegram, Local)
                        - Developed with: Python, OpenCV, Gradio
                        - Version: 1.0.0
                        """)              
                
                with gr.Column():
                    gr.Markdown("""### 🛠️ User Guide & Alert Setup
                        **Getting Started:**
                        - Image Analysis:** Upload any image for object detection
                        - Single Capture:** Test your camera with single frame capture
                        - Live Camera:** Start real-time monitoring
                        - Configure alerts** in System Configuration
                        """)
                    
                    gr.Markdown("""### Alert Setup Options:
                        **📧 Google Drive (Troubleshooting):**
                        - Create a Google Cloud project
                        - Enable Google Drive API
                        - Create Service Account and download JSON           
                        - Upload JSON in System Configuration
                        - Share target Drive folder with Service Account email
                        - Use folder ID in configuration
                            
                        **📱 Telegram (Recommended)**:
                        - Message @BotFather on Telegram
                        - Send `/newbot` command
                        - Follow instructions to create bot
                        - Get bot token from @BotFather
                        - Message your bot and visit:
                        `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates.
                        -NOTE: Replace <YOUR TOKEN> with your bot token.>
                        - **Find your chat ID in the response
                                """)
                        
                        
                    gr.Markdown("""
                        ** Whatsapp (Troubleshooting)**:
                        - Go to Meta for Developers.
                        - Create a Facebook App.
                        - Add WhatsApp Business API.
                        - Get phone number ID and access token.
                                
                        **SMS (Paid):**
                        - Visit https://account.africastalking.com
                        - Create a first time user acount and verify using credentials.
                        - create a production app for SMS service.
                        - Get your API key from the settings page.
                        - Add phone numbers in the System Configuration.
                        - Use comma to separate multiple numbers.
                    
                        **⚠️Troubleshooting:**
                        - Check 'security_alerts' folder for local alerts
                        - Try Telegram for reliable notifications
                        - Use mobile hotspot if network blocks emails
                        """)
                    

    return demo
# Launch the Gradio app with live server settings for sharing to access over the internet on public IP.

demo = build_ui()
demo.launch(server_name="0.0.0.0", server_port=7171,share=True, debug=True)

"""
if __name__ == "__main__":
    demo = build_ui()
    demo.launch(server_name="0.0.0.0", 
                server_port=7860,share=True, debug=True)
"""

