from Tkinter import *
from stoich import *
import json

root = Tk()

fuelList = []
fuelListbox = Listbox(root)
fuelListbox.pack(fill=X)

for key in fuels:
    fuelList.append(key)
    fuelListbox.insert(END,key)

phiScale = Scale(root,from_=0.05,to=1,resolution=0.05,orient=HORIZONTAL)
phiScale.pack(fill=X)

def onClick():
    current = fuelListbox.curselection()
    myfuel = fuelList[int(current[0])]
    myPhi = phiScale.get()
    balance(myfuel,myPhi)
    text.delete('1.0',END)
    text.insert(END,'Mols for balance:\n')
    text.insert(END,json.dumps(mol, sort_keys=True, indent=4))
    text.insert(END,'\nMol fractions:\n')
    text.insert(END,json.dumps(xi,sort_keys=True,indent=4))
    text.insert(END,'\nMass fractions:\n')
    text.insert(END,json.dumps(Yi,sort_keys=True,indent=4))

b = Button(root,text='Go!', command = onClick)
b.pack()
text = Text()
text.pack(fill=BOTH,expand=1)





root.mainloop()
