#!/usr/bin/env python3
"""
Windows2Go - Professional Tool
A comprehensive application for creating portable, bootable Windows To Go installations on USB drives.

*** DISCLAIMER ***
This is a powerful tool that directly manipulates disk drives.
A mistake can lead to PERMANENT DATA LOSS on ANY connected drive.
This process creates a NON-OFFICIAL "Windows2Go" environment. Performance and compatibility may vary.
USE AT YOUR OWN RISK.

Requirements:
- Windows 10/11 Pro or Enterprise (for DISM/BCDBoot)
- Run as Administrator
- STABLE 7-Zip command-line files (7z.exe, 7z.dll) in the same directory
- Python libraries: customtkinter, psutil, pillow, pywin32

Version: 3.0.0 (Windows2Go Edition)
Autor: LMLK-seal
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import psutil
import subprocess
import threading
import os
import sys
import time
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Callable
import tempfile
import shutil
import ctypes

# --- Application Configuration ---
APP_NAME = "Windows2Go"
APP_VERSION = "3.0.0"
CONFIG_FILE = "windows_togo_config.json"
SEVEN_ZIP_EXECUTABLE = "7z.exe"

# --- Custom Exception for Detailed Errors ---
class SubprocessError(Exception):
    def __init__(self, message, command_output=""):
        super().__init__(message)
        self.command_output = command_output

    def __str__(self):
        details = f"\n\n--- Command Output ---\n{self.command_output}" if self.command_output else ""
        return f"{super().__str__()}{details}"

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WindowsToGoCreator:
    def __init__(self):
        # --- Pre-flight Checks ---
        self.check_admin_rights()
        self.check_dependencies()

        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("900x750")
        self.root.minsize(800, 650)
        
        # --- Application State ---
        self.selected_iso_path = ""
        self.selected_drive: Optional[Dict] = None
        self.target_drive_letter: Optional[str] = None
        self.installation_thread: Optional[threading.Thread] = None
        self.current_process: Optional[subprocess.Popen] = None
        self.temp_iso_extract_path: Optional[str] = None
        self.is_installing = False
        
        self.load_config()
        self.setup_ui()
        self.refresh_drives()
        self.center_window()
        
    def check_admin_rights(self):
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                messagebox.showerror("Administrator Rights Required", "This application requires administrator privileges...")
                sys.exit(1)
        except Exception:
            messagebox.showwarning("Warning", "Could not verify admin rights. The application may fail.")

    def check_dependencies(self):
        if not shutil.which(SEVEN_ZIP_EXECUTABLE):
            messagebox.showerror("Dependency Missing", f"'{SEVEN_ZIP_EXECUTABLE}' not found...")
            sys.exit(1)

    def center_window(self):
        self.root.update_idletasks()
        width, height = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def load_config(self):
        self.config = {"last_iso_path": "", "partition_scheme": "MBR", "file_system": "NTFS"}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f: self.config.update(json.load(f))
            except Exception as e: print(f"Failed to load config: {e}")
            
    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f: json.dump(self.config, f, indent=4)
        except Exception as e: print(f"Failed to save config: {e}")
            
    # --- UI Setup ---
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        title_label = ctk.CTkLabel(self.main_frame, text=APP_NAME, font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(10, 5))
        subtitle_label = ctk.CTkLabel(self.main_frame, text="Create portable, bootable Windows installations on USB drives", font=ctk.CTkFont(size=14))
        subtitle_label.pack(pady=(0, 20))
        self.create_iso_selection_section()
        self.create_drive_selection_section()
        self.create_options_section()
        self.create_action_section()
        self.create_progress_section()
        self.create_log_section()
        
    def create_iso_selection_section(self):
        iso_frame = ctk.CTkFrame(self.main_frame)
        iso_frame.pack(fill="x", padx=20, pady=(0, 10))
        iso_title = ctk.CTkLabel(iso_frame, text="📀 1. Select Windows ISO File", font=ctk.CTkFont(size=16, weight="bold"))
        iso_title.pack(anchor="w", padx=20, pady=(10, 5))
        iso_selection_frame = ctk.CTkFrame(iso_frame)
        iso_selection_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.iso_path_var = ctk.StringVar(value=self.config.get("last_iso_path", ""))
        self.iso_path_entry = ctk.CTkEntry(iso_selection_frame, textvariable=self.iso_path_var, placeholder_text="Select Windows ISO file...", height=35)
        self.iso_path_entry.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=10)
        self.browse_iso_btn = ctk.CTkButton(iso_selection_frame, text="Browse", command=self.browse_iso_file, width=100, height=35)
        self.browse_iso_btn.pack(side="right", padx=(0, 15), pady=10)
        if self.iso_path_var.get(): self.selected_iso_path = self.iso_path_var.get()
        
    def create_drive_selection_section(self):
        drive_frame = ctk.CTkFrame(self.main_frame)
        drive_frame.pack(fill="x", padx=20, pady=(0, 10))
        drive_title = ctk.CTkLabel(drive_frame, text="💾 2. Select Target USB Drive", font=ctk.CTkFont(size=16, weight="bold"))
        drive_title.pack(anchor="w", padx=20, pady=(10, 5))
        warning_label = ctk.CTkLabel(drive_frame, text="⚠️ WARNING: All data on the selected USB drive will be permanently destroyed!", font=ctk.CTkFont(size=12, weight="bold"), text_color="orange")
        warning_label.pack(anchor="w", padx=20, pady=(0, 10))
        drive_selection_frame = ctk.CTkFrame(drive_frame)
        drive_selection_frame.pack(fill="x", padx=20, pady=(0, 15))
        self.drive_var = ctk.StringVar()
        self.drive_dropdown = ctk.CTkComboBox(drive_selection_frame, variable=self.drive_var, values=["No USB drives detected"], state="readonly", height=35)
        self.drive_dropdown.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=10)
        self.refresh_drives_btn = ctk.CTkButton(drive_selection_frame, text="Refresh", command=self.refresh_drives, width=100, height=35)
        self.refresh_drives_btn.pack(side="right", padx=(0, 15), pady=10)
        
    def create_options_section(self):
        options_frame = ctk.CTkFrame(self.main_frame)
        options_frame.pack(fill="x", padx=20, pady=(0, 10))
        options_title = ctk.CTkLabel(options_frame, text="⚙️ 3. Installation Options", font=ctk.CTkFont(size=16, weight="bold"))
        options_title.pack(anchor="w", padx=20, pady=(10, 5))
        options_grid = ctk.CTkFrame(options_frame)
        options_grid.pack(fill="x", padx=20, pady=(0, 15))
        options_grid.grid_columnconfigure((0, 1), weight=1)
        partition_label = ctk.CTkLabel(options_grid, text="Partition Scheme:")
        partition_label.grid(row=0, column=0, padx=15, pady=5, sticky="w")
        self.partition_var = ctk.StringVar(value=self.config["partition_scheme"])
        partition_dropdown = ctk.CTkComboBox(options_grid, variable=self.partition_var, values=["MBR"], state="disabled")
        partition_dropdown.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
        filesystem_label = ctk.CTkLabel(options_grid, text="File System:")
        filesystem_label.grid(row=0, column=1, padx=15, pady=5, sticky="w")
        self.filesystem_var = ctk.StringVar(value=self.config["file_system"])
        filesystem_dropdown = ctk.CTkComboBox(options_grid, variable=self.filesystem_var, values=["NTFS"], state="disabled")
        filesystem_dropdown.grid(row=1, column=1, padx=15, pady=(0, 10), sticky="ew")
        
    def create_action_section(self):
        action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=10)
        self.start_btn = ctk.CTkButton(action_frame, text="🚀 Create Windows2Go Drive", command=self.start_installation, height=45, font=ctk.CTkFont(size=16, weight="bold"))
        self.start_btn.pack(side="left", expand=True, padx=(0, 5))
        self.stop_btn = ctk.CTkButton(action_frame, text="⏹️ STOP", command=self.stop_installation, height=45, font=ctk.CTkFont(size=16, weight="bold"), state="disabled", fg_color="#D32F2F", hover_color="#B71C1C")
        self.stop_btn.pack(side="left", expand=True, padx=(5, 0))
        
    def create_progress_section(self):
        progress_frame = ctk.CTkFrame(self.main_frame)
        progress_frame.pack(fill="x", padx=20, pady=10)
        self.progress_label = ctk.CTkLabel(progress_frame, text="Ready to start.", font=ctk.CTkFont(size=12))
        self.progress_label.pack(pady=(10, 5))
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
    def create_log_section(self):
        log_frame = ctk.CTkFrame(self.main_frame)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        log_title = ctk.CTkLabel(log_frame, text="📋 Installation Log", font=ctk.CTkFont(size=16, weight="bold"))
        log_title.pack(anchor="w", padx=20, pady=(10, 5))
        self.log_text = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=11), wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self.log_message(f"{APP_NAME} initialized. Please run as Administrator.")
        self.log_message(f"Ensure STABLE '{SEVEN_ZIP_EXECUTABLE}' is in the application directory.")
        
    # --- Core Logic ---
    def browse_iso_file(self):
        initial_dir = os.path.dirname(self.config["last_iso_path"]) if self.config["last_iso_path"] else "/"
        file_path = filedialog.askopenfilename(title="Select Windows ISO", filetypes=[("ISO files", "*.iso")], initialdir=initial_dir)
        if file_path:
            self.selected_iso_path = file_path
            self.iso_path_var.set(file_path)
            self.config["last_iso_path"] = file_path
            self.save_config()
            self.log_message(f"Selected ISO: {os.path.basename(file_path)}")
            self.validate_iso_file(file_path)

    def validate_iso_file(self, file_path: str):
        try:
            file_size_gb = os.path.getsize(file_path) / (1024 ** 3)
            self.log_message(f"ISO file size: {file_size_gb:.2f} GB")
            if not (3 < file_size_gb < 20): self.log_message("Warning: Unusual ISO file size.", "warning")
            else: self.log_message("ISO file size appears valid.", "success")
        except Exception as e: self.log_message(f"Error validating ISO file: {str(e)}", "error")

    def get_usb_drives(self) -> List[Dict]:
        usb_drives = []
        try:
            # Use PowerShell instead of wmic (wmic is deprecated/removed in Windows 11 24H2+)
            ps_script = (
                "Get-PhysicalDisk | Where-Object { $_.BusType -eq 'USB' } | "
                "Select-Object DeviceId, FriendlyName, Size | "
                "ConvertTo-Json -Compress"
            )
            command = ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps_script]
            proc = subprocess.run(command, capture_output=True, text=True, check=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            output = proc.stdout.strip()
            if not output:
                return []

            import json as _json
            raw = _json.loads(output)
            # PowerShell returns a single object (dict) if only one disk, or a list
            if isinstance(raw, dict):
                raw = [raw]

            for disk in raw:
                try:
                    index = int(disk["DeviceId"])
                    size_bytes = int(disk["Size"])
                    size_gb = size_bytes / (1024 ** 3)
                    if size_gb < 1:
                        continue
                    model = disk.get("FriendlyName", "Unknown USB Drive")
                    mountpoint = f"Disk {index}"
                    for part in psutil.disk_partitions(all=True):
                        if f'PhysicalDrive{index}' in part.device:
                            mountpoint = part.mountpoint
                            break
                    usb_drives.append({
                        'device': mountpoint, 'index': index, 'model': model,
                        'total_gb': size_gb,
                        'display_name': f"{mountpoint} (Disk {index}) - {model} ({size_gb:.1f} GB)"
                    })
                except (ValueError, KeyError):
                    continue
        except Exception as e:
            self.log_message(f"Error detecting USB drives: {str(e)}", "error")
        return usb_drives

    def refresh_drives(self):
        self.log_message("Refreshing USB drives list...")
        self.available_drives = self.get_usb_drives()
        if self.available_drives:
            drive_names = [drive['display_name'] for drive in self.available_drives]
            self.drive_dropdown.configure(values=drive_names)
            if self.drive_var.get() not in drive_names:
                self.drive_var.set(drive_names[0])
            self.log_message(f"Found {len(self.available_drives)} USB drive(s).")
        else:
            self.drive_dropdown.configure(values=["No USB drives detected"])
            self.drive_dropdown.set("No USB drives detected")
            self.log_message("No USB drives detected.", "warning")

    def log_message(self, message: str, level: str = "info", end: str = "\n"):
        timestamp = time.strftime("%H:%M:%S")
        prefix = {"error": "❌", "warning": "⚠️", "success": "✅"}.get(level, "ℹ️")
        self.log_text.insert("end", f"[{timestamp}] {prefix} {message}{end}")
        self.log_text.see("end")
        self.root.update_idletasks()

    def validate_inputs(self) -> bool:
        if not self.selected_iso_path or not os.path.exists(self.selected_iso_path):
            messagebox.showerror("Validation Error", "Please select a valid Windows ISO file.")
            return False
        if "No USB" in self.drive_var.get():
            messagebox.showerror("Validation Error", "Please select a valid USB drive.")
            return False
        self.selected_drive = next((d for d in self.available_drives if d['display_name'] == self.drive_var.get()), None)
        if not self.selected_drive:
            messagebox.showerror("Validation Error", "Selected drive not found. Please refresh.")
            return False
        iso_size_gb = os.path.getsize(self.selected_iso_path) / (1024 ** 3)
        if self.selected_drive['total_gb'] < iso_size_gb + 5: # WTG needs more buffer space
            messagebox.showerror("Validation Error", "USB drive is too small. A Windows To Go installation requires more space than the ISO file size.")
            return False
        return True

    def confirm_installation(self) -> bool:
        return messagebox.askyesno("Confirm Installation", f"""
        \n⚠️ FINAL WARNING ⚠️
        This will PERMANENTLY DESTROY all data on:
        {self.selected_drive['display_name']}

        Are you absolutely sure you want to create a Windows To Go drive?
        """)

    def start_installation(self):
        if self.is_installing: return
        if not self.validate_inputs(): return
        if not self.confirm_installation(): self.log_message("Installation cancelled by user."); return
        self.save_config()
        self.is_installing = True
        self.toggle_ui_state(False)
        self.progress_bar.set(0)
        self.installation_thread = threading.Thread(target=self.installation_worker, daemon=True)
        self.installation_thread.start()

    def stop_installation(self):
        if not self.is_installing: return
        if messagebox.askyesno("Stop Installation", "Are you sure you want to stop?"):
            self.log_message("Stop signal received. Terminating...", "warning")
            self.is_installing = False
            if self.current_process:
                try: self.current_process.terminate()
                except Exception as e: self.log_message(f"Could not terminate: {e}", "error")

    def toggle_ui_state(self, enabled: bool):
        state, stop_state = ("normal", "disabled") if enabled else ("disabled", "normal")
        for widget in [self.start_btn, self.browse_iso_btn, self.refresh_drives_btn, self.drive_dropdown]:
            widget.configure(state=state)
        self.stop_btn.configure(state=stop_state)

    def _run_subprocess(self, command: List[str], progress_callback: Optional[Callable[[int], None]] = None):
        try:
            self.current_process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding='utf-8', errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            output_lines = []
            for line in iter(self.current_process.stdout.readline, ''):
                if not self.is_installing: self.current_process.terminate(); raise SubprocessError("Installation stopped by user.")
                output_lines.append(line)
                if progress_callback:
                    # Generic progress regex for DISM: [====== 20.0% ]
                    match = re.search(r'\[=*\s*(\d{1,3}(?:\.\d)?)\s*%\s*\]', line)
                    if match: progress_callback(float(match.group(1))); continue
                    # Progress regex for 7-Zip: "  1% ..."
                    match = re.search(r'^\s*(\d{1,3})%\s', line)
                    if match: progress_callback(int(match.group(1))); continue
                if '\r' not in line.strip(): self.log_text.insert("end", line); self.log_text.see("end"); self.root.update_idletasks()
            self.current_process.wait()
            full_output = "".join(output_lines)
            is_robocopy = command[0].lower() == 'robocopy'
            failed = (is_robocopy and self.current_process.returncode >= 8) or (not is_robocopy and self.current_process.returncode != 0)
            if failed:
                raise SubprocessError(f"Command `{' '.join(command)}` failed with exit code {self.current_process.returncode}.", full_output)
        except FileNotFoundError:
            raise SubprocessError(f"Command not found: {command[0]}", "Ensure the executable is in the correct directory or system PATH.")
        except Exception as e:
            if not isinstance(e, SubprocessError): raise SubprocessError(f"An unexpected error occurred: {e}")
            else: raise e
        finally:
            self.current_process = None

    def installation_worker(self):
        try:
            self.log_message("🚀 Starting Windows To Go creation process...")
            self.progress_label.configure(text="Phase 1/4: Extracting ISO..."); self.extract_iso()
            self.progress_label.configure(text="Phase 2/4: Preparing USB drive..."); self.prepare_usb_drive()
            self.progress_label.configure(text="Phase 3/4: Applying Windows Image..."); self.apply_windows_image()
            self.progress_label.configure(text="Phase 4/4: Creating boot files..."); self.make_bootable()
            self.progress_bar.set(1.0)
            self.progress_label.configure(text="Creation completed successfully!")
            self.log_message("✅ Windows To Go drive created successfully!", "success")
            messagebox.showinfo("Success", "Windows To Go drive has been created successfully!")
        except Exception as e:
            self.log_message(f"❌ Creation failed: {str(e)}", "error")
            if self.is_installing:
                messagebox.showerror("Creation Failed", str(e))
        finally:
            self._cleanup()
            self.is_installing = False
            self.toggle_ui_state(True)
            
    def _cleanup(self):
        if self.temp_iso_extract_path and os.path.exists(self.temp_iso_extract_path):
            self.log_message(f"Cleaning up temporary directory...")
            shutil.rmtree(self.temp_iso_extract_path, ignore_errors=True)
            self.temp_iso_extract_path = None
            self.log_message("Cleanup complete.")
    
    def _get_drive_letter_for_disk(self, disk_index: int) -> str:
        self.log_message(f"Querying diskpart for the new drive letter for Disk {disk_index}...", "info")
        script_content_list = "list volume\nexit"
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as sf:
            sf.write(script_content_list)
            script_path = sf.name
        try:
            proc = subprocess.run(
                ['diskpart', '/s', script_path], capture_output=True, text=True, check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            for line in proc.stdout.splitlines():
                if "WindowsUSB" in line:
                    parts = line.split()
                    if len(parts) > 2 and re.match(r'^[A-Z]$', parts[2]):
                        drive_letter = f"{parts[2]}:\\"
                        self.log_message(f"Diskpart assigned drive letter: {drive_letter}", "success")
                        return drive_letter
            raise RuntimeError("Could not find the 'WindowsUSB' volume in 'list volume' output.")
        finally:
            os.remove(script_path)

    def extract_iso(self):
        def update_extraction_progress(percent: int):
            progress_value = 0.05 + (percent / 100) * 0.15
            self.progress_bar.set(progress_value)
            self.progress_label.configure(text=f"Phase 1/4: Extracting ISO... ({percent}%)")
        self.progress_bar.set(0.05)
        self.log_message("Creating temporary directory for ISO extraction...")
        self.temp_iso_extract_path = tempfile.mkdtemp(prefix="win-togo-")
        self.log_message(f"Extracting to: {self.temp_iso_extract_path}", "info")
        command = [SEVEN_ZIP_EXECUTABLE, 'x', self.selected_iso_path, f'-o{self.temp_iso_extract_path}', '-y', '-bsp1']
        self._run_subprocess(command, progress_callback=update_extraction_progress)
        
    def prepare_usb_drive(self):
        self.progress_bar.set(0.20)
        disk_index = self.selected_drive['index']
        script_content_format = f"""
        automount enable
        select disk {disk_index}
        clean
        create partition primary
        select partition 1
        active
        format fs=NTFS quick label=WindowsUSB
        assign
        exit
        """
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as sf:
            sf.write(script_content_format.strip()); script_path = sf.name
        self.log_message(f"Executing diskpart to format Disk {disk_index}...", "warning")
        try:
            self._run_subprocess(['diskpart', '/s', script_path])
        finally:
            os.remove(script_path)
        self.target_drive_letter = self._get_drive_letter_for_disk(disk_index)

    def apply_windows_image(self):
        """Applies the Windows image using DISM."""
        def update_apply_progress(percent: float):
            progress_value = 0.25 + (percent / 100) * 0.65
            self.progress_bar.set(progress_value)
            self.progress_label.configure(text=f"Phase 3/4: Applying Windows Image... ({int(percent)}%)")

        self.progress_bar.set(0.25)
        if not self.target_drive_letter:
            raise RuntimeError("Cannot apply image because the target drive letter was not determined.")
        
        sources_dir = os.path.join(self.temp_iso_extract_path, "sources")
        wim_file = os.path.join(sources_dir, "install.wim")
        esd_file = os.path.join(sources_dir, "install.esd")
        
        image_file_path = ""
        if os.path.exists(wim_file):
            image_file_path = wim_file
        elif os.path.exists(esd_file):
            image_file_path = esd_file
        else:
            raise RuntimeError("Could not find install.wim or install.esd in the ISO's sources directory.")
            
        self.log_message(f"Found Windows image file: {os.path.basename(image_file_path)}", "info")
        self.log_message("Applying image with DISM. This is the longest step and may take a very long time...", "info")
        
        # NOTE: We are defaulting to Index:1. A more advanced version could parse the WIM for all indexes.
        command = [
            'dism', '/Apply-Image', f'/ImageFile:{image_file_path}',
            '/Index:1', f'/ApplyDir:{self.target_drive_letter}'
        ]
        self._run_subprocess(command, progress_callback=update_apply_progress)

    def make_bootable(self):
        """Creates boot files using BCDBoot."""
        self.progress_bar.set(0.95)
        if not self.target_drive_letter:
            raise RuntimeError("Cannot make drive bootable because the target drive letter was not determined.")

        windows_dir = os.path.join(self.target_drive_letter, 'Windows')
        drive_letter = self.target_drive_letter.strip('\\')
        
        self.log_message(f"Creating boot files on {drive_letter} using BCDBoot...", "info")
        
        # /f ALL creates boot files for both BIOS and UEFI systems for maximum compatibility.
        command = [
            'bcdboot', windows_dir, '/s', drive_letter, '/f', 'ALL'
        ]
        self._run_subprocess(command)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        if self.is_installing:
            if messagebox.askokcancel("Quit", "Installation in progress. Quit anyway?"):
                self.is_installing = False
                self.root.after(500, self.root.destroy)
        else:
            self.root.destroy()

if __name__ == "__main__":
    app = WindowsToGoCreator()
    app.run()
