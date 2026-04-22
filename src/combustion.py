import json
import os

_FUELS_PATH   = os.path.join(os.path.dirname(__file__), 'data', 'fuels.json')
_SPECIES_PATH = os.path.join(os.path.dirname(__file__), 'data', 'species.json')
_CAT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'fuel_categories.json')

with open(_FUELS_PATH)      as f: _fuels         = json.load(f)
with open(_SPECIES_PATH)    as f: _species        = json.load(f)
with open(_CAT_PATH) as f: _fuel_categories = json.load(f)

AIR_N2_O2_RATIO = 3.76


def fuel_names() -> list[str]:
    return sorted(_fuels.keys())


def fuel_category(fuel_name: str) -> str:
    """Return the category of a fuel, or 'unknown'."""
    for cat, fuels in _fuel_categories.items():
        if fuel_name in fuels:
            return cat
    return 'unknown'


def fuel_categories() -> list[str]:
    """Return sorted list of fuel categories."""
    return sorted(_fuel_categories.keys())


def fuels_in_category(cat: str) -> list[str]:
    """Return sorted list of fuel names in a category."""
    return sorted(_fuel_categories.get(cat, []))


def _stoich_coeff(fuel_name: str) -> float:
    f = _fuels[fuel_name]
    return f['C'] + f['H'] / 4.0 - f.get('O', 0) / 2.0


def balance(fuel_name: str, phi: float) -> dict:
    """Balance combustion reaction for a fuel at equivalence ratio phi."""
    if phi <= 0:
        raise ValueError(f"phi must be > 0, got {phi}")

    f = _fuels[fuel_name]
    x, y = f['C'], f['H']
    o = f.get('O', 0)
    a = x + y / 4.0 - o / 2.0

    o2_react = a / phi
    n2_react = AIR_N2_O2_RATIO * o2_react

    # reactant stream
    reactants = {fuel_name: 1.0, 'O2': o2_react, 'N2': n2_react}

    if phi <= 1.0:
        # lean/stoich: complete combustion
        products = {
            'CO2': x,
            'H2O': y / 2.0,
            'N2':  n2_react,
            'O2':  a * (1.0 / phi - 1.0),
        }
    else:
        products = _balance_rich(x, y, a, phi, n2_react)

    return {'reactants': reactants, 'products': products}


def _balance_rich(x: float, y: float, a: float, phi: float, n2: float) -> dict:
    B = y / 2.0 - 2.0 * a / phi + 2.0 * x
    n_CO  = x * B / (x + y / 2.0)
    n_CO2 = x - n_CO
    n_H2O = 2.0 * a / phi - 2.0 * x + n_CO
    n_H2  = y / 2.0 - n_H2O

    if n_H2O < 0 or n_H2 < 0:
        raise ValueError(
            f"phi={phi:.2f} exceeds model validity (soot formation not modelled). "
            f"Reduce phi below ~{_phi_max(x, y, a):.1f}."
        )

    return {'CO2': n_CO2, 'H2O': n_H2O, 'N2': n2, 'CO': n_CO, 'H2': n_H2}


def _phi_max(x: float, y: float, a: float) -> float:
    return 2.0 * a / x if x > 0 else 10.0


def compute_fractions(bal: dict, fuel_name: str) -> dict:
    f = _fuels[fuel_name]
    mw = {**{s: _species[s]['MW'] for s in _species}, fuel_name: f['MW']}

    def fracs(moles: dict) -> tuple[dict, dict]:
        total_mol  = sum(moles.values())
        total_mass = sum(n * mw[s] for s, n in moles.items())
        xf = {s: n / total_mol           for s, n in moles.items()}
        yf = {s: n * mw[s] / total_mass  for s, n in moles.items()}
        return xf, yf

    xi_r, yi_r = fracs(bal['reactants'])
    xi_p, yi_p = fracs(bal['products'])
    return {
        'mol_react':  xi_r, 'mol_prod':  xi_p,
        'mass_react': yi_r, 'mass_prod': yi_p,
    }
