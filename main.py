import tkinter as tk
from tkinter import ttk, messagebox
import yt_dlp as youtube_dl
import threading
import re
import os
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    full_path = os.path.join(base_path, relative_path)
    if os.path.exists(full_path):
        return full_path
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, relative_path)

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("600x300")
        
        # Verify FFmpeg exists
        ffmpeg_path = resource_path(os.path.join('ffmpeg', 'bin'))
        if not os.path.exists(os.path.join(ffmpeg_path, 'ffmpeg.exe')):
            messagebox.showerror("Error", f"FFmpeg not found in {ffmpeg_path}")
            root.destroy()
            return
        
        # Create and configure main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create download directory if it doesn't exist
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "YouTubeDownloads")
        os.makedirs(self.download_dir, exist_ok=True)
        
        # URL Entry
        self.url_label = ttk.Label(self.main_frame, text="YouTube URL:")
        self.url_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        
        # Download Type Selection
        self.type_label = ttk.Label(self.main_frame, text="Download Type:")
        self.type_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.type_var = tk.StringVar(value="audio")
        self.type_combo = ttk.Combobox(self.main_frame, textvariable=self.type_var, 
                                     values=["Audio Only", "Video with Audio", "Video without Audio"])
        self.type_combo.set("Audio Only")
        self.type_combo.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        self.type_combo.bind('<<ComboboxSelected>>', self.update_quality_options)
        
        # Quality Selection
        self.quality_label = ttk.Label(self.main_frame, text="Quality:")
        self.quality_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        self.quality_var = tk.StringVar(value="192")
        self.quality_combo = ttk.Combobox(self.main_frame, textvariable=self.quality_var)
        self.quality_combo.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=(0, 10))
        
        # Set initial quality options
        self.update_quality_options()
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Download Button
        self.download_button = ttk.Button(self.main_frame, text="Download", command=self.start_download)
        self.download_button.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3)

    def update_quality_options(self, event=None):
        download_type = self.type_var.get()
        if download_type == "Audio Only":
            self.quality_combo['values'] = ["64 kbps", "128 kbps", "192 kbps", "256 kbps", "320 kbps"]
            self.quality_combo.set("192 kbps")
        else:
            self.quality_combo['values'] = ["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p"]
            self.quality_combo.set("720p")

    def validate_url(self, url):
        youtube_regex = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
        return bool(re.match(youtube_regex, url))

    def get_download_options(self):
        download_type = self.type_var.get()
        quality = self.quality_var.get()
        
        if download_type == "Audio Only":
            quality_value = quality.split()[0]  # Extract numeric value from "XXX kbps"
            return {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality_value,
                }],
                'ffmpeg_location': resource_path(os.path.join('ffmpeg', 'bin')),
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            }
        else:
            # Convert quality string to vertical resolution
            resolution_map = {
                "144p": "144", "240p": "240", "360p": "360",
                "480p": "480", "720p": "720", "1080p": "1080",
                "1440p": "1440", "2160p": "2160"
            }
            resolution = resolution_map.get(quality, "720")
            
            format_str = (f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]' 
                         if download_type == "Video with Audio" 
                         else f'bestvideo[height<={resolution}]')
            
            return {
                'format': format_str,
                'ffmpeg_location': resource_path(os.path.join('ffmpeg', 'bin')),
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            }

    def download_content(self):
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            self.status_var.set("Ready to download")
            self.download_button['state'] = 'normal'
            self.progress.stop()
            return
            
        if not self.validate_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            self.status_var.set("Ready to download")
            self.download_button['state'] = 'normal'
            self.progress.stop()
            return

        ydl_opts = self.get_download_options()

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_var.set("Download completed!")
            messagebox.showinfo("Success", f"Content downloaded successfully to:\n{self.download_dir}")
        except Exception as e:
            self.status_var.set("Download failed!")
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        finally:
            self.download_button['state'] = 'normal'
            self.progress.stop()

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            self.status_var.set(f"Downloading... {d.get('_percent_str', 'N/A')}")
        elif d['status'] == 'finished':
            self.status_var.set("Processing content...")

    def start_download(self):
        self.download_button['state'] = 'disabled'
        self.status_var.set("Starting download...")
        self.progress.start()
        thread = threading.Thread(target=self.download_content)
        thread.daemon = True
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()