# -*- coding: utf-8 -*-
"""Ultimate Dork – tkinter GUI front-end."""

import os
import sys
import queue
import re
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

# ── palette (Catppuccin Mocha) ────────────────────────────────────────────────
BG      = '#1e1e2e'
BG2     = '#313244'
BG3     = '#45475a'
FG      = '#cdd6f4'
ACCENT  = '#cba6f7'
GREEN   = '#a6e3a1'
RED     = '#f38ba8'
YELLOW  = '#f9e2af'
BLUE    = '#89b4fa'
DIM     = '#6c7086'

FONT_MONO  = ('Courier New', 10)
FONT_UI    = ('Segoe UI', 10)
FONT_TITLE = ('Courier New', 15, 'bold')


def _strip(text):
    return ANSI_RE.sub('', text)


def _color_tag(text):
    """Guess a color tag from content keywords."""
    if '[!]' in text:  return 'g'
    if '[-]' in text:  return 'r'
    if '[E]'  in text: return 'y'
    if '[URL]' in text or '[*]' in text: return 'b'
    if text.startswith('- http'): return 'dim'
    return None


# ── main window ───────────────────────────────────────────────────────────────
class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title('Ultimate Dork  v2.0')
        self.configure(bg=BG)
        self.geometry('960x680')
        self.minsize(720, 520)

        self._q            = queue.Queue()
        self._stop_event   = threading.Event()
        self._thread       = None

        self._build_style()
        self._build_ui()
        self._check_deps()
        self._poll()

    # ── style ─────────────────────────────────────────────────────────────────
    def _build_style(self):
        s = ttk.Style(self)
        s.theme_use('clam')
        s.configure('.',
                    background=BG, foreground=FG,
                    fieldbackground=BG2, font=FONT_UI,
                    bordercolor=BG2, darkcolor=BG, lightcolor=BG,
                    troughcolor=BG2, selectbackground=ACCENT, selectforeground=BG)
        s.configure('TLabel',      background=BG,  foreground=FG)
        s.configure('TFrame',      background=BG)
        s.configure('TEntry',      fieldbackground=BG2, foreground=FG,
                    insertcolor=FG, padding=(4, 3))
        s.configure('TButton',     background=BG2, foreground=FG,
                    bordercolor=BG3, padding=(10, 5))
        s.map('TButton',
              background=[('active', ACCENT), ('disabled', BG2)],
              foreground=[('active', BG),     ('disabled', DIM)])
        s.configure('TCheckbutton', background=BG, foreground=FG)
        s.map('TCheckbutton', background=[('active', BG)])
        s.configure('TLabelframe',       background=BG, bordercolor=BG3)
        s.configure('TLabelframe.Label', background=BG, foreground=ACCENT,
                    font=(FONT_UI[0], FONT_UI[1], 'bold'))
        s.configure('Status.TLabel',     background=BG2, foreground=DIM,
                    padding=(8, 3))

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        # ── header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG2)
        hdr.pack(fill=tk.X)
        tk.Label(hdr, text='⚡  ULTIMATE DORK', bg=BG2, fg=ACCENT,
                 font=FONT_TITLE).pack(side=tk.LEFT, padx=16, pady=10)
        tk.Label(hdr, text='by 407 Authentic Exploit  ·  v2.0',
                 bg=BG2, fg=DIM, font=FONT_UI).pack(side=tk.LEFT, pady=10)

        # ── config panel ──────────────────────────────────────────────────────
        cfg = ttk.LabelFrame(self, text='Configuration', padding=(12, 8))
        cfg.pack(fill=tk.X, padx=14, pady=(10, 4))
        cfg.columnconfigure(1, weight=1)

        ttk.Label(cfg, text='Dork:').grid(row=0, column=0, sticky=tk.W, pady=4)
        self.dork_var = tk.StringVar()
        self._dork_entry = ttk.Entry(cfg, textvariable=self.dork_var)
        self._dork_entry.grid(row=0, column=1, sticky=tk.EW, padx=(8, 0), pady=4)
        self._dork_entry.bind('<Return>', lambda _e: self._start())

        ttk.Label(cfg, text='Proxy:').grid(row=1, column=0, sticky=tk.W, pady=4)
        self.proxy_var = tk.StringVar()
        ph_entry = ttk.Entry(cfg, textvariable=self.proxy_var, foreground=DIM)
        ph_entry.insert(0, 'optional — e.g. 127.0.0.1:8080 or socks5://host:port')
        ph_entry.grid(row=1, column=1, sticky=tk.EW, padx=(8, 0), pady=4)
        ph_entry.bind('<FocusIn>',  lambda e, w=ph_entry: self._ph_clear(w))
        ph_entry.bind('<FocusOut>', lambda e, w=ph_entry: self._ph_restore(w))
        self._proxy_ph = ph_entry

        ttk.Label(cfg, text='Config:').grid(row=2, column=0, sticky=tk.W, pady=4)
        cfg_row = ttk.Frame(cfg)
        cfg_row.grid(row=2, column=1, sticky=tk.EW, padx=(8, 0), pady=4)
        self.config_var = tk.StringVar(value=os.path.join(ROOT, 'config.json'))
        ttk.Entry(cfg_row, textvariable=self.config_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(cfg_row, text='Browse…', command=self._browse_config).pack(
            side=tk.LEFT, padx=(6, 0))

        self.scan_var = tk.BooleanVar()
        ttk.Checkbutton(cfg, text='Enable SQLi Scan',
                        variable=self.scan_var).grid(
            row=3, column=1, sticky=tk.W, padx=(8, 0), pady=(6, 2))

        # ── action row ────────────────────────────────────────────────────────
        btns = tk.Frame(self, bg=BG)
        btns.pack(fill=tk.X, padx=14, pady=6)

        self.start_btn = ttk.Button(btns, text='▶  Start', command=self._start)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 4))

        self.stop_btn = ttk.Button(btns, text='■  Stop',
                                   command=self._request_stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 4))

        ttk.Button(btns, text='Clear', command=self._clear).pack(
            side=tk.LEFT, padx=(0, 4))

        ttk.Button(btns, text='Save Output…', command=self._save_output).pack(
            side=tk.RIGHT)

        # ── output area ───────────────────────────────────────────────────────
        out_frame = ttk.LabelFrame(self, text='Output', padding=(6, 4))
        out_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 4))

        self.out = scrolledtext.ScrolledText(
            out_frame,
            bg=BG, fg=FG,
            font=FONT_MONO,
            insertbackground=FG,
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=0,
            wrap=tk.WORD,
        )
        self.out.pack(fill=tk.BOTH, expand=True)
        self.out.tag_config('g',   foreground=GREEN)
        self.out.tag_config('r',   foreground=RED)
        self.out.tag_config('y',   foreground=YELLOW)
        self.out.tag_config('b',   foreground=BLUE)
        self.out.tag_config('dim', foreground=DIM)

        # ── status bar ────────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value='Ready')
        ttk.Label(self, textvariable=self.status_var,
                  style='Status.TLabel').pack(fill=tk.X, side=tk.BOTTOM)

    # ── dep check at startup ──────────────────────────────────────────────────
    def _check_deps(self):
        try:
            import camoufox  # noqa: F401
            import requests   # noqa: F401
        except ImportError as exc:
            self.start_btn.config(state=tk.DISABLED)
            self._write(
                f'[!] Missing dependency: {exc}\n'
                f'    Run:  pip install -r requirements.txt\n'
                f'    Then: python -m camoufox fetch\n',
                tag='r',
            )
            return

        # Check Firefox binary is present (camoufox needs a fetch step)
        try:
            from camoufox.pkgman import get_path
            get_path()
        except Exception:
            self._write(
                '[!] camoufox Firefox binary not found.\n'
                '    Fetching now — this is a one-time download…\n',
                tag='y',
            )
            self._fetch_camoufox()

    def _fetch_camoufox(self):
        def _do():
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'camoufox', 'fetch'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    self._q.put(('[+] camoufox fetch complete.\n', 'g'))
                else:
                    self._q.put((
                        f'[-] camoufox fetch failed:\n{result.stderr}\n', 'r'
                    ))
            except Exception as exc:
                self._q.put((f'[-] {exc}\n', 'r'))
        threading.Thread(target=_do, daemon=True).start()

    # ── placeholder helpers ───────────────────────────────────────────────────
    _PH_TEXT = 'optional — e.g. 127.0.0.1:8080 or socks5://host:port'

    def _ph_clear(self, widget):
        if widget.get() == self._PH_TEXT:
            widget.delete(0, tk.END)
            widget.config(foreground=FG)

    def _ph_restore(self, widget):
        if not widget.get():
            widget.insert(0, self._PH_TEXT)
            widget.config(foreground=DIM)

    # ── output helpers ────────────────────────────────────────────────────────
    def _write(self, text, tag=None):
        clean = _strip(text)
        if not clean:
            return
        self.out.config(state=tk.NORMAL)
        t = tag or _color_tag(clean)
        if t:
            self.out.insert(tk.END, clean + ('\n' if not clean.endswith('\n') else ''), t)
        else:
            self.out.insert(tk.END, clean + ('\n' if not clean.endswith('\n') else ''))
        self.out.see(tk.END)
        self.out.config(state=tk.DISABLED)

    def _poll(self):
        try:
            while True:
                item = self._q.get_nowait()
                if item == '__done__':
                    self._on_done()
                elif isinstance(item, tuple):
                    self._write(item[0], tag=item[1])
                else:
                    self._write(item)
        except queue.Empty:
            pass
        self.after(40, self._poll)

    def _on_done(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set('Done')
        self._thread = None

    def _clear(self):
        self.out.config(state=tk.NORMAL)
        self.out.delete('1.0', tk.END)
        self.out.config(state=tk.DISABLED)
        self.status_var.set('Ready')

    def _save_output(self):
        path = filedialog.asksaveasfilename(
            initialdir=ROOT,
            defaultextension='.txt',
            filetypes=[('Text files', '*.txt'), ('All files', '*.*')],
        )
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(_strip(self.out.get('1.0', tk.END)))
            self.status_var.set(f'Saved → {path}')

    def _browse_config(self):
        path = filedialog.askopenfilename(
            initialdir=ROOT,
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
        )
        if path:
            self.config_var.set(path)

    # ── run ───────────────────────────────────────────────────────────────────
    def _start(self):
        dork = self.dork_var.get().strip()
        if not dork:
            messagebox.showwarning('Input required', 'Please enter a dork keyword.')
            return

        raw_proxy = self.proxy_var.get().strip()
        proxy = None if (not raw_proxy or raw_proxy == self._PH_TEXT) else raw_proxy

        try:
            from lib.core import run_dork  # noqa: F401
        except ImportError as exc:
            messagebox.showerror('Import error', str(exc))
            return

        self._stop_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set('Running…')
        self._write(f'[*] Starting — dork: {dork}\n', tag='b')

        def worker():
            from lib.core import run_dork
            try:
                run_dork(
                    dork=dork,
                    proxy=proxy,
                    config_path=self.config_var.get().strip(),
                    scan=self.scan_var.get(),
                    output_cb=lambda line: self._q.put(line),
                    stop_event=self._stop_event,
                )
            except Exception as exc:
                self._q.put(f'[-] Error: {exc}\n')
            finally:
                self._q.put('__done__')

        self._thread = threading.Thread(target=worker, daemon=True)
        self._thread.start()

    def _request_stop(self):
        self._stop_event.set()
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set('Stopping…')


# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = App()
    app.mainloop()
