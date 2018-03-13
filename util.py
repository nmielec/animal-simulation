import enum
import yaml

Season = enum.Enum('Seasons', 'winter spring summer fall')
DeathCause = enum.Enum('DeathCause', 'starvation age cold_weather hot_weather')
Gender = enum.Enum('Gender', 'male female')

def month_to_season(month):
    if month in [12, 1, 2]:
        return Season.winter
    if month in [3, 4, 5]:
        return Season.spring
    if month in [6, 7, 8]:
        return Season.summer
    if month in [9, 10, 11]:
        return Season.fall
    raise ValueError('Month should be between 1 and 12')


def get_data(path='data.yml'):
    with open('data.yml') as f:
        CONFIG = yaml.load(f)
    HABITAT_DATA_RAW = CONFIG['habitats']

    HABITAT_DATA = {}
    for habitat in HABITAT_DATA_RAW:
        HABITAT_DATA[habitat['name']] = habitat

    ANIMAL_DATA_RAW = CONFIG['species']

    ANIMAL_DATA = {}
    for animal in ANIMAL_DATA_RAW:
        ANIMAL_DATA[animal['name']] = animal['attributes']

    return ANIMAL_DATA, HABITAT_DATA