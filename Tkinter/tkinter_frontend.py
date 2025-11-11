import tkinter as tk
from tkinter import ttk
import threading
import requests
import time

BACKEND_URL = "http://10.11.129.142:8000/data"
POLL_INTERVAL_MS = 5000  # 5 seconds

class NodeCard(ttk.Frame):
    def __init__(self, parent, node_id):
        super().__init__(parent, padding=12)
        self.node_id = node_id

        # Card styling
        self['borderwidth'] = 1
        self['relief'] = 'ridge'

        # Header
        self.title = ttk.Label(self, text=f"Node {node_id}", font=("Segoe UI", 14, "bold"))
        self.title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,8))

        # Metrics
        ttk.Label(self, text="Temperature (°C):", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w")
        self.temp_val = ttk.Label(self, text="--", font=("Consolas", 12, "bold"))
        self.temp_val.grid(row=1, column=1, sticky="e")

        ttk.Label(self, text="Humidity (%):", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w")
        self.hum_val = ttk.Label(self, text="--", font=("Consolas", 12, "bold"))
        self.hum_val.grid(row=2, column=1, sticky="e")

        # Timestamp
        self.ts = ttk.Label(self, text="Last update: --", font=("Segoe UI", 8))
        self.ts.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8,0))

        for i in range(2):
            self.columnconfigure(i, weight=1)

    def update_values(self, node_data: dict):
        try:
            t = node_data.get("temperature", None)
            h = node_data.get("humidity", None)
            ts = node_data.get("timestamp", "--")

            self.temp_val.config(text=f"{t:.2f}" if isinstance(t, (int, float)) else "--")
            self.hum_val.config(text=f"{h:.2f}" if isinstance(h, (int, float)) else "--")
            self.ts.config(text=f"Last update: {ts}")
        except Exception as e:
            # Fallback display on unexpected structure
            self.temp_val.config(text="--")
            self.hum_val.config(text="--")
            self.ts.config(text=f"Last update: error: {e}")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌡️ IoT Dashboard: Temperature & Humidity")
        self.geometry("960x540")
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except:
            pass

        # Top title
        ttk.Label(self, text="🌡️ IoT Dashboard: Temperature & Humidity",
                  font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(12, 4))

        # Connected nodes label
        self.nodes_header = ttk.Label(self, text="📡 Connected Nodes", font=("Segoe UI", 12))
        self.nodes_header.pack(anchor="w", padx=16)

        # Info/Status message
        self.info_var = tk.StringVar(value="Waiting for ESP nodes to send data...")
        self.info_label = ttk.Label(self, textvariable=self.info_var, foreground="#555")
        self.info_label.pack(anchor="w", padx=16, pady=(0, 8))

        # Scrollable canvas for cards (in case there are many nodes)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.cards_frame = ttk.Frame(self.canvas)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(16,0), pady=(0,16))
        self.scrollbar.pack(side="right", fill="y", padx=(0,16), pady=(0,16))

        # Create window inside canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")

        # Auto-resize the inner frame width to the canvas width
        self.cards_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status = ttk.Label(self, textvariable=self.status_var, anchor="w", relief="sunken")
        status.pack(side="bottom", fill="x")

        # Node widgets cache
        self.node_cards = {}

        # Start polling
        self._stop = False
        self.after(0, self.schedule_poll)

        # Clean shutdown
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # Keep inner frame width in sync with canvas width
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_close(self):
        self._stop = True
        self.destroy()

    def schedule_poll(self):
        if self._stop:
            return
        # Run network request off the main thread
        threading.Thread(target=self.fetch_and_update, daemon=True).start()
        # Schedule next poll
        self.after(POLL_INTERVAL_MS, self.schedule_poll)

    def fetch_and_update(self):
        start = time.time()
        try:
            r = requests.get(BACKEND_URL, timeout=4)
            if r.status_code == 200:
                data = r.json()
            else:
                data = {}
                self._set_status(f"Warning: HTTP {r.status_code}")
        except Exception as e:
            data = {}
            self._set_status(f"Error fetching data: {e}")

        # Push UI updates back to main thread
        self.after(0, lambda: self.update_ui(data, start))

    def _set_status(self, text):
        # Update status in main thread safely
        self.after(0, lambda: self.status_var.set(text))

    def update_ui(self, data: dict, started_at: float):
        # Info line
        if not data:
            self.info_var.set("Waiting for ESP nodes to send data...")
        else:
            self.info_var.set(f"Connected: {len(data)} node(s)")

        # Build / update cards
        existing_ids = set(self.node_cards.keys())
        current_ids = set(data.keys())

        # Remove cards for nodes that disappeared
        for removed_id in existing_ids - current_ids:
            self.node_cards[removed_id].destroy()
            del self.node_cards[removed_id]

        # Create or update cards for current nodes
        # Layout as a responsive grid (wrap every 3 columns)
        max_cols = 3
        for idx, node_id in enumerate(sorted(current_ids)):
            row = idx // max_cols
            col = idx % max_cols

            if node_id not in self.node_cards:
                card = NodeCard(self.cards_frame, node_id)
                self.node_cards[node_id] = card
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            # Update values
            self.node_cards[node_id].update_values(data.get(node_id, {}))

        # Configure grid weights for responsiveness
        for c in range(3):
            self.cards_frame.columnconfigure(c, weight=1)

        # Update status timing
        elapsed = (time.time() - started_at) * 1000.0
        self.status_var.set(f"Last refresh OK • {elapsed:.0f} ms")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
