"""GODZIP Self-Extracting Archive (SFX) Standalone Runner.

Author: Chandan Bagh (baghchandan53@gmail.com, GitHub: @cbagh0819-ctrl)
"""

import sys
import os
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from godzip.common.constants import MAGIC_HEADER, MAGIC_TRAILER
from godzip.common.exceptions import ArchiveEncryptedError, InvalidPasswordError
from godzip.archive.reader import ArchiveReader


def find_embedded_archive() -> str:
    """Finds the .god archive payload embedded inside or alongside this executable."""
    exe_path = sys.executable if getattr(sys, "frozen", False) else __file__

    with open(exe_path, "rb") as fp:
        data = fp.read()

    # Search for GODZIP header magic
    idx = data.rfind(MAGIC_HEADER)
    if idx != -1:
        # Verify footer magic GEND at end
        if data.endswith(MAGIC_TRAILER) or MAGIC_TRAILER in data[idx:]:
            # Write out payload to a secure temporary .god container
            temp_god = os.path.join(tempfile.gettempdir(), f"godzip_sfx_{os.getpid()}.god")
            with open(temp_god, "wb") as out_fp:
                out_fp.write(data[idx:])
            return temp_god

    # Check companion .god file with same name
    base = os.path.splitext(exe_path)[0]
    cand = base + ".god"
    if os.path.exists(cand):
        return cand

    # Check command-line argument
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        return sys.argv[1]

    return None


class SFXApp:
    def __init__(self, archive_path: str):
        self.archive_path = archive_path
        self.reader = ArchiveReader(self.archive_path)
        self.info = self.reader.inspect()

        self.root = tk.Tk()
        self.root.title("GODZIP Self-Extracting Archive")
        self.root.geometry("520x340")
        self.root.resizable(False, False)
        self.root.configure(bg="#121316")

        self._build_ui()

    def _build_ui(self):
        # Header banner
        hdr_frame = tk.Frame(self.root, bg="#1a1c23", padx=16, pady=12)
        hdr_frame.pack(fill="x")

        title_lbl = tk.Label(
            hdr_frame,
            text="GODZIP Self-Extractor",
            font=("Segoe UI", 14, "bold"),
            fg="#f0f2f5",
            bg="#1a1c23"
        )
        title_lbl.pack(anchor="w")

        author_lbl = tk.Label(
            hdr_frame,
            text="Engine by Chandan Bagh (@cbagh0819-ctrl) | Lossless Architecture",
            font=("Segoe UI", 8),
            fg="#e63946",
            bg="#1a1c23"
        )
        author_lbl.pack(anchor="w")

        # Body container
        body = tk.Frame(self.root, bg="#121316", padx=20, pady=14)
        body.pack(fill="both", expand=True)

        # Archive summary
        total_mb = self.info['total_original_bytes'] / (1024 * 1024)
        stats_text = (
            f"Files: {self.info['file_count']} | Blocks: {self.info['block_count']} | "
            f"Uncompressed: {total_mb:.2f} MB | Ratio: {self.info['compression_ratio']:.2f}x"
        )
        if self.info.get("is_encrypted"):
            stats_text += " | [ENCRYPTED: AES-256]"

        stats_lbl = tk.Label(body, text=stats_text, font=("Segoe UI", 9), fg="#8d94a5", bg="#121316")
        stats_lbl.pack(anchor="w", pady=(0, 10))

        # Destination folder selection
        dest_lbl = tk.Label(body, text="Extraction Destination:", font=("Segoe UI", 9, "bold"), fg="#c5cad6", bg="#121316")
        dest_lbl.pack(anchor="w")

        dest_frame = tk.Frame(body, bg="#121316")
        dest_frame.pack(fill="x", pady=(4, 10))

        default_dir = os.path.abspath(os.path.join(os.getcwd(), "Extracted_Files"))
        self.dest_var = tk.StringVar(value=default_dir)
        dest_entry = tk.Entry(
            dest_frame,
            textvariable=self.dest_var,
            font=("Segoe UI", 9),
            bg="#1c1e27",
            fg="#ffffff",
            insertbackground="#ffffff",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#2d3142"
        )
        dest_entry.pack(side="left", fill="x", expand=True, ipady=4)

        browse_btn = tk.Button(
            dest_frame,
            text="Browse...",
            font=("Segoe UI", 9),
            bg="#282c3c",
            fg="#f0f2f5",
            relief="flat",
            command=self._browse_dest,
            padx=10
        )
        browse_btn.pack(side="right", padx=(8, 0))

        # Progress bar
        self.progress_bar = ttk.Progressbar(body, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill="x", pady=(10, 4))

        self.status_lbl = tk.Label(body, text="Ready to extract.", font=("Segoe UI", 8), fg="#8d94a5", bg="#121316")
        self.status_lbl.pack(anchor="w")

        # Action Buttons
        btn_frame = tk.Frame(body, bg="#121316")
        btn_frame.pack(fill="x", pady=(14, 0))

        self.extract_btn = tk.Button(
            btn_frame,
            text="Extract All Files",
            font=("Segoe UI", 10, "bold"),
            bg="#e63946",
            fg="#ffffff",
            relief="flat",
            command=self._run_extraction,
            padx=16,
            pady=4,
            cursor="hand2"
        )
        self.extract_btn.pack(side="right")

        cancel_btn = tk.Button(
            btn_frame,
            text="Close",
            font=("Segoe UI", 9),
            bg="#282c3c",
            fg="#ffffff",
            relief="flat",
            command=self.root.destroy,
            padx=14,
            pady=4
        )
        cancel_btn.pack(side="right", padx=(0, 10))

    def _browse_dest(self):
        d = filedialog.askdirectory(title="Select Destination Folder", initialdir=self.dest_var.get())
        if d:
            self.dest_var.set(d)

    def _run_extraction(self):
        dest = self.dest_var.get().strip()
        if not dest:
            return

        password = None
        if self.info.get("is_encrypted"):
            pwd = simpledialog.askstring("Password Required", "This archive is protected with AES-256-GCM.\nEnter password:", show="*")
            if not pwd:
                return
            password = pwd

        self.extract_btn.config(state="disabled")
        self.status_lbl.config(text="Extracting archive...", fg="#4895ef")
        self.root.update()

        try:
            reader = ArchiveReader(self.archive_path, password=password)

            def on_progress(p):
                pct = (p.bytes_processed / max(1, p.total_bytes)) * 100
                self.progress_bar["value"] = pct
                self.status_lbl.config(text=f"Extracting: {os.path.basename(p.current_file)} ({pct:.1f}%)")
                self.root.update()

            reader.extract(destination_dir=dest, progress_callback=on_progress)
            self.progress_bar["value"] = 100
            self.status_lbl.config(text=f"Successfully extracted {len(self.info['files'])} files!", fg="#2ec4b6")
            messagebox.showinfo("Extraction Complete", f"All files extracted successfully to:\n{dest}\n\n100% BLAKE3 Cryptographic Integrity Confirmed.")
            self.root.destroy()
        except InvalidPasswordError:
            messagebox.showerror("Password Error", "Incorrect password. Failed to decrypt archive.")
            self.extract_btn.config(state="normal")
            self.status_lbl.config(text="Password error. Try again.", fg="#e63946")
        except Exception as e:
            messagebox.showerror("Extraction Failed", str(e))
            self.extract_btn.config(state="normal")
            self.status_lbl.config(text=f"Error: {e}", fg="#e63946")

    def run(self):
        self.root.mainloop()


def main():
    archive_file = find_embedded_archive()
    if not archive_file or not os.path.exists(archive_file):
        # Fallback to command line or file prompt
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            archive_file = sys.argv[1]
        else:
            root = tk.Tk()
            root.withdraw()
            archive_file = filedialog.askopenfilename(
                title="Select GODZIP Archive to Extract",
                filetypes=[("GODZIP Archive", "*.god")]
            )
            root.destroy()
            if not archive_file:
                sys.exit(1)

    app = SFXApp(archive_file)
    app.run()


if __name__ == "__main__":
    main()
