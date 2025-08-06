import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
import queue
import urllib.parse
import hashlib
import time
import os
import logging
from datetime import timedelta
import json

# --- Configuration ---
KUROGAME_API_URLS = {
    "CNBETA_GAME_REVISED": "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10008_Pa0Q0EMFxukjEqX33pF9Uyvdc8MaGPSz/index.json",
    "CNBETA_LAUNCHER": "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10008_Pa0Q0EMFxukjEqX33pF9Uyvdc8MaGPSz/G152/index.json",
    "CNPROD_GAME": "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/index.json",
    "CNPROD_LAUNCHER": "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/G152/index.json",
    "OSBETA_GAME": "https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50013_HiDX7UaJOXpKl3pigJwVxhg5z1wllus5/index.json",
    "OSBETA_LAUNCHER": "https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50013_HiDX7UaJOXpKl3pigJwVxhg5z1wllus5/index.json",
    "OSPROD_GAME": "https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json",
    "OSPROD_LAUNCHER": "https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json",
}

DOWNLOAD_TIMEOUT = 30
CHUNK_SIZE = 8192

# --- Logging Setup ---
logging.basicConfig(filename='downloader.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class WutheringWavesDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Wuthering Waves Downloader - Full URL Support")
        master.geometry("1280x720")
        master.resizable(True, True)
        self._setup()

    def _setup(self):
        self._create_variables()
        self._setup_styles()
        self._create_widgets()

    def _create_variables(self):
        """Initialize all Tkinter variables"""
        self.download_speed_var = tk.StringVar(value="Speed: N/A")
        self.time_remaining_var = tk.StringVar(value="Time left: N/A")
        self.current_file_var = tk.StringVar(value="Current file: N/A")
        self.progress_var = tk.IntVar(value=0)
        self.status_message_var = tk.StringVar(value="Ready")
        self.selected_json_url_key = tk.StringVar()
        self.packages_to_download = []
        self.stop_download_flag = False
        self.download_queue = queue.Queue()
        self.active_download_threads = []

    def _setup_styles(self):
        """Configure UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', font=('Segoe UI', 10), padding=6)
        style.map('TButton', background=[('active', '#e0e0e0')])
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 10))
        style.configure('TProgressbar', thickness=18)
        style.configure('Status.TLabel', font=('Segoe UI', 9, 'italic'), foreground='#555555')
        style.configure('TCombobox', font=('Segoe UI', 10))

    def _create_widgets(self):
        """Create all UI widgets"""
        # Main container
        main_frame = ttk.Frame(self.master, padding=(15, 15, 15, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # JSON Data Section
        json_frame = ttk.LabelFrame(main_frame, text="JSON Data Source", padding=10)
        json_frame.pack(fill=tk.X, pady=5)

        # URL Selection
        selection_frame = ttk.Frame(json_frame)
        selection_frame.pack(fill=tk.X, pady=5)
        ttk.Label(selection_frame, text="API URL:").pack(side=tk.LEFT, padx=(0, 10))
        self.url_combobox = ttk.Combobox(selection_frame, 
                                        textvariable=self.selected_json_url_key,
                                        values=list(KUROGAME_API_URLS.keys()),
                                        state="readonly")
        self.url_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_combobox.set(list(KUROGAME_API_URLS.keys())[0])

        # Load Button
        self.btn_load = ttk.Button(json_frame, 
                                 text="Load JSON Data", 
                                 command=self._load_json_data)
        self.btn_load.pack(pady=(5, 0))

        # Output Display
        output_frame = ttk.LabelFrame(main_frame, 
                                    text="Data Output", 
                                    padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = tk.Text(output_frame, 
                                  wrap=tk.WORD, 
                                  font=("Consolas", 10), 
                                  bg="#ffffff", 
                                  padx=5, pady=5)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)

        # Download Section
        dl_frame = ttk.LabelFrame(main_frame, 
                                text="Download Control", 
                                padding=10)
        dl_frame.pack(fill=tk.X, pady=5)

        ttk.Label(dl_frame, 
                 textvariable=self.current_file_var, 
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.progress_bar = ttk.Progressbar(dl_frame, 
                                          orient='horizontal', 
                                          mode='determinate',
                                          variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X, pady=5)

        stats_frame = ttk.Frame(dl_frame)
        stats_frame.pack(fill=tk.X)
        ttk.Label(stats_frame, 
                 textvariable=self.download_speed_var).pack(side=tk.LEFT)
        ttk.Label(stats_frame, 
                 textvariable=self.time_remaining_var).pack(side=tk.RIGHT)

        # Control Buttons
        btn_frame = ttk.Frame(dl_frame)
        btn_frame.pack(pady=5)
        self.btn_stop = ttk.Button(btn_frame, 
                                  text="Stop Download", 
                                  command=self._stop_download,
                                  state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        self.btn_copy = ttk.Button(btn_frame, 
                                  text="Copy Text", 
                                  command=self._copy_text)
        self.btn_copy.pack(side=tk.LEFT, padx=5)

        # Packages Section
        packages_frame = ttk.LabelFrame(main_frame, 
                                      text="Available Packages", 
                                      padding=10)
        packages_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.canvas = tk.Canvas(packages_frame, 
                               borderwidth=0, 
                               background="#ffffff")
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(packages_frame, 
                                     orient="vertical", 
                                     command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), 
                                window=self.scroll_frame, 
                                anchor="nw",
                                tags="scroll_frame")

        self.scroll_frame.bind("<Configure>", 
                             lambda e: self.canvas.configure(
                                 scrollregion=self.canvas.bbox("all")))
        
        # Status Bar
        ttk.Label(main_frame, 
                 textvariable=self.status_message_var,
                 style='Status.TLabel').pack(fill=tk.X, pady=(5, 0))

        # Configure text tags
        self._configure_text_tags()

    def _configure_text_tags(self):
        """Set up text styling tags for the output box"""
        self.output_text.tag_configure("title", 
                                     font=("Segoe UI", 14, "bold"), 
                                     foreground="#0056b3")
        self.output_text.tag_configure("subtitle", 
                                     font=("Segoe UI", 12, "bold"), 
                                     foreground="#007bff")
        self.output_text.tag_configure("header", 
                                     font=("Segoe UI", 11, "bold"))
        self.output_text.tag_configure("url", 
                                     font=("Consolas", 9), 
                                     foreground="blue")
        self.output_text.tag_configure("success", 
                                     foreground="#28a745")
        self.output_text.tag_configure("warning", 
                                     foreground="#ffc107")
        self.output_text.tag_configure("error", 
                                     foreground="#dc3545")

    def _construct_full_url(self, base_cdn, path):
        """
        Constructs download URL handling both full paths and base paths
        Supports:
        - Full paths (starting with launcher/)
        - Relative paths combined with base_cdn
        """
        if not base_cdn:
            logging.error("Cannot construct URL - missing base CDN")
            return None

        # Ensure base_cdn ends with slash
        base_cdn = base_cdn.rstrip('/') + '/'

        # Handle full paths (starting with launcher/)
        if path.startswith('launcher/'):
            return urllib.parse.quote(base_cdn + path, safe=':/')
        
        # Combine with base_cdn
        return urllib.parse.quote(base_cdn + path, safe=':/')

    def _fetch_json(self, json_url):
        """Fetch and parse JSON data including resources and paths"""
        try:
            # Clear previous data
            self.packages_to_download = []
            for widget in self.scroll_frame.winfo_children():
                widget.destroy()

            # Fetch JSON
            self._update_status(f"Fetching JSON from: {json_url}")
            response = requests.get(json_url, timeout=DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            # Get base CDN
            cdns = data.get("default", {}).get("cdnList", [])
            base_cdn = cdns[0].get('url') if cdns else ""
            
            # Game vs Launcher handling
            is_game = "/game/" in json_url
            
            # Process game packages
            if is_game:
                # Patch configs
                for patch in data.get("default", {}).get("config", {}).get("patchConfig", []):
                    url = self._construct_full_url(base_cdn, patch.get("indexFile", ""))
                    if url:
                        self._add_package("Patch", 
                                        f"Patch v{patch.get('version', '')}", 
                                        url,
                                        patch.get("indexFileMd5", "N/A"),
                                        patch.get("size", 0))

                # Resources
                resources_path = data.get("default", {}).get("resources", "")
                if resources_path:
                    url = self._construct_full_url(base_cdn, resources_path)
                    if url:
                        self._add_package("Resources", 
                                        "Game Resources", 
                                        url, 
                                        "N/A", 
                                        0)

            # Launcher packages
            else:
                # Extract launcher resource information
                launcher_resource = data.get("default", {}).get("resource", {})
                if launcher_resource:
                    url = self._construct_full_url(base_cdn, launcher_resource.get("path", ""))
                    if url:
                        self._add_package("Launcher", 
                                        f"Launcher v{launcher_resource.get('version', 'N/A')}", 
                                        url, 
                                        launcher_resource.get("md5", "N/A"), 
                                        launcher_resource.get("size", 0))

            self._update_status(f"Found {len(self.packages_to_download)} packages")
            return True

        except Exception as e:
            self._update_status(f"Error fetching JSON: {str(e)}", "error")
            logging.error(f"JSON fetch error: {str(e)}")
            return False

    def _add_package(self, pkg_type, name, url, md5, size):
        """Add package to download list and create UI button"""
        self.packages_to_download.append((pkg_type, name, url, md5, size))
        
        # Create download button
        btn = ttk.Button(self.scroll_frame,
                        text=f"{pkg_type}: {name}",
                        command=lambda u=url, m=md5, n=name: self._start_download(u, m, n))
        btn.pack(fill=tk.X, pady=2)

    def _start_download(self, url, md5, name):
        """Start single file download"""
        if not url:
            self._update_status("Invalid download URL", "error")
            return

        # Get save path
        ext = '.json' if url.endswith('.json') else '.zip'
        save_path = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=name.replace(' ', '_') + ext,
            filetypes=[("All files", "*.*")])
        
        if not save_path:
            return

        # Setup download
        self.progress_var.set(0)
        self.current_file_var.set(f"Downloading: {os.path.basename(save_path)}")
        self.stop_download_flag = False
        self.btn_stop.config(state=tk.NORMAL)
        
        # Start download thread
        threading.Thread(
            target=self._download_file,
            args=(url, save_path, md5),
            daemon=True
        ).start()

    def _download_file(self, url, path, expected_md5):
        """Download file with progress tracking and verification"""
        try:
            # Download with progress
            with requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                md5_hash = hashlib.md5()

                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        if self.stop_download_flag:
                            raise Exception("Download stopped by user")
                        
                        if chunk:
                            f.write(chunk)
                            md5_hash.update(chunk)
                            downloaded += len(chunk)
                            
                            # Update progress
                            progress = int((downloaded / total_size) * 100) if total_size > 0 else 0
                            self.progress_var.set(progress)
                            
                            # Calculate speed
                            elapsed = time.time() - start_time
                            speed = downloaded / (elapsed + 0.001)  # bytes/sec
                            
                            # Update UI
                            self.master.after(0, lambda: self._update_speed(
                                speed, 
                                downloaded, 
                                total_size))

            # Verify MD5
            if expected_md5 and expected_md5 != "N/A":
                actual_md5 = md5_hash.hexdigest()
                if actual_md5.lower() == expected_md5.lower():
                    self._update_status("Download complete (MD5 verified)", "success")
                else:
                    self._update_status("Download complete (MD5 MISMATCH!)", "error")
            else:
                self._update_status("Download complete (no MD5 check)", "success")

        except Exception as e:
            self._update_status(f"Download failed: {str(e)}", "error")
            if os.path.exists(path):
                os.remove(path)
        finally:
            self.progress_var.set(0)
            self.btn_stop.config(state=tk.DISABLED)

    def _update_speed(self, speed, downloaded, total_size):
        """Update speed and time remaining display"""
        speed_kb = speed / 1024
        self.download_speed_var.set(f"Speed: {speed_kb:.2f} KB/s")
        
        if total_size > 0 and speed > 0:
            remaining = (total_size - downloaded) / speed
            self.time_remaining_var.set(f"Time left: {timedelta(seconds=int(remaining))}")

    def _update_status(self, message, tag="normal"):
        """Update status message and log output"""
        self.status_message_var.set(message)
        self.output_text.insert(tk.END, message + "\n", tag)
        self.output_text.see(tk.END)
        logging.info(message)

    def _stop_download(self):
        """Stop current download"""
        if messagebox.askyesno("Confirm", "Stop current download?"):
            self.stop_download_flag = True
            self.btn_stop.config(state=tk.DISABLED)

    def _copy_text(self):
        """Copy output text to clipboard"""
        text = self.output_text.get(1.0, tk.END)
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        self._update_status("Text copied to clipboard")

    def _load_json_data(self):
        """Load JSON data from selected URL"""
        url_key = self.selected_json_url_key.get()
        if url_key in KUROGAME_API_URLS:
            # Disable UI during load
            self.btn_load.config(state=tk.DISABLED)
            self.url_combobox.config(state=tk.DISABLED)
            
            # Start load in thread
            threading.Thread(
                target=lambda: self._fetch_and_display(KUROGAME_API_URLS[url_key]),
                daemon=True
            ).start()

    def _fetch_and_display(self, json_url):
        """Fetch JSON and update UI (run in thread)"""
        if self._fetch_json(json_url):
            self.master.after(0, lambda: self._display_data())
        
        # Re-enable UI
        self.master.after(0, lambda: self.btn_load.config(state=tk.NORMAL))
        self.master.after(0, lambda: self.url_combobox.config(state="readonly"))

    def _display_data(self):
        """Display loaded data in the output box"""
        self.output_text.delete(1.0, tk.END)
        
        
        # Display basic info
        url_key = self.selected_json_url_key.get()
        self.output_text.insert(tk.END, f"Wuthering Waves\n", "title")
     #   self.output_text.insert(tk.END, f"URL: {KUROGAME_API_URLS[url_key]}\n\n", "subtitle")
        
        # Display packages
        if self.packages_to_download:
            self.output_text.insert(tk.END, "Available Packages:\n", "header")
            for pkg in self.packages_to_download:
                self.output_text.insert(tk.END, f"{pkg[1]}\n", "normal")
                self.output_text.insert(tk.END, f"  URL: {pkg[2]}\n", "url")
                if pkg[3] != "N/A":
                    self.output_text.insert(tk.END, f"  MD5: {pkg[3]}\n", "normal")
                # --- START OF MODIFICATION ---
                # เพิ่มการแสดงผลขนาด (size) ของแพ็คเกจ
                if pkg[4] > 0: # ตรวจสอบว่า size มีค่ามากกว่า 0 ก่อนแสดง
                    # แปลง bytes เป็น KB, MB, GB เพื่อให้อ่านง่ายขึ้น
                    size_bytes = pkg[4]
                    if size_bytes >= (1024**3): # GB
                        size_display = f"{size_bytes / (1024**3):.2f} GB"
                    elif size_bytes >= (1024**2): # MB
                        size_display = f"{size_bytes / (1024**2):.2f} MB"
                    elif size_bytes >= 1024: # KB
                        size_display = f"{size_bytes / 1024:.2f} KB"
                    else:
                        size_display = f"{size_bytes} bytes"
                    self.output_text.insert(tk.END, f"  Size: {size_display}\n", "normal")
                # --- END OF MODIFICATION ---
                self.output_text.insert(tk.END, "\n", "normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = WutheringWavesDownloaderApp(root)
    root.mainloop()
