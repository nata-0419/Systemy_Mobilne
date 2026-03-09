import tkinter as tk
from tkinter import ttk
import random
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class main:
    def __init__(self, root):
        # okno głowne
        self.root = root
        self.root.title("Stacja Bazowa - Natalia Góras")
        self.root.geometry("900x800")

        # Dane Symulacji
        self.tick = 0
        self.is_running = False
        self.channels = [0] * 10
        self.queue = []
        self.history_q = [0]
        self.history_w = [0]
        self.history_ro = [0]

        self.setup_ui()

    def setup_ui(self):
        # Główny kontener grid
        self.root.columnconfigure(0, weight=1)  # Parametry i Wyniki tekstowe
        self.root.columnconfigure(1, weight=1)  # Kanały i Liczniki
        self.root.columnconfigure(2, weight=2)  # Wykresy

        # Parametry i Tabele
        left_frame = ttk.Frame(self.root, padding=10)
        left_frame.grid(row=0, column=0, sticky="nsw")

        # Parametry
        param_lb = ttk.LabelFrame(left_frame, text="Parametry", padding=5)
        param_lb.pack(fill="x", pady=5)
        self.params = {
            "Liczba kanałów": "5",
            "Długość kolejki": "5",
            "Natężenie ruchu (Poissona)": "1.0",
            "Średnia długość rozmowy": "25",
            "Odchylenie standardowe(Gaussa)": "2",
            "Minimalna długość rzmowy": "5",
            "Maksymalna długość rozmowy": "35",
            "Czas symulacji": "35"
        }

        self.entries = {}
        for label, val in self.params.items():
            row = ttk.Frame(param_lb)
            row.pack(fill="x")
            ttk.Label(row, text=label, width=20).pack(side="left")
            e = ttk.Entry(row, width=10)
            e.insert(0, val)
            e.pack(side="right")
            self.entries[label] = e

        # Tabele z wyniki
        res_lb = ttk.LabelFrame(left_frame, text="Wyniki szczegółowe", padding=5)
        res_lb.pack(fill="both", expand=True)
        self.result_text = tk.Text(res_lb, height=15, width=40, font=("Courier", 8))
        self.result_text.pack()
        self.result_text.insert("1.0", "Liczba Poissona | Liczba Gaussa | Czas.Przyjścia | Czas.Obsługi\n" + "-" * 40 + "\n")

        # Kanały i Status
        mid_frame = ttk.Frame(self.root, padding=10)
        mid_frame.grid(row=0, column=1, sticky="n")
        ttk.Label(mid_frame, text="Kanały", font=("Arial", 12, "bold")).pack()
        self.chan_frame = ttk.Frame(mid_frame)
        self.chan_frame.pack(pady=10)
        self.chan_widgets = []
        for i in range(10):
            lbl = tk.Label(self.chan_frame, text="WOLNY", bg="green", fg="white", width=10, height=2, relief="sunken")
            lbl.grid(row=i // 2, column=i % 2, padx=2, pady=2)
            self.chan_widgets.append(lbl)

        self.status_lbl = ttk.Label(mid_frame, text="Kolejka: 0 / 10\nObsłużone: 0\nOdrzucone: 0", justify="center")
        self.status_lbl.pack(pady=20)




