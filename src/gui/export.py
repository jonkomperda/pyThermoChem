import csv
from tkinter import filedialog, messagebox
from units import K_to_F, jkg_to_btu_lb


def export_csv(result: dict) -> None:
    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        title="Save results as CSV",
        initialfile=f"{result['fuel']}_phi{result['phi']:.2f}.csv",
    )
    if not path:
        return

    # display values in selected units
    units  = result['units']
    T_ad_K = result['T_ad_K']
    bal    = result['bal']
    frac   = result['frac']

    if units == 'SI':
        T_val     = T_ad_K
        T_unit    = 'K'
        hv_factor = 1 / 1000
        hv_unit   = 'kJ/kg'
    else:
        T_val     = K_to_F(T_ad_K)
        T_unit    = 'degF'
        hv_factor = jkg_to_btu_lb(1 / 1000)
        hv_unit   = 'BTU/lb'

    with open(path, 'w', newline='') as f:
        w = csv.writer(f)

        # summary header
        w.writerow(['pyThermoChem - Combustion Results'])
        w.writerow(['Fuel',   result['fuel']])
        w.writerow(['phi',    f"{result['phi']:.4f}"])
        w.writerow(['Method', result['method']])
        w.writerow(['Units',  units])
        w.writerow([])

        w.writerow(['Property', 'Value', 'Unit'])
        w.writerow(['T_ad',         f"{T_val:.2f}",                    T_unit])
        w.writerow(['LHV',          f"{result['LHV_Jkg']*hv_factor:.2f}", hv_unit])
        w.writerow(['HHV',          f"{result['HHV_Jkg']*hv_factor:.2f}", hv_unit])
        w.writerow(['AFR (stoich)', f"{result['AFR']:.4f}",            'kg_air/kg_fuel'])
        w.writerow([])

        # species tables
        w.writerow(['Stream', 'Species', 'n_mol', 'mol_frac', 'mass_frac'])
        for sp, n in sorted(bal['reactants'].items()):
            w.writerow(['reactant', sp, f"{n:.6f}",
                        f"{frac['mol_react'].get(sp, 0):.6f}",
                        f"{frac['mass_react'].get(sp, 0):.6f}"])
        for sp, n in sorted(bal['products'].items()):
            w.writerow(['product', sp, f"{n:.6f}",
                        f"{frac['mol_prod'].get(sp, 0):.6f}",
                        f"{frac['mass_prod'].get(sp, 0):.6f}"])

    messagebox.showinfo("Exported", f"Results saved to:\n{path}")
