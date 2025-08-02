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
from datetime import timedelta # For better time formatting
import json

# --- Configuration ---
# Kurogame (Wuthering Waves) API URLs
# Storing both 'launcher' and 'game' (resources) URLs
KUROGAME_API_URLS = {
    # Based on the provided JSON, this URL seems to be the source for game resources
    "CNBETA_GAME_REVISED": "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10008_Pa0Q0EMFxukjEqX33pF9Uyvdc8MaGPSz/index.json",
    # Other URLs remain as they might have different structures or be for launcher
    "CNBETA_LAUNCHER": "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10008_Pa0Q0EMFxukjEqX33pF9Uyvdc8MaGPSz/G152/index.json",
    "CNPROD_GAME": "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/game/G152/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/index.json",
    "CNPROD_LAUNCHER": "https://prod-cn-alicdn-gamestarter.kurogame.com/launcher/launcher/10003_Y8xXrXk65DqFHEDgApn3cpK5lfczpFx5/G152/index.json",
    "OSBETA_GAME": "https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50013_HiDX7UaJOXpKl3pigJwVxhg5z1wllus5/index.json",
    "OSBETA_LAUNCHER": "https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50013_HiDX7UaJOXpKl3pigJwVxhg5z1wllus5/index.json",
    "OSPROD_GAME": "https://prod-alicdn-gamestarter.kurogame.com/launcher/game/G153/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json",
    "OSPROD_LAUNCHER": "https://prod-volcdn-gamestarter.kurogame.net/launcher/launcher/50004_obOHXFrFanqsaIEOmuKroCcbZkQRBC7c/index.json",
}

DOWNLOAD_TIMEOUT = 30 # seconds for each request
CHUNK_SIZE = 8192 # bytes for file chunks

# --- Logging Setup ---
logging.basicConfig(filename='downloader.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class WutheringWavesDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Wuthering Waves JSON Viewer & Downloader")
        master.geometry("900x750") # Slightly larger window
        master.resizable(True, True)

        self._setup_variables()
        self._setup_styles()
        self._create_widgets()

        self.packages_to_download = [] # List to store (type, name, url, md5, size) for download buttons
        self.stop_download_flag = False
        self.download_queue = queue.Queue()
        self.active_download_threads = []

    def _setup_variables(self):
        """Initializes Tkinter variables for dynamic UI updates."""
        self.download_speed_var = tk.StringVar(value="ความเร็ว: N/A")
        self.time_remaining_var = tk.StringVar(value="เวลาที่เหลือ: N/A")
        self.current_file_var = tk.StringVar(value="ไฟล์ปัจจุบัน: N/A")
        self.progress_var = tk.IntVar(value=0)
        self.status_message_var = tk.StringVar(value="พร้อมใช้งาน")
        self.selected_json_url_key = tk.StringVar() # To hold the selected URL key

    def _setup_styles(self):
        """Configures ttk styles for a consistent look."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', font=('Segoe UI', 10), padding=8)
        style.map('TButton', background=[('active', '#e0e0e0')])
        style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 11))
        style.configure('TProgressbar', thickness=15)
        style.configure('Status.TLabel', font=('Segoe UI', 10, 'italic'), foreground='#555555')
        style.configure('TCombobox', font=('Segoe UI', 10)) # Added style for Combobox

    def _create_widgets(self):
        """Creates and lays out all GUI widgets."""
        main_frame = ttk.Frame(self.master, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- JSON Data Section ---
        json_frame = ttk.LabelFrame(main_frame, text="ข้อมูล JSON", padding=10)
        json_frame.pack(fill=tk.X, pady=10)

        # URL Selection Combobox
        url_selection_frame = ttk.Frame(json_frame)
        url_selection_frame.pack(fill=tk.X, pady=10)
        ttk.Label(url_selection_frame, text="🔗 เลือก URL JSON:", font=("Segoe UI", 11)).pack(side=tk.LEFT, padx=(0, 10))
        self.url_combobox = ttk.Combobox(url_selection_frame, textvariable=self.selected_json_url_key, state="readonly")
        self.url_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.url_combobox.config(values=list(KUROGAME_API_URLS.keys())) # Populate with all URL keys
        if KUROGAME_API_URLS:
            self.url_combobox.set(list(KUROGAME_API_URLS.keys())[0]) # Set default selection

        ttk.Label(json_frame, text="🔄 คลิกเพื่อโหลดข้อมูลจาก URL ที่เลือก:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.btn_load = ttk.Button(json_frame, text="โหลด JSON", command=self._load_json_data)
        self.btn_load.pack(pady=5)

        # --- Output Text Area ---
        output_frame = ttk.LabelFrame(main_frame, text="รายละเอียดข้อมูลและ Log", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.output_text = tk.Text(output_frame, wrap=tk.WORD, font=("Consolas", 10), height=15,
                                   bg="#ffffff", fg="#333333", relief=tk.FLAT, padx=5, pady=5)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(output_frame, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)

        # --- Download Progress and Controls Section ---
        download_frame = ttk.LabelFrame(main_frame, text="สถานะการดาวน์โหลด", padding=10)
        download_frame.pack(fill=tk.X, pady=10)

        ttk.Label(download_frame, textvariable=self.current_file_var, font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 5))

        self.progress_bar = ttk.Progressbar(download_frame, orient='horizontal', mode='determinate', variable=self.progress_var)
        self.progress_bar.pack(fill=tk.X, pady=5)

        status_labels_frame = ttk.Frame(download_frame)
        status_labels_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(status_labels_frame, textvariable=self.download_speed_var, font=("Segoe UI", 10)).pack(side=tk.LEFT, expand=True, anchor="w")
        ttk.Label(status_labels_frame, textvariable=self.time_remaining_var, font=("Segoe UI", 10)).pack(side=tk.RIGHT, expand=True, anchor="e")

        # --- Control Buttons (General) ---
        button_frame = ttk.Frame(download_frame)
        button_frame.pack(pady=5)

        self.btn_stop = ttk.Button(button_frame, text="⏸️ หยุดดาวน์โหลด", command=self._stop_download, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)

        self.btn_copy = ttk.Button(button_frame, text="📋 คัดลอกข้อความ", command=self._copy_text)
        self.btn_copy.pack(side=tk.LEFT, padx=5)

        # --- Dynamic Download Buttons Container ---
        self.dynamic_buttons_frame = ttk.LabelFrame(main_frame, text="เลือกแพ็คเกจดาวน์โหลด", padding=10)
        self.dynamic_buttons_frame.pack(fill=tk.X, pady=10)
        self.dynamic_buttons_canvas = tk.Canvas(self.dynamic_buttons_frame, borderwidth=0, background="#f0f0f0")
        self.dynamic_buttons_scrollframe = ttk.Frame(self.dynamic_buttons_canvas)
        self.dynamic_buttons_scrollbar = ttk.Scrollbar(self.dynamic_buttons_frame, orient="vertical", command=self.dynamic_buttons_canvas.yview)
        self.dynamic_buttons_canvas.configure(yscrollcommand=self.dynamic_buttons_scrollbar.set)

        self.dynamic_buttons_scrollbar.pack(side="right", fill="y")
        self.dynamic_buttons_canvas.pack(side="left", fill="both", expand=True)
        self.dynamic_buttons_canvas.create_window((0, 0), window=self.dynamic_buttons_scrollframe, anchor="nw", tags="self.dynamic_buttons_scrollframe")

        self.dynamic_buttons_scrollframe.bind("<Configure>", lambda e: self.dynamic_buttons_canvas.configure(scrollregion=self.dynamic_buttons_canvas.bbox("all")))
        self.dynamic_buttons_canvas.bind_all("<MouseWheel>", self._on_mousewheel)


        # --- Global Status Message ---
        ttk.Label(main_frame, textvariable=self.status_message_var, style='Status.TLabel').pack(fill=tk.X, pady=(5, 0))

    def _on_mousewheel(self, event):
        self.dynamic_buttons_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _update_status(self, message, log_level=logging.INFO):
        """Updates the status message in the GUI and logs it."""
        self.status_message_var.set(message)
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        if log_level == logging.INFO:
            logging.info(message)
        elif log_level == logging.WARNING:
            logging.warning(message)
        elif log_level == logging.ERROR:
            logging.error(message)

    def _sanitize_url_part(self, part: str) -> str:
        """Encodes URL parts to be safe for URLs, preserving slashes and common URL delimiters."""
        return urllib.parse.quote(part, safe="/")

    def _construct_full_url(self, base_cdn, base_path, file_name):
        """Constructs a full download URL from CDN, base path, and file name."""
        if not base_cdn or not file_name:
            logging.warning(f"Cannot construct URL: base_cdn='{base_cdn}', file_name='{file_name}'")
            return None

        # Ensure base_cdn ends with a slash if base_path is not empty
        if base_cdn and not base_cdn.endswith('/') and base_path:
            base_cdn += '/'
        # Ensure base_path ends with a slash if file_name is not empty
        if base_path and not base_path.endswith('/') and file_name:
            base_path += '/'
        
        # Sanitize each part before joining
        safe_base_path = self._sanitize_url_part(base_path)
        safe_file_name = self._sanitize_url_part(file_name)

        full_url = base_cdn + safe_base_path + safe_file_name
        logging.info(f"Constructed URL: {full_url}")
        return full_url

    def _fetch_json(self, json_url):
        """Fetches JSON data from the given URL and extracts download information."""
        self.output_text.delete(1.0, tk.END)
        self._update_status(f"🔄 กำลังดึงข้อมูล JSON จาก: {json_url}...", logging.INFO)

        self.packages_to_download.clear() # Clear previous packages
        # Clear dynamic buttons
        for widget in self.dynamic_buttons_scrollframe.winfo_children():
            widget.destroy()

        extracted_info = {
            "version": "N/A",
            "game_name": "Wuthering Waves", # Default game name
            "type": "N/A", # "game" or "launcher"
            "cdnList": [],
            "raw_data": {}
        }

        try:
            response = requests.get(json_url, timeout=DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            extracted_info["raw_data"] = data

            is_game_json = "/game/" in json_url
            extracted_info["type"] = "game" if is_game_json else "launcher"

            # Get base CDN and base URL from config
            base_cdn = data.get("default", {}).get("cdnList", [{}])[0].get('url', '')
            
            # Version can be in default.version or default.config.version
            extracted_info["version"] = data.get("default", {}).get("version", data.get("default", {}).get("config", {}).get("version", "N/A"))
            extracted_info["game_name"] = "Wuthering Waves" # Default name

            # Store CDN list for display
            cdns = data.get("default", {}).get("cdnList", [])
            extracted_info["cdnList"] = [cdn['url'] for cdn in cdns if 'url' in cdn]
            logging.info(f"Base CDN: {base_cdn}")
            logging.info(f"Detected Version: {extracted_info['version']}")

            if is_game_json:
                # For game JSON, the main game package is in resourcesDiff.currentGameInfo
                current_game_info = data.get("default", {}).get("resourcesDiff", {}).get("currentGameInfo", {})
                
                if current_game_info:
                    pkg_file_name = current_game_info.get("fileName")
                    pkg_md5 = current_game_info.get("md5", "N/A")
                    pkg_version = current_game_info.get("version", extracted_info["version"])
                    # The base path for this file is default.resourcesBasePath
                    base_path_for_main_game = data.get("default", {}).get("resourcesBasePath", "")
                    
                    full_download_url = self._construct_full_url(base_cdn, base_path_for_main_game, pkg_file_name)
                    if full_download_url:
                        self.packages_to_download.append(("GamePkg", f"{extracted_info['game_name']} v{pkg_version}", full_download_url, pkg_md5, 0)) # Size is not directly here, set to 0 for now
                        logging.info(f"Found Main Game Package: {pkg_file_name} at {full_download_url}")
                    else:
                        logging.warning(f"Could not construct URL for Main Game Package: fileName={pkg_file_name}, basePath={base_path_for_main_game}")
                else:
                    logging.warning("No 'currentGameInfo' found in resourcesDiff.")

                # Patch Configs
                patch_configs = data.get("default", {}).get("config", {}).get("patchConfig", [])
                if patch_configs:
                    logging.info(f"Found {len(patch_configs)} patch configurations.")
                    for i, patch_cfg in enumerate(patch_configs):
                        patch_version = patch_cfg.get("version", "N/A")
                        patch_index_file = patch_cfg.get("indexFile") # This is a path to another JSON
                        patch_md5 = patch_cfg.get("indexFileMd5", "N/A") # MD5 for the indexFile.json
                        patch_size = int(patch_cfg.get("size", 0)) # Size of the patch itself, not the indexFile.json

                        # Construct URL for the patch's indexFile.json
                        # Use patch_cfg.baseUrl for the path, and patch_index_file for the file name
                        patch_base_url = patch_cfg.get("baseUrl", "")
                        full_patch_url = self._construct_full_url(base_cdn, patch_base_url, patch_index_file)
                        
                        if full_patch_url:
                            # Note: This button downloads the indexFile.json for the patch, not the actual game patch files.
                            # To download actual patch files (e.g., .pak), we'd need to parse this indexFile.json.
                            self.packages_to_download.append(("PatchIndex", f"Patch v{patch_version} Index", full_patch_url, patch_md5, patch_size))
                            logging.info(f"Found Patch Index for v{patch_version}: {full_patch_url}")
                        else:
                            logging.warning(f"Could not construct URL for Patch Index v{patch_version}: indexFile={patch_index_file}, baseUrl={patch_base_url}")
                else:
                    logging.info("No 'patchConfig' found in game data.")
                
                # Note: No direct 'voice_packs' found in this JSON structure.
                
            else: # is_launcher_json
                launcher_info = data.get("data", {}).get("launcher", {})
                latest_launcher_data = launcher_info.get("latest", {})
                launcher_package = latest_launcher_data.get("package", {})

                extracted_info["game_name"] = "Wuthering Waves Launcher" # Specific name for launcher

                # Launcher Package
                if launcher_package:
                    pkg_file_name = launcher_package.get("fileName")
                    pkg_md5 = launcher_package.get("md5", "N/A")
                    pkg_size = int(launcher_package.get("size", 0))

                    # Construct URL for launcher package using CDN + baseUrl + fileName
                    # Launcher JSON might have its own baseUrl in default.config
                    launcher_base_url_config = data.get("default", {}).get("config", {}).get('baseUrl', '')
                    full_download_url = self._construct_full_url(base_cdn, launcher_base_url_config, pkg_file_name)
                    if full_download_url:
                        self.packages_to_download.append(("LauncherPkg", f"{extracted_info['game_name']} v{extracted_info['version']}", full_download_url, pkg_md5, pkg_size))
                        logging.info(f"Found Launcher Package: {pkg_file_name} at {full_download_url}")
                    else:
                        logging.warning(f"Could not construct URL for Launcher Package: fileName={pkg_file_name}, baseUrl={launcher_base_url_config}")
                else:
                    logging.warning("No 'package' found in latest launcher data.")

            if self.packages_to_download:
                self._update_status(f"✅ ดึงข้อมูล JSON สำเร็จ. พบ {len(self.packages_to_download)} แพ็คเกจที่ดาวน์โหลดได้", logging.INFO)
            else:
                self._update_status(f"⚠️ ดึงข้อมูล JSON สำเร็จ แต่ไม่พบแพ็คเกจที่ดาวน์โหลดได้ใน URL นี้", logging.WARNING)
            
            return extracted_info

        except requests.exceptions.Timeout:
            self._update_status("❌ ดึงข้อมูลล้มเหลว: หมดเวลาการเชื่อมต่อ (Timeout)", logging.ERROR)
            logging.error(f"Request Timeout for {json_url}")
        except requests.exceptions.RequestException as e:
            self._update_status(f"❌ ดึงข้อมูลล้มเหลว: ข้อผิดพลาดในการเชื่อมต่อหรือ HTTP: {e}", logging.ERROR)
            logging.error(f"Request Error for {json_url}: {e}")
        except ValueError as e:
            self._update_status(f"❌ ดึงข้อมูลล้มเหลว: ข้อมูล JSON ไม่สมบูรณ์หรือโครงสร้างไม่ถูกต้อง: {e}", logging.ERROR)
            logging.error(f"JSON Parsing Error for {json_url}: {e}")
        except Exception as e:
            self._update_status(f"❌ ดึงข้อมูลล้มเหลว: ข้อผิดพลาดที่ไม่คาดคิด: {e}", logging.ERROR)
            logging.error(f"Unexpected Error for {json_url}: {e}")
        return None

    def _load_json_data(self):
        """Wrapper to fetch JSON in a thread and display it."""
        selected_key = self.selected_json_url_key.get()
        json_url_to_fetch = KUROGAME_API_URLS.get(selected_key)

        if not json_url_to_fetch:
            self._update_status("⚠️ กรุณาเลือก URL JSON ที่ถูกต้อง", logging.WARNING)
            return

        # Disable load button and combobox while fetching
        self.btn_load.config(state=tk.DISABLED)
        self.url_combobox.config(state=tk.DISABLED)
        threading.Thread(target=lambda: self._fetch_and_display_json_threaded(json_url_to_fetch), daemon=True).start()

    def _fetch_and_display_json_threaded(self, json_url):
        """Fetches JSON and then updates the GUI."""
        extracted_data = self._fetch_json(json_url)
        self.master.after(0, lambda: self._display_data(extracted_data))
        self.master.after(0, lambda: self.btn_load.config(state=tk.NORMAL)) # Re-enable load button
        self.master.after(0, lambda: self.url_combobox.config(state="readonly")) # Re-enable combobox

    def _display_data(self, extracted_data):
        """Displays extracted JSON data and creates dynamic download buttons."""
        self.output_text.delete(1.0, tk.END) # Clear previous content

        # Clear dynamic buttons
        for widget in self.dynamic_buttons_scrollframe.winfo_children():
            widget.destroy()

        # Define text tags for styling
        self.output_text.tag_configure("title", font=("Segoe UI", 14, "bold"), foreground="#0056b3")
        self.output_text.tag_configure("subtitle", font=("Segoe UI", 12, "bold"), foreground="#007bff")
        self.output_text.tag_configure("header", font=("Segoe UI", 11, "bold"), foreground="#333333")
        self.output_text.tag_configure("normal", font=("Segoe UI", 10), foreground="#000000")
        self.output_text.tag_configure("url", font=("Segoe UI", 10, "underline"), foreground="blue")
        self.output_text.tag_configure("info", foreground="#28a745") # Green for success/info
        self.output_text.tag_configure("warning", foreground="#ffc107") # Yellow for warnings
        self.output_text.tag_configure("error", foreground="#dc3545") # Red for errors

        if not extracted_data:
            self.output_text.insert(tk.END, "❌ ไม่สามารถโหลดข้อมูลได้ กรุณาลองใหม่อีกครั้ง\n", "error")
            self.btn_stop.config(state=tk.DISABLED)
            return

        self.output_text.insert(tk.END, "Wuthering Waves\n\n", "title")
        self.output_text.insert(tk.END, f"DATA: {self.selected_json_url_key.get()}\n", "subtitle")
        self.output_text.insert(tk.END, f"API: {extracted_data.get('type', 'N/A').capitalize()}\n", "subtitle")
        self.output_text.insert(tk.END, f"Version: {extracted_data.get('version', 'N/A')}\n\n", "subtitle")

        # Display CDN URLs
            #    self.output_text.insert(tk.END, "--- CDN URLs ---\n", "header")
           #     if extracted_data.get('cdnList'):
           #         for cdn_url in extracted_data['cdnList']:
           #             self.output_text.insert(tk.END, f"- {cdn_url}\n", "normal")
           #     else:
          #          self.output_text.insert(tk.END, "ไม่มีข้อมูล CDN\n", "normal")
           #     self.output_text.insert(tk.END, "\n")

        # Display packages and create dynamic buttons
        if self.packages_to_download:
            self.output_text.insert(tk.END, "--- List of downloadable packages ---\n", "header")
            for ptype, pname, url, md5, size_bytes in self.packages_to_download:
                size_gb = size_bytes / (1024**3) if size_bytes else 0
                self.output_text.insert(tk.END, f"{pname}\n", "normal")
                self.output_text.insert(tk.END, f"  size: {size_gb:.2f} GB | MD5: {md5}\n", "normal")
                self.output_text.insert(tk.END, "  URL: ", "normal")
                self.output_text.insert(tk.END, f"{url}\n\n", "url")

                # Create dynamic download button
                btn = ttk.Button(self.dynamic_buttons_scrollframe, text=f"⬇️ ดาวน์โหลด {ptype}: {pname} ({size_gb:.2f} GB)",
                                 command=lambda u=url, m=md5, n=pname: self._start_single_download(u, m, n))
                btn.pack(pady=2, anchor='w', fill=tk.X)
            self.output_text.insert(tk.END, "\n")
            self.output_text.insert(tk.END, "\n", "info")
        else:
            self.output_text.insert(tk.END, "\n", "warning")
            
        self.btn_stop.config(state=tk.DISABLED)
        self._update_status("", logging.INFO)

    def _start_single_download(self, url, md5_checksum, package_name):
        """Initiates a single file download process for a specific package."""
        if self.stop_download_flag:
            messagebox.showwarning("Warning", "กำลังหยุดดาวน์โหลด ไม่สามารถเริ่มใหม่ได้")
            return

        initial_file_name = url.split("/")[-1]
        # Suggest a more descriptive file name
        suggested_file_name = f"{package_name.replace(' ', '_').replace(':', '').replace('/', '_')}_{initial_file_name}"

        save_path = filedialog.asksaveasfilename(defaultextension=".zip",
                                                 initialfile=suggested_file_name,
                                                 filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")])
        if not save_path:
            self._update_status("การดาวน์โหลดถูกยกเลิกโดยผู้ใช้", logging.INFO)
            return

        self.stop_download_flag = False
        self.progress_var.set(0)
        self.download_speed_var.set("ความเร็ว: 0 KB/s")
        self.time_remaining_var.set("เวลาที่เหลือ: N/A")
        self.current_file_var.set(f"ไฟล์ปัจจุบัน: {os.path.basename(save_path)}")

        # Disable all download buttons, load button, and comboboxes
        for widget in self.dynamic_buttons_scrollframe.winfo_children():
            widget.config(state=tk.DISABLED)
        self.btn_load.config(state=tk.DISABLED)
        self.url_combobox.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)

        self.download_queue.put((url, save_path, md5_checksum))
        self._update_status(f"⬇️ เพิ่มไฟล์ {os.path.basename(save_path)} ลงในคิว", logging.INFO)

        t = threading.Thread(target=self._process_download_queue, daemon=True)
        self.active_download_threads.append(t)
        t.start()

    def _process_download_queue(self):
        """Processes items in the download queue."""
        while not self.download_queue.empty():
            url, path, md5_checksum = self.download_queue.get()
            self._download_file(url, path, md5_checksum)
            self.download_queue.task_done()

        # Re-enable buttons after all downloads in queue are done
        self.master.after(100, lambda: self.btn_stop.config(state=tk.DISABLED))
        self.master.after(100, lambda: self.btn_load.config(state=tk.NORMAL))
        self.master.after(100, lambda: self.url_combobox.config(state="readonly"))
        self.master.after(100, lambda: self.current_file_var.set("ไฟล์ปัจจุบัน: ไม่มี"))
        self.master.after(100, lambda: self.status_message_var.set("พร้อมใช้งาน"))
        # Re-enable dynamic download buttons
        self.master.after(100, lambda: [widget.config(state=tk.NORMAL) for widget in self.dynamic_buttons_scrollframe.winfo_children()])
        self._update_status("คิวการดาวน์โหลดเสร็จสิ้น", logging.INFO)

    def _download_file(self, url, path, md5_checksum):
        """Downloads a single file with progress, speed, and MD5 verification."""
        self._update_status(f"⬇️ กำลังดาวน์โหลดไฟล์: {os.path.basename(path)}", logging.INFO)

        try:
            with requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT) as r:
                r.raise_for_status()
                total_length = int(r.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                last_update_time = time.time()
                last_downloaded = 0
                hasher = hashlib.md5()

                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                        if self.stop_download_flag:
                            self._update_status("⏸️ ดาวน์โหลดถูกยกเลิกโดยผู้ใช้", logging.INFO)
                            if os.path.exists(path):
                                os.remove(path)
                                self._update_status(f"ลบไฟล์ที่ดาวน์โหลดบางส่วน: {os.path.basename(path)}", logging.INFO)
                            return

                        if chunk:
                            f.write(chunk)
                            hasher.update(chunk)
                            downloaded += len(chunk)

                            current_time = time.time()
                            if current_time - last_update_time >= 0.5: # Update every 0.5 seconds
                                speed = (downloaded - last_downloaded) / (current_time - last_update_time) # bytes/sec
                                speed_kbps = speed / 1024
                                self.download_speed_var.set(f"ความเร็ว: {speed_kbps:.2f} KB/s")

                                if total_length > 0 and speed > 0:
                                    remaining_bytes = total_length - downloaded
                                    time_left_seconds = remaining_bytes / speed
                                    td = timedelta(seconds=int(time_left_seconds))
                                    self.time_remaining_var.set(f"เวลาที่เหลือ: {str(td)}")
                                else:
                                    self.time_remaining_var.set("เวลาที่เหลือ: คำนวณ...")

                                last_update_time = current_time
                                last_downloaded = downloaded

                            if total_length > 0:
                                percent = int(downloaded * 100 / total_length)
                                self.progress_var.set(percent)
                            else:
                                self.progress_var.set(0)
                            self.master.update_idletasks()

            self._update_status(f"✅ ดาวน์โหลดเสร็จสิ้น: {os.path.basename(path)}", logging.INFO)

            # MD5 Verification
            if md5_checksum and md5_checksum != "N/A":
                calculated_md5 = hasher.hexdigest()
                self._update_status(f"🔍 กำลังตรวจสอบ MD5...", logging.INFO)
                if calculated_md5.lower() == md5_checksum.lower(): # Case-insensitive comparison
                    self._update_status(f"✅ ตรวจสอบ MD5 สำเร็จ! ไฟล์สมบูรณ์", logging.INFO)
                    messagebox.showinfo("ดาวน์โหลดเสร็จสิ้น", f"ดาวน์โหลดไฟล์เสร็จสิ้นและตรวจสอบ MD5 สำเร็จ:\n{path}")
                else:
                    self._update_status(f"❌ ตรวจสอบ MD5 ล้มเหลว! ไฟล์อาจเสียหาย", logging.WARNING)
                    messagebox.showwarning("ดาวน์โหลดเสร็จสิ้น (MD5 ไม่ตรง)", f"ดาวน์โหลดไฟล์เสร็จสิ้น แต่ MD5 ไม่ตรงกัน:\nไฟล์: {path}\nMD5 ที่คาดหวัง: {md5_checksum}\nMD5 ที่คำนวณได้: {calculated_md5}\nไฟล์อาจเสียหาย!")
            else:
                messagebox.showinfo("ดาวน์โหลดเสร็จสิ้น", f"ดาวน์โหลดไฟล์เสร็จสิ้น:\n{path}\n(ไม่มี MD5 ให้ตรวจสอบ)")
                self._update_status(f"ดาวน์โหลดเสร็จสิ้น: {os.path.basename(path)} (ไม่มี MD5 ให้ตรวจสอบ)", logging.INFO)

        except requests.exceptions.RequestException as e:
            self._update_status(f"❌ ดาวน์โหลดไฟล์ล้มเหลว: ข้อผิดพลาดในการเชื่อมต่อหรือ HTTP: {e}", logging.ERROR)
            messagebox.showerror("Error", f"ดาวน์โหลดไฟล์ล้มเหลว: {e}")
        except IOError as e:
            self._update_status(f"❌ ดาวน์โหลดไฟล์ล้มเหลว: ข้อผิดพลาดในการเขียนไฟล์: {e}", logging.ERROR)
            messagebox.showerror("Error", f"ดาวน์โหลดไฟล์ล้มเหลว: {e}")
        except Exception as e:
            self._update_status(f"❌ ดาวน์โหลดไฟล์ล้มเหลว: ข้อผิดพลาดที่ไม่คาดคิด: {e}", logging.ERROR)
            messagebox.showerror("Error", f"ดาวน์โหลดไฟล์ล้มเหลว: {e}")
        finally:
            self.progress_var.set(0)
            self.download_speed_var.set("ความเร็ว: N/A")
            self.time_remaining_var.set("เวลาที่เหลือ: N/A")

    def _copy_text(self):
        """Copies the content of the output text widget to the clipboard."""
        text = self.output_text.get(1.0, tk.END)
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        messagebox.showinfo("คัดลอกข้อความ", "คัดลอกข้อความไปยังคลิปบอร์ดเรียบร้อยแล้ว")
        self._update_status("คัดลอกข้อความไปยังคลิปบอร์ด", logging.INFO)

    def _stop_download(self):
        """Sets the flag to stop the current download."""
        if messagebox.askyesno("ยืนยัน", "ต้องการหยุดดาวน์โหลดหรือไม่? ไฟล์ที่ดาวน์โหลดไปแล้วจะถูกลบ"):
            self.stop_download_flag = True
            self.btn_stop.config(state=tk.DISABLED)
            self._update_status("คำขอหยุดดาวน์โหลดถูกส่งแล้ว...", logging.INFO)

if __name__ == "__main__":
    root = tk.Tk()
    app = WutheringWavesDownloaderApp(root)
    root.mainloop()
