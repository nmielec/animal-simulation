#coding: utf-8
import random
import logging
import pandas as pd

from animalsimulation.habitat import Habitat
from animalsimulation.animal import Animal
from animalsimulation.util import get_data, Gender, month_to_season, Season

ANIMAL_DATA, HABITAT_DATA = get_data()

logging.basicConfig(filename='test.log', filemode='w', level=logging.INFO)

class Simulation(object):
    def __init__(self, habitat_type, species, start_month=1):
        self.habitat = Habitat(habitat_type)
        self.species = species
        self.current_year = 0
        self.current_month = start_month
        self.months = 0

        self.init_population(num=10, age_in_years=9)

        self.stats = pd.DataFrame(columns=['elapsed_months', 'year', 'month', 'temperature', 'food_stock', 'water_stock', 'male_population', 'female_population'])
        self.month_stats = []
        self.animal_stats = pd.DataFrame(columns=['id', 'short_id', 'year_birth', 'month_birth', 'year_death', 'month_death', 'children'])

    def run_one_month(self):
        self.current_temperature = self.habitat.month_temperature(self.current_month)
        logging.info('----------------------------------------------------')
        logging.info('Elapsed months {}'.format(self.months))
        logging.info('{} / {}'.format(self.current_month, self.current_year))
        logging.info('Temperature {}°'.format(self.current_temperature))
        logging.info('Habitat reserves {} food, {} water'.format(self.habitat.food_stock, self.habitat.water_stock))
        logging.info('{} animals : {}'.format(
            len(self.population),
                ', '.join((str(animal) for animal
                                       in sorted(self.population, key=lambda a: (a.age, a.id))))
            )
        )
        self.current_stats = {
            'births': 0,
            'deaths': {
                'hunger': 0,
                'thirst': 0,
                'cold': 0,
                'hot': 0,
                'age': 0,
                'elapsed_months': self.months,
                'year': self.current_year,
                'month': self.current_month,
                'temperature': self.current_temperature,
                'food_stock': self.habitat.food_stock,
                'water_stock': self.habitat.water_stock,
                'male_population': len([animal for animal in self.population if animal.gender == Gender.male]),
                'female_population': len([animal for animal in self.population if animal.gender == Gender.female]),
            },
        }
        self.feed_animals()

        for animal in self.population:
            animal.tick(self.current_temperature)

        self.breed_animals()
        self.replenish_habitat()
        self.eliminate_dying()
        self.fill_stats()

        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1

        self.months += 1

    def fill_stats(self):
        self.stats = self.stats.append({
            'elapsed_months': self.months,
            'year': self.current_year,
            'month': self.current_month,
            'temperature': self.current_temperature,
            'food_stock': self.habitat.food_stock,
            'water_stock': self.habitat.water_stock,
            'male_population': len([animal for animal in self.population if animal.gender == Gender.male]),
            'female_population': len([animal for animal in self.population if animal.gender == Gender.female]),
        }, ignore_index=True)

    def eliminate_dying(self):
        new_population = []
        for animal in self.population:
            if animal.last_drank_months > 1:
                logging.info('{} died of thirst'.format(animal))
            elif animal.last_ate_months > 3:
                logging.info('{} died of hunger'.format(animal))
            elif animal.is_old():
                logging.info('{} died of old age'.format(animal))
            elif animal.cold_for > 1:
                logging.info('{} died of cold'.format(animal))
            elif animal.hot_for > 1:
                logging.info('{} died of cold'.format(animal))
            else:
                logging.debug('{} survived'.format(animal))
                new_population.append(animal)
        self.population = new_population


    def replenish_habitat(self):
        self.habitat.replenish()

    def breed_animals(self):
        available_females = [animal for animal in self.population if animal.can_breed()]
        available_males = [animal for animal in self.population if animal.gender == Gender.male]


        if len(available_males) > 0 and len(available_females) > 0 and month_to_season(self.current_month) == Season.spring:
            num_can_eat = self.habitat.food_stock // ANIMAL_DATA[self.species]['monthly_food_consumption']
            if num_can_eat >= len(self.population):
                for female_animal in available_females:
                    female_animal.get_pregnant()
                    logging.debug('Female {} got pregnant'.format(female_animal))
            else:
                for female_animal in available_females:
                    if random.random() < 0.005:
                        female_animal.get_pregnant()
                        logging.debug('Female {} got pregnant'.format(female_animal))

        new_population = []
        for animal in self.population:
            new_population.append(animal)
            if animal.pregnancy_months_remaining == 0:
                animal.give_birth()
                gender = Gender.male if random.random() < 0.5 else Gender.female
                newborn = Animal(self.species, gender)
                new_population.append(newborn)
                logging.debug('{} animal {} was born'.format(gender.name, new_population[-1]))

        self.population = new_population

    def feed_animals(self):
        random.shuffle(self.population)
        num_can_eat = self.habitat.food_stock // ANIMAL_DATA[self.species]['monthly_food_consumption']
        for animal in self.population[:num_can_eat]:
            logging.debug('Animal {} ate'.format(animal))
            animal.eat()
        self.habitat.food_stock -= len(self.population[:num_can_eat]) * ANIMAL_DATA[self.species]['monthly_food_consumption']

        random.shuffle(self.population)
        num_can_drink = self.habitat.water_stock // ANIMAL_DATA[self.species]['monthly_water_consumption']
        for animal in self.population[:num_can_drink]:
            logging.debug('Animal {} drank'.format(animal))
            animal.drink()
        self.habitat.water_stock -= len(self.population[:num_can_drink]) * ANIMAL_DATA[self.species]['monthly_water_consumption']


    def run_n_months(self, n_months):
        for _ in range(n_months):
            self.run_one_month()
            if len(self.population) == 0:
                return

    def run_year(self):
        self.run_n_months(n_months=12)

    def run_n_years(self, n_years):
        self.run_n_months(n_months=n_years*12)

    def run_while_not_dead(self, max_years=50):
        while len(self.population) > 0:
            self.run_one_month()
            if self.current_year == max_years:
                break

    def init_population(self, num=30, age_in_years=5):
        self.population = []
        for _ in range(num):
            gender = random.choice([Gender.male, Gender.female])
            self.population.append(Animal(self.species, gender))
            self.population[-1].age_months = age_in_years*12

    def __repr__(self):
        lines = [
            'Simulation : ',
            'Habitat : {}'.format(self.habitat.type),
            'Species : {}'.format(self.species)
        ]
        return '\n'.join(lines)


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    sim = Simulation(habitat_type='plains', species='bear', start_month=3)
    sim.run_while_not_dead(max_years=500)
    logging.info('\n' + str(sim.stats))

    sim.stats.to_csv('stats.csv')

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    x = sim.stats.elapsed_months / 12
    ax1.plot(x, sim.stats.food_stock, label='Food stock')
    ax1.plot(x, sim.stats.water_stock, label='Water stock')
    ax2.plot(x, sim.stats.male_population, label='Male animals')
    ax2.plot(x, sim.stats.female_population, label='Female animals')
    ax1.legend()
    ax2.legend()
    plt.show()
    # logging.info(sim.population)
    # logging.info(sim)

