import json
import os
from combustion import balance
from nasa import h_nasa

_FUELS_PATH   = os.path.join(os.path.dirname(__file__), 'data', 'fuels.json')
_SPECIES_PATH = os.path.join(os.path.dirname(__file__), 'data', 'species.json')

with open(_FUELS_PATH)   as f: _fuels   = json.load(f)
with open(_SPECIES_PATH) as f: _species = json.load(f)

_MEAN_CP = {
    'CO2': 56.2,
    'H2O': 38.6,
    'N2':  33.7,
    'O2':  35.2,
    'CO':  33.6,
    'H2':  30.4,
}


def aft_simple(fuel_name: str, phi: float, T0: float = 298.15) -> float:
    """AFT using constant mean Cp values. Returns K."""
    f = _fuels[fuel_name]
    hf_fuel = f['hf']
    bal = balance(fuel_name, phi)

    # energy balance: H_products = H_reactants
    delta_h = sum(
        n * _species[sp]['hf']
        for sp, n in bal['products'].items()
        if sp in _species
    ) - hf_fuel

    cp_total = sum(
        n * _MEAN_CP[sp]
        for sp, n in bal['products'].items()
    )

    return T0 + (-delta_h) / cp_total


def aft_nasa(fuel_name: str, phi: float, T0: float = 298.15) -> float:
    """AFT via iterative energy balance using NASA 7-coeff polynomials. Returns K."""
    f = _fuels[fuel_name]
    hf_fuel = f['hf']
    bal = balance(fuel_name, phi)

    n_O2 = bal['reactants']['O2']
    n_N2 = bal['reactants']['N2']

    # reactant enthalpy at T0
    H_react = (hf_fuel
               + n_O2 * h_nasa('O2', T0)
               + n_N2 * h_nasa('N2', T0))

    def H_products(T: float) -> float:
        return sum(n * h_nasa(sp, T) for sp, n in bal['products'].items())

    def residual(T: float) -> float:
        return H_products(T) - H_react

    # bisection solver
    T_lo, T_hi = 600.0, 4500.0
    if residual(T_lo) * residual(T_hi) > 0:
        raise ValueError(
            f"Bisection failed for '{fuel_name}' at phi={phi}."
        )
    while (T_hi - T_lo) > 0.1:
        T_mid = (T_lo + T_hi) / 2.0
        if residual(T_lo) * residual(T_mid) <= 0:
            T_hi = T_mid
        else:
            T_lo = T_mid

    return (T_lo + T_hi) / 2.0
