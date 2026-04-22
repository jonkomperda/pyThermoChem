import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from combustion  import balance, compute_fractions, fuel_names, \
    fuel_categories, fuels_in_category
from properties  import lhv, hhv, afr_stoich
from aft         import aft_simple, aft_nasa
from units       import K_to_F, jkg_to_btu_lb
from gui.results_panel import ResultsPanel
from gui.export        import export_csv

# ── colour palette ──────────────────────────────────────────
BLUE_DARK   = "#1a3c6e"
BLUE_STEEL  = "#2e6da4"
BLUE_LIGHT  = "#e8f0fe"
BG_GRAY     = "#f5f5f5"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("pyThermoChem \u2014 Combustion Calculator")
        self.resizable(True, True)
        self._apply_theme()
        self._build_inputs()
        self._build_results()
        self._build_status_bar()
        self._last_result = None
        # Size to content after all widgets exist
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        self.minsize(650, 520)
        self.geometry(f"{w}x{h}")

    # ── theme ───────────────────────────────────────────────
    def _apply_theme(self):
        s = ttk.Style()
        s.theme_use("clam")

        s.configure(".", font=("Helvetica", 10))
        s.configure("TLabelFrame", font=("Helvetica", 10, "bold"),
                    foreground=BLUE_DARK, padding=6)
        s.configure("TLabelFrame.Label", font=("Helvetica", 10, "bold"),
                    foreground=BLUE_DARK)
        s.configure("TButton", padding=(8, 2), font=("Helvetica", 10))
        s.map("TButton", background=[("active", BLUE_STEEL)])
        s.configure("TCombobox", fieldbackground="white",
                    padding=2)
        s.configure("TRadiobutton", padding=2)
        s.configure("TScale", troughcolor="#d0d0d0",
                    background=BLUE_STEEL)
        s.configure("TSpinbox", fieldbackground="white",
                    padding=2, arrowsize=14)
        s.configure("Treeview", rowheight=24,
                    fieldbackground="white",
                    borderwidth=0)
        s.configure("Treeview.Heading",
                    font=("Helvetica", 9, "bold"),
                    background=BLUE_DARK, foreground="white")
        s.map("Treeview.Heading",
              background=[("active", BLUE_STEEL)])
        s.configure("TFrame", background=BG_GRAY)
        s.configure("Status.TLabel",
                    font=("Helvetica", 9), foreground="#555555")

    # ── inputs ──────────────────────────────────────────────
    def _build_inputs(self):
        frame = ttk.LabelFrame(self, text="Inputs", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Row 0: Category filter
        ttk.Label(frame, text="Category:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 4))
        self._cat_var = tk.StringVar(value='All')
        all_cats = ['All'] + fuel_categories()
        cat_cb = ttk.Combobox(frame, textvariable=self._cat_var,
                              values=all_cats, state='readonly',
                              width=12)
        cat_cb.grid(row=0, column=1, sticky=tk.W, padx=(0, 24))
        cat_cb.bind('<<ComboboxSelected>>', self._on_category_change)

        # Row 1: Fuel + phi
        ttk.Label(frame, text="Fuel:").grid(row=1, column=0, sticky=tk.W,
                                            padx=(0, 4))
        self._fuel_var = tk.StringVar(value='methane')
        fuel_cb = ttk.Combobox(frame, textvariable=self._fuel_var,
                                values=fuel_names(), state='readonly',
                                width=22)
        fuel_cb.grid(row=0, column=1, sticky=tk.W, padx=(0, 24))

        ttk.Label(frame, text="phi:").grid(row=1, column=2, sticky=tk.W,
                                           padx=(0, 4))
        self._phi_var = tk.DoubleVar(value=1.0)
        phi_spin = ttk.Spinbox(frame, textvariable=self._phi_var,
                                from_=0.1, to=2.0, increment=0.05,
                                format="%.2f", width=7)
        phi_spin.grid(row=1, column=3, sticky=tk.W, padx=(0, 4))
        self._phi_slider = ttk.Scale(frame, variable=self._phi_var,
                                     from_=0.1, to=2.0,
                                     orient=tk.HORIZONTAL, length=240,
                                     command=lambda v:
                                         self._phi_var.set(
                                             round(float(v), 2)))
        self._phi_slider.grid(row=1, column=4, sticky=tk.W)

        # Separator
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(
            row=2, column=0, columnspan=6, sticky=tk.EW, pady=(8, 4))

        # Row 3: AFT method
        ttk.Label(frame, text="AFT Method:").grid(
            row=3, column=0, sticky=tk.W, padx=(0, 4))
        self._method_var = tk.StringVar(value='simple')
        ttk.Radiobutton(frame, text="Simple (const Cp)",
                        variable=self._method_var,
                        value='simple').grid(
            row=3, column=1, sticky=tk.W, padx=(0, 8))
        ttk.Radiobutton(frame, text="NASA Polynomial",
                        variable=self._method_var,
                        value='nasa').grid(
            row=3, column=2, sticky=tk.W, padx=(0, 4))

        # Row 4: Units
        ttk.Label(frame, text="Units:").grid(
            row=4, column=0, sticky=tk.W, padx=(0, 4), pady=(4, 0))
        self._units_var = tk.StringVar(value='SI')
        ttk.Radiobutton(frame, text="SI  (K, kJ/kg)",
                        variable=self._units_var,
                        value='SI').grid(row=4, column=1, sticky=tk.W,
                                         padx=(0, 8))
        ttk.Radiobutton(frame, text="Imperial  (degF, BTU/lb)",
                        variable=self._units_var,
                        value='Imperial').grid(
            row=4, column=2, sticky=tk.W, padx=(0, 4), pady=(4, 0))

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=6,
                       sticky=tk.W, pady=(10, 0))
        ttk.Button(btn_frame, text="Calculate",
                   command=self._on_calculate).pack(
            side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="Export CSV",
                   command=self._on_export).pack(side=tk.LEFT)

    # ── results ─────────────────────────────────────────────
    def _build_results(self):
        self._results_panel = ResultsPanel(self)
        self._results_panel.pack(fill=tk.BOTH, expand=True,
                                 padx=10, pady=8)

    # ── status bar ──────────────────────────────────────────
    def _build_status_bar(self):
        self._status_frame = ttk.Frame(self)
        self._status_frame.pack(fill=tk.X, padx=10, pady=(0, 4))
        self._status_lbl = ttk.Label(
            self._status_frame, text="Ready", style="Status.TLabel")
        self._status_lbl.pack(side=tk.LEFT)

    def _update_status(self, fuel, phi, method, units):
        if phi < 0.99:
            mix = "Lean"
        elif phi > 1.01:
            mix = "Rich"
        else:
            mix = "Stoichiometric"
        self._status_lbl.config(
            text=f"{fuel}  |  phi={phi:.2f} ({mix})  |  "
                 f"{method}  |  {units}")

    def _on_category_change(self, event=None):
        cat = self._cat_var.get()
        if cat == 'All':
            fuels = fuel_names()
        else:
            fuels = fuels_in_category(cat)
        self._fuel_var['values'] = fuels
        self._fuel_var.set(fuels[0])

    # ── calculation ─────────────────────────────────────────
    def _on_calculate(self):
        fuel = self._fuel_var.get()
        try:
            phi = float(self._phi_var.get())
        except (ValueError, tk.TclError):
            messagebox.showerror("Input Error", "phi must be a number.")
            return

        try:
            # run combustion calculation
            bal     = balance(fuel, phi)
            frac    = compute_fractions(bal, fuel)
            lhv_val = lhv(fuel)
            hhv_val = hhv(fuel)
            afr_val = afr_stoich(fuel)
            aft_fn  = aft_nasa if self._method_var.get() == 'nasa' \
                      else aft_simple
            T_ad    = aft_fn(fuel, phi)
        except Exception as e:
            messagebox.showerror("Calculation Error", str(e))
            return

        units = self._units_var.get()
        if units == 'SI':
            # display in SI units
            T_display   = f"{T_ad:.1f} K"
            lhv_display = f"{lhv_val/1000:.1f} kJ/kg"
            hhv_display = f"{hhv_val/1000:.1f} kJ/kg"
        else:
            # display in Imperial units
            T_display   = f"{K_to_F(T_ad):.1f} degF"
            lhv_display = f"{jkg_to_btu_lb(lhv_val/1000):.1f} BTU/lb"
            hhv_display = f"{jkg_to_btu_lb(hhv_val/1000):.1f} BTU/lb"

        self._last_result = {
            'fuel': fuel, 'phi': phi,
            'method': self._method_var.get(), 'units': units,
            'T_ad_K': T_ad, 'LHV_Jkg': lhv_val, 'HHV_Jkg': hhv_val,
            'AFR': afr_val,
            'bal': bal, 'frac': frac,
        }

        self._results_panel.show(
            bal=bal, frac=frac,
            T_display=T_display,
            lhv_display=lhv_display,
            hhv_display=hhv_display,
            afr=afr_val,
        )
        self._update_status(fuel, phi,
                            self._method_var.get(), units)

    def _on_export(self):
        if self._last_result is None:
            messagebox.showinfo("No Data", "Run a calculation first.")
            return
        export_csv(self._last_result)
