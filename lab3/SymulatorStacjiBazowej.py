import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import csv
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class SymulatorStacjiBazowej:
    # Inicjalizacja głównych struktur danych symulatora zgodnie z modelem
    def __init__(self, okno):
        self.okno = okno
        self.okno.title("Stacja Bazowa Natalia Góras - Model M/M/S/S")
        self.okno.geometry("1450x850")

        self.sekunda = 0
        self.czy_aktywny = False
        self.lista_zdarzen = []
        self.stan_kanalow = []
        self.kolejka = []
        self.historia_ro, self.historia_q, self.historia_w = [], [], []
        self.licznik_odrzuconych = 0
        self.licznik_obsluzonych = 0
        self.logi_danych = []

        self.stworz_gui()

    def stworz_gui(self):
        self.okno.columnconfigure(0, weight=1)
        self.okno.columnconfigure(1, weight=2)
        self.okno.columnconfigure(2, weight=2)

        panel_lewy = ttk.Frame(self.okno, padding=10)
        panel_lewy.grid(row=0, column=0, sticky="nsew")

        rama_param = ttk.LabelFrame(panel_lewy, text=" Parametry Symulacji ", padding=10)
        rama_param.pack(fill="x")

        self.pola = {}
        parametry = [
            ("Liczba kanałów (S):", "10"),
            ("Natężenie (Lambda):", "1.0"),
            ("Śr. rozmowa (N):", "20"),
            ("Odchylenie (Sigma):", "5"),
            ("Min dł. rozmowy:", "10"),
            ("Maks dł. rozmowy:", "30"),
            ("Długość kolejki:", "10"),
            ("Czas symulacji:", "60")
        ]
        for t, d in parametry:
            f = ttk.Frame(rama_param)
            f.pack(fill="x", pady=1)
            ttk.Label(f, text=t, width=18).pack(side="left")
            e = ttk.Entry(f, width=8)
            e.insert(0, d)
            e.pack(side="right")
            self.pola[t] = e

        self.btn_start = ttk.Button(panel_lewy, text="START SYMULACJI", command=self.sterowanie)
        self.btn_start.pack(fill="x", pady=10)

        self.btn_plik = ttk.Button(panel_lewy, text="OTWÓRZ PLIK WYNIKÓW", command=self.otworz_plik, state="disabled")
        self.btn_plik.pack(fill="x")

        ttk.Label(panel_lewy, text="\nLogi szczegółowe (txt):").pack(anchor="w")
        self.txt_logi = tk.Text(panel_lewy, height=22, width=40, font=("Courier New", 9))
        self.txt_logi.pack(fill="both", expand=True)

        panel_mid = ttk.Frame(self.okno, padding=10)
        panel_mid.grid(row=0, column=1, sticky="n")

        ttk.Label(panel_mid, text="KANAŁY", font=("Arial", 12, "bold")).pack()
        self.rama_kanalow = ttk.Frame(panel_mid)
        self.rama_kanalow.pack(pady=10)
        self.widok_kanalow = []

        self.lbl_info = ttk.Label(panel_mid, text="Status: Gotowy", font=("Arial", 10), justify="center")
        self.lbl_info.pack(pady=10)

        panel_prawy = ttk.Frame(self.okno, padding=10)
        panel_prawy.grid(row=0, column=2, sticky="nsew")
        self.fig, (self.os_q, self.os_w, self.os_ro) = plt.subplots(3, 1, figsize=(5, 8))
        self.fig.tight_layout(pad=3.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=panel_prawy)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    # KROK 1: Generowanie czasów przybycia (lambda_i) zgodnie z rozkładem Poissona
    # KROK 2: Tworzenie par (lambda_i, mii_i)
    # Dla każdego przybycia losujemy czas trwania rozmowy wg rozkładu Gaussa
    # Uwzględniamy parametry N, Sigma oraz sztywne granice Min i Maks

    def generuj_harmonogram(self):
        self.lista_zdarzen = []
        t = 0
        limit = int(self.pola["Czas symulacji:"].get())
        lam = float(self.pola["Natężenie (Lambda):"].get())

        while t < limit + 5:
            # Rozkład Poissona dla odstępów czasu
            odstep = -math.log(1.0 - random.random()) / lam
            t += odstep
            # Rozkład Gaussa dla czasu trwania
            czas_obslugi = random.gauss(float(self.pola["Śr. rozmowa (N):"].get()),
                                        float(self.pola["Odchylenie (Sigma):"].get()))
            # Ograniczenia Min i Maks
            czas_obslugi = max(float(self.pola["Min dł. rozmowy:"].get()),
                               min(float(self.pola["Maks dł. rozmowy:"].get()), czas_obslugi))
            self.lista_zdarzen.append({'t': t, 'mu': int(czas_obslugi)})

    def sterowanie(self):
        if not self.czy_aktywny:
            self.generuj_harmonogram()
            self.S = int(self.pola["Liczba kanałów (S):"].get())
            self.stan_kanalow = [0] * self.S
            self.sekunda = 0
            self.kolejka = []
            self.licznik_odrzuconych = 0
            self.licznik_obsluzonych = 0
            self.logi_danych = []
            self.historia_ro, self.historia_q, self.historia_w = [], [], []
            self.txt_logi.delete("1.0", tk.END)

            for w in self.widok_kanalow: w.destroy()
            self.widok_kanalow = []
            for i in range(self.S):
                l = tk.Label(self.rama_kanalow, text="WOLNY", bg="green", fg="white", width=12, height=2,
                             relief="raised")
                l.grid(row=i // 2, column=i % 2, padx=2, pady=2)
                self.widok_kanalow.append(l)

            self.czy_aktywny = True
            self.btn_start.config(text="STOP")
            self.btn_plik.config(state="disabled")
            self.krok_petli()
        else:
            self.czy_aktywny = False
            self.btn_start.config(text="START SYMULACJI")


    def krok_petli(self):
        limit = int(self.pola["Czas symulacji:"].get())
        if not self.czy_aktywny or self.sekunda >= limit:
            if self.sekunda >= limit:
                self.zapisz_i_koniec()
            return

        self.sekunda += 1

        for i in range(self.S):
            if self.stan_kanalow[i] > 0: self.stan_kanalow[i] -= 1
        nowe_zgloszenia = [z for z in self.lista_zdarzen if self.sekunda - 1 <= z['t'] < self.sekunda]

        for zgl in nowe_zgloszenia:
            zajeto = False
            for i in range(self.S):
                if self.stan_kanalow[i] == 0:
                    self.stan_kanalow[i] = zgl['mu']
                    self.licznik_obsluzonych += 1
                    zajeto = True
                    break
            if not zajeto:
                if len(self.kolejka) < int(self.pola["Długość kolejki:"].get()):
                    self.kolejka.append(zgl['mu'])
                else:
                    self.licznik_odrzuconych += 1

        # Usunięcie przetworzonych z listy Lambda
        self.lista_zdarzen = [z for z in self.lista_zdarzen if z['t'] >= self.sekunda]

        # Obsługa kolejki
        for i in range(self.S):
            if self.stan_kanalow[i] == 0 and self.kolejka:
                self.stan_kanalow[i] = self.kolejka.pop(0)

        # Obliczanie Rho, Q, W
        zajete = sum(1 for s in self.stan_kanalow if s > 0)
        rho = zajete / self.S
        q = len(self.kolejka)
        w = (self.licznik_odrzuconych * 0.1) + (q * 0.05)

        self.historia_ro.append(rho);
        self.historia_q.append(q);
        self.historia_w.append(w)
        self.logi_danych.append([self.sekunda, rho, q, w])

        # Logi tekstowe i UI
        self.txt_logi.insert(tk.END, f"S:{self.sekunda} | Ro:{rho:.2f} | Q:{q} | Nowe:{len(nowe_zgloszenia)}\n")
        self.txt_logi.see(tk.END)
        self.odswiez_ui(rho, q, limit)

        self.okno.after(1000, self.krok_petli)

    def odswiez_ui(self, rho, q, limit):
        for i in range(self.S):
            if self.stan_kanalow[i] > 0:
                self.widok_kanalow[i].config(bg="red", text=f"Zajęty {self.stan_kanalow[i]}s")
            else:
                self.widok_kanalow[i].config(bg="green", text="WOLNY")

        self.lbl_info.config(
            text=f"Czas: {self.sekunda}/{limit}s\nKolejka: {q}\nObsłużone: {self.licznik_obsluzonych}\nOdrzucone: {self.licznik_odrzuconych}")

        for os, dane, tyt, kol in [(self.os_q, self.historia_q, "Q", "red"), (self.os_w, self.historia_w, "W", "blue"),
                                   (self.os_ro, self.historia_ro, "Ro", "green")]:
            os.clear();
            os.plot(dane, color=kol);
            os.set_title(tyt, fontsize=8)
        self.canvas.draw()

    def zapisz_i_koniec(self):
        nazwa = "NG_wyniki_symulacji.csv"
        try:
            with open(nazwa, "w", newline="", encoding="utf-8") as f:
                pisarz = csv.writer(f, delimiter=";")
                pisarz.writerow(["PARAMETRY SYMULACJI"])
                for k, v in self.pola.items():
                    pisarz.writerow([k, v.get()])
                pisarz.writerow([])
                pisarz.writerow(["WYNIKI (KOLUMNY: Rho, Q, W)"])
                pisarz.writerow(["Sekunda", "Rho", "Q", "W"])
                pisarz.writerows(self.logi_danych)
            self.btn_plik.config(state="normal")
            messagebox.showinfo("Sukces", f"Symulacja zakończona.\nPlik '{nazwa}' został zapisany.")
        except Exception as err:
            messagebox.showerror("Błąd pliku", f"Nie można zapisać pliku:\n{err}")

    def otworz_plik(self):
        try:
            os.startfile("NG_wyniki_symulacji.csv")
        except:
            messagebox.showerror("Błąd", "Nie znaleziono pliku lub brak domyślnej aplikacji.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SymulatorStacjiBazowej(root)
    root.mainloop()