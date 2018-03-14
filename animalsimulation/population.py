import random

from animal import Animal
from util import Gender

class Population(object):
    def __init__(self, species):
        self.species = species

        self.animals = []

    def init_population(self, num_animals=20, age_in_years=5):
        self.animals = []
        for _ in range(num_animals):
            gender = random.choice([Gender.MALE, Gender.FEMALE])
            animal = Animal(self.species, gender)
            animal.age = age_in_years
            self.animals.append(animal)

    def feed(self, food_stock, water_stock):
