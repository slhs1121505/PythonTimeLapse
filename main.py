import time
import os
import tkinter as tk
from tkinter import ttk
import pyautogui
import cv2
import numpy as np
from datetime import datetime
window = tk.Tk()
window.title("螢幕縮時錄影")
window.geometry("400x400")
window.resizable(False, False)
window.configure(bg="#f0f0f0")
if not os.path.exists("timelapse_images"):
    os.mkdir("timelapse_images")
if not os.path.exists("timelapse_videos"):
    os.mkdir("timelapse_videos")
frames = []
rec = False
start_time = None
style = ttk.Style()
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
style.configure("TButton", font=("Arial", 10, "bold"), padding=5)
style.configure("TEntry", padding=5)
style.configure("TRadiobutton", background="#f0f0f0", font=("Arial", 10))
style.configure("Status.TLabel", font=("Arial", 11), background="#f0f0f0", anchor="center")
style.configure("Countdown.TLabel", font=("Arial", 14, "bold"), background="#f0f0f0", foreground="#0066cc")
main_frame = ttk.Frame(window, style="TFrame")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
settings_frame = ttk.Frame(main_frame, style="TFrame")
settings_frame.pack(fill=tk.X, pady=10)
fps_frame = ttk.Frame(settings_frame, style="TFrame")
fps_frame.pack(fill=tk.X, pady=8)
fps_label = ttk.Label(fps_frame, text="輸出幀率 (FPS):", style="TLabel", width=15)
fps_label.pack(side=tk.LEFT, padx=5)
fps_entry = ttk.Entry(fps_frame, width=10)
fps_entry.pack(side=tk.LEFT, padx=5)
fps_entry.insert(0, "30")
speed_frame = ttk.Frame(settings_frame, style="TFrame")
speed_frame.pack(fill=tk.X, pady=8)
speed_label = ttk.Label(speed_frame, text="縮時倍數:", style="TLabel", width=15)
speed_label.pack(side=tk.LEFT, padx=5)
speed_entry = ttk.Entry(speed_frame, width=10)
speed_entry.pack(side=tk.LEFT, padx=5)
speed_entry.insert(0, "60")
codec_frame = ttk.Frame(settings_frame, style="TFrame")
codec_frame.pack(fill=tk.X, pady=8)
codec_label = ttk.Label(codec_frame, text="選擇編碼:", style="TLabel", width=15)
codec_label.pack(side=tk.LEFT, padx=5)
codec_var = tk.StringVar()
codec_var.set("H264")
codec_h264 = ttk.Radiobutton(codec_frame, text="H264", variable=codec_var, value="H264", style="TRadiobutton")
codec_h264.pack(side=tk.LEFT, padx=(5, 15))
codec_h265 = ttk.Radiobutton(codec_frame, text="H265", variable=codec_var, value="H265", style="TRadiobutton")
codec_h265.pack(side=tk.LEFT, padx=5)
status_frame = ttk.Frame(main_frame, style="TFrame")
status_frame.pack(padx=5, pady=10)
status_text = tk.StringVar()
status_text.set("準備開始")
status_label = ttk.Label(status_frame, textvariable=status_text, style="Status.TLabel")
status_label.pack(pady=5, padx=5, expand=True)
cdtext = tk.StringVar()
cd_label = ttk.Label(status_frame, textvariable=cdtext, style="Countdown.TLabel")
cd_label.pack(pady=5,padx=5)
def upd():
    if rec:
        now = time.time()
        pass_time = now - start_time
        interval = capture_interval - (pass_time%capture_interval)
        cdtext.set(f"下次截圖: {interval:.1f}秒")
        window.after(100, upd)
    else:
        cdtext.set("")
def screenshot():
    global frames, rec
    next = time.time()
    while rec:
        now = time.time()
        if now >= next:
            img = pyautogui.screenshot()
            img = np.array(img)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            frames.append(img)
            next += capture_interval
            status_text.set(f"已拍攝 {len(frames)} 張")
        time.sleep(0.1)
def toggle_recording():
    global rec, start_time, capture_interval, frames
    if not rec:
        fps = int(fps_entry.get())
        speed = int(speed_entry.get())
        rec = True
        frames = []
        start_time = time.time()
        capture_interval = speed / fps
        record_button.config(text="停止錄製", style="Stop.TButton")
        export_button.config(state=tk.DISABLED)
        status_text.set("錄製中...")
        upd()
        import threading
        screenshot_thread = threading.Thread(target=screenshot)
        screenshot_thread.daemon = True
        screenshot_thread.start()
    else:
        rec = False
        record_button.config(text="開始錄製", style="TButton")
        export_button.config(state=tk.NORMAL)
        status_text.set(f"錄製完成，共 {len(frames)} 張圖片")
def export_video():
    if len(frames) == 0:
        return
    fps = int(fps_entry.get())
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    if codec_var.get() == "H264":
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        filename = f"timelapse_videos/video_{current_time}_h264.mp4"
    else:
        fourcc = cv2.VideoWriter_fourcc(*'hev1')
        filename = f"timelapse_videos/video_{current_time}_h265.mp4"
    height, width, _ = frames[0].shape
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    status_text.set("正在製作影片...")
    for i, frame in enumerate(frames):
        out.write(frame)
    out.release()
    status_text.set(f"影片已儲存: {filename}")
style.configure("Stop.TButton", background="#ff6b6b")
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(status_frame, orient="horizontal", length=300, mode="determinate", variable=progress_var)
button_frame = ttk.Frame(main_frame, style="TFrame")
button_frame.pack(pady=20)
record_button = ttk.Button(button_frame, text="開始錄製", command=toggle_recording, width=15)
record_button.pack(side=tk.LEFT, padx=10)
export_button = ttk.Button(button_frame, text="匯出影片", command=export_video, width=15)
export_button.pack(side=tk.LEFT, padx=10)
window.mainloop()
