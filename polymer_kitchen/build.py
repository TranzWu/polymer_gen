from polymer_kitchen.parser import Parser
import numpy as np
import random
import copy

class Molecule():
    def __init__(self, recipe, atoms):
        self.recipe = recipe
        self.atoms = atoms

    def create_bonds(self):
        bonds = copy.deepcopy(self.recipe.bond_key_value)
        for b in bonds:
            for i in bonds[b]:
                bonds[b][i] = [self.atoms[j-1] for j in bonds[b][i]]
        
        self.bond_key_value = bonds
        return bonds

    def create_angles(self):
        angles = copy.deepcopy(self.recipe.angle_key_value)
        for a in angles:
            for i in angles[a]:
                angles[a][i] = [self.atoms[j-1] for j in angles[a][i]]
        self.angle_key_value = angles
        return angles

class Amorphous_builder():
    def __init__(self, formula):
        self.formula = formula
        self.formula.create_recipe()
        for i in formula.recipe:
            i.init()

    @property
    def stats(self):
        stats = {}
        for i in self.formula.recipe:
            for s in i.stats:
                if s in stats:
                    stats[s] += i.stats[s] * i.quantity
                else:
                    stats[s] = i.stats[s] * i.quantity
        return stats

    def create_raw_atoms(self):
        #return two lists: self.positions, self.type_list
        range_x = self.formula.box_size[0]
        range_y = self.formula.box_size[1]
        # self.position = np.random.uniform(low=0, high=range_x, 
        #                            size=(self.stats['total'], 2))
        x = np.linspace(0, range_x - 1.12, 15) + random.random()
        y = np.linspace(0, range_y - 1.12, 15) + random.random()
        g = np.meshgrid(x,y)
        print(x)
        positions = np.vstack(map(np.ravel, g)).T
        select = random.sample([i for i in range(len(x) * len(y))], self.stats['total'])
        self.position = positions[select]
        print(len(self.position))
        draw_from_the_box = [i for i in range(self.stats['total'])]
        index_to_type = {}
        for i in self.stats:
            if i != 'total':
                drawn = random.sample(draw_from_the_box, self.stats[i])
                index_to_type[i] = drawn
                for j in drawn:
                    draw_from_the_box.remove(j)
        self.index_to_type = index_to_type
        return

    def assign_atoms_to_molecule(self):
        select = copy.deepcopy(self.index_to_type)
        molecules = []
        for r in self.formula.recipe:
            for i in range(r.quantity):
                p = []
                for a in r.connect:
                    draw_atom = random.choice(select[a[1]])
                    p.append(draw_atom)
                    select[a[1]].remove(draw_atom)

                mol = Molecule(recipe=r, atoms=p)
                molecules.append(mol)

        self.molecules = molecules
        for m in self.molecules:
            m.create_bonds()
            m.create_angles()
        return 

    def create_bonds(self):
        bonds ={}
        all_bonds = [b for m in self.molecules for b in m.bond_key_value]
        all_r1 = [m.bond_key_value[b]['r1']
                 for m in self.molecules 
                 for b in m.bond_key_value]

        all_r2 = [m.bond_key_value[b]['r2']
                 for m in self.molecules 
                 for b in m.bond_key_value]
        #print(all_r1)
        #print(all_r2)
        help_list = [(b.length, b.intensity)
                    for m in self.molecules 
                    for b in m.bond_key_value]
        #print(help_list)
        help_set = set(help_list)

        help_index = [[idx for idx, j in enumerate(help_list) if j == i]for i in help_set]
        for i in list(help_index):
            bonds[all_bonds[i[0]]] = {}
            bonds[all_bonds[i[0]]]['r1'] = []
            bonds[all_bonds[i[0]]]['r2'] = []
            for j in i:
                for k in all_r1[j]:
                    bonds[all_bonds[i[0]]]['r1'].append(k)
                for k in all_r2[j]:
                    bonds[all_bonds[i[0]]]['r2'].append(k)
        self.bonds = bonds
        return 

    def create_angles(self):
        angles = {}
        all_angles = [a for m in self.molecules for a in m.angle_key_value]
        all_a1 = [m.angle_key_value[b]['a1']
                 for m in self.molecules 
                 for b in m.angle_key_value]

        all_a2 = [m.angle_key_value[b]['a2']
                 for m in self.molecules 
                 for b in m.angle_key_value]

        all_a3 = [m.angle_key_value[b]['a3']
                 for m in self.molecules 
                 for b in m.angle_key_value]

        help_list = [(a.theta, a.intensity)
                    for m in self.molecules 
                    for a in m.angle_key_value]

        help_set = set(help_list)
        help_index = [[idx for idx, j in enumerate(help_list) if j == i]for i in help_set]

        for i in list(help_index):
            angles[all_angles[i[0]]] = {}
            angles[all_angles[i[0]]]['a1'] = []
            angles[all_angles[i[0]]]['a2'] = []
            angles[all_angles[i[0]]]['a3'] = []
            for j in i:
                for k in all_a1[j]:
                    angles[all_angles[i[0]]]['a1'].append(k)
                for k in all_a2[j]:
                    angles[all_angles[i[0]]]['a2'].append(k)
                for k in all_a3[j]:
                    angles[all_angles[i[0]]]['a3'].append(k)
        self.angles = angles

        return

    def init(self):
        self.create_raw_atoms()
        self.assign_atoms_to_molecule()
        self.create_bonds()
        self.create_angles()
        return 

            