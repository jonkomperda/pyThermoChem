import json

#define globals
react = ['O2','N2']
prod  = ['CO2','H2O','N2','O2']
mol = {'react':{},'prod':{}}    # balance mols
xi  = {'react':{},'prod':{}}    # mol fractions
Yi  = {'react':{},'prod':{}}    # mass fractions
n_r = []                        # total mols reactants
n_p = []                        # total mols products
M   = []                        # total mass of mixture

# load our fuels from JSON database
fdata = open('fuels.json')
fuels = json.load(fdata)
del fdata

#load our species from JSON database
sdata = open('species.json')
speci = json.load(sdata)
del sdata

def balance(fuel,equiv=1.0):
    """balances reaction given a fuel and equivalance ratio"""
    curFuel = fuels[fuel]
    x,y = curFuel['C'],curFuel['H']
    
    # calculate a
    a = x + y / 4.0
    
    # calculate mols of reactant stream
    mol['react'][fuel] = 1.0
    mol['react']['O2'] = a / equiv
    mol['react']['N2'] = a * 3.76 / equiv
    
    #calculate mols of product stream
    mol['prod']['CO2'] = x
    mol['prod']['H2O'] = y/2.0
    mol['prod']['N2']  = a * 3.76 / equiv
    mol['prod']['O2']  = a*(1.0/equiv - 1.0)

def fractions(fuel):
    curFuel = fuels[fuel]
    
    #calculate total mols
    n_r = mol['react'][fuel]+mol['react']['O2']+mol['react']['N2']
    n_p = mol['prod']['CO2']+mol['prod']['H2O']+mol['prod']['N2']+mol['prod']['O2']
    
    # calculate mol fractions
    xi['react'][fuel] = mol['react'][fuel] / n_r
    for item in react:
        xi['react'][item] = mol['react'][item] / n_r
    for item in prod:
        xi['prod'][item] = mol['prod'][item] / n_p
    
    # calculate total mass
    M = mol['react'][fuel]*curFuel['MW'] + sum([mol['react'][item]*speci[item]['MW'] for item in react])
    
    # calculate mass fractions
    Yi['react'][fuel] = mol['react'][fuel]*curFuel['MW'] / M
    for item in react:
        Yi['react'][item] = mol['react'][item]*speci[item]['MW'] / M
    for item in prod:
        Yi['prod'][item] = mol['prod'][item]*speci[item]['MW'] / M

def Cp(fuel,T):
    """Calculates Cp of fuel based on temperature"""
    pass

balance('methane')
fractions('methane')
