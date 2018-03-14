
from habitat import Habitat
from population import Population

class World(object):
    def __init__(self, habitat_type, species, initial_month=3, pop_kwargs=None):
        self.habitat = Habitat(habitat_type, species)
        self.population = Population(species)

        if pop_kwargs is None:
            pop_kwargs = {}
        self.population.init_population(**pop_kwargs)

        self.month = initial_month

    def tick(self):
        self.habitat.tick(self.month)
        self.habitat.replenish()

        food_eaten, water_drunk = self.population.feed(self.habitat.food_stock, self.habitat.water_stock)
        self.habitat.food_stock -= food_eaten
        self.habitat.water_stock -= water_drunk

        self.population.breed()
        self.population.die()
        self.population.survive_temperature(self.habitat.temperature)

        self.month = 1 if self.month == 12 else self.month + 1

if __name__ == '__main__':
    w = World('plains', 'kangaroo')