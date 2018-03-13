#coding: utf-8
import uuid

from animalsimulation.util import Gender
from animalsimulation.util import get_data

ANIMAL_DATA, _ = get_data()


class Animal(object):
    def __init__(self, species, gender):
        self.species = species
        self.gender = gender

        self.id = str(uuid.uuid4())

        self.pregnancy_months_remaining = None

        self.last_ate_months = 0
        self.last_drank_months = 0
        self.age_months = 0

        self.ate_this_month = False
        self.drank_this_month = False

        self.cold_for = 0
        self.hot_for = 0

    def tick(self, temperature):
        if self.ate_this_month:
            self.last_ate_months = 0
        else:
            self.last_ate_months += 1
        if self.drank_this_month:
            self.last_drank_months = 0
        else:
            self.last_drank_months += 1

        if self.pregnancy_months_remaining is not None:
            self.pregnancy_months_remaining -= 1

        if self.is_cold(temperature):
            self.cold_for += 1
        elif self.is_hot(temperature):
            self.hot_for += 1
        else:
            self.hot_for = 0
            self.cold_for = 0

        self.age_months += 1

        self.ate_this_month = False
        self.drank_this_month = False

    def eat(self):
        self.ate_this_month = True

    def drink(self):
        self.drank_this_month = True

    def give_birth(self):
        self.pregnancy_months_remaining = None

    def get_pregnant(self):
        self.pregnancy_months_remaining = ANIMAL_DATA[self.species]['gestation_period']

    def is_cold(self, temperature):
        return temperature < ANIMAL_DATA[self.species]['minimum_temperature']
    def is_hot(self, temperature):
        return ANIMAL_DATA[self.species]['maximum_temperature'] < temperature

    def is_old(self):
        return self.age >= ANIMAL_DATA[self.species]['life_span']

    @property
    def age(self):
        return self.age_months // 12

    @property
    def short_id(self):
        return self.id[:3]

    def __repr__(self):
        return '{}{}'.format(self.short_id, 'M' if self.gender is Gender.male else 'F')
        return '{}{}'.format(self.id, '♂' if self.gender is Gender.male else '♀')
        return '{} year old {} {} #{}'.format(self.age, self.gender.name, self.species, self.id)

    def can_breed(self):
        if self.gender == Gender.male:
            return False
        age_ok = ANIMAL_DATA[self.species]['minimum_breeding_age'] <= self.age <= ANIMAL_DATA[self.species]['maximum_breeding_age']
        return age_ok and (self.pregnancy_months_remaining is None)
