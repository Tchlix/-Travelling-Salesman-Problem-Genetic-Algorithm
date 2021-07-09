import numpy as np


def generate_random_cities(
        count:      int,
        x_range:    (float,float),
        y_range:    (float,float)
):
    """
    Using uniform distribution,
    generate cloud of 'count' cities in given ranges
    ('x_range', 'y_range')
    :return: np.array with distances between each city
    """
    cities_coordinates = [(np.random.uniform(low=x_range[0], high=x_range[1]),
                           np.random.uniform(low=y_range[0], high=y_range[1])) for _ in range(count)]
    return cities_coordinates


def read_cities_from_file(
        path:   str
):
    """
    Read list of coordinates of cities from file
    :return: np.array with distances between each city
    """
    cities_coordinates = []
    with open(path, 'r') as file:
        for line in  file.readlines():
            coordinates_str = line.split()
            cities_coordinates.append((float(coordinates_str[0]), float(coordinates_str[1])))
    file.close()
    return cities_coordinates


def count_distances(coordinates):
    count = len(coordinates)
    distances = np.zeros(shape=(count, count))
    for i in range(count):
        for j in range(count):
            distances[i, j] = np.sqrt(np.power(coordinates[i][0]-coordinates[j][0], 2) +
                                      np.power(coordinates[i][1]-coordinates[j][1], 2))
    return distances
