import json
import os

_R = 8.314462  # J/(mol·K)
_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'nasa_coeffs.json')

with open(_DATA_PATH) as f:
    _nasa_data = json.load(f)


def _coeffs(species: str, T: float) -> list:
    entry = _nasa_data[species]
    return entry['low'] if T <= entry['Tmid'] else entry['high']


def h_nasa(species: str, T: float) -> float:
    """Molar enthalpy H in J/mol (includes hf° via a6 coefficient)."""
    # integrate Cp/T dT → h/RT
    a = _coeffs(species, T)
    h_over_RT = a[0] + a[1]*T/2 + a[2]*T**2/3 + a[3]*T**3/4 + a[4]*T**4/5 + a[5]/T
    return h_over_RT * _R * T
