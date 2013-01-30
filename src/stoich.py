import json
import sys, getopt

#define globals
react = ['O2','N2']
prod  = ['CO2','H2O','N2','O2']
mol = {'react':{},'prod':{}}    # balance mols
xi  = {'react':{},'prod':{}}    # mol fractions
Yi  = {'react':{},'prod':{}}    # mass fractions
n_r = []                        # total mols reactants
n_p = []                        # total mols products
M   = []                        # total mass of mixture

masses = {  'O2'    : 31.99886,
            'N2'    : 28.01344,
            'CO2'   : 44.00964,
            'H2O'   : 18.01532
         }

fuels = { 'methane'     : {'C':1.0,'H':4.0,'MW':16.043},
          'acetylene'   : {'C':2.0,'H':2.0,'MW':26.038},
          'ethene'      : {'C':2.0,'H':4.0,'MW':28.054},
          'ethane'      : {'C':2.0,'H':6.0,'MW':30.069},
          'propene'     : {'C':3.0,'H':6.0,'MW':42.080},
          'propane'     : {'C':3.0,'H':8.0,'MW':44.096},
          '1-butene'    : {'C':4.0,'H':8.0,'MW':56.107},
          'n-butane'    : {'C':4.0,'H':10.0,'MW':58.123},
          '1-pentene'   : {'C':5.0,'H':10.0,'MW':70.134},
          'n-pentane'   : {'C':5.0,'H':12.0,'MW':72.150},
          'benzene'     : {'C':6.0,'H':6.0,'MW':78.113},
          '1-hexene'    : {'C':6.0,'H':12.0,'MW':84.161},
          'n-hexane'    : {'C':6.0,'H':14.0,'MW':86.117},
          '1-heptene'   : {'C':7.0,'H':14.0,'MW':98.188},
          'n-heptane'   : {'C':7.0,'H':16.0,'MW':100.203},
        }

def balance(fuel,equiv):
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
    M = mol['react'][fuel]*curFuel['MW'] + sum([mol['react'][item]*masses[item] for item in react])
    
    # calculate mass fractions
    Yi['react'][fuel] = mol['react'][fuel]*curFuel['MW'] / M
    for item in react:
        Yi['react'][item] = mol['react'][item]*masses[item] / M
    for item in prod:
        Yi['prod'][item] = mol['prod'][item]*masses[item] / M
    
def printer():
    """Prints data in a pretty JSON format"""
    print 'Mols for balance:'
    print json.dumps(mol, sort_keys=True, indent=4)
    print '\nMol fractions:'
    print json.dumps(xi,sort_keys=True,indent=4)
    print '\nMass fractions:'
    print json.dumps(Yi,sort_keys=True,indent=4)

def getTerm(argv):
    """Sees if we have terminal input and passes data"""
    opts, args = getopt.getopt(argv, "h", ["help", "fuel=", "phi="])
    
    if len(opts) > 0:
        for item in opts:
            if len(opts) < 2:
                if 'fuel' in item[0]:
                    name = item[1]
                    phi = 1
            if len(opts) == 2:
                if 'fuel' in item[0]:
                    name = item[1]
                if 'phi' in item[0]:
                    phi = item[1]
        #balance(name,float(phi))
        return (name,float(phi))
    else:
        return False


if __name__ == '__main__':
    fromTerm = getTerm(sys.argv[1:])
    
    if not fromTerm:
        balance('propane',0.6)
        printer()
    else:
        balance(fromTerm[0],fromTerm[1])
        printer()