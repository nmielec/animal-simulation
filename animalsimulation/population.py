class Population(list):
    def males(self):
        return [animal for animal in self if animal.is_male()]

    def females(self):
        return [animal for animal in self if animal.is_female()]