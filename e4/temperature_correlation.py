import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def haversine(lat1, lon1, lat2, lon2):
    r = 6371  # Earth's radius in kilometers
    p = np.pi / 180
    a = 0.5 - np.cos((lat2-lat1)*p)/2 + np.cos(lat1*p) * \
        np.cos(lat2*p) * (1-np.cos((lon2-lon1)*p))/2
    return 2 * r * np.arcsin(np.sqrt(a))


def distance(city, stations):
    return haversine(city['latitude'], city['longitude'],
                     stations['latitude'], stations['longitude'])


def best_tmax(city, stations):
    distances = distance(city, stations)
    min_index = np.argmin(distances)
    return stations.iloc[min_index]['avg_tmax']


def main():
    stations_file = sys.argv[1]
    city_data_file = sys.argv[2]
    output = sys.argv[3]

    stations = pd.read_json(stations_file, lines=True)
    stations['avg_tmax'] = stations['avg_tmax'] / 10

    cities = pd.read_csv(city_data_file).dropna()
    cities['area'] = cities['area'] / (10**6)
    cities = cities[cities['area'] <= 10000]
    cities['population_density'] = cities['population'] / cities['area']

    cities['avg_max'] = cities.apply(
        best_tmax, stations=stations, axis=1)

    # Output
    plt.plot(cities['avg_max'], cities['population_density'], 'b.', alpha=0.5)
    plt.xlabel('Avg Max Temperature (\u00b0C)')
    plt.ylabel('Population Density (people/km\u00b2)')
    plt.title('Temperature vs Population Density')

    plt.savefig(output)

    plt.show()


main()
