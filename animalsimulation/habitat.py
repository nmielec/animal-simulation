import random
import logging

from animal import Animal
from util import Season, DeathCause, month_to_season, get_data, Gender

ANIMAL_DATA, HABITAT_DATA = get_data()

logging.getLogger(__name__)

class Habitat(object):
    def __init__(self, type, species):
        self.type = type
        self.food_stock = 0
        self.water_stock = 0
        self.species = species
        self.replenish()

        self.population = []
        self.init_population(num=30, age_in_years=5)

    def season_temperature(self, season):
        return HABITAT_DATA[self.type]['average_temperature'][season.lower()]

    def replenish(self):
        self.food_stock += HABITAT_DATA[self.type]['monthly_food']
        self.water_stock += HABITAT_DATA[self.type]['monthly_water']

        factor = 20
        if self.food_stock > factor * HABITAT_DATA[self.type]['monthly_food']:
            self.food_stock = factor * HABITAT_DATA[self.type]['monthly_food']
        if self.water_stock > factor * HABITAT_DATA[self.type]['monthly_water']:
            self.water_stock = factor * HABITAT_DATA[self.type]['monthly_water']

    def month_temperature(self, month):
        if random.random() < 0.5/100:
            max_dev = 15
        else:
            max_dev = 5
        return self.season_temperature(month_to_season(month).name) + random.randint(-max_dev, +max_dev)

    def tick(self, month):
        self.current_month = month
        self.current_temperature = self.month_temperature(month)

        self.replenish()

        self.feed_population()

        self.breed_population()

        self.tick_population()

        self.eliminate_population()

    def init_population(self, num=30, age_in_years=0):
        """Adds the first num animals to the population"""
        self.population = []
        for _ in range(num):
            gender = random.choice([Gender.MALE, Gender.FEMALE])
            animal = Animal(self.species, gender)
            animal.age = age_in_years
            self.population.append(animal)

    def feed_population(self):
        """Get animals to eat and drink, and apply consequences on the habitat

        The animals who can drink and eat dependent on the amount of resources left are selected randomly
        """
        random.shuffle(self.population)
        num_can_eat = self.food_stock // ANIMAL_DATA[self.species]['monthly_food_consumption']
        for animal in sorted(self.population[:num_can_eat], key=lambda a: a.id):
            logging.debug('{} ate'.format(animal))
            animal.eat()
        self.food_stock -= len(self.population[:num_can_eat]) * ANIMAL_DATA[self.species]['monthly_food_consumption']

        random.shuffle(self.population)
        num_can_drink = self.water_stock // ANIMAL_DATA[self.species]['monthly_water_consumption']
        for animal in sorted(self.population[:num_can_drink], key=lambda a: a.id):
            logging.debug('{} drank'.format(animal))
            animal.drink()
        self.water_stock -= len(self.population[:num_can_drink]) * ANIMAL_DATA[self.species]['monthly_water_consumption']

    def breed_population(self):
        """This method gets female animal pregnant and checks for new births

        TODO: there might be a better way to do all this, for example check for pregnancy in the animal tick and somehow communicate the new birth to the simulation
        """
        available_females = [animal for animal in self.population if animal.can_breed()]
        available_males = self.get_males()

        # Get available females pregnant
        if len(available_males) > 0 and len(available_females) > 0 and month_to_season(self.current_month) == Season.SPRING:
            num_can_eat = self.food_stock // ANIMAL_DATA[self.species]['monthly_food_consumption']
            for female_animal in available_females:
                if num_can_eat >= len(self.population) or random.random() < 0.005:
                    female_animal.get_pregnant()

        # End pregnancies
        new_population = []
        for animal in self.population:
            new_population.append(animal)
            if animal.pregnancy_months_remaining == 0:
                # animal_stats = self.animal_stats.loc[animal.id]
                # animal_stats.children += 1
                newborn = animal.give_birth()
                new_population.append(newborn)
                # self.log_animal(newborn)

        self.population = new_population

    def tick_population(self):
        for animal in self.population:
            animal.tick(self.current_temperature)

    def eliminate_population(self):
        """Removes animals which are dying from the population and logs the death cause

        TODO: The logical part of this function might be better placed inside the animal class
        a method of animal checking if it is dying that returns the cause of death which would be logged here
        """
        self.current_deaths = 0
        new_population = []
        for animal in self.population:
            death_cause = None
            if animal.last_drank_months > 1:
                logging.info('{} died of thirst'.format(animal))
                death_cause = DeathCause.THIRST
            elif animal.last_ate_months > 3:
                logging.info('{} died of hunger'.format(animal))
                death_cause = DeathCause.HUNGER
            elif animal.is_old():
                logging.info('{} died of old age'.format(animal))
                death_cause = DeathCause.AGE
            elif animal.cold_for > 1:
                logging.info('{} died of cold'.format(animal))
                death_cause = DeathCause.COLD
            elif animal.hot_for > 1:
                logging.info('{} died of heat'.format(animal))
                death_cause = DeathCause.HEAT
            else:
                logging.debug('{} survived'.format(animal))
                new_population.append(animal)
            if death_cause is not None:
                # pass
                animal_stats = self.animal_stats.loc[animal.id]
                animal_stats.death_cause = death_cause.name.lower()
                animal_stats.year_death = self.current_year
                animal_stats.month_death = self.current_month
                self.current_deaths += 1

        self.population = new_population

    def get_males(self):
        return [animal for animal in self.population if animal.is_male()]

    def get_females(self):
        return [animal for animal in self.population if animal.is_female()]