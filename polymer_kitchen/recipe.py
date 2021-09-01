class Bond():
    def __init__(self, input):
        self.input = input

    @property
    def text(self):
        return self.input.split()
    
    @property
    def index(self):
        return int(self.text[1])

    @property
    def length(self):
        return float(self.text[2])

    @property
    def intensity(self):
        return float(self.text[3])

    def __repr__(self):
        return f"(*length*:{self.length}, *intensity*:{self.intensity})"

class Angle():
    def __init__(self, input):
        self.input = input

    @property
    def text(self):
        return self.input.split()
    
    @property
    def index(self):
        return int(self.text[1])

    @property
    def theta(self):
        return float(self.text[2])

    @property
    def intensity(self):
        return float(self.text[3])

    def __repr__(self):
        return f"(*theta*:{self.theta}, *intensity*:{self.intensity})"

class Recipe():

    def __init__(self, input):
        self.input = input

    def key_value(self, key):
        for line in self.input:
            if key in line:
                clean = line.split()
        return int(clean[-1])

    def ini_quantity(self):
        return self.key_value('quantity')
    

    def ini_prms(self):
        marker = []
        for idx, line in enumerate(self.input):
            if 'PRMS' in line:
                marker.append(idx)
            if 'END prms' in line:
                marker.append(idx)
        assert(len(marker) == 2)
        assert(marker[0] < marker[1])
        return self.input[marker[0]+1:marker[1]]

    def ini_bonds(self):
        bond_list = []
        for line in self.prms:
            if 'bond' in line:
                b = Bond(line)
                bond_list.append(b)
        return bond_list

    def ini_angles(self):
        angle_list = []
        for line in self.prms:
            if 'angle' in line:
                agl = Angle(line)
                angle_list.append(agl)
        return angle_list
    
    def parse_paragraph(self, start, end):
        marker = []
        for idx, line in enumerate(self.input):
            if start in line:
                marker.append(idx)
            if end in line:
                marker.append(idx)

        assert(len(marker) == 2)
        assert(marker[0] < marker[1])
        text = self.input[marker[0]+1:marker[1]]
        text = [i.split() for i in text if i != '\n']
        text = [[int(j) for j in i] for i in text]
        return text

    @property
    def connect(self):
        return self.parse_paragraph('CONNECT', 'END connect')

    @property
    def stats(self):
        stats = {}
        stats['total'] = len(self.connect)
        for i in self.connect:
            if i[1] in stats:
                stats[i[1]] += 1
            else:
                stats[i[1]] = 1
        return stats

    def read_all_bonds(self):
        return self.parse_paragraph('BOND', 'END bond')

    @property
    def bond_key_value(self):
        bond_dic = {}
        for b in self.all_bonds:
            if self.bonds[b[0]-1] in bond_dic:
                bond_dic[self.bonds[b[0]-1]]['r1'].append(b[1])
                bond_dic[self.bonds[b[0]-1]]['r2'].append(b[2])
            else:
                bond_dic[self.bonds[b[0]-1]] = {}
                bond_dic[self.bonds[b[0]-1]]['r1'] = [b[1]]
                bond_dic[self.bonds[b[0]-1]]['r2'] = [b[2]]

        return bond_dic
    

    def read_all_angles(self):
        return self.parse_paragraph('ANGLE', 'END angle')

    @property
    def angle_key_value(self):
        angle_dic = {}
        for a in self.all_angles:
            if self.angles[a[0]-1] in angle_dic:
                angle_dic[self.angles[a[0]-1]]['a1'].append(a[1])
                angle_dic[self.angles[a[0]-1]]['a2'].append(a[2])
                angle_dic[self.angles[a[0]-1]]['a3'].append(a[3])
            else:
                angle_dic[self.angles[a[0]-1]] = {}
                angle_dic[self.angles[a[0]-1]]['a1'] = [a[1]]
                angle_dic[self.angles[a[0]-1]]['a2'] = [a[2]]
                angle_dic[self.angles[a[0]-1]]['a3'] = [a[3]]

        return angle_dic


    def init(self):
        self.prms = self.ini_prms()
        self.quantity = self.ini_quantity()
        self.bonds = self.ini_bonds()
        self.all_bonds = self.read_all_bonds()
        self.angles = self.ini_angles()
        self.all_angles = self.read_all_angles()

'''
The reason that you need this init function is that you don't want to 
call every function everytime you need the corresponding properties
(in some situations it would cause more serious problem other than
simple computational cost, for example, if you restore all the bonds
as objects, if you use the property decorator function to make it
a property, then everytime you want to use the property, it will
create a new instance of that bond class, which would make it impossible
to track the bond type if you want to store every possible bonds as
dicts)
'''


