from polymer_kitchen.recipe import Recipe

class Parser(Recipe):
    def __init__(self, recipe):
        self.fname = recipe

    @property
    def input(self):
        with open(self.fname) as f:
            rad = f.readlines()
        return rad 

    @property
    def N_recipe(self):
        return self.key_value('N_recipe')

    @property
    def dimensions(self):
        return self.key_value('dimensions')

    @property
    def atom_types(self):
        return self.key_value('atom_types')

    @property
    def box_size(self):
        for line in self.input:
            if 'box' in line:
                clean = line.split()
        clean = clean[1:]
        return [float(i) for i in clean]
    
    def create_recipe(self):
        start = []
        end = []
        recipe = []

        for idx, line in enumerate(self.input):
            if 'N = ' in line:
                start.append(idx)
            if 'END recipe' in line:
                end.append(idx)

        assert(len(start) == len(end))
        assert(len(start) == self.N_recipe)

        for i in range(self.N_recipe):
            rp = Recipe(self.input[start[i]:end[i]])
            recipe.append(rp)

        self.recipe = recipe
        return recipe
    
    
    
