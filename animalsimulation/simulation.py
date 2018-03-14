#coding: utf-8
import random
import logging
import pandas as pd

from animalsimulation.habitat import Habitat
from animalsimulation.animal import Animal
from animalsimulation.util import Gender


logging.basicConfig(filename='test.log', filemode='w', level=logging.INFO)

class Simulation(object):
    """Handler for the simulation
    Holds a species and a habitat and handles the interaction.
    Runs the simuation and gather the stats.

    TODO: the interaction between habitat and animals might be done in the habitat object
    """
    def __init__(self, habitat_type, species, start_month=1):
        self.habitat = Habitat(habitat_type, species)
        # self.species = species
        self.current_year = 0
        self.current_month = start_month
        self.months = 0

        self.stats = pd.DataFrame(columns=['elapsed_months', 'year', 'month', 'temperature', 'food_stock', 'water_stock', 'male_population', 'female_population', 'deaths'])
        self.animal_stats = pd.DataFrame(columns=['short_id', 'year_birth', 'month_birth', 'year_death', 'month_death', 'death_cause', 'children'])


    def run_one_month(self):
        """Main method of the simulation, runs one month of the simulation"""
        self.habitat.tick(self.current_month)

        logging.info('----------------------------------------------------')
        logging.info('Elapsed months {}'.format(self.months))
        logging.info('{} / {}'.format(self.current_month, self.current_year))
        logging.info('Temperature {}°'.format(self.habitat.current_temperature))
        logging.info('Habitat reserves {} food, {} water'.format(self.habitat.food_stock, self.habitat.water_stock))
        logging.info(
            '{} animals : {}'.format(
                len(self.habitat.population),
                ', '.join((str(animal) for animal
                           in sorted(self.habitat.population, key=lambda a: (a.age, a.id))))
            )
        )

        # self.fill_stats()

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
            'male_population': len(self.habitat.population.males()),
            'female_population': len(self.habitat.population.females()),
            'deaths': self.habitat.current_deaths,
        }, ignore_index=True)


    def run_n_months(self, n_months, stop_on_death=True):
        """Runs n months of the simulation"""
        for _ in range(n_months):
            self.run_one_month()
            if stop_on_death and len(self.habitat.population) == 0:
                break

    def run_year(self):
        """Runs one year of the simulation"""
        self.run_n_months(n_months=12)

    def run_n_years(self, n_years):
        """Run n years of the simulation"""
        self.run_n_months(n_months=n_years*12)

    def run_while_not_dead(self, max_years=50):
        """Runs the simulation until all animals are dead or max_years have been reached"""
        while len(self.habitat.population) > 0:
            self.run_one_month()
            if self.current_year == max_years:
                break


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
            'Species : {}'.format(self.habitat.species)
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
    sim.run_while_not_dead(max_years=1)
    logging.info('\n' + str(sim.stats))


    # sim.stats.to_csv('stats.csv')
    # sim.animal_stats.to_csv('animal_stats.csv')

    # print(sim.animal_stats)
    # sim.print_stats()

    # fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
    # x = sim.stats.elapsed_months / 12
    # ax1.plot(x, sim.stats.food_stock, label='Food stock')
    # ax1.plot(x, sim.stats.water_stock, label='Water stock')
    # ax2.plot(x, sim.stats.male_population, label='Male animals')
    # ax2.plot(x, sim.stats.female_population, label='Female animals')
    # ax1.legend()
    # ax2.legend()
    # plt.show()

