#coding: utf-8
import random
import logging
import pandas as pd

from animalsimulation.habitat import Habitat
from animalsimulation.animal import Animal
from animalsimulation.util import get_data, Gender, month_to_season, Season, DeathCause

ANIMAL_DATA, HABITAT_DATA = get_data()

logging.basicConfig(filename='test.log', filemode='w', level=logging.INFO)

class Simulation(object):
    """Handler for the simulation
    Holds a species and a habitat and handles the interaction.
    Runs the simuation and gather the stats.

    TODO: the interaction between habitat and animals might be done in the habitat object
    """
    def __init__(self, habitat_type, species, start_month=1):
        self.habitat = Habitat(habitat_type)
        self.species = species
        self.current_year = 0
        self.current_month = start_month
        self.months = 0

        self.stats = pd.DataFrame(columns=['elapsed_months', 'year', 'month', 'temperature', 'food_stock', 'water_stock', 'male_population', 'female_population', 'deaths'])
        self.animal_stats = pd.DataFrame(columns=['short_id', 'year_birth', 'month_birth', 'year_death', 'month_death', 'death_cause', 'children'])

        self.init_population(num=10, age_in_years=9)


    def run_one_month(self):
        """Main method of the simulation, runs one month of the simulation"""
        self.current_temperature = self.habitat.month_temperature(self.current_month)
        logging.info('----------------------------------------------------')
        logging.info('Elapsed months {}'.format(self.months))
        logging.info('{} / {}'.format(self.current_month, self.current_year))
        logging.info('Temperature {}°'.format(self.current_temperature))
        logging.info('Habitat reserves {} food, {} water'.format(self.habitat.food_stock, self.habitat.water_stock))
        logging.info(
            '{} animals : {}'.format(
                len(self.population),
                ', '.join((str(animal) for animal
                           in sorted(self.population, key=lambda a: (a.age, a.id))))
            )
        )
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
            'male_population': len([animal for animal in self.population if animal.is_male()]),
            'female_population': len([animal for animal in self.population if animal.is_female()]),
            'deaths': self.current_deaths,
        }, ignore_index=True)

    def eliminate_dying(self):
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


    def replenish_habitat(self):
        self.habitat.replenish()

    def breed_animals(self):
        """This method gets female animal pregnant and checks for new births

        TODO: there might be a better way to do all this, for example check for pregnancy in the animal tick and somehow communicate the new birth to the simulation
        """
        available_females = [animal for animal in self.population if animal.can_breed()]
        available_males = [animal for animal in self.population if animal.is_male()]

        # Get available females pregnant
        if len(available_males) > 0 and len(available_females) > 0 and month_to_season(self.current_month) == Season.SPRING:
            num_can_eat = self.habitat.food_stock // ANIMAL_DATA[self.species]['monthly_food_consumption']
            for female_animal in available_females:
                if num_can_eat >= len(self.population) or random.random() < 0.005:
                    female_animal.get_pregnant()

        # End pregnancies
        new_population = []
        for animal in self.population:
            new_population.append(animal)
            if animal.pregnancy_months_remaining == 0:
                animal_stats = self.animal_stats.loc[animal.id]
                animal_stats.children += 1
                newborn = animal.give_birth()
                new_population.append(newborn)
                self.log_animal(newborn)

        self.population = new_population

    def feed_animals(self):
        """Get animals to eat and drink, and apply consequences on the habitat

        The animals who can drink and eat dependent on the amount of resources left are selected randomly

        TODO: This might be refactored to go into the habitat
        """
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
        """Runs n months of the simulation"""
        for _ in range(n_months):
            self.run_one_month()
            if len(self.population) == 0:
                return

    def run_year(self):
        """Runs one year of the simulation"""
        self.run_n_months(n_months=12)

    def run_n_years(self, n_years):
        """Run n years of the simulation"""
        self.run_n_months(n_months=n_years*12)

    def run_while_not_dead(self, max_years=50):
        """Runs the simulation until all animals are dead or max_years have been reached"""
        while len(self.population) > 0:
            self.run_one_month()
            if self.current_year == max_years:
                break

    def init_population(self, num=30, age_in_years=0):
        """Adds the first num animals to the population"""
        self.population = []
        for _ in range(num):
            gender = random.choice([Gender.MALE, Gender.FEMALE])
            animal = Animal(self.species, gender)
            animal.age = age_in_years
            self.population.append(animal)
            self.log_animal(animal)

    def log_animal(self, animal):
        data = {
            'short_id': animal.short_id,
            'year_birth': self.current_year,
            'month_birth': self.current_month,
            'children': 0,
        }
        self.animal_stats.loc[animal.id] = [animal.short_id, self.current_year, self.current_month, None, None, None, 0]
        # self.animal_stats = self.animal_stats.append(data, ignore_index=True)

    def __repr__(self):
        lines = [
            'Simulation : ',
            'Habitat : {}'.format(self.habitat.type),
            'Species : {}'.format(self.species)
        ]
        return '\n'.join(lines)

    def print_stats(self):
        output = '''
1. {species}
2. {habitat}:
  A. Average Population: {avg_pop:.0f}
  B. Max Population: {max_pop}
  C. Mortality Rate: {mort_rate_percent:.0f}%  #monthly death percentage
  D. Causes of Death:
      - {starvation_percent:.0f}% starvation
      - {age_percent:.0f}% age
      - {cold_percent:.0f}% cold_weather
      - {heat_percent:.0f}% hot_weather
3. ran for {years} years
        '''

        avg_pop = (self.stats.male_population.sum() + self.stats.female_population.sum()) / self.months
        max_pop = (self.stats.male_population + self.stats.female_population).max()
        total_deaths = self.animal_stats.death_cause.count()
        starvation_percent = self.animal_stats.loc[self.animal_stats.death_cause.isin(['hunger', 'thirst'])].death_cause.count() / total_deaths *100
        age_percent = self.animal_stats.loc[self.animal_stats.death_cause == 'age'].death_cause.count() / total_deaths *100
        cold_percent = self.animal_stats.loc[self.animal_stats.death_cause == 'cold'].death_cause.count() / total_deaths *100
        heat_percent = self.animal_stats.loc[self.animal_stats.death_cause == 'heat'].death_cause.count() / total_deaths *100
        mort_rate_percent = self.animal_stats.death_cause.count() / self.months *100

        print(output.format(
            species=self.species,
            habitat=self.habitat.type,
            avg_pop=avg_pop,
            max_pop=max_pop,
            mort_rate_percent=mort_rate_percent,
            starvation_percent=starvation_percent,
            age_percent=age_percent,
            cold_percent=cold_percent,
            heat_percent=heat_percent,
            years=self.months//12,
        ))



if __name__ == '__main__':
    import matplotlib.pyplot as plt

    sim = Simulation(habitat_type='plains', species='bear', start_month=3)
    sim.run_while_not_dead(max_years=150)
    logging.info('\n' + str(sim.stats))

    sim.stats.to_csv('stats.csv')
    sim.animal_stats.to_csv('animal_stats.csv')

    # print(sim.animal_stats)
    sim.print_stats()

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

