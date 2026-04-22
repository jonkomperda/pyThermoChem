import tkinter as tk
from tkinter import ttk


class ResultsPanel(ttk.Frame):
    """Results display using ttk.Treeview for stoichiometry tables."""

    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    # ── layout ────────────────────────────────────────────────
    def _build(self):
        # reactants treeview
        lf = ttk.LabelFrame(self, text="Reactants", padding=4)
        lf.pack(fill=tk.X, padx=4, pady=(4, 0))
        self._reactant_tree = self._make_tree(lf, self._reactant_tags)
        self._pack_scroll(self._reactant_tree, lf)

        # products treeview
        lf = ttk.LabelFrame(self, text="Products", padding=4)
        lf.pack(fill=tk.X, padx=4, pady=(4, 0))
        self._product_tree = self._make_tree(lf, self._product_tags)
        self._pack_scroll(self._product_tree, lf)

        # combustion properties
        lf = ttk.LabelFrame(self, text="Combustion Properties", padding=4)
        lf.pack(fill=tk.X, padx=4, pady=(4, 0))
        self._lbl_lhv = ttk.Label(lf, text="LHV:        --", font=("Helvetica", 10))
        self._lbl_lhv.pack(anchor=tk.W, pady=(0, 2))
        self._lbl_hhv = ttk.Label(lf, text="HHV:        --", font=("Helvetica", 10))
        self._lbl_hhv.pack(anchor=tk.W, pady=(0, 2))
        self._lbl_afr = ttk.Label(lf, text="AFR:        --", font=("Helvetica", 10))
        self._lbl_afr.pack(anchor=tk.W, pady=(0, 2))

        # adiabatic flame temperature
        lf = ttk.LabelFrame(self, text="Adiabatic Flame Temperature", padding=4)
        lf.pack(fill=tk.X, padx=4, pady=(4, 0))
        self._lbl_tad = ttk.Label(
            lf, text="T_ad:  --",
            font=("Helvetica", 13, "bold"), foreground="#1a3c6e")
        self._lbl_tad.pack(anchor=tk.W)

        # rich-mixture warning (hidden by default)
        self._warn = ttk.Label(
            self,
            text="\u26a0 Rich mixture \u2014 CO and H\u2082 present in products",
            foreground="#b86e10", font=("Helvetica", 10, "italic"))
        self._warn.pack_forget()

    def _make_tree(self, parent, row_tags):
        cols = ("Species", "n (mol)", "Mol frac", "Mass frac")
        tree = ttk.Treeview(parent, columns=cols, show="headings",
                            selectmode=tk.NONE, height=8)
        tree.heading("Species", text="Species")
        tree.heading("n (mol)", text="n (mol)")
        tree.heading("Mol frac", text="Mol frac")
        tree.heading("Mass frac", text="Mass frac")
        tree.column("Species", width=150, anchor=tk.W)
        tree.column("n (mol)", width=110, anchor=tk.W)
        tree.column("Mol frac", width=110, anchor=tk.W)
        tree.column("Mass frac", width=110, anchor=tk.W)
        tree.tag_configure("Reactant", background="#e8f0fe")
        tree.tag_configure("Product", background="#e6f4ea")
        tree.tag_configure("ReactantHead", background="#d0e0f0",
                           font=("Helvetica", 9, "bold"))
        tree.tag_configure("ProductHead", background="#c8e6d0",
                           font=("Helvetica", 9, "bold"))
        return tree

    @staticmethod
    def _pack_scroll(tree, parent):
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # ── row colour helpers ────────────────────────────────────
    @staticmethod
    def _reactant_tags(n):
        """Cycle through a header row and coloured reactant rows."""
        tags = []
        for i in range(n):
            tags.append("ReactantHead" if i == 0 else "Reactant")
        return tags

    @staticmethod
    def _product_tags(n):
        tags = []
        for i in range(n):
            tags.append("ProductHead" if i == 0 else "Product")
        return tags

    # ── public API ────────────────────────────────────────────
    def show(self, *, bal: dict, frac: dict, T_display: str,
             lhv_display: str, hhv_display: str, afr: float):
        # ── Reactants ──
        self._reactant_tree.delete(*self._reactant_tree.get_children())
        rkeys = list(bal["reactants"])
        for i, sp in enumerate(rkeys):
            n = bal["reactants"][sp]
            xi = frac["mol_react"].get(sp, 0)
            yi = frac["mass_react"].get(sp, 0)
            self._reactant_tree.insert("", tk.END,
                                       values=(sp, f"{n:.4f}",
                                               f"{xi:.4f}", f"{yi:.4f}"),
                                       tags=self._reactant_tags(len(rkeys)))

        # ── Products ──
        self._product_tree.delete(*self._product_tree.get_children())
        pkeys = list(bal["products"])
        for i, sp in enumerate(pkeys):
            n = bal["products"][sp]
            xi = frac["mol_prod"].get(sp, 0)
            yi = frac["mass_prod"].get(sp, 0)
            self._product_tree.insert("", tk.END,
                                      values=(sp, f"{n:.4f}",
                                              f"{xi:.4f}", f"{yi:.4f}"),
                                      tags=self._product_tags(len(pkeys)))

        # ── Properties ──
        self._lbl_lhv.config(text=f"LHV:        {lhv_display}")
        self._lbl_hhv.config(text=f"HHV:        {hhv_display}")
        self._lbl_afr.config(text=f"AFR:        {afr:.4f}  kg air / kg fuel")

        # ── AFT ──
        self._lbl_tad.config(text=f"T_ad:  {T_display}")

        # ── Warning ──
        has_co_h2 = any(sp in bal["products"] for sp in ("CO", "H2"))
        if has_co_h2:
            self._warn.pack(pady=(4, 0))
        else:
            self._warn.pack_forget()
