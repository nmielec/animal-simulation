import random

from animalsimulation.util import month_to_season
from animalsimulation.util import get_data

_, HABITAT_DATA = get_data()


class Habitat(object):
    def __init__(self, type):
        self.type = type
        self.food_stock = 0
        self.water_stock = 0
        self.replenish()

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
