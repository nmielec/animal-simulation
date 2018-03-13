import enum
import yaml

Season = enum.Enum('Seasons', 'WINTER SPRING SUMMER FALL')
DeathCause = enum.Enum('DeathCause', 'HUNGER THIRST AGE COLD HEAT')
Gender = enum.Enum('Gender', 'MALE FEMALE')

def month_to_season(month):
    if month in [12, 1, 2]:
        return Season.WINTER
    if month in [3, 4, 5]:
        return Season.SPRING
    if month in [6, 7, 8]:
        return Season.SUMMER
    if month in [9, 10, 11]:
        return Season.FALL
    raise ValueError('Month should be between 1 and 12')


def get_data(path='data.yml'):
    with open(path) as f:
        config = yaml.load(f)

    raw_habitat_data = config['habitats']
    habitat_data = {}
    for habitat in raw_habitat_data:
        habitat_data[habitat['name']] = habitat

    raw_animal_data = config['species']
    animal_data = {}
    for animal in raw_animal_data:
        animal_data[animal['name']] = animal['attributes']

    return animal_data, habitat_data