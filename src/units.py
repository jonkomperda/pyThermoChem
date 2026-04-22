_KJ_PER_BTU    = 1.05505585262
_LB_PER_KG     = 2.20462262185
_BTU_LB_PER_KJ_KG = 1.0 / (_KJ_PER_BTU * _LB_PER_KG)


def K_to_C(T_K: float) -> float:
    return T_K - 273.15


def K_to_F(T_K: float) -> float:
    return T_K * 9.0 / 5.0 - 459.67


def jkg_to_btu_lb(kj_per_kg: float) -> float:
    """Convert kJ/kg to BTU/lb."""
    return kj_per_kg * _BTU_LB_PER_KJ_KG


def btu_lb_to_jkg(btu_per_lb: float) -> float:
    """Convert BTU/lb to kJ/kg."""
    return btu_per_lb / _BTU_LB_PER_KJ_KG
