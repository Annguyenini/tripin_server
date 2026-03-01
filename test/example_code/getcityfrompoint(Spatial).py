import geopandas
from shapely.geometry import Point

cities = geopandas.read_file('src/assets/geo/geoBoundariesCGAZ_ADM1.geojson')
sindex = cities.sindex
point = Point(105.834160,21.027764)
possible_index = list(sindex.intersection(point.bounds))
possible_cities = cities.iloc[possible_index]

for _,city in possible_cities.iterrows():
    if city.geometry.contains(point):
        print (city)
    
