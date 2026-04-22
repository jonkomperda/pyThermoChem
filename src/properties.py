import json
import os

_FUELS_PATH   = os.path.join(os.path.dirname(__file__), 'data', 'fuels.json')
_SPECIES_PATH = os.path.join(os.path.dirname(__file__), 'data', 'species.json')

with open(_FUELS_PATH)   as f: _fuels   = json.load(f)
with open(_SPECIES_PATH) as f: _species = json.load(f)

_AIR_N2_O2 = 3.76
_HF_H2O_GAS = -241845.0
_HF_H2O_LIQ = -285830.0
_HF_CO2     = -393546.0
_MW_O2  = 31.99886
_MW_N2  = 28.01344


def lhv(fuel_name: str) -> float:
    """Lower heating value in J/kg (H2O product as gas)."""
    f = _fuels[fuel_name]
    x, y = f['C'], f['H']
    hf_fuel = f['hf']
    mw_fuel = f['MW']
    # heat of combustion: H_products - H_reactants
    delta_h = x * _HF_CO2 + (y / 2.0) * _HF_H2O_GAS - hf_fuel
    return -delta_h / (mw_fuel * 1e-3)


def hhv(fuel_name: str) -> float:
    """Higher heating value in J/kg (H2O product as liquid)."""
    f = _fuels[fuel_name]
    y = f['H']
    # LHV + latent heat of condensation for water produced
    return lhv(fuel_name) - (y / 2.0) * (_HF_H2O_LIQ - _HF_H2O_GAS) / (f['MW'] * 1e-3)


def afr_stoich(fuel_name: str) -> float:
    """Stoichiometric air-fuel ratio (mass of air / mass of fuel)."""
    f = _fuels[fuel_name]
    x, y = f['C'], f['H']
    # stoich O2 demand (corrected for fuel oxygen)
    a = x + y / 4.0 - f.get('O', 0) / 2.0
    mass_air  = a * _MW_O2 + a * _AIR_N2_O2 * _MW_N2
    mass_fuel = f['MW']
    return mass_air / mass_fuel
